import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import PrivateRoute from '../components/PrivateRoute';
import LoginPage from '../pages/Login';
import RegisterPage from '../pages/Register';
import Dashboard from '../pages/Dashboard';
import Tasks from '../pages/Tasks';
import Projects from '../pages/Projects';
import Calendar from '../pages/Calendar';
import Analytics from '../pages/Analytics';
import Settings from '../pages/Settings';
import Profile from '../pages/Profile';
import TemplateLibrary from '../pages/TemplateLibrary';
import DomainConfigurationDetails from '../pages/DomainConfigurationDetails';
import TemplateCreation from '../pages/TemplateCreation';
import ErrorHandlingDemo from '../pages/ErrorHandlingDemo';
import DataManagementDemo from '../pages/DataManagementDemo';
import NotFound from '../pages/NotFound';

// Create the router configuration
const router = createBrowserRouter([
  // Public routes
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  
  // Private routes wrapped in authentication
  {
    path: '/',
    element: (
      <PrivateRoute>
        <Dashboard />
      </PrivateRoute>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <PrivateRoute>
        <Dashboard />
      </PrivateRoute>
    ),
  },
  {
    path: '/tasks',
    element: (
      <PrivateRoute>
        <Tasks />
      </PrivateRoute>
    ),
  },
  {
    path: '/projects',
    element: (
      <PrivateRoute>
        <Projects />
      </PrivateRoute>
    ),
  },
  {
    path: '/calendar',
    element: (
      <PrivateRoute>
        <Calendar />
      </PrivateRoute>
    ),
  },
  {
    path: '/analytics',
    element: (
      <PrivateRoute>
        <Analytics />
      </PrivateRoute>
    ),
  },
  {
    path: '/settings',
    element: (
      <PrivateRoute>
        <Settings />
      </PrivateRoute>
    ),
  },
  {
    path: '/profile',
    element: (
      <PrivateRoute>
        <Profile />
      </PrivateRoute>
    ),
  },
  {
    path: '/templates',
    element: (
      <PrivateRoute>
        <TemplateLibrary />
      </PrivateRoute>
    ),
  },
  {
    path: '/templates/domain/:domainId',
    element: (
      <PrivateRoute>
        <DomainConfigurationDetails />
      </PrivateRoute>
    ),
  },
  {
    path: '/templates/create',
    element: (
      <PrivateRoute>
        <TemplateCreation />
      </PrivateRoute>
    ),
  },
  {
    path: '/demo/error-handling',
    element: (
      <PrivateRoute>
        <ErrorHandlingDemo />
      </PrivateRoute>
    ),
  },
  {
    path: '/demo/data-management',
    element: (
      <PrivateRoute>
        <DataManagementDemo />
      </PrivateRoute>
    ),
  },
  
  // Catch-all route for 404
  {
    path: '*',
    element: <NotFound />,
  },
]);

/**
 * Main app router component with auth provider
 */
const AppRouter: React.FC = () => {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
};

export default AppRouter;