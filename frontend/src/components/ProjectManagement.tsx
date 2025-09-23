/**
 * Project Management Component
 * Handles project creation, management, and overview
 */
import React, { useState, useEffect } from 'react';
import './ProjectManagement.css';

interface Project {
  id: number;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  startDate: string;
  endDate?: string;
  progress: number;
  teamMembers: Array<{
    id: number;
    name: string;
    role: string;
    avatar?: string;
  }>;
  tasksTotal: number;
  tasksCompleted: number;
  budget?: number;
  spent?: number;
}

const ProjectManagement: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);

  // Mock data
  useEffect(() => {
    const mockProjects: Project[] = [
      {
        id: 1,
        name: 'TeamFlow Backend API',
        description: 'Develop comprehensive REST API for task management platform',
        status: 'active',
        priority: 'high',
        startDate: '2025-09-01',
        endDate: '2025-10-15',
        progress: 75,
        teamMembers: [
          { id: 1, name: 'John Doe', role: 'Lead Developer' },
          { id: 2, name: 'Jane Smith', role: 'Backend Developer' },
          { id: 3, name: 'Bob Johnson', role: 'DevOps Engineer' }
        ],
        tasksTotal: 45,
        tasksCompleted: 34,
        budget: 50000,
        spent: 37500
      },
      {
        id: 2,
        name: 'Frontend Dashboard',
        description: 'Build responsive React dashboard with modern UI/UX',
        status: 'active',
        priority: 'medium',
        startDate: '2025-09-15',
        endDate: '2025-11-01',
        progress: 45,
        teamMembers: [
          { id: 4, name: 'Alice Wilson', role: 'Frontend Developer' },
          { id: 5, name: 'Charlie Brown', role: 'UI/UX Designer' }
        ],
        tasksTotal: 32,
        tasksCompleted: 14,
        budget: 35000,
        spent: 15750
      },
      {
        id: 3,
        name: 'Mobile Application',
        description: 'Cross-platform mobile app for iOS and Android',
        status: 'planning',
        priority: 'medium',
        startDate: '2025-10-01',
        endDate: '2025-12-15',
        progress: 10,
        teamMembers: [
          { id: 6, name: 'David Lee', role: 'Mobile Developer' },
          { id: 7, name: 'Emma Davis', role: 'QA Engineer' }
        ],
        tasksTotal: 28,
        tasksCompleted: 3,
        budget: 45000,
        spent: 4500
      },
      {
        id: 4,
        name: 'Security Audit',
        description: 'Comprehensive security assessment and penetration testing',
        status: 'completed',
        priority: 'urgent',
        startDate: '2025-08-01',
        endDate: '2025-08-31',
        progress: 100,
        teamMembers: [
          { id: 8, name: 'Frank Wilson', role: 'Security Specialist' }
        ],
        tasksTotal: 15,
        tasksCompleted: 15,
        budget: 20000,
        spent: 19000
      }
    ];
    setProjects(mockProjects);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'status-active';
      case 'completed': return 'status-completed';
      case 'planning': return 'status-planning';
      case 'on_hold': return 'status-hold';
      case 'cancelled': return 'status-cancelled';
      default: return 'status-default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'priority-urgent';
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return 'priority-default';
    }
  };

  const filteredProjects = projects.filter(project => {
    const matchesStatus = !statusFilter || project.status === statusFilter;
    const matchesSearch = !searchTerm || 
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const ProjectCard: React.FC<{ project: Project }> = ({ project }) => (
    <div className="project-card">
      <div className="project-header">
        <h3>{project.name}</h3>
        <div className="project-badges">
          <span className={`status-badge ${getStatusColor(project.status)}`}>
            {project.status.replace('_', ' ')}
          </span>
          <span className={`priority-badge ${getPriorityColor(project.priority)}`}>
            {project.priority}
          </span>
        </div>
      </div>
      
      <p className="project-description">{project.description}</p>
      
      <div className="project-progress">
        <div className="progress-header">
          <span>Progress</span>
          <span>{project.progress}%</span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${project.progress}%` }}
          />
        </div>
      </div>

      <div className="project-stats">
        <div className="stat">
          <span className="stat-label">Tasks</span>
          <span className="stat-value">{project.tasksCompleted}/{project.tasksTotal}</span>
        </div>
        {project.budget && (
          <div className="stat">
            <span className="stat-label">Budget</span>
            <span className="stat-value">
              ${(project.spent || 0).toLocaleString()}/${project.budget.toLocaleString()}
            </span>
          </div>
        )}
      </div>

      <div className="project-team">
        <span className="team-label">Team:</span>
        <div className="team-avatars">
          {project.teamMembers.slice(0, 3).map(member => (
            <div key={member.id} className="team-avatar" title={member.name}>
              {member.name.charAt(0)}
            </div>
          ))}
          {project.teamMembers.length > 3 && (
            <div className="team-avatar team-more">
              +{project.teamMembers.length - 3}
            </div>
          )}
        </div>
      </div>

      <div className="project-dates">
        <span>📅 {new Date(project.startDate).toLocaleDateString()}</span>
        {project.endDate && (
          <span>→ {new Date(project.endDate).toLocaleDateString()}</span>
        )}
      </div>
    </div>
  );

  return (
    <div className="project-management">
      <div className="header">
        <h1>Projects</h1>
        <button 
          className="btn-primary"
          onClick={() => setCreateModalOpen(true)}
        >
          + New Project
        </button>
      </div>

      {/* Filters */}
      <div className="filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">All Statuses</option>
          <option value="planning">Planning</option>
          <option value="active">Active</option>
          <option value="on_hold">On Hold</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>

        <div className="view-toggle">
          <button
            className={`view-btn ${view === 'grid' ? 'active' : ''}`}
            onClick={() => setView('grid')}
          >
            ⊞ Grid
          </button>
          <button
            className={`view-btn ${view === 'list' ? 'active' : ''}`}
            onClick={() => setView('list')}
          >
            ☰ List
          </button>
        </div>
      </div>

      {/* Project Display */}
      <div className={`projects-container ${view}`}>
        {filteredProjects.map(project => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <div className="empty-state">
          <h3>No projects found</h3>
          <p>Try adjusting your search criteria or create a new project.</p>
        </div>
      )}

      {/* Create Project Modal */}
      {createModalOpen && (
        <div className="modal-overlay" onClick={() => setCreateModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Project</h2>
              <button 
                className="modal-close"
                onClick={() => setCreateModalOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Project Name</label>
                <input type="text" className="form-input" placeholder="Enter project name" />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea className="form-textarea" rows={3} placeholder="Project description" />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Priority</label>
                  <select className="form-select">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <select className="form-select">
                    <option value="planning">Planning</option>
                    <option value="active">Active</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Start Date</label>
                  <input type="date" className="form-input" />
                </div>
                <div className="form-group">
                  <label>End Date</label>
                  <input type="date" className="form-input" />
                </div>
              </div>
              <div className="form-group">
                <label>Budget</label>
                <input type="number" className="form-input" placeholder="Project budget" />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn-secondary"
                onClick={() => setCreateModalOpen(false)}
              >
                Cancel
              </button>
              <button 
                className="btn-primary"
                onClick={() => setCreateModalOpen(false)}
              >
                Create Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectManagement;