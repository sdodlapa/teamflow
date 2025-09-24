"""Advanced task analytics models for Day 3 implementation."""

import enum
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, 
    JSON as JSONField
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class TaskComplexityType(str, enum.Enum):
    """Task complexity categories."""
    
    TRIVIAL = "trivial"        # 1-2 points
    SIMPLE = "simple"          # 3-4 points  
    MODERATE = "moderate"      # 5-6 points
    COMPLEX = "complex"        # 7-8 points
    CRITICAL = "critical"      # 9-10 points


class WorkflowStatus(str, enum.Enum):
    """Workflow execution status."""
    
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BottleneckType(str, enum.Enum):
    """Types of process bottlenecks."""
    
    RESOURCE = "resource"      # Not enough people
    DEPENDENCY = "dependency"  # Waiting on other tasks
    APPROVAL = "approval"      # Waiting for approvals
    TECHNICAL = "technical"    # Technical blockers
    COMMUNICATION = "communication"  # Communication issues


class TaskProductivityMetrics(BaseModel):
    """Model for tracking individual task productivity metrics."""

    __tablename__ = "task_productivity_metrics"

    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    
    # Time metrics
    time_to_completion = Column(Float, nullable=True)  # Hours from creation to completion
    estimation_accuracy = Column(Float, nullable=True)  # Estimated vs actual ratio (1.0 = perfect)
    
    # Quality metrics
    revision_count = Column(Integer, default=0)  # Number of times reopened/changed
    quality_score = Column(Float, nullable=True)  # 0.0-1.0 based on reviews/feedback
    revision_efficiency = Column(Float, nullable=True)  # Quality vs revisions ratio
    
    # Complexity metrics
    complexity_accuracy = Column(Float, nullable=True)  # Predicted vs actual complexity
    actual_complexity_score = Column(Integer, nullable=True)  # 1-10 retrospective score
    
    # Performance indicators
    blocked_time_hours = Column(Float, default=0.0)  # Time spent blocked
    review_cycles = Column(Integer, default=0)  # Number of review iterations
    stakeholder_satisfaction = Column(Float, nullable=True)  # 1.0-5.0 rating
    
    # Metadata
    calculation_date = Column(DateTime, default=datetime.utcnow)
    metrics_version = Column(String(20), default="1.0")  # For schema evolution
    
    # Relationships
    task = relationship("Task", backref="productivity_metrics")

    def __repr__(self) -> str:
        return f"<TaskProductivityMetrics(task_id={self.task_id}, quality_score={self.quality_score})>"


class TeamPerformanceMetrics(BaseModel):
    """Model for tracking team-level performance metrics."""

    __tablename__ = "team_performance_metrics"
    
    # Team identification
    team_identifier = Column(String(100), nullable=False, index=True)  # project_id, org_id, or custom
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    tasks_completed_on_time = Column(Integer, default=0)
    avg_task_completion_time = Column(Float, nullable=True)  # Average hours
    avg_complexity_score = Column(Float, nullable=True)
    
    # Quality metrics
    avg_quality_score = Column(Float, nullable=True)
    avg_revision_count = Column(Float, nullable=True)
    customer_satisfaction = Column(Float, nullable=True)
    
    # Productivity indicators
    velocity_points = Column(Float, nullable=True)  # Story points completed
    productivity_trend = Column(Float, nullable=True)  # Compared to previous period
    efficiency_score = Column(Float, nullable=True)  # Overall efficiency rating
    
    # Process metrics
    bottleneck_areas = Column(JSONField, nullable=True)  # List of bottleneck types
    communication_score = Column(Float, nullable=True)  # Based on comment/activity patterns
    collaboration_index = Column(Float, nullable=True)  # Cross-team interaction score
    
    # Predictive metrics
    burnout_risk_score = Column(Float, nullable=True)  # 0.0-1.0 burnout prediction
    capacity_utilization = Column(Float, nullable=True)  # Team capacity usage %
    
    def __repr__(self) -> str:
        return f"<TeamPerformanceMetrics(team={self.team_identifier}, period={self.period_start.date()})>"


class WorkflowExecutionAnalytics(BaseModel):
    """Model for tracking workflow execution state (analytics-focused)."""

    __tablename__ = "workflow_execution_analytics"
    
    # Workflow identification
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    execution_name = Column(String(200), nullable=True)  # Human-readable name
    
    # Entity association
    entity_type = Column(String(50), nullable=False)  # "task", "project", "user"
    entity_id = Column(Integer, nullable=False, index=True)
    
    # Execution state
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, nullable=False)
    
    # Execution data
    execution_data = Column(JSONField, nullable=True)  # Dynamic data for steps
    error_details = Column(JSONField, nullable=True)  # Error information if failed
    completion_percentage = Column(Float, default=0.0)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    
    # Performance tracking
    estimated_duration = Column(Integer, nullable=True)  # Estimated minutes
    actual_duration = Column(Integer, nullable=True)  # Actual minutes
    
    # Relationships
    workflow_template = relationship("WorkflowTemplate", back_populates="analytics_executions")
    step_logs = relationship("WorkflowStepLogAnalytics", back_populates="execution", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<WorkflowExecutionAnalytics(id={self.id}, template_id={self.workflow_template_id}, status={self.status})>"


class WorkflowStepLogAnalytics(BaseModel):
    """Model for logging individual workflow step execution (analytics-focused)."""

    __tablename__ = "workflow_step_log_analytics"
    
    # References
    workflow_execution_id = Column(Integer, ForeignKey("workflow_execution_analytics.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(200), nullable=False)
    
    # Execution details
    status = Column(String(50), nullable=False)  # "pending", "running", "completed", "failed", "skipped"
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Step data
    input_data = Column(JSONField, nullable=True)  # Data provided to step
    output_data = Column(JSONField, nullable=True)  # Data produced by step
    error_message = Column(Text, nullable=True)
    
    # Performance
    duration_seconds = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    execution = relationship("WorkflowExecutionAnalytics", back_populates="step_logs")

    def __repr__(self) -> str:
        return f"<WorkflowStepLogAnalytics(execution_id={self.workflow_execution_id}, step={self.step_number}, status={self.status})>"


class BottleneckAnalysis(BaseModel):
    """Model for identifying and tracking process bottlenecks."""

    __tablename__ = "bottleneck_analyses"
    
    # Analysis scope
    analysis_type = Column(String(50), nullable=False)  # "project", "team", "organization"
    scope_identifier = Column(String(100), nullable=False, index=True)
    analysis_period_start = Column(DateTime, nullable=False)
    analysis_period_end = Column(DateTime, nullable=False)
    
    # Bottleneck identification
    bottleneck_type = Column(SQLEnum(BottleneckType), nullable=False)
    bottleneck_location = Column(String(200), nullable=False)  # Where the bottleneck occurs
    severity_score = Column(Float, nullable=False)  # 0.0-1.0 severity rating
    
    # Impact metrics
    affected_tasks_count = Column(Integer, default=0)
    avg_delay_hours = Column(Float, nullable=True)  # Average delay caused
    productivity_impact = Column(Float, nullable=True)  # % reduction in productivity
    
    # Analysis details
    root_cause = Column(Text, nullable=True)  # Detailed root cause analysis
    suggested_solutions = Column(JSONField, nullable=True)  # List of suggested fixes
    
    # Status tracking
    resolution_status = Column(String(50), default="identified")  # "identified", "in_progress", "resolved"
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Validation
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0 confidence in analysis
    validation_status = Column(String(50), default="pending")  # "pending", "confirmed", "disputed"

    def __repr__(self) -> str:
        return f"<BottleneckAnalysis(type={self.bottleneck_type}, severity={self.severity_score})>"


class ProjectHealthMetrics(BaseModel):
    """Model for overall project health assessment."""

    __tablename__ = "project_health_metrics"
    
    # Project reference
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    assessment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Health indicators
    overall_health_score = Column(Float, nullable=False)  # 0.0-100.0 composite score
    velocity_score = Column(Float, nullable=True)  # Task completion velocity
    quality_score = Column(Float, nullable=True)  # Overall output quality
    team_satisfaction = Column(Float, nullable=True)  # Team happiness score
    
    # Risk indicators
    deadline_risk = Column(Float, nullable=True)  # Risk of missing deadlines
    budget_risk = Column(Float, nullable=True)  # Risk of budget overrun
    resource_risk = Column(Float, nullable=True)  # Risk of resource constraints
    technical_risk = Column(Float, nullable=True)  # Technical/complexity risks
    
    # Trend analysis
    health_trend = Column(Float, nullable=True)  # Improving/declining trend
    predicted_completion_date = Column(DateTime, nullable=True)
    predicted_budget_usage = Column(Float, nullable=True)  # % of budget
    
    # Recommendations
    critical_issues = Column(JSONField, nullable=True)  # List of critical issues
    recommendations = Column(JSONField, nullable=True)  # Improvement recommendations
    action_items = Column(JSONField, nullable=True)  # Specific action items
    
    # Relationships
    project = relationship("Project", backref="health_metrics")

    def __repr__(self) -> str:
        return f"<ProjectHealthMetrics(project_id={self.project_id}, health_score={self.overall_health_score})>"


class TaskComplexityEstimation(BaseModel):
    """Model for AI-powered task complexity estimation."""

    __tablename__ = "task_complexity_estimations"
    
    # Task reference
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    
    # Estimation details
    complexity_score = Column(Integer, nullable=False)  # 1-10 scale
    complexity_type = Column(SQLEnum(TaskComplexityType), nullable=False)
    confidence_level = Column(Float, nullable=False)  # 0.0-1.0
    
    # Estimation factors
    description_complexity = Column(Float, nullable=True)  # Based on description analysis
    skill_requirements_score = Column(Float, nullable=True)  # Required skills complexity
    dependency_complexity = Column(Float, nullable=True)  # Dependency chain complexity
    historical_similarity = Column(Float, nullable=True)  # Similarity to past tasks
    
    # AI model information
    model_version = Column(String(50), nullable=False)  # AI model version used
    feature_weights = Column(JSONField, nullable=True)  # Feature importance weights
    
    # Validation
    human_validation = Column(Integer, nullable=True)  # Human expert validation (1-10)
    actual_complexity = Column(Integer, nullable=True)  # Retrospective actual complexity
    accuracy_score = Column(Float, nullable=True)  # Prediction accuracy
    
    # Relationships
    task = relationship("Task", back_populates="complexity_estimations")

    def __repr__(self) -> str:
        return f"<TaskComplexityEstimation(task_id={self.task_id}, score={self.complexity_score})>"


class SmartAssignmentLog(BaseModel):
    """Model for logging smart task assignment decisions."""

    __tablename__ = "smart_assignment_logs"
    
    # Assignment details
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assignment_method = Column(String(50), nullable=False)  # "manual", "auto", "smart"
    
    # Algorithm details (for smart assignments)
    algorithm_version = Column(String(20), nullable=True)
    candidate_users = Column(JSONField, nullable=True)  # List of considered users
    scoring_details = Column(JSONField, nullable=True)  # Detailed scoring breakdown
    
    # Assignment factors
    skill_match_score = Column(Float, nullable=True)  # 0.0-1.0
    workload_score = Column(Float, nullable=True)  # 0.0-1.0
    availability_score = Column(Float, nullable=True)  # 0.0-1.0
    performance_score = Column(Float, nullable=True)  # 0.0-1.0
    final_score = Column(Float, nullable=True)  # Combined score
    
    # Performance tracking
    assignment_success = Column(Boolean, nullable=True)  # Task completed successfully
    completion_time = Column(Float, nullable=True)  # Time to completion
    quality_rating = Column(Float, nullable=True)  # Quality of output
    
    # Relationships
    task = relationship("Task", back_populates="assignment_logs")
    assigned_user = relationship("User", backref="smart_assignments")

    def __repr__(self) -> str:
        return f"<SmartAssignmentLog(task_id={self.task_id}, user_id={self.assigned_user_id}, score={self.final_score})>"