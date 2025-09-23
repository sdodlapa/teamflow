import React from 'react';
import './AdminDashboard.css';

interface AdminDashboardProps {
  userRole: string;
}

// Simplified Admin Dashboard without external UI library dependencies
const AdminDashboard: React.FC<AdminDashboardProps> = () => {
  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p>System overview and management</p>
      </div>
      
      <div className="admin-grid">
        <div className="admin-card">
          <h3>System Health</h3>
          <div className="health-score">98%</div>
          <p>All systems operational</p>
        </div>
        
        <div className="admin-card">
          <h3>Active Users</h3>
          <div className="metric">1,247</div>
          <p>+12% from last week</p>
        </div>
        
        <div className="admin-card">
          <h3>Total Projects</h3>
          <div className="metric">89</div>
          <p>15 active this week</p>
        </div>
        
        <div className="admin-card">
          <h3>Completed Tasks</h3>
          <div className="metric">3,456</div>
          <p>+8% completion rate</p>
        </div>
      </div>

      <div className="admin-section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          <div className="activity-item">
            <span className="activity-type">Project Created</span>
            <span className="activity-description">New project "Website Redesign" created</span>
            <span className="activity-time">2 hours ago</span>
          </div>
          <div className="activity-item">
            <span className="activity-type">User Registered</span>
            <span className="activity-description">john.doe@company.com joined</span>
            <span className="activity-time">4 hours ago</span>
          </div>
          <div className="activity-item">
            <span className="activity-type">Task Completed</span>
            <span className="activity-description">Database optimization completed</span>
            <span className="activity-time">6 hours ago</span>
          </div>
        </div>
      </div>

      <div className="admin-section">
        <h2>System Configuration</h2>
        <div className="config-grid">
          <button className="config-btn">User Management</button>
          <button className="config-btn">System Settings</button>
          <button className="config-btn">Backup & Restore</button>
          <button className="config-btn">Security Audit</button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;