import React, { useState, useEffect } from 'react';
import {
  Users, UserPlus, Shield, Settings, Search,
  MoreVertical, Edit, Trash2, Lock, Unlock,
  Clock, UserCheck, UserX, Download,
  Upload, RefreshCw, Eye, Key
} from 'lucide-react';
import './UserManagementDashboard.css';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatar?: string;
  role: 'super_admin' | 'admin' | 'manager' | 'user';
  status: 'active' | 'inactive' | 'suspended' | 'pending';
  department?: string;
  position?: string;
  phone?: string;
  location?: string;
  lastActive: string;
  joinedAt: string;
  permissions: string[];
  organizationId: string;
  projects: string[];
  tasksAssigned: number;
  tasksCompleted: number;
  loginCount: number;
  ipAddress?: string;
  deviceInfo?: string;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  userCount: number;
  isSystem: boolean;
  createdAt: string;
}

interface Permission {
  id: string;
  name: string;
  description: string;
  category: 'users' | 'projects' | 'tasks' | 'reports' | 'system';
  isSystem: boolean;
}

interface UserStats {
  totalUsers: number;
  activeUsers: number;
  pendingUsers: number;
  suspendedUsers: number;
  newUsersThisMonth: number;
  averageSessionTime: number;
}

interface UserManagementDashboardProps {
  organizationId?: string;
}

export const UserManagementDashboard: React.FC<UserManagementDashboardProps> = ({
  organizationId
}) => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [activeTab, setActiveTab] = useState<'users' | 'roles' | 'permissions'>('users');
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [sortBy, setSortBy] = useState<'name' | 'role' | 'status' | 'lastActive'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [isLoading, setIsLoading] = useState(true);

  // Mock data generation
  const generateMockUsers = (): User[] => {
    const mockUsers: User[] = [
      {
        id: 'user-1',
        email: 'john.doe@company.com',
        firstName: 'John',
        lastName: 'Doe',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
        role: 'admin',
        status: 'active',
        department: 'Engineering',
        position: 'Senior Developer',
        phone: '+1 (555) 123-4567',
        location: 'San Francisco, CA',
        lastActive: '2024-01-25T14:30:00Z',
        joinedAt: '2023-06-15T09:00:00Z',
        permissions: ['users.read', 'users.write', 'projects.read', 'projects.write'],
        organizationId: 'org-1',
        projects: ['project-1', 'project-2'],
        tasksAssigned: 24,
        tasksCompleted: 18,
        loginCount: 156,
        ipAddress: '192.168.1.100',
        deviceInfo: 'Chrome on macOS'
      },
      {
        id: 'user-2',
        email: 'jane.smith@company.com',
        firstName: 'Jane',
        lastName: 'Smith',
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b6fd?w=100&h=100&fit=crop&crop=face',
        role: 'manager',
        status: 'active',
        department: 'Marketing',
        position: 'Marketing Manager',
        phone: '+1 (555) 234-5678',
        location: 'New York, NY',
        lastActive: '2024-01-25T16:45:00Z',
        joinedAt: '2023-08-20T10:30:00Z',
        permissions: ['users.read', 'projects.read', 'projects.write', 'reports.read'],
        organizationId: 'org-1',
        projects: ['project-3', 'project-4'],
        tasksAssigned: 16,
        tasksCompleted: 14,
        loginCount: 89,
        ipAddress: '192.168.1.101',
        deviceInfo: 'Safari on iPhone'
      },
      {
        id: 'user-3',
        email: 'bob.wilson@company.com',
        firstName: 'Bob',
        lastName: 'Wilson',
        role: 'user',
        status: 'pending',
        department: 'Sales',
        position: 'Sales Representative',
        phone: '+1 (555) 345-6789',
        location: 'Austin, TX',
        lastActive: '2024-01-20T11:20:00Z',
        joinedAt: '2024-01-15T14:00:00Z',
        permissions: ['tasks.read', 'tasks.write'],
        organizationId: 'org-1',
        projects: ['project-5'],
        tasksAssigned: 8,
        tasksCompleted: 3,
        loginCount: 12,
        ipAddress: '192.168.1.102',
        deviceInfo: 'Chrome on Windows'
      },
      {
        id: 'user-4',
        email: 'alice.brown@company.com',
        firstName: 'Alice',
        lastName: 'Brown',
        avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
        role: 'super_admin',
        status: 'active',
        department: 'IT',
        position: 'System Administrator',
        phone: '+1 (555) 456-7890',
        location: 'Seattle, WA',
        lastActive: '2024-01-25T17:00:00Z',
        joinedAt: '2023-01-10T08:00:00Z',
        permissions: ['*'],
        organizationId: 'org-1',
        projects: ['project-1', 'project-2', 'project-3'],
        tasksAssigned: 12,
        tasksCompleted: 12,
        loginCount: 445,
        ipAddress: '192.168.1.103',
        deviceInfo: 'Firefox on Linux'
      },
      {
        id: 'user-5',
        email: 'charlie.davis@company.com',
        firstName: 'Charlie',
        lastName: 'Davis',
        role: 'user',
        status: 'suspended',
        department: 'HR',
        position: 'HR Specialist',
        phone: '+1 (555) 567-8901',
        location: 'Chicago, IL',
        lastActive: '2024-01-18T09:15:00Z',
        joinedAt: '2023-11-05T13:30:00Z',
        permissions: ['users.read', 'reports.read'],
        organizationId: 'org-1',
        projects: [],
        tasksAssigned: 5,
        tasksCompleted: 2,
        loginCount: 34,
        ipAddress: '192.168.1.104',
        deviceInfo: 'Edge on Windows'
      }
    ];
    return mockUsers;
  };

  const generateMockRoles = (): Role[] => {
    return [
      {
        id: 'role-1',
        name: 'Super Admin',
        description: 'Full system access with all permissions',
        permissions: ['*'],
        userCount: 1,
        isSystem: true,
        createdAt: '2023-01-01T00:00:00Z'
      },
      {
        id: 'role-2',
        name: 'Admin',
        description: 'Administrative access with user and project management',
        permissions: ['users.read', 'users.write', 'projects.read', 'projects.write', 'reports.read'],
        userCount: 2,
        isSystem: true,
        createdAt: '2023-01-01T00:00:00Z'
      },
      {
        id: 'role-3',
        name: 'Manager',
        description: 'Team management with limited administrative access',
        permissions: ['users.read', 'projects.read', 'projects.write', 'reports.read', 'tasks.read', 'tasks.write'],
        userCount: 1,
        isSystem: false,
        createdAt: '2023-06-01T00:00:00Z'
      },
      {
        id: 'role-4',
        name: 'User',
        description: 'Basic user access for task management',
        permissions: ['tasks.read', 'tasks.write', 'projects.read'],
        userCount: 2,
        isSystem: true,
        createdAt: '2023-01-01T00:00:00Z'
      }
    ];
  };

  const generateMockPermissions = (): Permission[] => {
    return [
      {
        id: 'perm-1',
        name: 'users.read',
        description: 'View user information and profiles',
        category: 'users',
        isSystem: true
      },
      {
        id: 'perm-2',
        name: 'users.write',
        description: 'Create, edit, and manage user accounts',
        category: 'users',
        isSystem: true
      },
      {
        id: 'perm-3',
        name: 'projects.read',
        description: 'View project information and details',
        category: 'projects',
        isSystem: true
      },
      {
        id: 'perm-4',
        name: 'projects.write',
        description: 'Create, edit, and manage projects',
        category: 'projects',
        isSystem: true
      },
      {
        id: 'perm-5',
        name: 'tasks.read',
        description: 'View task information and assignments',
        category: 'tasks',
        isSystem: true
      },
      {
        id: 'perm-6',
        name: 'tasks.write',
        description: 'Create, edit, and manage tasks',
        category: 'tasks',
        isSystem: true
      },
      {
        id: 'perm-7',
        name: 'reports.read',
        description: 'View reports and analytics',
        category: 'reports',
        isSystem: true
      },
      {
        id: 'perm-8',
        name: 'system.admin',
        description: 'Full system administration access',
        category: 'system',
        isSystem: true
      }
    ];
  };

  const generateMockStats = (): UserStats => {
    return {
      totalUsers: 156,
      activeUsers: 142,
      pendingUsers: 8,
      suspendedUsers: 6,
      newUsersThisMonth: 23,
      averageSessionTime: 4.2
    };
  };

  useEffect(() => {
    // Simulate API loading
    setIsLoading(true);
    setTimeout(() => {
      setUsers(generateMockUsers());
      setRoles(generateMockRoles());
      setPermissions(generateMockPermissions());
      setStats(generateMockStats());
      setIsLoading(false);
    }, 1000);
  }, [organizationId]);

  const filteredUsers = users.filter(user => {
    const matchesSearch = searchQuery === '' || 
      `${user.firstName} ${user.lastName}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (user.department && user.department.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesRole = filterRole === '' || user.role === filterRole;
    const matchesStatus = filterStatus === '' || user.status === filterStatus;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const sortedUsers = [...filteredUsers].sort((a, b) => {
    let aValue: string | number;
    let bValue: string | number;
    
    switch (sortBy) {
      case 'name':
        aValue = `${a.firstName} ${a.lastName}`.toLowerCase();
        bValue = `${b.firstName} ${b.lastName}`.toLowerCase();
        break;
      case 'role':
        aValue = a.role;
        bValue = b.role;
        break;
      case 'status':
        aValue = a.status;
        bValue = b.status;
        break;
      case 'lastActive':
        aValue = new Date(a.lastActive).getTime();
        bValue = new Date(b.lastActive).getTime();
        break;
      default:
        aValue = a.id;
        bValue = b.id;
    }
    
    if (sortOrder === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  const handleUserSelect = (userId: string) => {
    setSelectedUsers(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSelectAll = () => {
    if (selectedUsers.length === sortedUsers.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(sortedUsers.map(user => user.id));
    }
  };

  const handleBulkAction = (action: 'activate' | 'suspend' | 'delete') => {
    if (selectedUsers.length === 0) return;
    
    console.log(`Performing ${action} on users:`, selectedUsers);
    // Simulate API call
    setSelectedUsers([]);
  };

  const getStatusColor = (status: User['status']) => {
    switch (status) {
      case 'active':
        return '#10b981';
      case 'pending':
        return '#f59e0b';
      case 'suspended':
        return '#ef4444';
      case 'inactive':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const getRoleColor = (role: User['role']) => {
    switch (role) {
      case 'super_admin':
        return '#ef4444';
      case 'admin':
        return '#f59e0b';
      case 'manager':
        return '#3b82f6';
      case 'user':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const formatLastActive = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffHours < 168) return `${Math.floor(diffHours / 24)}d ago`;
    return date.toLocaleDateString();
  };

  const renderStatsCards = () => {
    if (!stats) return null;

    const statCards = [
      {
        title: 'Total Users',
        value: stats.totalUsers,
        icon: <Users size={24} />,
        color: '#3b82f6',
        change: '+12%'
      },
      {
        title: 'Active Users',
        value: stats.activeUsers,
        icon: <UserCheck size={24} />,
        color: '#10b981',
        change: '+5%'
      },
      {
        title: 'Pending Approval',
        value: stats.pendingUsers,
        icon: <Clock size={24} />,
        color: '#f59e0b',
        change: '+3'
      },
      {
        title: 'Suspended',
        value: stats.suspendedUsers,
        icon: <UserX size={24} />,
        color: '#ef4444',
        change: '-2'
      }
    ];

    return (
      <div className="stats-grid">
        {statCards.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon" style={{ color: stat.color }}>
              {stat.icon}
            </div>
            <div className="stat-content">
              <div className="stat-value">{stat.value.toLocaleString()}</div>
              <div className="stat-title">{stat.title}</div>
              <div className="stat-change" style={{ color: stat.change.startsWith('+') ? '#10b981' : '#ef4444' }}>
                {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderUserTable = () => {
    return (
      <div className="user-table-container">
        <div className="table-header">
          <div className="table-controls">
            <div className="search-box">
              <Search size={16} />
              <input
                type="text"
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <div className="filter-controls">
              <select
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
              >
                <option value="">All Roles</option>
                <option value="super_admin">Super Admin</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="user">User</option>
              </select>
              
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="pending">Pending</option>
                <option value="suspended">Suspended</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
          
          <div className="table-actions">
            {selectedUsers.length > 0 && (
              <div className="bulk-actions">
                <span className="selected-count">{selectedUsers.length} selected</span>
                <button
                  className="action-btn secondary"
                  onClick={() => handleBulkAction('activate')}
                >
                  <UserCheck size={14} />
                  Activate
                </button>
                <button
                  className="action-btn secondary"
                  onClick={() => handleBulkAction('suspend')}
                >
                  <UserX size={14} />
                  Suspend
                </button>
                <button
                  className="action-btn danger"
                  onClick={() => handleBulkAction('delete')}
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            )}
            
            <button className="action-btn secondary">
              <Download size={16} />
              Export
            </button>
            <button className="action-btn secondary">
              <Upload size={16} />
              Import
            </button>
            <button
              className="action-btn primary"
              onClick={() => console.log('Add user modal')}
            >
              <UserPlus size={16} />
              Add User
            </button>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="user-table">
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    checked={selectedUsers.length === sortedUsers.length && sortedUsers.length > 0}
                    onChange={handleSelectAll}
                  />
                </th>
                <th
                  className="sortable"
                  onClick={() => {
                    setSortBy('name');
                    setSortOrder(sortBy === 'name' && sortOrder === 'asc' ? 'desc' : 'asc');
                  }}
                >
                  User
                </th>
                <th
                  className="sortable"
                  onClick={() => {
                    setSortBy('role');
                    setSortOrder(sortBy === 'role' && sortOrder === 'asc' ? 'desc' : 'asc');
                  }}
                >
                  Role
                </th>
                <th
                  className="sortable"
                  onClick={() => {
                    setSortBy('status');
                    setSortOrder(sortBy === 'status' && sortOrder === 'asc' ? 'desc' : 'asc');
                  }}
                >
                  Status
                </th>
                <th>Department</th>
                <th>Projects</th>
                <th>Tasks</th>
                <th
                  className="sortable"
                  onClick={() => {
                    setSortBy('lastActive');
                    setSortOrder(sortBy === 'lastActive' && sortOrder === 'asc' ? 'desc' : 'asc');
                  }}
                >
                  Last Active
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="loading-cell">
                    <RefreshCw size={20} className="spinning" />
                    Loading users...
                  </td>
                </tr>
              ) : sortedUsers.length === 0 ? (
                <tr>
                  <td colSpan={9} className="empty-cell">
                    No users found matching your criteria
                  </td>
                </tr>
              ) : (
                sortedUsers.map(user => (
                  <tr key={user.id} className={selectedUsers.includes(user.id) ? 'selected' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.id)}
                        onChange={() => handleUserSelect(user.id)}
                      />
                    </td>
                    <td>
                      <div className="user-cell">
                        <div className="user-avatar">
                          {user.avatar ? (
                            <img src={user.avatar} alt={`${user.firstName} ${user.lastName}`} />
                          ) : (
                            <div className="avatar-placeholder">
                              {user.firstName.charAt(0)}{user.lastName.charAt(0)}
                            </div>
                          )}
                        </div>
                        <div className="user-info">
                          <div className="user-name">{user.firstName} {user.lastName}</div>
                          <div className="user-email">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span 
                        className="role-badge"
                        style={{ backgroundColor: getRoleColor(user.role) + '20', color: getRoleColor(user.role) }}
                      >
                        {user.role.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(user.status) + '20', color: getStatusColor(user.status) }}
                      >
                        {user.status.charAt(0).toUpperCase() + user.status.slice(1)}
                      </span>
                    </td>
                    <td>
                      <div className="department-cell">
                        <div>{user.department}</div>
                        <div className="position">{user.position}</div>
                      </div>
                    </td>
                    <td>{user.projects.length}</td>
                    <td>
                      <div className="tasks-cell">
                        <span className="task-count">{user.tasksCompleted}/{user.tasksAssigned}</span>
                        <div className="task-progress">
                          <div
                            className="progress-fill"
                            style={{ width: `${(user.tasksCompleted / user.tasksAssigned) * 100}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td>{formatLastActive(user.lastActive)}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="action-icon-btn"
                          onClick={() => console.log('Edit user:', user.id)}
                          title="Edit User"
                        >
                          <Edit size={14} />
                        </button>
                        <button
                          className="action-icon-btn"
                          title="View Details"
                        >
                          <Eye size={14} />
                        </button>
                        <button
                          className="action-icon-btn"
                          title={user.status === 'active' ? 'Suspend' : 'Activate'}
                        >
                          {user.status === 'active' ? <Lock size={14} /> : <Unlock size={14} />}
                        </button>
                        <button className="action-icon-btn">
                          <MoreVertical size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="user-management-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>User Management</h1>
          <p>Manage users, roles, and permissions across your organization</p>
        </div>
        <div className="header-actions">
          <button className="action-btn secondary">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="action-btn secondary">
            <Settings size={16} />
            Settings
          </button>
        </div>
      </div>

      {renderStatsCards()}

      <div className="dashboard-tabs">
        <button
          className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <Users size={16} />
          Users ({users.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'roles' ? 'active' : ''}`}
          onClick={() => setActiveTab('roles')}
        >
          <Shield size={16} />
          Roles ({roles.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'permissions' ? 'active' : ''}`}
          onClick={() => setActiveTab('permissions')}
        >
          <Key size={16} />
          Permissions ({permissions.length})
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'users' && renderUserTable()}
        {activeTab === 'roles' && (
          <div className="roles-content">
            <div className="roles-header">
              <h3>Role Management</h3>
              <button
                className="action-btn primary"
                onClick={() => console.log('Create role modal')}
              >
                <Shield size={16} />
                Create Role
              </button>
            </div>
            {/* Role management content will be implemented */}
            <div className="coming-soon">Role management interface coming soon...</div>
          </div>
        )}
        {activeTab === 'permissions' && (
          <div className="permissions-content">
            <div className="permissions-header">
              <h3>Permission Management</h3>
            </div>
            {/* Permission management content will be implemented */}
            <div className="coming-soon">Permission management interface coming soon...</div>
          </div>
        )}
      </div>
    </div>
  );
};