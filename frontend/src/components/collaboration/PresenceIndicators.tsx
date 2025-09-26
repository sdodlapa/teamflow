import React from 'react';
import { useCollaboration } from './CollaborationProvider';

interface PresenceIndicatorProps {
  userId?: string;
  showStatus?: boolean;
  showActivity?: boolean;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export const PresenceIndicator: React.FC<PresenceIndicatorProps> = ({
  userId,
  showStatus = true,
  showActivity = false,
  size = 'medium',
  className = ''
}) => {
  const { getUserStatus, activeUsers } = useCollaboration();
  
  if (!userId) return null;
  
  const status = getUserStatus(userId);
  const user = activeUsers.find(u => u.user_id === userId);
  
  const statusColors = {
    online: 'bg-green-500',
    away: 'bg-yellow-500', 
    offline: 'bg-gray-400'
  };
  
  const sizes = {
    small: 'w-2 h-2',
    medium: 'w-3 h-3',
    large: 'w-4 h-4'
  };
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {showStatus && (
        <div className="relative">
          <div 
            className={`${sizes[size]} ${statusColors[status]} rounded-full border-2 border-white shadow-sm`}
            title={`User is ${status}`}
          />
          {status === 'online' && (
            <div 
              className={`absolute inset-0 ${sizes[size]} bg-green-500 rounded-full animate-ping opacity-75`}
            />
          )}
        </div>
      )}
      
      {showActivity && user?.current_activity && (
        <span className="text-xs text-gray-600 truncate max-w-32">
          {user.current_activity.description || `${user.current_activity.type} ${user.current_activity.entity_type}`}
        </span>
      )}
    </div>
  );
};

interface ActiveUsersListProps {
  maxDisplay?: number;
  showActivity?: boolean;
  className?: string;
}

export const ActiveUsersList: React.FC<ActiveUsersListProps> = ({
  maxDisplay = 5,
  showActivity = true,
  className = ''
}) => {
  const { activeUsers } = useCollaboration();
  
  const displayUsers = activeUsers.slice(0, maxDisplay);
  const remainingCount = Math.max(0, activeUsers.length - maxDisplay);
  
  if (activeUsers.length === 0) {
    return (
      <div className={`text-sm text-gray-500 ${className}`}>
        No active users
      </div>
    );
  }
  
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        {activeUsers.length} active user{activeUsers.length !== 1 ? 's' : ''}
      </div>
      
      <div className="space-y-1">
        {displayUsers.map((user) => (
          <div key={user.user_id} className="flex items-center gap-3 p-2 rounded-lg bg-gray-50">
            <PresenceIndicator 
              userId={user.user_id} 
              size="small"
            />
            
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">
                User {user.user_id}
              </div>
              
              {showActivity && user.current_activity && (
                <div className="text-xs text-gray-600 truncate">
                  {user.current_activity.description || 
                   `${user.current_activity.type} ${user.current_activity.entity_type || ''}`}
                </div>
              )}
            </div>
            
            <div className="text-xs text-gray-500">
              {new Date(user.last_seen).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        ))}
      </div>
      
      {remainingCount > 0 && (
        <div className="text-xs text-gray-500 text-center py-1">
          +{remainingCount} more user{remainingCount !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

interface CollaborationStatusProps {
  className?: string;
}

export const CollaborationStatus: React.FC<CollaborationStatusProps> = ({
  className = ''
}) => {
  const { isConnected, connectionError, activeUsers } = useCollaboration();
  
  if (connectionError) {
    return (
      <div className={`flex items-center gap-2 text-sm text-red-600 ${className}`}>
        <div className="w-2 h-2 bg-red-500 rounded-full" />
        {connectionError}
      </div>
    );
  }
  
  if (!isConnected) {
    return (
      <div className={`flex items-center gap-2 text-sm text-yellow-600 ${className}`}>
        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
        Connecting...
      </div>
    );
  }
  
  return (
    <div className={`flex items-center gap-2 text-sm text-green-600 ${className}`}>
      <div className="w-2 h-2 bg-green-500 rounded-full" />
      Connected • {activeUsers.length} online
    </div>
  );
};