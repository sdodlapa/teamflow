/**
 * Analytics Page Component
 * Performance insights and analytics dashboard with real-time data
 */

import React, { useState } from 'react';
import Layout from '../components/Layout';
import { BarChart3, TestTube } from 'lucide-react';
import { AnalyticsDashboard } from '../components/Analytics/AnalyticsDashboard';
import { AnalyticsTest } from '../components/AnalyticsTest';

const Analytics: React.FC = () => {
  const [showTest, setShowTest] = useState(false);

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <BarChart3 className="mr-3 text-blue-600" size={32} />
              Analytics Dashboard
            </h1>
            <p className="text-gray-600 mt-1">
              Real-time performance insights and productivity analytics for your team
            </p>
          </div>
          <button
            onClick={() => setShowTest(!showTest)}
            className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
          >
            <TestTube className="w-4 h-4 mr-2" />
            {showTest ? 'Hide' : 'Show'} API Test
          </button>
        </div>

        {/* API Test Component */}
        {showTest && (
          <div className="mb-8">
            <AnalyticsTest />
          </div>
        )}

        {/* Analytics Dashboard */}
        <AnalyticsDashboard />
      </div>
    </Layout>
  );
};

export default Analytics;