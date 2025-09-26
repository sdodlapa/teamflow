/**
 * Analytics Data Hooks
 * React Query hooks for analytics and reporting data
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../utils/apiClient';
import { queryKeys } from '../lib/queryClient';

// Types
export interface DashboardStats {
  tasks: {
    total: number;
    pending: number;
    in_progress: number;
    completed: number;
    overdue: number;
    completion_rate: number;
  };
  projects: {
    total: number;
    active: number;
    completed: number;
    on_hold: number;
    cancelled: number;
    completion_rate: number;
  };
  team: {
    total_members: number;
    active_members: number;
    tasks_per_member: number;
  };
  deadlines: {
    due_today: number;
    due_this_week: number;
    overdue: number;
  };
  productivity: {
    tasks_completed_today: number;
    tasks_completed_this_week: number;
    tasks_completed_this_month: number;
    average_completion_time: number; // in hours
  };
}

export interface TaskAnalytics {
  task_creation_trend: Array<{
    date: string;
    count: number;
  }>;
  task_completion_trend: Array<{
    date: string;
    count: number;
  }>;
  status_distribution: Array<{
    status: string;
    count: number;
    percentage: number;
  }>;
  priority_distribution: Array<{
    priority: string;
    count: number;
    percentage: number;
  }>;
  assignee_performance: Array<{
    user_id: number;
    user_name: string;
    user_email: string;
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    completion_rate: number;
    average_completion_time: number; // in hours
  }>;
  category_distribution: Array<{
    category: string;
    count: number;
    percentage: number;
  }>;
}

export interface ProjectAnalytics {
  project_progress: Array<{
    project_id: number;
    project_name: string;
    completion_percentage: number;
    total_tasks: number;
    completed_tasks: number;
    team_members: number;
    days_remaining: number;
  }>;
  budget_analysis: Array<{
    project_id: number;
    project_name: string;
    budget: number;
    spent_amount: number;
    remaining_budget: number;
    budget_utilization: number; // percentage
  }>;
  timeline_analysis: Array<{
    project_id: number;
    project_name: string;
    start_date: string;
    due_date: string;
    estimated_completion: string;
    is_on_track: boolean;
    days_ahead_behind: number;
  }>;
  team_workload: Array<{
    user_id: number;
    user_name: string;
    user_email: string;
    project_count: number;
    total_tasks: number;
    workload_percentage: number;
  }>;
}

export interface TeamAnalytics {
  member_activity: Array<{
    user_id: number;
    user_name: string;
    user_email: string;
    last_active: string;
    tasks_created: number;
    tasks_completed: number;
    comments_made: number;
    projects_joined: number;
  }>;
  collaboration_metrics: {
    total_comments: number;
    average_response_time: number; // in hours
    most_collaborative_project: {
      id: number;
      name: string;
      comment_count: number;
    };
  };
  skill_distribution: Array<{
    skill: string;
    member_count: number;
    expertise_levels: Record<string, number>;
  }>;
  department_breakdown: Array<{
    department: string;
    member_count: number;
    task_completion_rate: number;
  }>;
}

export interface TimeAnalytics {
  daily_activity: Array<{
    date: string;
    tasks_created: number;
    tasks_completed: number;
    hours_logged: number;
  }>;
  weekly_summary: Array<{
    week_start: string;
    tasks_created: number;
    tasks_completed: number;
    hours_logged: number;
    productivity_score: number;
  }>;
  monthly_trends: Array<{
    month: string;
    tasks_created: number;
    tasks_completed: number;
    hours_logged: number;
    team_growth: number;
  }>;
  peak_hours: Array<{
    hour: number;
    activity_count: number;
  }>;
}

export interface PerformanceMetrics {
  system_health: {
    api_response_time: number; // in ms
    database_query_time: number; // in ms
    active_users: number;
    error_rate: number; // percentage
    uptime: number; // percentage
  };
  usage_statistics: {
    total_api_calls: number;
    most_used_endpoints: Array<{
      endpoint: string;
      call_count: number;
    }>;
    peak_usage_times: Array<{
      hour: number;
      request_count: number;
    }>;
  };
  feature_adoption: Array<{
    feature: string;
    usage_count: number;
    adoption_rate: number; // percentage
  }>;
}

// Date range type for analytics queries
export type DateRange = {
  start_date: string;
  end_date: string;
};

// API functions
const analyticsApi = {
  // Dashboard overview statistics
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/analytics/dashboard');
    return response.data;
  },
  
  // Task analytics with date range
  getTaskAnalytics: async (dateRange?: DateRange): Promise<TaskAnalytics> => {
    const params = new URLSearchParams();
    if (dateRange?.start_date) params.append('start_date', dateRange.start_date);
    if (dateRange?.end_date) params.append('end_date', dateRange.end_date);
    
    const queryString = params.toString();
    const url = `/analytics/tasks${queryString ? `?${queryString}` : ''}`;
    
    const response = await apiClient.get<TaskAnalytics>(url);
    return response.data;
  },
  
  // Project analytics
  getProjectAnalytics: async (dateRange?: DateRange): Promise<ProjectAnalytics> => {
    const params = new URLSearchParams();
    if (dateRange?.start_date) params.append('start_date', dateRange.start_date);
    if (dateRange?.end_date) params.append('end_date', dateRange.end_date);
    
    const queryString = params.toString();
    const url = `/analytics/projects${queryString ? `?${queryString}` : ''}`;
    
    const response = await apiClient.get<ProjectAnalytics>(url);
    return response.data;
  },
  
  // Team analytics
  getTeamAnalytics: async (dateRange?: DateRange): Promise<TeamAnalytics> => {
    const params = new URLSearchParams();
    if (dateRange?.start_date) params.append('start_date', dateRange.start_date);
    if (dateRange?.end_date) params.append('end_date', dateRange.end_date);
    
    const queryString = params.toString();
    const url = `/analytics/team${queryString ? `?${queryString}` : ''}`;
    
    const response = await apiClient.get<TeamAnalytics>(url);
    return response.data;
  },
  
  // Time-based analytics
  getTimeAnalytics: async (dateRange?: DateRange): Promise<TimeAnalytics> => {
    const params = new URLSearchParams();
    if (dateRange?.start_date) params.append('start_date', dateRange.start_date);
    if (dateRange?.end_date) params.append('end_date', dateRange.end_date);
    
    const queryString = params.toString();
    const url = `/analytics/time${queryString ? `?${queryString}` : ''}`;
    
    const response = await apiClient.get<TimeAnalytics>(url);
    return response.data;
  },
  
  // Performance metrics
  getPerformanceMetrics: async (): Promise<PerformanceMetrics> => {
    const response = await apiClient.get<PerformanceMetrics>('/analytics/performance');
    return response.data;
  },
  
  // Export analytics data
  exportAnalytics: async (type: 'csv' | 'excel', dateRange?: DateRange): Promise<Blob> => {
    const params = new URLSearchParams();
    params.append('format', type);
    if (dateRange?.start_date) params.append('start_date', dateRange.start_date);
    if (dateRange?.end_date) params.append('end_date', dateRange.end_date);
    
    const token = localStorage.getItem('access_token');
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    
    const response = await fetch(`${baseUrl}/analytics/export?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Export failed');
    }
    
    return await response.blob();
  },
};

// React Query Hooks

/**
 * Hook to fetch dashboard statistics
 */
export const useDashboardStats = () => {
  return useQuery({
    queryKey: [...queryKeys.analytics.all, 'dashboard'],
    queryFn: analyticsApi.getDashboardStats,
    staleTime: 2 * 60 * 1000, // 2 minutes - dashboard should be relatively fresh
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  });
};

/**
 * Hook to fetch task analytics
 */
export const useTaskAnalytics = (dateRange?: DateRange) => {
  return useQuery({
    queryKey: [...queryKeys.analytics.all, 'tasks', dateRange],
    queryFn: () => analyticsApi.getTaskAnalytics(dateRange),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to fetch project analytics
 */
export const useProjectAnalytics = (dateRange?: DateRange) => {
  return useQuery({
    queryKey: [...queryKeys.analytics.all, 'projects', dateRange],
    queryFn: () => analyticsApi.getProjectAnalytics(dateRange),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to fetch team analytics
 */
export const useTeamAnalytics = (dateRange?: DateRange) => {
  return useQuery({
    queryKey: [...queryKeys.analytics.all, 'team', dateRange],
    queryFn: () => analyticsApi.getTeamAnalytics(dateRange),
    staleTime: 10 * 60 * 1000, // 10 minutes - team data changes less frequently
  });
};

/**
 * Hook to fetch time analytics
 */
export const useTimeAnalytics = (dateRange?: DateRange) => {
  return useQuery({
    queryKey: [...queryKeys.analytics.all, 'time', dateRange],
    queryFn: () => analyticsApi.getTimeAnalytics(dateRange),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to fetch performance metrics
 */
export const usePerformanceMetrics = () => {
  return useQuery({
    queryKey: [...queryKeys.analytics.all, 'performance'],
    queryFn: analyticsApi.getPerformanceMetrics,
    staleTime: 1 * 60 * 1000, // 1 minute - performance metrics should be fresh
    refetchInterval: 2 * 60 * 1000, // Auto-refresh every 2 minutes
  });
};

/**
 * Hook for exporting analytics data
 * Note: This doesn't use React Query since it's a one-time operation
 */
export const useExportAnalytics = () => {
  const exportData = async (type: 'csv' | 'excel', dateRange?: DateRange) => {
    try {
      const blob = await analyticsApi.exportAnalytics(type, dateRange);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analytics-${new Date().toISOString().split('T')[0]}.${type === 'csv' ? 'csv' : 'xlsx'}`;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      
      return true;
    } catch (error) {
      console.error('Export failed:', error);
      return false;
    }
  };
  
  return { exportData };
};

// Utility functions for common analytics calculations

/**
 * Calculate completion rate percentage
 */
export const calculateCompletionRate = (completed: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
};

/**
 * Calculate trend percentage change
 */
export const calculateTrendChange = (current: number, previous: number): number => {
  if (previous === 0) return current > 0 ? 100 : 0;
  return Math.round(((current - previous) / previous) * 100);
};

/**
 * Get status color for metrics
 */
export const getMetricStatus = (value: number, thresholds: { good: number; warning: number }) => {
  if (value >= thresholds.good) return 'success';
  if (value >= thresholds.warning) return 'warning';
  return 'error';
};

/**
 * Format duration from hours to human readable
 */
export const formatDuration = (hours: number): string => {
  if (hours < 1) {
    return `${Math.round(hours * 60)}m`;
  } else if (hours < 24) {
    return `${Math.round(hours * 10) / 10}h`;
  } else {
    const days = Math.floor(hours / 24);
    const remainingHours = Math.round((hours % 24) * 10) / 10;
    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
  }
};