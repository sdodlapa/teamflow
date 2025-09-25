import React, { useState, useEffect, useRef } from 'react';
import {
  Send, Smile, Paperclip, Phone, Video,
  Search, Settings, Users, Hash, Lock, Globe,
  MessageCircle, Reply, Edit3, Trash2,
  ThumbsUp, Mic, MicOff, Image, File, Plus, X,
  Check, CheckCheck, Clock, User
} from 'lucide-react';
import './RealTimeChatSystem.css';

interface User {
  id: string;
  name: string;
  username: string;
  avatar?: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  lastSeen?: string;
  role?: string;
}

interface Message {
  id: string;
  senderId: string;
  content: string;
  timestamp: string;
  type: 'text' | 'image' | 'file' | 'system' | 'voice';
  editedAt?: string;
  replyTo?: string;
  reactions: {
    emoji: string;
    users: string[];
  }[];
  status: 'sending' | 'sent' | 'delivered' | 'read';
  metadata?: {
    fileName?: string;
    fileSize?: number;
    fileType?: string;
    duration?: number;
    imageUrl?: string;
    thumbnailUrl?: string;
  };
}

interface Channel {
  id: string;
  name: string;
  type: 'direct' | 'group' | 'channel' | 'project';
  description?: string;
  isPrivate: boolean;
  memberCount: number;
  unreadCount: number;
  lastMessage?: Message;
  members: User[];
  createdBy: string;
  createdAt: string;
  settings: {
    notifications: boolean;
    pinned: boolean;
    archived: boolean;
  };
}

interface RealTimeChatSystemProps {
  userId: string;
  initialChannelId?: string;
  onChannelChange?: (channelId: string) => void;
}

export const RealTimeChatSystem: React.FC<RealTimeChatSystemProps> = ({
  userId,
  initialChannelId,
  onChannelChange
}) => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [activeChannelId, setActiveChannelId] = useState<string>(initialChannelId || '');
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageInput, setMessageInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showChannelList, setShowChannelList] = useState(true);
  const [showUserList, setShowUserList] = useState(false);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [replyToMessage, setReplyToMessage] = useState<Message | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [typingUsers] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [onlineUsers, setOnlineUsers] = useState<User[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageInputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Mock data
  const generateMockChannels = (): Channel[] => {
    return [
      {
        id: 'channel-1',
        name: 'General',
        type: 'channel',
        description: 'General team discussions',
        isPrivate: false,
        memberCount: 15,
        unreadCount: 3,
        members: [],
        createdBy: 'admin',
        createdAt: '2024-01-01',
        settings: {
          notifications: true,
          pinned: true,
          archived: false
        }
      },
      {
        id: 'dm-1',
        name: 'John Doe',
        type: 'direct',
        isPrivate: true,
        memberCount: 2,
        unreadCount: 1,
        members: [],
        createdBy: userId,
        createdAt: '2024-01-15',
        settings: {
          notifications: true,
          pinned: false,
          archived: false
        }
      },
      {
        id: 'project-1',
        name: 'Project Alpha',
        type: 'project',
        description: 'Project Alpha development team',
        isPrivate: true,
        memberCount: 8,
        unreadCount: 0,
        members: [],
        createdBy: 'pm-1',
        createdAt: '2024-01-10',
        settings: {
          notifications: true,
          pinned: false,
          archived: false
        }
      },
      {
        id: 'group-1',
        name: 'Design Team',
        type: 'group',
        description: 'Design team coordination',
        isPrivate: false,
        memberCount: 5,
        unreadCount: 7,
        members: [],
        createdBy: 'design-lead',
        createdAt: '2024-01-05',
        settings: {
          notifications: true,
          pinned: true,
          archived: false
        }
      }
    ];
  };

  const generateMockMessages = (): Message[] => {
    return [
      {
        id: 'msg-1',
        senderId: 'user-1',
        content: 'Hey everyone! How\'s the project coming along?',
        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        type: 'text',
        reactions: [
          { emoji: '👍', users: ['user-2', 'user-3'] },
          { emoji: '❤️', users: ['user-4'] }
        ],
        status: 'read'
      },
      {
        id: 'msg-2',
        senderId: 'user-2',
        content: 'Making great progress! Just finished the authentication module.',
        timestamp: new Date(Date.now() - 55 * 60 * 1000).toISOString(),
        type: 'text',
        reactions: [],
        status: 'read',
        replyTo: 'msg-1'
      },
      {
        id: 'msg-3',
        senderId: 'user-3',
        content: 'Check out this mockup for the dashboard',
        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        type: 'image',
        reactions: [
          { emoji: '🎨', users: ['user-1', 'user-2'] }
        ],
        status: 'read',
        metadata: {
          imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop',
          thumbnailUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=200&h=150&fit=crop'
        }
      },
      {
        id: 'msg-4',
        senderId: userId,
        content: 'Looks amazing! Can we schedule a review meeting?',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        type: 'text',
        reactions: [],
        status: 'delivered',
        replyTo: 'msg-3'
      },
      {
        id: 'msg-5',
        senderId: 'user-4',
        content: 'project-requirements.pdf',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        type: 'file',
        reactions: [],
        status: 'read',
        metadata: {
          fileName: 'project-requirements.pdf',
          fileSize: 2048000,
          fileType: 'application/pdf'
        }
      },
      {
        id: 'msg-6',
        senderId: 'user-1',
        content: 'Sure! How about 3 PM today?',
        timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        type: 'text',
        reactions: [],
        status: 'read'
      },
      {
        id: 'msg-7',
        senderId: userId,
        content: 'Perfect! I\'ll send out the calendar invite.',
        timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        type: 'text',
        reactions: [],
        status: 'sending'
      }
    ];
  };

  const generateMockUsers = (): User[] => {
    return [
      {
        id: 'user-1',
        name: 'John Doe',
        username: 'johndoe',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
        status: 'online',
        role: 'Developer'
      },
      {
        id: 'user-2',
        name: 'Jane Smith',
        username: 'janesmith',
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b6fd?w=100&h=100&fit=crop&crop=face',
        status: 'online',
        role: 'Designer'
      },
      {
        id: 'user-3',
        name: 'Mike Johnson',
        username: 'mikejohnson',
        avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
        status: 'away',
        role: 'Project Manager'
      },
      {
        id: 'user-4',
        name: 'Sarah Wilson',
        username: 'sarahwilson',
        avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
        status: 'busy',
        role: 'QA Engineer'
      }
    ];
  };

  useEffect(() => {
    setIsLoading(true);
    setTimeout(() => {
      const mockChannels = generateMockChannels();
      const mockUsers = generateMockUsers();
      setChannels(mockChannels);
      setOnlineUsers(mockUsers);
      
      if (!activeChannelId && mockChannels.length > 0) {
        setActiveChannelId(mockChannels[0].id);
      }
      
      if (activeChannelId) {
        const mockMessages = generateMockMessages();
        setMessages(mockMessages);
      }
      
      setIsLoading(false);
    }, 1000);
  }, [activeChannelId]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (onChannelChange && activeChannelId) {
      onChannelChange(activeChannelId);
    }
  }, [activeChannelId, onChannelChange]);

  const handleSendMessage = () => {
    if (!messageInput.trim() || !activeChannelId) return;

    const newMessage: Message = {
      id: `msg-${Date.now()}`,
      senderId: userId,
      content: messageInput,
      timestamp: new Date().toISOString(),
      type: 'text',
      reactions: [],
      status: 'sending',
      replyTo: replyToMessage?.id
    };

    setMessages(prev => [...prev, newMessage]);
    setMessageInput('');
    setReplyToMessage(null);

    // Simulate message delivery
    setTimeout(() => {
      setMessages(prev => prev.map(msg =>
        msg.id === newMessage.id ? { ...msg, status: 'delivered' } : msg
      ));
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleReaction = (messageId: string, emoji: string) => {
    setMessages(prev => prev.map(msg => {
      if (msg.id === messageId) {
        const existingReaction = msg.reactions.find(r => r.emoji === emoji);
        if (existingReaction) {
          if (existingReaction.users.includes(userId)) {
            // Remove reaction
            return {
              ...msg,
              reactions: msg.reactions.map(r =>
                r.emoji === emoji
                  ? { ...r, users: r.users.filter(u => u !== userId) }
                  : r
              ).filter(r => r.users.length > 0)
            };
          } else {
            // Add reaction
            return {
              ...msg,
              reactions: msg.reactions.map(r =>
                r.emoji === emoji
                  ? { ...r, users: [...r.users, userId] }
                  : r
              )
            };
          }
        } else {
          // New reaction
          return {
            ...msg,
            reactions: [...msg.reactions, { emoji, users: [userId] }]
          };
        }
      }
      return msg;
    }));
  };

  const handleEditMessage = (messageId: string, newContent: string) => {
    setMessages(prev => prev.map(msg =>
      msg.id === messageId
        ? { ...msg, content: newContent, editedAt: new Date().toISOString() }
        : msg
    ));
    setEditingMessageId(null);
  };

  const handleDeleteMessage = (messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  };

  const getStatusIcon = (status: Message['status']) => {
    switch (status) {
      case 'sending':
        return <Clock size={12} className="status-icon sending" />;
      case 'sent':
        return <Check size={12} className="status-icon sent" />;
      case 'delivered':
        return <CheckCheck size={12} className="status-icon delivered" />;
      case 'read':
        return <CheckCheck size={12} className="status-icon read" />;
      default:
        return null;
    }
  };

  const getChannelIcon = (channel: Channel) => {
    switch (channel.type) {
      case 'direct':
        return <User size={16} />;
      case 'group':
        return <Users size={16} />;
      case 'channel':
        return channel.isPrivate ? <Lock size={16} /> : <Hash size={16} />;
      case 'project':
        return <Globe size={16} />;
      default:
        return <Hash size={16} />;
    }
  };

  const getUserById = (id: string): User | undefined => {
    return onlineUsers.find(user => user.id === id);
  };

  const activeChannel = channels.find(c => c.id === activeChannelId);

  const renderMessage = (message: Message, index: number) => {
    const sender = getUserById(message.senderId);
    const isOwnMessage = message.senderId === userId;
    const previousMessage = index > 0 ? messages[index - 1] : null;
    const showSender = !previousMessage || previousMessage.senderId !== message.senderId;
    const replyToMsg = message.replyTo ? messages.find(m => m.id === message.replyTo) : null;

    return (
      <div
        key={message.id}
        className={`message ${isOwnMessage ? 'own-message' : ''} ${showSender ? 'show-sender' : ''}`}
      >
        {showSender && !isOwnMessage && (
          <div className="message-sender">
            {sender?.avatar ? (
              <img src={sender.avatar} alt={sender.name} className="sender-avatar" />
            ) : (
              <div className="sender-avatar-placeholder">
                <User size={16} />
              </div>
            )}
          </div>
        )}

        <div className="message-content">
          {showSender && !isOwnMessage && (
            <div className="message-header">
              <span className="sender-name">{sender?.name || 'Unknown User'}</span>
              <span className="message-time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>
          )}

          {replyToMsg && (
            <div className="reply-preview">
              <div className="reply-line" />
              <div className="reply-content">
                <span className="reply-author">
                  {getUserById(replyToMsg.senderId)?.name || 'Unknown'}
                </span>
                <span className="reply-text">
                  {replyToMsg.content.length > 50
                    ? `${replyToMsg.content.substring(0, 50)}...`
                    : replyToMsg.content
                  }
                </span>
              </div>
            </div>
          )}

          <div className="message-body">
            {editingMessageId === message.id ? (
              <div className="edit-input">
                <textarea
                  defaultValue={message.content}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleEditMessage(message.id, e.currentTarget.value);
                    } else if (e.key === 'Escape') {
                      setEditingMessageId(null);
                    }
                  }}
                  autoFocus
                />
              </div>
            ) : (
              <>
                {message.type === 'text' && (
                  <div className="text-content">
                    {message.content}
                    {message.editedAt && <span className="edited-indicator">(edited)</span>}
                  </div>
                )}

                {message.type === 'image' && message.metadata?.imageUrl && (
                  <div className="image-content">
                    <img
                      src={message.metadata.imageUrl}
                      alt="Shared image"
                      className="message-image"
                    />
                  </div>
                )}

                {message.type === 'file' && message.metadata && (
                  <div className="file-content">
                    <File size={20} />
                    <div className="file-info">
                      <span className="file-name">{message.metadata.fileName}</span>
                      <span className="file-size">
                        {((message.metadata.fileSize || 0) / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </div>
                  </div>
                )}
              </>
            )}

            <div className="message-actions">
              {message.reactions.length > 0 && (
                <div className="message-reactions">
                  {message.reactions.map((reaction, idx) => (
                    <button
                      key={idx}
                      className={`reaction-btn ${
                        reaction.users.includes(userId) ? 'user-reacted' : ''
                      }`}
                      onClick={() => handleReaction(message.id, reaction.emoji)}
                    >
                      {reaction.emoji} {reaction.users.length}
                    </button>
                  ))}
                </div>
              )}

              <div className="message-meta">
                {isOwnMessage && getStatusIcon(message.status)}
                <div className="message-options">
                  <button
                    className="message-option-btn"
                    onClick={() => handleReaction(message.id, '👍')}
                  >
                    <ThumbsUp size={12} />
                  </button>
                  <button
                    className="message-option-btn"
                    onClick={() => setReplyToMessage(message)}
                  >
                    <Reply size={12} />
                  </button>
                  {isOwnMessage && (
                    <>
                      <button
                        className="message-option-btn"
                        onClick={() => setEditingMessageId(message.id)}
                      >
                        <Edit3 size={12} />
                      </button>
                      <button
                        className="message-option-btn"
                        onClick={() => handleDeleteMessage(message.id)}
                      >
                        <Trash2 size={12} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="chat-system">
      <div className={`channel-sidebar ${showChannelList ? 'visible' : 'hidden'}`}>
        <div className="sidebar-header">
          <h2>Channels</h2>
          <button className="add-channel-btn">
            <Plus size={16} />
          </button>
        </div>

        <div className="channel-search">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search channels..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="channel-list">
          {channels
            .filter(channel =>
              channel.name.toLowerCase().includes(searchQuery.toLowerCase())
            )
            .map(channel => (
              <button
                key={channel.id}
                className={`channel-item ${channel.id === activeChannelId ? 'active' : ''}`}
                onClick={() => setActiveChannelId(channel.id)}
              >
                <div className="channel-icon">
                  {getChannelIcon(channel)}
                </div>
                <div className="channel-info">
                  <span className="channel-name">{channel.name}</span>
                  {channel.unreadCount > 0 && (
                    <span className="unread-count">{channel.unreadCount}</span>
                  )}
                </div>
              </button>
            ))}
        </div>

        <div className="online-users">
          <h3>Online Users</h3>
          {onlineUsers
            .filter(user => user.status === 'online')
            .map(user => (
              <div key={user.id} className="online-user">
                <div className="user-avatar">
                  {user.avatar ? (
                    <img src={user.avatar} alt={user.name} />
                  ) : (
                    <User size={16} />
                  )}
                  <div className={`status-indicator ${user.status}`} />
                </div>
                <span className="user-name">{user.name}</span>
              </div>
            ))}
        </div>
      </div>

      <div className="chat-main">
        <div className="chat-header">
          <button
            className="toggle-sidebar-btn"
            onClick={() => setShowChannelList(!showChannelList)}
          >
            <MessageCircle size={20} />
          </button>

          <div className="channel-info">
            <div className="channel-icon">
              {activeChannel && getChannelIcon(activeChannel)}
            </div>
            <div>
              <h3>{activeChannel?.name}</h3>
              {activeChannel?.description && (
                <p className="channel-description">{activeChannel.description}</p>
              )}
            </div>
          </div>

          <div className="chat-actions">
            <button className="chat-action-btn">
              <Phone size={16} />
            </button>
            <button className="chat-action-btn">
              <Video size={16} />
            </button>
            <button className="chat-action-btn">
              <Settings size={16} />
            </button>
            <button
              className="chat-action-btn"
              onClick={() => setShowUserList(!showUserList)}
            >
              <Users size={16} />
            </button>
          </div>
        </div>

        <div className="messages-container">
          {isLoading ? (
            <div className="loading-state">
              <MessageCircle size={32} />
              <p>Loading messages...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="empty-state">
              <MessageCircle size={48} />
              <h3>No messages yet</h3>
              <p>Start the conversation by sending a message!</p>
            </div>
          ) : (
            <div className="messages-list">
              {messages.map((message, index) => renderMessage(message, index))}
              <div ref={messagesEndRef} />
            </div>
          )}

          {typingUsers.length > 0 && (
            <div className="typing-indicator">
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="typing-text">
                {typingUsers.join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
              </span>
            </div>
          )}
        </div>

        <div className="message-input-container">
          {replyToMessage && (
            <div className="reply-preview-input">
              <div className="reply-info">
                <Reply size={14} />
                <span>
                  Replying to {getUserById(replyToMessage.senderId)?.name}
                </span>
                <button
                  className="cancel-reply-btn"
                  onClick={() => setReplyToMessage(null)}
                >
                  <X size={14} />
                </button>
              </div>
              <div className="reply-content-preview">
                {replyToMessage.content.length > 100
                  ? `${replyToMessage.content.substring(0, 100)}...`
                  : replyToMessage.content
                }
              </div>
            </div>
          )}

          <div className="message-input">
            <div className="input-actions">
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                multiple
                accept="image/*,video/*,.pdf,.doc,.docx,.txt"
              />
              <button
                className="input-action-btn"
                onClick={() => fileInputRef.current?.click()}
              >
                <Paperclip size={16} />
              </button>
              <button className="input-action-btn">
                <Image size={16} />
              </button>
              <button
                className={`input-action-btn ${isRecording ? 'recording' : ''}`}
                onClick={() => setIsRecording(!isRecording)}
              >
                {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
              </button>
            </div>

            <textarea
              ref={messageInputRef}
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              rows={1}
              className="message-textarea"
            />

            <div className="send-actions">
              <button className="emoji-btn">
                <Smile size={16} />
              </button>
              <button
                className="send-btn"
                onClick={handleSendMessage}
                disabled={!messageInput.trim()}
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {showUserList && (
        <div className="user-sidebar">
          <div className="sidebar-header">
            <h3>Members</h3>
            <button
              className="close-sidebar-btn"
              onClick={() => setShowUserList(false)}
            >
              <X size={16} />
            </button>
          </div>

          <div className="user-list">
            {onlineUsers.map(user => (
              <div key={user.id} className="user-item">
                <div className="user-avatar">
                  {user.avatar ? (
                    <img src={user.avatar} alt={user.name} />
                  ) : (
                    <User size={20} />
                  )}
                  <div className={`status-indicator ${user.status}`} />
                </div>
                <div className="user-info">
                  <span className="user-name">{user.name}</span>
                  <span className="user-role">{user.role}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};