"""
Enhanced comment system schemas for API serialization.

Provides comprehensive Pydantic models for the enhanced comment system including:
- Comment creation and editing
- Threading and nested replies  
- @mention system with user suggestions
- File attachments and media support
- Reactions and engagement metrics
- Activity tracking and notifications
"""

from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from uuid import UUID

# ===== ENUMS AND CONSTANTS =====

class CommentSortBy(str, Enum):
    """Sorting options for comments."""
    CREATED_AT = "created_at"
    LIKE_COUNT = "like_count"
    REPLY_COUNT = "reply_count"
    UPDATED_AT = "updated_at"

class CommentSortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"

class ActivityType(str, Enum):
    """Comment activity types."""
    CREATED = "created"
    EDITED = "edited"
    DELETED = "deleted"
    LIKED = "liked"
    UNLIKED = "unliked"
    MENTIONED = "mentioned"
    REPLIED = "replied"

class AttachmentType(str, Enum):
    """Attachment type options."""
    FILE = "file"
    IMAGE = "image"
    INLINE_IMAGE = "inline_image"
    VIDEO = "video"
    DOCUMENT = "document"

# ===== BASE COMMENT SCHEMAS =====

class CommentUserInfo(BaseModel):
    """User information for comment responses."""
    id: UUID
    name: str
    email: str
    avatar_url: Optional[str] = None

class CommentThreadInfo(BaseModel):
    """Thread hierarchy information."""
    parent_comment_id: Optional[int] = None
    thread_depth: int = 0
    thread_root_id: Optional[int] = None
    is_thread_starter: bool = False
    thread_path: List[int] = []

class CommentEngagement(BaseModel):
    """Comment engagement metrics."""
    like_count: int = 0
    reply_count: int = 0
    view_count: int = 0
    reaction_count: int = 0

class CommentStatus(BaseModel):
    """Comment status flags."""
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_pinned: bool = False
    is_resolved: bool = False
    is_deleted: bool = False

class CommentTimestamps(BaseModel):
    """Comment timestamp information."""
    created_at: datetime
    updated_at: Optional[datetime] = None

# ===== MENTION SCHEMAS =====

class MentionBase(BaseModel):
    """Base mention information."""
    mention_text: str
    context_snippet: Optional[str] = None

class MentionCreate(MentionBase):
    """Schema for creating mentions."""
    mentioned_user_id: UUID

class MentionRead(MentionBase):
    """Schema for reading mention information."""
    id: int
    mentioned_user: Optional[CommentUserInfo] = None
    is_read: bool = False
    created_at: datetime

class MentionSuggestion(BaseModel):
    """User mention suggestion."""
    user_id: UUID
    mention_text: str
    display_name: str
    email: str
    avatar_url: Optional[str] = None

class UserMentionResponse(BaseModel):
    """Response for user mention notifications."""
    id: int
    mention_text: str
    context_snippet: Optional[str] = None
    is_read: bool = False
    created_at: datetime
    comment: Dict[str, Any]
    mentioning_user: CommentUserInfo

# ===== ATTACHMENT SCHEMAS =====

class AttachmentBase(BaseModel):
    """Base attachment information."""
    display_name: str
    is_inline: bool = False

class AttachmentCreate(AttachmentBase):
    """Schema for creating attachments."""
    file_id: UUID
    attachment_type: AttachmentType = AttachmentType.FILE

class AttachmentRead(AttachmentBase):
    """Schema for reading attachment information."""
    id: int
    file_id: UUID
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    attachment_type: str
    is_image: bool = False
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    uploaded_at: datetime

class InlineImageResponse(BaseModel):
    """Response for inline image uploads."""
    attachment_id: int
    file_id: UUID
    inline_url: str
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    alt_text: Optional[str] = None
    file_size: int
    dimensions: Optional[Dict[str, int]] = None
    markdown_embed: str

class BulkUploadResponse(BaseModel):
    """Response for bulk file uploads."""
    message: str
    successful_uploads: List[Dict[str, Any]]
    failed_uploads: List[Dict[str, Any]]
    total_files: int
    success_count: int
    failure_count: int

# ===== MAIN COMMENT SCHEMAS =====

class CommentCreateRequest(BaseModel):
    """Request schema for creating comments."""
    content: str = Field(..., min_length=1, max_length=10000)
    parent_comment_id: Optional[int] = None

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Comment content cannot be empty')
        return v

class CommentEditRequest(BaseModel):
    """Request schema for editing comments."""
    content: str = Field(..., min_length=1, max_length=10000)

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Comment content cannot be empty')
        return v

class CommentRead(BaseModel):
    """Complete comment response schema."""
    id: int
    content: str
    content_html: Optional[str] = None
    task_id: int
    user: Optional[CommentUserInfo] = None
    thread_info: CommentThreadInfo
    engagement: CommentEngagement
    mentions: List[MentionRead] = []
    attachments: List[AttachmentRead] = []
    status: CommentStatus
    timestamps: CommentTimestamps
    
    # Optional nested replies for threaded display
    replies: Optional[List["CommentRead"]] = []

class CommentListResponse(BaseModel):
    """Response schema for comment lists."""
    comments: List[CommentRead]
    total_comments: int
    has_more: bool
    pagination: Dict[str, Any]

class CommentThreadResponse(BaseModel):
    """Response for comment thread queries."""
    thread_root_id: int
    thread_structure: Dict[str, Any]
    total_comments: int
    max_depth_reached: bool

# ===== REACTION SCHEMAS =====

class ReactionCreate(BaseModel):
    """Schema for creating comment reactions."""
    emoji: str = Field(..., min_length=1, max_length=10)
    reaction_type: str = "emoji"

class ReactionRead(BaseModel):
    """Schema for reading reaction information."""
    id: int
    emoji: str
    reaction_type: str
    user: CommentUserInfo
    created_at: datetime

class LikeResponse(BaseModel):
    """Response for comment like actions."""
    message: str
    liked: bool
    like_count: int

# ===== ACTIVITY SCHEMAS =====

class ActivityRead(BaseModel):
    """Schema for comment activity records."""
    id: int
    activity_type: str
    description: str
    user: CommentUserInfo
    activity_data: Optional[Dict[str, Any]] = None
    created_at: datetime

class CommentAnalytics(BaseModel):
    """Comment analytics and metrics."""
    total_comments: int
    total_threads: int
    average_thread_depth: float
    most_liked_comment_id: Optional[int] = None
    most_replied_comment_id: Optional[int] = None
    top_commenters: List[Dict[str, Any]] = []
    activity_timeline: List[Dict[str, Any]] = []

# ===== QUERY PARAMETER SCHEMAS =====

class CommentQueryParams(BaseModel):
    """Query parameters for comment listing."""
    include_threads: bool = True
    sort_by: CommentSortBy = CommentSortBy.CREATED_AT
    sort_order: CommentSortOrder = CommentSortOrder.ASC
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

class MentionQueryParams(BaseModel):
    """Query parameters for mention searches."""
    q: str = Field(..., min_length=1, description="Search query")
    task_id: Optional[int] = None
    limit: int = Field(10, ge=1, le=50)

class UserMentionQueryParams(BaseModel):
    """Query parameters for user mention listings."""
    unread_only: bool = False
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

# ===== RESPONSE WRAPPERS =====

class CommentResponse(BaseModel):
    """Standard comment API response."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Union[CommentRead, CommentListResponse, CommentThreadResponse]] = None
    errors: Optional[List[str]] = None

class MentionListResponse(BaseModel):
    """Response for mention listings."""
    mentions: List[UserMentionResponse]
    total_unread: int
    pagination: Dict[str, Any]

class MentionSuggestionsResponse(BaseModel):
    """Response for mention suggestions."""
    suggestions: List[MentionSuggestion]

class AttachmentListResponse(BaseModel):
    """Response for attachment listings."""
    attachments: List[AttachmentRead]
    total_attachments: int
    total_size: int
    has_images: bool

# ===== WEBSOCKET SCHEMAS =====

class CommentWebSocketMessage(BaseModel):
    """WebSocket message for real-time comment updates."""
    type: str  # "comment_created", "comment_edited", "comment_deleted", "mention_created"
    task_id: int
    comment_id: Optional[int] = None
    user_id: UUID
    data: Dict[str, Any]
    timestamp: datetime

class CommentNotification(BaseModel):
    """Comment notification schema."""
    id: str
    type: str  # "mention", "reply", "like"
    title: str
    message: str
    comment_id: int
    task_id: int
    sender: CommentUserInfo
    recipient_id: UUID
    is_read: bool = False
    created_at: datetime
    action_url: str

# Enable forward references
CommentRead.model_rebuild()

# ===== VALIDATION HELPERS =====

class CommentValidationError(Exception):
    """Custom exception for comment validation errors."""
    pass

def validate_mention_format(mention_text: str) -> bool:
    """Validate mention text format."""
    if not mention_text.startswith('@'):
        return False
    if len(mention_text) < 2:
        return False
    return True

def validate_thread_depth(depth: int, max_depth: int = 10) -> bool:
    """Validate thread depth limits."""
    return 0 <= depth <= max_depth

def sanitize_html_content(content: str) -> str:
    """Sanitize HTML content for safe display."""
    # Basic HTML sanitization - in production, use a proper HTML sanitizer
    import re
    
    # Allow basic formatting tags
    allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'code', 'pre', 'br', 'p']
    pattern = r'<(?!(?:' + '|'.join(allowed_tags) + r'|\/(?:' + '|'.join(allowed_tags) + r'))\b)[^>]*>'
    
    return re.sub(pattern, '', content)