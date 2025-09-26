import React, { useState, useEffect } from 'react';
import { useCollaboration } from './CollaborationProvider';

interface LiveUpdateNotificationProps {
  className?: string;
}

export const LiveUpdateNotification: React.FC<LiveUpdateNotificationProps> = ({
  className = ''
}) => {
  const { subscribeToMessages } = useCollaboration();
  const [notifications, setNotifications] = useState<Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
    user_id: string;
  }>>([]);
  
  useEffect(() => {
    const unsubscribe = subscribeToMessages((message) => {
      let notificationMessage = '';
      
      switch (message.type) {
        case 'task_update':
          notificationMessage = `Task "${message.data?.title || message.task_id}" was updated`;
          break;
        case 'project_update':
          notificationMessage = `Project "${message.data?.name || message.project_id}" was updated`;
          break;
        case 'user_presence':
          if (message.action === 'joined') {
            notificationMessage = `User ${message.user_id} joined the workspace`;
          } else if (message.action === 'left') {
            notificationMessage = `User ${message.user_id} left the workspace`;
          }
          break;
        default:
          return; // Don't show notification for other message types
      }
      
      if (notificationMessage) {
        const notification = {
          id: `notification-${Date.now()}`,
          type: message.type,
          message: notificationMessage,
          timestamp: message.timestamp,
          user_id: message.user_id || 'system'
        };
        
        setNotifications(prev => [notification, ...prev.slice(0, 4)]); // Keep only latest 5
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
          setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 5000);
      }
    });
    
    return unsubscribe;
  }, [subscribeToMessages]);
  
  if (notifications.length === 0) return null;
  
  return (
    <div className={`fixed top-4 right-4 space-y-2 z-50 ${className}`}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm animate-slide-in-right"
        >
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm text-gray-800">{notification.message}</p>
              <p className="text-xs text-gray-500 mt-1">
                {new Date(notification.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

interface CollaborativeEditingIndicatorProps {
  entityType: string;
  entityId: string;
  currentField?: string;
  className?: string;
}

export const CollaborativeEditingIndicator: React.FC<CollaborativeEditingIndicatorProps> = ({
  entityType,
  entityId,
  currentField,
  className = ''
}) => {
  const { subscribeToMessages, activeUsers, updateActivity } = useCollaboration();
  const [editingUsers, setEditingUsers] = useState<Array<{
    user_id: string;
    field: string;
    timestamp: string;
  }>>([]);
  
  // Track when current user starts/stops editing
  useEffect(() => {
    if (currentField) {
      updateActivity({
        type: 'editing',
        entity_type: entityType,
        entity_id: entityId,
        description: `Editing ${currentField}`
      });
    } else {
      updateActivity({
        type: 'viewing',
        entity_type: entityType,
        entity_id: entityId,
        description: `Viewing ${entityType}`
      });
    }
  }, [currentField, entityType, entityId, updateActivity]);
  
  // Listen for other users' editing activities
  useEffect(() => {
    const unsubscribe = subscribeToMessages((message) => {
      if (message.type === 'user_activity' && 
          message.activity?.entity_type === entityType &&
          message.activity?.entity_id === entityId &&
          message.activity?.type === 'editing') {
        
        const editingUser = {
          user_id: message.user_id!,
          field: message.activity.description || 'unknown field',
          timestamp: message.timestamp
        };
        
        setEditingUsers(prev => {
          const filtered = prev.filter(u => u.user_id !== message.user_id);
          return [...filtered, editingUser];
        });
        
        // Remove after timeout
        setTimeout(() => {
          setEditingUsers(prev => prev.filter(u => 
            u.user_id !== editingUser.user_id || u.timestamp !== editingUser.timestamp
          ));
        }, 10000);
      }
    });
    
    return unsubscribe;
  }, [subscribeToMessages, entityType, entityId]);
  
  const otherEditingUsers = editingUsers.filter(u => 
    activeUsers.some(au => au.user_id === u.user_id)
  );
  
  if (otherEditingUsers.length === 0) return null;
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex -space-x-2">
        {otherEditingUsers.slice(0, 3).map((user) => (
          <div
            key={user.user_id}
            className="w-6 h-6 bg-gradient-to-r from-green-400 to-blue-500 rounded-full border-2 border-white flex items-center justify-center text-xs font-semibold text-white"
            title={`User ${user.user_id} is ${user.field}`}
          >
            {user.user_id.charAt(0).toUpperCase()}
          </div>
        ))}
        {otherEditingUsers.length > 3 && (
          <div className="w-6 h-6 bg-gray-500 rounded-full border-2 border-white flex items-center justify-center text-xs font-semibold text-white">
            +{otherEditingUsers.length - 3}
          </div>
        )}
      </div>
      <div className="text-sm text-gray-600">
        {otherEditingUsers.length === 1 
          ? `${otherEditingUsers[0].field.replace('Editing ', '')}`
          : `${otherEditingUsers.length} users editing`
        }
      </div>
      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
    </div>
  );
};

export default LiveUpdateNotification;