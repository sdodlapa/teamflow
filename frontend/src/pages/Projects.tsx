/**
 * Projects Page Component
 * Comprehensive project management with CRUD operations, team management, and filtering
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Filter, Search, ChevronDown, RefreshCw, Trash2, Edit, Users, Calendar, BarChart3 } from 'lucide-react';
import Layout from '../components/Layout';
import { 
  projectApi, 
  Project, 
  ProjectFilters, 
  PROJECT_STATUSES, 
  PROJECT_PRIORITIES,
  PROJECT_MEMBER_ROLES,
  ProjectCreate,
  ProjectUpdate,
  ProjectMember
} from '../services/projectApi';

// Project Card Component
const ProjectCard: React.FC<{
  project: Project;
  onEdit: (project: Project) => void;
  onDelete: (projectId: number) => void;
  onManageMembers: (project: Project) => void;
}> = ({ project, onEdit, onDelete, onManageMembers }) => {
  const statusConfig = PROJECT_STATUSES.find(s => s.value === project.status);
  const priorityConfig = PROJECT_PRIORITIES.find(p => p.value === project.priority);
  
  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getDaysRemaining = () => {
    if (!project.end_date) return null;
    const endDate = new Date(project.end_date);
    const today = new Date();
    const diffTime = endDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysRemaining = getDaysRemaining();

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-xl font-semibold text-gray-900 truncate">
              {statusConfig?.icon} {project.name}
            </h3>
            <div className="flex gap-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusConfig?.color}`}>
                {statusConfig?.label}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityConfig?.color}`}>
                {priorityConfig?.icon} {priorityConfig?.label}
              </span>
            </div>
          </div>
          
          {project.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {project.description}
            </p>
          )}
          
          {/* Project Stats */}
          <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-3">
            <div className="flex items-center gap-1">
              <Users size={14} />
              <span>{project.members?.length || 0} members</span>
            </div>
            {project.task_count !== undefined && (
              <div className="flex items-center gap-1">
                <BarChart3 size={14} />
                <span>{project.task_count} tasks</span>
              </div>
            )}
            <span>Created: {formatDate(project.created_at)}</span>
          </div>
          
          {/* Date Information */}
          <div className="flex flex-wrap gap-4 text-sm text-gray-500">
            {project.start_date && (
              <div className="flex items-center gap-1">
                <Calendar size={14} />
                <span>Started: {formatDate(project.start_date)}</span>
              </div>
            )}
            {project.end_date && (
              <div className="flex items-center gap-1">
                <Calendar size={14} />
                <span>Due: {formatDate(project.end_date)}</span>
                {daysRemaining !== null && (
                  <span className={`ml-1 px-2 py-0.5 text-xs rounded ${
                    daysRemaining < 0 
                      ? 'bg-red-100 text-red-700' 
                      : daysRemaining <= 7 
                        ? 'bg-yellow-100 text-yellow-700' 
                        : 'bg-green-100 text-green-700'
                  }`}>
                    {daysRemaining < 0 ? `${Math.abs(daysRemaining)} days overdue` : `${daysRemaining} days left`}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-2 ml-4">
          <button
            onClick={() => onManageMembers(project)}
            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
            title="Manage Members"
          >
            <Users size={16} />
          </button>
          
          <button
            onClick={() => onEdit(project)}
            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
            title="Edit Project"
          >
            <Edit size={16} />
          </button>
          
          <button
            onClick={() => onDelete(project.id)}
            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
            title="Delete Project"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

// Project Form Modal Component
const ProjectFormModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ProjectCreate | ProjectUpdate) => Promise<void>;
  project?: Project;
  isLoading?: boolean;
}> = ({ isOpen, onClose, onSubmit, project, isLoading = false }) => {
  const [formData, setFormData] = useState<ProjectCreate>({
    name: '',
    description: '',
    organization_id: 1, // Default org - would come from context in production
    status: 'planning',
    priority: 'medium',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name,
        description: project.description || '',
        organization_id: project.organization_id,
        status: project.status,
        priority: project.priority,
        start_date: project.start_date || '',
        end_date: project.end_date || ''
      });
    } else {
      setFormData({
        name: '',
        description: '',
        organization_id: 1,
        status: 'planning',
        priority: 'medium',
        start_date: '',
        end_date: ''
      });
    }
  }, [project, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      start_date: formData.start_date || undefined,
      end_date: formData.end_date || undefined
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-semibold mb-6">
          {project ? 'Edit Project' : 'Create New Project'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Project Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter project name"
              maxLength={100}
            />
          </div>
          
          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
              maxLength={2000}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter project description"
            />
          </div>
          
          {/* Status and Priority */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Project['status'] }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {PROJECT_STATUSES.map(status => (
                  <option key={status.value} value={status.value}>
                    {status.icon} {status.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as Project['priority'] }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {PROJECT_PRIORITIES.map(priority => (
                  <option key={priority.value} value={priority.value}>
                    {priority.icon} {priority.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Start and End Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Form Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Saving...' : project ? 'Update Project' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Member Management Modal Component
const MemberManagementModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  project?: Project;
}> = ({ isOpen, onClose, project }) => {
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState<ProjectMember['role']>('developer');
  const [addingMember, setAddingMember] = useState(false);

  useEffect(() => {
    if (isOpen && project) {
      loadMembers();
    }
  }, [isOpen, project]);

  const loadMembers = async () => {
    if (!project) return;
    
    try {
      setLoading(true);
      setError(null);
      const fetchedMembers = await projectApi.getProjectMembers(project.id);
      setMembers(fetchedMembers);
    } catch (err: any) {
      setError(err.message || 'Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  const handleAddMember = async () => {
    if (!project || !newMemberEmail.trim()) return;
    
    try {
      setAddingMember(true);
      setError(null);
      const newMember = await projectApi.addProjectMember(project.id, {
        user_email: newMemberEmail,
        role: newMemberRole
      });
      setMembers(prev => [...prev, newMember]);
      setNewMemberEmail('');
      setNewMemberRole('developer');
    } catch (err: any) {
      setError(err.message || 'Failed to add member');
    } finally {
      setAddingMember(false);
    }
  };

  const handleUpdateMemberRole = async (memberId: number, role: ProjectMember['role']) => {
    if (!project) return;
    
    try {
      setError(null);
      const updatedMember = await projectApi.updateProjectMember(project.id, memberId, { role });
      setMembers(prev => prev.map(member => 
        member.id === memberId ? updatedMember : member
      ));
    } catch (err: any) {
      setError(err.message || 'Failed to update member role');
    }
  };

  const handleRemoveMember = async (memberId: number) => {
    if (!project || !confirm('Are you sure you want to remove this member?')) return;
    
    try {
      setError(null);
      await projectApi.removeProjectMember(project.id, memberId);
      setMembers(prev => prev.filter(member => member.id !== memberId));
    } catch (err: any) {
      setError(err.message || 'Failed to remove member');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">
            Manage Members - {project?.name}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          >
            ×
          </button>
        </div>
        
        {/* Add Member Section */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="font-medium mb-3">Add New Member</h3>
          <div className="flex gap-3">
            <input
              type="email"
              placeholder="Enter email address"
              value={newMemberEmail}
              onChange={(e) => setNewMemberEmail(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <select
              value={newMemberRole}
              onChange={(e) => setNewMemberRole(e.target.value as ProjectMember['role'])}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {PROJECT_MEMBER_ROLES.map(role => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>
            <button
              onClick={handleAddMember}
              disabled={addingMember || !newMemberEmail.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {addingMember ? 'Adding...' : 'Add'}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-4">
            {error}
          </div>
        )}

        {/* Members List */}
        {loading ? (
          <div className="flex justify-center items-center py-8">
            <RefreshCw className="animate-spin text-blue-600" size={24} />
          </div>
        ) : members.length === 0 ? (
          <div className="text-center py-8">
            <Users className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No members yet</h3>
            <p className="text-gray-600">Add team members to start collaborating</p>
          </div>
        ) : (
          <div className="space-y-3">
            <h3 className="font-medium">Team Members ({members.length})</h3>
            {members.map(member => {
              return (
                <div key={member.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        {member.user_name?.charAt(0) || member.user_email.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {member.user_name || member.user_email}
                        </p>
                        <p className="text-sm text-gray-600">{member.user_email}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <select
                      value={member.role}
                      onChange={(e) => handleUpdateMemberRole(member.id, e.target.value as ProjectMember['role'])}
                      className="px-3 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {PROJECT_MEMBER_ROLES.map(role => (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      ))}
                    </select>
                    
                    {member.role !== 'owner' && (
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Remove member"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

// Main Projects Page Component
const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // Modal states
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [showMemberManagement, setShowMemberManagement] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  
  // Filter state
  const [filters, setFilters] = useState<ProjectFilters>({
    status: [],
    priority: []
  });
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Load projects
  const loadProjects = useCallback(async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      setError(null);
      
      const projectList = await projectApi.getProjects(filters);
      
      // Apply client-side search filter if needed
      let filteredProjects = projectList.projects;
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        filteredProjects = projectList.projects.filter(project =>
          project.name.toLowerCase().includes(query) ||
          project.description?.toLowerCase().includes(query)
        );
      }
      
      setProjects(filteredProjects);
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, searchQuery]);

  // Initial load
  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  // Refresh projects
  const handleRefresh = async () => {
    setRefreshing(true);
    await loadProjects(false);
    setRefreshing(false);
  };

  // Create project
  const handleCreateProject = async (projectData: ProjectCreate) => {
    try {
      setFormLoading(true);
      const newProject = await projectApi.createProject(projectData);
      setProjects(prev => [newProject, ...prev]);
      setShowProjectForm(false);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to create project');
    } finally {
      setFormLoading(false);
    }
  };

  // Update project
  const handleUpdateProject = async (projectData: ProjectUpdate) => {
    if (!editingProject) return;
    
    try {
      setFormLoading(true);
      const updatedProject = await projectApi.updateProject(editingProject.id, projectData);
      setProjects(prev => prev.map(project => 
        project.id === editingProject.id ? updatedProject : project
      ));
      setShowProjectForm(false);
      setEditingProject(null);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to update project');
    } finally {
      setFormLoading(false);
    }
  };

  // Delete project
  const handleDeleteProject = async (projectId: number) => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) return;
    
    try {
      await projectApi.deleteProject(projectId);
      setProjects(prev => prev.filter(project => project.id !== projectId));
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete project');
    }
  };

  // Edit project
  const handleEditProject = (project: Project) => {
    setEditingProject(project);
    setShowProjectForm(true);
  };

  // Manage members
  const handleManageMembers = (project: Project) => {
    setSelectedProject(project);
    setShowMemberManagement(true);
  };

  // Handle form submit
  const handleFormSubmit = async (projectData: ProjectCreate | ProjectUpdate) => {
    if (editingProject) {
      await handleUpdateProject(projectData as ProjectUpdate);
    } else {
      await handleCreateProject(projectData as ProjectCreate);
    }
  };

  // Close modals
  const handleCloseProjectForm = () => {
    setShowProjectForm(false);
    setEditingProject(null);
  };

  const handleCloseMemberManagement = () => {
    setShowMemberManagement(false);
    setSelectedProject(null);
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
            <p className="text-gray-600 mt-1">
              Manage your team's projects and collaborations
            </p>
          </div>
          
          <button
            onClick={() => setShowProjectForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus size={20} />
            New Project
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              <Filter size={16} />
              Filters
              <ChevronDown size={16} className={`transform transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
          
          {/* Expandable Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <div className="space-y-2">
                  {PROJECT_STATUSES.map(status => (
                    <label key={status.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={filters.status?.includes(status.value) || false}
                        onChange={(e) => {
                          const statusList = filters.status || [];
                          if (e.target.checked) {
                            setFilters(prev => ({
                              ...prev,
                              status: [...statusList, status.value]
                            }));
                          } else {
                            setFilters(prev => ({
                              ...prev,
                              status: statusList.filter(s => s !== status.value)
                            }));
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {status.icon} {status.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Priority Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                <div className="space-y-2">
                  {PROJECT_PRIORITIES.map(priority => (
                    <label key={priority.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={filters.priority?.includes(priority.value) || false}
                        onChange={(e) => {
                          const priorityList = filters.priority || [];
                          if (e.target.checked) {
                            setFilters(prev => ({
                              ...prev,
                              priority: [...priorityList, priority.value]
                            }));
                          } else {
                            setFilters(prev => ({
                              ...prev,
                              priority: priorityList.filter(p => p !== priority.value)
                            }));
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {priority.icon} {priority.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Project Grid */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <RefreshCw className="animate-spin text-blue-600" size={32} />
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Plus size={48} className="mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || filters.status?.length || filters.priority?.length
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first project'
              }
            </p>
            {!searchQuery && !filters.status?.length && !filters.priority?.length && (
              <button
                onClick={() => setShowProjectForm(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Your First Project
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Project Count */}
            <div className="text-sm text-gray-600 mb-4">
              Showing {projects.length} project{projects.length !== 1 ? 's' : ''}
            </div>
            
            {/* Project Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {projects.map(project => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onEdit={handleEditProject}
                  onDelete={handleDeleteProject}
                  onManageMembers={handleManageMembers}
                />
              ))}
            </div>
          </div>
        )}

        {/* Project Form Modal */}
        <ProjectFormModal
          isOpen={showProjectForm}
          onClose={handleCloseProjectForm}
          onSubmit={handleFormSubmit}
          project={editingProject || undefined}
          isLoading={formLoading}
        />

        {/* Member Management Modal */}
        <MemberManagementModal
          isOpen={showMemberManagement}
          onClose={handleCloseMemberManagement}
          project={selectedProject || undefined}
        />
      </div>
    </Layout>
  );
};

export default Projects;