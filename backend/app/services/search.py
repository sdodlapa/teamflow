"""
Advanced search service for TeamFlow.
Provides full-text search, filtering, and indexing capabilities.
"""
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from sqlalchemy import and_, or_, text, func, desc, asc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.models.search import (
    SavedSearch, SearchHistory, SearchIndexEntry, SearchFilter,
    SearchSuggestion, SearchAnalytics, SearchScope, SearchOperator
)
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserStatus
from app.models.file_management import FileUpload
from app.models.time_tracking import TaskTimeLog
from app.schemas.search import (
    AdvancedSearchRequest, SearchRequestFilter, SearchSortConfig,
    SearchResultItem, SearchResponse, SavedSearchRequest,
    QuickSearchRequest, QuickSearchResponse, SortDirection
)
from app.schemas.user import UserRead


class SearchIndexService:
    """Service for managing search index and content indexing."""
    
    def __init__(self):
        self.entity_indexers = {
            "task": self._index_task,
            "project": self._index_project,
            "user": self._index_user,
            "file": self._index_file,
            "time_entry": self._index_time_entry,
        }
    
    def index_entity(self, entity_type: str, entity_id: int, db: Session) -> bool:
        """Index a single entity for search."""
        try:
            indexer = self.entity_indexers.get(entity_type)
            if not indexer:
                return False
            
            return indexer(entity_id, db)
        except Exception as e:
            print(f"Error indexing {entity_type} {entity_id}: {e}")
            return False
    
    def _index_task(self, task_id: int, db: Session) -> bool:
        """Index a task for search."""
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            # Remove existing index entry
            db.query(SearchIndexEntry).filter(
                SearchIndexEntry.entity_type == "task",
                SearchIndexEntry.entity_id == task_id
            ).delete()
            
            # Create new index entry
            content_parts = [task.description] if task.description else []
            
            # Add comments content
            if task.comments:
                content_parts.extend([comment.content for comment in task.comments if comment.content])
            
            # Create tags from labels and status
            tags = []
            if task.labels:
                tags.extend(task.labels)
            tags.append(f"status:{task.status}")
            tags.append(f"priority:{task.priority}")
            if task.assigned_to:
                tags.append(f"assignee:{task.assigned_to}")
            
            # Build metadata
            metadata = {
                "project_id": task.project_id,
                "project_name": task.project.name if task.project else None,
                "status": task.status,
                "priority": task.priority,
                "assigned_to": task.assigned_to,
                "assignee_name": task.assignee.full_name if task.assignee else None,
                "created_by": task.created_by,
                "creator_name": task.creator.full_name if task.creator else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "estimated_hours": task.estimated_hours,
                "labels": task.labels,
                "comments_count": len(task.comments) if task.comments else 0,
            }
            
            index_entry = SearchIndexEntry(
                entity_type="task",
                entity_id=task_id,
                organization_id=task.organization_id,
                title=task.title,
                content=" ".join(content_parts),
                tags=" ".join(tags),
                search_metadata=metadata,
                boost_score=2 if task.priority in ["high", "urgent"] else 1
            )
            
            db.add(index_entry)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error indexing task {task_id}: {e}")
            return False
    
    def _index_project(self, project_id: int, db: Session) -> bool:
        """Index a project for search."""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            # Remove existing index entry
            db.query(SearchIndexEntry).filter(
                SearchIndexEntry.entity_type == "project",
                SearchIndexEntry.entity_id == project_id
            ).delete()
            
            # Create tags
            tags = [f"status:{project.status}"]
            if project.priority:
                tags.append(f"priority:{project.priority}")
            
            # Build metadata
            metadata = {
                "status": project.status,
                "priority": project.priority,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "created_by": project.created_by,
                "creator_name": project.creator.full_name if project.creator else None,
                "task_count": len(project.tasks) if project.tasks else 0,
                "member_count": len(project.members) if project.members else 0,
            }
            
            index_entry = SearchIndexEntry(
                entity_type="project",
                entity_id=project_id,
                organization_id=project.organization_id,
                title=project.name,
                content=project.description,
                tags=" ".join(tags),
                search_metadata=metadata,
                boost_score=3  # Projects get higher boost
            )
            
            db.add(index_entry)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error indexing project {project_id}: {e}")
            return False
    
    def _index_user(self, user_id: int, db: Session) -> bool:
        """Index a user for search."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Remove existing index entry
            db.query(SearchIndexEntry).filter(
                SearchIndexEntry.entity_type == "user",
                SearchIndexEntry.entity_id == user_id
            ).delete()
            
            # Create content from bio and other fields
            content_parts = []
            if user.bio:
                content_parts.append(user.bio)
            if user.job_title:
                content_parts.append(user.job_title)
            if user.department:
                content_parts.append(user.department)
            
            # Create tags
            tags = [f"status:{user.status}", f"role:{user.role}"]
            if user.department:
                tags.append(f"department:{user.department}")
            
            # Build metadata
            metadata = {
                "email": user.email,
                "role": user.role,
                "status": user.status,
                "job_title": user.job_title,
                "department": user.department,
                "organization_id": user.organization_id,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.status == UserStatus.ACTIVE,
            }
            
            index_entry = SearchIndexEntry(
                entity_type="user",
                entity_id=user_id,
                organization_id=user.organization_id,
                title=user.full_name,
                content=" ".join(content_parts),
                tags=" ".join(tags),
                search_metadata=metadata,
                boost_score=1
            )
            
            db.add(index_entry)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error indexing user {user_id}: {e}")
            return False
    
    def _index_file(self, file_id: int, db: Session) -> bool:
        """Index a file for search."""
        try:
            file_upload = db.query(FileUpload).filter(FileUpload.id == file_id).first()
            if not file_upload:
                return False
            
            # Remove existing index entry
            db.query(SearchIndexEntry).filter(
                SearchIndexEntry.entity_type == "file",
                SearchIndexEntry.entity_id == file_id
            ).delete()
            
            # Create tags
            tags = [f"type:{file_upload.file_type}", f"visibility:{file_upload.visibility}"]
            if file_upload.project_id:
                tags.append(f"project:{file_upload.project_id}")
            if file_upload.task_id:
                tags.append(f"task:{file_upload.task_id}")
            
            # Build metadata
            metadata = {
                "file_type": file_upload.file_type,
                "file_size": file_upload.file_size,
                "mime_type": file_upload.mime_type,
                "visibility": file_upload.visibility,
                "project_id": file_upload.project_id,
                "project_name": file_upload.project.name if file_upload.project else None,
                "task_id": file_upload.task_id,
                "uploaded_by": file_upload.uploaded_by,
                "uploader_name": file_upload.uploader.full_name if file_upload.uploader else None,
                "is_image": file_upload.is_image,
                "is_document": file_upload.is_document,
                "scan_status": file_upload.scan_status,
            }
            
            index_entry = SearchIndexEntry(
                entity_type="file",
                entity_id=file_id,
                organization_id=file_upload.organization_id,
                title=file_upload.original_filename,
                content=file_upload.description,
                tags=" ".join(tags),
                search_metadata=metadata,
                boost_score=1
            )
            
            db.add(index_entry)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error indexing file {file_id}: {e}")
            return False
    
    def _index_time_entry(self, entry_id: int, db: Session) -> bool:
        """Index a time entry for search."""
        try:
            entry = db.query(TaskTimeLog).filter(TaskTimeLog.id == entry_id).first()
            if not entry:
                return False
            
            # Remove existing index entry
            db.query(SearchIndexEntry).filter(
                SearchIndexEntry.entity_type == "time_entry",
                SearchIndexEntry.entity_id == entry_id
            ).delete()
            
            # Create tags
            tags = []
            if entry.task_id:
                tags.append(f"task:{entry.task_id}")
            if entry.task and entry.task.project_id:
                tags.append(f"project:{entry.task.project_id}")
            
            # Build metadata
            metadata = {
                "task_id": entry.task_id,
                "task_title": entry.task.title if entry.task else None,
                "project_id": entry.task.project_id if entry.task else None,
                "project_name": entry.task.project.name if entry.task and entry.task.project else None,
                "user_id": entry.user_id,
                "user_name": entry.user.full_name if entry.user else None,
                "hours_logged": float(entry.hours_logged) if entry.hours_logged else 0,
                "logged_date": entry.logged_date.isoformat() if entry.logged_date else None,
                "is_billable": entry.is_billable,
            }
            
            # Use task title and description for title/content
            title = f"Time Entry"
            if entry.task:
                title = f"Time Entry - {entry.task.title}"
            
            index_entry = SearchIndexEntry(
                entity_type="time_entry",
                entity_id=entry_id,
                organization_id=entry.organization_id,
                title=title,
                content=entry.description,
                tags=" ".join(tags),
                search_metadata=metadata,
                boost_score=1
            )
            
            db.add(index_entry)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error indexing time entry {entry_id}: {e}")
            return False
    
    def bulk_index(self, entity_type: str, organization_id: int, db: Session, force_reindex: bool = False) -> Dict[str, int]:
        """Bulk index entities of a specific type."""
        results = {"indexed": 0, "failed": 0, "skipped": 0}
        
        try:
            # Get entity query based on type
            if entity_type == "task":
                entities = db.query(Task).filter(Task.organization_id == organization_id).all()
            elif entity_type == "project":
                entities = db.query(Project).filter(Project.organization_id == organization_id).all()
            elif entity_type == "user":
                entities = db.query(User).filter(User.organization_id == organization_id).all()
            elif entity_type == "file":
                entities = db.query(FileUpload).filter(
                    FileUpload.organization_id == organization_id,
                    FileUpload.is_active == True
                ).all()
            elif entity_type == "time_entry":
                entities = db.query(TaskTimeLog).filter(TaskTimeLog.organization_id == organization_id).all()
            else:
                return results
            
            for entity in entities:
                # Check if already indexed
                if not force_reindex:
                    existing = db.query(SearchIndexEntry).filter(
                        SearchIndexEntry.entity_type == entity_type,
                        SearchIndexEntry.entity_id == entity.id,
                        SearchIndexEntry.organization_id == organization_id
                    ).first()
                    
                    if existing:
                        results["skipped"] += 1
                        continue
                
                # Index the entity
                if self.index_entity(entity_type, entity.id, db):
                    results["indexed"] += 1
                else:
                    results["failed"] += 1
            
            return results
            
        except Exception as e:
            print(f"Error in bulk indexing {entity_type}: {e}")
            return results


class SearchService:
    """Main search service for advanced search operations."""
    
    def __init__(self):
        self.index_service = SearchIndexService()
    
    async def search(
        self,
        request: AdvancedSearchRequest,
        user: UserRead,
        db: Session
    ) -> SearchResponse:
        """Perform advanced search with filters and sorting."""
        start_time = time.time()
        
        try:
            # Build base query
            query = db.query(SearchIndexEntry).filter(
                SearchIndexEntry.organization_id == user.organization_id,
                SearchIndexEntry.is_active == True
            )
            
            # Apply scope filter
            if request.scope != SearchScope.ALL:
                query = query.filter(SearchIndexEntry.entity_type == request.scope.value)
            
            # Apply text search
            if request.query:
                search_terms = request.query.lower().split()
                
                if request.fuzzy_matching:
                    # Use ILIKE for fuzzy matching
                    conditions = []
                    for term in search_terms:
                        term_condition = or_(
                            SearchIndexEntry.title.ilike(f"%{term}%"),
                            SearchIndexEntry.content.ilike(f"%{term}%"),
                            SearchIndexEntry.tags.ilike(f"%{term}%")
                        )
                        conditions.append(term_condition)
                    
                    if conditions:
                        query = query.filter(and_(*conditions))
                else:
                    # Exact matching
                    for term in search_terms:
                        query = query.filter(
                            or_(
                                SearchIndexEntry.title.contains(term),
                                SearchIndexEntry.content.contains(term),
                                SearchIndexEntry.tags.contains(term)
                            )
                        )
            
            # Apply advanced filters
            if request.filters:
                query = self._apply_filters(query, request.filters, db)
            
            # Apply context filters
            if request.project_ids:
                # Filter by projects through metadata
                project_conditions = []
                for project_id in request.project_ids:
                    project_conditions.append(
                        SearchIndexEntry.search_metadata.contains(f'"project_id": {project_id}')
                    )
                if project_conditions:
                    query = query.filter(or_(*project_conditions))
            
            if request.date_range_start or request.date_range_end:
                if request.date_range_start:
                    query = query.filter(SearchIndexEntry.indexed_at >= request.date_range_start)
                if request.date_range_end:
                    query = query.filter(SearchIndexEntry.indexed_at <= request.date_range_end)
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply sorting
            if request.sort:
                query = self._apply_sorting(query, request.sort)
            else:
                # Default sorting by relevance (boost_score) and recency
                query = query.order_by(
                    desc(SearchIndexEntry.boost_score),
                    desc(SearchIndexEntry.updated_at)
                )
            
            # Apply pagination
            offset = (request.page - 1) * request.page_size
            results = query.offset(offset).limit(request.page_size).all()
            
            # Convert to search result items
            items = []
            for result in results:
                item = self._convert_to_search_result(result, request.highlight_matches, request.query)
                if item:
                    items.append(item)
            
            # Calculate search duration
            search_duration_ms = int((time.time() - start_time) * 1000)
            
            # Record search in history
            await self._record_search_history(request, user, total_count, search_duration_ms, db)
            
            # Calculate pagination info
            total_pages = (total_count + request.page_size - 1) // request.page_size
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(request.query, user, db) if request.query else []
            
            return SearchResponse(
                items=items,
                total_count=total_count,
                page=request.page,
                page_size=request.page_size,
                total_pages=total_pages,
                query=request.query,
                scope=request.scope.value,
                search_duration_ms=search_duration_ms,
                suggestions=suggestions[:5],  # Limit suggestions
                has_more_results=total_count > (request.page * request.page_size)
            )
            
        except Exception as e:
            print(f"Search error: {e}")
            return SearchResponse(
                items=[],
                total_count=0,
                page=request.page,
                page_size=request.page_size,
                total_pages=0,
                query=request.query,
                scope=request.scope.value,
                search_duration_ms=int((time.time() - start_time) * 1000),
                has_more_results=False
            )
    
    def _apply_filters(self, query, filters: List[SearchRequestFilter], db: Session):
        """Apply advanced filters to search query."""
        for filter_item in filters:
            field = filter_item.field
            operator = filter_item.operator
            value = filter_item.value
            
            # Map filter field to database field or metadata path
            if field in ["title", "content", "tags"]:
                db_field = getattr(SearchIndexEntry, field)
                
                if operator == SearchOperator.EQUALS:
                    query = query.filter(db_field == value)
                elif operator == SearchOperator.NOT_EQUALS:
                    query = query.filter(db_field != value)
                elif operator == SearchOperator.CONTAINS:
                    query = query.filter(db_field.ilike(f"%{value}%"))
                elif operator == SearchOperator.NOT_CONTAINS:
                    query = query.filter(~db_field.ilike(f"%{value}%"))
                elif operator == SearchOperator.STARTS_WITH:
                    query = query.filter(db_field.ilike(f"{value}%"))
                elif operator == SearchOperator.ENDS_WITH:
                    query = query.filter(db_field.ilike(f"%{value}"))
            else:
                # Handle metadata filters
                if operator == SearchOperator.EQUALS:
                    query = query.filter(
                        SearchIndexEntry.search_metadata.contains(f'"{field}": "{value}"') |
                        SearchIndexEntry.search_metadata.contains(f'"{field}": {value}')
                    )
                elif operator == SearchOperator.IN and filter_item.values:
                    conditions = []
                    for val in filter_item.values:
                        conditions.append(
                            SearchIndexEntry.search_metadata.contains(f'"{field}": "{val}"') |
                            SearchIndexEntry.search_metadata.contains(f'"{field}": {val}')
                        )
                    query = query.filter(or_(*conditions))
        
        return query
    
    def _apply_sorting(self, query, sort_configs: List[SearchSortConfig]):
        """Apply sorting to search query."""
        for sort_config in sort_configs:
            field = sort_config.field
            direction = sort_config.direction
            
            if field in ["title", "created_at", "updated_at", "boost_score"]:
                db_field = getattr(SearchIndexEntry, field)
                if field == "created_at":
                    db_field = SearchIndexEntry.indexed_at
                
                if direction == SortDirection.DESC:
                    query = query.order_by(desc(db_field))
                else:
                    query = query.order_by(asc(db_field))
        
        return query
    
    def _convert_to_search_result(
        self,
        index_entry: SearchIndexEntry,
        highlight_matches: bool,
        search_query: Optional[str]
    ) -> Optional[SearchResultItem]:
        """Convert search index entry to search result item."""
        try:
            metadata = index_entry.search_metadata or {}
            
            # Calculate relevance score (simplified)
            score = min(index_entry.boost_score / 3.0, 1.0)
            
            # Generate highlights if requested
            highlights = {}
            if highlight_matches and search_query:
                highlights = self._generate_highlights(index_entry, search_query)
            
            # Build URL based on entity type
            url = self._generate_entity_url(index_entry.entity_type, index_entry.entity_id)
            
            return SearchResultItem(
                id=index_entry.entity_id,
                type=index_entry.entity_type,
                title=index_entry.title,
                content=index_entry.content[:200] + "..." if index_entry.content and len(index_entry.content) > 200 else index_entry.content,
                score=score,
                highlights=highlights if highlights else None,
                metadata=metadata,
                created_at=index_entry.indexed_at,
                updated_at=index_entry.updated_at,
                project_id=metadata.get("project_id"),
                project_name=metadata.get("project_name"),
                created_by=metadata.get("created_by"),
                created_by_name=metadata.get("creator_name") or metadata.get("user_name"),
                url=url
            )
            
        except Exception as e:
            print(f"Error converting search result: {e}")
            return None
    
    def _generate_highlights(self, index_entry: SearchIndexEntry, search_query: str) -> Dict[str, List[str]]:
        """Generate text highlights for search matches."""
        highlights = {}
        terms = search_query.lower().split()
        
        for field in ["title", "content"]:
            field_value = getattr(index_entry, field)
            if field_value:
                field_highlights = []
                for term in terms:
                    if term in field_value.lower():
                        # Simple highlighting - mark term with <mark> tags
                        highlighted = field_value.replace(
                            term, f"<mark>{term}</mark>",
                            # Case-insensitive replacement would be more complex
                        )
                        field_highlights.append(highlighted)
                
                if field_highlights:
                    highlights[field] = field_highlights
        
        return highlights
    
    def _generate_entity_url(self, entity_type: str, entity_id: int) -> Optional[str]:
        """Generate URL for entity based on type."""
        url_mapping = {
            "task": f"/tasks/{entity_id}",
            "project": f"/projects/{entity_id}",
            "user": f"/users/{entity_id}",
            "file": f"/files/{entity_id}",
            "time_entry": f"/time-tracking/{entity_id}",
        }
        return url_mapping.get(entity_type)
    
    async def _record_search_history(
        self,
        request: AdvancedSearchRequest,
        user: UserRead,
        results_count: int,
        duration_ms: int,
        db: Session
    ):
        """Record search in user's search history."""
        try:
            history_entry = SearchHistory(
                user_id=user.id,
                organization_id=user.organization_id,
                search_query=request.query,
                search_scope=request.scope.value,
                filters_used={"filters": [filter.dict() for filter in request.filters]} if request.filters else None,
                results_count=results_count,
                search_duration_ms=duration_ms
            )
            
            db.add(history_entry)
            db.commit()
            
        except Exception as e:
            print(f"Error recording search history: {e}")
            db.rollback()
    
    async def _generate_suggestions(
        self,
        query: str,
        user: UserRead,
        db: Session
    ) -> List[str]:
        """Generate search suggestions based on query and history."""
        try:
            suggestions = []
            
            # Get suggestions from search suggestions table
            suggestion_records = db.query(SearchSuggestion).filter(
                SearchSuggestion.organization_id == user.organization_id,
                SearchSuggestion.suggestion_text.ilike(f"%{query}%"),
                SearchSuggestion.is_active == True
            ).order_by(desc(SearchSuggestion.usage_count)).limit(10).all()
            
            suggestions.extend([s.suggestion_text for s in suggestion_records])
            
            return suggestions
            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return []
    
    async def quick_search(
        self,
        request: QuickSearchRequest,
        user: UserRead,
        db: Session
    ) -> QuickSearchResponse:
        """Perform quick search with limited results."""
        start_time = time.time()
        
        try:
            # Build simple query
            query = db.query(SearchIndexEntry).filter(
                SearchIndexEntry.organization_id == user.organization_id,
                SearchIndexEntry.is_active == True
            )
            
            # Apply scope filter if specified
            if request.scope:
                query = query.filter(SearchIndexEntry.entity_type == request.scope.value)
            
            # Apply text search
            search_terms = request.query.lower().split()
            conditions = []
            for term in search_terms:
                term_condition = or_(
                    SearchIndexEntry.title.ilike(f"%{term}%"),
                    SearchIndexEntry.content.ilike(f"%{term}%"),
                    SearchIndexEntry.tags.ilike(f"%{term}%")
                )
                conditions.append(term_condition)
            
            if conditions:
                query = query.filter(and_(*conditions))
            
            # Get total count
            total_found = query.count()
            
            # Get limited results with boost-based sorting
            results = query.order_by(
                desc(SearchIndexEntry.boost_score),
                desc(SearchIndexEntry.updated_at)
            ).limit(request.limit).all()
            
            # Convert to search result items
            items = []
            for result in results:
                item = self._convert_to_search_result(result, False, request.query)
                if item:
                    items.append(item)
            
            search_duration_ms = int((time.time() - start_time) * 1000)
            
            return QuickSearchResponse(
                results=items,
                total_found=total_found,
                search_duration_ms=search_duration_ms
            )
            
        except Exception as e:
            print(f"Quick search error: {e}")
            return QuickSearchResponse(
                results=[],
                total_found=0,
                search_duration_ms=int((time.time() - start_time) * 1000)
            )