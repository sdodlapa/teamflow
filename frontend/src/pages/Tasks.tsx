/**
 * Tasks Page Component
 * Comprehensive task management with CRUD operations, filtering, and real-time updates
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Filter, Search, ChevronDown, RefreshCw, Trash2, Edit } from 'lucide-react';
import Layout from '../components/Layout';
import { 
  taskApi, 
  Task, 
  TaskFilters, 
  TASK_STATUSES, 
  TASK_PRIORITIES,
  TaskCreate,
  TaskUpdate
} from '../services/taskApi';

// Task List Item Component
const TaskItem: React.FC<{
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => void;
  onStatusChange: (taskId: number, status: Task['status']) => void;
}> = ({ task, onEdit, onDelete, onStatusChange }) => {
  const statusConfig = TASK_STATUSES.find(s => s.value === task.status);
  const priorityConfig = TASK_PRIORITIES.find(p => p.value === task.priority);
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {/* Task Title & Description */}
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {task.title}
            </h3>
            <div className="flex gap-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusConfig?.color}`}>
                {statusConfig?.label}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityConfig?.color}`}>
                {priorityConfig?.label}
              </span>
            </div>
          </div>
          
          {task.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {task.description}
            </p>
          )}
          
          {/* Task Metadata */}
          <div className="flex flex-wrap gap-4 text-xs text-gray-500">
            {task.assignee_email && (
              <span>Assigned to: {task.assignee_email}</span>
            )}
            {task.due_date && (
              <span>Due: {formatDate(task.due_date)}</span>
            )}
            {task.estimated_hours && (
              <span>Estimated: {task.estimated_hours}h</span>
            )}
            {task.time_spent && (
              <span>Spent: {task.time_spent}h</span>
            )}
            <span>Created: {formatDate(task.created_at)}</span>
          </div>
          
          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex gap-2 mt-2">
              {task.tags.map((tag, index) => (
                <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-2 ml-4">
          {/* Status Dropdown */}
          <select
            value={task.status}
            onChange={(e) => onStatusChange(task.id, e.target.value as Task['status'])}
            className="text-xs px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {TASK_STATUSES.map(status => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
          
          <button
            onClick={() => onEdit(task)}
            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
            title="Edit Task"
          >
            <Edit size={16} />
          </button>
          
          <button
            onClick={() => onDelete(task.id)}
            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
            title="Delete Task"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

// Task Form Modal Component
const TaskFormModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void>;
  task?: Task;
  isLoading?: boolean;
}> = ({ isOpen, onClose, onSubmit, task, isLoading = false }) => {
  const [formData, setFormData] = useState<TaskCreate>({
    title: '',
    description: '',
    priority: 'medium',
    status: 'todo',
    assignee_email: '',
    due_date: '',
    estimated_hours: undefined,
    tags: []
  });

  const [tagsInput, setTagsInput] = useState('');

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || '',
        priority: task.priority,
        status: task.status,
        assignee_email: task.assignee_email || '',
        due_date: task.due_date ? task.due_date.split('T')[0] : '',
        estimated_hours: task.estimated_hours,
        tags: task.tags || []
      });
      setTagsInput(task.tags?.join(', ') || '');
    } else {
      setFormData({
        title: '',
        description: '',
        priority: 'medium',
        status: 'todo',
        assignee_email: '',
        due_date: '',
        estimated_hours: undefined,
        tags: []
      });
      setTagsInput('');
    }
  }, [task, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const tags = tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag);
    onSubmit({
      ...formData,
      tags: tags.length > 0 ? tags : undefined,
      estimated_hours: formData.estimated_hours || undefined
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-semibold mb-6">
          {task ? 'Edit Task' : 'Create New Task'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter task title"
            />
          </div>
          
          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter task description"
            />
          </div>
          
          {/* Priority and Status */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority *
              </label>
              <select
                required
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as Task['priority'] }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {TASK_PRIORITIES.map(priority => (
                  <option key={priority.value} value={priority.value}>
                    {priority.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Task['status'] }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {TASK_STATUSES.map(status => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Assignee and Due Date */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Assignee Email
              </label>
              <input
                type="email"
                value={formData.assignee_email}
                onChange={(e) => setFormData(prev => ({ ...prev, assignee_email: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="user@example.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Estimated Hours */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estimated Hours
            </label>
            <input
              type="number"
              min="0"
              step="0.5"
              value={formData.estimated_hours || ''}
              onChange={(e) => setFormData(prev => ({ 
                ...prev, 
                estimated_hours: e.target.value ? parseFloat(e.target.value) : undefined 
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0.0"
            />
          </div>
          
          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="frontend, urgent, bug"
            />
          </div>
          
          {/* Form Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Saving...' : task ? 'Update Task' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Main Tasks Page Component
const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // Modal state
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState<TaskFilters>({
    status: [],
    priority: [],
    assignee_email: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Load tasks
  const loadTasks = useCallback(async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      setError(null);
      
      const fetchedTasks = await taskApi.getTasks(filters);
      
      // Apply client-side search filter if needed
      let filteredTasks = fetchedTasks;
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        filteredTasks = fetchedTasks.filter(task =>
          task.title.toLowerCase().includes(query) ||
          task.description?.toLowerCase().includes(query) ||
          task.assignee_email?.toLowerCase().includes(query)
        );
      }
      
      setTasks(filteredTasks);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, searchQuery]);

  // Initial load
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  // Refresh tasks
  const handleRefresh = async () => {
    setRefreshing(true);
    await loadTasks(false);
    setRefreshing(false);
  };

  // Create task
  const handleCreateTask = async (taskData: TaskCreate) => {
    try {
      setFormLoading(true);
      const newTask = await taskApi.createTask(taskData);
      setTasks(prev => [newTask, ...prev]);
      setShowTaskForm(false);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    } finally {
      setFormLoading(false);
    }
  };

  // Update task
  const handleUpdateTask = async (taskData: TaskUpdate) => {
    if (!editingTask) return;
    
    try {
      setFormLoading(true);
      const updatedTask = await taskApi.updateTask(editingTask.id, taskData);
      setTasks(prev => prev.map(task => 
        task.id === editingTask.id ? updatedTask : task
      ));
      setShowTaskForm(false);
      setEditingTask(null);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to update task');
    } finally {
      setFormLoading(false);
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId: number) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await taskApi.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete task');
    }
  };

  // Update task status
  const handleStatusChange = async (taskId: number, status: Task['status']) => {
    try {
      const updatedTask = await taskApi.updateTaskStatus(taskId, status);
      setTasks(prev => prev.map(task => 
        task.id === taskId ? updatedTask : task
      ));
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to update task status');
    }
  };

  // Edit task
  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowTaskForm(true);
  };

  // Handle form submit (create or update)
  const handleFormSubmit = async (taskData: TaskCreate | TaskUpdate) => {
    if (editingTask) {
      await handleUpdateTask(taskData as TaskUpdate);
    } else {
      await handleCreateTask(taskData as TaskCreate);
    }
  };

  // Close modal
  const handleCloseModal = () => {
    setShowTaskForm(false);
    setEditingTask(null);
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
            <p className="text-gray-600 mt-1">
              Manage and track your team's tasks
            </p>
          </div>
          
          <button
            onClick={() => setShowTaskForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus size={20} />
            New Task
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              <Filter size={16} />
              Filters
              <ChevronDown size={16} className={`transform transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
          
          {/* Expandable Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <div className="space-y-2">
                  {TASK_STATUSES.map(status => (
                    <label key={status.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={filters.status?.includes(status.value) || false}
                        onChange={(e) => {
                          const statusList = filters.status || [];
                          if (e.target.checked) {
                            setFilters(prev => ({
                              ...prev,
                              status: [...statusList, status.value]
                            }));
                          } else {
                            setFilters(prev => ({
                              ...prev,
                              status: statusList.filter(s => s !== status.value)
                            }));
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">{status.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Priority Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                <div className="space-y-2">
                  {TASK_PRIORITIES.map(priority => (
                    <label key={priority.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={filters.priority?.includes(priority.value) || false}
                        onChange={(e) => {
                          const priorityList = filters.priority || [];
                          if (e.target.checked) {
                            setFilters(prev => ({
                              ...prev,
                              priority: [...priorityList, priority.value]
                            }));
                          } else {
                            setFilters(prev => ({
                              ...prev,
                              priority: priorityList.filter(p => p !== priority.value)
                            }));
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">{priority.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Assignee Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Assignee Email</label>
                <input
                  type="email"
                  placeholder="Filter by assignee..."
                  value={filters.assignee_email || ''}
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    assignee_email: e.target.value || undefined
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Task List */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <RefreshCw className="animate-spin text-blue-600" size={32} />
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Plus size={48} className="mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || filters.status?.length || filters.priority?.length || filters.assignee_email
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first task'
              }
            </p>
            {!searchQuery && !filters.status?.length && !filters.priority?.length && !filters.assignee_email && (
              <button
                onClick={() => setShowTaskForm(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Your First Task
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Task Count */}
            <div className="text-sm text-gray-600 mb-4">
              Showing {tasks.length} task{tasks.length !== 1 ? 's' : ''}
            </div>
            
            {/* Task Items */}
            {tasks.map(task => (
              <TaskItem
                key={task.id}
                task={task}
                onEdit={handleEditTask}
                onDelete={handleDeleteTask}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>
        )}

        {/* Task Form Modal */}
        <TaskFormModal
          isOpen={showTaskForm}
          onClose={handleCloseModal}
          onSubmit={handleFormSubmit}
          task={editingTask || undefined}
          isLoading={formLoading}
        />
      </div>
    </Layout>
  );
};

export default Tasks;