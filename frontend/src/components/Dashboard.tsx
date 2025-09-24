/**
 * Universal Dashboard Component - Template System Ready
 * Provides overview of any domain entities with real API integration
 */
import React, { useState, useEffect } from 'react';
import './Dashboard.css';

interface DashboardStats {
  totalEntities: number;
  completedEntities: number;
  inProgressEntities: number;
  overdueEntities: number;
  totalProjects: number;
  activeProjects: number;
  teamMembers: number;
  completionRate: number;
}

interface RecentActivity {
  id: number;
  type: 'entity_created' | 'entity_completed' | 'project_created' | 'user_joined';
  title: string;
  description: string;
  timestamp: string;
  user: string;
}

interface ProjectProgress {
  id: number;
  name: string;
  progress: number;
  entitiesCompleted: number;
  totalEntities: number;
  dueDate: string;
  status: 'on_track' | 'at_risk' | 'overdue';
}

interface DomainConfig {
  name: string;
  title: string;
  primaryEntity: string;
  secondaryEntity: string;
  logo: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalEntities: 0,
    completedEntities: 0,
    inProgressEntities: 0,
    overdueEntities: 0,
    totalProjects: 0,
    activeProjects: 0,
    teamMembers: 0,
    completionRate: 0
  });
  
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [projectProgress, setProjectProgress] = useState<ProjectProgress[]>([]);
  const [domainConfig, setDomainConfig] = useState<DomainConfig>({
    name: 'teamflow_original',
    title: 'TeamFlow',
    primaryEntity: 'Task',
    secondaryEntity: 'Project', 
    logo: '🚀'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load dashboard data from real API
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load domain configuration
      const domainResponse = await fetch('/api/v1/template/domain-config');
      if (domainResponse.ok) {
        const domainData = await domainResponse.json();
        setDomainConfig(domainData);
      }

      // Load dashboard statistics
      const statsResponse = await fetch('/api/v1/analytics/dashboard');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Load recent activity
      const activityResponse = await fetch('/api/v1/analytics/recent-activity?limit=10');
      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        setRecentActivity(activityData);
      }

      // Load project progress
      const progressResponse = await fetch('/api/v1/analytics/project-progress');
      if (progressResponse.ok) {
        const progressData = await progressResponse.json();
        setProjectProgress(progressData);
      }

    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
      console.error('Dashboard data loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'entity_completed': return '✅';
      case 'entity_created': return '📝';
      case 'project_created': return '📁';
      case 'user_joined': return '👤';
      default: return '📌';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_track': return 'status-success';
      case 'at_risk': return 'status-warning';
      case 'overdue': return 'status-danger';
      default: return 'status-default';
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p>Loading dashboard data...</p>
        </div>
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p className="error-message">{error}</p>
        </div>
        <button onClick={loadDashboardData} className="retry-button">
          Retry Loading
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{domainConfig.logo} {domainConfig.title} Dashboard</h1>
        <p>Welcome back! Here's what's happening with your {domainConfig.primaryEntity.toLowerCase()}s.</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>{stats.totalEntities}</h3>
            <p>Total {domainConfig.primaryEntity}s</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{stats.completedEntities}</h3>
            <p>Completed</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🔄</div>
          <div className="stat-content">
            <h3>{stats.inProgressEntities}</h3>
            <p>In Progress</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>{stats.overdueEntities}</h3>
            <p>Overdue</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <h3>{stats.totalProjects}</h3>
            <p>Total {domainConfig.secondaryEntity}s</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{stats.teamMembers}</h3>
            <p>Team Members</p>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Project Progress */}
        <div className="dashboard-section">
          <h2>{domainConfig.secondaryEntity} Progress</h2>
          <div className="projects-list">
            {projectProgress.length === 0 ? (
              <p className="no-data">No {domainConfig.secondaryEntity.toLowerCase()}s found. <button onClick={loadDashboardData}>Refresh</button></p>
            ) : (
              projectProgress.map(project => (
                <div key={project.id} className="project-card">
                  <div className="project-header">
                    <h3>{project.name}</h3>
                    <span className={`project-status ${getStatusColor(project.status)}`}>
                      {project.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${project.progress}%` }}
                    ></div>
                    <span className="progress-text">{project.progress}%</span>
                  </div>
                  <div className="project-details">
                    <span>{project.entitiesCompleted}/{project.totalEntities} {domainConfig.primaryEntity.toLowerCase()}s</span>
                    <span>Due: {new Date(project.dueDate).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-section">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            {recentActivity.length === 0 ? (
              <p className="no-data">No recent activity. <button onClick={loadDashboardData}>Refresh</button></p>
            ) : (
              recentActivity.map(activity => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-icon">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="activity-content">
                    <h4>{activity.title}</h4>
                    <p>{activity.description}</p>
                    <div className="activity-meta">
                      <span className="activity-user">{activity.user}</span>
                      <span className="activity-time">{activity.timestamp}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Performance Chart */}
        <div className="dashboard-section">
          <h2>Performance Overview</h2>
          <div className="performance-chart">
            <div className="chart-container">
              <div className="completion-rate">
                <div className="rate-circle">
                  <div className="rate-value">{stats.completionRate}%</div>
                  <div className="rate-label">Completion Rate</div>
                </div>
              </div>
              <div className="performance-stats">
                <div className="perf-stat">
                  <span className="perf-label">{domainConfig.primaryEntity}s Completed This Week</span>
                  <span className="perf-value">{stats.completedEntities}</span>
                </div>
                <div className="perf-stat">
                  <span className="perf-label">Active {domainConfig.secondaryEntity}s</span>
                  <span className="perf-value">{stats.activeProjects}</span>
                </div>
                <div className="perf-stat">
                  <span className="perf-label">Team Members</span>
                  <span className="perf-value">{stats.teamMembers}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dashboard-section">
          <h2>Quick Actions</h2>
          <div className="quick-actions">
            <button className="action-btn">
              <span className="action-icon">➕</span>
              Create {domainConfig.primaryEntity}
            </button>
            <button className="action-btn">
              <span className="action-icon">📁</span>
              New {domainConfig.secondaryEntity}
            </button>
            <button className="action-btn">
              <span className="action-icon">👥</span>
              Invite Member
            </button>
            <button className="action-btn">
              <span className="action-icon">📊</span>
              View Reports
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;