"""
Advanced search and filtering models for TeamFlow.
Supports full-text search, faceted filtering, and saved searches.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class SearchScope(str, Enum):
    """Search scope options."""
    
    ALL = "all"
    TASKS = "tasks"
    PROJECTS = "projects"
    USERS = "users"
    FILES = "files"
    COMMENTS = "comments"
    TIME_ENTRIES = "time_entries"


class SearchOperator(str, Enum):
    """Search operators for filters."""
    
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    REGEX = "regex"


class SortDirection(str, Enum):
    """Sort direction options."""
    
    ASC = "asc"
    DESC = "desc"


class SavedSearch(Base):
    """Model for saved search queries."""
    
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Search identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    search_uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Ownership and organization
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Search configuration
    search_query = Column(Text, nullable=True)  # Full-text search query
    search_scope = Column(String(20), default=SearchScope.ALL.value, nullable=False)
    filters = Column(JSON, nullable=True)  # Advanced filters as JSON
    sort_config = Column(JSON, nullable=True)  # Sort configuration
    
    # Sharing and visibility
    is_public = Column(Boolean, default=False, nullable=False)
    is_shared = Column(Boolean, default=False, nullable=False)
    shared_with_team = Column(Boolean, default=False, nullable=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    organization = relationship("Organization")
    shared_users = relationship("SavedSearchShare", back_populates="saved_search", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SavedSearch(id={self.id}, name='{self.name}', scope='{self.search_scope}')>"
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()


class SavedSearchShare(Base):
    """Model for sharing saved searches with specific users."""
    
    __tablename__ = "saved_search_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    
    saved_search_id = Column(Integer, ForeignKey("saved_searches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Sharing permissions
    can_edit = Column(Boolean, default=False, nullable=False)
    can_reshare = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    saved_search = relationship("SavedSearch", back_populates="shared_users")
    user = relationship("User", foreign_keys=[user_id])
    sharer = relationship("User", foreign_keys=[shared_by])
    
    def __repr__(self):
        return f"<SavedSearchShare(saved_search_id={self.saved_search_id}, user_id={self.user_id})>"


class SearchHistory(Base):
    """Model for tracking user search history."""
    
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User and organization
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Search details
    search_query = Column(Text, nullable=True)
    search_scope = Column(String(20), nullable=False)
    filters_used = Column(JSON, nullable=True)
    
    # Results metadata
    results_count = Column(Integer, nullable=False, default=0)
    search_duration_ms = Column(Integer, nullable=True)  # Search execution time
    
    # Search context
    session_id = Column(String(36), nullable=True)  # For grouping related searches
    referrer_page = Column(String(255), nullable=True)  # Where search was initiated
    
    # Metadata
    searched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, query='{self.search_query[:50]}...')>"


class SearchIndexEntry(Base):
    """Model for search index entries to support full-text search."""
    
    __tablename__ = "search_index"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Indexed content
    entity_type = Column(String(50), nullable=False)  # 'task', 'project', 'user', etc.
    entity_id = Column(Integer, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Searchable content
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Space-separated tags for tag search
    search_metadata = Column(JSON, nullable=True)  # Additional searchable metadata
    
    # Search optimization
    search_vector = Column(Text, nullable=True)  # Pre-computed search vector
    boost_score = Column(Integer, default=1, nullable=False)  # Relevance boost
    
    # Status and timestamps
    is_active = Column(Boolean, default=True, nullable=False)
    indexed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<SearchIndexEntry(entity_type='{self.entity_type}', entity_id={self.entity_id})>"
    
    @property
    def searchable_content(self) -> str:
        """Get combined searchable content."""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.content:
            parts.append(self.content)
        if self.tags:
            parts.append(self.tags)
        return " ".join(parts)


class SearchFilter(Base):
    """Model for predefined search filters."""
    
    __tablename__ = "search_filters"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Filter identification
    name = Column(String(255), nullable=False)
    key = Column(String(100), nullable=False)  # Unique key for the filter
    category = Column(String(100), nullable=False)  # Group filters by category
    
    # Filter configuration
    entity_type = Column(String(50), nullable=False)  # Which entity this filter applies to
    field_name = Column(String(100), nullable=False)  # Database field to filter on
    field_type = Column(String(50), nullable=False)  # 'string', 'number', 'date', 'boolean', 'enum'
    
    # Filter options
    available_operators = Column(JSON, nullable=False)  # List of supported operators
    default_operator = Column(String(20), nullable=False)
    
    # UI configuration
    display_order = Column(Integer, default=0, nullable=False)
    is_advanced = Column(Boolean, default=False, nullable=False)  # Show in advanced search only
    placeholder_text = Column(String(255), nullable=True)
    help_text = Column(Text, nullable=True)
    
    # Options for enum/select filters
    filter_options = Column(JSON, nullable=True)  # Available options for dropdowns
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Organization scope
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Null for global filters
    
    # Relationships
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<SearchFilter(key='{self.key}', entity_type='{self.entity_type}')>"


class SearchSuggestion(Base):
    """Model for search suggestions and autocomplete."""
    
    __tablename__ = "search_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Suggestion content
    suggestion_text = Column(String(500), nullable=False)
    suggestion_type = Column(String(50), nullable=False)  # 'query', 'filter', 'tag', 'user', 'project'
    
    # Context
    entity_type = Column(String(50), nullable=True)  # Associated entity type
    entity_id = Column(Integer, nullable=True)  # Associated entity ID
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=1, nullable=False)
    last_used = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<SearchSuggestion(text='{self.suggestion_text}', type='{self.suggestion_type}')>"
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()


class SearchAnalytics(Base):
    """Model for search analytics and reporting."""
    
    __tablename__ = "search_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Analytics period
    date = Column(DateTime, nullable=False)  # Date for this analytics record
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Search metrics
    total_searches = Column(Integer, default=0, nullable=False)
    unique_users = Column(Integer, default=0, nullable=False)
    avg_search_duration_ms = Column(Integer, default=0, nullable=False)
    
    # Popular searches
    popular_queries = Column(JSON, nullable=True)  # Top search queries
    popular_filters = Column(JSON, nullable=True)  # Most used filters
    popular_scopes = Column(JSON, nullable=True)  # Most searched scopes
    
    # Search success metrics
    zero_result_searches = Column(Integer, default=0, nullable=False)
    one_result_searches = Column(Integer, default=0, nullable=False)
    multiple_result_searches = Column(Integer, default=0, nullable=False)
    
    # User behavior
    avg_results_per_search = Column(Integer, default=0, nullable=False)
    saved_searches_created = Column(Integer, default=0, nullable=False)
    
    # Created timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<SearchAnalytics(date={self.date.date()}, org_id={self.organization_id})>"