"""
Search API endpoints for TeamFlow.
Provides advanced search, filtering, and search management capabilities.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.search import (
    SavedSearch, SearchHistory, SearchFilter, SearchAnalytics,
    SearchSuggestion, SearchIndexEntry, SearchScope
)
from app.models.user import User
from app.schemas.search import (
    AdvancedSearchRequest, SearchResponse, QuickSearchRequest, QuickSearchResponse,
    SavedSearchRequest, SavedSearchResponse, SearchFilterRequest, SearchFilterResponse,
    SearchHistoryResponse, SearchAnalyticsResponse, SearchSuggestionResponse,
    BulkIndexRequest, BulkIndexResponse
)
from app.schemas.user import UserRead
from app.services.search import SearchService, SearchIndexService


router = APIRouter(prefix="/search", tags=["search"])
search_service = SearchService()
index_service = SearchIndexService()


@router.post("/advanced", response_model=SearchResponse)
async def advanced_search(
    request: AdvancedSearchRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform advanced search with filters, sorting, and faceting.
    
    Features:
    - Full-text search across multiple entity types
    - Advanced filtering and faceting
    - Customizable sorting
    - Result highlighting
    - Pagination support
    """
    return await search_service.search(request, current_user, db)


@router.post("/quick", response_model=QuickSearchResponse)
async def quick_search(
    request: QuickSearchRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform quick search with limited results for autocomplete/suggestions.
    
    Features:
    - Fast response for typeahead search
    - Limited result set
    - Relevance-based sorting
    """
    return await search_service.quick_search(request, current_user, db)


@router.get("/suggestions", response_model=List[SearchSuggestionResponse])
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Search query to get suggestions for"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on query and user history.
    
    Features:
    - Query-based suggestions
    - Popular search terms
    - User-specific suggestions
    """
    try:
        # Get suggestions from database
        suggestions = db.query(SearchSuggestion).filter(
            SearchSuggestion.organization_id == current_user.organization_id,
            SearchSuggestion.suggestion_text.ilike(f"%{query}%"),
            SearchSuggestion.is_active == True
        ).order_by(desc(SearchSuggestion.usage_count)).limit(limit).all()
        
        return [
            SearchSuggestionResponse(
                id=s.id,
                suggestion_text=s.suggestion_text,
                suggestion_type=s.suggestion_type,
                usage_count=s.usage_count
            )
            for s in suggestions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")


@router.post("/saved", response_model=SavedSearchResponse)
async def save_search(
    request: SavedSearchRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a search query for future use.
    
    Features:
    - Save complex search queries
    - Name and describe searches
    - Share searches with others
    - Schedule search notifications
    """
    try:
        # Create saved search
        saved_search = SavedSearch(
            name=request.name,
            description=request.description,
            search_query=request.search_query,
            search_scope=request.search_scope,
            filters=request.filters,
            sort_config=request.sort_config,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            is_public=request.is_public,
            is_default=request.is_default,
            notification_enabled=request.notification_enabled,
            notification_frequency=request.notification_frequency
        )
        
        db.add(saved_search)
        db.commit()
        db.refresh(saved_search)
        
        return SavedSearchResponse(
            id=saved_search.id,
            name=saved_search.name,
            description=saved_search.description,
            search_query=saved_search.search_query,
            search_scope=saved_search.search_scope,
            filters=saved_search.filters,
            sort_config=saved_search.sort_config,
            is_public=saved_search.is_public,
            is_default=saved_search.is_default,
            notification_enabled=saved_search.notification_enabled,
            notification_frequency=saved_search.notification_frequency,
            usage_count=saved_search.usage_count,
            created_at=saved_search.created_at,
            updated_at=saved_search.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving search: {str(e)}")


@router.get("/saved", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    include_public: bool = Query(True, description="Include public saved searches"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's saved searches and optionally public searches.
    
    Features:
    - User's personal saved searches
    - Public/shared searches
    - Usage statistics
    """
    try:
        query = db.query(SavedSearch).filter(
            SavedSearch.organization_id == current_user.organization_id
        )
        
        if include_public:
            query = query.filter(
                or_(
                    SavedSearch.user_id == current_user.id,
                    SavedSearch.is_public == True
                )
            )
        else:
            query = query.filter(SavedSearch.user_id == current_user.id)
        
        saved_searches = query.order_by(desc(SavedSearch.updated_at)).all()
        
        return [
            SavedSearchResponse(
                id=s.id,
                name=s.name,
                description=s.description,
                search_query=s.search_query,
                search_scope=s.search_scope,
                filters=s.filters,
                sort_config=s.sort_config,
                is_public=s.is_public,
                is_default=s.is_default,
                notification_enabled=s.notification_enabled,
                notification_frequency=s.notification_frequency,
                usage_count=s.usage_count,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
            for s in saved_searches
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting saved searches: {str(e)}")


@router.get("/saved/{search_id}", response_model=SavedSearchResponse)
async def get_saved_search(
    search_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific saved search by ID."""
    try:
        saved_search = db.query(SavedSearch).filter(
            SavedSearch.id == search_id,
            SavedSearch.organization_id == current_user.organization_id,
            or_(
                SavedSearch.user_id == current_user.id,
                SavedSearch.is_public == True
            )
        ).first()
        
        if not saved_search:
            raise HTTPException(status_code=404, detail="Saved search not found")
        
        # Increment usage count
        saved_search.usage_count += 1
        saved_search.last_used_at = datetime.utcnow()
        db.commit()
        
        return SavedSearchResponse(
            id=saved_search.id,
            name=saved_search.name,
            description=saved_search.description,
            search_query=saved_search.search_query,
            search_scope=saved_search.search_scope,
            filters=saved_search.filters,
            sort_config=saved_search.sort_config,
            is_public=saved_search.is_public,
            is_default=saved_search.is_default,
            notification_enabled=saved_search.notification_enabled,
            notification_frequency=saved_search.notification_frequency,
            usage_count=saved_search.usage_count,
            created_at=saved_search.created_at,
            updated_at=saved_search.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting saved search: {str(e)}")


@router.put("/saved/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: int,
    request: SavedSearchRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a saved search."""
    try:
        saved_search = db.query(SavedSearch).filter(
            SavedSearch.id == search_id,
            SavedSearch.user_id == current_user.id,
            SavedSearch.organization_id == current_user.organization_id
        ).first()
        
        if not saved_search:
            raise HTTPException(status_code=404, detail="Saved search not found")
        
        # Update fields
        saved_search.name = request.name
        saved_search.description = request.description
        saved_search.search_query = request.search_query
        saved_search.search_scope = request.search_scope
        saved_search.filters = request.filters
        saved_search.sort_config = request.sort_config
        saved_search.is_public = request.is_public
        saved_search.is_default = request.is_default
        saved_search.notification_enabled = request.notification_enabled
        saved_search.notification_frequency = request.notification_frequency
        saved_search.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(saved_search)
        
        return SavedSearchResponse(
            id=saved_search.id,
            name=saved_search.name,
            description=saved_search.description,
            search_query=saved_search.search_query,
            search_scope=saved_search.search_scope,
            filters=saved_search.filters,
            sort_config=saved_search.sort_config,
            is_public=saved_search.is_public,
            is_default=saved_search.is_default,
            notification_enabled=saved_search.notification_enabled,
            notification_frequency=saved_search.notification_frequency,
            usage_count=saved_search.usage_count,
            created_at=saved_search.created_at,
            updated_at=saved_search.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating saved search: {str(e)}")


@router.delete("/saved/{search_id}")
async def delete_saved_search(
    search_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a saved search."""
    try:
        saved_search = db.query(SavedSearch).filter(
            SavedSearch.id == search_id,
            SavedSearch.user_id == current_user.id,
            SavedSearch.organization_id == current_user.organization_id
        ).first()
        
        if not saved_search:
            raise HTTPException(status_code=404, detail="Saved search not found")
        
        db.delete(saved_search)
        db.commit()
        
        return {"message": "Saved search deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting saved search: {str(e)}")


@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of history entries"),
    days: int = Query(30, ge=1, le=365, description="Days of history to retrieve"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's search history.
    
    Features:
    - Recent search queries
    - Search performance metrics
    - Frequent search patterns
    """
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        history = db.query(SearchHistory).filter(
            SearchHistory.user_id == current_user.id,
            SearchHistory.organization_id == current_user.organization_id,
            SearchHistory.searched_at >= since_date
        ).order_by(desc(SearchHistory.searched_at)).limit(limit).all()
        
        return [
            SearchHistoryResponse(
                id=h.id,
                search_query=h.search_query,
                search_scope=h.search_scope,
                filters_used=h.filters_used,
                results_count=h.results_count,
                search_duration_ms=h.search_duration_ms,
                searched_at=h.searched_at
            )
            for h in history
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search history: {str(e)}")


@router.get("/analytics", response_model=SearchAnalyticsResponse)
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Days of analytics to retrieve"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search analytics and statistics.
    
    Features:
    - Search volume trends
    - Popular search terms
    - Performance metrics
    - User search patterns
    """
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get basic search statistics
        total_searches = db.query(SearchHistory).filter(
            SearchHistory.organization_id == current_user.organization_id,
            SearchHistory.searched_at >= since_date
        ).count()
        
        # Get average search duration
        avg_duration = db.query(func.avg(SearchHistory.search_duration_ms)).filter(
            SearchHistory.organization_id == current_user.organization_id,
            SearchHistory.searched_at >= since_date
        ).scalar() or 0
        
        # Get search volume by day
        daily_searches = db.query(
            func.date(SearchHistory.searched_at).label('date'),
            func.count().label('count')
        ).filter(
            SearchHistory.organization_id == current_user.organization_id,
            SearchHistory.searched_at >= since_date
        ).group_by(func.date(SearchHistory.searched_at)).order_by('date').all()
        
        # Get popular search terms
        popular_terms = db.query(
            SearchHistory.search_query,
            func.count().label('count')
        ).filter(
            SearchHistory.organization_id == current_user.organization_id,
            SearchHistory.searched_at >= since_date,
            SearchHistory.search_query.isnot(None),
            SearchHistory.search_query != ""
        ).group_by(SearchHistory.search_query).order_by(desc('count')).limit(10).all()
        
        # Get search scope distribution
        scope_distribution = db.query(
            SearchHistory.search_scope,
            func.count().label('count')
        ).filter(
            SearchHistory.organization_id == current_user.organization_id,
            SearchHistory.searched_at >= since_date
        ).group_by(SearchHistory.search_scope).all()
        
        return SearchAnalyticsResponse(
            total_searches=total_searches,
            average_search_duration_ms=int(avg_duration),
            search_volume_trend=[
                {"date": str(day.date), "count": day.count}
                for day in daily_searches
            ],
            popular_search_terms=[
                {"term": term.search_query, "count": term.count}
                for term in popular_terms
            ],
            search_scope_distribution=[
                {"scope": scope.search_scope, "count": scope.count}
                for scope in scope_distribution
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search analytics: {str(e)}")


@router.post("/filters", response_model=SearchFilterResponse)
async def create_search_filter(
    request: SearchFilterRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a reusable search filter.
    
    Features:
    - Save complex filter configurations
    - Share filters with team
    - Predefined filter templates
    """
    try:
        search_filter = SearchFilter(
            name=request.name,
            description=request.description,
            filter_type=request.filter_type,
            filter_config=request.filter_config,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            is_public=request.is_public
        )
        
        db.add(search_filter)
        db.commit()
        db.refresh(search_filter)
        
        return SearchFilterResponse(
            id=search_filter.id,
            name=search_filter.name,
            description=search_filter.description,
            filter_type=search_filter.filter_type,
            filter_config=search_filter.filter_config,
            is_public=search_filter.is_public,
            usage_count=search_filter.usage_count,
            created_at=search_filter.created_at,
            updated_at=search_filter.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating search filter: {str(e)}")


@router.get("/filters", response_model=List[SearchFilterResponse])
async def get_search_filters(
    include_public: bool = Query(True, description="Include public search filters"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available search filters."""
    try:
        query = db.query(SearchFilter).filter(
            SearchFilter.organization_id == current_user.organization_id
        )
        
        if include_public:
            query = query.filter(
                or_(
                    SearchFilter.user_id == current_user.id,
                    SearchFilter.is_public == True
                )
            )
        else:
            query = query.filter(SearchFilter.user_id == current_user.id)
        
        filters = query.order_by(desc(SearchFilter.updated_at)).all()
        
        return [
            SearchFilterResponse(
                id=f.id,
                name=f.name,
                description=f.description,
                filter_type=f.filter_type,
                filter_config=f.filter_config,
                is_public=f.is_public,
                usage_count=f.usage_count,
                created_at=f.created_at,
                updated_at=f.updated_at
            )
            for f in filters
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search filters: {str(e)}")


@router.post("/index/bulk", response_model=BulkIndexResponse)
async def bulk_index_entities(
    request: BulkIndexRequest,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger bulk indexing of entities for search.
    
    Features:
    - Index specific entity types
    - Force reindexing of existing content
    - Background processing for large datasets
    """
    try:
        if request.background:
            # Run indexing in background
            background_tasks.add_task(
                _background_bulk_index,
                request.entity_types,
                current_user.organization_id,
                request.force_reindex
            )
            
            return BulkIndexResponse(
                message="Bulk indexing started in background",
                started_at=datetime.utcnow(),
                is_background=True
            )
        else:
            # Run indexing synchronously
            results = {}
            for entity_type in request.entity_types:
                result = index_service.bulk_index(
                    entity_type, current_user.organization_id, db, request.force_reindex
                )
                results[entity_type] = result
            
            return BulkIndexResponse(
                message="Bulk indexing completed",
                results=results,
                completed_at=datetime.utcnow(),
                is_background=False
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting bulk indexing: {str(e)}")


@router.post("/index/{entity_type}/{entity_id}")
async def index_entity(
    entity_type: str,
    entity_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Index a specific entity for search."""
    try:
        success = index_service.index_entity(entity_type, entity_id, db)
        
        if success:
            return {"message": f"Successfully indexed {entity_type} {entity_id}"}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to index {entity_type} {entity_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing entity: {str(e)}")


async def _background_bulk_index(entity_types: List[str], organization_id: int, force_reindex: bool):
    """Background task for bulk indexing."""
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            for entity_type in entity_types:
                await index_service.bulk_index_async(entity_type, organization_id, db, force_reindex)
        except Exception as e:
            print(f"Background bulk index error: {e}")
            await db.rollback()
        else:
            await db.commit()