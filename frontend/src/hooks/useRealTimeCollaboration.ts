import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import webSocketService, { CollaborationEvent } from '../services/webSocketService';

export interface CollaborativeUser {
  id: string;
  name: string;
  avatar?: string;
  cursor?: {
    x: number;
    y: number;
    element?: string;
  };
  isActive: boolean;
  lastSeen: number;
}

export interface ChatMessage {
  id: string;
  user: {
    id: string;
    name: string;
    avatar?: string;
  };
  message: string;
  timestamp: number;
}

export interface UseRealTimeCollaboration {
  // Connection state
  isConnected: boolean;
  connectionState: string;
  
  // Users and presence
  collaborativeUsers: CollaborativeUser[];
  activeUsersCount: number;
  
  // Chat
  chatMessages: ChatMessage[];
  sendChatMessage: (message: string) => void;
  
  // Template collaboration
  joinTemplate: (templateId: string) => void;
  leaveTemplate: (templateId: string) => void;
  broadcastChange: (changes: any) => void;
  sendCursorPosition: (position: { x: number; y: number; element?: string }) => void;
  
  // Events
  onTemplateUpdate: (callback: (templateId: string, data: any) => void) => void;
  onUserJoined: (callback: (user: CollaborativeUser) => void) => void;
  onUserLeft: (callback: (userId: string) => void) => void;
  
  // Connection management
  connect: () => void;
  disconnect: () => void;
}

export const useRealTimeCollaboration = (): UseRealTimeCollaboration => {
  const { user, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('disconnected');
  const [collaborativeUsers, setCollaborativeUsers] = useState<CollaborativeUser[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [currentTemplateId, setCurrentTemplateId] = useState<string | null>(null);
  
  // Event callbacks
  const [templateUpdateCallback, setTemplateUpdateCallback] = useState<((templateId: string, data: any) => void) | null>(null);
  const [userJoinedCallback, setUserJoinedCallback] = useState<((user: CollaborativeUser) => void) | null>(null);
  const [userLeftCallback, setUserLeftCallback] = useState<((userId: string) => void) | null>(null);

  // Initialize WebSocket connection when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [isAuthenticated, user]);

  // Set up WebSocket event handlers
  useEffect(() => {
    webSocketService.onConnect(() => {
      setIsConnected(true);
      setConnectionState('connected');
    });

    webSocketService.onDisconnect(() => {
      setIsConnected(false);
      setConnectionState('disconnected');
      setCollaborativeUsers([]);
    });

    webSocketService.onError(() => {
      setConnectionState('error');
    });

    webSocketService.onCollaborationEvent((event: CollaborationEvent) => {
      handleCollaborationEvent(event);
    });

    webSocketService.onTemplateUpdate((templateId: string, data: any) => {
      templateUpdateCallback?.(templateId, data);
    });

    webSocketService.onUserPresence((users: any[]) => {
      const mappedUsers: CollaborativeUser[] = users.map(u => ({
        id: u.id,
        name: u.name,
        avatar: u.avatar,
        cursor: u.cursor,
        isActive: u.is_active || true,
        lastSeen: u.last_seen || Date.now()
      }));
      setCollaborativeUsers(mappedUsers);
    });

    webSocketService.onMessage(() => {
      setConnectionState(webSocketService.connectionState);
    });

    return () => {
      // Cleanup is handled by the service
    };
  }, [templateUpdateCallback, userJoinedCallback, userLeftCallback]);

  const handleCollaborationEvent = useCallback((event: CollaborationEvent) => {
    switch (event.type) {
      case 'user_joined':
        const newUser: CollaborativeUser = {
          id: event.user.id,
          name: event.user.name,
          avatar: event.user.avatar,
          isActive: true,
          lastSeen: event.timestamp
        };
        setCollaborativeUsers(prev => [...prev.filter(u => u.id !== event.user.id), newUser]);
        userJoinedCallback?.(newUser);
        break;

      case 'user_left':
        setCollaborativeUsers(prev => prev.filter(u => u.id !== event.user.id));
        userLeftCallback?.(event.user.id);
        break;

      case 'cursor_moved':
        setCollaborativeUsers(prev => prev.map(u => 
          u.id === event.user.id 
            ? { ...u, cursor: event.data.position, lastSeen: event.timestamp }
            : u
        ));
        break;

      case 'chat_message':
        const newMessage: ChatMessage = {
          id: `${event.user.id}_${event.timestamp}`,
          user: event.user,
          message: event.data.message,
          timestamp: event.timestamp
        };
        setChatMessages(prev => [...prev, newMessage].slice(-100)); // Keep last 100 messages
        break;

      case 'template_updated':
        // This is handled by the onTemplateUpdate callback
        break;

      case 'selection_changed':
        setCollaborativeUsers(prev => prev.map(u => 
          u.id === event.user.id 
            ? { ...u, lastSeen: event.timestamp }
            : u
        ));
        break;

      default:
        console.log('Unhandled collaboration event:', event);
    }
  }, [templateUpdateCallback, userJoinedCallback, userLeftCallback]);

  const connect = useCallback(() => {
    if (isAuthenticated && user) {
      // In a real implementation, you'd get the token from your auth service
      const token = localStorage.getItem('access_token');
      webSocketService.connect(token || undefined);
    }
  }, [isAuthenticated, user]);

  const disconnect = useCallback(() => {
    if (currentTemplateId) {
      webSocketService.leaveTemplate(currentTemplateId);
    }
    webSocketService.disconnect();
    setIsConnected(false);
    setConnectionState('disconnected');
    setCollaborativeUsers([]);
    setChatMessages([]);
  }, [currentTemplateId]);

  const joinTemplate = useCallback((templateId: string) => {
    if (currentTemplateId && currentTemplateId !== templateId) {
      webSocketService.leaveTemplate(currentTemplateId);
    }
    setCurrentTemplateId(templateId);
    webSocketService.joinTemplate(templateId);
    setChatMessages([]); // Clear chat when switching templates
  }, [currentTemplateId]);

  const leaveTemplate = useCallback((templateId: string) => {
    webSocketService.leaveTemplate(templateId);
    if (currentTemplateId === templateId) {
      setCurrentTemplateId(null);
      setCollaborativeUsers([]);
      setChatMessages([]);
    }
  }, [currentTemplateId]);

  const broadcastChange = useCallback((changes: any) => {
    if (currentTemplateId) {
      webSocketService.broadcastTemplateChange(currentTemplateId, changes);
    }
  }, [currentTemplateId]);

  const sendCursorPosition = useCallback((position: { x: number; y: number; element?: string }) => {
    if (currentTemplateId) {
      webSocketService.sendCursorPosition(currentTemplateId, position);
    }
  }, [currentTemplateId]);

  const sendChatMessage = useCallback((message: string) => {
    if (currentTemplateId && message.trim()) {
      webSocketService.sendChatMessage(currentTemplateId, message.trim());
    }
  }, [currentTemplateId]);

  const onTemplateUpdate = useCallback((callback: (templateId: string, data: any) => void) => {
    setTemplateUpdateCallback(() => callback);
  }, []);

  const onUserJoined = useCallback((callback: (user: CollaborativeUser) => void) => {
    setUserJoinedCallback(() => callback);
  }, []);

  const onUserLeft = useCallback((callback: (userId: string) => void) => {
    setUserLeftCallback(() => callback);
  }, []);

  return {
    isConnected,
    connectionState,
    collaborativeUsers,
    activeUsersCount: collaborativeUsers.filter(u => u.isActive).length,
    chatMessages,
    sendChatMessage,
    joinTemplate,
    leaveTemplate,
    broadcastChange,
    sendCursorPosition,
    onTemplateUpdate,
    onUserJoined,
    onUserLeft,
    connect,
    disconnect,
  };
};