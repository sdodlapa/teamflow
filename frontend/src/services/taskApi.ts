/**
 * Task API Service
 * Handles all task-related API operations for TeamFlow
 */

import { apiClient } from './apiClient';

// Task interfaces aligned with backend schemas
export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'in_review' | 'done' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee_id?: number;
  assignee_email?: string;
  due_date?: string;
  tags?: string[];
  estimated_hours?: number;
  time_spent?: number;
  project_id?: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  created_by_id: number;
  updated_by_id?: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'in_review' | 'done' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee_email?: string;
  due_date?: string;
  tags?: string[];
  estimated_hours?: number;
  project_id?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'in_review' | 'done' | 'cancelled';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  assignee_email?: string;
  due_date?: string;
  tags?: string[];
  estimated_hours?: number;
  time_spent?: number;
  project_id?: number;
}

export interface TaskFilters {
  status?: string[];
  priority?: string[];
  assignee_email?: string;
  project_id?: number;
  skip?: number;
  limit?: number;
}

// Status and priority options for UI dropdowns
export const TASK_STATUSES = [
  { value: 'todo', label: 'To Do', color: 'bg-gray-100 text-gray-800' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-blue-100 text-blue-800' },
  { value: 'in_review', label: 'In Review', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'done', label: 'Done', color: 'bg-green-100 text-green-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' },
];

export const TASK_PRIORITIES = [
  { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800' },
  { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-800' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-100 text-red-800' },
];

class TaskApiService {
  /**
   * Get all tasks with optional filtering
   */
  async getTasks(filters: TaskFilters = {}): Promise<Task[]> {
    try {
      const params = new URLSearchParams();
      
      if (filters.status?.length) {
        filters.status.forEach(status => params.append('status', status));
      }
      if (filters.priority?.length) {
        filters.priority.forEach(priority => params.append('priority', priority));
      }
      if (filters.assignee_email) {
        params.append('assignee_email', filters.assignee_email);
      }
      if (filters.project_id) {
        params.append('project_id', filters.project_id.toString());
      }
      if (filters.skip !== undefined) {
        params.append('skip', filters.skip.toString());
      }
      if (filters.limit !== undefined) {
        params.append('limit', filters.limit.toString());
      }

      const queryString = params.toString();
      const response = await apiClient.get<Task[]>(
        `/tasks${queryString ? `?${queryString}` : ''}`
      );
      
      return response;
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      throw error;
    }
  }

  /**
   * Get a specific task by ID
   */
  async getTask(taskId: number): Promise<Task> {
    try {
      const response = await apiClient.get<Task>(`/tasks/${taskId}`);
      return response;
    } catch (error) {
      console.error(`Failed to fetch task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new task
   */
  async createTask(taskData: TaskCreate): Promise<Task> {
    try {
      const response = await apiClient.post<Task>('/tasks', taskData);
      return response;
    } catch (error) {
      console.error('Failed to create task:', error);
      throw error;
    }
  }

  /**
   * Update an existing task
   */
  async updateTask(taskId: number, taskData: TaskUpdate): Promise<Task> {
    try {
      const response = await apiClient.put<Task>(`/tasks/${taskId}`, taskData);
      return response;
    } catch (error) {
      console.error(`Failed to update task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Update only task status
   */
  async updateTaskStatus(
    taskId: number, 
    status: Task['status']
  ): Promise<Task> {
    try {
      const response = await apiClient.patch<Task>(
        `/tasks/${taskId}/status`, 
        { status }
      );
      return response;
    } catch (error) {
      console.error(`Failed to update task ${taskId} status:`, error);
      throw error;
    }
  }

  /**
   * Delete a task (soft delete)
   */
  async deleteTask(taskId: number): Promise<void> {
    try {
      await apiClient.delete(`/tasks/${taskId}`);
    } catch (error) {
      console.error(`Failed to delete task ${taskId}:`, error);
      throw error;
    }
  }

  /**
   * Get user's assigned tasks
   */
  async getMyTasks(): Promise<Task[]> {
    try {
      const response = await apiClient.get<Task[]>('/tasks/my-tasks');
      return response;
    } catch (error) {
      console.error('Failed to fetch my tasks:', error);
      // Fallback data for development
      return [];
    }
  }
}

// Export singleton instance
export const taskApi = new TaskApiService();