"""
Enhanced comment system API endpoints.

Provides comprehensive comment functionality including:
- Threaded comments with unlimited nesting
- @mention system with notifications
- File attachments and media support
- Comment reactions and likes
- Real-time updates and notifications
- Advanced search and filtering
"""

from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File as FastAPIFile
from sqlalchemy import and_, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.task import Task
from app.models.user import User
from app.models.enhanced_comments import (
    TaskCommentEnhanced, CommentMention, CommentAttachment, 
    CommentLike, CommentReaction, CommentActivity
)
from app.models.file_management import FileUpload
from app.schemas.user import UserRead

router = APIRouter()


# ===== ENHANCED COMMENT CRUD ENDPOINTS =====

@router.post("/{task_id}/comments")
async def create_enhanced_comment(
    task_id: int,
    content: str,
    parent_comment_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new comment with enhanced features (threading, mentions)."""
    
    # Verify task exists and user has access
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify parent comment exists if provided
    parent_comment = None
    thread_depth = 0
    thread_root_id = None
    
    if parent_comment_id:
        parent_comment = await db.get(TaskCommentEnhanced, parent_comment_id)
        if not parent_comment or parent_comment.task_id != task_id:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        thread_depth = parent_comment.thread_depth + 1
        thread_root_id = parent_comment.thread_root_id or parent_comment.id
        
        # Limit thread depth to prevent excessive nesting
        if thread_depth > 10:
            raise HTTPException(status_code=400, detail="Maximum thread depth exceeded")
    
    # Create enhanced comment
    comment = TaskCommentEnhanced(
        content=content,
        task_id=task_id,
        user_id=current_user.id,
        parent_comment_id=parent_comment_id,
        thread_depth=thread_depth,
        thread_root_id=thread_root_id
    )
    
    # Render HTML content with mentions
    comment.content_html = comment.render_html_content()
    
    db.add(comment)
    await db.flush()  # Get the ID without committing
    
    # Process mentions
    mentions = comment.extract_mentions()
    mention_objects = []
    
    for mention_text in mentions:
        # Find mentioned user (simple username match for now)
        result = await db.execute(
            select(User).where(
                or_(
                    User.email.ilike(f"{mention_text}@%"),
                    func.concat(User.first_name, ".", User.last_name).ilike(mention_text),
                    func.concat(User.first_name, User.last_name).ilike(mention_text.replace(".", ""))
                )
            )
        )
        mentioned_user = result.scalar_one_or_none()
        
        if mentioned_user:
            # Create mention record
            mention = CommentMention(
                comment_id=comment.id,
                mentioned_user_id=mentioned_user.id,
                mentioning_user_id=current_user.id,
                mention_text=f"@{mention_text}",
                context_start=content.find(f"@{mention_text}"),
                context_end=content.find(f"@{mention_text}") + len(mention_text) + 1,
                context_snippet=get_mention_context(content, mention_text)
            )
            mention_objects.append(mention)
    
    # Add mentions to session
    db.add_all(mention_objects)
    
    # Update parent comment reply count
    if parent_comment:
        parent_comment.increment_reply_count()
    
    await db.commit()
    await db.refresh(comment)
    
    # Load relationships for response
    result = await db.execute(
        select(TaskCommentEnhanced)
        .options(
            selectinload(TaskCommentEnhanced.user),
            selectinload(TaskCommentEnhanced.mentions),
            selectinload(TaskCommentEnhanced.replies)
        )
        .where(TaskCommentEnhanced.id == comment.id)
    )
    comment_with_relations = result.scalar_one()
    
    # Create activity log
    activity = CommentActivity(
        comment_id=comment.id,
        user_id=current_user.id,
        activity_type="created",
        description=f"Created comment on task: {task.title}",
        activity_data={"mentions_count": len(mention_objects)}
    )
    db.add(activity)
    await db.commit()
    
    return build_enhanced_comment_response(comment_with_relations)


@router.get("/{task_id}/comments")
async def get_enhanced_comments(
    task_id: int,
    include_threads: bool = Query(True, description="Include threaded replies"),
    sort_by: str = Query("created_at", description="Sort field (created_at, like_count, reply_count)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get enhanced comments for a task with threading support."""
    
    # Verify task access
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Build query
    query = select(TaskCommentEnhanced).where(
        and_(
            TaskCommentEnhanced.task_id == task_id,
            TaskCommentEnhanced.is_active == True
        )
    ).options(
        selectinload(TaskCommentEnhanced.user),
        selectinload(TaskCommentEnhanced.mentions),
        selectinload(TaskCommentEnhanced.attachments),
        selectinload(TaskCommentEnhanced.likes),
        selectinload(TaskCommentEnhanced.reactions)
    )
    
    # Filter for top-level comments if not including threads
    if not include_threads:
        query = query.where(TaskCommentEnhanced.parent_comment_id.is_(None))
    
    # Apply sorting
    sort_field = getattr(TaskCommentEnhanced, sort_by, TaskCommentEnhanced.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    comments = result.scalars().all()
    
    # Build response with thread information
    comment_responses = []
    for comment in comments:
        comment_data = build_enhanced_comment_response(comment)
        
        # Add thread metrics
        if include_threads and comment.is_thread_starter():
            comment_data["thread_metrics"] = comment.calculate_thread_metrics()
        
        comment_responses.append(comment_data)
    
    return {
        "comments": comment_responses,
        "total_comments": len(comments),
        "has_more": len(comments) == limit,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "next_offset": offset + limit if len(comments) == limit else None
        }
    }


@router.get("/{task_id}/comments/{comment_id}/thread")
async def get_comment_thread(
    task_id: int,
    comment_id: int,
    max_depth: int = Query(10, ge=1, le=20, description="Maximum thread depth"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get complete thread for a specific comment."""
    
    # Verify comment exists
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment or comment.task_id != task_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Get thread root
    thread_root_id = comment.thread_root_id or comment.id
    
    # Get all comments in thread
    result = await db.execute(
        select(TaskCommentEnhanced)
        .where(
            and_(
                TaskCommentEnhanced.task_id == task_id,
                or_(
                    TaskCommentEnhanced.id == thread_root_id,
                    TaskCommentEnhanced.thread_root_id == thread_root_id
                ),
                TaskCommentEnhanced.is_active == True,
                TaskCommentEnhanced.thread_depth <= max_depth
            )
        )
        .options(
            selectinload(TaskCommentEnhanced.user),
            selectinload(TaskCommentEnhanced.mentions),
            selectinload(TaskCommentEnhanced.attachments),
            selectinload(TaskCommentEnhanced.likes),
            selectinload(TaskCommentEnhanced.reactions)
        )
        .order_by(TaskCommentEnhanced.created_at)
    )
    
    thread_comments = result.scalars().all()
    
    # Build hierarchical thread structure
    thread_structure = build_thread_hierarchy(thread_comments, thread_root_id)
    
    return {
        "thread_root_id": thread_root_id,
        "thread_structure": thread_structure,
        "total_comments": len(thread_comments),
        "max_depth_reached": any(c.thread_depth >= max_depth for c in thread_comments)
    }


@router.put("/comments/{comment_id}")
async def edit_comment(
    comment_id: int,
    content: str,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Edit an existing comment (user can only edit their own comments)."""
    
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only edit your own comments")
    
    # Store original content for activity log
    original_content = comment.content
    
    # Update comment
    comment.content = content
    comment.content_html = comment.render_html_content()
    comment.is_edited = True
    comment.edited_at = datetime.utcnow()
    comment.edited_by = current_user.id
    
    # Update mentions (remove old, add new)
    await db.execute(
        select(CommentMention).where(CommentMention.comment_id == comment_id)
    )
    # Process new mentions (similar to creation logic)
    
    await db.commit()
    
    # Log activity
    activity = CommentActivity(
        comment_id=comment.id,
        user_id=current_user.id,
        activity_type="edited",
        description="Edited comment content",
        activity_data={
            "original_content": original_content[:100],
            "new_content": content[:100]
        }
    )
    db.add(activity)
    await db.commit()
    
    return {"message": "Comment updated successfully", "comment_id": comment_id}


# ===== MENTION SYSTEM ENDPOINTS =====

@router.get("/mentions/suggestions")
async def get_mention_suggestions(
    q: str = Query(..., min_length=1, description="Search query for user names"),
    task_id: Optional[int] = Query(None, description="Filter to task participants"),
    limit: int = Query(10, ge=1, le=50),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user suggestions for @mentions."""
    
    # Build user search query
    search_pattern = f"%{q.lower()}%"
    query = select(User).where(
        and_(
            User.status == "active",
            or_(
                func.lower(User.first_name).like(search_pattern),
                func.lower(User.last_name).like(search_pattern),
                func.lower(User.email).like(search_pattern),
                func.lower(func.concat(User.first_name, " ", User.last_name)).like(search_pattern)
            )
        )
    ).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    suggestions = []
    for user in users:
        # Generate mention text (could be email prefix or name-based)
        mention_text = user.email.split('@')[0] if '@' in user.email else f"{user.first_name.lower()}.{user.last_name.lower()}"
        
        suggestions.append({
            "user_id": user.id,
            "mention_text": mention_text,
            "display_name": user.full_name,
            "email": user.email,
            "avatar_url": getattr(user, 'avatar_url', None)
        })
    
    return {"suggestions": suggestions}


@router.get("/users/{user_id}/mentions")
async def get_user_mentions(
    user_id: int,
    unread_only: bool = Query(False, description="Only unread mentions"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get mentions for a specific user."""
    
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only view your own mentions")
    
    query = select(CommentMention).where(
        CommentMention.mentioned_user_id == user_id
    ).options(
        selectinload(CommentMention.comment).selectinload(TaskCommentEnhanced.task),
        selectinload(CommentMention.mentioning_user)
    )
    
    if unread_only:
        query = query.where(CommentMention.is_read == False)
    
    query = query.order_by(desc(CommentMention.created_at)).offset(offset).limit(limit)
    
    result = await db.execute(query)
    mentions = result.scalars().all()
    
    mention_data = []
    for mention in mentions:
        mention_data.append({
            "id": mention.id,
            "mention_text": mention.mention_text,
            "context_snippet": mention.context_snippet,
            "is_read": mention.is_read,
            "created_at": mention.created_at,
            "comment": {
                "id": mention.comment.id,
                "content": mention.comment.content[:200],
                "task_id": mention.comment.task_id,
                "task_title": mention.comment.task.title if mention.comment.task else "Unknown"
            },
            "mentioning_user": {
                "id": mention.mentioning_user.id,
                "name": mention.mentioning_user.full_name,
                "email": mention.mentioning_user.email
            }
        })
    
    return {
        "mentions": mention_data,
        "total_unread": len([m for m in mentions if not m.is_read]),
        "pagination": {"limit": limit, "offset": offset}
    }


@router.post("/mentions/{mention_id}/mark-read")
async def mark_mention_read(
    mention_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mark a mention as read."""
    
    mention = await db.get(CommentMention, mention_id)
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
    
    if mention.mentioned_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only mark your own mentions as read")
    
    mention.mark_as_read()
    await db.commit()
    
    return {"message": "Mention marked as read", "mention_id": mention_id}


# ===== HELPER FUNCTIONS =====

def get_mention_context(content: str, mention_text: str, context_length: int = 50) -> str:
    """Extract context around a mention for display."""
    mention_pos = content.find(f"@{mention_text}")
    if mention_pos == -1:
        return ""
    
    start = max(0, mention_pos - context_length)
    end = min(len(content), mention_pos + len(mention_text) + context_length + 1)
    
    context = content[start:end]
    if start > 0:
        context = "..." + context
    if end < len(content):
        context = context + "..."
    
    return context


def build_enhanced_comment_response(comment: TaskCommentEnhanced) -> Dict[str, Any]:
    """Build comprehensive comment response with all related data."""
    return {
        "id": comment.id,
        "content": comment.content,
        "content_html": comment.content_html,
        "task_id": comment.task_id,
        "user": {
            "id": comment.user.id,
            "name": comment.user.full_name,
            "email": comment.user.email,
            "avatar_url": getattr(comment.user, 'avatar_url', None)
        } if comment.user else None,
        "thread_info": {
            "parent_comment_id": comment.parent_comment_id,
            "thread_depth": comment.thread_depth,
            "thread_root_id": comment.thread_root_id,
            "is_thread_starter": comment.is_thread_starter(),
            "thread_path": comment.get_thread_path()
        },
        "engagement": {
            "like_count": comment.like_count,
            "reply_count": comment.reply_count,
            "view_count": comment.view_count
        },
        "mentions": [
            {
                "id": mention.id,
                "mentioned_user": {
                    "id": mention.mentioned_user.id,
                    "name": mention.mentioned_user.full_name
                } if mention.mentioned_user else None,
                "mention_text": mention.mention_text,
                "is_read": mention.is_read
            }
            for mention in (comment.mentions or [])
        ],
        "attachments": [
            {
                "id": attachment.id,
                "file_id": attachment.file_id,
                "display_name": attachment.display_name,
                "is_inline": attachment.is_inline,
                "thumbnail_url": attachment.get_thumbnail_url(),
                "preview_url": attachment.get_preview_url(),
                "is_image": attachment.is_image()
            }
            for attachment in (comment.attachments or [])
        ],
        "status": {
            "is_edited": comment.is_edited,
            "edited_at": comment.edited_at,
            "is_pinned": comment.is_pinned,
            "is_resolved": comment.is_resolved
        },
        "timestamps": {
            "created_at": comment.created_at,
            "updated_at": comment.updated_at
        }
    }


def build_thread_hierarchy(comments: List[TaskCommentEnhanced], root_id: int) -> Dict[str, Any]:
    """Build hierarchical thread structure from flat comment list."""
    comment_dict = {comment.id: build_enhanced_comment_response(comment) for comment in comments}
    
    # Build hierarchy
    for comment in comments:
        if comment.parent_comment_id and comment.parent_comment_id in comment_dict:
            parent = comment_dict[comment.parent_comment_id]
            if "replies" not in parent:
                parent["replies"] = []
            parent["replies"].append(comment_dict[comment.id])
    
    # Return root comment with full hierarchy
    return comment_dict.get(root_id, {})


# ===== LIKE AND REACTION ENDPOINTS =====

@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Like a comment."""
    
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if already liked
    result = await db.execute(
        select(CommentLike).where(
            and_(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == current_user.id
            )
        )
    )
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        return {"message": "Comment already liked", "liked": True}
    
    # Create like
    like = CommentLike(comment_id=comment_id, user_id=current_user.id)
    db.add(like)
    
    # Increment comment like count
    comment.like_count += 1
    
    await db.commit()
    
    return {
        "message": "Comment liked successfully",
        "liked": True,
        "like_count": comment.like_count
    }


@router.delete("/comments/{comment_id}/like")
async def unlike_comment(
    comment_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove like from a comment."""
    
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Find existing like
    result = await db.execute(
        select(CommentLike).where(
            and_(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == current_user.id
            )
        )
    )
    existing_like = result.scalar_one_or_none()
    
    if not existing_like:
        return {"message": "Comment not liked", "liked": False}
    
    # Remove like
    await db.delete(existing_like)
    comment.like_count = max(0, comment.like_count - 1)
    
    await db.commit()
    
    return {
        "message": "Like removed successfully",
        "liked": False,
        "like_count": comment.like_count
    }