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

// Legacy compatibility
export const useDashboardStats = useDashboardAnalytics;
