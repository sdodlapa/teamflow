import React, { useState, useEffect, useRef } from 'react';
import {
  FileText, Download, Clock,
  BarChart3, PieChart, LineChart, TrendingUp,
  Users, Target, Settings,
  Play, RefreshCw, Share2,
  Plus, ChevronDown, Search
} from 'lucide-react';
import './RealtimeReporting.css';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: 'performance' | 'users' | 'projects' | 'custom';
  chartTypes: ('bar' | 'line' | 'pie' | 'donut')[];
  metrics: string[];
  filters: ReportFilter[];
  schedule?: 'daily' | 'weekly' | 'monthly';
  lastGenerated?: string;
  createdBy: string;
}

interface ReportFilter {
  field: string;
  operator: 'equals' | 'contains' | 'greater' | 'less' | 'between';
  value: string | number | [number, number];
  label: string;
}

interface ReportData {
  id: string;
  name: string;
  type: string;
  data: any[];
  metadata: {
    totalRecords: number;
    generatedAt: string;
    executionTime: number;
    filters: ReportFilter[];
  };
}

interface RealtimeReportingProps {
  organizationId?: string;
  projectId?: string;
}

export const RealtimeReporting: React.FC<RealtimeReportingProps> = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<ReportFilter[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showTemplateBuilder] = useState(false);
  const [exportFormat] = useState<'pdf' | 'xlsx' | 'csv'>('pdf');
  const intervalRef = useRef<number | null>(null);

  // Mock report templates
  const mockTemplates: ReportTemplate[] = [
    {
      id: 'user-activity',
      name: 'User Activity Report',
      description: 'Comprehensive analysis of user engagement and activity patterns',
      type: 'users',
      chartTypes: ['line', 'bar'],
      metrics: ['active_users', 'session_duration', 'page_views', 'engagement_rate'],
      filters: [
        { field: 'date_range', operator: 'between', value: [7, 30], label: 'Date Range' },
        { field: 'user_role', operator: 'equals', value: 'all', label: 'User Role' }
      ],
      schedule: 'daily',
      lastGenerated: '2025-09-25T10:00:00Z',
      createdBy: 'System'
    },
    {
      id: 'project-performance',
      name: 'Project Performance Dashboard',
      description: 'Track project completion rates, timelines, and resource utilization',
      type: 'projects',
      chartTypes: ['bar', 'pie'],
      metrics: ['completion_rate', 'on_time_delivery', 'resource_utilization', 'budget_variance'],
      filters: [
        { field: 'project_status', operator: 'equals', value: 'active', label: 'Status' },
        { field: 'team_size', operator: 'greater', value: 3, label: 'Team Size' }
      ],
      schedule: 'weekly',
      lastGenerated: '2025-09-24T14:30:00Z',
      createdBy: 'Project Manager'
    },
    {
      id: 'system-health',
      name: 'System Health Monitoring',
      description: 'Real-time system performance metrics and health indicators',
      type: 'performance',
      chartTypes: ['line', 'donut'],
      metrics: ['response_time', 'error_rate', 'cpu_usage', 'memory_usage', 'uptime'],
      filters: [
        { field: 'time_window', operator: 'equals', value: '24h', label: 'Time Window' },
        { field: 'severity', operator: 'greater', value: 'warning', label: 'Alert Severity' }
      ],
      schedule: 'daily',
      lastGenerated: '2025-09-25T12:15:00Z',
      createdBy: 'DevOps Team'
    },
    {
      id: 'revenue-analytics',
      name: 'Revenue & Growth Analytics',
      description: 'Financial performance tracking with revenue forecasting',
      type: 'performance',
      chartTypes: ['line', 'bar'],
      metrics: ['revenue', 'growth_rate', 'mrr', 'churn_rate', 'ltv'],
      filters: [
        { field: 'subscription_type', operator: 'equals', value: 'all', label: 'Subscription Type' },
        { field: 'region', operator: 'contains', value: '', label: 'Region' }
      ],
      schedule: 'monthly',
      lastGenerated: '2025-09-20T09:00:00Z',
      createdBy: 'Finance Team'
    }
  ];

  useEffect(() => {
    if (realTimeMode && selectedTemplate) {
      intervalRef.current = setInterval(() => {
        generateReport(selectedTemplate, true);
      }, 30000); // Update every 30 seconds
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [realTimeMode, selectedTemplate]);

  const generateReport = async (template: ReportTemplate, isRealTime = false) => {
    if (!isRealTime) setLoading(true);

    // Simulate API call
    setTimeout(() => {
      const mockData: ReportData = {
        id: `report-${Date.now()}`,
        name: template.name,
        type: template.type,
        data: generateMockChartData(template),
        metadata: {
          totalRecords: Math.floor(Math.random() * 10000) + 1000,
          generatedAt: new Date().toISOString(),
          executionTime: Math.floor(Math.random() * 2000) + 500,
          filters: selectedFilters
        }
      };

      setReportData(mockData);
      if (!isRealTime) setLoading(false);
    }, isRealTime ? 100 : 1500);
  };

  const generateMockChartData = (template: ReportTemplate) => {
    const data = [];
    const dataPoints = 30;

    for (let i = 0; i < dataPoints; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (dataPoints - i));
      
      const point: any = {
        date: date.toISOString().split('T')[0],
        label: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      };

      template.metrics.forEach(metric => {
        point[metric] = Math.floor(Math.random() * 1000) + 100;
      });

      data.push(point);
    }

    return data;
  };

  const handleTemplateSelect = (template: ReportTemplate) => {
    setSelectedTemplate(template);
    setSelectedFilters(template.filters);
    generateReport(template);
  };

  const handleExport = (format: 'pdf' | 'xlsx' | 'csv') => {
    // Simulate export
    console.log(`Exporting report in ${format} format...`);
  };

  const handleSchedule = (template: ReportTemplate) => {
    console.log(`Scheduling report: ${template.name}`);
  };

  const filteredTemplates = mockTemplates.filter(template =>
    template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    template.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderTemplateCard = (template: ReportTemplate) => {
    const isSelected = selectedTemplate?.id === template.id;
    
    return (
      <div
        key={template.id}
        className={`template-card ${isSelected ? 'selected' : ''}`}
        onClick={() => handleTemplateSelect(template)}
      >
        <div className="template-header">
          <div className="template-icon">
            {template.type === 'users' && <Users size={20} />}
            {template.type === 'projects' && <Target size={20} />}
            {template.type === 'performance' && <TrendingUp size={20} />}
            {template.type === 'custom' && <Settings size={20} />}
          </div>
          <div className="template-info">
            <h3 className="template-name">{template.name}</h3>
            <p className="template-description">{template.description}</p>
          </div>
        </div>
        
        <div className="template-meta">
          <div className="template-metrics">
            <span className="metrics-count">{template.metrics.length} metrics</span>
            <div className="chart-types">
              {template.chartTypes.map(type => (
                <span key={type} className="chart-type">
                  {type === 'bar' && <BarChart3 size={12} />}
                  {type === 'line' && <LineChart size={12} />}
                  {type === 'pie' && <PieChart size={12} />}
                </span>
              ))}
            </div>
          </div>
          
          <div className="template-schedule">
            {template.schedule && (
              <span className="schedule-badge">
                <Clock size={12} />
                {template.schedule}
              </span>
            )}
            {template.lastGenerated && (
              <span className="last-generated">
                Last: {new Date(template.lastGenerated).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderFilters = () => {
    if (selectedFilters.length === 0) return null;

    return (
      <div className="filters-section">
        <h4>Active Filters</h4>
        <div className="filters-list">
          {selectedFilters.map((filter, index) => (
            <div key={index} className="filter-item">
              <span className="filter-label">{filter.label}</span>
              <select
                value={filter.value as string}
                onChange={(e) => {
                  const newFilters = [...selectedFilters];
                  newFilters[index].value = e.target.value;
                  setSelectedFilters(newFilters);
                }}
              >
                <option value="all">All</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderChart = () => {
    if (!reportData || !reportData.data.length) return null;

    const maxValue = Math.max(...reportData.data.map(d => 
      Math.max(...Object.values(d).filter(v => typeof v === 'number'))
    ));

    return (
      <div className="chart-visualization">
        <div className="chart-header">
          <h3>{reportData.name}</h3>
          <div className="chart-actions">
            <button className="chart-toggle">
              <BarChart3 size={16} />
            </button>
            <button className="chart-toggle">
              <LineChart size={16} />
            </button>
            <button className="chart-toggle">
              <PieChart size={16} />
            </button>
          </div>
        </div>
        
        <div className="chart-content">
          <div className="chart-grid">
            {reportData.data.slice(-15).map((point, index) => (
              <div key={index} className="chart-point">
                <div 
                  className="point-bar"
                  style={{
                    height: `${(point[selectedTemplate?.metrics[0] || 'value'] / maxValue) * 100}%`
                  }}
                />
                <span className="point-label">{point.label}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="chart-legend">
          {selectedTemplate?.metrics.map(metric => (
            <div key={metric} className="legend-item">
              <div className="legend-color" />
              <span>{metric.replace('_', ' ').toUpperCase()}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderReportMetadata = () => {
    if (!reportData) return null;

    return (
      <div className="report-metadata">
        <div className="metadata-header">
          <h4>Report Information</h4>
          <div className="realtime-toggle">
            <label>
              <input
                type="checkbox"
                checked={realTimeMode}
                onChange={(e) => setRealTimeMode(e.target.checked)}
              />
              <span>Real-time updates</span>
              {realTimeMode && <div className="pulse-indicator" />}
            </label>
          </div>
        </div>
        
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="metadata-label">Total Records</span>
            <span className="metadata-value">{reportData.metadata.totalRecords.toLocaleString()}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Execution Time</span>
            <span className="metadata-value">{reportData.metadata.executionTime}ms</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Generated</span>
            <span className="metadata-value">
              {new Date(reportData.metadata.generatedAt).toLocaleString()}
            </span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Report ID</span>
            <span className="metadata-value">{reportData.id}</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="realtime-reporting">
      <div className="reporting-header">
        <div className="header-content">
          <h1>Real-time Reporting</h1>
          <p>Generate custom reports and analytics with live data updates</p>
        </div>
        
        <div className="header-actions">
          <button
            className="action-btn secondary"
            onClick={() => console.log('New Template')}
          >
            <Plus size={16} />
            New Template
          </button>
          <div className="export-dropdown">
            <button className="action-btn secondary">
              <Download size={16} />
              Export
              <ChevronDown size={14} />
            </button>
          </div>
          {selectedTemplate && (
            <button
              className="action-btn secondary"
              onClick={() => handleSchedule(selectedTemplate)}
            >
              <Clock size={16} />
              Schedule
            </button>
          )}
        </div>
      </div>

      <div className="reporting-content">
        <div className="reporting-sidebar">
          <div className="sidebar-header">
            <div className="search-bar">
              <Search size={16} />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          <div className="templates-list">
            <h3>Report Templates</h3>
            {filteredTemplates.map(renderTemplateCard)}
          </div>
        </div>

        <div className="reporting-main">
          {selectedTemplate ? (
            <>
              <div className="report-controls">
                <div className="control-group">
                  <button
                    className="control-btn primary"
                    onClick={() => generateReport(selectedTemplate)}
                    disabled={loading}
                  >
                    {loading ? <RefreshCw size={16} className="spinning" /> : <Play size={16} />}
                    {loading ? 'Generating...' : 'Generate Report'}
                  </button>
                  
                  {reportData && (
                    <>
                      <button
                        className="control-btn secondary"
                        onClick={() => handleExport('pdf')}
                      >
                        <Download size={16} />
                        Export PDF
                      </button>
                      <button
                        className="control-btn secondary"
                        onClick={() => console.log('Share report')}
                      >
                        <Share2 size={16} />
                        Share
                      </button>
                    </>
                  )}
                </div>

                {renderFilters()}
              </div>

              {loading && (
                <div className="loading-state">
                  <div className="loading-spinner" />
                  <p>Generating report...</p>
                </div>
              )}

              {reportData && !loading && (
                <div className="report-results">
                  {renderChart()}
                  {renderReportMetadata()}
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <FileText size={64} />
              <h3>Select a Report Template</h3>
              <p>Choose a template from the sidebar to generate your first report</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};