/**
 * Main Dashboard Component
 * Provides overview of tasks, projects, and team performance
 */
import React, { useState, useEffect } from 'react';
import './Dashboard.css';

interface DashboardStats {
  totalTasks: number;
  completedTasks: number;
  inProgressTasks: number;
  overdueTasks: number;
  totalProjects: number;
  activeProjects: number;
  teamMembers: number;
  completionRate: number;
}

interface RecentActivity {
  id: number;
  type: 'task_created' | 'task_completed' | 'project_created' | 'user_joined';
  title: string;
  description: string;
  timestamp: string;
  user: string;
}

interface ProjectProgress {
  id: number;
  name: string;
  progress: number;
  tasksCompleted: number;
  totalTasks: number;
  dueDate: string;
  status: 'on_track' | 'at_risk' | 'overdue';
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalTasks: 0,
    completedTasks: 0,
    inProgressTasks: 0,
    overdueTasks: 0,
    totalProjects: 0,
    activeProjects: 0,
    teamMembers: 0,
    completionRate: 0
  });
  
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [projectProgress, setProjectProgress] = useState<ProjectProgress[]>([]);

  // Mock data for development
  useEffect(() => {
    const mockStats: DashboardStats = {
      totalTasks: 127,
      completedTasks: 89,
      inProgressTasks: 24,
      overdueTasks: 8,
      totalProjects: 12,
      activeProjects: 8,
      teamMembers: 15,
      completionRate: 70
    };

    const mockActivity: RecentActivity[] = [
      {
        id: 1,
        type: 'task_completed',
        title: 'User Authentication',
        description: 'Completed JWT implementation',
        timestamp: '2 hours ago',
        user: 'John Doe'
      },
      {
        id: 2,
        type: 'project_created',
        title: 'Mobile App Development',
        description: 'New project created for iOS/Android app',
        timestamp: '4 hours ago',
        user: 'Jane Smith'
      },
      {
        id: 3,
        type: 'task_created',
        title: 'Database Optimization',
        description: 'New task for improving query performance',
        timestamp: '6 hours ago',
        user: 'Bob Johnson'
      },
      {
        id: 4,
        type: 'user_joined',
        title: 'New Team Member',
        description: 'Alice Wilson joined the development team',
        timestamp: '1 day ago',
        user: 'System'
      }
    ];

    const mockProjects: ProjectProgress[] = [
      {
        id: 1,
        name: 'TeamFlow Backend',
        progress: 85,
        tasksCompleted: 34,
        totalTasks: 40,
        dueDate: '2025-10-15',
        status: 'on_track'
      },
      {
        id: 2,
        name: 'Frontend Dashboard',
        progress: 60,
        tasksCompleted: 18,
        totalTasks: 30,
        dueDate: '2025-10-20',
        status: 'at_risk'
      },
      {
        id: 3,
        name: 'Mobile App',
        progress: 25,
        tasksCompleted: 5,
        totalTasks: 20,
        dueDate: '2025-09-30',
        status: 'overdue'
      },
      {
        id: 4,
        name: 'API Documentation',
        progress: 90,
        tasksCompleted: 18,
        totalTasks: 20,
        dueDate: '2025-10-10',
        status: 'on_track'
      }
    ];

    setStats(mockStats);
    setRecentActivity(mockActivity);
    setProjectProgress(mockProjects);
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'task_completed': return '✅';
      case 'task_created': return '📝';
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

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome back! Here's what's happening with your projects.</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>{stats.totalTasks}</h3>
            <p>Total Tasks</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{stats.completedTasks}</h3>
            <p>Completed</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🔄</div>
          <div className="stat-content">
            <h3>{stats.inProgressTasks}</h3>
            <p>In Progress</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>{stats.overdueTasks}</h3>
            <p>Overdue</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <h3>{stats.activeProjects}</h3>
            <p>Active Projects</p>
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

      {/* Main Content Grid */}
      <div className="dashboard-content">
        {/* Project Progress */}
        <div className="dashboard-section">
          <h2>Project Progress</h2>
          <div className="project-list">
            {projectProgress.map(project => (
              <div key={project.id} className="project-item">
                <div className="project-header">
                  <h4>{project.name}</h4>
                  <span className={`status-badge ${getStatusColor(project.status)}`}>
                    {project.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="project-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                  <span className="progress-text">{project.progress}%</span>
                </div>
                <div className="project-details">
                  <span>{project.tasksCompleted}/{project.totalTasks} tasks</span>
                  <span>Due: {new Date(project.dueDate).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-section">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            {recentActivity.map(activity => (
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
            ))}
          </div>
        </div>

        {/* Performance Chart */}
        <div className="dashboard-section">
          <h2>Team Performance</h2>
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
                  <span className="perf-label">Tasks Completed This Week</span>
                  <span className="perf-value">23</span>
                </div>
                <div className="perf-stat">
                  <span className="perf-label">Average Time per Task</span>
                  <span className="perf-value">4.2h</span>
                </div>
                <div className="perf-stat">
                  <span className="perf-label">Team Velocity</span>
                  <span className="perf-value">+12%</span>
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
              Create Task
            </button>
            <button className="action-btn">
              <span className="action-icon">📁</span>
              New Project
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