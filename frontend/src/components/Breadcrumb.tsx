/**
 * Breadcrumb Navigation Component
 * Provides breadcrumb navigation with React Router integration
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { useBreadcrumbs, BreadcrumbItem } from '../hooks/useBreadcrumbs';

interface BreadcrumbProps {
  className?: string;
  maxItems?: number;
  showHomeIcon?: boolean;
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({
  className = '',
  maxItems = 4,
  showHomeIcon = true
}) => {
  const location = useLocation();
  const breadcrumbs = useBreadcrumbs();

  // Don't show breadcrumbs on the home page
  if (location.pathname === '/dashboard' || location.pathname === '/') {
    return null;
  }

  // Limit breadcrumbs if too many
  const displayBreadcrumbs = breadcrumbs.length > maxItems 
    ? [
        breadcrumbs[0], // Always show home
        { label: '...', path: '', icon: '' } as BreadcrumbItem,
        ...breadcrumbs.slice(-(maxItems - 2))
      ]
    : breadcrumbs;

  return (
    <nav className={`flex ${className}`} aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-3">
        {displayBreadcrumbs.map((item, index) => {
          const isLast = index === displayBreadcrumbs.length - 1;
          const isEllipsis = item.label === '...';
          
          return (
            <li key={`${item.path}-${index}`} className="inline-flex items-center">
              {index > 0 && (
                <ChevronRight className="w-4 h-4 text-gray-400 mx-1" />
              )}
              
              {isEllipsis ? (
                <span className="text-gray-500 text-sm">...</span>
              ) : isLast ? (
                <span className="flex items-center text-sm font-medium text-gray-500">
                  {showHomeIcon && item.icon && (
                    <span className="mr-2">{item.icon}</span>
                  )}
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.path}
                  className="flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
                >
                  {showHomeIcon && item.path === '/dashboard' ? (
                    <Home className="w-4 h-4 mr-2" />
                  ) : showHomeIcon && item.icon ? (
                    <span className="mr-2">{item.icon}</span>
                  ) : null}
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumb;