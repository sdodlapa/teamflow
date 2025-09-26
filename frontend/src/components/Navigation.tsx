/**
 * Navigation Component
 * Enhanced navigation with React Router, active states, and user menu
 */

import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ChevronDown, LogOut, Settings, User, Bell } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { CollaborationStatus } from './collaboration';

interface NavigationItem {
  name: string;
  path: string;
  icon: string;
  description?: string;
}

const navigationItems: NavigationItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: '📊', description: 'Overview and metrics' },
  { name: 'Tasks', path: '/tasks', icon: '📋', description: 'Task management' },
  { name: 'Projects', path: '/projects', icon: '📁', description: 'Project collaboration' },
  { name: 'Templates', path: '/templates', icon: '📦', description: 'Template library' },
  { name: 'Calendar', path: '/calendar', icon: '📅', description: 'Schedule and events' },
  { name: 'Analytics', path: '/analytics', icon: '📈', description: 'Performance insights' },
  { name: 'Collaboration', path: '/collaboration-demo', icon: '👥', description: 'Real-time collaboration demo' },
];

const Navigation: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string): boolean => {
    if (path === '/dashboard') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname.startsWith(path);
  };

  const getUserInitials = (): string => {
    if (user?.full_name) {
      return user.full_name
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    return (user?.name || user?.email || 'U').charAt(0).toUpperCase();
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and Main Navigation */}
          <div className="flex items-center">
            {/* Logo */}
            <div className="flex-shrink-0">
              <Link to="/dashboard" className="flex items-center">
                <span className="text-2xl font-bold text-blue-600 hover:text-blue-700 transition-colors">
                  🚀 TeamFlow
                </span>
              </Link>
            </div>
            
            {/* Main Navigation Links */}
            <div className="hidden md:ml-10 md:flex md:items-baseline md:space-x-2">
              {navigationItems.map((item) => {
                const active = isActive(item.path);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      active
                        ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-500'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                    title={item.description}
                  >
                    <span className="mr-2">{item.icon}</span>
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* User Menu and Actions */}
          <div className="flex items-center">
            {/* Real-time Collaboration Status */}
            <div className="mr-3">
              <CollaborationStatus />
            </div>
            
            {/* Notifications (placeholder) */}
            <button
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-md transition-colors mr-2"
              title="Notifications"
            >
              <Bell size={20} />
            </button>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center text-sm bg-white rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 p-2 transition-colors"
                id="user-menu-button"
                aria-expanded={showUserMenu}
                aria-haspopup="true"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    {getUserInitials()}
                  </div>
                  <div className="hidden md:flex md:flex-col md:items-start md:text-left">
                    <div className="text-sm font-medium text-gray-900">
                      {user?.full_name || user?.name || 'User'}
                    </div>
                    <div className="text-xs text-gray-500 truncate max-w-32">
                      {user?.email}
                    </div>
                  </div>
                  <ChevronDown 
                    className={`ml-2 w-4 h-4 text-gray-400 transition-transform ${
                      showUserMenu ? 'rotate-180' : ''
                    }`} 
                  />
                </div>
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <div
                  className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu-button"
                >
                  <div className="py-1" role="none">
                    {/* User Info Header */}
                    <div className="px-4 py-3 border-b border-gray-100">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                          {getUserInitials()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-gray-900 truncate">
                            {user?.full_name || user?.name || 'User'}
                          </div>
                          <div className="text-sm text-gray-500 truncate">
                            {user?.email}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Menu Items */}
                    <Link
                      to="/profile"
                      className="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                      role="menuitem"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <User className="mr-3 w-4 h-4 text-gray-400 group-hover:text-gray-500" />
                      Profile Settings
                    </Link>

                    <Link
                      to="/settings"
                      className="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                      role="menuitem"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <Settings className="mr-3 w-4 h-4 text-gray-400 group-hover:text-gray-500" />
                      Account Settings
                    </Link>

                    <div className="border-t border-gray-100"></div>

                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        handleLogout();
                      }}
                      className="group flex w-full items-center px-4 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600"
                      role="menuitem"
                    >
                      <LogOut className="mr-3 w-4 h-4 text-gray-400 group-hover:text-red-500" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation (placeholder for future implementation) */}
      <div className="md:hidden border-t border-gray-200 bg-gray-50 px-4 py-3">
        <div className="flex space-x-1 overflow-x-auto">
          {navigationItems.map((item) => {
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap ${
                  active
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Click outside handler */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </nav>
  );
};

export default Navigation;