/**
 * Not Found (404) Page Component
 * Enhanced 404 page with navigation options
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft, Map } from 'lucide-react';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full text-center">
        {/* 404 Illustration */}
        <div className="mb-8">
          <div className="text-8xl font-bold text-blue-600 mb-4">404</div>
          <div className="text-6xl mb-4">🔍</div>
        </div>

        {/* Error Message */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Page Not Found</h1>
          <p className="text-gray-600 text-lg mb-6">
            Oops! The page you're looking for doesn't exist or may have been moved.
          </p>
        </div>

        {/* Navigation Options */}
        <div className="space-y-4">
          <Link
            to="/dashboard"
            className="w-full flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Home className="mr-2" size={20} />
            Go to Dashboard
          </Link>

          <button
            onClick={() => window.history.back()}
            className="w-full flex items-center justify-center px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="mr-2" size={20} />
            Go Back
          </button>
        </div>

        {/* Quick Links */}
        <div className="mt-12">
          <h3 className="text-sm font-medium text-gray-900 mb-4">Or try these popular pages:</h3>
          <div className="grid grid-cols-2 gap-3">
            <Link
              to="/tasks"
              className="flex items-center justify-center px-4 py-2 text-sm text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
            >
              📋 Tasks
            </Link>
            <Link
              to="/projects"
              className="flex items-center justify-center px-4 py-2 text-sm text-green-600 bg-green-50 rounded-md hover:bg-green-100 transition-colors"
            >
              📁 Projects
            </Link>
            <Link
              to="/calendar"
              className="flex items-center justify-center px-4 py-2 text-sm text-purple-600 bg-purple-50 rounded-md hover:bg-purple-100 transition-colors"
            >
              📅 Calendar
            </Link>
            <Link
              to="/analytics"
              className="flex items-center justify-center px-4 py-2 text-sm text-orange-600 bg-orange-50 rounded-md hover:bg-orange-100 transition-colors"
            >
              📈 Analytics
            </Link>
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-12 p-6 bg-white rounded-lg border border-gray-200">
          <div className="flex items-center justify-center mb-3">
            <Map className="text-blue-600" size={24} />
          </div>
          <h3 className="text-sm font-medium text-gray-900 mb-2">Need Help?</h3>
          <p className="text-xs text-gray-600 mb-4">
            If you think this is an error, please contact support or check the URL for typos.
          </p>
          <div className="flex justify-center space-x-4 text-xs">
            <a href="#" className="text-blue-600 hover:text-blue-700">
              Contact Support
            </a>
            <span className="text-gray-300">•</span>
            <a href="#" className="text-blue-600 hover:text-blue-700">
              Report Issue
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;