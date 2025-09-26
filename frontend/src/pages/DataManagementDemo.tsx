/**
 * Data Management Demo Page
 * Comprehensive demonstration of React Query data management capabilities
 */

import React, { useState } from 'react';
import {
  Database,
  RefreshCw,
  Download,
  CheckCircle2,
  FolderOpen,
  Activity,
  Zap,
  Shield,
  Gauge,
  BarChart3
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingComponents';

// Import all our data hooks
import { 
  useDashboardStats, 
  useTaskAnalytics, 
  useProjectAnalytics, 
  useTeamAnalytics,
  useTimeAnalytics,
  usePerformanceMetrics,
  useExportAnalytics,
  calculateCompletionRate,
  type DateRange
} from '../hooks/useAnalytics';
import { useProjects, useProjectStats, useCreateProject } from '../hooks/useProjects';
import { useTasks, useCreateTask, useUpdateTask } from '../hooks/useTasks';
import { useToast } from '../contexts/ToastContext';

const DataManagementDemo: React.FC = () => {
  const [_selectedDateRange, _setSelectedDateRange] = useState<{
    start_date?: string;
    end_date?: string;
  }>({});
  
  const [taskFilter, _setTaskFilter] = useState<{
    status?: Array<'todo' | 'in_progress' | 'completed' | 'cancelled'>;
  }>({});
  
  const [projectFilter, _setProjectFilter] = useState<{
    status?: Array<'active' | 'completed' | 'on_hold' | 'cancelled'>;
  }>({});

  const toast = useToast();
  const { exportData } = useExportAnalytics();

  // Data hooks with various configurations
  const dashboardQuery = useDashboardStats();
  const taskAnalyticsQuery = useTaskAnalytics();
  const projectAnalyticsQuery = useProjectAnalytics();
  const teamAnalyticsQuery = useTeamAnalytics();
  const timeAnalyticsQuery = useTimeAnalytics();
  const performanceQuery = usePerformanceMetrics();
  
  const projectStatsQuery = useProjectStats();
  const projectsQuery = useProjects(projectFilter);
  const tasksQuery = useTasks(taskFilter);
  
  // Mutation hooks
  const createProjectMutation = useCreateProject();
  const createTaskMutation = useCreateTask();
  const updateTaskMutation = useUpdateTask();

  // Demo actions
  const handleCreateSampleProject = () => {
    createProjectMutation.mutate({
      name: `Demo Project ${new Date().toLocaleTimeString()}`,
      description: 'A sample project created from the data management demo',
      priority: 'medium',
      start_date: new Date().toISOString().split('T')[0],
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    });
  };

  const handleCreateSampleTask = () => {
    const projects = projectsQuery.data;
    if (!projects || projects.length === 0) {
      toast.error('Please create a project first');
      return;
    }
    
    createTaskMutation.mutate({
      title: `Demo Task ${new Date().toLocaleTimeString()}`,
      description: 'A sample task created from the data management demo',
      priority: 'medium',
      status: 'todo',
      project_id: projects[0].id,
      due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
    });
  };

  const handleUpdateRandomTask = () => {
    const tasks = tasksQuery.data;
    if (!tasks || tasks.length === 0) {
      toast.error('No tasks available to update');
      return;
    }
    
    const randomTask = tasks[Math.floor(Math.random() * tasks.length)];
    const statuses: Array<'todo' | 'in_progress' | 'completed'> = ['todo', 'in_progress', 'completed'];
    const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
    
    updateTaskMutation.mutate({
      id: randomTask.id,
      data: { status: newStatus }
    });
  };

  const handleExportData = async (format: 'csv' | 'excel') => {
    const success = await exportData(format);
    if (success) {
      toast.success(`Analytics exported as ${format.toUpperCase()}`);
    } else {
      toast.error('Export failed');
    }
  };

  const handleRefreshAll = () => {
    // Manually refetch all queries to demonstrate cache invalidation
    dashboardQuery.refetch();
    taskAnalyticsQuery.refetch();
    projectAnalyticsQuery.refetch();
    teamAnalyticsQuery.refetch();
    timeAnalyticsQuery.refetch();
    performanceQuery.refetch();
    projectStatsQuery.refetch();
    projectsQuery.refetch();
    tasksQuery.refetch();
  };

  // Calculate loading states
  const isLoading = [
    dashboardQuery.isLoading,
    taskAnalyticsQuery.isLoading,
    projectAnalyticsQuery.isLoading,
    projectsQuery.isLoading,
    tasksQuery.isLoading
  ].some(Boolean);

  // Calculate error states
  const hasErrors = [
    dashboardQuery.error,
    taskAnalyticsQuery.error,
    projectAnalyticsQuery.error,
    projectsQuery.error,
    tasksQuery.error
  ].some(Boolean);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg text-white p-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <Database className="h-8 w-8" />
                <h1 className="text-3xl font-bold">Data Management Demo</h1>
              </div>
              <p className="text-blue-100 text-lg">
                Comprehensive demonstration of TanStack React Query data management
              </p>
              <p className="text-blue-200 text-sm mt-2">
                Features: Optimistic Updates • Smart Caching • Real-time Sync • Error Boundaries
              </p>
            </div>
            <div className="text-right">
              <div className="bg-white/20 rounded-lg p-4 backdrop-blur-sm">
                <div className="text-2xl font-bold">Day 8</div>
                <div className="text-sm text-blue-200">Data Management & State</div>
              </div>
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Shield className="h-5 w-5 mr-2 text-blue-600" />
              Control Panel
            </h2>
            <div className="flex items-center space-x-2">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                isLoading ? 'bg-yellow-100 text-yellow-800' :
                hasErrors ? 'bg-red-100 text-red-800' :
                'bg-green-100 text-green-800'
              }`}>
                {isLoading ? 'Loading...' : hasErrors ? 'Has Errors' : 'All Systems Go'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Refresh All Data */}
            <button
              onClick={handleRefreshAll}
              disabled={isLoading}
              className="flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh All</span>
            </button>

            {/* Create Sample Project */}
            <button
              onClick={handleCreateSampleProject}
              disabled={createProjectMutation.isPending}
              className="flex items-center justify-center space-x-2 bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <FolderOpen className="h-4 w-4" />
              <span>Create Project</span>
            </button>

            {/* Create Sample Task */}
            <button
              onClick={handleCreateSampleTask}
              disabled={createTaskMutation.isPending}
              className="flex items-center justify-center space-x-2 bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>Create Task</span>
            </button>

            {/* Update Random Task */}
            <button
              onClick={handleUpdateRandomTask}
              disabled={updateTaskMutation.isPending || !tasksQuery.data?.length}
              className="flex items-center justify-center space-x-2 bg-orange-600 text-white px-4 py-3 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Zap className="h-4 w-4" />
              <span>Update Random</span>
            </button>
          </div>

          {/* Export Controls */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
              <Download className="h-4 w-4 mr-2" />
              Data Export
            </h3>
            <div className="flex space-x-3">
              <button
                onClick={() => handleExportData('csv')}
                className="flex items-center space-x-2 bg-gray-600 text-white px-3 py-2 rounded-md hover:bg-gray-700 transition-colors text-sm"
              >
                <Download className="h-3 w-3" />
                <span>Export CSV</span>
              </button>
              <button
                onClick={() => handleExportData('excel')}
                className="flex items-center space-x-2 bg-gray-600 text-white px-3 py-2 rounded-md hover:bg-gray-700 transition-colors text-sm"
              >
                <Download className="h-3 w-3" />
                <span>Export Excel</span>
              </button>
            </div>
          </div>
        </div>

        {/* Real-time Statistics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Dashboard Stats */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Dashboard</h3>
              <Activity className="h-5 w-5 text-blue-600" />
            </div>
            {dashboardQuery.isLoading ? (
              <LoadingSpinner />
            ) : dashboardQuery.data ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Tasks</span>
                  <span className="font-semibold">{dashboardQuery.data.tasks.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Projects</span>
                  <span className="font-semibold">{dashboardQuery.data.projects.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Team</span>
                  <span className="font-semibold">{dashboardQuery.data.team.total_members}</span>
                </div>
                <div className="pt-3 border-t border-gray-200">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Completion</span>
                    <span className="font-semibold text-green-600">
                      {calculateCompletionRate(
                        dashboardQuery.data.tasks.completed,
                        dashboardQuery.data.tasks.total
                      )}%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No data available</div>
            )}
          </div>

          {/* Project Statistics */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Projects</h3>
              <FolderOpen className="h-5 w-5 text-green-600" />
            </div>
            {projectStatsQuery.isLoading ? (
              <LoadingSpinner />
            ) : projectStatsQuery.data ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Active</span>
                  <span className="font-semibold text-green-600">
                    {projectStatsQuery.data.by_status.active || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Completed</span>
                  <span className="font-semibold text-blue-600">
                    {projectStatsQuery.data.by_status.completed || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Overdue</span>
                  <span className="font-semibold text-red-600">
                    {projectStatsQuery.data.overdue || 0}
                  </span>
                </div>
                <div className="pt-3 border-t border-gray-200">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Avg. Progress</span>
                    <span className="font-semibold">
                      {Math.round(projectStatsQuery.data.completion_average || 0)}%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No project data</div>
            )}
          </div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
              <Gauge className="h-5 w-5 text-purple-600" />
            </div>
            {performanceQuery.isLoading ? (
              <LoadingSpinner />
            ) : performanceQuery.data ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">API Response</span>
                  <span className="font-semibold">
                    {performanceQuery.data.system_health.api_response_time}ms
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Active Users</span>
                  <span className="font-semibold text-green-600">
                    {performanceQuery.data.system_health.active_users}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Error Rate</span>
                  <span className="font-semibold text-red-600">
                    {performanceQuery.data.system_health.error_rate}%
                  </span>
                </div>
                <div className="pt-3 border-t border-gray-200">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Uptime</span>
                    <span className="font-semibold text-green-600">
                      {performanceQuery.data.system_health.uptime}%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No performance data</div>
            )}
          </div>

          {/* Query Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Query Status</h3>
              <BarChart3 className="h-5 w-5 text-indigo-600" />
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Active Queries</span>
                <span className="font-semibold">9</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Loading</span>
                <span className="font-semibold text-yellow-600">
                  {[
                    dashboardQuery.isLoading,
                    projectsQuery.isLoading,
                    tasksQuery.isLoading,
                    taskAnalyticsQuery.isLoading,
                    projectAnalyticsQuery.isLoading
                  ].filter(Boolean).length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Errors</span>
                <span className="font-semibold text-red-600">
                  {[
                    dashboardQuery.error,
                    projectsQuery.error,
                    tasksQuery.error,
                    taskAnalyticsQuery.error,
                    projectAnalyticsQuery.error
                  ].filter(Boolean).length}
                </span>
              </div>
              <div className="pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Cached</span>
                  <span className="font-semibold text-blue-600">
                    {[
                      dashboardQuery.isSuccess,
                      projectsQuery.isSuccess,
                      tasksQuery.isSuccess
                    ].filter(Boolean).length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Data Preview Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Projects */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent Projects</h3>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  projectsQuery.isLoading ? 'bg-yellow-500' :
                  projectsQuery.error ? 'bg-red-500' : 'bg-green-500'
                }`} />
                <span className="text-sm text-gray-500">
                  {projectsQuery.data?.length || 0} items
                </span>
              </div>
            </div>
            
            {projectsQuery.isLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : projectsQuery.data && projectsQuery.data.length > 0 ? (
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {projectsQuery.data.slice(0, 5).map((project) => (
                  <div key={project.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 truncate">{project.name}</p>
                      <p className="text-sm text-gray-500">
                        {project.completion_percentage}% complete • {project.status}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-12 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500"
                          style={{ width: `${project.completion_percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FolderOpen className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p>No projects found</p>
              </div>
            )}
          </div>

          {/* Recent Tasks */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent Tasks</h3>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  tasksQuery.isLoading ? 'bg-yellow-500' :
                  tasksQuery.error ? 'bg-red-500' : 'bg-green-500'
                }`} />
                <span className="text-sm text-gray-500">
                  {tasksQuery.data?.length || 0} items
                </span>
              </div>
            </div>
            
            {tasksQuery.isLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : tasksQuery.data && tasksQuery.data.length > 0 ? (
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {tasksQuery.data.slice(0, 5).map((task) => (
                  <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 truncate">{task.title}</p>
                      <p className="text-sm text-gray-500">
                        {task.priority} priority • {task.status}
                      </p>
                    </div>
                    <div className={`px-2 py-1 text-xs rounded-full ${
                      task.status === 'completed' ? 'bg-green-100 text-green-800' :
                      task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      task.status === 'todo' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {task.status}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p>No tasks found</p>
              </div>
            )}
          </div>
        </div>

        {/* Technical Features Summary */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow-sm border border-indigo-200 p-6">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Zap className="h-6 w-6 text-indigo-600" />
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-indigo-900 mb-3">
                Advanced Data Management Features Demonstrated
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <h5 className="font-medium text-indigo-800">Query Management</h5>
                  <ul className="text-sm text-indigo-700 space-y-1">
                    <li>• Parallel data fetching</li>
                    <li>• Smart caching strategies</li>
                    <li>• Automatic refetching</li>
                    <li>• Background updates</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h5 className="font-medium text-indigo-800">Optimistic Updates</h5>
                  <ul className="text-sm text-indigo-700 space-y-1">
                    <li>• Instant UI feedback</li>
                    <li>• Rollback on errors</li>
                    <li>• Cache synchronization</li>
                    <li>• Mutation queuing</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h5 className="font-medium text-indigo-800">Error Handling</h5>
                  <ul className="text-sm text-indigo-700 space-y-1">
                    <li>• Retry mechanisms</li>
                    <li>• Fallback states</li>
                    <li>• Error boundaries</li>
                    <li>• User notifications</li>
                  </ul>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-indigo-200">
                <p className="text-indigo-700 text-sm">
                  🚀 <strong>Day 8 Complete:</strong> Advanced data management with TanStack React Query 
                  provides enterprise-grade state management with optimistic updates, intelligent caching, 
                  and comprehensive error handling.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataManagementDemo;