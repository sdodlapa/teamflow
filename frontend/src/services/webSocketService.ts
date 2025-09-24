// WebSocket service for real-time collaboration
import { toast } from 'react-hot-toast';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  user_id?: string;
  template_id?: string;
}

export interface CollaborationEvent {
  type: 'user_joined' | 'user_left' | 'template_updated' | 'cursor_moved' | 'selection_changed' | 'chat_message';
  user: {
    id: string;
    name: string;
    avatar?: string;
  };
  data: any;
  timestamp: number;
}

export interface WebSocketCallbacks {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
  onCollaborationEvent?: (event: CollaborationEvent) => void;
  onTemplateUpdate?: (templateId: string, data: any) => void;
  onUserPresence?: (users: any[]) => void;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000; // Start with 1 second
  private callbacks: WebSocketCallbacks = {};
  private currentTemplateId: string | null = null;
  private heartbeatInterval: number | null = null;

  constructor() {
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
    this.send = this.send.bind(this);
  }

  /**
   * Connect to WebSocket server with JWT token authentication
   */
  connect(token?: string): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    const url = token ? `${wsUrl}?token=${token}` : wsUrl;

    try {
      this.socket = new WebSocket(url);
      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.callbacks.onError?.(error as Event);
    }
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.reconnectInterval = 1000;
      this.startHeartbeat();
      this.callbacks.onConnect?.();
      toast.success('Connected to real-time updates');
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.stopHeartbeat();
      this.callbacks.onDisconnect?.();
      
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.scheduleReconnect();
      } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        toast.error('Lost connection to real-time updates');
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.callbacks.onError?.(error);
    };

    this.socket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    this.callbacks.onMessage?.(message);

    switch (message.type) {
      case 'collaboration_event':
        this.callbacks.onCollaborationEvent?.(message.data as CollaborationEvent);
        break;
      
      case 'template_updated':
        this.callbacks.onTemplateUpdate?.(message.template_id!, message.data);
        break;
      
      case 'user_presence':
        this.callbacks.onUserPresence?.(message.data.users);
        break;
      
      case 'notification':
        this.handleNotification(message.data);
        break;
      
      case 'pong':
        // Heartbeat response
        break;
      
      default:
        console.log('Unhandled WebSocket message type:', message.type);
    }
  }

  private handleNotification(data: any): void {
    switch (data.level) {
      case 'success':
        toast.success(data.message);
        break;
      case 'error':
        toast.error(data.message);
        break;
      case 'warning':
        toast(data.message, { icon: '⚠️' });
        break;
      case 'info':
      default:
        toast(data.message, { icon: 'ℹ️' });
        break;
    }
  }

  /**
   * Schedule automatic reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    setTimeout(() => {
      this.reconnectAttempts++;
      this.reconnectInterval *= 1.5; // Exponential backoff
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect();
    }, this.reconnectInterval);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          data: {},
          timestamp: Date.now()
        });
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.socket) {
      this.socket.close(1000, 'Client disconnecting');
      this.socket = null;
    }
  }

  send(message: WebSocketMessage): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }

  // Template collaboration methods
  joinTemplate(templateId: string): void {
    this.currentTemplateId = templateId;
    this.send({
      type: 'join_template',
      data: { template_id: templateId },
      timestamp: Date.now()
    });
  }

  leaveTemplate(templateId: string): void {
    if (this.currentTemplateId === templateId) {
      this.currentTemplateId = null;
    }
    this.send({
      type: 'leave_template',
      data: { template_id: templateId },
      timestamp: Date.now()
    });
  }

  broadcastTemplateChange(templateId: string, changes: any): void {
    this.send({
      type: 'template_change',
      data: {
        template_id: templateId,
        changes
      },
      timestamp: Date.now()
    });
  }

  sendCursorPosition(templateId: string, position: { x: number; y: number; element?: string }): void {
    this.send({
      type: 'cursor_position',
      data: {
        template_id: templateId,
        position
      },
      timestamp: Date.now()
    });
  }

  sendChatMessage(templateId: string, message: string): void {
    this.send({
      type: 'chat_message',
      data: {
        template_id: templateId,
        message
      },
      timestamp: Date.now()
    });
  }

  // Event handler registration
  onConnect(callback: () => void): void {
    this.callbacks.onConnect = callback;
  }

  onDisconnect(callback: () => void): void {
    this.callbacks.onDisconnect = callback;
  }

  onError(callback: (error: Event) => void): void {
    this.callbacks.onError = callback;
  }

  onMessage(callback: (message: WebSocketMessage) => void): void {
    this.callbacks.onMessage = callback;
  }

  onCollaborationEvent(callback: (event: CollaborationEvent) => void): void {
    this.callbacks.onCollaborationEvent = callback;
  }

  onTemplateUpdate(callback: (templateId: string, data: any) => void): void {
    this.callbacks.onTemplateUpdate = callback;
  }

  onUserPresence(callback: (users: any[]) => void): void {
    this.callbacks.onUserPresence = callback;
  }

  // Getters
  get isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  get currentTemplate(): string | null {
    return this.currentTemplateId;
  }

  get connectionState(): string {
    if (!this.socket) return 'disconnected';
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'disconnected';
      default: return 'unknown';
    }
  }
}

export const webSocketService = new WebSocketService();
export default webSocketService;