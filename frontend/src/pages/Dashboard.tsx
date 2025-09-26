import React from 'react';
import { 
  Calendar, 
  CheckCircle2, 
  Clock, 
  TrendingUp, 
  Users, 
  FolderOpen,
  AlertTriangle,
  Activity
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingComponents';
import { useDashboardStats, useTaskAnalytics, useProjectAnalytics } from '../hooks/useAnalytics';
import { useProjects } from '../hooks/useProjects';
import { useTasks } from '../hooks/useTasks';

const Dashboard: React.FC = () => {
  // Fetch dashboard data using React Query
  const { 
    data: dashboardStats, 
    isLoading: statsLoading, 
    error: statsError 
  } = useDashboardStats();
  
  const { 
    isLoading: taskAnalyticsLoading 
  } = useTaskAnalytics();
  
  const { 
    isLoading: projectAnalyticsLoading 
  } = useProjectAnalytics();
  
  const { 
    data: recentProjects, 
    isLoading: projectsLoading 
  } = useProjects({ 
    status: ['active', 'on_hold'], 
  });
  
  const { 
    data: recentTasks, 
    isLoading: tasksLoading 
  } = useTasks({ 
    status: ['todo', 'in_progress']
  });

  // Loading state
  if (statsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="lg" />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (statsError) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center">
              <AlertTriangle className="h-6 w-6 text-red-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-red-800">Failed to load dashboard data</h3>
                <p className="text-red-600 mt-1">Please try again in a moment.</p>
                <button 
                  onClick={() => window.location.reload()}
                  className="mt-3 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const stats = dashboardStats || {
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
  };

  // Helper function to get completion rate color
  const getCompletionRateColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600';
    if (rate >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Helper function to format percentage
  const formatPercentage = (value: number) => `${Math.round(value)}%`;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">Welcome back! Here's your project overview.</p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Activity className="h-4 w-4" />
              <span>Live Data • React Query Powered</span>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Tasks */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Tasks</p>
                <p className="text-2xl font-bold text-gray-900">{stats.tasks.total}</p>
                <p className={`text-sm ${getCompletionRateColor(stats.tasks.completion_rate)}`}>
                  {formatPercentage(stats.tasks.completion_rate)} completion rate
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <CheckCircle2 className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Active Projects */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Projects</p>
                <p className="text-2xl font-bold text-gray-900">{stats.projects.active}</p>
                <p className={`text-sm ${getCompletionRateColor(stats.projects.completion_rate)}`}>
                  {formatPercentage(stats.projects.completion_rate)} on track
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <FolderOpen className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* Team Members */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Team Members</p>
                <p className="text-2xl font-bold text-gray-900">{stats.team.total_members}</p>
                <p className="text-sm text-gray-500">
                  {stats.team.tasks_per_member.toFixed(1)} tasks/member avg
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>

          {/* Overdue Tasks */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Overdue Tasks</p>
                <p className="text-2xl font-bold text-red-600">{stats.tasks.overdue}</p>
                <p className="text-sm text-gray-500">
                  {stats.deadlines.due_today} due today
                </p>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts and Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Productivity Trends */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Productivity Trends</h3>
              <TrendingUp className="h-5 w-5 text-gray-400" />
            </div>
            
            {taskAnalyticsLoading ? (
              <div className="flex items-center justify-center h-40">
                <LoadingSpinner />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Today</span>
                  <span className="font-semibold">{stats.productivity.tasks_completed_today} tasks</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">This Week</span>
                  <span className="font-semibold">{stats.productivity.tasks_completed_this_week} tasks</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">This Month</span>
                  <span className="font-semibold">{stats.productivity.tasks_completed_this_month} tasks</span>
                </div>
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Avg. Completion Time</span>
                    <span className="font-semibold">
                      {stats.productivity.average_completion_time.toFixed(1)}h
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Project Progress */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Project Status</h3>
              <FolderOpen className="h-5 w-5 text-gray-400" />
            </div>
            
            {projectAnalyticsLoading ? (
              <div className="flex items-center justify-center h-40">
                <LoadingSpinner />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Active</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="font-semibold">{stats.projects.active}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">On Hold</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <span className="font-semibold">{stats.projects.on_hold}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Completed</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="font-semibold">{stats.projects.completed}</span>
                  </div>
                </div>
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Success Rate</span>
                    <span className={`font-semibold ${getCompletionRateColor(stats.projects.completion_rate)}`}>
                      {formatPercentage(stats.projects.completion_rate)}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Tasks */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent Tasks</h3>
              <Clock className="h-5 w-5 text-gray-400" />
            </div>
            
            {tasksLoading ? (
              <div className="flex items-center justify-center h-40">
                <LoadingSpinner />
              </div>
            ) : recentTasks && recentTasks.length > 0 ? (
              <div className="space-y-3">
                {recentTasks.slice(0, 5).map((task) => (
                  <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 truncate">{task.title}</p>
                      <p className="text-sm text-gray-500">
                        {task.priority} priority • {task.status}
                      </p>
                    </div>
                    <div className={`px-2 py-1 text-xs rounded-full ${
                      task.priority === 'high' ? 'bg-red-100 text-red-800' :
                      task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {task.priority}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-40 text-gray-500">
                <p>No recent tasks found</p>
              </div>
            )}
          </div>

          {/* Recent Projects */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Active Projects</h3>
              <Calendar className="h-5 w-5 text-gray-400" />
            </div>
            
            {projectsLoading ? (
              <div className="flex items-center justify-center h-40">
                <LoadingSpinner />
              </div>
            ) : recentProjects && recentProjects.length > 0 ? (
              <div className="space-y-3">
                {recentProjects.slice(0, 5).map((project) => (
                  <div key={project.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 truncate">{project.name}</p>
                      <p className="text-sm text-gray-500">
                        {project.completion_percentage}% complete • {project.task_count} tasks
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-12 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 transition-all"
                          style={{ width: `${project.completion_percentage}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 min-w-max">
                        {project.completion_percentage}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-40 text-gray-500">
                <p>No active projects found</p>
              </div>
            )}
          </div>
        </div>

        {/* Data Management Demo Notice */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-sm border border-blue-200 p-6">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-blue-900">
                Advanced Data Management Active
              </h4>
              <p className="text-blue-700 mt-1 mb-3">
                This dashboard is powered by TanStack React Query with optimistic updates, 
                intelligent caching, and real-time synchronization.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                  Optimistic Updates
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800">
                  Smart Caching
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
                  Real-time Sync
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-yellow-100 text-yellow-800">
                  Error Boundaries
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;