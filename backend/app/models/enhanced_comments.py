"""
Enhanced comment system models for threaded discussions and mentions.
Extends the existing task comment system with advanced features.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import BaseModel, JSONField
import datetime
import re
from typing import List, Dict, Any, Optional


class TaskCommentEnhanced(Base):
    """
    Enhanced task comment model with threading, mentions, and rich content support.
    Extends the basic comment functionality with advanced collaboration features.
    """
    __tablename__ = "task_comments_enhanced"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic content
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)  # Rendered HTML with mentions/formatting
    content_metadata = Column(JSONField, nullable=True)  # Mentions, links, etc.
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Threading support
    parent_comment_id = Column(Integer, ForeignKey("task_comments_enhanced.id"), nullable=True, index=True)
    thread_depth = Column(Integer, default=0, nullable=False, index=True)
    thread_root_id = Column(Integer, ForeignKey("task_comments_enhanced.id"), nullable=True, index=True)
    
    # Engagement metrics
    like_count = Column(Integer, default=0, nullable=False)
    reply_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    # Content status
    is_edited = Column(Boolean, default=False, nullable=False)
    edited_at = Column(DateTime, nullable=True)
    edited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Visibility and moderation
    is_active = Column(Boolean, default=True, nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="enhanced_comments")
    user = relationship("User", foreign_keys=[user_id], back_populates="enhanced_comments")
    editor = relationship("User", foreign_keys=[edited_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    # Threading relationships
    parent_comment = relationship("TaskCommentEnhanced", remote_side=[id], foreign_keys=[parent_comment_id], back_populates="replies")
    replies = relationship("TaskCommentEnhanced", foreign_keys=[parent_comment_id], back_populates="parent_comment", cascade="all, delete-orphan")
    thread_root = relationship("TaskCommentEnhanced", remote_side=[id], foreign_keys=[thread_root_id])
    
    # Enhanced feature relationships
    mentions = relationship("CommentMention", back_populates="comment", cascade="all, delete-orphan")
    attachments = relationship("CommentAttachment", back_populates="comment", cascade="all, delete-orphan")
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")
    reactions = relationship("CommentReaction", back_populates="comment", cascade="all, delete-orphan")
    activities = relationship("CommentActivity", back_populates="comment", cascade="all, delete-orphan")

    def extract_mentions(self) -> List[str]:
        """Extract @username mentions from comment content."""
        mention_pattern = r'@(\w+(?:\.\w+)?)'
        mentions = re.findall(mention_pattern, self.content)
        return list(set(mentions))  # Remove duplicates

    def render_html_content(self) -> str:
        """Render comment content with mentions and formatting as HTML."""
        html_content = self.content
        
        # Convert mentions to HTML links
        mention_pattern = r'@(\w+(?:\.\w+)?)'
        html_content = re.sub(
            mention_pattern, 
            r'<span class="mention" data-user="\1">@\1</span>', 
            html_content
        )
        
        # Convert line breaks to HTML
        html_content = html_content.replace('\n', '<br>')
        
        return html_content

    def calculate_thread_metrics(self) -> Dict[str, Any]:
        """Calculate thread-level metrics for this comment."""
        total_replies = len(self.replies)
        total_likes = sum(reply.like_count for reply in self.replies) + self.like_count
        
        return {
            "direct_replies": total_replies,
            "total_thread_likes": total_likes,
            "thread_participants": len(set([reply.user_id for reply in self.replies] + [self.user_id])),
            "last_activity": max([reply.updated_at for reply in self.replies] + [self.updated_at]) if self.replies else self.updated_at
        }

    def increment_reply_count(self):
        """Increment reply count when a new reply is added."""
        self.reply_count += 1
        if self.parent_comment:
            self.parent_comment.increment_reply_count()

    def is_thread_starter(self) -> bool:
        """Check if this comment starts a thread (no parent)."""
        return self.parent_comment_id is None

    def get_thread_path(self) -> List[int]:
        """Get the path from thread root to this comment."""
        path = [self.id]
        current = self.parent_comment
        
        while current:
            path.insert(0, current.id)
            current = current.parent_comment
            
        return path

    def __repr__(self):
        status = f"depth:{self.thread_depth}, replies:{self.reply_count}"
        return f"<TaskCommentEnhanced(id={self.id}, task_id={self.task_id}, {status})>"


class CommentMention(Base):
    """
    @Mention system for comments with notification support.
    Tracks when users are mentioned in comments and manages notification state.
    """
    __tablename__ = "comment_mentions"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("task_comments_enhanced.id"), nullable=False, index=True)
    mentioned_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentioning_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Mention details
    mention_text = Column(String(100), nullable=False)  # "@john.doe" or "@john"
    context_start = Column(Integer, nullable=False)  # Character position in comment
    context_end = Column(Integer, nullable=False)
    context_snippet = Column(String(200), nullable=True)  # Surrounding text context
    
    # Notification status
    is_read = Column(Boolean, default=False, nullable=False)
    is_notified = Column(Boolean, default=False, nullable=False)
    notified_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    comment = relationship("TaskCommentEnhanced", back_populates="mentions")
    mentioned_user = relationship("User", foreign_keys=[mentioned_user_id], back_populates="received_comment_mentions")
    mentioning_user = relationship("User", foreign_keys=[mentioning_user_id], back_populates="created_comment_mentions")

    def mark_as_read(self):
        """Mark mention as read by the user."""
        self.is_read = True
        self.read_at = datetime.datetime.utcnow()

    def mark_as_notified(self):
        """Mark that user has been notified about this mention."""
        self.is_notified = True
        self.notified_at = datetime.datetime.utcnow()

    def get_notification_context(self) -> Dict[str, Any]:
        """Get context information for notifications."""
        return {
            "task_id": self.comment.task_id,
            "task_title": self.comment.task.title if self.comment.task else "Unknown Task",
            "mentioning_user_name": self.mentioning_user.full_name if self.mentioning_user else "Unknown User",
            "comment_preview": self.context_snippet or self.comment.content[:100],
            "mention_text": self.mention_text,
            "comment_url": f"/tasks/{self.comment.task_id}/comments/{self.comment.id}"
        }

    def __repr__(self):
        return f"<CommentMention(id={self.id}, {self.mention_text}, read={self.is_read})>"


class CommentAttachment(Base):
    """
    File attachments linked to specific comments.
    Supports images, documents, and other file types with metadata.
    """
    __tablename__ = "comment_attachments"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("task_comments_enhanced.id"), nullable=False, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False, index=True)
    
    # Attachment metadata
    display_name = Column(String(255), nullable=True)  # Custom name for display
    description = Column(Text, nullable=True)
    attachment_order = Column(Integer, default=0, nullable=False)  # Order within comment
    
    # File properties (cached from FileUpload for performance)
    file_size = Column(Integer, nullable=True)  # File size in bytes
    mime_type = Column(String(255), nullable=True)  # MIME type
    attachment_type = Column(String(50), default="file", nullable=False)  # file, image, video, etc.
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who uploaded
    
    # Additional metadata
    attachment_metadata = Column(JSONField, nullable=True)  # Extra file/attachment metadata
    
    # Display settings
    is_inline = Column(Boolean, default=False, nullable=False)  # Show inline vs as attachment
    show_thumbnail = Column(Boolean, default=True, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    comment = relationship("TaskCommentEnhanced", back_populates="attachments")
    file = relationship("FileUpload", back_populates="comment_attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def get_thumbnail_url(self) -> Optional[str]:
        """Get thumbnail URL if available."""
        if self.file and hasattr(self.file, 'thumbnail_path') and self.file.thumbnail_path:
            return f"/api/v1/files/{self.file.id}/thumbnail"
        return None

    def get_preview_url(self) -> Optional[str]:
        """Get file preview URL."""
        if self.file:
            return f"/api/v1/files/{self.file.id}/preview"
        return None

    def is_image(self) -> bool:
        """Check if attachment is an image file."""
        if self.file and hasattr(self.file, 'mime_type'):
            return self.file.mime_type.startswith('image/')
        return False

    def __repr__(self):
        return f"<CommentAttachment(id={self.id}, comment_id={self.comment_id}, file_id={self.file_id})>"


class CommentLike(Base):
    """
    Like/thumbs up system for comments.
    Tracks which users liked which comments with timestamp.
    """
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("task_comments_enhanced.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    comment = relationship("TaskCommentEnhanced", back_populates="likes")
    user = relationship("User", back_populates="comment_likes")

    def __repr__(self):
        return f"<CommentLike(comment_id={self.comment_id}, user_id={self.user_id})>"


class CommentReaction(Base):
    """
    Emoji reaction system for comments (😀, 👍, ❤️, etc.).
    More expressive than simple likes with variety of emoji reactions.
    """
    __tablename__ = "comment_reactions"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("task_comments_enhanced.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Reaction details
    emoji = Column(String(10), nullable=False, index=True)  # Unicode emoji
    emoji_name = Column(String(50), nullable=False)  # Human readable name
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    comment = relationship("TaskCommentEnhanced", back_populates="reactions")
    user = relationship("User", back_populates="comment_reactions")

    def __repr__(self):
        return f"<CommentReaction(comment_id={self.comment_id}, user_id={self.user_id}, emoji='{self.emoji}')>"


class CommentActivity(Base):
    """
    Activity log for comment-related actions.
    Tracks edits, mentions, likes, and other interactions for audit purposes.
    """
    __tablename__ = "comment_activities"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("task_comments_enhanced.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # created, edited, liked, mentioned, etc.
    description = Column(Text, nullable=False)  # Human-readable description
    activity_data = Column(JSONField, nullable=True)  # Additional structured data
    
    # Context
    ip_address = Column(String(45), nullable=True)  # For audit trail
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    comment = relationship("TaskCommentEnhanced", back_populates="activities")
    user = relationship("User", back_populates="comment_activities")

    def __repr__(self):
        return f"<CommentActivity(comment_id={self.comment_id}, type='{self.activity_type}')>"