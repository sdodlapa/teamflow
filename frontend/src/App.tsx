import { useState } from 'react';
import Dashboard from './components/Dashboard';
import TaskManagement from './components/TaskManagement';
import ProjectManagement from './components/ProjectManagement';
import Login from './components/Login';
import { TemplateBuilderPage } from './pages/TemplateBuilderPage';
import TemplateLibraryPage from './pages/TemplateLibraryPage';
import TemplateMarketplacePage from './pages/TemplateMarketplacePage';
import './App.css';

interface User {
  id: number;
  name: string;
  email: string;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState<'dashboard' | 'tasks' | 'projects' | 'templates' | 'template-library' | 'template-marketplace'>('dashboard');
  const [user, setUser] = useState<User | null>(null);

  const handleLogin = (credentials: { email: string; password: string }) => {
    // Mock authentication - in a real app, this would make an API call
    console.log('Login attempt:', credentials);
    
    // Simulate successful login
    setUser({
      id: 1,
      name: 'John Doe',
      email: credentials.email
    });
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setCurrentView('dashboard');
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app">
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
        </div>

        <div className="nav-user">
          <div className="user-info">
            <div className="user-avatar">
              {user?.name.charAt(0) || 'U'}
            </div>
            <div className="user-details">
              <span className="user-name">{user?.name}</span>
              <span className="user-email">{user?.email}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
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
      </main>
    </div>
  );
}

export default App;