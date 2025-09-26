/**
 * Template Management - Day 13 Implementation
 * Edit, delete, version, clone, and manage existing templates
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  Save, 
  ArrowLeft, 
  Edit3,
  Trash2,
  Copy,
  Share2,
  History,
  Settings,
  Eye,
  AlertTriangle,
  CheckCircle,
  User,
  Plus,
  MoreVertical,
  Lock,
  Unlock
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingComponents';

// Template Management interfaces
interface TemplateVersion {
  id: string;
  version: string;
  description: string;
  author: string;
  created_at: string;
  is_current: boolean;
  changes: string[];
  size: string;
}

interface TemplatePermission {
  user_id: string;
  user_name: string;
  permission: 'view' | 'edit' | 'admin';
  granted_at: string;
  granted_by: string;
}

interface ManagedTemplate {
  id: string;
  name: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  entities: any[];
  relationships: any[];
  workflows: any[];
  version: string;
  author: string;
  created_at: string;
  updated_at: string;
  is_public: boolean;
  is_official: boolean;
  usage_count: number;
  rating: number;
  total_ratings: number;
  versions: TemplateVersion[];
  permissions: TemplatePermission[];
  metadata: {
    total_entities: number;
    total_fields: number;
    total_relationships: number;
    complexity_score: number;
  };
}

interface CloneOptions {
  new_name: string;
  new_title: string;
  copy_versions: boolean;
  copy_permissions: boolean;
  make_private: boolean;
}

export const TemplateManagement: React.FC = () => {
  const navigate = useNavigate();
  const { templateId } = useParams<{ templateId: string }>();
  
  // State management
  const [template, setTemplate] = useState<ManagedTemplate | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'edit' | 'versions' | 'permissions' | 'settings'>('edit');
  
  // Modals and operations
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [showVersionModal, setShowVersionModal] = useState(false);
  
  // Form states
  const [editedTemplate, setEditedTemplate] = useState<Partial<ManagedTemplate>>({});
  const [cloneOptions, setCloneOptions] = useState<CloneOptions>({
    new_name: '',
    new_title: '',
    copy_versions: false,
    copy_permissions: false,
    make_private: true
  });
  const [versionDescription, setVersionDescription] = useState('');
  const [newPermission, setNewPermission] = useState({ user_name: '', permission: 'view' as const });

  // Load template data
  useEffect(() => {
    const loadTemplate = async () => {
      try {
        setLoading(true);
        
        if (!templateId) {
          throw new Error('Template ID is required');
        }

        // Simulate loading template for management
        // In real implementation: await fetch(`/api/v1/templates/${templateId}/manage`)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const mockTemplate: ManagedTemplate = {
          id: templateId,
          name: 'task_management_pro',
          title: 'Task Management Pro',
          description: 'Advanced task management system with team collaboration, time tracking, and project analytics. Perfect for growing teams and complex project workflows.',
          category: 'business',
          tags: ['tasks', 'projects', 'collaboration', 'analytics', 'time-tracking'],
          entities: [
            { name: 'Task', fields: 12, relationships: 3 },
            { name: 'Project', fields: 8, relationships: 4 },
            { name: 'User', fields: 6, relationships: 2 },
            { name: 'Team', fields: 5, relationships: 3 }
          ],
          relationships: [
            { from: 'Task', to: 'Project', type: 'belongs_to' },
            { from: 'Task', to: 'User', type: 'assigned_to' },
            { from: 'User', to: 'Team', type: 'member_of' }
          ],
          workflows: [
            { name: 'Task Creation', steps: 5 },
            { name: 'Project Setup', steps: 8 }
          ],
          version: '2.1.0',
          author: 'TeamFlow Admin',
          created_at: '2025-08-15T10:00:00Z',
          updated_at: '2025-09-20T14:30:00Z',
          is_public: true,
          is_official: true,
          usage_count: 1250,
          rating: 4.9,
          total_ratings: 234,
          versions: [
            {
              id: 'v2.1.0',
              version: '2.1.0',
              description: 'Added advanced analytics and reporting features',
              author: 'TeamFlow Admin',
              created_at: '2025-09-20T14:30:00Z',
              is_current: true,
              changes: [
                'Added analytics dashboard',
                'Enhanced reporting system', 
                'Improved performance',
                'Bug fixes and optimizations'
              ],
              size: '2.4 MB'
            },
            {
              id: 'v2.0.0',
              version: '2.0.0',
              description: 'Major update with workflow automation',
              author: 'TeamFlow Admin',
              created_at: '2025-09-01T09:15:00Z',
              is_current: false,
              changes: [
                'Added workflow automation',
                'New user interface',
                'Enhanced security features'
              ],
              size: '2.1 MB'
            },
            {
              id: 'v1.5.0',
              version: '1.5.0',
              description: 'Added team collaboration features',
              author: 'TeamFlow Admin',
              created_at: '2025-08-20T16:45:00Z',
              is_current: false,
              changes: [
                'Team collaboration tools',
                'Real-time notifications',
                'Improved task assignment'
              ],
              size: '1.8 MB'
            }
          ],
          permissions: [
            {
              user_id: 'user1',
              user_name: 'Alice Johnson',
              permission: 'admin',
              granted_at: '2025-08-15T10:00:00Z',
              granted_by: 'System'
            },
            {
              user_id: 'user2',
              user_name: 'Bob Smith',
              permission: 'edit',
              granted_at: '2025-09-01T12:00:00Z',
              granted_by: 'Alice Johnson'
            },
            {
              user_id: 'user3',
              user_name: 'Carol Davis',
              permission: 'view',
              granted_at: '2025-09-15T14:20:00Z',
              granted_by: 'Alice Johnson'
            }
          ],
          metadata: {
            total_entities: 4,
            total_fields: 31,
            total_relationships: 7,
            complexity_score: 8.5
          }
        };
        
        setTemplate(mockTemplate);
        setEditedTemplate(mockTemplate);
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load template');
      } finally {
        setLoading(false);
      }
    };

    loadTemplate();
  }, [templateId]);

  // Handle template save
  const handleSaveTemplate = async () => {
    if (!template || !editedTemplate) return;
    
    try {
      setSaving(true);
      
      // Simulate save operation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update template with edited data
      const updatedTemplate = {
        ...template,
        ...editedTemplate,
        updated_at: new Date().toISOString(),
        version: incrementVersion(template.version)
      };
      
      setTemplate(updatedTemplate);
      setEditedTemplate(updatedTemplate);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save template');
    } finally {
      setSaving(false);
    }
  };

  // Handle template deletion
  const handleDeleteTemplate = async () => {
    if (!template) return;
    
    try {
      // Simulate deletion
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Navigate back to templates list
      navigate('/templates');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete template');
    }
    
    setShowDeleteModal(false);
  };

  // Handle template cloning
  const handleCloneTemplate = async () => {
    if (!template) return;
    
    try {
      // Simulate cloning
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const clonedId = `${template.id}_clone_${Date.now()}`;
      
      // Navigate to the cloned template
      navigate(`/templates/manage/${clonedId}`);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clone template');
    }
    
    setShowCloneModal(false);
  };

  // Handle version creation
  const handleCreateVersion = async () => {
    if (!template || !versionDescription.trim()) return;
    
    try {
      const newVersion: TemplateVersion = {
        id: `v${incrementVersion(template.version)}`,
        version: incrementVersion(template.version),
        description: versionDescription,
        author: 'Current User',
        created_at: new Date().toISOString(),
        is_current: true,
        changes: ['Manual version creation'],
        size: '2.5 MB'
      };
      
      // Update versions list
      const updatedVersions = template.versions.map(v => ({ ...v, is_current: false }));
      updatedVersions.unshift(newVersion);
      
      setTemplate({
        ...template,
        versions: updatedVersions,
        version: newVersion.version
      });
      
      setVersionDescription('');
      setShowVersionModal(false);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create version');
    }
  };

  // Helper functions
  const incrementVersion = (version: string): string => {
    const parts = version.split('.').map(Number);
    parts[2] += 1;
    return parts.join('.');
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPermissionColor = (permission: string): string => {
    switch (permission) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'edit': return 'bg-blue-100 text-blue-800';
      case 'view': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Render functions
  const renderEditTab = () => (
    <div className="space-y-6">
      {/* Basic Information */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Template Name</label>
            <input
              type="text"
              value={editedTemplate.name || ''}
              onChange={(e) => setEditedTemplate({...editedTemplate, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Display Title</label>
            <input
              type="text"
              value={editedTemplate.title || ''}
              onChange={(e) => setEditedTemplate({...editedTemplate, title: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            value={editedTemplate.description || ''}
            onChange={(e) => setEditedTemplate({...editedTemplate, description: e.target.value})}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={editedTemplate.category || ''}
              onChange={(e) => setEditedTemplate({...editedTemplate, category: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="business">Business</option>
              <option value="ecommerce">E-commerce</option>
              <option value="healthcare">Healthcare</option>
              <option value="education">Education</option>
              <option value="finance">Finance</option>
              <option value="technology">Technology</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
            <input
              type="text"
              value={editedTemplate.tags?.join(', ') || ''}
              onChange={(e) => setEditedTemplate({...editedTemplate, tags: e.target.value.split(',').map(t => t.trim())})}
              placeholder="Enter tags separated by commas"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Template Structure */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Template Structure</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{template?.metadata.total_entities}</div>
            <div className="text-sm text-blue-700">Entities</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{template?.metadata.total_fields}</div>
            <div className="text-sm text-green-700">Fields</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{template?.metadata.total_relationships}</div>
            <div className="text-sm text-purple-700">Relationships</div>
          </div>
        </div>
      </div>

      {/* Save Actions */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={() => navigate('/templates')}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
        >
          Cancel
        </button>
        
        <button
          onClick={handleSaveTemplate}
          disabled={saving}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? (
            <>
              <LoadingSpinner />
              <span className="ml-2">Saving...</span>
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </>
          )}
        </button>
      </div>
    </div>
  );

  const renderVersionsTab = () => (
    <div className="space-y-6">
      {/* Create New Version */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Version History</h3>
          <button
            onClick={() => setShowVersionModal(true)}
            className="flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Version
          </button>
        </div>
        
        <div className="space-y-4">
          {template?.versions.map(version => (
            <div key={version.id} className={`p-4 border rounded-lg ${
              version.is_current ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`px-2 py-1 text-xs rounded-full font-medium ${
                    version.is_current 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    v{version.version}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{version.description}</h4>
                    <p className="text-sm text-gray-600">
                      By {version.author} • {formatDate(version.created_at)} • {version.size}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {version.is_current && (
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                      Current
                    </span>
                  )}
                  <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              {version.changes.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-gray-700 mb-1">Changes:</p>
                  <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                    {version.changes.map((change, index) => (
                      <li key={index}>{change}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderPermissionsTab = () => (
    <div className="space-y-6">
      {/* Current Permissions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Access Permissions</h3>
        
        <div className="space-y-3">
          {template?.permissions.map(permission => (
            <div key={permission.user_id} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-gray-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{permission.user_name}</p>
                  <p className="text-sm text-gray-600">
                    Added by {permission.granted_by} • {formatDate(permission.granted_at)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded-full ${getPermissionColor(permission.permission)}`}>
                  {permission.permission}
                </span>
                <button className="p-1 text-gray-400 hover:text-red-600 rounded">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
        
        {/* Add New Permission */}
        <div className="mt-6 pt-6 border-t">
          <h4 className="font-medium text-gray-900 mb-3">Add New Permission</h4>
          <div className="flex space-x-3">
            <input
              type="text"
              placeholder="Username or email"
              value={newPermission.user_name}
              onChange={(e) => setNewPermission({...newPermission, user_name: e.target.value})}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <select
              value={newPermission.permission}
              onChange={(e) => setNewPermission({...newPermission, permission: e.target.value as any})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="view">View</option>
              <option value="edit">Edit</option>
              <option value="admin">Admin</option>
            </select>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettingsTab = () => (
    <div className="space-y-6">
      {/* Visibility Settings */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Visibility & Sharing</h3>
        
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={template?.is_public}
              onChange={(e) => setEditedTemplate({...editedTemplate, is_public: e.target.checked})}
              className="rounded border-gray-300"
            />
            <div className="ml-3">
              <div className="flex items-center">
                {template?.is_public ? <Unlock className="h-4 w-4 text-green-500 mr-2" /> : <Lock className="h-4 w-4 text-red-500 mr-2" />}
                <span className="font-medium">Public Template</span>
              </div>
              <p className="text-sm text-gray-600">Allow other users to discover and use this template</p>
            </div>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={template?.is_official}
              className="rounded border-gray-300"
              disabled
            />
            <div className="ml-3">
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-blue-500 mr-2" />
                <span className="font-medium text-gray-400">Official Template</span>
              </div>
              <p className="text-sm text-gray-600">Verified by TeamFlow team (admin only)</p>
            </div>
          </label>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="bg-white rounded-lg shadow-sm border border-red-200 p-6">
        <h3 className="text-lg font-medium text-red-900 mb-4 flex items-center">
          <AlertTriangle className="h-5 w-5 mr-2" />
          Danger Zone
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 border border-red-200 rounded-lg">
            <div>
              <h4 className="font-medium text-gray-900">Delete Template</h4>
              <p className="text-sm text-gray-600">Permanently delete this template and all its versions</p>
            </div>
            <button
              onClick={() => setShowDeleteModal(true)}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !template) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Template</h2>
          <p className="text-gray-600 mb-4">{error || 'Template not found'}</p>
          <button
            onClick={() => navigate('/templates')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Templates
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/templates')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600 rounded-md"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{template.title}</h1>
                <p className="text-sm text-gray-600">
                  v{template.version} • {template.usage_count} uses • Updated {formatDate(template.updated_at)}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate(`/templates/details/${template.id}`)}
                className="flex items-center px-3 py-2 border border-gray-300 text-sm rounded-md hover:bg-gray-50"
              >
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </button>
              
              <button
                onClick={() => setShowCloneModal(true)}
                className="flex items-center px-3 py-2 border border-gray-300 text-sm rounded-md hover:bg-gray-50"
              >
                <Copy className="h-4 w-4 mr-2" />
                Clone
              </button>
              
              <button
                onClick={() => window.open(`/templates/share/${template.id}`, '_blank')}
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'edit', name: 'Edit Template', icon: Edit3 },
              { id: 'versions', name: 'Versions', icon: History },
              { id: 'permissions', name: 'Permissions', icon: User },
              { id: 'settings', name: 'Settings', icon: Settings }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'edit' && renderEditTab()}
        {activeTab === 'versions' && renderVersionsTab()}
        {activeTab === 'permissions' && renderPermissionsTab()}
        {activeTab === 'settings' && renderSettingsTab()}
      </div>

      {/* Modals */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center mb-4">
              <AlertTriangle className="h-6 w-6 text-red-500 mr-3" />
              <h3 className="text-lg font-medium text-gray-900">Delete Template</h3>
            </div>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete "{template.title}"? This action cannot be undone and will remove all versions and data associated with this template.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteTemplate}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Delete Template
              </button>
            </div>
          </div>
        </div>
      )}

      {showCloneModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Clone Template</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Template Name</label>
                <input
                  type="text"
                  value={cloneOptions.new_name}
                  onChange={(e) => setCloneOptions({...cloneOptions, new_name: e.target.value})}
                  placeholder={`${template.name}_copy`}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Display Title</label>
                <input
                  type="text"
                  value={cloneOptions.new_title}
                  onChange={(e) => setCloneOptions({...cloneOptions, new_title: e.target.value})}
                  placeholder={`${template.title} (Copy)`}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={cloneOptions.copy_versions}
                    onChange={(e) => setCloneOptions({...cloneOptions, copy_versions: e.target.checked})}
                    className="rounded border-gray-300"
                  />
                  <span className="ml-2 text-sm">Copy version history</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={cloneOptions.make_private}
                    onChange={(e) => setCloneOptions({...cloneOptions, make_private: e.target.checked})}
                    className="rounded border-gray-300"
                  />
                  <span className="ml-2 text-sm">Make cloned template private</span>
                </label>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCloneModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCloneTemplate}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Clone Template
              </button>
            </div>
          </div>
        </div>
      )}

      {showVersionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Version</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Version Description</label>
                <textarea
                  value={versionDescription}
                  onChange={(e) => setVersionDescription(e.target.value)}
                  placeholder="Describe what changed in this version..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="text-sm text-gray-600">
                <p>New version will be: <span className="font-medium">v{incrementVersion(template.version)}</span></p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowVersionModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateVersion}
                disabled={!versionDescription.trim()}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                Create Version
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateManagement;