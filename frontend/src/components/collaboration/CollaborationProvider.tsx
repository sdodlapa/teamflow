import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

// Temporary auth hook - replace with actual auth context
const useAuth = () => ({
  user: { id: 'temp-user-id', name: 'Test User' },
  token: 'temp-token'  // In production, use actual JWT token
});

interface CollaborationUser {
  user_id: string;
  status: 'online' | 'away' | 'offline';
  last_seen: string;
  current_activity?: {
    type: 'viewing' | 'editing' | 'idle';
    entity_type?: string;
    entity_id?: string;
    description?: string;
  };
}

interface CollaborationMessage {
  type: string;
  timestamp: string;
  user_id?: string;
  data?: any;
  [key: string]: any;
}

interface CollaborationContextType {
  // Connection state
  isConnected: boolean;
  connectionError: string | null;
  
  // Users and presence
  activeUsers: CollaborationUser[];
  currentUserActivity: CollaborationUser['current_activity'];
  
  // Messaging
  sendMessage: (message: CollaborationMessage) => void;
  subscribeToMessages: (callback: (message: CollaborationMessage) => void) => () => void;
  
  // User actions
  updateActivity: (activity: CollaborationUser['current_activity']) => void;
  sendTypingIndicator: (entityType: string, entityId: string, isTyping: boolean) => void;
  
  // Utilities
  getUserStatus: (userId: string) => 'online' | 'away' | 'offline';
  isUserOnline: (userId: string) => boolean;
}

const CollaborationContext = createContext<CollaborationContextType | undefined>(undefined);

interface CollaborationProviderProps {
  children: React.ReactNode;
  workspaceId: string;
}

export const CollaborationProvider: React.FC<CollaborationProviderProps> = ({
  children,
  workspaceId
}) => {
  const { user, token } = useAuth();
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [activeUsers, setActiveUsers] = useState<CollaborationUser[]>([]);
  const [currentUserActivity, setCurrentUserActivity] = useState<CollaborationUser['current_activity']>();
  const [messageCallbacks, setMessageCallbacks] = useState<Array<(message: CollaborationMessage) => void>>([]);

  // WebSocket connection management
  const connect = useCallback(() => {
    if (!user || !token || !workspaceId) return;

    try {
      const wsUrl = `ws://localhost:8000/api/v1/collaboration/ws/${workspaceId}?token=${token}`;
      const newSocket = new WebSocket(wsUrl);

      newSocket.onopen = () => {
        console.log('🔗 Connected to collaboration service');
        setIsConnected(true);
        setConnectionError(null);
        
        // Send initial ping
        newSocket.send(JSON.stringify({
          type: 'ping',
          timestamp: new Date().toISOString()
        }));
      };

      newSocket.onmessage = (event) => {
        try {
          const message: CollaborationMessage = JSON.parse(event.data);
          handleMessage(message);
          
          // Notify all subscribers
          messageCallbacks.forEach(callback => callback(message));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      newSocket.onclose = (event) => {
        console.log('🔌 Disconnected from collaboration service', event.code, event.reason);
        setIsConnected(false);
        
        if (event.code !== 1000) { // Not a normal closure
          setConnectionError('Connection lost. Attempting to reconnect...');
          
          // Attempt to reconnect after delay
          setTimeout(() => {
            if (!isConnected) {
              connect();
            }
          }, 3000);
        }
      };

      newSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('Connection error occurred');
      };

      setSocket(newSocket);
    } catch (error) {
      console.error('Failed to connect to collaboration service:', error);
      setConnectionError('Failed to establish connection');
    }
  }, [user, token, workspaceId, isConnected, messageCallbacks]);

  // Handle incoming messages
  const handleMessage = (message: CollaborationMessage) => {
    switch (message.type) {
      case 'pong':
        // Handle ping/pong for connection health
        break;
        
      case 'user_presence':
        if (message.action === 'joined') {
          setActiveUsers(prev => {
            const filtered = prev.filter(u => u.user_id !== message.user_id);
            return [...filtered, {
              user_id: message.user_id!,
              status: 'online' as const,
              last_seen: message.timestamp
            }];
          });
        } else if (message.action === 'left') {
          setActiveUsers(prev => prev.filter(u => u.user_id !== message.user_id));
        }
        break;
        
      case 'user_activity':
        setActiveUsers(prev => prev.map(user => 
          user.user_id === message.user_id 
            ? { ...user, current_activity: message.activity }
            : user
        ));
        break;
        
      case 'task_update':
      case 'project_update':
      case 'new_comment':
      case 'typing_indicator':
        // These are handled by specific subscribers
        break;
        
      default:
        console.log('Unknown message type:', message.type, message);
    }
  };

  // Send message to server
  const sendMessage = useCallback((message: CollaborationMessage) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  }, [socket]);

  // Subscribe to messages
  const subscribeToMessages = useCallback((callback: (message: CollaborationMessage) => void) => {
    setMessageCallbacks(prev => [...prev, callback]);
    
    // Return unsubscribe function
    return () => {
      setMessageCallbacks(prev => prev.filter(cb => cb !== callback));
    };
  }, []);

  // Update user activity
  const updateActivity = useCallback((activity: CollaborationUser['current_activity']) => {
    setCurrentUserActivity(activity);
    sendMessage({
      type: 'user_activity',
      activity,
      timestamp: new Date().toISOString()
    });
  }, [sendMessage]);

  // Send typing indicator
  const sendTypingIndicator = useCallback((entityType: string, entityId: string, isTyping: boolean) => {
    sendMessage({
      type: 'typing_indicator',
      entity_type: entityType,
      entity_id: entityId,
      is_typing: isTyping,
      timestamp: new Date().toISOString()
    });
  }, [sendMessage]);

  // Utility functions
  const getUserStatus = useCallback((userId: string): 'online' | 'away' | 'offline' => {
    const user = activeUsers.find(u => u.user_id === userId);
    return user?.status || 'offline';
  }, [activeUsers]);

  const isUserOnline = useCallback((userId: string): boolean => {
    return getUserStatus(userId) === 'online';
  }, [getUserStatus]);

  // Connection lifecycle
  useEffect(() => {
    if (user && token && workspaceId) {
      connect();
    }

    return () => {
      if (socket) {
        socket.close(1000, 'Component unmounting');
      }
    };
  }, [user, token, workspaceId]); // Remove connect from dependencies to avoid loops

  // Heartbeat to keep connection alive
  useEffect(() => {
    if (isConnected && socket) {
      const interval = setInterval(() => {
        sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      }, 30000); // Ping every 30 seconds

      return () => clearInterval(interval);
    }
  }, [isConnected, socket, sendMessage]);

  const contextValue: CollaborationContextType = {
    isConnected,
    connectionError,
    activeUsers,
    currentUserActivity,
    sendMessage,
    subscribeToMessages,
    updateActivity,
    sendTypingIndicator,
    getUserStatus,
    isUserOnline
  };

  return (
    <CollaborationContext.Provider value={contextValue}>
      {children}
    </CollaborationContext.Provider>
  );
};

export const useCollaboration = () => {
  const context = useContext(CollaborationContext);
  if (context === undefined) {
    throw new Error('useCollaboration must be used within a CollaborationProvider');
  }
  return context;
};