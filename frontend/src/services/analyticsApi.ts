/**
 * Analytics API Service
 * Day 25: Analytics Dashboard Integration
 */

import { apiClient } from '../utils/apiClient';

// Types matching backend models
export interface DashboardStats {
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  overdue_tasks: number;
  active_projects: number;
  active_users: number;
  total_time_logged_hours: number;
  completion_rate: number;
  avg_completion_time_hours: number;
  productivity_score: number;
  tasks_trend: number;
  completion_trend: number;
  productivity_trend: number;
  time_trend: number;
}

export interface RecentActivityItem {
  id: string;
  type: string;
  description: string;
  user_name?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface KeyInsight {
  id: string;
  title: string;
  description: string;
  impact: 'positive' | 'negative' | 'neutral';
  category: 'productivity' | 'performance' | 'resources' | 'deadlines';
  confidence: number;
  action_required: boolean;
  recommendations: string[];
}

export interface AnalyticsDashboardData {
  dashboard_stats: DashboardStats;
  recent_activity: RecentActivityItem[];
  key_insights: KeyInsight[];
  performance_summary: Record<string, any>;
  period_days: number;
  last_updated: string;
}

export interface TaskAnalytics {
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  avg_completion_time_hours: number;
  overdue_count: number;
  by_priority: Record<string, number>;
  by_status: Record<string, number>;
  by_assignee: Array<{
    name: string;
    assigned: number;
    completed: number;
    completion_rate: number;
  }>;
  completion_trend: Array<{
    date: string;
    completed: number;
    total: number;
  }>;
}

export interface ProjectAnalytics {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  project_health: Record<string, any>;
  resource_utilization: Record<string, any>;
  milestone_tracking: Record<string, any>;
  project_performance: Array<Record<string, any>>;
}

export interface TeamAnalytics {
  team_size: number;
  active_members: number;
  productivity_metrics: Record<string, any>;
  workload_distribution: Array<{
    user: string;
    workload: number;
    capacity: number;
    efficiency: number;
  }>;
  collaboration_metrics: Record<string, any>;
  skill_analysis: Record<string, any>;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

class AnalyticsApiService {
  private readonly baseUrl = '/api/v1/analytics';

  /**
   * Get comprehensive dashboard analytics
   */
  async getDashboardAnalytics(days: number = 30): Promise<AnalyticsDashboardData> {
    // Temporarily force mock data for testing while authentication is being fixed
    // TODO: Remove this when authentication is working
    return this.getMockDashboardData(days);
    
    try {
      const response = await apiClient.get<AnalyticsDashboardData>(
        `${this.baseUrl}/dashboard?days=${days}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard analytics:', error);
      // Return mock data for development
      return this.getMockDashboardData(days);
    }
  }

  /**
   * Get detailed task analytics
   */
  async getTaskAnalytics(
    days: number = 30, 
    projectId?: number, 
    assigneeId?: number
  ): Promise<TaskAnalytics> {
    try {
      const params = new URLSearchParams({ days: days.toString() });
      if (projectId) params.append('project_id', projectId.toString());
      if (assigneeId) params.append('assignee_id', assigneeId.toString());

      const response = await apiClient.get<TaskAnalytics>(
        `${this.baseUrl}/tasks?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching task analytics:', error);
      return this.getMockTaskAnalytics();
    }
  }

  /**
   * Get project analytics
   */
  async getProjectAnalytics(days: number = 30): Promise<ProjectAnalytics> {
    try {
      const response = await apiClient.get<ProjectAnalytics>(
        `${this.baseUrl}/projects?days=${days}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching project analytics:', error);
      return this.getMockProjectAnalytics();
    }
  }

  /**
   * Get team analytics
   */
  async getTeamAnalytics(days: number = 30, teamId?: number): Promise<TeamAnalytics> {
    try {
      const params = new URLSearchParams({ days: days.toString() });
      if (teamId) params.append('team_id', teamId.toString());

      const response = await apiClient.get<TeamAnalytics>(
        `${this.baseUrl}/team?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching team analytics:', error);
      return this.getMockTeamAnalytics();
    }
  }

  /**
   * Export analytics data
   */
  async exportAnalytics(
    format: 'csv' | 'excel' | 'pdf' = 'csv',
    days: number = 30,
    includeCharts: boolean = false
  ): Promise<Blob> {
    try {
      const params = new URLSearchParams({
        format,
        days: days.toString(),
        include_charts: includeCharts.toString()
      });

      const response = await apiClient.get(`${this.baseUrl}/export?${params.toString()}`, {
        headers: { 'Accept': 'application/octet-stream' }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error exporting analytics:', error);
      throw error;
    }
  }

  /**
   * Refresh analytics cache
   */
  async refreshCache(): Promise<void> {
    try {
      await apiClient.post(`${this.baseUrl}/refresh`);
    } catch (error) {
      console.error('Error refreshing analytics cache:', error);
      throw error;
    }
  }

  // Mock data methods for development/fallback
  private getMockDashboardData(days: number): AnalyticsDashboardData {
    return {
      dashboard_stats: {
        total_tasks: 156,
        completed_tasks: 89,
        in_progress_tasks: 45,
        overdue_tasks: 12,
        active_projects: 12,
        active_users: 24,
        total_time_logged_hours: 1248.5,
        completion_rate: 57.1,
        avg_completion_time_hours: 4.2,
        productivity_score: 85.0,
        tasks_trend: 12.0,
        completion_trend: 8.0,
        productivity_trend: 7.0,
        time_trend: -15.0
      },
      recent_activity: [
        {
          id: 'act-001',
          type: 'task_completed',
          description: 'Sarah completed "Homepage Design" task',
          user_name: 'Sarah Johnson',
          timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString()
        },
        {
          id: 'act-002',
          type: 'project_created',
          description: 'New project "Mobile App" created by John',
          user_name: 'John Smith',
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString()
        },
        {
          id: 'act-003',
          type: 'task_overdue',
          description: 'Task "API Integration" is overdue',
          timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString()
        }
      ],
      key_insights: [
        {
          id: 'insight-001',
          title: 'Productivity Increased',
          description: 'Team velocity has improved by 12% this month',
          impact: 'positive',
          category: 'productivity',
          confidence: 0.85,
          action_required: false,
          recommendations: ['Continue current practices', 'Consider scaling successful strategies']
        },
        {
          id: 'insight-002',
          title: 'Faster Task Completion',
          description: 'Average task completion time improved by 15%',
          impact: 'positive',
          category: 'performance',
          confidence: 0.92,
          action_required: false,
          recommendations: []
        },
        {
          id: 'insight-003',
          title: 'Upcoming Deadlines',
          description: '3 high-priority tasks approaching deadlines',
          impact: 'neutral',
          category: 'deadlines',
          confidence: 1.0,
          action_required: true,
          recommendations: ['Review task priorities', 'Allocate additional resources', 'Consider deadline extensions']
        }
      ],
      performance_summary: {
        api_response_time: 245,
        database_performance: 92,
        cache_hit_rate: 87,
        system_health: 'healthy'
      },
      period_days: days,
      last_updated: new Date().toISOString()
    };
  }

  private getMockTaskAnalytics(): TaskAnalytics {
    return {
      total_tasks: 156,
      completed_tasks: 89,
      completion_rate: 57.1,
      avg_completion_time_hours: 4.2,
      overdue_count: 12,
      by_priority: {
        high: 35,
        medium: 78,
        low: 43
      },
      by_status: {
        todo: 22,
        in_progress: 45,
        in_review: 10,
        done: 89
      },
      by_assignee: [
        { name: 'Sarah Johnson', assigned: 25, completed: 18, completion_rate: 72.0 },
        { name: 'John Smith', assigned: 32, completed: 20, completion_rate: 62.5 },
        { name: 'Mike Davis', assigned: 28, completed: 22, completion_rate: 78.6 }
      ],
      completion_trend: [
        { date: '2024-09-19', completed: 8, total: 12 },
        { date: '2024-09-20', completed: 12, total: 15 },
        { date: '2024-09-21', completed: 10, total: 14 },
        { date: '2024-09-22', completed: 15, total: 18 },
        { date: '2024-09-23', completed: 11, total: 16 }
      ]
    };
  }

  private getMockProjectAnalytics(): ProjectAnalytics {
    return {
      total_projects: 12,
      active_projects: 8,
      completed_projects: 4,
      project_health: {
        healthy: 6,
        at_risk: 2,
        critical: 0
      },
      resource_utilization: {
        optimal: 5,
        over_allocated: 2,
        under_allocated: 1
      },
      milestone_tracking: {
        on_track: 18,
        behind: 4,
        ahead: 2
      },
      project_performance: [
        {
          id: 1,
          name: 'Website Redesign',
          completion: 85,
          health: 'healthy',
          team_size: 6,
          tasks_completed: 45,
          tasks_total: 53
        },
        {
          id: 2,
          name: 'Mobile App',
          completion: 32,
          health: 'healthy',
          team_size: 4,
          tasks_completed: 12,
          tasks_total: 37
        }
      ]
    };
  }

  private getMockTeamAnalytics(): TeamAnalytics {
    return {
      team_size: 24,
      active_members: 22,
      productivity_metrics: {
        avg_tasks_per_member: 6.5,
        avg_completion_time: 4.2,
        team_velocity: 85.0,
        collaboration_score: 78.0
      },
      workload_distribution: [
        { user: 'Sarah Johnson', workload: 85, capacity: 100, efficiency: 92 },
        { user: 'John Smith', workload: 78, capacity: 100, efficiency: 88 },
        { user: 'Mike Davis', workload: 92, capacity: 100, efficiency: 95 }
      ],
      collaboration_metrics: {
        shared_tasks: 34,
        cross_team_projects: 3,
        communication_frequency: 4.2,
        knowledge_sharing: 67
      },
      skill_analysis: {
        frontend: { members: 8, proficiency: 85 },
        backend: { members: 6, proficiency: 92 },
        design: { members: 4, proficiency: 88 },
        devops: { members: 2, proficiency: 78 }
      }
    };
  }
}

// Export singleton instance
export const analyticsApi = new AnalyticsApiService();
export default analyticsApi;