"""Task model for task management."""

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class TaskStatus(str, enum.Enum):
    """Task status options."""
    
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Task model for task management."""

    __tablename__ = "tasks"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Task properties
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    # Time tracking
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    
    # Dates
    due_date = Column(DateTime, nullable=True)
    
    # Task organization
    tags = Column(String(1000), nullable=True)  # JSON string of tags
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    dependencies = relationship(
        "TaskDependency", 
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    dependent_tasks = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.depends_on_id", 
        back_populates="depends_on_task",
        cascade="all, delete-orphan"
    )
    
    # Advanced feature relationships
    time_logs = relationship("TaskTimeLog", back_populates="task", cascade="all, delete-orphan")
    activities = relationship("TaskActivity", back_populates="task", cascade="all, delete-orphan")
    mentions = relationship("TaskMention", back_populates="task", cascade="all, delete-orphan")
    assignment_history = relationship("TaskAssignmentHistory", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"

    @property
    def tags_list(self) -> List[str]:
        """Parse tags string into list."""
        if not self.tags:
            return []
        try:
            import json
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return []

    @tags_list.setter
    def tags_list(self, value: List[str]) -> None:
        """Set tags from list."""
        import json
        self.tags = json.dumps(value) if value else None


class TaskComment(Base):
    """Task comment model for task discussions."""

    __tablename__ = "task_comments"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")
    mentions = relationship("TaskMention", back_populates="comment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TaskComment(id={self.id}, task_id={self.task_id}, user_id={self.user_id})>"


class TaskDependency(Base):
    """Task dependency model for task relationships."""

    __tablename__ = "task_dependencies"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    depends_on_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_id], back_populates="dependent_tasks")

    def __repr__(self) -> str:
        return f"<TaskDependency(task_id={self.task_id}, depends_on_id={self.depends_on_id})>"