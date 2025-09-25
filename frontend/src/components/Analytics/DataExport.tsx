import React, { useState } from 'react';
import {
  Download, FileText, Filter, Settings,
  Database, BarChart3, PieChart, FileSpreadsheet,
  Clock, CheckCircle, AlertCircle,
  X, Plus, Trash2, Eye, Save
} from 'lucide-react';
import './DataExport.css';

interface ExportFormat {
  id: string;
  name: string;
  extension: string;
  icon: React.ReactNode;
  description: string;
  supported: boolean;
}

interface DataSource {
  id: string;
  name: string;
  type: 'tasks' | 'users' | 'projects' | 'analytics' | 'performance';
  icon: React.ReactNode;
  description: string;
  recordCount: number;
}

interface ExportFilter {
  field: string;
  operator: 'equals' | 'contains' | 'between' | 'in';
  value: string | string[] | { from: string; to: string };
}

interface ExportTemplate {
  id: string;
  name: string;
  description: string;
  dataSources: string[];
  formats: string[];
  filters: ExportFilter[];
  schedule?: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    time: string;
    emails: string[];
  };
  createdAt: string;
  lastUsed?: string;
}

interface ExportJob {
  id: string;
  templateName: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  startedAt: string;
  completedAt?: string;
  downloadUrl?: string;
  error?: string;
}

interface DataExportProps {
  onClose?: () => void;
}

export const DataExport: React.FC<DataExportProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<'export' | 'templates' | 'history'>('export');
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [selectedFormats, setSelectedFormats] = useState<string[]>(['csv']);
  const [filters, setFilters] = useState<ExportFilter[]>([]);
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  const [exportName, setExportName] = useState('');
  const [templates, setTemplates] = useState<ExportTemplate[]>([]);
  const [exportJobs, setExportJobs] = useState<ExportJob[]>([]);
  const [showTemplateModal, setShowTemplateModal] = useState(false);

  // Mock data
  const exportFormats: ExportFormat[] = [
    {
      id: 'csv',
      name: 'CSV',
      extension: '.csv',
      icon: <FileSpreadsheet size={20} />,
      description: 'Comma-separated values format',
      supported: true
    },
    {
      id: 'json',
      name: 'JSON',
      extension: '.json',
      icon: <FileText size={20} />,
      description: 'JavaScript Object Notation',
      supported: true
    },
    {
      id: 'xlsx',
      name: 'Excel',
      extension: '.xlsx',
      icon: <FileSpreadsheet size={20} />,
      description: 'Microsoft Excel format',
      supported: true
    },
    {
      id: 'pdf',
      name: 'PDF',
      extension: '.pdf',
      icon: <FileText size={20} />,
      description: 'Portable Document Format',
      supported: false
    }
  ];

  const dataSources: DataSource[] = [
    {
      id: 'tasks',
      name: 'Tasks',
      type: 'tasks',
      icon: <CheckCircle size={20} />,
      description: 'All task data including status, assignments, and timestamps',
      recordCount: 1247
    },
    {
      id: 'projects',
      name: 'Projects',
      type: 'projects',
      icon: <Database size={20} />,
      description: 'Project information, timelines, and progress',
      recordCount: 45
    },
    {
      id: 'users',
      name: 'Users',
      type: 'users',
      icon: <Database size={20} />,
      description: 'User profiles and activity data',
      recordCount: 156
    },
    {
      id: 'analytics',
      name: 'Analytics',
      type: 'analytics',
      icon: <BarChart3 size={20} />,
      description: 'Performance metrics and usage statistics',
      recordCount: 8934
    },
    {
      id: 'performance',
      name: 'Performance',
      type: 'performance',
      icon: <PieChart size={20} />,
      description: 'System performance and health metrics',
      recordCount: 12043
    }
  ];

  const mockTemplates: ExportTemplate[] = [
    {
      id: 'weekly-report',
      name: 'Weekly Performance Report',
      description: 'Weekly summary of tasks, projects, and performance metrics',
      dataSources: ['tasks', 'projects', 'analytics'],
      formats: ['csv', 'pdf'],
      filters: [
        { field: 'date', operator: 'between', value: { from: '2024-01-01', to: '2024-01-07' } }
      ],
      schedule: {
        enabled: true,
        frequency: 'weekly',
        time: '09:00',
        emails: ['manager@company.com', 'team@company.com']
      },
      createdAt: '2024-01-15T10:00:00Z',
      lastUsed: '2024-01-22T09:00:00Z'
    },
    {
      id: 'task-export',
      name: 'Task Data Export',
      description: 'Complete export of task information',
      dataSources: ['tasks'],
      formats: ['csv', 'xlsx'],
      filters: [],
      createdAt: '2024-01-10T14:30:00Z',
      lastUsed: '2024-01-20T16:45:00Z'
    }
  ];

  const mockJobs: ExportJob[] = [
    {
      id: 'job-1',
      templateName: 'Weekly Performance Report',
      status: 'completed',
      progress: 100,
      startedAt: '2024-01-22T09:00:00Z',
      completedAt: '2024-01-22T09:02:30Z',
      downloadUrl: '/api/exports/job-1/download'
    },
    {
      id: 'job-2',
      templateName: 'Task Data Export',
      status: 'processing',
      progress: 65,
      startedAt: '2024-01-22T15:30:00Z'
    },
    {
      id: 'job-3',
      templateName: 'User Analytics',
      status: 'failed',
      progress: 0,
      startedAt: '2024-01-22T14:00:00Z',
      error: 'Database connection timeout'
    }
  ];

  React.useEffect(() => {
    setTemplates(mockTemplates);
    setExportJobs(mockJobs);
  }, []);

  const handleSourceToggle = (sourceId: string) => {
    setSelectedSources(prev =>
      prev.includes(sourceId)
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    );
  };

  const handleFormatToggle = (formatId: string) => {
    setSelectedFormats(prev =>
      prev.includes(formatId)
        ? prev.filter(id => id !== formatId)
        : [...prev, formatId]
    );
  };

  const addFilter = () => {
    setFilters(prev => [
      ...prev,
      { field: '', operator: 'equals', value: '' }
    ]);
  };

  const removeFilter = (index: number) => {
    setFilters(prev => prev.filter((_, i) => i !== index));
  };

  const updateFilter = (index: number, updates: Partial<ExportFilter>) => {
    setFilters(prev => prev.map((filter, i) =>
      i === index ? { ...filter, ...updates } : filter
    ));
  };

  const handleExport = async () => {
    if (selectedSources.length === 0) {
      alert('Please select at least one data source');
      return;
    }

    if (selectedFormats.length === 0) {
      alert('Please select at least one export format');
      return;
    }

    // Create new export job
    const newJob: ExportJob = {
      id: `job-${Date.now()}`,
      templateName: exportName || 'Custom Export',
      status: 'pending',
      progress: 0,
      startedAt: new Date().toISOString()
    };

    setExportJobs(prev => [newJob, ...prev]);
    setActiveTab('history');

    // Simulate export processing
    setTimeout(() => {
      setExportJobs(prev => prev.map(job =>
        job.id === newJob.id
          ? { ...job, status: 'processing', progress: 25 }
          : job
      ));
    }, 500);

    setTimeout(() => {
      setExportJobs(prev => prev.map(job =>
        job.id === newJob.id
          ? { ...job, progress: 75 }
          : job
      ));
    }, 2000);

    setTimeout(() => {
      setExportJobs(prev => prev.map(job =>
        job.id === newJob.id
          ? {
              ...job,
              status: 'completed',
              progress: 100,
              completedAt: new Date().toISOString(),
              downloadUrl: `/api/exports/${newJob.id}/download`
            }
          : job
      ));
    }, 4000);
  };

  const saveAsTemplate = () => {
    if (!exportName.trim()) {
      alert('Please enter a template name');
      return;
    }

    const newTemplate: ExportTemplate = {
      id: `template-${Date.now()}`,
      name: exportName,
      description: `Custom template for ${selectedSources.join(', ')} export`,
      dataSources: selectedSources,
      formats: selectedFormats,
      filters,
      createdAt: new Date().toISOString()
    };

    setTemplates(prev => [newTemplate, ...prev]);
    setShowTemplateModal(false);
    alert('Template saved successfully!');
  };

  const loadTemplate = (template: ExportTemplate) => {
    setSelectedSources(template.dataSources);
    setSelectedFormats(template.formats);
    setFilters(template.filters);
    setExportName(template.name);
    setActiveTab('export');
  };

  const getStatusColor = (status: ExportJob['status']) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'processing':
      case 'pending':
        return '#3b82f6';
      case 'failed':
        return '#ef4444';
      default:
        return '#64748b';
    }
  };

  const renderExportTab = () => (
    <div className="export-tab">
      <div className="export-section">
        <h3>Data Sources</h3>
        <div className="sources-grid">
          {dataSources.map(source => (
            <div
              key={source.id}
              className={`source-card ${selectedSources.includes(source.id) ? 'selected' : ''}`}
              onClick={() => handleSourceToggle(source.id)}
            >
              <div className="source-icon">{source.icon}</div>
              <div className="source-info">
                <div className="source-name">{source.name}</div>
                <div className="source-description">{source.description}</div>
                <div className="source-count">{source.recordCount.toLocaleString()} records</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="export-section">
        <h3>Export Formats</h3>
        <div className="formats-grid">
          {exportFormats.map(format => (
            <div
              key={format.id}
              className={`format-card ${selectedFormats.includes(format.id) ? 'selected' : ''} ${!format.supported ? 'disabled' : ''}`}
              onClick={() => format.supported && handleFormatToggle(format.id)}
            >
              <div className="format-icon">{format.icon}</div>
              <div className="format-info">
                <div className="format-name">{format.name}</div>
                <div className="format-description">{format.description}</div>
                {!format.supported && <div className="format-coming-soon">Coming Soon</div>}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="export-section">
        <h3>Filters & Options</h3>
        
        <div className="filter-controls">
          <div className="date-range">
            <label>Date Range</label>
            <div className="date-inputs">
              <input
                type="date"
                value={dateRange.from}
                onChange={(e) => setDateRange(prev => ({ ...prev, from: e.target.value }))}
                placeholder="From date"
              />
              <span>to</span>
              <input
                type="date"
                value={dateRange.to}
                onChange={(e) => setDateRange(prev => ({ ...prev, to: e.target.value }))}
                placeholder="To date"
              />
            </div>
          </div>

          <div className="export-name">
            <label>Export Name</label>
            <input
              type="text"
              value={exportName}
              onChange={(e) => setExportName(e.target.value)}
              placeholder="Enter export name (optional)"
            />
          </div>
        </div>

        <div className="custom-filters">
          <div className="filters-header">
            <span>Custom Filters</span>
            <button className="add-filter-btn" onClick={addFilter}>
              <Plus size={16} />
              Add Filter
            </button>
          </div>
          
          {filters.map((filter, index) => (
            <div key={index} className="filter-row">
              <select
                value={filter.field}
                onChange={(e) => updateFilter(index, { field: e.target.value })}
              >
                <option value="">Select field</option>
                <option value="status">Status</option>
                <option value="priority">Priority</option>
                <option value="assignee">Assignee</option>
                <option value="project">Project</option>
                <option value="created_date">Created Date</option>
              </select>
              
              <select
                value={filter.operator}
                onChange={(e) => updateFilter(index, { operator: e.target.value as any })}
              >
                <option value="equals">Equals</option>
                <option value="contains">Contains</option>
                <option value="between">Between</option>
                <option value="in">In</option>
              </select>
              
              <input
                type="text"
                value={filter.value as string}
                onChange={(e) => updateFilter(index, { value: e.target.value })}
                placeholder="Filter value"
              />
              
              <button
                className="remove-filter-btn"
                onClick={() => removeFilter(index)}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="export-actions">
        <button className="action-btn secondary" onClick={() => setShowTemplateModal(true)}>
          <Save size={16} />
          Save as Template
        </button>
        <button className="action-btn primary" onClick={handleExport}>
          <Download size={16} />
          Start Export
        </button>
      </div>
    </div>
  );

  const renderTemplatesTab = () => (
    <div className="templates-tab">
      <div className="templates-header">
        <h3>Export Templates</h3>
        <button className="action-btn primary" onClick={() => setActiveTab('export')}>
          <Plus size={16} />
          New Template
        </button>
      </div>

      <div className="templates-list">
        {templates.map(template => (
          <div key={template.id} className="template-card">
            <div className="template-info">
              <div className="template-name">{template.name}</div>
              <div className="template-description">{template.description}</div>
              <div className="template-meta">
                <span>Sources: {template.dataSources.join(', ')}</span>
                <span>Formats: {template.formats.join(', ')}</span>
                {template.lastUsed && (
                  <span>Last used: {new Date(template.lastUsed).toLocaleDateString()}</span>
                )}
              </div>
            </div>
            <div className="template-actions">
              <button
                className="template-action-btn"
                onClick={() => loadTemplate(template)}
                title="Use Template"
              >
                <Eye size={16} />
              </button>
              <button
                className="template-action-btn"
                onClick={() => console.log('Edit template:', template.id)}
                title="Edit Template"
              >
                <Settings size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderHistoryTab = () => (
    <div className="history-tab">
      <div className="history-header">
        <h3>Export History</h3>
        <button className="action-btn secondary">
          <Filter size={16} />
          Filter
        </button>
      </div>

      <div className="jobs-list">
        {exportJobs.map(job => (
          <div key={job.id} className="job-card">
            <div className="job-info">
              <div className="job-name">{job.templateName}</div>
              <div className="job-time">
                <Clock size={12} />
                Started: {new Date(job.startedAt).toLocaleString()}
              </div>
              {job.completedAt && (
                <div className="job-time">
                  <CheckCircle size={12} />
                  Completed: {new Date(job.completedAt).toLocaleString()}
                </div>
              )}
              {job.error && (
                <div className="job-error">
                  <AlertCircle size={12} />
                  {job.error}
                </div>
              )}
            </div>

            <div className="job-status">
              <div
                className="status-indicator"
                style={{ color: getStatusColor(job.status) }}
              >
                {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
              </div>
              
              {job.status === 'processing' && (
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              )}
              
              {job.status === 'completed' && job.downloadUrl && (
                <button className="download-btn">
                  <Download size={14} />
                  Download
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="data-export">
      <div className="export-header">
        <div className="header-content">
          <h1>Data Export</h1>
          <p>Export your data in various formats with custom filters and scheduling</p>
        </div>
        {onClose && (
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        )}
      </div>

      <div className="export-tabs">
        <button
          className={`tab-btn ${activeTab === 'export' ? 'active' : ''}`}
          onClick={() => setActiveTab('export')}
        >
          <Download size={16} />
          Export Data
        </button>
        <button
          className={`tab-btn ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          <FileText size={16} />
          Templates
        </button>
        <button
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <Clock size={16} />
          History
        </button>
      </div>

      <div className="export-content">
        {activeTab === 'export' && renderExportTab()}
        {activeTab === 'templates' && renderTemplatesTab()}
        {activeTab === 'history' && renderHistoryTab()}
      </div>

      {showTemplateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Save Export Template</h3>
              <button className="close-btn" onClick={() => setShowTemplateModal(false)}>
                <X size={16} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Template Name</label>
                <input
                  type="text"
                  value={exportName}
                  onChange={(e) => setExportName(e.target.value)}
                  placeholder="Enter template name"
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  placeholder="Enter template description"
                  rows={3}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="action-btn secondary"
                onClick={() => setShowTemplateModal(false)}
              >
                Cancel
              </button>
              <button className="action-btn primary" onClick={saveAsTemplate}>
                Save Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};