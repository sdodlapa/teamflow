import React, { useState, useEffect } from 'react';
import {
  Shield, Plus, Edit, Trash2, Users, Key,
  Settings, Search, MoreVertical, Copy,
  CheckCircle, X, Save
} from 'lucide-react';
import './RoleManagement.css';

interface Permission {
  id: string;
  name: string;
  description: string;
  category: 'users' | 'projects' | 'tasks' | 'reports' | 'system';
  isSystem: boolean;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  userCount: number;
  isSystem: boolean;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

interface RoleFormData {
  name: string;
  description: string;
  permissions: string[];
  isActive: boolean;
}

interface RoleManagementProps {
  onClose?: () => void;
}

export const RoleManagement: React.FC<RoleManagementProps> = ({ onClose }) => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [formData, setFormData] = useState<RoleFormData>({
    name: '',
    description: '',
    permissions: [],
    isActive: true
  });
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  // Mock data generation
  const generateMockPermissions = (): Permission[] => {
    return [
      // User Management Permissions
      {
        id: 'users.read',
        name: 'View Users',
        description: 'View user profiles and information',
        category: 'users',
        isSystem: true
      },
      {
        id: 'users.write',
        name: 'Manage Users',
        description: 'Create, edit, and delete user accounts',
        category: 'users',
        isSystem: true
      },
      {
        id: 'users.roles',
        name: 'Assign Roles',
        description: 'Assign and modify user roles',
        category: 'users',
        isSystem: true
      },
      // Project Management Permissions
      {
        id: 'projects.read',
        name: 'View Projects',
        description: 'View project details and information',
        category: 'projects',
        isSystem: true
      },
      {
        id: 'projects.write',
        name: 'Manage Projects',
        description: 'Create, edit, and delete projects',
        category: 'projects',
        isSystem: true
      },
      {
        id: 'projects.admin',
        name: 'Project Admin',
        description: 'Full administrative access to projects',
        category: 'projects',
        isSystem: true
      },
      // Task Management Permissions
      {
        id: 'tasks.read',
        name: 'View Tasks',
        description: 'View task details and assignments',
        category: 'tasks',
        isSystem: true
      },
      {
        id: 'tasks.write',
        name: 'Manage Tasks',
        description: 'Create, edit, and delete tasks',
        category: 'tasks',
        isSystem: true
      },
      {
        id: 'tasks.assign',
        name: 'Assign Tasks',
        description: 'Assign tasks to team members',
        category: 'tasks',
        isSystem: true
      },
      // Reports Permissions
      {
        id: 'reports.read',
        name: 'View Reports',
        description: 'View analytics and reports',
        category: 'reports',
        isSystem: true
      },
      {
        id: 'reports.export',
        name: 'Export Reports',
        description: 'Export data and generate reports',
        category: 'reports',
        isSystem: true
      },
      // System Permissions
      {
        id: 'system.admin',
        name: 'System Admin',
        description: 'Full system administration access',
        category: 'system',
        isSystem: true
      },
      {
        id: 'system.settings',
        name: 'System Settings',
        description: 'Manage system configuration and settings',
        category: 'system',
        isSystem: true
      }
    ];
  };

  const generateMockRoles = (): Role[] => {
    return [
      {
        id: 'role-1',
        name: 'Super Administrator',
        description: 'Complete access to all system functions and data',
        permissions: ['*'], // Wildcard for all permissions
        userCount: 2,
        isSystem: true,
        isActive: true,
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-01-01T00:00:00Z',
        createdBy: 'System'
      },
      {
        id: 'role-2',
        name: 'Administrator',
        description: 'Administrative access with user and project management capabilities',
        permissions: ['users.read', 'users.write', 'users.roles', 'projects.read', 'projects.write', 'projects.admin', 'reports.read', 'reports.export'],
        userCount: 5,
        isSystem: true,
        isActive: true,
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2024-01-15T10:30:00Z',
        createdBy: 'System'
      },
      {
        id: 'role-3',
        name: 'Project Manager',
        description: 'Manage projects and teams with limited administrative access',
        permissions: ['users.read', 'projects.read', 'projects.write', 'tasks.read', 'tasks.write', 'tasks.assign', 'reports.read'],
        userCount: 12,
        isSystem: false,
        isActive: true,
        createdAt: '2023-06-15T09:00:00Z',
        updatedAt: '2023-08-20T14:45:00Z',
        createdBy: 'admin@company.com'
      },
      {
        id: 'role-4',
        name: 'Team Lead',
        description: 'Lead team members and manage task assignments',
        permissions: ['users.read', 'projects.read', 'tasks.read', 'tasks.write', 'tasks.assign'],
        userCount: 8,
        isSystem: false,
        isActive: true,
        createdAt: '2023-08-01T11:20:00Z',
        updatedAt: '2023-12-10T16:15:00Z',
        createdBy: 'manager@company.com'
      },
      {
        id: 'role-5',
        name: 'Team Member',
        description: 'Basic access for task management and project viewing',
        permissions: ['projects.read', 'tasks.read', 'tasks.write'],
        userCount: 45,
        isSystem: true,
        isActive: true,
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-01-01T00:00:00Z',
        createdBy: 'System'
      },
      {
        id: 'role-6',
        name: 'Viewer',
        description: 'Read-only access to projects and tasks',
        permissions: ['projects.read', 'tasks.read'],
        userCount: 23,
        isSystem: false,
        isActive: true,
        createdAt: '2023-09-10T13:30:00Z',
        updatedAt: '2023-11-05T09:25:00Z',
        createdBy: 'admin@company.com'
      },
      {
        id: 'role-7',
        name: 'Analyst',
        description: 'Access to reports and analytics with limited project visibility',
        permissions: ['projects.read', 'tasks.read', 'reports.read', 'reports.export'],
        userCount: 6,
        isSystem: false,
        isActive: false,
        createdAt: '2023-10-20T15:45:00Z',
        updatedAt: '2024-01-08T11:10:00Z',
        createdBy: 'manager@company.com'
      }
    ];
  };

  useEffect(() => {
    setIsLoading(true);
    setTimeout(() => {
      setPermissions(generateMockPermissions());
      setRoles(generateMockRoles());
      setIsLoading(false);
    }, 800);
  }, []);

  const filteredRoles = roles.filter(role =>
    role.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    role.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateRole = () => {
    setEditingRole(null);
    setFormData({
      name: '',
      description: '',
      permissions: [],
      isActive: true
    });
    setSelectedPermissions([]);
    setShowRoleModal(true);
  };

  const handleEditRole = (role: Role) => {
    setEditingRole(role);
    setFormData({
      name: role.name,
      description: role.description,
      permissions: role.permissions,
      isActive: role.isActive
    });
    setSelectedPermissions(role.permissions);
    setShowRoleModal(true);
  };

  const handleDeleteRole = (roleId: string) => {
    const role = roles.find(r => r.id === roleId);
    if (role && role.isSystem) {
      alert('System roles cannot be deleted');
      return;
    }
    if (window.confirm('Are you sure you want to delete this role?')) {
      setRoles(roles.filter(r => r.id !== roleId));
    }
  };

  const handleDuplicateRole = (role: Role) => {
    const newRole: Role = {
      ...role,
      id: `role-${Date.now()}`,
      name: `${role.name} (Copy)`,
      isSystem: false,
      userCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      createdBy: 'current-user@company.com'
    };
    setRoles([...roles, newRole]);
  };

  const handleSaveRole = () => {
    if (!formData.name.trim()) {
      alert('Role name is required');
      return;
    }

    if (editingRole) {
      // Update existing role
      setRoles(roles.map(role =>
        role.id === editingRole.id
          ? {
              ...role,
              name: formData.name,
              description: formData.description,
              permissions: selectedPermissions,
              isActive: formData.isActive,
              updatedAt: new Date().toISOString()
            }
          : role
      ));
    } else {
      // Create new role
      const newRole: Role = {
        id: `role-${Date.now()}`,
        name: formData.name,
        description: formData.description,
        permissions: selectedPermissions,
        userCount: 0,
        isSystem: false,
        isActive: formData.isActive,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: 'current-user@company.com'
      };
      setRoles([...roles, newRole]);
    }

    setShowRoleModal(false);
    setEditingRole(null);
  };

  const handlePermissionToggle = (permissionId: string) => {
    setSelectedPermissions(prev =>
      prev.includes(permissionId)
        ? prev.filter(id => id !== permissionId)
        : [...prev, permissionId]
    );
  };

  const handleSelectAllPermissions = (category: string) => {
    const categoryPermissions = permissions
      .filter(p => p.category === category)
      .map(p => p.id);
    
    const allSelected = categoryPermissions.every(id => selectedPermissions.includes(id));
    
    if (allSelected) {
      setSelectedPermissions(prev => prev.filter(id => !categoryPermissions.includes(id)));
    } else {
      setSelectedPermissions(prev => [...new Set([...prev, ...categoryPermissions])]);
    }
  };

  const getPermissionsByCategory = (category: string) => {
    return permissions.filter(p => p.category === category);
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'users':
        return <Users size={16} />;
      case 'projects':
        return <Settings size={16} />;
      case 'tasks':
        return <CheckCircle size={16} />;
      case 'reports':
        return <Settings size={16} />;
      case 'system':
        return <Shield size={16} />;
      default:
        return <Key size={16} />;
    }
  };

  const renderRoleCard = (role: Role) => (
    <div key={role.id} className={`role-card ${!role.isActive ? 'inactive' : ''}`}>
      <div className="role-header">
        <div className="role-title">
          <div className="role-name">
            {role.name}
            {role.isSystem && <span className="system-badge">System</span>}
            {!role.isActive && <span className="inactive-badge">Inactive</span>}
          </div>
          <div className="role-description">{role.description}</div>
        </div>
        
        <div className="role-actions">
          <button
            className="action-icon-btn"
            onClick={() => handleEditRole(role)}
            title="Edit Role"
          >
            <Edit size={16} />
          </button>
          <button
            className="action-icon-btn"
            onClick={() => handleDuplicateRole(role)}
            title="Duplicate Role"
          >
            <Copy size={16} />
          </button>
          {!role.isSystem && (
            <button
              className="action-icon-btn danger"
              onClick={() => handleDeleteRole(role.id)}
              title="Delete Role"
            >
              <Trash2 size={16} />
            </button>
          )}
          <button className="action-icon-btn">
            <MoreVertical size={16} />
          </button>
        </div>
      </div>

      <div className="role-stats">
        <div className="stat-item">
          <Users size={14} />
          <span>{role.userCount} users</span>
        </div>
        <div className="stat-item">
          <Key size={14} />
          <span>{role.permissions.includes('*') ? 'All' : role.permissions.length} permissions</span>
        </div>
      </div>

      <div className="role-permissions">
        <div className="permissions-preview">
          {role.permissions.includes('*') ? (
            <span className="permission-badge all-permissions">All Permissions</span>
          ) : (
            role.permissions.slice(0, 3).map(permId => {
              const perm = permissions.find(p => p.id === permId);
              return perm ? (
                <span key={perm.id} className="permission-badge">
                  {perm.name}
                </span>
              ) : null;
            })
          )}
          {role.permissions.length > 3 && !role.permissions.includes('*') && (
            <span className="more-permissions">+{role.permissions.length - 3} more</span>
          )}
        </div>
      </div>

      <div className="role-meta">
        <span>Updated: {new Date(role.updatedAt).toLocaleDateString()}</span>
        <span>By: {role.createdBy}</span>
      </div>
    </div>
  );

  const renderPermissionModal = () => {
    const categories = ['users', 'projects', 'tasks', 'reports', 'system'];
    
    return (
      <div className="modal-overlay">
        <div className="modal-content large">
          <div className="modal-header">
            <h3>{editingRole ? 'Edit Role' : 'Create New Role'}</h3>
            <button className="close-btn" onClick={() => setShowRoleModal(false)}>
              <X size={16} />
            </button>
          </div>

          <div className="modal-body">
            <div className="role-form">
              <div className="form-section">
                <h4>Role Information</h4>
                <div className="form-group">
                  <label>Role Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Enter role name"
                  />
                </div>
                
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe this role's purpose and responsibilities"
                    rows={3}
                  />
                </div>

                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={formData.isActive}
                      onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                    />
                    Active Role
                  </label>
                </div>
              </div>

              <div className="form-section">
                <h4>Permissions</h4>
                <div className="permissions-grid">
                  {categories.map(category => {
                    const categoryPerms = getPermissionsByCategory(category);
                    const selectedCount = categoryPerms.filter(p => selectedPermissions.includes(p.id)).length;
                    
                    return (
                      <div key={category} className="permission-category">
                        <div className="category-header">
                          <div className="category-title">
                            {getCategoryIcon(category)}
                            <span>{category.charAt(0).toUpperCase() + category.slice(1)}</span>
                            <span className="selected-count">({selectedCount}/{categoryPerms.length})</span>
                          </div>
                          <button
                            type="button"
                            className="select-all-btn"
                            onClick={() => handleSelectAllPermissions(category)}
                          >
                            {selectedCount === categoryPerms.length ? 'Deselect All' : 'Select All'}
                          </button>
                        </div>
                        
                        <div className="permissions-list">
                          {categoryPerms.map(permission => (
                            <label key={permission.id} className="permission-item">
                              <input
                                type="checkbox"
                                checked={selectedPermissions.includes(permission.id)}
                                onChange={() => handlePermissionToggle(permission.id)}
                              />
                              <div className="permission-info">
                                <div className="permission-name">{permission.name}</div>
                                <div className="permission-description">{permission.description}</div>
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <div className="selected-summary">
              {selectedPermissions.length} permissions selected
            </div>
            <div className="footer-actions">
              <button
                className="action-btn secondary"
                onClick={() => setShowRoleModal(false)}
              >
                Cancel
              </button>
              <button
                className="action-btn primary"
                onClick={handleSaveRole}
              >
                <Save size={16} />
                {editingRole ? 'Update Role' : 'Create Role'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="role-management">
      <div className="management-header">
        <div className="header-content">
          <h1>Role Management</h1>
          <p>Create and manage user roles with granular permissions</p>
        </div>
        
        <div className="header-actions">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search roles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <button
            className="action-btn primary"
            onClick={handleCreateRole}
          >
            <Plus size={16} />
            Create Role
          </button>
          
          {onClose && (
            <button className="action-btn secondary" onClick={onClose}>
              <X size={16} />
              Close
            </button>
          )}
        </div>
      </div>

      <div className="roles-stats">
        <div className="stat-card">
          <Shield size={24} />
          <div className="stat-content">
            <div className="stat-value">{roles.length}</div>
            <div className="stat-label">Total Roles</div>
          </div>
        </div>
        <div className="stat-card">
          <Users size={24} />
          <div className="stat-content">
            <div className="stat-value">{roles.reduce((sum, role) => sum + role.userCount, 0)}</div>
            <div className="stat-label">Users Assigned</div>
          </div>
        </div>
        <div className="stat-card">
          <Key size={24} />
          <div className="stat-content">
            <div className="stat-value">{permissions.length}</div>
            <div className="stat-label">Available Permissions</div>
          </div>
        </div>
        <div className="stat-card">
          <CheckCircle size={24} />
          <div className="stat-content">
            <div className="stat-value">{roles.filter(r => r.isActive).length}</div>
            <div className="stat-label">Active Roles</div>
          </div>
        </div>
      </div>

      <div className="roles-grid">
        {isLoading ? (
          <div className="loading-state">
            <div className="loading-spinner" />
            <p>Loading roles...</p>
          </div>
        ) : filteredRoles.length === 0 ? (
          <div className="empty-state">
            <Shield size={48} />
            <h3>No roles found</h3>
            <p>Try adjusting your search criteria or create a new role</p>
            <button className="action-btn primary" onClick={handleCreateRole}>
              <Plus size={16} />
              Create First Role
            </button>
          </div>
        ) : (
          filteredRoles.map(renderRoleCard)
        )}
      </div>

      {showRoleModal && renderPermissionModal()}
    </div>
  );
};