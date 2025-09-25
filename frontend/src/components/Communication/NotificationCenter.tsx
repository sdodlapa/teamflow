import React, { useState, useEffect } from 'react';
import {
  Bell, BellOff, Settings, Search, MoreVertical,
  Check, X, Mail, MessageSquare, AlertTriangle,
  CheckCircle, Info, User, Activity,
  Trash2, Archive, Volume2, VolumeX, Eye,
  EyeOff, Star, StarOff, Pin, PinOff
} from 'lucide-react';
import './NotificationCenter.css';

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'message' | 'system';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  isArchived: boolean;
  isPinned: boolean;
  isStarred: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: 'task' | 'project' | 'user' | 'system' | 'reminder' | 'social';
  sender?: {
    id: string;
    name: string;
    avatar?: string;
    email: string;
  };
  actionUrl?: string;
  actionText?: string;
  metadata?: {
    taskId?: string;
    projectId?: string;
    userId?: string;
    dueDate?: string;
    mentions?: string[];
  };
}

interface NotificationSettings {
  emailNotifications: boolean;
  pushNotifications: boolean;
  browserNotifications: boolean;
  soundEnabled: boolean;
  categories: {
    tasks: boolean;
    projects: boolean;
    users: boolean;
    system: boolean;
    reminders: boolean;
    social: boolean;
  };
  priority: {
    low: boolean;
    medium: boolean;
    high: boolean;
    urgent: boolean;
  };
  quietHours: {
    enabled: boolean;
    startTime: string;
    endTime: string;
  };
}

interface NotificationCenterProps {
  userId?: string;
  onClose?: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  userId,
  onClose
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filteredNotifications, setFilteredNotifications] = useState<Notification[]>([]);
  const [activeTab, setActiveTab] = useState<'all' | 'unread' | 'archived' | 'starred'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [filterPriority, setFilterPriority] = useState<string>('');
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<NotificationSettings>({
    emailNotifications: true,
    pushNotifications: true,
    browserNotifications: true,
    soundEnabled: true,
    categories: {
      tasks: true,
      projects: true,
      users: true,
      system: true,
      reminders: true,
      social: true
    },
    priority: {
      low: true,
      medium: true,
      high: true,
      urgent: true
    },
    quietHours: {
      enabled: false,
      startTime: '22:00',
      endTime: '08:00'
    }
  });
  const [isLoading, setIsLoading] = useState(true);

  // Mock notification data
  const generateMockNotifications = (): Notification[] => {
    return [
      {
        id: 'notif-1',
        type: 'warning',
        title: 'Task Deadline Approaching',
        message: 'The task "Implement user authentication" is due in 2 hours. Please complete it soon.',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        isRead: false,
        isArchived: false,
        isPinned: true,
        isStarred: false,
        priority: 'high',
        category: 'task',
        sender: {
          id: 'system',
          name: 'TeamFlow System',
          email: 'system@teamflow.com'
        },
        actionUrl: '/tasks/task-123',
        actionText: 'View Task',
        metadata: {
          taskId: 'task-123',
          projectId: 'project-456',
          dueDate: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString()
        }
      },
      {
        id: 'notif-2',
        type: 'message',
        title: 'New Message from John Doe',
        message: 'Hey! Can you review the latest project updates? I\'ve made some changes to the design specs.',
        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        isRead: false,
        isArchived: false,
        isPinned: false,
        isStarred: true,
        priority: 'medium',
        category: 'social',
        sender: {
          id: 'user-1',
          name: 'John Doe',
          avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
          email: 'john.doe@company.com'
        },
        actionUrl: '/messages/conv-789',
        actionText: 'Reply',
        metadata: {
          userId: 'user-1',
          mentions: ['@currentUser']
        }
      },
      {
        id: 'notif-3',
        type: 'success',
        title: 'Project Milestone Completed',
        message: 'Congratulations! The "Phase 1 Development" milestone has been successfully completed.',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        isRead: true,
        isArchived: false,
        isPinned: false,
        isStarred: false,
        priority: 'medium',
        category: 'project',
        sender: {
          id: 'system',
          name: 'TeamFlow System',
          email: 'system@teamflow.com'
        },
        actionUrl: '/projects/project-456',
        actionText: 'View Project',
        metadata: {
          projectId: 'project-456'
        }
      },
      {
        id: 'notif-4',
        type: 'info',
        title: 'New Team Member Added',
        message: 'Alice Brown has been added to your project team. Welcome her to get started!',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        isRead: true,
        isArchived: false,
        isPinned: false,
        isStarred: false,
        priority: 'low',
        category: 'user',
        sender: {
          id: 'user-2',
          name: 'Project Manager',
          avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b6fd?w=100&h=100&fit=crop&crop=face',
          email: 'manager@company.com'
        },
        actionUrl: '/team/user-3',
        actionText: 'View Profile',
        metadata: {
          userId: 'user-3',
          projectId: 'project-456'
        }
      },
      {
        id: 'notif-5',
        type: 'system',
        title: 'System Maintenance Scheduled',
        message: 'System maintenance is scheduled for tonight from 11 PM to 1 AM. Please save your work.',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        isRead: false,
        isArchived: false,
        isPinned: true,
        isStarred: false,
        priority: 'urgent',
        category: 'system',
        sender: {
          id: 'admin',
          name: 'System Administrator',
          email: 'admin@teamflow.com'
        },
        metadata: {
          dueDate: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString()
        }
      },
      {
        id: 'notif-6',
        type: 'error',
        title: 'Failed to Upload File',
        message: 'The file "project-requirements.pdf" failed to upload. Please try again or contact support.',
        timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
        isRead: true,
        isArchived: true,
        isPinned: false,
        isStarred: false,
        priority: 'medium',
        category: 'system',
        sender: {
          id: 'system',
          name: 'TeamFlow System',
          email: 'system@teamflow.com'
        },
        actionUrl: '/support',
        actionText: 'Contact Support'
      },
      {
        id: 'notif-7',
        type: 'message',
        title: 'Meeting Reminder',
        message: 'Daily standup meeting starts in 15 minutes. Join the video call when ready.',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        isRead: false,
        isArchived: false,
        isPinned: false,
        isStarred: true,
        priority: 'high',
        category: 'reminder',
        sender: {
          id: 'calendar',
          name: 'Calendar System',
          email: 'calendar@teamflow.com'
        },
        actionUrl: '/meetings/daily-standup',
        actionText: 'Join Meeting',
        metadata: {
          dueDate: new Date(Date.now() + 15 * 60 * 1000).toISOString()
        }
      }
    ];
  };

  useEffect(() => {
    setIsLoading(true);
    setTimeout(() => {
      const mockNotifications = generateMockNotifications();
      setNotifications(mockNotifications);
      setIsLoading(false);
    }, 800);
  }, [userId]);

  useEffect(() => {
    let filtered = notifications;

    // Filter by tab
    switch (activeTab) {
      case 'unread':
        filtered = filtered.filter(n => !n.isRead);
        break;
      case 'archived':
        filtered = filtered.filter(n => n.isArchived);
        break;
      case 'starred':
        filtered = filtered.filter(n => n.isStarred);
        break;
      default:
        filtered = filtered.filter(n => !n.isArchived);
    }

    // Filter by search
    if (searchQuery) {
      filtered = filtered.filter(n =>
        n.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.sender?.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by type
    if (filterType) {
      filtered = filtered.filter(n => n.type === filterType);
    }

    // Filter by category
    if (filterCategory) {
      filtered = filtered.filter(n => n.category === filterCategory);
    }

    // Filter by priority
    if (filterPriority) {
      filtered = filtered.filter(n => n.priority === filterPriority);
    }

    setFilteredNotifications(filtered);
  }, [notifications, activeTab, searchQuery, filterType, filterCategory, filterPriority]);

  const handleNotificationAction = (notificationId: string, action: string) => {
    setNotifications(prev => prev.map(n => {
      if (n.id === notificationId) {
        switch (action) {
          case 'read':
            return { ...n, isRead: true };
          case 'unread':
            return { ...n, isRead: false };
          case 'archive':
            return { ...n, isArchived: true };
          case 'unarchive':
            return { ...n, isArchived: false };
          case 'star':
            return { ...n, isStarred: true };
          case 'unstar':
            return { ...n, isStarred: false };
          case 'pin':
            return { ...n, isPinned: true };
          case 'unpin':
            return { ...n, isPinned: false };
          case 'delete':
            return n; // Will be filtered out below
        }
      }
      return n;
    }));

    if (action === 'delete') {
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    }
  };

  const handleBulkAction = (action: string) => {
    if (selectedNotifications.length === 0) return;

    selectedNotifications.forEach(id => {
      handleNotificationAction(id, action);
    });

    setSelectedNotifications([]);
  };

  const handleSelectAll = () => {
    if (selectedNotifications.length === filteredNotifications.length) {
      setSelectedNotifications([]);
    } else {
      setSelectedNotifications(filteredNotifications.map(n => n.id));
    }
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={16} />;
      case 'warning':
        return <AlertTriangle size={16} />;
      case 'error':
        return <X size={16} />;
      case 'message':
        return <MessageSquare size={16} />;
      case 'system':
        return <Settings size={16} />;
      default:
        return <Info size={16} />;
    }
  };

  const getNotificationColor = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return '#10b981';
      case 'warning':
        return '#f59e0b';
      case 'error':
        return '#ef4444';
      case 'message':
        return '#3b82f6';
      case 'system':
        return '#8b5cf6';
      default:
        return '#64748b';
    }
  };

  const getPriorityColor = (priority: Notification['priority']) => {
    switch (priority) {
      case 'urgent':
        return '#ef4444';
      case 'high':
        return '#f59e0b';
      case 'medium':
        return '#3b82f6';
      default:
        return '#64748b';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const renderNotificationCard = (notification: Notification) => (
    <div
      key={notification.id}
      className={`notification-card ${!notification.isRead ? 'unread' : ''} ${notification.isPinned ? 'pinned' : ''}`}
    >
      <div className="notification-header">
        <input
          type="checkbox"
          checked={selectedNotifications.includes(notification.id)}
          onChange={() => {
            setSelectedNotifications(prev =>
              prev.includes(notification.id)
                ? prev.filter(id => id !== notification.id)
                : [...prev, notification.id]
            );
          }}
        />
        
        <div 
          className="notification-type-icon"
          style={{ color: getNotificationColor(notification.type) }}
        >
          {getNotificationIcon(notification.type)}
        </div>

        <div
          className="notification-priority"
          style={{ backgroundColor: getPriorityColor(notification.priority) }}
          title={`${notification.priority} priority`}
        />

        <div className="notification-actions">
          {notification.isPinned ? (
            <button
              className="action-btn-small"
              onClick={() => handleNotificationAction(notification.id, 'unpin')}
              title="Unpin"
            >
              <PinOff size={12} />
            </button>
          ) : (
            <button
              className="action-btn-small"
              onClick={() => handleNotificationAction(notification.id, 'pin')}
              title="Pin"
            >
              <Pin size={12} />
            </button>
          )}

          {notification.isStarred ? (
            <button
              className="action-btn-small"
              onClick={() => handleNotificationAction(notification.id, 'unstar')}
              title="Unstar"
            >
              <StarOff size={12} />
            </button>
          ) : (
            <button
              className="action-btn-small"
              onClick={() => handleNotificationAction(notification.id, 'star')}
              title="Star"
            >
              <Star size={12} />
            </button>
          )}

          <button className="action-btn-small">
            <MoreVertical size={12} />
          </button>
        </div>
      </div>

      <div className="notification-content">
        <div className="notification-sender">
          {notification.sender?.avatar ? (
            <img
              src={notification.sender.avatar}
              alt={notification.sender.name}
              className="sender-avatar"
            />
          ) : (
            <div className="sender-avatar-placeholder">
              <User size={14} />
            </div>
          )}
          <span className="sender-name">{notification.sender?.name}</span>
          <span className="notification-time">{formatTimestamp(notification.timestamp)}</span>
        </div>

        <div className="notification-body">
          <h4 className="notification-title">{notification.title}</h4>
          <p className="notification-message">{notification.message}</p>
        </div>

        {notification.actionUrl && (
          <div className="notification-footer">
            <button className="notification-action-btn">
              {notification.actionText || 'View'}
            </button>
            <div className="notification-quick-actions">
              {!notification.isRead ? (
                <button
                  className="quick-action-btn"
                  onClick={() => handleNotificationAction(notification.id, 'read')}
                  title="Mark as read"
                >
                  <Eye size={12} />
                </button>
              ) : (
                <button
                  className="quick-action-btn"
                  onClick={() => handleNotificationAction(notification.id, 'unread')}
                  title="Mark as unread"
                >
                  <EyeOff size={12} />
                </button>
              )}
              <button
                className="quick-action-btn"
                onClick={() => handleNotificationAction(notification.id, 'archive')}
                title="Archive"
              >
                <Archive size={12} />
              </button>
              <button
                className="quick-action-btn"
                onClick={() => handleNotificationAction(notification.id, 'delete')}
                title="Delete"
              >
                <Trash2 size={12} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderSettingsPanel = () => (
    <div className="settings-panel">
      <div className="settings-header">
        <h3>Notification Settings</h3>
        <button
          className="close-settings-btn"
          onClick={() => setShowSettings(false)}
        >
          <X size={16} />
        </button>
      </div>

      <div className="settings-content">
        <div className="settings-section">
          <h4>Delivery Methods</h4>
          <label className="setting-item">
            <input
              type="checkbox"
              checked={settings.emailNotifications}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                emailNotifications: e.target.checked
              }))}
            />
            <Mail size={16} />
            Email Notifications
          </label>
          <label className="setting-item">
            <input
              type="checkbox"
              checked={settings.pushNotifications}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                pushNotifications: e.target.checked
              }))}
            />
            <Bell size={16} />
            Push Notifications
          </label>
          <label className="setting-item">
            <input
              type="checkbox"
              checked={settings.browserNotifications}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                browserNotifications: e.target.checked
              }))}
            />
            <Activity size={16} />
            Browser Notifications
          </label>
          <label className="setting-item">
            <input
              type="checkbox"
              checked={settings.soundEnabled}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                soundEnabled: e.target.checked
              }))}
            />
            {settings.soundEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
            Sound Notifications
          </label>
        </div>

        <div className="settings-section">
          <h4>Categories</h4>
          {Object.entries(settings.categories).map(([category, enabled]) => (
            <label key={category} className="setting-item">
              <input
                type="checkbox"
                checked={enabled}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  categories: {
                    ...prev.categories,
                    [category]: e.target.checked
                  }
                }))}
              />
              <span className="category-name">{category.charAt(0).toUpperCase() + category.slice(1)}</span>
            </label>
          ))}
        </div>

        <div className="settings-section">
          <h4>Priority Levels</h4>
          {Object.entries(settings.priority).map(([priority, enabled]) => (
            <label key={priority} className="setting-item">
              <input
                type="checkbox"
                checked={enabled}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  priority: {
                    ...prev.priority,
                    [priority]: e.target.checked
                  }
                }))}
              />
              <span 
                className="priority-indicator"
                style={{ backgroundColor: getPriorityColor(priority as any) }}
              />
              <span className="priority-name">{priority.charAt(0).toUpperCase() + priority.slice(1)}</span>
            </label>
          ))}
        </div>

        <div className="settings-section">
          <h4>Quiet Hours</h4>
          <label className="setting-item">
            <input
              type="checkbox"
              checked={settings.quietHours.enabled}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                quietHours: {
                  ...prev.quietHours,
                  enabled: e.target.checked
                }
              }))}
            />
            <BellOff size={16} />
            Enable Quiet Hours
          </label>
          {settings.quietHours.enabled && (
            <div className="quiet-hours-config">
              <div className="time-input">
                <label>From:</label>
                <input
                  type="time"
                  value={settings.quietHours.startTime}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    quietHours: {
                      ...prev.quietHours,
                      startTime: e.target.value
                    }
                  }))}
                />
              </div>
              <div className="time-input">
                <label>To:</label>
                <input
                  type="time"
                  value={settings.quietHours.endTime}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    quietHours: {
                      ...prev.quietHours,
                      endTime: e.target.value
                    }
                  }))}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="settings-footer">
        <button className="action-btn secondary">Reset to Default</button>
        <button className="action-btn primary">Save Settings</button>
      </div>
    </div>
  );

  const unreadCount = notifications.filter(n => !n.isRead && !n.isArchived).length;

  return (
    <div className="notification-center">
      <div className="notification-header">
        <div className="header-content">
          <h1>
            <Bell size={24} />
            Notifications
            {unreadCount > 0 && <span className="unread-badge">{unreadCount}</span>}
          </h1>
          <p>Stay updated with your team's activities and important updates</p>
        </div>

        <div className="header-actions">
          <button
            className="action-btn secondary"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings size={16} />
            Settings
          </button>
          {onClose && (
            <button className="action-btn secondary" onClick={onClose}>
              <X size={16} />
              Close
            </button>
          )}
        </div>
      </div>

      {showSettings && renderSettingsPanel()}

      <div className="notification-controls">
        <div className="notification-tabs">
          {(['all', 'unread', 'archived', 'starred'] as const).map(tab => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === 'unread' && unreadCount > 0 && (
                <span className="tab-count">{unreadCount}</span>
              )}
            </button>
          ))}
        </div>

        <div className="control-actions">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search notifications..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="filter-controls">
            <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
              <option value="">All Types</option>
              <option value="info">Info</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="message">Message</option>
              <option value="system">System</option>
            </select>

            <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
              <option value="">All Categories</option>
              <option value="task">Tasks</option>
              <option value="project">Projects</option>
              <option value="user">Users</option>
              <option value="system">System</option>
              <option value="reminder">Reminders</option>
              <option value="social">Social</option>
            </select>

            <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
              <option value="">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>

        {selectedNotifications.length > 0 && (
          <div className="bulk-actions">
            <span className="selected-count">
              {selectedNotifications.length} selected
            </span>
            <button
              className="bulk-action-btn"
              onClick={() => handleBulkAction('read')}
            >
              <Check size={14} />
              Mark Read
            </button>
            <button
              className="bulk-action-btn"
              onClick={() => handleBulkAction('archive')}
            >
              <Archive size={14} />
              Archive
            </button>
            <button
              className="bulk-action-btn danger"
              onClick={() => handleBulkAction('delete')}
            >
              <Trash2 size={14} />
              Delete
            </button>
          </div>
        )}
      </div>

      <div className="notification-list">
        {isLoading ? (
          <div className="loading-state">
            <Bell size={32} />
            <p>Loading notifications...</p>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="empty-state">
            <BellOff size={48} />
            <h3>No notifications found</h3>
            <p>You're all caught up! Check back later for new updates.</p>
          </div>
        ) : (
          <>
            <div className="list-controls">
              <button
                className="select-all-btn"
                onClick={handleSelectAll}
              >
                {selectedNotifications.length === filteredNotifications.length ? 'Deselect All' : 'Select All'}
              </button>
              <span className="notification-count">
                Showing {filteredNotifications.length} notifications
              </span>
            </div>
            <div className="notifications-container">
              {filteredNotifications.map(renderNotificationCard)}
            </div>
          </>
        )}
      </div>
    </div>
  );
};