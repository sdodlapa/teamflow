/**
 * Breadcrumb Hook
 * Provides breadcrumb navigation for the application
 */

import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';

export interface BreadcrumbItem {
  label: string;
  path: string;
  icon?: string;
}

interface BreadcrumbConfig {
  title: string;
  icon?: string;
}

const routeConfig: Record<string, BreadcrumbConfig> = {
  '/dashboard': { title: 'Dashboard', icon: '🏠' },
  '/tasks': { title: 'Tasks', icon: '✅' },
  '/projects': { title: 'Projects', icon: '📁' },
  '/calendar': { title: 'Calendar', icon: '📅' },
  '/analytics': { title: 'Analytics', icon: '�' },
  '/settings': { title: 'Settings', icon: '⚙️' },
  '/profile': { title: 'Profile', icon: '👤' },
  '/demo': { title: 'Demo', icon: '🧪' },
  '/demo/error-handling': { title: 'Error Handling', icon: '🐛' },
};

export const useBreadcrumbs = (): BreadcrumbItem[] => {
  const location = useLocation();

  return useMemo(() => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [];

    // Always start with Home (Dashboard)
    breadcrumbs.push({
      label: 'Home',
      path: '/dashboard',
      icon: '🏠'
    });

    // Build breadcrumbs from path segments
    let currentPath = '';
    
    pathSegments.forEach((segment) => {
      currentPath += `/${segment}`;
      
      // Check if we have a direct match in routeConfig
      const config = routeConfig[currentPath];
      if (config) {
        breadcrumbs.push({
          label: config.title,
          path: currentPath,
          icon: config.icon
        });
      } else {
        // Handle dynamic routes (like /projects/123)
        const dynamicRoute = Object.keys(routeConfig).find(route => {
          const routeSegments = route.split('/').filter(Boolean);
          if (routeSegments.length !== pathSegments.length) return false;
          
          return routeSegments.every((routeSegment, i) => 
            routeSegment.startsWith(':') || routeSegment === pathSegments[i]
          );
        });
        
        if (dynamicRoute) {
          const config = routeConfig[dynamicRoute];
          let label = config.title;
          
          // For specific ID routes, try to make the label more descriptive
          if (dynamicRoute.includes(':id')) {
            const id = pathSegments[pathSegments.indexOf(segment)];
            if (dynamicRoute.startsWith('/projects/')) {
              label = `Project ${id}`;
            } else if (dynamicRoute.startsWith('/tasks/')) {
              label = `Task ${id}`;
            }
          }
          
          breadcrumbs.push({
            label,
            path: currentPath,
            icon: config.icon
          });
        } else {
          // Fallback for unknown routes
          breadcrumbs.push({
            label: segment.charAt(0).toUpperCase() + segment.slice(1),
            path: currentPath,
            icon: '📄'
          });
        }
      }
    });

    return breadcrumbs;
  }, [location.pathname]);
};

export default useBreadcrumbs;