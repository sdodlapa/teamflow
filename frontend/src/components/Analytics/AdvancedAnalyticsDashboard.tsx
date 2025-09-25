import React, { useState, useEffect, useMemo } from 'react';
import { 
  LineChart, PieChart, TrendingUp, TrendingDown, 
  Calendar, Filter, Download, RefreshCw, Settings, Eye,
  Users, CheckCircle, Clock, AlertTriangle, Target, Activity,
  ArrowUp, ArrowDown, MoreHorizontal,
  Grid, List, Maximize2
} from 'lucide-react';
import './AdvancedAnalyticsDashboard.css';

// Types for Analytics Dashboard
interface AnalyticsData {
  overview: OverviewMetrics;
  taskMetrics: TaskAnalytics;
  userMetrics: UserAnalytics;
  projectMetrics: ProjectAnalytics;
  performanceMetrics: PerformanceAnalytics;
  timeSeriesData: TimeSeriesData[];
  chartData: ChartData[];
}

interface OverviewMetrics {
  totalTasks: number;
  completedTasks: number;
  activeTasks: number;
  overdueTasks: number;
  totalUsers: number;
  activeUsers: number;
  totalProjects: number;
  activeProjects: number;
  completionRate: number;
  productivityScore: number;
}

interface TaskAnalytics {
  completionTrends: TrendData[];
  priorityDistribution: DistributionData[];
  statusDistribution: DistributionData[];
  averageCompletionTime: number;
  taskVelocity: number;
  burndownData: BurndownData[];
}

interface UserAnalytics {
  topPerformers: UserPerformance[];
  teamProductivity: TeamProductivity[];
  userActivity: UserActivity[];
  collaborationMetrics: CollaborationMetrics;
}

interface ProjectAnalytics {
  projectProgress: ProjectProgress[];
  milestoneTracking: MilestoneData[];
  budgetTracking: BudgetData[];
  timeTracking: TimeData[];
  riskAssessment: RiskData[];
}

interface PerformanceAnalytics {
  systemMetrics: SystemMetrics;
  apiMetrics: APIMetrics;
  errorTracking: ErrorData[];
  performanceTrends: PerformanceTrend[];
}

interface TrendData {
  period: string;
  value: number;
  change: number;
  target?: number;
}

interface DistributionData {
  label: string;
  value: number;
  percentage: number;
  color: string;
}

interface BurndownData {
  period: string;
  value: number;
  target: number;
}

interface UserPerformance {
  userId: string;
  name: string;
  completedTasks: number;
  score: number;
}

interface TeamProductivity {
  teamId: string;
  name: string;
  productivity: number;
  trend: 'up' | 'down';
}

interface UserActivity {
  userId: string;
  name: string;
  lastActive: string;
  sessionsToday: number;
}

interface CollaborationMetrics {
  averageResponseTime: number;
  collaborationScore: number;
  meetingsPerWeek: number;
}

interface ProjectProgress {
  projectId: string;
  name: string;
  progress: number;
  status: string;
  dueDate: string;
  budget: {
    allocated: number;
    spent: number;
  };
}

interface MilestoneData {
  milestoneId: string;
  name: string;
  status: string;
  completedDate?: string;
  targetDate?: string;
}

interface BudgetData {
  projectId: string;
  allocated: number;
  spent: number;
  remaining: number;
  burnRate: number;
}

interface TimeData {
  projectId: string;
  estimated: number;
  actual: number;
  remaining: number;
}

interface RiskData {
  riskId: string;
  project: string;
  risk: string;
  impact: string;
  probability: string;
}

interface SystemMetrics {
  uptime: number;
  responseTime: number;
  throughput: number;
  errorRate: number;
}

interface APIMetrics {
  totalRequests: number;
  averageResponseTime: number;
  successRate: number;
  rateLimitHits: number;
}

interface ErrorData {
  errorId: string;
  message: string;
  count: number;
  severity: string;
}

interface PerformanceTrend {
  period: string;
  responseTime: number;
  throughput: number;
  errors: number;
}

interface TimeSeriesData {
  timestamp: string;
  value: number;
  category: string;
}

interface ChartData {
  id: string;
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter';
  data: any[];
  config: ChartConfig;
}

interface ChartConfig {
  xAxis?: string;
  yAxis?: string;
  colors: string[];
  showLegend: boolean;
  showGrid: boolean;
  responsive: boolean;
}






const AdvancedAnalyticsDashboard: React.FC = () => {
  // Core state
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    overview: {
      totalTasks: 2847,
      completedTasks: 1923,
      activeTasks: 756,
      overdueTasks: 168,
      totalUsers: 145,
      activeUsers: 89,
      totalProjects: 23,
      activeProjects: 18,
      completionRate: 87.5,
      productivityScore: 92.3
    },
    taskMetrics: {
      completionTrends: [
        { period: '2024-01', value: 234, change: 12.5, target: 250 },
        { period: '2024-02', value: 267, change: 14.1, target: 250 },
        { period: '2024-03', value: 298, change: 11.6, target: 280 },
        { period: '2024-04', value: 312, change: 4.7, target: 300 },
        { period: '2024-05', value: 289, change: -7.4, target: 310 },
        { period: '2024-06', value: 334, change: 15.6, target: 320 }
      ],
      priorityDistribution: [
        { label: 'High', value: 234, percentage: 28.5, color: '#ef4444' },
        { label: 'Medium', value: 456, percentage: 55.4, color: '#f59e0b' },
        { label: 'Low', value: 132, percentage: 16.1, color: '#10b981' }
      ],
      statusDistribution: [
        { label: 'Completed', value: 1923, percentage: 67.5, color: '#10b981' },
        { label: 'In Progress', value: 756, percentage: 26.6, color: '#3b82f6' },
        { label: 'Todo', value: 168, percentage: 5.9, color: '#6b7280' }
      ],
      averageCompletionTime: 4.2,
      taskVelocity: 23.8,
      burndownData: [
        { period: 'Week 1', value: 100, target: 95 },
        { period: 'Week 2', value: 85, target: 80 },
        { period: 'Week 3', value: 68, target: 65 },
        { period: 'Week 4', value: 45, target: 50 },
        { period: 'Week 5', value: 32, target: 35 },
        { period: 'Week 6', value: 18, target: 20 }
      ]
    },
    userMetrics: {
      topPerformers: [
        { userId: '1', name: 'Sarah Chen', completedTasks: 89, score: 94.5 },
        { userId: '2', name: 'Mike Johnson', completedTasks: 82, score: 91.2 },
        { userId: '3', name: 'Emily Rodriguez', completedTasks: 76, score: 88.7 }
      ],
      teamProductivity: [
        { teamId: '1', name: 'Engineering', productivity: 92.3, trend: 'up' },
        { teamId: '2', name: 'Design', productivity: 89.1, trend: 'up' },
        { teamId: '3', name: 'Marketing', productivity: 85.4, trend: 'down' }
      ],
      userActivity: [
        { userId: '1', name: 'Sarah Chen', lastActive: '2024-01-15T14:30:00Z', sessionsToday: 3 }
      ],
      collaborationMetrics: {
        averageResponseTime: 2.3,
        collaborationScore: 87.6,
        meetingsPerWeek: 12.4
      }
    },
    projectMetrics: {
      projectProgress: [
        { 
          projectId: '1', 
          name: 'TeamFlow V2', 
          progress: 78, 
          status: 'on-track',
          dueDate: '2024-03-01',
          budget: { allocated: 150000, spent: 89000 }
        },
        { 
          projectId: '2', 
          name: 'Mobile App', 
          progress: 45, 
          status: 'at-risk',
          dueDate: '2024-04-15',
          budget: { allocated: 200000, spent: 125000 }
        }
      ],
      milestoneTracking: [
        { milestoneId: '1', name: 'MVP Release', status: 'completed', completedDate: '2024-01-10' },
        { milestoneId: '2', name: 'Beta Testing', status: 'in-progress', targetDate: '2024-02-01' }
      ],
      budgetTracking: [
        { projectId: '1', allocated: 150000, spent: 89000, remaining: 61000, burnRate: 0.59 }
      ],
      timeTracking: [
        { projectId: '1', estimated: 2400, actual: 1890, remaining: 510 }
      ],
      riskAssessment: [
        { riskId: '1', project: 'TeamFlow V2', risk: 'Resource Allocation', impact: 'medium', probability: 'low' }
      ]
    },
    performanceMetrics: {
      systemMetrics: {
        uptime: 99.95,
        responseTime: 245,
        throughput: 1250,
        errorRate: 0.02
      },
      apiMetrics: {
        totalRequests: 1250000,
        averageResponseTime: 180,
        successRate: 99.8,
        rateLimitHits: 45
      },
      errorTracking: [
        { errorId: '1', message: 'Connection timeout', count: 12, severity: 'medium' }
      ],
      performanceTrends: [
        { period: '2024-01-01', responseTime: 245, throughput: 1250, errors: 3 }
      ]
    },
    timeSeriesData: [
      { timestamp: '2024-01-01T00:00:00Z', value: 150, category: 'tasks' },
      { timestamp: '2024-01-02T00:00:00Z', value: 165, category: 'tasks' }
    ],
    chartData: [
      {
        id: '1',
        title: 'Task Completion Trends',
        type: 'line',
        data: [],
        config: {
          colors: ['#3b82f6', '#10b981'],
          showLegend: true,
          showGrid: true,
          responsive: true
        }
      }
    ]
  });

  // UI state
  const [selectedDashboard, setSelectedDashboard] = useState<string>('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('30d');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isCustomizing, setIsCustomizing] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Dashboard configurations
  const dashboards = [
    { id: 'overview', name: 'Executive Overview', icon: TrendingUp },
    { id: 'tasks', name: 'Task Analytics', icon: CheckCircle },
    { id: 'users', name: 'Team Performance', icon: Users },
    { id: 'projects', name: 'Project Insights', icon: Target },
    { id: 'performance', name: 'System Performance', icon: Activity }
  ];

  const timeRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' },
    { value: 'custom', label: 'Custom Range' }
  ];

  // Compute derived metrics
  const derivedMetrics = useMemo(() => {
    const { overview, taskMetrics } = analyticsData;
    
    return {
      completionRateChange: taskMetrics.completionTrends.length > 1 
        ? taskMetrics.completionTrends[taskMetrics.completionTrends.length - 1].change
        : 0,
      overduePercentage: (overview.overdueTasks / overview.totalTasks) * 100,
      activeUserPercentage: (overview.activeUsers / overview.totalUsers) * 100,
      projectSuccessRate: 85.4, // Calculated based on project status
      avgTasksPerUser: overview.totalTasks / overview.totalUsers
    };
  }, [analyticsData]);

  // Refresh analytics data
  const refreshAnalytics = async () => {
    setRefreshing(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Update data with small random variations to simulate real-time updates
    setAnalyticsData(prev => ({
      ...prev,
      overview: {
        ...prev.overview,
        activeTasks: prev.overview.activeTasks + Math.floor(Math.random() * 10) - 5,
        completionRate: Math.max(0, Math.min(100, prev.overview.completionRate + (Math.random() * 4) - 2))
      }
    }));
    
    setRefreshing(false);
  };

  // Format large numbers
  const formatNumber = (num: number): string => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  // Format percentage with trend indicator
  const formatPercentageWithTrend = (value: number, trend?: number) => {
    const trendIcon = trend !== undefined ? (
      trend > 0 ? <ArrowUp size={12} className="trend-up" /> : 
      trend < 0 ? <ArrowDown size={12} className="trend-down" /> : null
    ) : null;
    
    return (
      <span className="percentage-with-trend">
        {value.toFixed(1)}%
        {trendIcon}
        {trend !== undefined && (
          <span className={`trend-value ${trend > 0 ? 'positive' : trend < 0 ? 'negative' : 'neutral'}`}>
            {Math.abs(trend).toFixed(1)}%
          </span>
        )}
      </span>
    );
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on-track': return '#10b981';
      case 'at-risk': return '#f59e0b';
      case 'delayed': return '#ef4444';
      case 'completed': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  // Effect for auto-refresh
  useEffect(() => {
    const interval = setInterval(refreshAnalytics, 300000); // 5 minutes
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="analytics-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-left">
          <div className="dashboard-title">
            <h1>Analytics Dashboard</h1>
            <p className="dashboard-subtitle">
              Real-time insights and performance metrics for TeamFlow
            </p>
          </div>
        </div>

        <div className="header-controls">
          <div className="time-range-selector">
            <Calendar size={16} />
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="time-range-select"
            >
              {timeRanges.map(range => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
          </div>

          <button 
            className="control-btn"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={16} />
            Filters
          </button>

          <button 
            className="control-btn"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
          >
            {viewMode === 'grid' ? <List size={16} /> : <Grid size={16} />}
            {viewMode === 'grid' ? 'List' : 'Grid'}
          </button>

          <button 
            className="control-btn primary"
            onClick={refreshAnalytics}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spinning' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>

          <button className="control-btn secondary">
            <Download size={16} />
            Export
          </button>

          <div className="control-divider"></div>

          <button className="control-btn">
            <Settings size={16} />
          </button>
        </div>
      </div>

      {/* Dashboard Navigation */}
      <div className="dashboard-navigation">
        <div className="nav-tabs">
          {dashboards.map(dashboard => {
            const Icon = dashboard.icon;
            return (
              <button
                key={dashboard.id}
                className={`nav-tab ${selectedDashboard === dashboard.id ? 'active' : ''}`}
                onClick={() => setSelectedDashboard(dashboard.id)}
              >
                <Icon size={16} />
                {dashboard.name}
              </button>
            );
          })}
        </div>

        <div className="nav-actions">
          <button 
            className="action-btn"
            onClick={() => setIsCustomizing(!isCustomizing)}
          >
            <Settings size={16} />
            Customize
          </button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filters-content">
            <div className="filter-group">
              <label>Project</label>
              <select className="filter-select">
                <option value="">All Projects</option>
                <option value="1">TeamFlow V2</option>
                <option value="2">Mobile App</option>
              </select>
            </div>
            
            <div className="filter-group">
              <label>Team</label>
              <select className="filter-select">
                <option value="">All Teams</option>
                <option value="engineering">Engineering</option>
                <option value="design">Design</option>
                <option value="marketing">Marketing</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Status</label>
              <select className="filter-select">
                <option value="">All Status</option>
                <option value="completed">Completed</option>
                <option value="in-progress">In Progress</option>
                <option value="todo">To Do</option>
              </select>
            </div>

            <div className="filter-actions">
              <button className="filter-btn primary">Apply Filters</button>
              <button className="filter-btn secondary">Clear All</button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="dashboard-content">
        {selectedDashboard === 'overview' && (
          <div className="overview-dashboard">
            {/* Key Metrics Overview */}
            <div className="metrics-overview">
              <div className="metrics-grid">
                <div className="metric-card primary">
                  <div className="metric-header">
                    <div className="metric-icon">
                      <CheckCircle size={24} />
                    </div>
                    <div className="metric-trend positive">
                      <TrendingUp size={16} />
                    </div>
                  </div>
                  <div className="metric-value">
                    {formatNumber(analyticsData.overview.completedTasks)}
                  </div>
                  <div className="metric-label">Tasks Completed</div>
                  <div className="metric-change">
                    +{derivedMetrics.completionRateChange.toFixed(1)}% from last month
                  </div>
                </div>

                <div className="metric-card secondary">
                  <div className="metric-header">
                    <div className="metric-icon">
                      <Clock size={24} />
                    </div>
                    <div className="metric-trend neutral">
                      <Activity size={16} />
                    </div>
                  </div>
                  <div className="metric-value">
                    {formatNumber(analyticsData.overview.activeTasks)}
                  </div>
                  <div className="metric-label">Active Tasks</div>
                  <div className="metric-change">
                    {formatPercentageWithTrend(
                      (analyticsData.overview.activeTasks / analyticsData.overview.totalTasks) * 100
                    )}
                  </div>
                </div>

                <div className="metric-card warning">
                  <div className="metric-header">
                    <div className="metric-icon">
                      <AlertTriangle size={24} />
                    </div>
                    <div className="metric-trend negative">
                      <TrendingDown size={16} />
                    </div>
                  </div>
                  <div className="metric-value">
                    {analyticsData.overview.overdueTasks}
                  </div>
                  <div className="metric-label">Overdue Tasks</div>
                  <div className="metric-change">
                    {formatPercentageWithTrend(derivedMetrics.overduePercentage)}
                  </div>
                </div>

                <div className="metric-card success">
                  <div className="metric-header">
                    <div className="metric-icon">
                      <Users size={24} />
                    </div>
                    <div className="metric-trend positive">
                      <TrendingUp size={16} />
                    </div>
                  </div>
                  <div className="metric-value">
                    {analyticsData.overview.activeUsers}
                  </div>
                  <div className="metric-label">Active Users</div>
                  <div className="metric-change">
                    {formatPercentageWithTrend(derivedMetrics.activeUserPercentage)}
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Score */}
            <div className="performance-section">
              <div className="section-header">
                <h3>Overall Performance</h3>
                <div className="performance-actions">
                  <button className="performance-btn">
                    <Eye size={16} />
                    Details
                  </button>
                </div>
              </div>
              
              <div className="performance-cards">
                <div className="performance-card">
                  <div className="performance-title">Completion Rate</div>
                  <div className="performance-value">
                    {analyticsData.overview.completionRate.toFixed(1)}%
                  </div>
                  <div className="performance-bar">
                    <div 
                      className="performance-fill"
                      style={{ width: `${analyticsData.overview.completionRate}%` }}
                    ></div>
                  </div>
                  <div className="performance-target">
                    Target: 85%
                  </div>
                </div>

                <div className="performance-card">
                  <div className="performance-title">Productivity Score</div>
                  <div className="performance-value">
                    {analyticsData.overview.productivityScore.toFixed(1)}
                  </div>
                  <div className="performance-bar">
                    <div 
                      className="performance-fill"
                      style={{ width: `${analyticsData.overview.productivityScore}%` }}
                    ></div>
                  </div>
                  <div className="performance-target">
                    Target: 90.0
                  </div>
                </div>

                <div className="performance-card">
                  <div className="performance-title">Project Success Rate</div>
                  <div className="performance-value">
                    {derivedMetrics.projectSuccessRate.toFixed(1)}%
                  </div>
                  <div className="performance-bar">
                    <div 
                      className="performance-fill"
                      style={{ width: `${derivedMetrics.projectSuccessRate}%` }}
                    ></div>
                  </div>
                  <div className="performance-target">
                    Target: 80%
                  </div>
                </div>
              </div>
            </div>

            {/* Charts Section */}
            <div className="charts-section">
              <div className="charts-grid">
                <div className="chart-card">
                  <div className="chart-header">
                    <h4>Task Completion Trends</h4>
                    <div className="chart-actions">
                      <button className="chart-action-btn">
                        <Maximize2 size={16} />
                      </button>
                      <button className="chart-action-btn">
                        <MoreHorizontal size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="chart-content">
                    <div className="chart-placeholder line-chart">
                      <LineChart size={48} />
                      <p>Task completion trends over time</p>
                      <div className="chart-data-points">
                        {analyticsData.taskMetrics.completionTrends.map((point, index) => (
                          <div key={index} className="data-point">
                            <span className="point-period">{point.period}</span>
                            <span className="point-value">{point.value}</span>
                            <span className={`point-change ${point.change > 0 ? 'positive' : 'negative'}`}>
                              {point.change > 0 ? '+' : ''}{point.change.toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="chart-card">
                  <div className="chart-header">
                    <h4>Priority Distribution</h4>
                    <div className="chart-actions">
                      <button className="chart-action-btn">
                        <Maximize2 size={16} />
                      </button>
                      <button className="chart-action-btn">
                        <MoreHorizontal size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="chart-content">
                    <div className="chart-placeholder pie-chart">
                      <PieChart size={48} />
                      <p>Task distribution by priority</p>
                      <div className="pie-legend">
                        {analyticsData.taskMetrics.priorityDistribution.map((item, index) => (
                          <div key={index} className="legend-item">
                            <div 
                              className="legend-color"
                              style={{ backgroundColor: item.color }}
                            ></div>
                            <span className="legend-label">{item.label}</span>
                            <span className="legend-value">
                              {item.value} ({item.percentage}%)
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="chart-card full-width">
                  <div className="chart-header">
                    <h4>Project Progress Overview</h4>
                    <div className="chart-actions">
                      <button className="chart-action-btn">
                        <Maximize2 size={16} />
                      </button>
                      <button className="chart-action-btn">
                        <MoreHorizontal size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="chart-content">
                    <div className="project-progress-chart">
                      {analyticsData.projectMetrics.projectProgress.map((project) => (
                        <div key={project.projectId} className="project-progress-item">
                          <div className="project-info">
                            <div className="project-name">{project.name}</div>
                            <div className="project-meta">
                              <span className="project-due">Due: {new Date(project.dueDate).toLocaleDateString()}</span>
                              <span 
                                className="project-status"
                                style={{ color: getStatusColor(project.status) }}
                              >
                                {project.status.replace('-', ' ')}
                              </span>
                            </div>
                          </div>
                          <div className="project-progress-bar">
                            <div 
                              className="progress-fill"
                              style={{ 
                                width: `${project.progress}%`,
                                backgroundColor: getStatusColor(project.status)
                              }}
                            ></div>
                          </div>
                          <div className="project-progress-value">
                            {project.progress}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Team Performance */}
            <div className="team-section">
              <div className="section-header">
                <h3>Team Performance</h3>
                <div className="section-actions">
                  <button className="section-btn">View All Teams</button>
                </div>
              </div>

              <div className="team-performance-grid">
                {analyticsData.userMetrics.teamProductivity.map((team) => (
                  <div key={team.teamId} className="team-card">
                    <div className="team-header">
                      <div className="team-name">{team.name}</div>
                      <div className={`team-trend ${team.trend}`}>
                        {team.trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                      </div>
                    </div>
                    <div className="team-score">
                      {team.productivity.toFixed(1)}
                    </div>
                    <div className="team-label">Productivity Score</div>
                    <div className="team-progress">
                      <div 
                        className="team-progress-fill"
                        style={{ width: `${team.productivity}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedDashboard === 'tasks' && (
          <div className="tasks-dashboard">
            <div className="dashboard-section">
              <div className="section-header">
                <h3>Task Analytics</h3>
                <p className="section-description">
                  Comprehensive insights into task performance and completion patterns
                </p>
              </div>

              <div className="tasks-metrics-grid">
                <div className="task-metric-card">
                  <div className="metric-title">Average Completion Time</div>
                  <div className="metric-value large">
                    {analyticsData.taskMetrics.averageCompletionTime.toFixed(1)} days
                  </div>
                  <div className="metric-subtitle">
                    Down from 4.8 days last month
                  </div>
                </div>

                <div className="task-metric-card">
                  <div className="metric-title">Task Velocity</div>
                  <div className="metric-value large">
                    {analyticsData.taskMetrics.taskVelocity.toFixed(1)} tasks/week
                  </div>
                  <div className="metric-subtitle">
                    Team average across all projects
                  </div>
                </div>

                <div className="task-metric-card">
                  <div className="metric-title">Burndown Progress</div>
                  <div className="metric-value large">
                    82% on track
                  </div>
                  <div className="metric-subtitle">
                    Current sprint progress
                  </div>
                </div>
              </div>

              <div className="task-charts-grid">
                <div className="chart-card">
                  <div className="chart-header">
                    <h4>Burndown Chart</h4>
                    <select className="chart-filter">
                      <option>Current Sprint</option>
                      <option>Last Sprint</option>
                      <option>All Sprints</option>
                    </select>
                  </div>
                  <div className="chart-content">
                    <div className="burndown-chart">
                      {analyticsData.taskMetrics.burndownData.map((point, index) => (
                        <div key={index} className="burndown-point">
                          <div className="burndown-period">{point.period}</div>
                          <div className="burndown-bars">
                            <div className="burndown-bar actual" style={{ height: `${point.value}%` }}>
                              <span className="bar-value">{point.value}</span>
                            </div>
                            <div className="burndown-bar target" style={{ height: `${point.target}%` }}>
                              <span className="bar-value">{point.target}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="chart-legend">
                      <div className="legend-item">
                        <div className="legend-color actual"></div>
                        <span>Actual</span>
                      </div>
                      <div className="legend-item">
                        <div className="legend-color target"></div>
                        <span>Target</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="chart-card">
                  <div className="chart-header">
                    <h4>Status Distribution</h4>
                    <button className="chart-export-btn">
                      <Download size={16} />
                    </button>
                  </div>
                  <div className="chart-content">
                    <div className="status-distribution">
                      {analyticsData.taskMetrics.statusDistribution.map((status, index) => (
                        <div key={index} className="status-item">
                          <div className="status-info">
                            <div 
                              className="status-color"
                              style={{ backgroundColor: status.color }}
                            ></div>
                            <div className="status-details">
                              <div className="status-label">{status.label}</div>
                              <div className="status-count">{formatNumber(status.value)} tasks</div>
                            </div>
                          </div>
                          <div className="status-percentage">
                            {status.percentage.toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedDashboard === 'users' && (
          <div className="users-dashboard">
            <div className="dashboard-section">
              <div className="section-header">
                <h3>Team Performance Analytics</h3>
                <p className="section-description">
                  Individual and team productivity insights
                </p>
              </div>

              <div className="top-performers">
                <h4>Top Performers This Month</h4>
                <div className="performers-list">
                  {analyticsData.userMetrics.topPerformers.map((performer, index) => (
                    <div key={performer.userId} className="performer-card">
                      <div className="performer-rank">#{index + 1}</div>
                      <div className="performer-info">
                        <div className="performer-name">{performer.name}</div>
                        <div className="performer-stats">
                          {performer.completedTasks} tasks completed
                        </div>
                      </div>
                      <div className="performer-score">
                        {performer.score.toFixed(1)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="collaboration-metrics">
                <h4>Collaboration Insights</h4>
                <div className="collaboration-grid">
                  <div className="collaboration-card">
                    <div className="collaboration-metric">
                      {analyticsData.userMetrics.collaborationMetrics.averageResponseTime.toFixed(1)}h
                    </div>
                    <div className="collaboration-label">Avg Response Time</div>
                  </div>
                  
                  <div className="collaboration-card">
                    <div className="collaboration-metric">
                      {analyticsData.userMetrics.collaborationMetrics.collaborationScore.toFixed(1)}%
                    </div>
                    <div className="collaboration-label">Collaboration Score</div>
                  </div>
                  
                  <div className="collaboration-card">
                    <div className="collaboration-metric">
                      {analyticsData.userMetrics.collaborationMetrics.meetingsPerWeek.toFixed(1)}
                    </div>
                    <div className="collaboration-label">Meetings per Week</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedDashboard === 'projects' && (
          <div className="projects-dashboard">
            <div className="dashboard-section">
              <div className="section-header">
                <h3>Project Insights</h3>
                <p className="section-description">
                  Track project progress, budgets, and milestone achievements
                </p>
              </div>

              <div className="projects-overview">
                {analyticsData.projectMetrics.projectProgress.map((project) => (
                  <div key={project.projectId} className="project-overview-card">
                    <div className="project-header">
                      <div className="project-title">
                        <h4>{project.name}</h4>
                        <span 
                          className="project-status-badge"
                          style={{ backgroundColor: getStatusColor(project.status) }}
                        >
                          {project.status.replace('-', ' ')}
                        </span>
                      </div>
                      <div className="project-progress-circle">
                        <div className="progress-text">{project.progress}%</div>
                      </div>
                    </div>
                    
                    <div className="project-details">
                      <div className="project-detail-item">
                        <span className="detail-label">Due Date:</span>
                        <span className="detail-value">
                          {new Date(project.dueDate).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <div className="project-detail-item">
                        <span className="detail-label">Budget:</span>
                        <span className="detail-value">
                          ${formatNumber(project.budget.spent)} / ${formatNumber(project.budget.allocated)}
                        </span>
                      </div>
                      
                      <div className="project-budget-bar">
                        <div 
                          className="budget-fill"
                          style={{ 
                            width: `${(project.budget.spent / project.budget.allocated) * 100}%`,
                            backgroundColor: project.budget.spent > project.budget.allocated * 0.8 ? '#ef4444' : '#10b981'
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="milestones-section">
                <h4>Milestone Tracking</h4>
                <div className="milestones-timeline">
                  {analyticsData.projectMetrics.milestoneTracking.map((milestone) => (
                    <div key={milestone.milestoneId} className="milestone-item">
                      <div className={`milestone-status ${milestone.status}`}>
                        {milestone.status === 'completed' ? (
                          <CheckCircle size={16} />
                        ) : (
                          <Clock size={16} />
                        )}
                      </div>
                      <div className="milestone-content">
                        <div className="milestone-name">{milestone.name}</div>
                        <div className="milestone-date">
                          {milestone.status === 'completed' 
                            ? `Completed: ${new Date(milestone.completedDate!).toLocaleDateString()}`
                            : `Target: ${new Date(milestone.targetDate!).toLocaleDateString()}`
                          }
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedDashboard === 'performance' && (
          <div className="performance-dashboard">
            <div className="dashboard-section">
              <div className="section-header">
                <h3>System Performance</h3>
                <p className="section-description">
                  Monitor system health, API performance, and error tracking
                </p>
              </div>

              <div className="performance-metrics-grid">
                <div className="perf-metric-card uptime">
                  <div className="perf-metric-icon">
                    <Activity size={24} />
                  </div>
                  <div className="perf-metric-value">
                    {analyticsData.performanceMetrics.systemMetrics.uptime}%
                  </div>
                  <div className="perf-metric-label">Uptime</div>
                  <div className="perf-metric-status good">Excellent</div>
                </div>

                <div className="perf-metric-card response-time">
                  <div className="perf-metric-icon">
                    <Clock size={24} />
                  </div>
                  <div className="perf-metric-value">
                    {analyticsData.performanceMetrics.systemMetrics.responseTime}ms
                  </div>
                  <div className="perf-metric-label">Avg Response Time</div>
                  <div className="perf-metric-status good">Good</div>
                </div>

                <div className="perf-metric-card throughput">
                  <div className="perf-metric-icon">
                    <TrendingUp size={24} />
                  </div>
                  <div className="perf-metric-value">
                    {formatNumber(analyticsData.performanceMetrics.systemMetrics.throughput)}
                  </div>
                  <div className="perf-metric-label">Requests/min</div>
                  <div className="perf-metric-status excellent">Excellent</div>
                </div>

                <div className="perf-metric-card error-rate">
                  <div className="perf-metric-icon">
                    <AlertTriangle size={24} />
                  </div>
                  <div className="perf-metric-value">
                    {analyticsData.performanceMetrics.systemMetrics.errorRate}%
                  </div>
                  <div className="perf-metric-label">Error Rate</div>
                  <div className="perf-metric-status excellent">Excellent</div>
                </div>
              </div>

              <div className="api-metrics-section">
                <h4>API Performance</h4>
                <div className="api-metrics-cards">
                  <div className="api-metric-item">
                    <div className="api-metric-label">Total Requests</div>
                    <div className="api-metric-value">
                      {formatNumber(analyticsData.performanceMetrics.apiMetrics.totalRequests)}
                    </div>
                    <div className="api-metric-change">+12.5% from yesterday</div>
                  </div>
                  
                  <div className="api-metric-item">
                    <div className="api-metric-label">Success Rate</div>
                    <div className="api-metric-value">
                      {analyticsData.performanceMetrics.apiMetrics.successRate}%
                    </div>
                    <div className="api-metric-change">-0.1% from yesterday</div>
                  </div>
                  
                  <div className="api-metric-item">
                    <div className="api-metric-label">Avg Response Time</div>
                    <div className="api-metric-value">
                      {analyticsData.performanceMetrics.apiMetrics.averageResponseTime}ms
                    </div>
                    <div className="api-metric-change">-15ms from yesterday</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;