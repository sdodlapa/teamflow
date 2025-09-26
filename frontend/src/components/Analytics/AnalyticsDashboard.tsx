import React, { useState, useEffect, useMemo } from 'react';
import {
  BarChart3, TrendingUp, Users, Target,
  Filter, Download, RefreshCw, Settings,
  Activity, Zap, AlertTriangle, CheckCircle2,
  ArrowUp, ArrowDown, Minus, MoreHorizontal,
  PieChart, LineChart, Activity as Pulse,
  Database, Globe, Shield, Star
} from 'lucide-react';
import './AnalyticsDashboard.css';
import { useDashboardAnalytics, useTaskAnalytics, useProjectAnalytics } from '../../hooks/useAnalytics';

interface AnalyticsMetric {
  id: string;
  name: string;
  value: number;
  previousValue: number;
  format: 'number' | 'percentage' | 'currency' | 'duration';
  trend: 'up' | 'down' | 'neutral';
  category: 'performance' | 'users' | 'tasks' | 'system';
}

interface ChartDataPoint {
  label: string;
  value: number;
  date: string;
  category?: string;
}

interface AnalyticsFilter {
  dateRange: 'today' | '7days' | '30days' | '90days' | 'custom';
  organizations?: string[];
  projects?: string[];
  users?: string[];
  customStart?: string;
  customEnd?: string;
}

interface AnalyticsDashboardProps {
  organizationId?: string;
  projectId?: string;
  userId?: string;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [selectedView, setSelectedView] = useState<'overview' | 'performance' | 'users' | 'projects'>('overview');
  const [filters, setFilters] = useState<AnalyticsFilter>({
    dateRange: '30days'
  });
  const [showFilters, setShowFilters] = useState(false);

    // Real data from analytics API
  const { data: dashboardData, isLoading: loadingDashboard } = useDashboardAnalytics(30);
  const { isLoading: loadingTasks } = useTaskAnalytics(30);
  const { isLoading: loadingProjects } = useProjectAnalytics(30);

  // Combined loading state
  const loading = loadingDashboard || loadingTasks || loadingProjects;
  const metrics: AnalyticsMetric[] = useMemo(() => {
    const stats = dashboardData?.dashboard_stats;
    if (!stats) return [];

    return [
      {
        id: 'total_tasks',
        name: 'Total Tasks',
        value: stats.total_tasks,
        previousValue: Math.round(stats.total_tasks * (1 - stats.tasks_trend / 100)),
        format: 'number',
        trend: stats.tasks_trend > 0 ? 'up' : stats.tasks_trend < 0 ? 'down' : 'neutral',
        category: 'tasks'
      },
      {
        id: 'completion_rate',
        name: 'Completion Rate',
        value: stats.completion_rate,
        previousValue: Math.round((stats.completion_rate * (1 - stats.completion_trend / 100)) * 10) / 10,
        format: 'percentage',
        trend: stats.completion_trend > 0 ? 'up' : stats.completion_trend < 0 ? 'down' : 'neutral',
        category: 'performance'
      },
      {
        id: 'active_users',
        name: 'Active Users',
        value: stats.active_users,
        previousValue: stats.active_users - 3,
        format: 'number',
        trend: 'up',
        category: 'users'
      },
      {
        id: 'productivity_score',
        name: 'Productivity Score',
        value: stats.productivity_score,
        previousValue: Math.round((stats.productivity_score * (1 - stats.productivity_trend / 100)) * 10) / 10,
        format: 'percentage',
        trend: stats.productivity_trend > 0 ? 'up' : stats.productivity_trend < 0 ? 'down' : 'neutral',
        category: 'performance'
      },
      {
        id: 'avg_completion_time',
        name: 'Avg Completion Time',
        value: stats.avg_completion_time_hours,
        previousValue: Math.round((stats.avg_completion_time_hours * (1 + Math.abs(stats.time_trend) / 100)) * 10) / 10,
        format: 'duration',
        trend: stats.time_trend < 0 ? 'up' : stats.time_trend > 0 ? 'down' : 'neutral', // Lower time is better
        category: 'performance'
      },
      {
        id: 'active_projects',
        name: 'Active Projects',
        value: stats.active_projects,
        previousValue: stats.active_projects,
        format: 'number',
        trend: 'neutral',
        category: 'tasks'
      }
    ];
  }, [dashboardData]);

  // Mock chart data (will be replaced with real data later)
  const mockChartData: ChartDataPoint[] = [
    { label: 'Jan', value: 4200, date: '2025-01-01', category: 'users' },
    { label: 'Feb', value: 4600, date: '2025-02-01', category: 'users' },
    { label: 'Mar', value: 5100, date: '2025-03-01', category: 'users' },
    { label: 'Apr', value: 4800, date: '2025-04-01', category: 'users' },
    { label: 'May', value: 5400, date: '2025-05-01', category: 'users' },
    { label: 'Jun', value: 5900, date: '2025-06-01', category: 'users' },
    { label: 'Jul', value: 6200, date: '2025-07-01', category: 'users' },
    { label: 'Aug', value: 5800, date: '2025-08-01', category: 'users' },
    { label: 'Sep', value: 6400, date: '2025-09-01', category: 'users' }
  ];

  const mockTaskData: ChartDataPoint[] = [
    { label: 'To Do', value: 1247, date: '2025-09-25', category: 'todo' },
    { label: 'In Progress', value: 892, date: '2025-09-25', category: 'progress' },
    { label: 'Review', value: 345, date: '2025-09-25', category: 'review' },
    { label: 'Done', value: 2156, date: '2025-09-25', category: 'done' }
  ];

  useEffect(() => {
    // Effects for real data loading are handled by React Query
  }, [filters]);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate API call
    setTimeout(() => {
      setRefreshing(false);
    }, 1000);
  };

  const formatMetricValue = (value: number, format: AnalyticsMetric['format']): string => {
    switch (format) {
      case 'number':
        return value.toLocaleString();
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'duration':
        return `${value}ms`;
      default:
        return value.toString();
    }
  };

  const getTrendIcon = (trend: AnalyticsMetric['trend']) => {
    switch (trend) {
      case 'up':
        return <ArrowUp size={16} className="trend-up" />;
      case 'down':
        return <ArrowDown size={16} className="trend-down" />;
      default:
        return <Minus size={16} className="trend-neutral" />;
    }
  };

  const getTrendPercentage = (current: number, previous: number): number => {
    if (previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  };

  const renderMetricCard = (metric: AnalyticsMetric) => {
    const trendPercentage = getTrendPercentage(metric.value, metric.previousValue);
    
    return (
      <div key={metric.id} className="metric-card">
        <div className="metric-header">
          <h3 className="metric-name">{metric.name}</h3>
          <button className="metric-menu">
            <MoreHorizontal size={16} />
          </button>
        </div>
        
        <div className="metric-value">
          <span className="value-primary">
            {formatMetricValue(metric.value, metric.format)}
          </span>
          <div className="metric-trend">
            {getTrendIcon(metric.trend)}
            <span className={`trend-percentage trend-${metric.trend}`}>
              {Math.abs(trendPercentage).toFixed(1)}%
            </span>
          </div>
        </div>
        
        <div className="metric-comparison">
          vs {formatMetricValue(metric.previousValue, metric.format)} last period
        </div>
        
        <div className="metric-category">
          <span className={`category-badge category-${metric.category}`}>
            {metric.category}
          </span>
        </div>
      </div>
    );
  };

  const renderChart = () => {
    return (
      <div className="chart-container">
        <div className="chart-header">
          <h3>User Activity Trend</h3>
          <div className="chart-actions">
            <button className="chart-action">
              <LineChart size={16} />
            </button>
            <button className="chart-action">
              <BarChart3 size={16} />
            </button>
            <button className="chart-action">
              <PieChart size={16} />
            </button>
          </div>
        </div>
        
        <div className="chart-content">
          <div className="chart-grid">
            {mockChartData.map((point, index) => (
              <div key={index} className="chart-bar">
                <div 
                  className="bar-fill"
                  style={{ 
                    height: `${(point.value / Math.max(...mockChartData.map(p => p.value))) * 100}%` 
                  }}
                />
                <span className="bar-label">{point.label}</span>
                <span className="bar-value">{point.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderTaskDistribution = () => {
    const total = mockTaskData.reduce((sum, item) => sum + item.value, 0);
    
    return (
      <div className="distribution-container">
        <div className="distribution-header">
          <h3>Task Distribution</h3>
          <span className="total-count">{total.toLocaleString()} total</span>
        </div>
        
        <div className="distribution-chart">
          <div className="pie-chart">
            {mockTaskData.map((item, index) => {
              const percentage = (item.value / total) * 100;
              const angle = (percentage / 100) * 360;
              
              return (
                <div
                  key={index}
                  className={`pie-slice slice-${item.category}`}
                  style={{
                    '--slice-angle': `${angle}deg`,
                    '--slice-offset': `${index * 90}deg`
                  } as React.CSSProperties}
                />
              );
            })}
          </div>
          
          <div className="distribution-legend">
            {mockTaskData.map((item, index) => {
              const percentage = (item.value / total) * 100;
              
              return (
                <div key={index} className="legend-item">
                  <div className={`legend-color color-${item.category}`} />
                  <span className="legend-label">{item.label}</span>
                  <span className="legend-value">
                    {item.value.toLocaleString()} ({percentage.toFixed(1)}%)
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  const renderActivityFeed = () => {
    const activities = [
      { icon: CheckCircle2, message: 'Project "Mobile App Redesign" completed', time: '2 minutes ago', type: 'success' },
      { icon: Users, message: '5 new users joined the platform', time: '15 minutes ago', type: 'info' },
      { icon: AlertTriangle, message: 'High CPU usage detected on server-2', time: '32 minutes ago', type: 'warning' },
      { icon: Database, message: 'Database backup completed successfully', time: '1 hour ago', type: 'success' },
      { icon: Shield, message: 'Security scan completed - no issues found', time: '2 hours ago', type: 'success' },
      { icon: Globe, message: 'New deployment to production environment', time: '3 hours ago', type: 'info' }
    ];

    return (
      <div className="activity-feed">
        <div className="activity-header">
          <h3>Recent Activity</h3>
          <button className="view-all-btn">View All</button>
        </div>
        
        <div className="activity-list">
          {activities.map((activity, index) => (
            <div key={index} className={`activity-item activity-${activity.type}`}>
              <div className="activity-icon">
                <activity.icon size={16} />
              </div>
              <div className="activity-content">
                <p className="activity-message">{activity.message}</p>
                <span className="activity-time">{activity.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="loading-spinner" />
        <p>Loading analytics data...</p>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">Analytics Dashboard</h1>
          <p className="dashboard-subtitle">
            Comprehensive insights and performance metrics
          </p>
        </div>
        
        <div className="header-actions">
          <button
            className="action-btn secondary"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={16} />
            Filters
          </button>
          <button
            className="action-btn secondary"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spinning' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <button className="action-btn secondary">
            <Download size={16} />
            Export
          </button>
          <button className="action-btn secondary">
            <Settings size={16} />
            Settings
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="filters-panel">
          <div className="filter-group">
            <label>Date Range</label>
            <select 
              value={filters.dateRange}
              onChange={(e) => setFilters(prev => ({ 
                ...prev, 
                dateRange: e.target.value as AnalyticsFilter['dateRange']
              }))}
            >
              <option value="today">Today</option>
              <option value="7days">Last 7 Days</option>
              <option value="30days">Last 30 Days</option>
              <option value="90days">Last 90 Days</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>View</label>
            <select 
              value={selectedView}
              onChange={(e) => setSelectedView(e.target.value as any)}
            >
              <option value="overview">Overview</option>
              <option value="performance">Performance</option>
              <option value="users">Users</option>
              <option value="projects">Projects</option>
            </select>
          </div>
        </div>
      )}

      <div className="dashboard-nav">
        <button 
          className={`nav-item ${selectedView === 'overview' ? 'active' : ''}`}
          onClick={() => setSelectedView('overview')}
        >
          <BarChart3 size={20} />
          <span>Overview</span>
        </button>
        <button 
          className={`nav-item ${selectedView === 'performance' ? 'active' : ''}`}
          onClick={() => setSelectedView('performance')}
        >
          <TrendingUp size={20} />
          <span>Performance</span>
        </button>
        <button 
          className={`nav-item ${selectedView === 'users' ? 'active' : ''}`}
          onClick={() => setSelectedView('users')}
        >
          <Users size={20} />
          <span>Users</span>
        </button>
        <button 
          className={`nav-item ${selectedView === 'projects' ? 'active' : ''}`}
          onClick={() => setSelectedView('projects')}
        >
          <Target size={20} />
          <span>Projects</span>
        </button>
      </div>

      <div className="dashboard-content">
        <div className="metrics-grid">
          {metrics.map(renderMetricCard)}
        </div>

        <div className="charts-section">
          <div className="chart-row">
            <div className="chart-col-large">
              {renderChart()}
            </div>
            <div className="chart-col-small">
              {renderTaskDistribution()}
            </div>
          </div>
        </div>

        <div className="insights-section">
          <div className="insights-grid">
            <div className="insight-panel">
              {renderActivityFeed()}
            </div>
            
            <div className="insight-panel">
              <div className="performance-summary">
                <h3>Performance Summary</h3>
                <div className="summary-metrics">
                  <div className="summary-item">
                    <Activity size={20} />
                    <div>
                      <span className="summary-label">System Health</span>
                      <span className="summary-value good">Excellent</span>
                    </div>
                  </div>
                  <div className="summary-item">
                    <Pulse size={20} />
                    <div>
                      <span className="summary-label">Response Time</span>
                      <span className="summary-value good">Fast</span>
                    </div>
                  </div>
                  <div className="summary-item">
                    <Star size={20} />
                    <div>
                      <span className="summary-label">User Satisfaction</span>
                      <span className="summary-value good">4.8/5</span>
                    </div>
                  </div>
                  <div className="summary-item">
                    <Zap size={20} />
                    <div>
                      <span className="summary-label">Performance Score</span>
                      <span className="summary-value good">98/100</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};