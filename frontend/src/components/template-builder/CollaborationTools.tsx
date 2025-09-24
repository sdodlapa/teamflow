import React, { useState, useEffect } from 'react';
import {
  Users,
  Share2,
  MessageSquare,
  Eye,
  Edit,
  User,
  Crown,
  Shield,
  UserPlus,
  Globe,
  Lock,
  Copy,
  Check,
  X,
  MoreHorizontal,
  Video,
  Activity,
  MessageCircle,
  Send
} from 'lucide-react';
import { DomainConfig, Entity, Relationship } from '../../types/template';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  status: 'online' | 'offline' | 'away';
  last_active: string;
  permissions: string[];
  joined_at: string;
}

interface Comment {
  id: string;
  author: TeamMember;
  content: string;
  timestamp: string;
  target_type: 'entity' | 'field' | 'relationship' | 'config';
  target_id: string;
  resolved: boolean;
  replies: Comment[];
}

interface ActivityEvent {
  id: string;
  user: TeamMember;
  action: 'created' | 'updated' | 'deleted' | 'commented' | 'shared';
  target_type: 'entity' | 'field' | 'relationship' | 'template';
  target_name: string;
  timestamp: string;
  description: string;
}

interface ShareSettings {
  visibility: 'private' | 'team' | 'organization' | 'public';
  allow_comments: boolean;
  allow_edits: boolean;
  require_approval: boolean;
  link_expires_at?: string;
}

interface CollaborationToolsProps {
  domainConfig: DomainConfig;
  entities: Entity[];
  relationships: Relationship[];
  onClose?: () => void;
}

const CollaborationTools: React.FC<CollaborationToolsProps> = ({
  domainConfig,
  entities,
  relationships,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'team' | 'comments' | 'activity' | 'sharing'>('team');
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [activities, setActivities] = useState<ActivityEvent[]>([]);
  const [shareSettings, setShareSettings] = useState<ShareSettings>({
    visibility: 'team',
    allow_comments: true,
    allow_edits: false,
    require_approval: true
  });
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [selectedTarget, setSelectedTarget] = useState<{type: string, id: string, name: string} | null>(null);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'editor' | 'viewer'>('viewer');
  const [shareLink, setShareLink] = useState('');
  const [linkCopied, setLinkCopied] = useState(false);

  useEffect(() => {
    loadTeamMembers();
    loadComments();
    loadActivities();
    generateShareLink();
  }, []);

  const loadTeamMembers = () => {
    const mockMembers: TeamMember[] = [
      {
        id: '1',
        name: 'John Doe',
        email: 'john@example.com',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
        role: 'owner',
        status: 'online',
        last_active: '2024-12-02T10:30:00Z',
        permissions: ['read', 'write', 'admin', 'share'],
        joined_at: '2024-11-01T00:00:00Z'
      },
      {
        id: '2',
        name: 'Jane Smith',
        email: 'jane@example.com',
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b765?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
        role: 'admin',
        status: 'online',
        last_active: '2024-12-02T09:45:00Z',
        permissions: ['read', 'write', 'admin'],
        joined_at: '2024-11-03T00:00:00Z'
      },
      {
        id: '3',
        name: 'Mike Johnson',
        email: 'mike@example.com',
        avatar: 'https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
        role: 'editor',
        status: 'away',
        last_active: '2024-12-02T08:20:00Z',
        permissions: ['read', 'write'],
        joined_at: '2024-11-05T00:00:00Z'
      },
      {
        id: '4',
        name: 'Sarah Wilson',
        email: 'sarah@example.com',
        avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
        role: 'viewer',
        status: 'offline',
        last_active: '2024-12-01T16:30:00Z',
        permissions: ['read'],
        joined_at: '2024-11-10T00:00:00Z'
      },
      {
        id: '5',
        name: 'Alex Chen',
        email: 'alex@example.com',
        role: 'editor',
        status: 'online',
        last_active: '2024-12-02T10:15:00Z',
        permissions: ['read', 'write'],
        joined_at: '2024-11-15T00:00:00Z'
      }
    ];
    setTeamMembers(mockMembers);
  };

  const loadComments = () => {
    const mockComments: Comment[] = [
      {
        id: '1',
        author: teamMembers.find(m => m.id === '2') || teamMembers[0],
        content: 'Should we add validation rules for the email field in the User entity?',
        timestamp: '2024-12-02T09:45:00Z',
        target_type: 'entity',
        target_id: 'user',
        resolved: false,
        replies: [
          {
            id: '1-1',
            author: teamMembers.find(m => m.id === '1') || teamMembers[0],
            content: 'Good point! Let\'s add regex validation and uniqueness constraint.',
            timestamp: '2024-12-02T10:00:00Z',
            target_type: 'entity',
            target_id: 'user',
            resolved: false,
            replies: []
          }
        ]
      },
      {
        id: '2',
        author: teamMembers.find(m => m.id === '3') || teamMembers[0],
        content: 'The relationship between Task and Project looks complex. Should we simplify?',
        timestamp: '2024-12-02T08:30:00Z',
        target_type: 'relationship',
        target_id: 'task-project',
        resolved: true,
        replies: []
      }
    ];
    setComments(mockComments);
  };

  const loadActivities = () => {
    const mockActivities: ActivityEvent[] = [
      {
        id: '1',
        user: teamMembers.find(m => m.id === '2') || teamMembers[0],
        action: 'updated',
        target_type: 'entity',
        target_name: 'User',
        timestamp: '2024-12-02T10:15:00Z',
        description: 'Added email validation field'
      },
      {
        id: '2',
        user: teamMembers.find(m => m.id === '1') || teamMembers[0],
        action: 'created',
        target_type: 'relationship',
        target_name: 'User-Role',
        timestamp: '2024-12-02T10:00:00Z',
        description: 'Created many-to-many relationship'
      },
      {
        id: '3',
        user: teamMembers.find(m => m.id === '3') || teamMembers[0],
        action: 'commented',
        target_type: 'entity',
        target_name: 'Task',
        timestamp: '2024-12-02T09:30:00Z',
        description: 'Left feedback on task structure'
      },
      {
        id: '4',
        user: teamMembers.find(m => m.id === '4') || teamMembers[0],
        action: 'shared',
        target_type: 'template',
        target_name: 'Template Configuration',
        timestamp: '2024-12-02T09:00:00Z',
        description: 'Shared template with external reviewer'
      }
    ];
    setActivities(mockActivities);
  };

  const generateShareLink = () => {
    const baseUrl = window.location.origin;
    const templateId = domainConfig.name.toLowerCase().replace(/\s+/g, '-');
    setShareLink(`${baseUrl}/templates/shared/${templateId}?token=${Math.random().toString(36).substr(2, 9)}`);
  };

  const handleInviteUser = () => {
    if (!inviteEmail.trim()) return;

    const newMember: TeamMember = {
      id: Date.now().toString(),
      name: inviteEmail.split('@')[0],
      email: inviteEmail,
      role: inviteRole,
      status: 'offline',
      last_active: new Date().toISOString(),
      permissions: inviteRole === 'editor' ? ['read', 'write'] : ['read'],
      joined_at: new Date().toISOString()
    };

    setTeamMembers([...teamMembers, newMember]);
    setInviteEmail('');
    setShowInviteDialog(false);
    
    // Simulate email invitation
    alert(`Invitation sent to ${inviteEmail}`);
  };

  const handleAddComment = () => {
    if (!newComment.trim() || !selectedTarget) return;

    const comment: Comment = {
      id: Date.now().toString(),
      author: teamMembers[0], // Current user
      content: newComment,
      timestamp: new Date().toISOString(),
      target_type: selectedTarget.type as any,
      target_id: selectedTarget.id,
      resolved: false,
      replies: []
    };

    setComments([comment, ...comments]);
    setNewComment('');
  };

  const copyShareLink = async () => {
    try {
      await navigator.clipboard.writeText(shareLink);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy link:', err);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner':
        return <Crown className="h-4 w-4 text-yellow-500" />;
      case 'admin':
        return <Shield className="h-4 w-4 text-purple-500" />;
      case 'editor':
        return <Edit className="h-4 w-4 text-blue-500" />;
      default:
        return <Eye className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-400';
      case 'away':
        return 'bg-yellow-400';
      default:
        return 'bg-gray-400';
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const past = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - past.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Collaboration Tools</h2>
            <p className="text-gray-600 mt-1">Real-time collaboration for {domainConfig.title}</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setActiveTab('sharing')}
              className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-2"
            >
              <Share2 className="h-4 w-4" />
              <span>Share</span>
            </button>
            
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'team', label: 'Team Members', icon: Users, count: teamMembers.length },
              { id: 'comments', label: 'Comments', icon: MessageSquare, count: comments.length },
              { id: 'activity', label: 'Activity', icon: Activity, count: activities.length },
              { id: 'sharing', label: 'Sharing & Permissions', icon: Share2 }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {activeTab === 'team' && (
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Team Members</h3>
                  <p className="text-gray-600">Manage who has access to this template</p>
                </div>
                
                <button
                  onClick={() => setShowInviteDialog(true)}
                  className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <UserPlus className="h-4 w-4" />
                  <span>Invite Member</span>
                </button>
              </div>

              <div className="space-y-4">
                {teamMembers.map(member => (
                  <div key={member.id} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="relative">
                          {member.avatar ? (
                            <img
                              src={member.avatar}
                              alt={member.name}
                              className="h-10 w-10 rounded-full"
                            />
                          ) : (
                            <div className="h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                              <User className="h-5 w-5 text-gray-500" />
                            </div>
                          )}
                          <div className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white ${getStatusColor(member.status)}`} />
                        </div>
                        
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-gray-900">{member.name}</span>
                            {getRoleIcon(member.role)}
                            <span className="text-sm text-gray-500 capitalize">{member.role}</span>
                          </div>
                          <div className="text-sm text-gray-600 flex items-center space-x-2">
                            <span>{member.email}</span>
                            <span>•</span>
                            <span>Last active {formatTimeAgo(member.last_active)}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1">
                          {member.status === 'online' && (
                            <div className="flex items-center space-x-1">
                              <MessageCircle className="h-4 w-4 text-blue-500 cursor-pointer hover:text-blue-600" />
                              <Video className="h-4 w-4 text-green-500 cursor-pointer hover:text-green-600" />
                            </div>
                          )}
                        </div>
                        
                        {member.role !== 'owner' && (
                          <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                            <MoreHorizontal className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-4">
                        <span className="text-gray-600">
                          Joined {new Date(member.joined_at).toLocaleDateString()}
                        </span>
                        <div className="flex items-center space-x-1">
                          <span className="text-gray-600">Permissions:</span>
                          <div className="flex space-x-1">
                            {member.permissions.map(permission => (
                              <span
                                key={permission}
                                className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs capitalize"
                              >
                                {permission}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'comments' && (
            <div className="max-w-4xl mx-auto">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Comments & Feedback</h3>
                <p className="text-gray-600">Discuss template elements with your team</p>
              </div>

              {/* Add Comment Form */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Comment on:
                  </label>
                  <select
                    value={selectedTarget ? `${selectedTarget.type}:${selectedTarget.id}` : ''}
                    onChange={(e) => {
                      if (e.target.value) {
                        const [type, id] = e.target.value.split(':');
                        const name = type === 'entity' 
                          ? entities.find(e => e.id === id)?.name 
                          : relationships.find(r => r.id === id)?.sourceEntityId + ' → ' + relationships.find(r => r.id === id)?.targetEntityId;
                        setSelectedTarget({ type, id, name: name || id });
                      } else {
                        setSelectedTarget(null);
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select target...</option>
                    <optgroup label="Entities">
                      {entities.map(entity => (
                        <option key={entity.id} value={`entity:${entity.id}`}>
                          {entity.name}
                        </option>
                      ))}
                    </optgroup>
                    <optgroup label="Relationships">
                      {relationships.map(rel => (
                        <option key={rel.id} value={`relationship:${rel.id}`}>
                          {rel.sourceEntityId} → {rel.targetEntityId}
                        </option>
                      ))}
                    </optgroup>
                  </select>
                </div>
                
                <div className="flex space-x-3">
                  <div className="flex-1">
                    <textarea
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="Add your comment or feedback..."
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    />
                  </div>
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim() || !selectedTarget}
                    className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <Send className="h-4 w-4" />
                    <span>Post</span>
                  </button>
                </div>
              </div>

              {/* Comments List */}
              <div className="space-y-4">
                {comments.map(comment => (
                  <div key={comment.id} className={`border rounded-lg p-4 ${comment.resolved ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {comment.author.avatar ? (
                          <img
                            src={comment.author.avatar}
                            alt={comment.author.name}
                            className="h-8 w-8 rounded-full"
                          />
                        ) : (
                          <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                            <User className="h-4 w-4 text-gray-500" />
                          </div>
                        )}
                        
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-gray-900">{comment.author.name}</span>
                            <span className="text-sm text-gray-500">{formatTimeAgo(comment.timestamp)}</span>
                          </div>
                          <div className="text-xs text-gray-600 flex items-center space-x-1">
                            <span>on</span>
                            <span className="font-medium capitalize">{comment.target_type}</span>
                            <span>•</span>
                            <span>{comment.target_id}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {comment.resolved ? (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                            Resolved
                          </span>
                        ) : (
                          <button className="px-2 py-1 bg-gray-100 text-gray-700 hover:bg-gray-200 text-xs rounded transition-colors">
                            Mark Resolved
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <p className="text-gray-800 mb-3">{comment.content}</p>
                    
                    {comment.replies.length > 0 && (
                      <div className="border-l-2 border-gray-200 pl-4 space-y-3">
                        {comment.replies.map(reply => (
                          <div key={reply.id} className="flex items-start space-x-3">
                            {reply.author.avatar ? (
                              <img
                                src={reply.author.avatar}
                                alt={reply.author.name}
                                className="h-6 w-6 rounded-full"
                              />
                            ) : (
                              <div className="h-6 w-6 bg-gray-200 rounded-full flex items-center justify-center">
                                <User className="h-3 w-3 text-gray-500" />
                              </div>
                            )}
                            
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="font-medium text-sm text-gray-900">{reply.author.name}</span>
                                <span className="text-xs text-gray-500">{formatTimeAgo(reply.timestamp)}</span>
                              </div>
                              <p className="text-sm text-gray-800">{reply.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'activity' && (
            <div className="max-w-4xl mx-auto">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Recent Activity</h3>
                <p className="text-gray-600">Track all changes and interactions with this template</p>
              </div>

              <div className="space-y-4">
                {activities.map(activity => (
                  <div key={activity.id} className="flex items-start space-x-4 p-4 bg-white border border-gray-200 rounded-lg">
                    {activity.user.avatar ? (
                      <img
                        src={activity.user.avatar}
                        alt={activity.user.name}
                        className="h-8 w-8 rounded-full"
                      />
                    ) : (
                      <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-gray-500" />
                      </div>
                    )}
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium text-gray-900">{activity.user.name}</span>
                        <span className={`px-2 py-0.5 text-xs rounded ${
                          activity.action === 'created' ? 'bg-green-100 text-green-700' :
                          activity.action === 'updated' ? 'bg-blue-100 text-blue-700' :
                          activity.action === 'deleted' ? 'bg-red-100 text-red-700' :
                          activity.action === 'commented' ? 'bg-purple-100 text-purple-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {activity.action}
                        </span>
                        <span className="text-sm text-gray-500">{activity.target_type}</span>
                        <span className="font-medium text-sm text-gray-900">{activity.target_name}</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{activity.description}</p>
                      <span className="text-xs text-gray-500">{formatTimeAgo(activity.timestamp)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'sharing' && (
            <div className="max-w-4xl mx-auto">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Sharing & Permissions</h3>
                <p className="text-gray-600">Control who can access and modify this template</p>
              </div>

              <div className="space-y-6">
                {/* Visibility Settings */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Visibility Settings</h4>
                  
                  <div className="space-y-3">
                    {[
                      { value: 'private', icon: Lock, label: 'Private', desc: 'Only team members can access' },
                      { value: 'team', icon: Users, label: 'Team', desc: 'All organization members can view' },
                      { value: 'organization', icon: Shield, label: 'Organization', desc: 'Anyone in your organization' },
                      { value: 'public', icon: Globe, label: 'Public', desc: 'Anyone with the link can view' }
                    ].map(option => (
                      <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                        <input
                          type="radio"
                          name="visibility"
                          value={option.value}
                          checked={shareSettings.visibility === option.value}
                          onChange={(e) => setShareSettings({...shareSettings, visibility: e.target.value as any})}
                          className="mt-1"
                        />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <option.icon className="h-4 w-4 text-gray-500" />
                            <span className="font-medium text-gray-900">{option.label}</span>
                          </div>
                          <p className="text-sm text-gray-600">{option.desc}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Permission Settings */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Permission Settings</h4>
                  
                  <div className="space-y-3">
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-gray-900">Allow Comments</span>
                        <p className="text-sm text-gray-600">Let viewers leave feedback and suggestions</p>
                      </div>
                      <input
                        type="checkbox"
                        checked={shareSettings.allow_comments}
                        onChange={(e) => setShareSettings({...shareSettings, allow_comments: e.target.checked})}
                        className="rounded"
                      />
                    </label>
                    
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-gray-900">Allow Edits</span>
                        <p className="text-sm text-gray-600">Allow others to make changes to the template</p>
                      </div>
                      <input
                        type="checkbox"
                        checked={shareSettings.allow_edits}
                        onChange={(e) => setShareSettings({...shareSettings, allow_edits: e.target.checked})}
                        className="rounded"
                      />
                    </label>
                    
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-gray-900">Require Approval</span>
                        <p className="text-sm text-gray-600">Review changes before they're applied</p>
                      </div>
                      <input
                        type="checkbox"
                        checked={shareSettings.require_approval}
                        onChange={(e) => setShareSettings({...shareSettings, require_approval: e.target.checked})}
                        className="rounded"
                      />
                    </label>
                  </div>
                </div>

                {/* Share Link */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Share Link</h4>
                  
                  <div className="flex items-center space-x-3">
                    <div className="flex-1">
                      <input
                        type="text"
                        value={shareLink}
                        readOnly
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 text-sm"
                      />
                    </div>
                    
                    <button
                      onClick={copyShareLink}
                      className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-2"
                    >
                      {linkCopied ? (
                        <>
                          <Check className="h-4 w-4" />
                          <span>Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  
                  <p className="text-sm text-gray-600 mt-2">
                    Anyone with this link can {shareSettings.visibility === 'private' ? 'view' : shareSettings.allow_edits ? 'view and edit' : 'view'} this template
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Invite Dialog */}
      {showInviteDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Invite Team Member</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@company.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="viewer">Viewer - Can view only</option>
                  <option value="editor">Editor - Can view and edit</option>
                </select>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowInviteDialog(false)}
                className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleInviteUser}
                disabled={!inviteEmail.trim()}
                className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
              >
                Send Invitation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollaborationTools;