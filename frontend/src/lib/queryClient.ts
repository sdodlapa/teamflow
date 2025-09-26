/**
 * React Query Configuration
 * Centralized data fetching and state management setup
 */

import { QueryClient, DefaultOptions } from '@tanstack/react-query';

// Default query options for consistent behavior
const queryConfig: DefaultOptions = {
  queries: {
    // Stale time: How long data is considered fresh (5 minutes)
    staleTime: 5 * 60 * 1000,
    
    // Cache time: How long unused data stays in cache (10 minutes)
    gcTime: 10 * 60 * 1000,
    
    // Retry failed requests 3 times with exponential backoff
    retry: (failureCount, error: any) => {
      // Don't retry on 4xx errors (client errors)
      if (error?.response?.status >= 400 && error?.response?.status < 500) {
        return false;
      }
      // Retry up to 3 times for other errors
      return failureCount < 3;
    },
    
    // Retry delay with exponential backoff
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    
    // Refetch on window focus for fresh data
    refetchOnWindowFocus: true,
    
    // Refetch on reconnect after network issues
    refetchOnReconnect: true,
    
    // Don't refetch on mount if data is fresh
    refetchOnMount: true,
  },
  mutations: {
    // Retry failed mutations once
    retry: 1,
    
    // Mutation retry delay
    retryDelay: 1000,
  },
};

// Create the query client instance
export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});

// Query key factory for consistent key generation
export const queryKeys = {
  // User-related queries
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (filters?: any) => [...queryKeys.users.lists(), filters] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: string | number) => [...queryKeys.users.details(), id] as const,
    current: () => [...queryKeys.users.all, 'current'] as const,
  },
  
  // Task-related queries  
  tasks: {
    all: ['tasks'] as const,
    lists: () => [...queryKeys.tasks.all, 'list'] as const,
    list: (filters?: any) => [...queryKeys.tasks.lists(), filters] as const,
    details: () => [...queryKeys.tasks.all, 'detail'] as const,
    detail: (id: string | number) => [...queryKeys.tasks.details(), id] as const,
    stats: () => [...queryKeys.tasks.all, 'stats'] as const,
  },
  
  // Project-related queries
  projects: {
    all: ['projects'] as const,
    lists: () => [...queryKeys.projects.all, 'list'] as const,
    list: (filters?: any) => [...queryKeys.projects.lists(), filters] as const,
    details: () => [...queryKeys.projects.all, 'detail'] as const,
    detail: (id: string | number) => [...queryKeys.projects.details(), id] as const,
    tasks: (projectId: string | number) => [...queryKeys.projects.detail(projectId), 'tasks'] as const,
  },
  
  // Organization-related queries
  organizations: {
    all: ['organizations'] as const,
    lists: () => [...queryKeys.organizations.all, 'list'] as const,
    current: () => [...queryKeys.organizations.all, 'current'] as const,
    members: (orgId: string | number) => [...queryKeys.organizations.all, orgId, 'members'] as const,
  },
  
  // Analytics queries
  analytics: {
    all: ['analytics'] as const,
    dashboard: () => [...queryKeys.analytics.all, 'dashboard'] as const,
    tasks: (dateRange?: { from: string; to: string }) => [...queryKeys.analytics.all, 'tasks', dateRange] as const,
    projects: (dateRange?: { from: string; to: string }) => [...queryKeys.analytics.all, 'projects', dateRange] as const,
    performance: () => [...queryKeys.analytics.all, 'performance'] as const,
  },
} as const;

// Cache invalidation helpers
export const invalidateQueries = {
  // Invalidate all user data
  users: () => queryClient.invalidateQueries({ queryKey: queryKeys.users.all }),
  
  // Invalidate specific user
  user: (id: string | number) => queryClient.invalidateQueries({ queryKey: queryKeys.users.detail(id) }),
  
  // Invalidate all tasks
  tasks: () => queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all }),
  
  // Invalidate specific task
  task: (id: string | number) => queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(id) }),
  
  // Invalidate all projects
  projects: () => queryClient.invalidateQueries({ queryKey: queryKeys.projects.all }),
  
  // Invalidate specific project
  project: (id: string | number) => queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(id) }),
  
  // Invalidate analytics
  analytics: () => queryClient.invalidateQueries({ queryKey: queryKeys.analytics.all }),
  
  // Invalidate everything (use sparingly)
  all: () => queryClient.invalidateQueries(),
};

// Prefetch helpers for better UX
export const prefetchQueries = {
  // Prefetch user profile on login
  userProfile: async (userId: string | number) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.users.detail(userId),
      queryFn: () => {
        // This would be replaced with actual API call
        return Promise.resolve({ id: userId, name: 'User' });
      },
    });
  },
  
  // Prefetch dashboard data
  dashboard: async () => {
    await Promise.all([
      queryClient.prefetchQuery({
        queryKey: queryKeys.tasks.stats(),
        queryFn: () => Promise.resolve({ total: 0, completed: 0, pending: 0 }),
      }),
      queryClient.prefetchQuery({
        queryKey: queryKeys.analytics.dashboard(),
        queryFn: () => Promise.resolve({ metrics: {} }),
      }),
    ]);
  },
};

// Optimistic update helpers
export const optimisticUpdates = {
  // Update task status optimistically
  updateTaskStatus: (taskId: string | number, newStatus: string) => {
    queryClient.setQueryData(queryKeys.tasks.detail(taskId), (oldData: any) => ({
      ...oldData,
      status: newStatus,
      updated_at: new Date().toISOString(),
    }));
    
    // Also update the task in any lists
    queryClient.setQueriesData(
      { queryKey: queryKeys.tasks.lists() },
      (oldData: any) => {
        if (!oldData) return oldData;
        return oldData.map((task: any) =>
          task.id === taskId ? { ...task, status: newStatus } : task
        );
      }
    );
  },
  
  // Add new task optimistically
  addTask: (newTask: any) => {
    queryClient.setQueriesData(
      { queryKey: queryKeys.tasks.lists() },
      (oldData: any) => {
        if (!oldData) return [newTask];
        return [newTask, ...oldData];
      }
    );
  },
  
  // Remove task optimistically
  removeTask: (taskId: string | number) => {
    queryClient.setQueriesData(
      { queryKey: queryKeys.tasks.lists() },
      (oldData: any) => {
        if (!oldData) return oldData;
        return oldData.filter((task: any) => task.id !== taskId);
      }
    );
  },
};