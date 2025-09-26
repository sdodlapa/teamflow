/**
 * Analytics Dashboard Test - Day 25 Implementation
 * Quick test component to validate analytics functionality
 */

import React from 'react';
import { useDashboardAnalytics, useTaskAnalytics } from '../hooks/useAnalytics';

export const AnalyticsTest: React.FC = () => {
  const { data: dashboardData, isLoading, error } = useDashboardAnalytics(30);
  const { data: taskData } = useTaskAnalytics(30);

  if (isLoading) return <div className="p-4">Loading analytics...</div>;
  if (error) return <div className="p-4 text-red-600">Error: {error.message}</div>;

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border">
      <h2 className="text-xl font-bold mb-4">🧪 Analytics API Test</h2>
      
      {dashboardData ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-2xl font-bold text-blue-600">
                {dashboardData.dashboard_stats.total_tasks}
              </div>
              <div className="text-sm text-blue-800">Total Tasks</div>
            </div>
            
            <div className="bg-green-50 p-3 rounded">
              <div className="text-2xl font-bold text-green-600">
                {dashboardData.dashboard_stats.completed_tasks}
              </div>
              <div className="text-sm text-green-800">Completed</div>
            </div>
            
            <div className="bg-purple-50 p-3 rounded">
              <div className="text-2xl font-bold text-purple-600">
                {dashboardData.dashboard_stats.active_projects}
              </div>
              <div className="text-sm text-purple-800">Active Projects</div>
            </div>
            
            <div className="bg-orange-50 p-3 rounded">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round(dashboardData.dashboard_stats.completion_rate)}%
              </div>
              <div className="text-sm text-orange-800">Completion Rate</div>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="font-semibold mb-2">Recent Activity:</h3>
            <div className="space-y-2">
              {dashboardData.recent_activity.slice(0, 3).map((activity) => (
                <div key={activity.id} className="text-sm text-gray-600 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span>{activity.description}</span>
                  <span className="text-gray-400">({activity.user_name})</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6">
            <h3 className="font-semibold mb-2">Key Insights:</h3>
            <div className="space-y-2">
              {dashboardData.key_insights.slice(0, 2).map((insight) => (
                <div key={insight.id} className={`p-2 rounded text-sm ${
                  insight.impact === 'positive' ? 'bg-green-50 text-green-800' :
                  insight.impact === 'negative' ? 'bg-red-50 text-red-800' :
                  'bg-blue-50 text-blue-800'
                }`}>
                  <div className="font-medium">{insight.title}</div>
                  <div>{insight.description}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 text-xs text-gray-500">
            ✅ API Connection: Working | Last Updated: {new Date(dashboardData.last_updated).toLocaleTimeString()}
          </div>
        </div>
      ) : (
        <div className="text-gray-500">No dashboard data available</div>
      )}

      {taskData && (
        <div className="mt-6 pt-4 border-t">
          <h3 className="font-semibold mb-2">Task Analytics:</h3>
          <div className="text-sm space-y-1">
            <div>Total: {taskData.total_tasks}</div>
            <div>Completed: {taskData.completed_tasks}</div>
            <div>Completion Rate: {Math.round(taskData.completion_rate)}%</div>
            <div>Overdue: {taskData.overdue_count}</div>
          </div>
        </div>
      )}
    </div>
  );
};