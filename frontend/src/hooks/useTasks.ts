/**
 * Task Data Hooks
 * React Query hooks for task data management
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../utils/apiClient';
import { queryKeys, optimisticUpdates } from '../lib/queryClient';
import { useToast } from '../contexts/ToastContext';

// Types
export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee_id?: number;
  assignee_email?: string;
  project_id?: number;
  due_date?: string;
  estimated_hours?: number;
  time_spent?: number;
  tags?: string[];
  created_at: string;
  updated_at: string;
  created_by: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority: Task['priority'];
  status?: Task['status'];
  assignee_email?: string;
  project_id?: number;
  due_date?: string;
  estimated_hours?: number;
  tags?: string[];
}

export interface TaskUpdate extends Partial<TaskCreate> {
  time_spent?: number;
}

export interface TaskFilters {
  status?: Task['status'][];
  priority?: Task['priority'][];
  assignee_id?: number;
  project_id?: number;
  due_date_from?: string;
  due_date_to?: string;
  search?: string;
}

// API functions
const taskApi = {
  // Get all tasks with optional filtering
  getTasks: async (filters?: TaskFilters): Promise<Task[]> => {
    const params = new URLSearchParams();
    
    if (filters?.status?.length) {
      filters.status.forEach(status => params.append('status', status));
    }
    if (filters?.priority?.length) {
      filters.priority.forEach(priority => params.append('priority', priority));
    }
    if (filters?.assignee_id) {
      params.append('assignee_id', filters.assignee_id.toString());
    }
    if (filters?.project_id) {
      params.append('project_id', filters.project_id.toString());
    }
    if (filters?.due_date_from) {
      params.append('due_date_from', filters.due_date_from);
    }
    if (filters?.due_date_to) {
      params.append('due_date_to', filters.due_date_to);
    }
    if (filters?.search) {
      params.append('search', filters.search);
    }
    
    const queryString = params.toString();
    const url = `/tasks${queryString ? `?${queryString}` : ''}`;
    
    const response = await apiClient.get<Task[]>(url);
    return response.data;
  },
  
  // Get single task by ID
  getTask: async (id: number): Promise<Task> => {
    const response = await apiClient.get<Task>(`/tasks/${id}`);
    return response.data;
  },
  
  // Create new task
  createTask: async (data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>('/tasks', data);
    return response.data;
  },
  
  // Update existing task
  updateTask: async (id: number, data: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put<Task>(`/tasks/${id}`, data);
    return response.data;
  },
  
  // Delete task
  deleteTask: async (id: number): Promise<void> => {
    await apiClient.delete(`/tasks/${id}`);
  },
  
  // Update task status only
  updateTaskStatus: async (id: number, status: Task['status']): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/tasks/${id}/status`, { status });
    return response.data;
  },
  
  // Get task statistics
  getTaskStats: async (): Promise<{
    total: number;
    by_status: Record<Task['status'], number>;
    by_priority: Record<Task['priority'], number>;
    overdue: number;
    due_today: number;
  }> => {
    const response = await apiClient.get('/tasks/stats');
    return response.data;
  },
};

// React Query Hooks

/**
 * Hook to fetch all tasks with optional filtering
 */
export const useTasks = (filters?: TaskFilters) => {
  return useQuery({
    queryKey: queryKeys.tasks.list(filters),
    queryFn: () => taskApi.getTasks(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes - tasks change frequently
    select: (data) => {
      // Optional data transformation
      return data.sort((a, b) => {
        // Sort by priority (critical first) then by created date (newest first)
        const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
        const aPriority = priorityOrder[a.priority];
        const bPriority = priorityOrder[b.priority];
        
        if (aPriority !== bPriority) {
          return aPriority - bPriority;
        }
        
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
    },
  });
};

/**
 * Hook to fetch a single task
 */
export const useTask = (id: number, enabled = true) => {
  return useQuery({
    queryKey: queryKeys.tasks.detail(id),
    queryFn: () => taskApi.getTask(id),
    enabled: enabled && !!id,
  });
};

/**
 * Hook to fetch task statistics
 */
export const useTaskStats = () => {
  return useQuery({
    queryKey: queryKeys.tasks.stats(),
    queryFn: taskApi.getTaskStats,
    staleTime: 5 * 60 * 1000, // 5 minutes - stats don't change as frequently
  });
};

/**
 * Hook to create a new task
 */
export const useCreateTask = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: taskApi.createTask,
    onMutate: async (newTask) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.tasks.lists() });
      
      // Create temporary task for optimistic update
      const tempTask: Task = {
        id: Date.now(), // Temporary ID
        ...newTask,
        status: newTask.status || 'todo',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        created_by: 1, // Would come from auth context
      };
      
      // Optimistically add the task
      optimisticUpdates.addTask(tempTask);
      
      return { tempTask };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.tempTask) {
        optimisticUpdates.removeTask(context.tempTask.id);
      }
      toast.error('Failed to create task');
    },
    onSuccess: (_data) => {
      toast.success('Task created successfully!');
    },
    onSettled: () => {
      // Refetch to get the real data
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.stats() });
    },
  });
};

/**
 * Hook to update a task
 */
export const useUpdateTask = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TaskUpdate }) => 
      taskApi.updateTask(id, data),
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.tasks.detail(id) });
      
      // Snapshot current value
      const previousTask = queryClient.getQueryData(queryKeys.tasks.detail(id));
      
      // Optimistically update the task
      queryClient.setQueryData(queryKeys.tasks.detail(id), (old: any) => ({
        ...old,
        ...data,
        updated_at: new Date().toISOString(),
      }));
      
      // Update in lists too
      queryClient.setQueriesData(
        { queryKey: queryKeys.tasks.lists() },
        (oldData: any) => {
          if (!oldData) return oldData;
          return oldData.map((task: Task) =>
            task.id === id ? { ...task, ...data, updated_at: new Date().toISOString() } : task
          );
        }
      );
      
      return { previousTask, id };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousTask) {
        queryClient.setQueryData(queryKeys.tasks.detail(context.id), context.previousTask);
      }
      toast.error('Failed to update task');
    },
    onSuccess: () => {
      toast.success('Task updated successfully!');
    },
    onSettled: (_data, _error, variables) => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.lists() });
    },
  });
};

/**
 * Hook to update task status with optimistic updates
 */
export const useUpdateTaskStatus = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: Task['status'] }) => 
      taskApi.updateTaskStatus(id, status),
    onMutate: async ({ id, status }) => {
      // Optimistic update
      optimisticUpdates.updateTaskStatus(id, status);
      
      return { id, status };
    },
    onError: (_error, _variables, _context) => {
      // On error, we could rollback, but React Query will refetch anyway
      toast.error(`Failed to update task status`);
    },
    onSuccess: (_data, variables) => {
      toast.success(`Task marked as ${variables.status.replace('_', ' ')}`);
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.stats() });
    },
  });
};

/**
 * Hook to delete a task
 */
export const useDeleteTask = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: taskApi.deleteTask,
    onMutate: async (id) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.tasks.lists() });
      
      // Snapshot current tasks
      const previousTasks = queryClient.getQueryData(queryKeys.tasks.lists());
      
      // Optimistically remove the task
      optimisticUpdates.removeTask(id);
      
      return { previousTasks, id };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueriesData(
          { queryKey: queryKeys.tasks.lists() },
          context.previousTasks
        );
      }
      toast.error('Failed to delete task');
    },
    onSuccess: () => {
      toast.success('Task deleted successfully');
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.stats() });
    },
  });
};