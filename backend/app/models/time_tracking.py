"""
Time tracking models for detailed task time management.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime
from typing import Optional


class TaskTimeLog(Base):
    """
    Detailed time tracking entries for tasks.
    Supports start/stop time tracking, billable hours, and productivity analytics.
    """
    __tablename__ = "task_time_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Time tracking
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)  # Null means timer is still running
    duration_minutes = Column(Integer, nullable=True)  # Auto-calculated when end_time is set
    
    # Description and categorization
    description = Column(Text, nullable=True)
    is_billable = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="time_logs")
    user = relationship("User", back_populates="time_logs")

    def calculate_duration(self) -> Optional[int]:
        """Calculate duration in minutes if both start and end times are set."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None

    def stop_timer(self, end_time: Optional[datetime.datetime] = None) -> int:
        """
        Stop the timer and calculate duration.
        Returns duration in minutes.
        """
        if not end_time:
            end_time = datetime.datetime.utcnow()
        
        self.end_time = end_time
        self.duration_minutes = self.calculate_duration()
        return self.duration_minutes or 0

    @property
    def is_running(self) -> bool:
        """Check if timer is currently running."""
        return self.end_time is None and self.is_active

    def __repr__(self):
        status = "running" if self.is_running else f"{self.duration_minutes}min"
        return f"<TaskTimeLog(task_id={self.task_id}, user_id={self.user_id}, {status})>"


class TaskTemplate(Base):
    """
    Reusable task templates for common work patterns.
    Enables rapid task creation and process standardization.
    """
    __tablename__ = "task_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)  # e.g., "development", "design", "meeting"
    
    # Template defaults
    estimated_hours = Column(Integer, nullable=True)
    priority = Column(String(20), nullable=True)  # Will use TaskPriority enum values
    tags = Column(Text, nullable=True)  # JSON list of default tags
    
    # Template metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)  # Track how often template is used
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="task_templates")
    creator = relationship("User", back_populates="created_task_templates")

    def increment_usage(self):
        """Increment usage counter when template is used."""
        self.usage_count += 1

    def __repr__(self):
        return f"<TaskTemplate(name='{self.name}', category='{self.category}', usage={self.usage_count})>"


class TaskActivity(Base):
    """
    Comprehensive activity log for tasks.
    Tracks all changes, mentions, and interactions for audit and notification purposes.
    """
    __tablename__ = "task_activities"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # created, updated, assigned, commented, etc.
    description = Column(Text, nullable=False)  # Human-readable activity description
    activity_data = Column(Text, nullable=True)  # JSON data for detailed change tracking
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    # Relationships
    task = relationship("Task", back_populates="activities")
    user = relationship("User", back_populates="task_activities")

    def __repr__(self):
        return f"<TaskActivity(task_id={self.task_id}, type='{self.activity_type}', user_id={self.user_id})>"


class TaskMention(Base):
    """
    @Mention system for task comments and descriptions.
    Enables targeted notifications and team communication.
    """
    __tablename__ = "task_mentions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    comment_id = Column(Integer, ForeignKey("task_comments.id"), nullable=True, index=True)  # Null for task description mentions
    mentioned_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentioning_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Mention context
    context = Column(Text, nullable=True)  # Snippet of text around the mention
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    # Relationships
    task = relationship("Task", back_populates="mentions")
    comment = relationship("TaskComment", back_populates="mentions")
    mentioned_user = relationship("User", foreign_keys=[mentioned_user_id], back_populates="received_mentions")
    mentioning_user = relationship("User", foreign_keys=[mentioning_user_id], back_populates="created_mentions")

    def mark_as_read(self):
        """Mark mention as read by the user."""
        self.is_read = True

    def __repr__(self):
        return f"<TaskMention(task_id={self.task_id}, mentioned_user_id={self.mentioned_user_id}, read={self.is_read})>"


class TaskAssignmentHistory(Base):
    """
    Track task assignment changes for workload analysis and audit purposes.
    """
    __tablename__ = "task_assignment_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    previous_assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    new_assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Assignment context
    reason = Column(Text, nullable=True)  # Optional reason for assignment change
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    # Relationships
    task = relationship("Task", back_populates="assignment_history")
    previous_assignee = relationship("User", foreign_keys=[previous_assignee_id], back_populates="previous_assignments")
    new_assignee = relationship("User", foreign_keys=[new_assignee_id], back_populates="new_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by], back_populates="assignments_made")

    def __repr__(self):
        return f"<TaskAssignmentHistory(task_id={self.task_id}, {self.previous_assignee_id}→{self.new_assignee_id})>"