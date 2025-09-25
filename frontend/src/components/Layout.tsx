/**
 * Layout Component
 * Enhanced layout with improved navigation and breadcrumb system
 */

import React from 'react';
import Navigation from './Navigation';
import Breadcrumb from './Breadcrumb';

interface LayoutProps {
  children: React.ReactNode;
  showBreadcrumbs?: boolean;
}

const Layout: React.FC<LayoutProps> = ({ children, showBreadcrumbs = true }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Enhanced Navigation */}
      <Navigation />

      {/* Breadcrumb Navigation */}
      {showBreadcrumbs && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <Breadcrumb />
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1">{children}</main>
    </div>
  );
};

export default Layout;