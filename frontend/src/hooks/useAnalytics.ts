/**
 * Analytics Data Hooks - Day 25 Implementation
 */
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../services/analyticsApi';

export const useDashboardAnalytics = (days: number = 30) => {
  return useQuery({
    queryKey: ['analytics', 'dashboard', days],
    queryFn: () => analyticsApi.getDashboardAnalytics(days),
    staleTime: 2 * 60 * 1000,
    retry: 2,
  });
};

export const useTaskAnalytics = (days: number = 30) => {
  return useQuery({
    queryKey: ['analytics', 'tasks', days],
    queryFn: () => analyticsApi.getTaskAnalytics(days),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
};

export const useProjectAnalytics = (days: number = 30) => {
  return useQuery({
    queryKey: ['analytics', 'projects', days],
    queryFn: () => analyticsApi.getProjectAnalytics(days),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
};

// Additional analytics hooks for DataManagementDemo compatibility
export const useTeamAnalytics = (days: number = 30, teamId?: number) => {
  return useQuery({
    queryKey: ['analytics', 'team', days, teamId],
    queryFn: () => analyticsApi.getTeamAnalytics(days, teamId),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
};

export const useTimeAnalytics = (days: number = 30) => {
  // Map to task analytics since we don't have a separate time analytics endpoint
  return useQuery({
    queryKey: ['analytics', 'tasks', 'time', days],
    queryFn: () => analyticsApi.getTaskAnalytics(days),
    staleTime: 5 * 60 * 1000,
    retry: 2,
    select: (data) => ({
      total_hours: data?.avg_completion_time_hours * (data?.completed_tasks || 0),
      avg_hours_per_task: data?.avg_completion_time_hours || 0,
      time_distribution: data?.completion_trend || [],
    }),
  });
};

export const usePerformanceMetrics = (days: number = 30) => {
  // Map to dashboard analytics to get performance data
  return useQuery({
    queryKey: ['analytics', 'dashboard', 'performance', days],
    queryFn: () => analyticsApi.getDashboardAnalytics(days),
    staleTime: 5 * 60 * 1000,
    retry: 2,
    select: (data) => ({
      productivity_score: data?.dashboard_stats?.productivity_score || 0,
      completion_rate: data?.dashboard_stats?.completion_rate || 0,
      avg_completion_time_hours: data?.dashboard_stats?.avg_completion_time_hours || 0,
      performance_summary: data?.performance_summary || {},
    }),
  });
};

export const useExportAnalytics = () => {
  return {
    exportDashboard: (format: 'csv' | 'excel' | 'pdf' = 'csv') => 
      analyticsApi.exportAnalytics(format, 30, false),
    exportTasks: (format: 'csv' | 'excel' | 'pdf' = 'csv') => 
      analyticsApi.exportAnalytics(format, 30, false),
    exportProjects: (format: 'csv' | 'excel' | 'pdf' = 'csv') => 
      analyticsApi.exportAnalytics(format, 30, false),
  };
};

// Utility functions
export const calculateCompletionRate = (completed: number, total: number): number => {
  return total > 0 ? (completed / total) * 100 : 0;
};

// Legacy compatibility
export const useDashboardStats = useDashboardAnalytics;
