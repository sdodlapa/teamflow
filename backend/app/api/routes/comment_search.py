"""
Advanced search and filtering capabilities for enhanced comment system.

Provides comprehensive search functionality including:
- Full-text search across comment content
- Filter by user, date range, mentions
- Cross-task and cross-project search
- Advanced search operators and syntax
- Search analytics and insights
"""

from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, func, desc, asc, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from uuid import UUID
import re

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.enhanced_comments import TaskCommentEnhanced, CommentMention, CommentAttachment
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.schemas.user import UserRead

router = APIRouter()


class CommentSearchService:
    """Service class for advanced comment search functionality."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def full_text_search(
        self,
        query: str,
        user_id: UUID,
        task_ids: Optional[List[int]] = None,
        project_ids: Optional[List[int]] = None,
        author_ids: Optional[List[UUID]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        include_deleted: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Perform full-text search across comments with advanced filtering.
        """
        
        # Build base query
        base_query = select(TaskCommentEnhanced).options(
            selectinload(TaskCommentEnhanced.user),
            selectinload(TaskCommentEnhanced.task),
            selectinload(TaskCommentEnhanced.mentions),
            selectinload(TaskCommentEnhanced.attachments)
        )
        
        # Build search conditions
        conditions = []
        
        # Full-text search condition
        if query:
            search_terms = self._parse_search_query(query)
            for term in search_terms:
                if term.get("type") == "text":
                    conditions.append(
                        or_(
                            TaskCommentEnhanced.content.ilike(f"%{term['value']}%"),
                            TaskCommentEnhanced.content_html.ilike(f"%{term['value']}%")
                        )
                    )
                elif term.get("type") == "user":
                    # Search by username mentioned in content
                    conditions.append(
                        TaskCommentEnhanced.content.ilike(f"%@{term['value']}%")
                    )
                elif term.get("type") == "tag":
                    # Search by hashtags or special markers
                    conditions.append(
                        TaskCommentEnhanced.content.ilike(f"%#{term['value']}%")
                    )
        
        # Task filtering
        if task_ids:
            conditions.append(TaskCommentEnhanced.task_id.in_(task_ids))
        
        # Author filtering
        if author_ids:
            conditions.append(TaskCommentEnhanced.user_id.in_(author_ids))
        
        # Date range filtering
        if date_from:
            conditions.append(TaskCommentEnhanced.created_at >= date_from)
        if date_to:
            conditions.append(TaskCommentEnhanced.created_at <= date_to)
        
        # Active/deleted filtering
        if not include_deleted:
            conditions.append(TaskCommentEnhanced.is_active == True)
        
        # Apply conditions
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Apply project filtering (requires join with tasks)
        if project_ids:
            base_query = base_query.join(Task).where(Task.project_id.in_(project_ids))
        
        # Count total results
        count_query = select(func.count()).select_from(
            base_query.subquery()
        )
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply ordering and pagination
        search_query = base_query.order_by(
            desc(TaskCommentEnhanced.created_at)
        ).offset(offset).limit(limit)
        
        # Execute search
        result = await self.db.execute(search_query)
        comments = result.scalars().all()
        
        # Build search results
        search_results = []
        for comment in comments:
            # Calculate relevance score (simplified)
            relevance_score = self._calculate_relevance_score(comment, query)
            
            # Extract search highlights
            highlights = self._extract_highlights(comment, query)
            
            search_results.append({
                "comment": self._build_comment_response(comment),
                "relevance_score": relevance_score,
                "highlights": highlights,
                "task_info": {
                    "id": comment.task.id,
                    "title": comment.task.title,
                    "project_id": comment.task.project_id
                } if comment.task else None
            })
        
        return {
            "results": search_results,
            "total_count": total_count,
            "query": query,
            "filters_applied": {
                "task_ids": task_ids,
                "project_ids": project_ids, 
                "author_ids": author_ids,
                "date_range": {"from": date_from, "to": date_to},
                "include_deleted": include_deleted
            },
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(search_results) == limit
            }
        }
    
    def _parse_search_query(self, query: str) -> List[Dict[str, str]]:
        """Parse search query for special operators and terms."""
        terms = []
        
        # Simple parsing - in production, use a proper query parser
        # Handle @username mentions
        mentions = re.findall(r'@(\w+)', query)
        for mention in mentions:
            terms.append({"type": "user", "value": mention})
        
        # Handle #hashtags
        hashtags = re.findall(r'#(\w+)', query) 
        for hashtag in hashtags:
            terms.append({"type": "tag", "value": hashtag})
        
        # Handle quoted phrases
        quoted_phrases = re.findall(r'"([^"]+)"', query)
        for phrase in quoted_phrases:
            terms.append({"type": "text", "value": phrase})
        
        # Handle remaining text (remove mentions, hashtags, quotes)
        remaining_text = re.sub(r'@\w+|#\w+|"[^"]+"', '', query).strip()
        if remaining_text:
            # Split into individual words
            words = remaining_text.split()
            for word in words:
                if len(word) > 2:  # Ignore very short words
                    terms.append({"type": "text", "value": word})
        
        return terms
    
    def _calculate_relevance_score(self, comment: TaskCommentEnhanced, query: str) -> float:
        """Calculate relevance score for search results."""
        score = 0.0
        content = (comment.content or "").lower()
        query_lower = query.lower()
        
        # Exact phrase matches get highest score
        if query_lower in content:
            score += 10.0
        
        # Word matches
        query_words = query_lower.split()
        for word in query_words:
            if word in content:
                score += 2.0
        
        # Recent comments get bonus points
        days_ago = (datetime.utcnow() - comment.created_at).days
        if days_ago < 7:
            score += 5.0 - days_ago
        
        # Comments with attachments get bonus
        if comment.attachments:
            score += 1.0
        
        # Popular comments (with likes/replies) get bonus
        score += (comment.like_count or 0) * 0.5
        score += (comment.reply_count or 0) * 0.3
        
        return round(score, 2)
    
    def _extract_highlights(self, comment: TaskCommentEnhanced, query: str) -> List[str]:
        """Extract highlighted snippets from comment content."""
        content = comment.content or ""
        highlights = []
        
        query_words = query.lower().split()
        content_lower = content.lower()
        
        for word in query_words:
            if word in content_lower:
                # Find the word position
                start_pos = content_lower.find(word)
                if start_pos != -1:
                    # Extract context around the word
                    context_start = max(0, start_pos - 50)
                    context_end = min(len(content), start_pos + len(word) + 50)
                    
                    highlight = content[context_start:context_end]
                    if context_start > 0:
                        highlight = "..." + highlight
                    if context_end < len(content):
                        highlight = highlight + "..."
                    
                    highlights.append(highlight)
        
        return highlights[:3]  # Limit to 3 highlights
    
    def _build_comment_response(self, comment: TaskCommentEnhanced) -> Dict[str, Any]:
        """Build comment response object for search results."""
        return {
            "id": comment.id,
            "content": comment.content,
            "content_html": comment.content_html,
            "task_id": comment.task_id,
            "user": {
                "id": comment.user.id,
                "name": comment.user.full_name,
                "email": comment.user.email
            } if comment.user else None,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "is_edited": comment.is_edited,
            "like_count": comment.like_count or 0,
            "reply_count": comment.reply_count or 0,
            "has_attachments": bool(comment.attachments),
            "mention_count": len(comment.mentions or [])
        }


@router.get("/comments/search")
async def search_comments(
    q: str = Query(..., min_length=2, description="Search query"),
    task_ids: Optional[str] = Query(None, description="Comma-separated task IDs"),
    project_ids: Optional[str] = Query(None, description="Comma-separated project IDs"),
    author_emails: Optional[str] = Query(None, description="Comma-separated author emails"),
    date_from: Optional[datetime] = Query(None, description="Search from date"),
    date_to: Optional[datetime] = Query(None, description="Search to date"),
    include_deleted: bool = Query(False, description="Include deleted comments"),
    sort_by: str = Query("relevance", description="Sort by: relevance, date, author"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    limit: int = Query(25, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Result offset"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Advanced comment search with filtering and sorting.
    
    Search operators:
    - @username: Find comments mentioning a user
    - #tag: Find comments with hashtags
    - "exact phrase": Find exact phrase matches
    - word1 word2: Find comments containing all words
    """
    
    # Parse filter parameters
    task_id_list = None
    if task_ids:
        try:
            task_id_list = [int(tid.strip()) for tid in task_ids.split(",") if tid.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task IDs format")
    
    project_id_list = None
    if project_ids:
        try:
            project_id_list = [int(pid.strip()) for pid in project_ids.split(",") if pid.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid project IDs format")
    
    author_id_list = None
    if author_emails:
        try:
            # Convert emails to user IDs
            author_email_list = [email.strip() for email in author_emails.split(",") if email.strip()]
            result = await db.execute(
                select(User.id).where(User.email.in_(author_email_list))
            )
            author_id_list = [row[0] for row in result.fetchall()]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid author emails")
    
    # Perform search
    search_service = CommentSearchService(db)
    search_results = await search_service.full_text_search(
        query=q,
        user_id=current_user.id,
        task_ids=task_id_list,
        project_ids=project_id_list,
        author_ids=author_id_list,
        date_from=date_from,
        date_to=date_to,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset
    )
    
    return search_results


@router.get("/comments/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Partial query for suggestions"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get search suggestions for comment search autocomplete."""
    
    suggestions = {
        "users": [],
        "tags": [],
        "phrases": []
    }
    
    # Get user suggestions for @mentions
    if q.startswith("@"):
        username_query = q[1:].lower()
        result = await db.execute(
            select(User).where(
                or_(
                    func.lower(User.first_name).like(f"{username_query}%"),
                    func.lower(User.last_name).like(f"{username_query}%"),
                    func.lower(User.email).like(f"{username_query}%")
                )
            ).limit(10)
        )
        users = result.scalars().all()
        
        suggestions["users"] = [
            {
                "value": f"@{user.email.split('@')[0]}",
                "display": f"{user.full_name} ({user.email})",
                "type": "user"
            }
            for user in users
        ]
    
    # Get common hashtags
    elif q.startswith("#"):
        # This would typically query a hashtags table or extract from comment content
        common_tags = ["bug", "feature", "urgent", "resolved", "question"]
        tag_query = q[1:].lower()
        
        suggestions["tags"] = [
            {
                "value": f"#{tag}",
                "display": f"#{tag}",
                "type": "hashtag"
            }
            for tag in common_tags
            if tag.startswith(tag_query)
        ]
    
    # Get phrase suggestions
    else:
        # This would typically be based on popular search terms
        common_phrases = [
            "assigned to me",
            "created last week", 
            "high priority",
            "needs review",
            "bug report"
        ]
        
        suggestions["phrases"] = [
            {
                "value": phrase,
                "display": phrase,
                "type": "phrase"
            }
            for phrase in common_phrases
            if q.lower() in phrase.lower()
        ]
    
    return suggestions


@router.get("/comments/search/analytics")
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Analytics period in days"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get comment search analytics and insights."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Comment activity over time
    activity_result = await db.execute(
        select(
            func.date(TaskCommentEnhanced.created_at).label('date'),
            func.count(TaskCommentEnhanced.id).label('count')
        )
        .where(TaskCommentEnhanced.created_at >= start_date)
        .group_by(func.date(TaskCommentEnhanced.created_at))
        .order_by(func.date(TaskCommentEnhanced.created_at))
    )
    
    activity_data = [
        {"date": row.date.isoformat(), "count": row.count}
        for row in activity_result.fetchall()
    ]
    
    # Top commenters
    commenters_result = await db.execute(
        select(
            User.full_name,
            User.email,
            func.count(TaskCommentEnhanced.id).label('comment_count')
        )
        .join(TaskCommentEnhanced, User.id == TaskCommentEnhanced.user_id)
        .where(TaskCommentEnhanced.created_at >= start_date)
        .group_by(User.id, User.full_name, User.email)
        .order_by(desc(func.count(TaskCommentEnhanced.id)))
        .limit(10)
    )
    
    top_commenters = [
        {
            "name": row.full_name,
            "email": row.email,
            "comment_count": row.comment_count
        }
        for row in commenters_result.fetchall()
    ]
    
    # Comment statistics
    stats_result = await db.execute(
        select(
            func.count(TaskCommentEnhanced.id).label('total_comments'),
            func.count(TaskCommentEnhanced.id).filter(TaskCommentEnhanced.parent_comment_id.isnot(None)).label('reply_comments'),
            func.sum(TaskCommentEnhanced.like_count).label('total_likes'),
            func.count(CommentMention.id).label('total_mentions'),
            func.count(CommentAttachment.id).label('total_attachments')
        )
        .outerjoin(CommentMention, TaskCommentEnhanced.id == CommentMention.comment_id)
        .outerjoin(CommentAttachment, TaskCommentEnhanced.id == CommentAttachment.comment_id)
        .where(TaskCommentEnhanced.created_at >= start_date)
    )
    
    stats = stats_result.fetchone()
    
    return {
        "period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat()
        },
        "activity_timeline": activity_data,
        "top_commenters": top_commenters,
        "statistics": {
            "total_comments": stats.total_comments or 0,
            "reply_comments": stats.reply_comments or 0,
            "total_likes": stats.total_likes or 0,
            "total_mentions": stats.total_mentions or 0,
            "total_attachments": stats.total_attachments or 0,
            "avg_comments_per_day": round((stats.total_comments or 0) / days, 2)
        }
    }