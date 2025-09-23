"""
Advanced reporting and analytics models for TeamFlow.
Provides comprehensive business intelligence and data visualization capabilities.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey,
    Float, Date, Enum as SQLEnum, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ReportType(str, Enum):
    """Types of reports available in the system."""
    PROJECT_OVERVIEW = "project_overview"
    TASK_ANALYTICS = "task_analytics"
    TIME_TRACKING = "time_tracking"
    USER_PRODUCTIVITY = "user_productivity"
    TEAM_PERFORMANCE = "team_performance"
    RESOURCE_UTILIZATION = "resource_utilization"
    BUDGET_ANALYSIS = "budget_analysis"
    MILESTONE_TRACKING = "milestone_tracking"
    CUSTOM_DASHBOARD = "custom_dashboard"
    WORKFLOW_ANALYSIS = "workflow_analysis"


class ReportFormat(str, Enum):
    """Export formats for reports."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    PNG = "png"
    SVG = "svg"


class ReportFrequency(str, Enum):
    """Frequency options for automated reports."""
    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ChartType(str, Enum):
    """Types of charts available for visualization."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    RADAR = "radar"
    POLAR = "polar"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    GANTT = "gantt"
    BURNDOWN = "burndown"
    VELOCITY = "velocity"


class MetricType(str, Enum):
    """Types of metrics that can be tracked."""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    TREND = "trend"
    CUSTOM = "custom"


class ReportTemplate(Base):
    """
    Predefined and custom report templates.
    Defines the structure and configuration for generating reports.
    """
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True)
    
    # Template configuration
    configuration = Column(JSON, nullable=False, default={})  # Report layout and settings
    default_filters = Column(JSON, default={})  # Default filter values
    chart_configurations = Column(JSON, default=[])  # Chart definitions
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Template properties
    is_system_template = Column(Boolean, default=False, index=True)  # Built-in templates
    is_public = Column(Boolean, default=False, index=True)  # Shared with organization
    is_active = Column(Boolean, default=True, index=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="report_templates")
    creator = relationship("User", foreign_keys=[created_by])
    reports = relationship("Report", back_populates="template", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_report_templates_org_type", "organization_id", "report_type"),
        Index("ix_report_templates_public_active", "is_public", "is_active"),
    )


class Report(Base):
    """
    Generated reports with data and metadata.
    Stores actual report instances with their data and generation info.
    """
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Report data
    data = Column(JSON, nullable=False, default={})  # Processed report data
    metadata = Column(JSON, default={})  # Generation metadata
    filters_applied = Column(JSON, default={})  # Filters used for this report
    
    # Generation info
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Data range
    data_start_date = Column(Date, index=True)
    data_end_date = Column(Date, index=True)
    
    # Report status and properties
    generation_duration_ms = Column(Integer)  # Time taken to generate
    data_points_count = Column(Integer)  # Number of data points included
    file_size_bytes = Column(Integer)  # Size of generated report data
    
    # Sharing and access
    is_public = Column(Boolean, default=False, index=True)
    shared_with_users = Column(JSON, default=[])  # List of user IDs
    access_permissions = Column(JSON, default={})  # Detailed access controls
    
    # Archival
    is_archived = Column(Boolean, default=False, index=True)
    archived_at = Column(DateTime)
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="reports")
    organization = relationship("Organization", back_populates="reports")
    generator = relationship("User", foreign_keys=[generated_by])
    exports = relationship("ReportExport", back_populates="report", cascade="all, delete-orphan")
    schedules = relationship("ReportSchedule", back_populates="report", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_reports_org_generated", "organization_id", "generated_at"),
        Index("ix_reports_template_date", "template_id", "generated_at"),
        Index("ix_reports_date_range", "data_start_date", "data_end_date"),
    )


class ReportExport(Base):
    """
    Report exports in various formats.
    Tracks exported versions of reports for download and sharing.
    """
    __tablename__ = "report_exports"
    
    id = Column(Integer, primary_key=True, index=True)
    export_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Export information
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    format = Column(SQLEnum(ReportFormat), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))  # Path to exported file
    file_size_bytes = Column(Integer)
    content_type = Column(String(100))
    
    # Export metadata
    export_settings = Column(JSON, default={})  # Format-specific settings
    generation_duration_ms = Column(Integer)
    
    # Access and tracking
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    exported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    exported_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime)
    
    # Expiration and cleanup
    expires_at = Column(DateTime, index=True)  # When to auto-delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    
    # Relationships
    report = relationship("Report", back_populates="exports")
    organization = relationship("Organization")
    exporter = relationship("User", foreign_keys=[exported_by])
    
    __table_args__ = (
        Index("ix_report_exports_org_format", "organization_id", "format"),
        Index("ix_report_exports_expires", "expires_at", "is_deleted"),
    )


class ReportSchedule(Base):
    """
    Automated report generation schedules.
    Configures automatic generation and delivery of reports.
    """
    __tablename__ = "report_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Schedule configuration
    report_id = Column(Integer, ForeignKey("reports.id"), index=True)  # Optional base report
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False, index=True)
    frequency = Column(SQLEnum(ReportFrequency), nullable=False, index=True)
    
    # Timing settings
    scheduled_time = Column(String(10))  # Time of day (HH:MM format)
    scheduled_day = Column(Integer)  # Day of week (0-6) or month (1-31)
    timezone = Column(String(50), default="UTC")
    
    # Filters and parameters
    default_filters = Column(JSON, default={})
    parameters = Column(JSON, default={})  # Additional report parameters
    
    # Delivery settings
    auto_export_formats = Column(JSON, default=[])  # Formats to auto-export
    email_recipients = Column(JSON, default=[])  # Email addresses for delivery
    notification_settings = Column(JSON, default={})
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Schedule status
    is_active = Column(Boolean, default=True, index=True)
    last_run_at = Column(DateTime, index=True)
    next_run_at = Column(DateTime, index=True)
    run_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_failure_reason = Column(Text)
    
    # Relationships
    report = relationship("Report", back_populates="schedules")
    template = relationship("ReportTemplate")
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index("ix_report_schedules_active_next_run", "is_active", "next_run_at"),
        Index("ix_report_schedules_org_active", "organization_id", "is_active"),
    )


class Dashboard(Base):
    """
    Custom dashboards with multiple widgets and visualizations.
    Provides flexible dashboard creation with various chart types.
    """
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Dashboard configuration
    layout_config = Column(JSON, nullable=False, default={})  # Grid layout configuration
    theme_settings = Column(JSON, default={})  # Color scheme and styling
    refresh_interval = Column(Integer, default=300)  # Auto-refresh interval in seconds
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Dashboard properties
    is_public = Column(Boolean, default=False, index=True)
    is_default = Column(Boolean, default=False, index=True)  # Default dashboard for user
    is_system_dashboard = Column(Boolean, default=False, index=True)  # Built-in dashboards
    
    # Access and sharing
    shared_with_users = Column(JSON, default=[])  # List of user IDs
    access_permissions = Column(JSON, default={})  # View/edit permissions
    
    # Usage tracking
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="dashboards")
    creator = relationship("User", foreign_keys=[created_by])
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_dashboards_org_public", "organization_id", "is_public"),
        Index("ix_dashboards_creator_default", "created_by", "is_default"),
    )


class DashboardWidget(Base):
    """
    Individual widgets within dashboards.
    Represents charts, metrics, and other visualizations on dashboards.
    """
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    widget_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    widget_type = Column(SQLEnum(ChartType), nullable=False, index=True)
    
    # Widget configuration
    query_config = Column(JSON, nullable=False, default={})  # Data query configuration
    chart_config = Column(JSON, default={})  # Chart-specific settings
    filter_config = Column(JSON, default={})  # Widget-specific filters
    
    # Layout and positioning
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False, index=True)
    position_x = Column(Integer, nullable=False, default=0)
    position_y = Column(Integer, nullable=False, default=0)
    width = Column(Integer, nullable=False, default=4)  # Grid width
    height = Column(Integer, nullable=False, default=3)  # Grid height
    
    # Widget properties
    refresh_interval = Column(Integer, default=300)  # Override dashboard refresh
    is_visible = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0)
    
    # Cache settings
    cache_duration_seconds = Column(Integer, default=300)
    last_data_update = Column(DateTime)
    cached_data = Column(JSON)  # Cached widget data
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")
    organization = relationship("Organization")
    
    __table_args__ = (
        Index("ix_dashboard_widgets_dashboard_order", "dashboard_id", "display_order"),
        Index("ix_dashboard_widgets_org_type", "organization_id", "widget_type"),
        CheckConstraint("position_x >= 0", name="check_position_x_positive"),
        CheckConstraint("position_y >= 0", name="check_position_y_positive"),
        CheckConstraint("width > 0", name="check_width_positive"),
        CheckConstraint("height > 0", name="check_height_positive"),
    )


class AnalyticsMetric(Base):
    """
    Calculated metrics and KPIs for analytics.
    Stores computed business metrics for reporting and dashboards.
    """
    __tablename__ = "analytics_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Metric identification
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(SQLEnum(MetricType), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # project, task, user, etc.
    
    # Metric value and metadata
    value = Column(Float, nullable=False)
    unit = Column(String(50))  # seconds, count, percentage, etc.
    calculation_method = Column(Text)  # How the metric was calculated
    
    # Dimensional attributes
    entity_type = Column(String(50), index=True)  # project, task, user, organization
    entity_id = Column(Integer, index=True)  # ID of the specific entity
    dimensions = Column(JSON, default={})  # Additional dimensional data
    
    # Time attributes
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    source_data = Column(JSON, default={})  # Source data used for calculation
    
    # Data quality
    confidence_score = Column(Float, default=1.0)  # 0-1 confidence in accuracy
    is_estimated = Column(Boolean, default=False, index=True)
    data_completeness = Column(Float, default=1.0)  # 0-1 completeness of source data
    
    # Relationships
    organization = relationship("Organization")
    
    __table_args__ = (
        Index("ix_analytics_metrics_org_name_period", "organization_id", "metric_name", "period_start", "period_end"),
        Index("ix_analytics_metrics_entity", "entity_type", "entity_id", "period_start"),
        Index("ix_analytics_metrics_category_period", "category", "period_start", "period_end"),
        UniqueConstraint("organization_id", "metric_name", "entity_type", "entity_id", "period_start", "period_end", 
                        name="uq_analytics_metric_period"),
    )


class ReportAlert(Base):
    """
    Alert configurations for report monitoring.
    Triggers notifications when metrics exceed thresholds.
    """
    __tablename__ = "report_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Alert configuration
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    metric_name = Column(String(255), nullable=False, index=True)
    
    # Threshold settings
    threshold_value = Column(Float, nullable=False)
    threshold_operator = Column(String(10), nullable=False)  # >, <, >=, <=, ==, !=
    threshold_type = Column(String(20), default="absolute")  # absolute, percentage, change
    
    # Alert conditions
    evaluation_window = Column(Integer, default=24)  # Hours to look back
    consecutive_periods = Column(Integer, default=1)  # Periods threshold must be exceeded
    severity_level = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Notification settings
    notification_channels = Column(JSON, default=[])  # email, slack, webhook, etc.
    notification_recipients = Column(JSON, default=[])  # User IDs or email addresses
    notification_template = Column(Text)  # Custom notification message
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Alert status
    is_active = Column(Boolean, default=True, index=True)
    last_evaluated_at = Column(DateTime, index=True)
    last_triggered_at = Column(DateTime, index=True)
    trigger_count = Column(Integer, default=0)
    
    # Snooze functionality
    is_snoozed = Column(Boolean, default=False, index=True)
    snoozed_until = Column(DateTime)
    snoozed_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    snoozer = relationship("User", foreign_keys=[snoozed_by])
    
    __table_args__ = (
        Index("ix_report_alerts_org_active", "organization_id", "is_active"),
        Index("ix_report_alerts_metric_active", "metric_name", "is_active"),
        Index("ix_report_alerts_next_eval", "is_active", "last_evaluated_at"),
    )