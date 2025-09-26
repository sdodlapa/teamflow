import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useCollaboration } from './CollaborationProvider';

interface RealtimeCommentsProps {
  entityType: string;
  entityId: string;
  className?: string;
}

interface Comment {
  id: string;
  user_id: string;
  text: string;
  timestamp: string;
  is_temporary?: boolean;
}

interface TypingUser {
  user_id: string;
  timestamp: string;
}

export const RealtimeComments: React.FC<RealtimeCommentsProps> = ({
  entityType,
  entityId,
  className = ''
}) => {
  const { subscribeToMessages, sendMessage, sendTypingIndicator } = useCollaboration();
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef<number>();
  
  // Handle incoming real-time messages
  useEffect(() => {
    const unsubscribe = subscribeToMessages((message) => {
      if (message.type === 'new_comment' && 
          message.entity_type === entityType && 
          message.entity_id === entityId) {
        
        // Add new comment to list
        const comment: Comment = {
          id: `temp-${Date.now()}`,
          user_id: message.user_id!,
          text: message.text,
          timestamp: message.timestamp,
          is_temporary: true
        };
        
        setComments(prev => [...prev, comment]);
      }
      
      if (message.type === 'typing_indicator' && 
          message.entity_type === entityType && 
          message.entity_id === entityId) {
        
        setTypingUsers(prev => {
          const filtered = prev.filter(u => u.user_id !== message.user_id);
          
          if (message.is_typing) {
            return [...filtered, {
              user_id: message.user_id!,
              timestamp: message.timestamp
            }];
          } else {
            return filtered;
          }
        });
      }
    });
    
    return unsubscribe;
  }, [subscribeToMessages, entityType, entityId]);
  
  // Clean up old typing indicators
  useEffect(() => {
    const interval = setInterval(() => {
      const cutoff = new Date(Date.now() - 5000).toISOString(); // 5 seconds ago
      setTypingUsers(prev => prev.filter(u => u.timestamp > cutoff));
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Handle typing indicators
  const handleTyping = useCallback(() => {
    if (!isTyping) {
      setIsTyping(true);
      sendTypingIndicator(entityType, entityId, true);
    }
    
    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    // Set new timeout to stop typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      sendTypingIndicator(entityType, entityId, false);
    }, 2000);
  }, [isTyping, sendTypingIndicator, entityType, entityId]);
  
  // Handle comment submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newComment.trim()) return;
    
    // Send comment via WebSocket
    sendMessage({
      type: 'comment',
      entity_type: entityType,
      entity_id: entityId,
      text: newComment.trim(),
      timestamp: new Date().toISOString()
    });
    
    // Clear input
    setNewComment('');
    
    // Stop typing indicator
    if (isTyping) {
      setIsTyping(false);
      sendTypingIndicator(entityType, entityId, false);
    }
  };
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewComment(e.target.value);
    handleTyping();
  };
  
  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          Live Comments
        </h3>
        <p className="text-sm text-gray-600">
          Comments appear in real-time for all team members
        </p>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {/* Comments list */}
        <div className="space-y-3 p-4">
          {comments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">💬</div>
              <p>No comments yet. Start the conversation!</p>
            </div>
          ) : (
            comments.map((comment) => (
              <div 
                key={comment.id}
                className={`flex gap-3 p-3 rounded-lg ${
                  comment.is_temporary 
                    ? 'bg-blue-50 border-l-4 border-l-blue-400' 
                    : 'bg-gray-50'
                }`}
              >
                <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  {comment.user_id.charAt(0).toUpperCase()}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold text-gray-900">
                      User {comment.user_id}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(comment.timestamp).toLocaleTimeString()}
                    </span>
                    {comment.is_temporary && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                        Live
                      </span>
                    )}
                  </div>
                  <p className="text-gray-800">{comment.text}</p>
                </div>
              </div>
            ))
          )}
          
          {/* Typing indicators */}
          {typingUsers.length > 0 && (
            <div className="flex items-center gap-2 text-sm text-gray-600 px-3 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span>
                {typingUsers.length === 1 
                  ? `User ${typingUsers[0].user_id} is typing...`
                  : `${typingUsers.length} users are typing...`
                }
              </span>
            </div>
          )}
        </div>
      </div>
      
      {/* Comment input */}
      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={newComment}
            onChange={handleInputChange}
            placeholder="Add a comment..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={!newComment.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default RealtimeComments;