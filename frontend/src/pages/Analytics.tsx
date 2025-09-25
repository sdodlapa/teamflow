/**
 * Analytics Page Component
 * Performance insights and analytics dashboard (placeholder for future implementation)
 */

import React from 'react';
import Layout from '../components/Layout';
import { BarChart3, TrendingUp, Users, Clock, Target } from 'lucide-react';

const Analytics: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <BarChart3 className="mr-3 text-blue-600" size={32} />
              Analytics
            </h1>
            <p className="text-gray-600 mt-1">
              Performance insights and productivity analytics for your team
            </p>
          </div>
        </div>

        {/* Analytics Placeholder */}
        <div className="bg-white border border-gray-200 rounded-lg p-8">
          <div className="text-center py-16">
            <BarChart3 size={64} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analytics Dashboard Coming Soon</h3>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
              Comprehensive analytics and insights will help you track team productivity, project progress, 
              and identify optimization opportunities.
            </p>
            
            {/* Feature Preview Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="text-blue-600" size={24} />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Performance Trends</h4>
                <p className="text-sm text-gray-600">Track productivity trends and identify patterns over time</p>
              </div>
              
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Users className="text-green-600" size={24} />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Team Analytics</h4>
                <p className="text-sm text-gray-600">Analyze team performance and workload distribution</p>
              </div>
              
              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="text-purple-600" size={24} />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Time Tracking</h4>
                <p className="text-sm text-gray-600">Monitor time spent on tasks and projects for better planning</p>
              </div>
              
              <div className="text-center p-6 bg-orange-50 rounded-lg">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Target className="text-orange-600" size={24} />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Goal Tracking</h4>
                <p className="text-sm text-gray-600">Set and monitor progress toward team and project goals</p>
              </div>
            </div>

            {/* Sample Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg">
                <div className="text-3xl font-bold">85%</div>
                <div className="text-blue-100 text-sm">Team Productivity</div>
                <div className="text-blue-200 text-xs mt-1">↑ 12% from last month</div>
              </div>
              
              <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-lg">
                <div className="text-3xl font-bold">32</div>
                <div className="text-green-100 text-sm">Completed Tasks</div>
                <div className="text-green-200 text-xs mt-1">This week</div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-lg">
                <div className="text-3xl font-bold">4.2h</div>
                <div className="text-purple-100 text-sm">Avg. Task Time</div>
                <div className="text-purple-200 text-xs mt-1">↓ 0.8h improved</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Analytics;