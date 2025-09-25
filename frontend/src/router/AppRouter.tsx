import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import PrivateRoute from '../components/PrivateRoute';
import LoginPage from '../pages/Login';
import RegisterPage from '../pages/Register';

// Placeholder components - replace with actual components when they exist
const PlaceholderPage: React.FC<{ title: string }> = ({ title }) => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">{title}</h1>
      <p className="text-gray-600">This page is under development</p>
    </div>
  </div>
);

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
        <PlaceholderPage title="Dashboard" />
      </PrivateRoute>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <PrivateRoute>
        <PlaceholderPage title="Dashboard" />
      </PrivateRoute>
    ),
  },
  {
    path: '/tasks',
    element: (
      <PrivateRoute>
        <PlaceholderPage title="Tasks" />
      </PrivateRoute>
    ),
  },
  {
    path: '/projects',
    element: (
      <PrivateRoute>
        <PlaceholderPage title="Projects" />
      </PrivateRoute>
    ),
  },
  {
    path: '/calendar',
    element: (
      <PrivateRoute>
        <PlaceholderPage title="Calendar" />
      </PrivateRoute>
    ),
  },
  {
    path: '/analytics',
    element: (
      <PrivateRoute>
        <PlaceholderPage title="Analytics" />
      </PrivateRoute>
    ),
  },
  {
    path: '/settings',
    element: (
      <PrivateRoute>
        <PlaceholderPage title="Settings" />
      </PrivateRoute>
    ),
  },
  {
    path: '/profile',
    element: (
      <PrivateRoute>
        <PlaceholderPage title="Profile" />
      </PrivateRoute>
    ),
  },
  
  // Catch-all route
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
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