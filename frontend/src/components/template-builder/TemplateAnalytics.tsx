import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Users,
  Eye,
  Download,
  Star,
  Activity,
  Target,
  Zap,
  AlertCircle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  RefreshCw,
  Share2,
  Code,
  Database,
  X
} from 'lucide-react';
import { DomainConfig, Entity, Relationship } from '../../types/template';

interface AnalyticsMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  change: number;
  change_type: 'increase' | 'decrease' | 'neutral';
  trend: number[];
  category: 'usage' | 'performance' | 'engagement' | 'quality';
}

interface UsageData {
  date: string;
  views: number;
  downloads: number;
  unique_users: number;
  generated_projects: number;
}

interface GeographicData {
  country: string;
  users: number;
  percentage: number;
}

interface TemplateInsight {
  id: string;
  type: 'optimization' | 'trend' | 'issue' | 'success';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  actionable: boolean;
  suggested_action?: string;
  timestamp: string;
}

interface PerformanceMetric {
  metric: string;
  current_value: number;
  benchmark: number;
  score: number;
  status: 'excellent' | 'good' | 'needs_improvement' | 'poor';
}

interface TemplateAnalyticsProps {
  domainConfig: DomainConfig;
  entities: Entity[];
  relationships: Relationship[];
  onClose?: () => void;
}

const TemplateAnalytics: React.FC<TemplateAnalyticsProps> = ({
  domainConfig,
  entities,
  relationships,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'usage' | 'performance' | 'insights'>('overview');
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [metrics, setMetrics] = useState<AnalyticsMetric[]>([]);
  const [usageData, setUsageData] = useState<UsageData[]>([]);
  const [geographicData, setGeographicData] = useState<GeographicData[]>([]);
  const [insights, setInsights] = useState<TemplateInsight[]>([]);
  const [performance, setPerformance] = useState<PerformanceMetric[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    setIsLoading(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock analytics data
    setMetrics([
      {
        id: '1',
        name: 'Total Views',
        value: 12547,
        unit: 'views',
        change: 23.5,
        change_type: 'increase',
        trend: [100, 120, 110, 140, 160, 155, 170, 165, 180, 175, 190, 185, 200],
        category: 'usage'
      },
      {
        id: '2',
        name: 'Downloads',
        value: 3456,
        unit: 'downloads',
        change: 15.2,
        change_type: 'increase',
        trend: [50, 55, 48, 62, 70, 68, 75, 72, 80, 78, 85, 82, 90],
        category: 'usage'
      },
      {
        id: '3',
        name: 'Generated Projects',
        value: 847,
        unit: 'projects',
        change: 34.7,
        change_type: 'increase',
        trend: [10, 12, 11, 15, 18, 16, 20, 19, 22, 21, 25, 24, 28],
        category: 'engagement'
      },
      {
        id: '4',
        name: 'Avg Generation Time',
        value: 4.2,
        unit: 'seconds',
        change: -8.3,
        change_type: 'decrease',
        trend: [6, 5.8, 5.5, 5.2, 5.0, 4.8, 4.6, 4.4, 4.3, 4.2, 4.1, 4.0, 4.2],
        category: 'performance'
      },
      {
        id: '5',
        name: 'Template Rating',
        value: 4.8,
        unit: 'stars',
        change: 2.1,
        change_type: 'increase',
        trend: [4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.7, 4.8, 4.8, 4.8, 4.8, 4.8, 4.8],
        category: 'quality'
      },
      {
        id: '6',
        name: 'Active Users',
        value: 2341,
        unit: 'users',
        change: 18.9,
        change_type: 'increase',
        trend: [150, 160, 155, 170, 180, 175, 190, 185, 200, 195, 210, 205, 220],
        category: 'engagement'
      }
    ]);

    setUsageData([
      { date: '2024-11-01', views: 456, downloads: 123, unique_users: 89, generated_projects: 34 },
      { date: '2024-11-02', views: 512, downloads: 145, unique_users: 102, generated_projects: 41 },
      { date: '2024-11-03', views: 489, downloads: 134, unique_users: 95, generated_projects: 38 },
      { date: '2024-11-04', views: 678, downloads: 189, unique_users: 134, generated_projects: 52 },
      { date: '2024-11-05', views: 734, downloads: 203, unique_users: 156, generated_projects: 58 },
      { date: '2024-11-06', views: 612, downloads: 167, unique_users: 123, generated_projects: 45 },
      { date: '2024-11-07', views: 598, downloads: 178, unique_users: 134, generated_projects: 49 }
    ]);

    setGeographicData([
      { country: 'United States', users: 456, percentage: 32.1 },
      { country: 'Germany', users: 289, percentage: 20.3 },
      { country: 'United Kingdom', users: 234, percentage: 16.4 },
      { country: 'France', users: 167, percentage: 11.7 },
      { country: 'Canada', users: 123, percentage: 8.6 },
      { country: 'Netherlands', users: 89, percentage: 6.2 },
      { country: 'Others', users: 72, percentage: 4.7 }
    ]);

    setInsights([
      {
        id: '1',
        type: 'success',
        title: 'High Engagement Rate',
        description: 'Your template has a 68% higher engagement rate than similar templates',
        impact: 'high',
        actionable: false,
        timestamp: '2024-12-02T10:00:00Z'
      },
      {
        id: '2',
        type: 'optimization',
        title: 'Entity Complexity Optimization',
        description: 'Templates with fewer than 8 entities show 23% better performance',
        impact: 'medium',
        actionable: true,
        suggested_action: 'Consider consolidating similar entities or splitting complex ones',
        timestamp: '2024-12-02T09:30:00Z'
      },
      {
        id: '3',
        type: 'trend',
        title: 'Growing International Usage',
        description: 'International downloads increased by 45% this month',
        impact: 'medium',
        actionable: true,
        suggested_action: 'Consider adding internationalization features',
        timestamp: '2024-12-02T09:00:00Z'
      },
      {
        id: '4',
        type: 'issue',
        title: 'Generation Time Spike',
        description: 'Code generation took 15% longer on Dec 1st due to complex relationships',
        impact: 'low',
        actionable: true,
        suggested_action: 'Review relationship complexity and add indexes',
        timestamp: '2024-12-01T16:00:00Z'
      }
    ]);

    setPerformance([
      {
        metric: 'Code Generation Speed',
        current_value: 4.2,
        benchmark: 5.0,
        score: 84,
        status: 'good'
      },
      {
        metric: 'Template Complexity',
        current_value: entities.length,
        benchmark: 8,
        score: entities.length <= 8 ? 90 : Math.max(50, 90 - (entities.length - 8) * 10),
        status: entities.length <= 6 ? 'excellent' : entities.length <= 8 ? 'good' : entities.length <= 12 ? 'needs_improvement' : 'poor'
      },
      {
        metric: 'Field Optimization',
        current_value: entities.reduce((sum, e) => sum + e.fields.length, 0),
        benchmark: entities.length * 6,
        score: Math.min(100, (entities.reduce((sum, e) => sum + e.fields.length, 0) / (entities.length * 6)) * 100),
        status: 'good'
      },
      {
        metric: 'Relationship Efficiency',
        current_value: relationships.length,
        benchmark: Math.floor(entities.length * 1.5),
        score: Math.min(100, Math.max(0, 100 - Math.abs(relationships.length - Math.floor(entities.length * 1.5)) * 10)),
        status: 'excellent'
      }
    ]);

    setIsLoading(false);
  };

  const getMetricIcon = (category: string) => {
    switch (category) {
      case 'usage':
        return <Eye className="h-5 w-5" />;
      case 'performance':
        return <Zap className="h-5 w-5" />;
      case 'engagement':
        return <Users className="h-5 w-5" />;
      case 'quality':
        return <Star className="h-5 w-5" />;
      default:
        return <BarChart3 className="h-5 w-5" />;
    }
  };

  const getChangeIcon = (changeType: string) => {
    switch (changeType) {
      case 'increase':
        return <ArrowUp className="h-4 w-4 text-green-500" />;
      case 'decrease':
        return <ArrowDown className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'optimization':
        return <Target className="h-5 w-5 text-blue-500" />;
      case 'trend':
        return <TrendingUp className="h-5 w-5 text-purple-500" />;
      case 'issue':
        return <AlertCircle className="h-5 w-5 text-orange-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'text-green-700 bg-green-100';
      case 'good':
        return 'text-blue-700 bg-blue-100';
      case 'needs_improvement':
        return 'text-yellow-700 bg-yellow-100';
      case 'poor':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const formatNumber = (num: number, unit?: string) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M${unit ? ` ${unit}` : ''}`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K${unit ? ` ${unit}` : ''}`;
    }
    return `${num}${unit ? ` ${unit}` : ''}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Template Analytics</h2>
            <p className="text-gray-600 mt-1">Performance insights and usage analytics for {domainConfig.title}</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
            
            <button
              onClick={loadAnalyticsData}
              disabled={isLoading}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
            >
              <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'usage', label: 'Usage Analytics', icon: Activity },
              { id: 'performance', label: 'Performance', icon: Zap },
              { id: 'insights', label: 'AI Insights', icon: Target }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading analytics data...</p>
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Key Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {metrics.map(metric => (
                      <div key={metric.id} className="bg-white border border-gray-200 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div className={`p-2 rounded-lg ${{
                            usage: 'bg-blue-100 text-blue-600',
                            performance: 'bg-green-100 text-green-600',
                            engagement: 'bg-purple-100 text-purple-600',
                            quality: 'bg-yellow-100 text-yellow-600'
                          }[metric.category]}`}>
                            {getMetricIcon(metric.category)}
                          </div>
                          <div className="flex items-center space-x-1">
                            {getChangeIcon(metric.change_type)}
                            <span className={`text-sm font-medium ${
                              metric.change_type === 'increase' ? 'text-green-600' :
                              metric.change_type === 'decrease' ? 'text-red-600' : 'text-gray-600'
                            }`}>
                              {Math.abs(metric.change).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="mb-4">
                          <div className="text-2xl font-bold text-gray-900">
                            {formatNumber(metric.value, metric.unit === 'views' || metric.unit === 'downloads' || metric.unit === 'projects' || metric.unit === 'users' ? '' : metric.unit)}
                          </div>
                          <div className="text-sm text-gray-600 capitalize">{metric.name}</div>
                        </div>
                        
                        {/* Mini trend chart */}
                        <div className="h-16 flex items-end space-x-1">
                          {metric.trend.map((point, index) => (
                            <div
                              key={index}
                              className="flex-1 bg-blue-200 rounded-t"
                              style={{
                                height: `${(point / Math.max(...metric.trend)) * 100}%`
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Geographic Distribution */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Geographic Distribution</h3>
                      <div className="space-y-3">
                        {geographicData.map(country => (
                          <div key={country.country} className="flex items-center justify-between">
                            <span className="text-gray-900">{country.country}</span>
                            <div className="flex items-center space-x-3">
                              <div className="w-32 bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-blue-500 h-2 rounded-full"
                                  style={{ width: `${country.percentage}%` }}
                                />
                              </div>
                              <span className="text-sm text-gray-600 w-12 text-right">
                                {country.percentage}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Usage Trends</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <Eye className="h-5 w-5 text-blue-600" />
                            <span className="font-medium text-blue-900">Peak Usage</span>
                          </div>
                          <span className="text-blue-800">Wed 2-4 PM</span>
                        </div>
                        
                        <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <Download className="h-5 w-5 text-green-600" />
                            <span className="font-medium text-green-900">Top Download Day</span>
                          </div>
                          <span className="text-green-800">Thursday</span>
                        </div>
                        
                        <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <Users className="h-5 w-5 text-purple-600" />
                            <span className="font-medium text-purple-900">Avg. Session</span>
                          </div>
                          <span className="text-purple-800">8.5 minutes</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'usage' && (
                <div className="space-y-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Usage Statistics</h3>
                    
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Views</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Downloads</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unique Users</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generated Projects</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {usageData.map((data, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                {formatDate(data.date)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{data.views}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{data.downloads}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{data.unique_users}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{data.generated_projects}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Usage Patterns */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 mb-4">Most Used Features</h4>
                      <div className="space-y-3">
                        {[
                          { feature: 'Entity Designer', usage: 89 },
                          { feature: 'Code Generation', usage: 76 },
                          { feature: 'Relationship Mapping', usage: 64 },
                          { feature: 'Preview Mode', usage: 52 }
                        ].map(item => (
                          <div key={item.feature} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">{item.feature}</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-blue-500 h-2 rounded-full"
                                  style={{ width: `${item.usage}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500 w-8">{item.usage}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 mb-4">Popular Export Formats</h4>
                      <div className="space-y-3">
                        {[
                          { format: 'React + TypeScript', count: 1247, color: 'bg-blue-500' },
                          { format: 'Node.js + Express', count: 856, color: 'bg-green-500' },
                          { format: 'Python + FastAPI', count: 634, color: 'bg-yellow-500' },
                          { format: 'Vue.js + Nuxt', count: 423, color: 'bg-purple-500' }
                        ].map(item => (
                          <div key={item.format} className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <div className={`w-3 h-3 rounded-full ${item.color}`} />
                              <span className="text-sm text-gray-700">{item.format}</span>
                            </div>
                            <span className="text-sm font-medium text-gray-900">{item.count}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 mb-4">User Engagement</h4>
                      <div className="space-y-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">68%</div>
                          <div className="text-sm text-gray-600">Completion Rate</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">8.5</div>
                          <div className="text-sm text-gray-600">Avg. Session (min)</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">34%</div>
                          <div className="text-sm text-gray-600">Return Users</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'performance' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {performance.map((perf, index) => (
                      <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="font-medium text-gray-900">{perf.metric}</h4>
                          <span className={`px-2 py-1 text-xs rounded ${getStatusColor(perf.status)}`}>
                            {perf.status.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <div className="mb-4">
                          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                            <span>Current: {perf.current_value}</span>
                            <span>Benchmark: {perf.benchmark}</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                              className={`h-3 rounded-full ${
                                perf.score >= 90 ? 'bg-green-500' :
                                perf.score >= 70 ? 'bg-blue-500' :
                                perf.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${Math.min(100, perf.score)}%` }}
                            />
                          </div>
                          <div className="text-right mt-1">
                            <span className="text-sm font-medium text-gray-900">{perf.score}/100</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Template Architecture Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <Database className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-blue-900">{entities.length}</div>
                        <div className="text-sm text-blue-700">Total Entities</div>
                        <div className="text-xs text-blue-600 mt-1">
                          {entities.length <= 6 ? 'Optimal' : entities.length <= 10 ? 'Good' : 'Consider simplifying'}
                        </div>
                      </div>
                      
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <Code className="h-8 w-8 text-green-600 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-green-900">
                          {entities.reduce((sum, e) => sum + e.fields.length, 0)}
                        </div>
                        <div className="text-sm text-green-700">Total Fields</div>
                        <div className="text-xs text-green-600 mt-1">
                          Avg {Math.round(entities.reduce((sum, e) => sum + e.fields.length, 0) / entities.length)} per entity
                        </div>
                      </div>
                      
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <Share2 className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-purple-900">{relationships.length}</div>
                        <div className="text-sm text-purple-700">Relationships</div>
                        <div className="text-xs text-purple-600 mt-1">
                          {relationships.length / entities.length < 2 ? 'Well balanced' : 'High complexity'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'insights' && (
                <div className="space-y-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">AI-Powered Insights</h3>
                    <p className="text-gray-600 mb-6">
                      Our AI analyzes your template usage patterns and provides actionable recommendations
                    </p>
                    
                    <div className="space-y-4">
                      {insights.map(insight => (
                        <div key={insight.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-start space-x-3">
                              {getInsightIcon(insight.type)}
                              <div>
                                <h4 className="font-medium text-gray-900">{insight.title}</h4>
                                <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 text-xs rounded ${
                                insight.impact === 'high' ? 'bg-red-100 text-red-700' :
                                insight.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-green-100 text-green-700'
                              }`}>
                                {insight.impact} impact
                              </span>
                              <span className="text-xs text-gray-500">
                                {new Date(insight.timestamp).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                          
                          {insight.actionable && insight.suggested_action && (
                            <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                              <div className="flex items-start space-x-2">
                                <Target className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                                <div>
                                  <div className="text-sm font-medium text-blue-900">Suggested Action:</div>
                                  <div className="text-sm text-blue-800">{insight.suggested_action}</div>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Recommendation Cards */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200 rounded-lg p-6">
                      <div className="flex items-center space-x-3 mb-4">
                        <TrendingUp className="h-6 w-6 text-blue-600" />
                        <h4 className="font-semibold text-blue-900">Growth Opportunities</h4>
                      </div>
                      <ul className="space-y-2 text-sm text-blue-800">
                        <li>• Add mobile-responsive templates for 23% growth potential</li>
                        <li>• Implement dark mode support (requested by 34% of users)</li>
                        <li>• Create template variations for different project sizes</li>
                      </ul>
                    </div>
                    
                    <div className="bg-gradient-to-br from-green-50 to-emerald-100 border border-green-200 rounded-lg p-6">
                      <div className="flex items-center space-x-3 mb-4">
                        <CheckCircle className="h-6 w-6 text-green-600" />
                        <h4 className="font-semibold text-green-900">Strengths to Leverage</h4>
                      </div>
                      <ul className="space-y-2 text-sm text-green-800">
                        <li>• High user retention (68% above average)</li>
                        <li>• Excellent performance metrics</li>
                        <li>• Strong international adoption</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplateAnalytics;