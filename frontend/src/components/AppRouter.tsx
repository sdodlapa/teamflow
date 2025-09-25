import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Dashboard from './Dashboard';
import TaskManagement from './TaskManagement';
import ProjectManagement from './ProjectManagement';
import Login from './Login';
import { TemplateBuilderPage } from '../pages/TemplateBuilderPage';
import TemplateLibraryPage from '../pages/TemplateLibraryPage';
import TemplateMarketplacePage from '../pages/TemplateMarketplacePage';
import BackendIntegrationTest from './BackendIntegrationTest';

type ViewType = 'dashboard' | 'tasks' | 'projects' | 'templates' | 'template-library' | 'template-marketplace' | 'integration-test';

const AppRouter: React.FC = () => {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login />;
  }

  // Main authenticated app
  return (
    <>
      <nav className="app-nav">
        <div className="nav-brand">
          <span className="nav-logo">🚀</span>
          <span className="nav-title">TeamFlow</span>
        </div>
        
        <div className="nav-links">
          <button
            className={`nav-link ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={`nav-link ${currentView === 'projects' ? 'active' : ''}`}
            onClick={() => setCurrentView('projects')}
          >
            📁 Projects
          </button>
          <button
            className={`nav-link ${currentView === 'tasks' ? 'active' : ''}`}
            onClick={() => setCurrentView('tasks')}
          >
            📋 Tasks
          </button>
          <button
            className={`nav-link ${currentView === 'templates' ? 'active' : ''}`}
            onClick={() => setCurrentView('templates')}
          >
            🛠️ Template Builder
          </button>
          <button
            className={`nav-link ${currentView === 'template-library' ? 'active' : ''}`}
            onClick={() => setCurrentView('template-library')}
          >
            📚 Template Library
          </button>
          <button
            className={`nav-link ${currentView === 'template-marketplace' ? 'active' : ''}`}
            onClick={() => setCurrentView('template-marketplace')}
          >
            🏪 Marketplace
          </button>
          <button
            className={`nav-link ${currentView === 'integration-test' ? 'active' : ''}`}
            onClick={() => setCurrentView('integration-test')}
          >
            🔧 Integration Test
          </button>
        </div>

        <div className="nav-user">
          <div className="user-info">
            <div className="user-avatar">
              {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            </div>
            <div className="user-details">
              <span className="user-name">
                {user?.first_name && user?.last_name 
                  ? `${user.first_name} ${user.last_name}` 
                  : user?.username || 'User'
                }
              </span>
              <span className="user-email">{user?.email}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={logout}>
            🚪 Logout
          </button>
        </div>
      </nav>

      <main className="app-main">
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'projects' && <ProjectManagement />}
        {currentView === 'tasks' && <TaskManagement />}
        {currentView === 'templates' && <TemplateBuilderPage />}
        {currentView === 'template-library' && <TemplateLibraryPage />}
        {currentView === 'template-marketplace' && <TemplateMarketplacePage />}
        {currentView === 'integration-test' && <BackendIntegrationTest />}
      </main>
    </>
  );
};

export default AppRouter;