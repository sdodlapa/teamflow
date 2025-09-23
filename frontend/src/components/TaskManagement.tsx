/**
 * Main Task Management Component
 * Provides comprehensive task management interface with multiple views
 */
import React, { useState, useEffect } from 'react';
import './TaskManagement.css';

interface Task {
  id: number;
  title: string;
  description: string;
  status: 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE' | 'CANCELLED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  assignee?: {
    id: number;
    name: string;
    avatar?: string;
  };
  dueDate?: string;
  project: {
    id: number;
    name: string;
  };
  estimatedHours?: number;
  actualHours?: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

const TaskManagement: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [view, setView] = useState<'kanban' | 'list' | 'calendar'>('kanban');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data for development
  useEffect(() => {
    const mockTasks: Task[] = [
      {
        id: 1,
        title: 'Implement user authentication',
        description: 'Set up JWT authentication with login/logout functionality',
        status: 'IN_PROGRESS',
        priority: 'HIGH',
        assignee: { id: 1, name: 'John Doe' },
        dueDate: '2025-09-30',
        project: { id: 1, name: 'TeamFlow Backend' },
        estimatedHours: 8,
        actualHours: 5,
        tags: ['authentication', 'security'],
        createdAt: '2025-09-20T10:00:00Z',
        updatedAt: '2025-09-23T14:30:00Z'
      },
      {
        id: 2,
        title: 'Design task dashboard',
        description: 'Create responsive dashboard for task overview',
        status: 'TODO',
        priority: 'MEDIUM',
        assignee: { id: 2, name: 'Jane Smith' },
        dueDate: '2025-10-05',
        project: { id: 2, name: 'TeamFlow Frontend' },
        estimatedHours: 12,
        tags: ['ui', 'dashboard'],
        createdAt: '2025-09-21T09:00:00Z',
        updatedAt: '2025-09-21T09:00:00Z'
      },
      {
        id: 3,
        title: 'Database optimization',
        description: 'Optimize slow queries and add proper indexing',
        status: 'DONE',
        priority: 'HIGH',
        assignee: { id: 3, name: 'Bob Johnson' },
        project: { id: 1, name: 'TeamFlow Backend' },
        estimatedHours: 6,
        actualHours: 7,
        tags: ['database', 'performance'],
        createdAt: '2025-09-19T11:00:00Z',
        updatedAt: '2025-09-22T16:00:00Z'
      }
    ];
    setTasks(mockTasks);
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'URGENT': return 'priority-urgent';
      case 'HIGH': return 'priority-high';
      case 'MEDIUM': return 'priority-medium';
      case 'LOW': return 'priority-low';
      default: return 'priority-default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DONE': return 'status-done';
      case 'IN_PROGRESS': return 'status-progress';
      case 'IN_REVIEW': return 'status-review';
      case 'CANCELLED': return 'status-cancelled';
      default: return 'status-default';
    }
  };

  const KanbanView: React.FC = () => {
    const columns = ['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE'];
    
    return (
      <div className="kanban-container">
        {columns.map(status => (
          <div className="kanban-column" key={status}>
            <div className="kanban-header">
              <h3>{status.replace('_', ' ')}</h3>
              <span className="task-count">
                {tasks.filter(t => t.status === status).length}
              </span>
            </div>
            <div className="kanban-tasks">
              {tasks.filter(task => task.status === status).map(task => (
                <div key={task.id} className="task-card">
                  <h4>{task.title}</h4>
                  <div className="task-meta">
                    <span className={`priority-badge ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                    {task.assignee && (
                      <div className="assignee">
                        <div className="avatar">
                          {task.assignee.name.charAt(0)}
                        </div>
                        <span>{task.assignee.name}</span>
                      </div>
                    )}
                  </div>
                  <div className="task-tags">
                    {task.tags.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const ListView: React.FC = () => (
    <div className="list-container">
      <div className="task-list">
        {tasks.map(task => (
          <div key={task.id} className="task-list-item">
            <div className="task-info">
              <h4>{task.title}</h4>
              <p>{task.description}</p>
              <div className="task-details">
                <span>Project: {task.project.name}</span>
                {task.assignee && <span>Assignee: {task.assignee.name}</span>}
                {task.dueDate && (
                  <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                )}
              </div>
            </div>
            <div className="task-badges">
              <span className={`status-badge ${getStatusColor(task.status)}`}>
                {task.status}
              </span>
              <span className={`priority-badge ${getPriorityColor(task.priority)}`}>
                {task.priority}
              </span>
            </div>
            <div className="task-actions">
              <button className="btn-action btn-start">▶</button>
              <button className="btn-action btn-complete">✓</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="task-management">
      <div className="header">
        <h1>Task Management</h1>
        <button 
          className="btn-primary"
          onClick={() => setCreateDialogOpen(true)}
        >
          + Create Task
        </button>
      </div>

      {/* Filters and Search */}
      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-controls">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Statuses</option>
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="IN_REVIEW">In Review</option>
            <option value="DONE">Done</option>
          </select>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Priorities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="URGENT">Urgent</option>
          </select>
        </div>
      </div>

      {/* View Selector */}
      <div className="view-selector">
        <button 
          className={`view-tab ${view === 'kanban' ? 'active' : ''}`}
          onClick={() => setView('kanban')}
        >
          📋 Kanban
        </button>
        <button 
          className={`view-tab ${view === 'list' ? 'active' : ''}`}
          onClick={() => setView('list')}
        >
          📄 List
        </button>
        <button 
          className={`view-tab ${view === 'calendar' ? 'active' : ''}`}
          onClick={() => setView('calendar')}
        >
          📅 Calendar
        </button>
      </div>

      {/* Task Views */}
      {view === 'kanban' && <KanbanView />}
      {view === 'list' && <ListView />}
      {view === 'calendar' && (
        <div className="calendar-placeholder">
          <h3>Calendar view coming soon...</h3>
        </div>
      )}

      {/* Create Task Dialog */}
      {createDialogOpen && (
        <div className="modal-overlay" onClick={() => setCreateDialogOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Task</h2>
              <button 
                className="modal-close"
                onClick={() => setCreateDialogOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="title">Task Title</label>
                <input
                  id="title"
                  type="text"
                  className="form-input"
                  placeholder="Enter task title"
                />
              </div>
              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  className="form-textarea"
                  rows={3}
                  placeholder="Enter task description"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="priority">Priority</label>
                  <select id="priority" className="form-select">
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="dueDate">Due Date</label>
                  <input
                    id="dueDate"
                    type="date"
                    className="form-input"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="estimatedHours">Estimated Hours</label>
                  <input
                    id="estimatedHours"
                    type="number"
                    className="form-input"
                    min="0"
                    step="0.5"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="tags">Tags</label>
                  <input
                    id="tags"
                    type="text"
                    className="form-input"
                    placeholder="frontend, bug, urgent"
                  />
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn-secondary"
                onClick={() => setCreateDialogOpen(false)}
              >
                Cancel
              </button>
              <button 
                className="btn-primary"
                onClick={() => setCreateDialogOpen(false)}
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskManagement;