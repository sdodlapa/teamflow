/**
 * Enhanced Tasks Page with Error Handling & Loading States
 * Demonstrates comprehensive error handling, loading states, and user feedback
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Search, RefreshCw, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import { ErrorDisplay } from '../components/ErrorComponents';
import { LoadingSpinner, LoadingSkeleton, LoadingButton } from '../components/LoadingComponents';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { useToast } from '../contexts/ToastContext';
import { ApiError } from '../utils/apiClient';

// Mock Task interface (replace with actual API types)
interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee_email?: string;
  due_date?: string;
  created_at: string;
  updated_at: string;
}

interface TaskCreate {
  title: string;
  description?: string;
  priority: Task['priority'];
  status?: Task['status'];
  assignee_email?: string;
  due_date?: string;
}

// Enhanced Task Card with error states
const TaskCard: React.FC<{
  task: Task;
  onUpdate: (task: Task) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}> = ({ task, onUpdate, onDelete }) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const toast = useToast();

  const handleStatusChange = async (newStatus: Task['status']) => {
    try {
      setIsUpdating(true);
      const updatedTask = { ...task, status: newStatus };
      await onUpdate(updatedTask);
      toast.success(`Task status updated to ${newStatus}`);
    } catch (error) {
      toast.error('Failed to update task status');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${task.title}"?`)) return;
    
    try {
      setIsDeleting(true);
      await onDelete(task.id);
      toast.success('Task deleted successfully');
    } catch (error) {
      toast.error('Failed to delete task');
      setIsDeleting(false);
    }
  };



  const priorityColors = {
    low: 'bg-gray-100 text-gray-700',
    medium: 'bg-yellow-100 text-yellow-700',
    high: 'bg-orange-100 text-orange-700',
    critical: 'bg-red-100 text-red-700',
  };

  return (
    <div className={`bg-white border rounded-lg p-4 shadow-sm transition-all ${
      isDeleting ? 'opacity-50 pointer-events-none' : 'hover:shadow-md'
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {task.title}
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityColors[task.priority]}`}>
              {task.priority}
            </span>
          </div>
          
          {task.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {task.description}
            </p>
          )}
          
          <div className="flex items-center gap-4 text-xs text-gray-500">
            {task.assignee_email && <span>👤 {task.assignee_email}</span>}
            {task.due_date && <span>📅 {new Date(task.due_date).toLocaleDateString()}</span>}
            <span>🕒 {new Date(task.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-4">
          <select
            value={task.status}
            onChange={(e) => handleStatusChange(e.target.value as Task['status'])}
            disabled={isUpdating}
            className="text-xs px-2 py-1 border rounded focus:ring-2 focus:ring-blue-500"
          >
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          
          {isUpdating && <LoadingSpinner size="sm" />}
          
          <LoadingButton
            onClick={handleDelete}
            isLoading={isDeleting}
            loadingText="Deleting..."
            className="px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded border border-red-200"
          >
            Delete
          </LoadingButton>
        </div>
      </div>
    </div>
  );
};

// Create Task Form with validation
const CreateTaskForm: React.FC<{
  onSubmit: (task: TaskCreate) => Promise<void>;
  onCancel: () => void;
}> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<TaskCreate>({
    title: '',
    description: '',
    priority: 'medium',
    status: 'todo',
    assignee_email: '',
    due_date: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { loading, executeWithLoading } = useErrorHandler();

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (formData.assignee_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.assignee_email)) {
      newErrors.assignee_email = 'Please enter a valid email address';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    const result = await executeWithLoading(async () => {
      return onSubmit({
        ...formData,
        description: formData.description || undefined,
        assignee_email: formData.assignee_email || undefined,
        due_date: formData.due_date || undefined,
      });
    });

    if (result !== null) {
      onCancel(); // Close form on success
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg">
        <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className={`w-full px-3 py-2 border rounded-md ${
                errors.title ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
              }`}
              placeholder="Enter task title"
            />
            {errors.title && (
              <div className="flex items-center mt-1 text-sm text-red-600">
                <AlertCircle size={14} className="mr-1" />
                {errors.title}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500"
              placeholder="Enter task description (optional)"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Priority</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as Task['priority'] }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Task['status'] }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Assignee Email</label>
            <input
              type="email"
              value={formData.assignee_email}
              onChange={(e) => setFormData(prev => ({ ...prev, assignee_email: e.target.value }))}
              className={`w-full px-3 py-2 border rounded-md ${
                errors.assignee_email ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
              }`}
              placeholder="user@example.com (optional)"
            />
            {errors.assignee_email && (
              <div className="flex items-center mt-1 text-sm text-red-600">
                <AlertCircle size={14} className="mr-1" />
                {errors.assignee_email}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Due Date</label>
            <input
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading && <LoadingSpinner size="sm" className="mr-2" />}
              {loading ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Main Tasks Component
const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { loading, error, executeWithLoading, clearError } = useErrorHandler();
  const toast = useToast();

  // Mock API functions (replace with actual API calls)
  const mockApi = {
    getTasks: async (): Promise<Task[]> => {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simulate occasional errors for demonstration
      if (Math.random() < 0.1) {
        throw new Error('Network connection failed');
      }
      
      return [
        {
          id: 1,
          title: 'Implement user authentication',
          description: 'Add login and registration functionality',
          status: 'in_progress' as const,
          priority: 'high' as const,
          assignee_email: 'john@example.com',
          due_date: '2024-01-15',
          created_at: '2024-01-01T10:00:00Z',
          updated_at: '2024-01-05T10:00:00Z',
        },
        {
          id: 2,
          title: 'Design database schema',
          description: 'Create efficient database structure for the application',
          status: 'completed' as const,
          priority: 'medium' as const,
          assignee_email: 'sarah@example.com',
          due_date: '2024-01-10',
          created_at: '2024-01-01T11:00:00Z',
          updated_at: '2024-01-08T15:30:00Z',
        },
        {
          id: 3,
          title: 'Fix responsive layout issues',
          description: 'Address mobile layout problems on task cards',
          status: 'todo' as const,
          priority: 'critical' as const,
          due_date: '2024-01-20',
          created_at: '2024-01-02T09:00:00Z',
          updated_at: '2024-01-02T09:00:00Z',
        },
      ];
    },

    createTask: async (task: TaskCreate): Promise<Task> => {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (Math.random() < 0.15) {
        const error = new Error('Validation failed') as ApiError;
        error.status = 422;
        error.response = {
          status: 422,
          statusText: 'Unprocessable Entity',
          data: { message: 'Task title already exists' },
        };
        throw error;
      }
      
      return {
        ...task,
        id: Date.now(),
        status: task.status || 'todo',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    },

    updateTask: async (id: number, updates: Partial<Task>): Promise<Task> => {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      if (Math.random() < 0.1) {
        throw new Error('Server error occurred');
      }
      
      return { ...updates, id, updated_at: new Date().toISOString() } as Task;
    },

    deleteTask: async (_id: number): Promise<void> => {
      await new Promise(resolve => setTimeout(resolve, 600));
      
      if (Math.random() < 0.1) {
        const error = new Error('Task not found') as ApiError;
        error.status = 404;
        throw error;
      }
    },
  };

  // Load tasks
  const loadTasks = useCallback(async () => {
    const result = await executeWithLoading(async () => {
      const fetchedTasks = await mockApi.getTasks();
      return fetchedTasks;
    });

    if (result) {
      setTasks(result);
    }
  }, [executeWithLoading]);

  // Create task
  const createTask = async (taskData: TaskCreate) => {
    const newTask = await mockApi.createTask(taskData);
    setTasks(prev => [newTask, ...prev]);
    toast.success('Task created successfully!');
  };

  // Update task
  const updateTask = async (updatedTask: Task) => {
    const result = await mockApi.updateTask(updatedTask.id, updatedTask);
    setTasks(prev => prev.map(task => 
      task.id === updatedTask.id ? result : task
    ));
  };

  // Delete task
  const deleteTask = async (id: number) => {
    await mockApi.deleteTask(id);
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  // Filter tasks by search query
  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (task.description?.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (task.assignee_email?.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Load tasks on component mount
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
            <p className="text-gray-600 mt-1">
              Manage your tasks with comprehensive error handling
            </p>
          </div>
          
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus size={20} />
            New Task
          </button>
        </div>

        {/* Search and Actions */}
        <div className="bg-white border rounded-lg p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <LoadingButton
              onClick={loadTasks}
              isLoading={loading}
              loadingText="Refreshing..."
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <RefreshCw size={16} />
              Refresh
            </LoadingButton>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <ErrorDisplay
            type={error.type}
            message={error.message}
            details={error.details}
            onRetry={() => {
              clearError();
              loadTasks();
            }}
            onDismiss={clearError}
            className="mb-6"
          />
        )}

        {/* Content */}
        {loading && tasks.length === 0 ? (
          <LoadingSkeleton rows={5} className="space-y-4" />
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Plus size={48} className="mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery 
                ? `No tasks match "${searchQuery}"`
                : 'Get started by creating your first task'
              }
            </p>
            {!searchQuery && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Your First Task
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-sm text-gray-600">
              Showing {filteredTasks.length} of {tasks.length} tasks
            </div>
            
            {filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onUpdate={updateTask}
                onDelete={deleteTask}
              />
            ))}
          </div>
        )}

        {/* Create Task Form */}
        {showCreateForm && (
          <CreateTaskForm
            onSubmit={createTask}
            onCancel={() => setShowCreateForm(false)}
          />
        )}
      </div>
    </Layout>
  );
};

export default Tasks;