"""
Advanced search and filtering schemas for TeamFlow API.
Defines request/response models for search operations and filter management.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.search import SearchScope, SearchOperator


class SortDirection(str, Enum):
    """Sort direction enum."""
    ASC = "asc"
    DESC = "desc"


class SearchRequestFilter(BaseModel):
    """Single filter in a search request."""
    
    field: str = Field(..., description="Field name to filter on")
    operator: SearchOperator = Field(..., description="Filter operator")
    value: Union[str, int, float, bool, List[Any], None] = Field(..., description="Filter value")
    values: Optional[List[Any]] = Field(None, description="Multiple values for IN/BETWEEN operators")
    
    class Config:
        use_enum_values = True


class SearchSortConfig(BaseModel):
    """Sort configuration for search results."""
    
    field: str = Field(..., description="Field to sort by")
    direction: SortDirection = Field(SortDirection.DESC, description="Sort direction")
    boost: Optional[float] = Field(None, ge=0.1, le=10.0, description="Relevance boost multiplier")
    
    class Config:
        use_enum_values = True


class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search operations."""
    
    # Basic search
    query: Optional[str] = Field(None, max_length=500, description="Full-text search query")
    scope: SearchScope = Field(SearchScope.ALL, description="Search scope")
    
    # Advanced filtering
    filters: Optional[List[SearchRequestFilter]] = Field(None, description="Advanced filters")
    
    # Sorting and pagination
    sort: Optional[List[SearchSortConfig]] = Field(None, description="Sort configuration")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Results per page")
    
    # Search options
    include_archived: bool = Field(False, description="Include archived/deleted items")
    fuzzy_matching: bool = Field(True, description="Enable fuzzy text matching")
    highlight_matches: bool = Field(True, description="Highlight search matches in results")
    
    # Context filters
    project_ids: Optional[List[int]] = Field(None, description="Limit search to specific projects")
    user_ids: Optional[List[int]] = Field(None, description="Limit search to specific users")
    date_range_start: Optional[datetime] = Field(None, description="Start date for date-based filtering")
    date_range_end: Optional[datetime] = Field(None, description="End date for date-based filtering")
    
    # Performance options
    timeout_ms: Optional[int] = Field(None, ge=100, le=30000, description="Search timeout in milliseconds")
    
    class Config:
        use_enum_values = True


class SearchResultItem(BaseModel):
    """Individual search result item."""
    
    # Basic item info
    id: int
    type: str = Field(..., description="Entity type (task, project, user, file, etc.)")
    title: str
    content: Optional[str] = Field(None, description="Content snippet")
    
    # Relevance and matching
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    highlights: Optional[Dict[str, List[str]]] = Field(None, description="Highlighted text matches")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional item metadata")
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Context
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
    
    # URLs and navigation
    url: Optional[str] = Field(None, description="Direct link to the item")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Response model for search operations."""
    
    # Results
    items: List[SearchResultItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
    # Search metadata
    query: Optional[str]
    scope: str
    search_duration_ms: int
    
    # Facets and aggregations
    facets: Optional[Dict[str, Dict[str, int]]] = Field(None, description="Faceted search results")
    suggestions: Optional[List[str]] = Field(None, description="Search suggestions")
    
    # Search quality indicators
    has_more_results: bool
    estimated_total: Optional[int] = Field(None, description="Estimated total results if different from total_count")
    
    class Config:
        from_attributes = True


class SavedSearchRequest(BaseModel):
    """Request model for creating/updating saved searches."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Search name")
    description: Optional[str] = Field(None, max_length=1000, description="Search description")
    
    # Search configuration
    search_query: Optional[str] = Field(None, max_length=500, description="Full-text search query")
    search_scope: SearchScope = Field(SearchScope.ALL, description="Search scope")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    sort_config: Optional[Dict[str, Any]] = Field(None, description="Sort configuration")
    
    # Sharing settings
    is_public: bool = Field(False, description="Make search publicly visible")
    is_default: bool = Field(False, description="Set as default search")
    
    # Notification settings
    notification_enabled: bool = Field(False, description="Enable notifications for this search")
    notification_frequency: Optional[str] = Field(None, description="Notification frequency")
    
    class Config:
        use_enum_values = True


class SavedSearchResponse(BaseModel):
    """Response model for saved searches."""
    
    id: int
    name: str
    description: Optional[str]
    
    # Search configuration
    search_query: Optional[str]
    search_scope: str
    filters: Optional[Dict[str, Any]]
    sort_config: Optional[Dict[str, Any]]
    
    # Sharing and visibility
    is_public: bool
    is_default: bool
    
    # Notification settings
    notification_enabled: bool
    notification_frequency: Optional[str]
    
    # Usage tracking
    usage_count: int
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SavedSearchListResponse(BaseModel):
    """Response model for listing saved searches."""
    
    searches: List[SavedSearchResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True


class SearchFilterDefinition(BaseModel):
    """Definition of an available search filter."""
    
    key: str
    name: str
    category: str
    entity_type: str
    field_name: str
    field_type: str
    
    # Filter configuration
    available_operators: List[str]
    default_operator: str
    
    # UI configuration
    display_order: int
    is_advanced: bool
    placeholder_text: Optional[str]
    help_text: Optional[str]
    
    # Options for select/enum filters
    filter_options: Optional[List[Dict[str, Any]]] = Field(None, description="Available filter options")
    
    class Config:
        from_attributes = True


class SearchFiltersResponse(BaseModel):
    """Response model for available search filters."""
    
    filters: List[SearchFilterDefinition]
    categories: List[str] = Field(..., description="Available filter categories")
    
    class Config:
        from_attributes = True


class SearchSuggestionResponse(BaseModel):
    """Response model for search suggestions."""
    
    suggestions: List[str]
    suggestion_types: Dict[str, List[str]] = Field(..., description="Suggestions grouped by type")
    
    class Config:
        from_attributes = True


class QuickSearchRequest(BaseModel):
    """Request model for quick search (simplified)."""
    
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    scope: Optional[SearchScope] = Field(None, description="Limit search scope")
    limit: int = Field(10, ge=1, le=50, description="Maximum results to return")
    
    class Config:
        use_enum_values = True


class QuickSearchResponse(BaseModel):
    """Response model for quick search results."""
    
    results: List[SearchResultItem]
    total_found: int
    search_duration_ms: int
    
    class Config:
        from_attributes = True


class SearchHistoryItem(BaseModel):
    """Individual search history item."""
    
    id: int
    search_query: Optional[str]
    search_scope: str
    results_count: int
    searched_at: datetime
    
    class Config:
        from_attributes = True


class SearchHistoryResponse(BaseModel):
    """Response model for search history."""
    
    history: List[SearchHistoryItem]
    total_count: int
    
    class Config:
        from_attributes = True


class SearchAnalyticsResponse(BaseModel):
    """Response model for search analytics."""
    
    # Basic metrics
    total_searches: int
    average_search_duration_ms: int
    
    # Trends and distributions
    search_volume_trend: List[Dict[str, Any]]
    popular_search_terms: List[Dict[str, Any]]
    search_scope_distribution: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class BulkIndexRequest(BaseModel):
    """Request model for bulk indexing operations."""
    
    entity_type: str = Field(..., description="Type of entities to index")
    entity_ids: Optional[List[int]] = Field(None, description="Specific entity IDs (null for all)")
    force_reindex: bool = Field(False, description="Force reindexing even if already indexed")
    
    class Config:
        from_attributes = True


class IndexStatusResponse(BaseModel):
    """Response model for indexing status."""
    
    total_entities: int
    indexed_entities: int
    pending_entities: int
    failed_entities: int
    last_index_update: Optional[datetime]
    
    # Per-entity type breakdown
    entity_type_status: Dict[str, Dict[str, int]]
    
    class Config:
        from_attributes = True


class SearchFilterRequest(BaseModel):
    """Request model for creating search filters."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Filter name")
    description: Optional[str] = Field(None, max_length=1000, description="Filter description")
    filter_type: str = Field(..., description="Type of filter (predefined, custom)")
    filter_config: Dict[str, Any] = Field(..., description="Filter configuration")
    is_public: bool = Field(False, description="Make filter publicly available")
    
    class Config:
        from_attributes = True


class SearchFilterResponse(BaseModel):
    """Response model for search filters."""
    
    id: int
    name: str
    description: Optional[str]
    filter_type: str
    filter_config: Dict[str, Any]
    is_public: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SearchHistoryResponse(BaseModel):
    """Response model for individual search history item."""
    
    id: int
    search_query: Optional[str]
    search_scope: str
    filters_used: Optional[Dict[str, Any]]
    results_count: int
    search_duration_ms: int
    searched_at: datetime
    
    class Config:
        from_attributes = True


class SearchSuggestionResponse(BaseModel):
    """Response model for search suggestions."""
    
    id: int
    suggestion_text: str
    suggestion_type: str
    usage_count: int
    
    class Config:
        from_attributes = True


class BulkIndexRequest(BaseModel):
    """Request model for bulk indexing operations."""
    
    entity_types: List[str] = Field(..., description="Types of entities to index")
    force_reindex: bool = Field(False, description="Force reindexing even if already indexed")
    background: bool = Field(True, description="Run indexing in background")
    
    class Config:
        from_attributes = True


class BulkIndexResponse(BaseModel):
    """Response model for bulk indexing operations."""
    
    message: str
    results: Optional[Dict[str, Dict[str, int]]] = Field(None, description="Indexing results per entity type")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_background: bool = False
    
    class Config:
        from_attributes = True