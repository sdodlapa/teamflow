"""
Advanced reporting and analytics schemas for TeamFlow API.
Defines request/response models for business intelligence and data visualization.
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.analytics import (
    ReportType, ReportFormat, ReportFrequency, ChartType, MetricType
)


class DateRangeRequest(BaseModel):
    """Date range specification for reports."""
    
    start_date: date = Field(..., description="Start date for data range")
    end_date: date = Field(..., description="End date for data range")
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class ReportFilter(BaseModel):
    """Filter configuration for reports."""
    
    field: str = Field(..., description="Field to filter on")
    operator: str = Field(..., description="Filter operator (eq, ne, gt, lt, in, etc.)")
    value: Union[str, int, float, List[Any]] = Field(..., description="Filter value(s)")
    label: Optional[str] = Field(None, description="Human-readable filter label")


class ChartConfiguration(BaseModel):
    """Chart configuration for visualizations."""
    
    chart_type: ChartType = Field(..., description="Type of chart")
    title: str = Field(..., description="Chart title")
    x_axis: Dict[str, Any] = Field(default_factory=dict, description="X-axis configuration")
    y_axis: Dict[str, Any] = Field(default_factory=dict, description="Y-axis configuration")
    colors: Optional[List[str]] = Field(None, description="Custom color palette")
    options: Dict[str, Any] = Field(default_factory=dict, description="Additional chart options")
    
    class Config:
        use_enum_values = True


class ReportTemplateRequest(BaseModel):
    """Request model for creating/updating report templates."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    report_type: ReportType = Field(..., description="Type of report")
    
    # Configuration
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Report configuration")
    default_filters: Dict[str, Any] = Field(default_factory=dict, description="Default filter values")
    chart_configurations: List[ChartConfiguration] = Field(default_factory=list, description="Chart definitions")
    
    # Properties
    is_public: bool = Field(False, description="Make template publicly available")
    
    class Config:
        use_enum_values = True


class ReportTemplateResponse(BaseModel):
    """Response model for report templates."""
    
    id: int
    template_uuid: str
    name: str
    description: Optional[str]
    report_type: str
    
    # Configuration
    configuration: Dict[str, Any]
    default_filters: Dict[str, Any]
    chart_configurations: List[Dict[str, Any]]
    
    # Properties
    is_system_template: bool
    is_public: bool
    is_active: bool
    
    # Usage
    usage_count: int
    last_used_at: Optional[datetime]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReportGenerationRequest(BaseModel):
    """Request model for generating reports."""
    
    template_id: int = Field(..., description="Template to use for generation")
    name: Optional[str] = Field(None, max_length=255, description="Custom report name")
    description: Optional[str] = Field(None, max_length=1000, description="Report description")
    
    # Data range
    date_range: DateRangeRequest = Field(..., description="Date range for report data")
    
    # Filters
    filters: List[ReportFilter] = Field(default_factory=list, description="Additional filters")
    
    # Options
    include_raw_data: bool = Field(False, description="Include raw data in report")
    cache_duration_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Cache duration")
    
    class Config:
        use_enum_values = True


class ReportResponse(BaseModel):
    """Response model for generated reports."""
    
    id: int
    report_uuid: str
    name: str
    description: Optional[str]
    
    # Report data
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    filters_applied: Dict[str, Any]
    
    # Generation info
    template_id: int
    generated_at: datetime
    generation_duration_ms: Optional[int]
    data_points_count: Optional[int]
    
    # Data range
    data_start_date: Optional[date]
    data_end_date: Optional[date]
    
    # Properties
    is_public: bool
    is_archived: bool
    
    class Config:
        from_attributes = True


class ReportExportRequest(BaseModel):
    """Request model for exporting reports."""
    
    format: ReportFormat = Field(..., description="Export format")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Format-specific settings")
    expires_in_hours: Optional[int] = Field(24, ge=1, le=168, description="Hours until export expires")
    
    class Config:
        use_enum_values = True


class ReportExportResponse(BaseModel):
    """Response model for report exports."""
    
    id: int
    export_uuid: str
    format: str
    filename: str
    file_size_bytes: Optional[int]
    
    # Status
    exported_at: datetime
    expires_at: Optional[datetime]
    download_count: int
    
    # Download info
    download_url: Optional[str] = Field(None, description="Temporary download URL")
    
    class Config:
        from_attributes = True


class DashboardRequest(BaseModel):
    """Request model for creating/updating dashboards."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Dashboard name")
    description: Optional[str] = Field(None, max_length=1000, description="Dashboard description")
    
    # Configuration
    layout_config: Dict[str, Any] = Field(default_factory=dict, description="Grid layout")
    theme_settings: Dict[str, Any] = Field(default_factory=dict, description="Theme and styling")
    refresh_interval: int = Field(300, ge=30, le=3600, description="Auto-refresh interval in seconds")
    
    # Sharing
    is_public: bool = Field(False, description="Make dashboard publicly visible")
    is_default: bool = Field(False, description="Set as default dashboard")
    shared_with_users: List[int] = Field(default_factory=list, description="User IDs to share with")
    
    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    """Response model for dashboards."""
    
    id: int
    dashboard_uuid: str
    name: str
    description: Optional[str]
    
    # Configuration
    layout_config: Dict[str, Any]
    theme_settings: Dict[str, Any]
    refresh_interval: int
    
    # Properties
    is_public: bool
    is_default: bool
    is_system_dashboard: bool
    
    # Access
    shared_with_users: List[int]
    access_permissions: Dict[str, Any]
    
    # Usage
    view_count: int
    last_viewed_at: Optional[datetime]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Widget count
    widget_count: Optional[int] = Field(None, description="Number of widgets on dashboard")
    
    class Config:
        from_attributes = True


class DashboardWidgetRequest(BaseModel):
    """Request model for creating/updating dashboard widgets."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Widget title")
    description: Optional[str] = Field(None, max_length=1000, description="Widget description")
    widget_type: ChartType = Field(..., description="Type of visualization")
    
    # Configuration
    query_config: Dict[str, Any] = Field(..., description="Data query configuration")
    chart_config: Dict[str, Any] = Field(default_factory=dict, description="Chart settings")
    filter_config: Dict[str, Any] = Field(default_factory=dict, description="Widget filters")
    
    # Layout
    position_x: int = Field(0, ge=0, description="X position in grid")
    position_y: int = Field(0, ge=0, description="Y position in grid")
    width: int = Field(4, ge=1, le=12, description="Width in grid units")
    height: int = Field(3, ge=1, le=12, description="Height in grid units")
    
    # Properties
    refresh_interval: Optional[int] = Field(None, ge=30, le=3600, description="Custom refresh interval")
    is_visible: bool = Field(True, description="Widget visibility")
    display_order: int = Field(0, description="Display order on dashboard")
    
    class Config:
        use_enum_values = True


class DashboardWidgetResponse(BaseModel):
    """Response model for dashboard widgets."""
    
    id: int
    widget_uuid: str
    title: str
    description: Optional[str]
    widget_type: str
    
    # Configuration
    query_config: Dict[str, Any]
    chart_config: Dict[str, Any]
    filter_config: Dict[str, Any]
    
    # Layout
    dashboard_id: int
    position_x: int
    position_y: int
    width: int
    height: int
    
    # Properties
    refresh_interval: Optional[int]
    is_visible: bool
    display_order: int
    
    # Cache
    cache_duration_seconds: Optional[int]
    last_data_update: Optional[datetime]
    cached_data: Optional[Dict[str, Any]]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DashboardWidgetDataResponse(BaseModel):
    """Response model for widget data."""
    
    widget_id: int
    data: Dict[str, Any] = Field(..., description="Chart data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Data metadata")
    last_updated: datetime
    cache_expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AnalyticsMetricRequest(BaseModel):
    """Request model for creating analytics metrics."""
    
    metric_name: str = Field(..., max_length=255, description="Metric name")
    metric_type: MetricType = Field(..., description="Type of metric")
    category: str = Field(..., max_length=100, description="Metric category")
    
    # Value and metadata
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    calculation_method: Optional[str] = Field(None, description="How metric was calculated")
    
    # Dimensions
    entity_type: Optional[str] = Field(None, max_length=50, description="Entity type")
    entity_id: Optional[int] = Field(None, description="Entity ID")
    dimensions: Dict[str, Any] = Field(default_factory=dict, description="Additional dimensions")
    
    # Time period
    period_start: date = Field(..., description="Metric period start")
    period_end: date = Field(..., description="Metric period end")
    
    # Data quality
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in accuracy")
    is_estimated: bool = Field(False, description="Whether value is estimated")
    data_completeness: float = Field(1.0, ge=0.0, le=1.0, description="Data completeness")
    
    class Config:
        use_enum_values = True


class AnalyticsMetricResponse(BaseModel):
    """Response model for analytics metrics."""
    
    id: int
    metric_uuid: str
    metric_name: str
    metric_type: str
    category: str
    
    # Value and metadata
    value: float
    unit: Optional[str]
    calculation_method: Optional[str]
    
    # Dimensions
    entity_type: Optional[str]
    entity_id: Optional[int]
    dimensions: Dict[str, Any]
    
    # Time period
    period_start: date
    period_end: date
    calculated_at: datetime
    
    # Data quality
    confidence_score: float
    is_estimated: bool
    data_completeness: float
    
    class Config:
        from_attributes = True


class MetricsQueryRequest(BaseModel):
    """Request model for querying metrics."""
    
    metric_names: Optional[List[str]] = Field(None, description="Specific metrics to retrieve")
    categories: Optional[List[str]] = Field(None, description="Metric categories to include")
    entity_types: Optional[List[str]] = Field(None, description="Entity types to filter by")
    entity_ids: Optional[List[int]] = Field(None, description="Specific entity IDs")
    
    # Time range
    date_range: DateRangeRequest = Field(..., description="Date range for metrics")
    
    # Aggregation
    group_by: Optional[List[str]] = Field(None, description="Fields to group results by")
    aggregate_function: Optional[str] = Field(None, description="Aggregation function (sum, avg, max, min)")
    
    # Options
    include_estimated: bool = Field(True, description="Include estimated values")
    min_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Minimum confidence score")
    
    class Config:
        from_attributes = True


class MetricsQueryResponse(BaseModel):
    """Response model for metrics queries."""
    
    metrics: List[AnalyticsMetricResponse]
    total_count: int
    aggregations: Optional[Dict[str, Any]] = Field(None, description="Aggregated results")
    
    # Query metadata
    query_duration_ms: int
    cache_hit: bool = False
    
    class Config:
        from_attributes = True


class ReportScheduleRequest(BaseModel):
    """Request model for creating report schedules."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Schedule name")
    description: Optional[str] = Field(None, max_length=1000, description="Schedule description")
    
    # Schedule configuration
    template_id: int = Field(..., description="Report template to use")
    frequency: ReportFrequency = Field(..., description="Generation frequency")
    
    # Timing
    scheduled_time: str = Field("09:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Time of day (HH:MM)")
    scheduled_day: Optional[int] = Field(None, ge=0, le=31, description="Day of week (0-6) or month (1-31)")
    timezone: str = Field("UTC", description="Timezone for scheduling")
    
    # Parameters
    default_filters: Dict[str, Any] = Field(default_factory=dict, description="Default filters")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")
    
    # Delivery
    auto_export_formats: List[ReportFormat] = Field(default_factory=list, description="Auto-export formats")
    email_recipients: List[str] = Field(default_factory=list, description="Email recipients")
    notification_settings: Dict[str, Any] = Field(default_factory=dict, description="Notification settings")
    
    class Config:
        use_enum_values = True


class ReportScheduleResponse(BaseModel):
    """Response model for report schedules."""
    
    id: int
    schedule_uuid: str
    name: str
    description: Optional[str]
    
    # Schedule configuration
    template_id: int
    frequency: str
    
    # Timing
    scheduled_time: str
    scheduled_day: Optional[int]
    timezone: str
    
    # Parameters
    default_filters: Dict[str, Any]
    parameters: Dict[str, Any]
    
    # Delivery
    auto_export_formats: List[str]
    email_recipients: List[str]
    notification_settings: Dict[str, Any]
    
    # Status
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    run_count: int
    failure_count: int
    last_failure_reason: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReportAlertRequest(BaseModel):
    """Request model for creating report alerts."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Alert name")
    description: Optional[str] = Field(None, max_length=1000, description="Alert description")
    metric_name: str = Field(..., max_length=255, description="Metric to monitor")
    
    # Threshold
    threshold_value: float = Field(..., description="Threshold value")
    threshold_operator: str = Field(..., pattern=r"^(>|<|>=|<=|==|!=)$", description="Threshold operator")
    threshold_type: str = Field("absolute", pattern=r"^(absolute|percentage|change)$", description="Threshold type")
    
    # Conditions
    evaluation_window: int = Field(24, ge=1, le=168, description="Evaluation window in hours")
    consecutive_periods: int = Field(1, ge=1, le=10, description="Consecutive periods for trigger")
    severity_level: str = Field("medium", pattern=r"^(low|medium|high|critical)$", description="Alert severity")
    
    # Notifications
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    notification_recipients: List[str] = Field(default_factory=list, description="Recipients")
    notification_template: Optional[str] = Field(None, description="Custom notification message")
    
    class Config:
        from_attributes = True


class ReportAlertResponse(BaseModel):
    """Response model for report alerts."""
    
    id: int
    alert_uuid: str
    name: str
    description: Optional[str]
    metric_name: str
    
    # Threshold
    threshold_value: float
    threshold_operator: str
    threshold_type: str
    
    # Conditions
    evaluation_window: int
    consecutive_periods: int
    severity_level: str
    
    # Notifications
    notification_channels: List[str]
    notification_recipients: List[str]
    notification_template: Optional[str]
    
    # Status
    is_active: bool
    last_evaluated_at: Optional[datetime]
    last_triggered_at: Optional[datetime]
    trigger_count: int
    
    # Snooze
    is_snoozed: bool
    snoozed_until: Optional[datetime]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsSummaryResponse(BaseModel):
    """Response model for analytics summary."""
    
    # Overview
    total_reports_generated: int
    total_dashboards: int
    total_active_alerts: int
    total_scheduled_reports: int
    
    # Recent activity
    recent_reports: List[Dict[str, Any]]
    recent_alerts: List[Dict[str, Any]]
    
    # Popular content
    popular_templates: List[Dict[str, Any]]
    popular_dashboards: List[Dict[str, Any]]
    
    # System health
    avg_report_generation_time: float
    cache_hit_rate: float
    alert_response_rate: float
    
    class Config:
        from_attributes = True