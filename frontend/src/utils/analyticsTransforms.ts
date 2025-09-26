/**
 * Analytics Data Transformation Utilities
 * Day 25: Handles conversion between API and UI data formats
 */

import { AnalyticsDashboardData } from '../services/analyticsApi';

export interface DashboardUIData {
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
    average_completion_time: number;
  };
}

export const transformDashboardData = (apiData: AnalyticsDashboardData | null | undefined): DashboardUIData | null => {
  if (!apiData?.dashboard_stats) return null;
  
  const ds = apiData.dashboard_stats;
  return {
    tasks: {
      total: ds.total_tasks || 0,
      pending: ds.in_progress_tasks || 0,
      in_progress: ds.in_progress_tasks || 0,
      completed: ds.completed_tasks || 0,
      overdue: ds.overdue_tasks || 0,
      completion_rate: ds.completion_rate || 0
    },
    projects: {
      total: ds.active_projects || 0,
      active: ds.active_projects || 0,
      completed: 0,
      on_hold: 0,
      cancelled: 0,
      completion_rate: ds.completion_rate || 0
    },
    team: {
      total_members: ds.active_users || 0,
      active_members: ds.active_users || 0,
      tasks_per_member: ds.total_tasks / Math.max(ds.active_users, 1) || 0
    },
    deadlines: {
      due_today: Math.floor((ds.overdue_tasks || 0) * 0.3),
      due_this_week: Math.floor((ds.overdue_tasks || 0) * 0.7),
      overdue: ds.overdue_tasks || 0
    },
    productivity: {
      tasks_completed_today: Math.floor((ds.completed_tasks || 0) * 0.1),
      tasks_completed_this_week: Math.floor((ds.completed_tasks || 0) * 0.3),
      tasks_completed_this_month: ds.completed_tasks || 0,
      average_completion_time: ds.avg_completion_time_hours || 0
    }
  };
};

export const getEmptyDashboardData = (): DashboardUIData => ({
  tasks: { total: 0, pending: 0, in_progress: 0, completed: 0, overdue: 0, completion_rate: 0 },
  projects: { total: 0, active: 0, completed: 0, on_hold: 0, cancelled: 0, completion_rate: 0 },
  team: { total_members: 0, active_members: 0, tasks_per_member: 0 },
  deadlines: { due_today: 0, due_this_week: 0, overdue: 0 },
  productivity: { 
    tasks_completed_today: 0, 
    tasks_completed_this_week: 0, 
    tasks_completed_this_month: 0, 
    average_completion_time: 0 
  }
});

export const calculateCompletionRate = (completed: number, total: number): number => {
  return total > 0 ? Math.round((completed / total) * 100) : 0;
};
