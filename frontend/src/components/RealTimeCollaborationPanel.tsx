import React, { useState, useRef, useEffect } from 'react';
import { Users, MessageCircle, Wifi, WifiOff, Send } from 'lucide-react';
import { useRealTimeCollaboration, CollaborativeUser } from '../hooks/useRealTimeCollaboration';

interface RealTimeCollaborationPanelProps {
  templateId?: string;
  onUserPresenceChange?: (users: CollaborativeUser[]) => void;
  onTemplateUpdate?: (templateId: string, data: any) => void;
}

const RealTimeCollaborationPanel: React.FC<RealTimeCollaborationPanelProps> = ({
  templateId,
  onUserPresenceChange,
  onTemplateUpdate,
}) => {
  const collaboration = useRealTimeCollaboration();
  const [showChat, setShowChat] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [showUsersList, setShowUsersList] = useState(false);
  const chatMessagesRef = useRef<HTMLDivElement>(null);

  // Join template when templateId changes
  useEffect(() => {
    if (templateId && collaboration.isConnected) {
      collaboration.joinTemplate(templateId);
    }
    return () => {
      if (templateId) {
        collaboration.leaveTemplate(templateId);
      }
    };
  }, [templateId, collaboration.isConnected]);

  // Set up event handlers
  useEffect(() => {
    if (onUserPresenceChange) {
      onUserPresenceChange(collaboration.collaborativeUsers);
    }
  }, [collaboration.collaborativeUsers, onUserPresenceChange]);

  useEffect(() => {
    if (onTemplateUpdate) {
      collaboration.onTemplateUpdate(onTemplateUpdate);
    }
  }, [onTemplateUpdate]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [collaboration.chatMessages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatMessage.trim()) {
      collaboration.sendChatMessage(chatMessage);
      setChatMessage('');
    }
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getConnectionStatusColor = () => {
    switch (collaboration.connectionState) {
      case 'connected': return '#10b981';
      case 'connecting': return '#f59e0b';
      case 'disconnected': return '#ef4444';
      case 'error': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const getConnectionStatusIcon = () => {
    return collaboration.isConnected ? <Wifi size={16} /> : <WifiOff size={16} />;
  };

  return (
    <div style={{
      position: 'fixed',
      top: '80px',
      right: '20px',
      width: '320px',
      background: 'white',
      borderRadius: '0.75rem',
      boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
      border: '1px solid #e5e7eb',
      zIndex: 1000,
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '1rem',
        borderBottom: '1px solid #e5e7eb',
        background: '#f8fafc'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ margin: 0, fontSize: '0.875rem', fontWeight: '600', color: '#1f2937' }}>
            Live Collaboration
          </h3>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.75rem',
            color: getConnectionStatusColor()
          }}>
            {getConnectionStatusIcon()}
            <span style={{ textTransform: 'capitalize' }}>
              {collaboration.connectionState}
            </span>
          </div>
        </div>
      </div>

      {/* Active Users */}
      <div style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '0.75rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={16} color="#6b7280" />
            <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
              Active Users ({collaboration.activeUsersCount})
            </span>
          </div>
          <button
            onClick={() => setShowUsersList(!showUsersList)}
            style={{
              background: 'none',
              border: 'none',
              color: '#6366f1',
              cursor: 'pointer',
              fontSize: '0.75rem'
            }}
          >
            {showUsersList ? 'Hide' : 'Show'}
          </button>
        </div>

        {showUsersList && (
          <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
            {collaboration.collaborativeUsers.length === 0 ? (
              <p style={{ fontSize: '0.75rem', color: '#6b7280', textAlign: 'center' }}>
                No other users online
              </p>
            ) : (
              collaboration.collaborativeUsers.map((user) => (
                <div
                  key={user.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.25rem 0',
                    fontSize: '0.75rem'
                  }}
                >
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: user.isActive ? '#10b981' : '#6b7280'
                  }} />
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    background: '#e5e7eb',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.625rem',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    {user.avatar || user.name.charAt(0).toUpperCase()}
                  </div>
                  <span style={{ color: '#374151' }}>{user.name}</span>
                  {user.cursor && (
                    <span style={{ fontSize: '0.625rem', color: '#6b7280' }}>
                      ✍️ editing
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Chat */}
      <div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem',
          borderBottom: showChat ? '1px solid #e5e7eb' : 'none'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <MessageCircle size={16} color="#6b7280" />
            <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
              Team Chat
            </span>
            {collaboration.chatMessages.length > 0 && (
              <span style={{
                background: '#ef4444',
                color: 'white',
                fontSize: '0.625rem',
                padding: '0.125rem 0.375rem',
                borderRadius: '0.75rem',
                minWidth: '16px',
                textAlign: 'center'
              }}>
                {collaboration.chatMessages.length}
              </span>
            )}
          </div>
          <button
            onClick={() => setShowChat(!showChat)}
            style={{
              background: 'none',
              border: 'none',
              color: '#6366f1',
              cursor: 'pointer',
              fontSize: '0.75rem'
            }}
          >
            {showChat ? 'Hide' : 'Show'}
          </button>
        </div>

        {showChat && (
          <>
            {/* Chat Messages */}
            <div
              ref={chatMessagesRef}
              style={{
                maxHeight: '200px',
                overflowY: 'auto',
                padding: '0.75rem',
                background: '#f8fafc'
              }}
            >
              {collaboration.chatMessages.length === 0 ? (
                <p style={{
                  fontSize: '0.75rem',
                  color: '#6b7280',
                  textAlign: 'center',
                  fontStyle: 'italic'
                }}>
                  No messages yet. Start the conversation!
                </p>
              ) : (
                collaboration.chatMessages.map((message) => (
                  <div key={message.id} style={{ marginBottom: '0.75rem' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginBottom: '0.25rem'
                    }}>
                      <div style={{
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        background: '#e5e7eb',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.625rem',
                        fontWeight: '600',
                        color: '#374151'
                      }}>
                        {message.user.avatar || message.user.name.charAt(0).toUpperCase()}
                      </div>
                      <span style={{ fontSize: '0.75rem', fontWeight: '500', color: '#374151' }}>
                        {message.user.name}
                      </span>
                      <span style={{ fontSize: '0.625rem', color: '#6b7280' }}>
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                    <p style={{
                      fontSize: '0.75rem',
                      color: '#1f2937',
                      margin: '0 0 0 1.75rem',
                      wordWrap: 'break-word'
                    }}>
                      {message.message}
                    </p>
                  </div>
                ))
              )}
            </div>

            {/* Chat Input */}
            <form onSubmit={handleSendMessage} style={{ padding: '0.75rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="Type a message..."
                  disabled={!collaboration.isConnected}
                  style={{
                    flex: 1,
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    fontSize: '0.75rem',
                    outline: 'none'
                  }}
                />
                <button
                  type="submit"
                  disabled={!collaboration.isConnected || !chatMessage.trim()}
                  style={{
                    padding: '0.5rem',
                    background: collaboration.isConnected && chatMessage.trim() ? '#3b82f6' : '#9ca3af',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: collaboration.isConnected && chatMessage.trim() ? 'pointer' : 'not-allowed',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <Send size={14} />
                </button>
              </div>
            </form>
          </>
        )}
      </div>

      {/* Connection Status Footer */}
      {!collaboration.isConnected && (
        <div style={{
          padding: '0.75rem',
          background: '#fef3c7',
          borderTop: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <p style={{
            fontSize: '0.75rem',
            color: '#92400e',
            margin: 0
          }}>
            {collaboration.connectionState === 'connecting' 
              ? 'Connecting to collaboration...' 
              : 'Collaboration unavailable'
            }
          </p>
          <button
            onClick={collaboration.connect}
            style={{
              marginTop: '0.5rem',
              padding: '0.25rem 0.75rem',
              background: '#f59e0b',
              color: 'white',
              border: 'none',
              borderRadius: '0.25rem',
              fontSize: '0.75rem',
              cursor: 'pointer'
            }}
          >
            Reconnect
          </button>
        </div>
      )}
    </div>
  );
};

export default RealTimeCollaborationPanel;