/**
 * Project API Service
 * Handles all project-related API operations for TeamFlow
 */

import { apiClient } from './apiClient';

// Project interfaces aligned with backend schemas
export interface Project {
  id: number;
  name: string;
  description?: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  start_date?: string;
  end_date?: string;
  organization_id: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  created_by_id: number;
  updated_by_id?: number;
  members?: ProjectMember[];
  task_count?: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  organization_id: number;
  status?: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  start_date?: string;
  end_date?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  start_date?: string;
  end_date?: string;
}

export interface ProjectMember {
  id: number;
  user_id: number;
  user_email: string;
  user_name: string;
  role: 'owner' | 'admin' | 'developer' | 'viewer';
  joined_at: string;
  is_active: boolean;
}

export interface ProjectMemberCreate {
  user_email: string;
  role?: 'owner' | 'admin' | 'developer' | 'viewer';
}

export interface ProjectMemberUpdate {
  role: 'owner' | 'admin' | 'developer' | 'viewer';
}

export interface ProjectList {
  projects: Project[];
  total: number;
  skip: number;
  limit: number;
}

export interface ProjectFilters {
  status?: string[];
  priority?: string[];
  organization_id?: number;
  skip?: number;
  limit?: number;
}

// Status and priority options for UI dropdowns
export const PROJECT_STATUSES = [
  { value: 'planning', label: 'Planning', color: 'bg-gray-100 text-gray-800', icon: '📋' },
  { value: 'active', label: 'Active', color: 'bg-green-100 text-green-800', icon: '🚀' },
  { value: 'on_hold', label: 'On Hold', color: 'bg-yellow-100 text-yellow-800', icon: '⏸️' },
  { value: 'completed', label: 'Completed', color: 'bg-blue-100 text-blue-800', icon: '✅' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800', icon: '❌' },
];

export const PROJECT_PRIORITIES = [
  { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800', icon: '📌' },
  { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-800', icon: '📍' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800', icon: '🔥' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-100 text-red-800', icon: '🚨' },
];

export const PROJECT_MEMBER_ROLES = [
  { value: 'owner', label: 'Owner', description: 'Full access and project ownership' },
  { value: 'admin', label: 'Admin', description: 'Manage project and team members' },
  { value: 'developer', label: 'Developer', description: 'Create and manage tasks' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access to project' },
];

class ProjectApiService {
  /**
   * Get all projects with optional filtering
   */
  async getProjects(filters: ProjectFilters = {}): Promise<ProjectList> {
    try {
      const params = new URLSearchParams();
      
      if (filters.status?.length) {
        filters.status.forEach(status => params.append('status', status));
      }
      if (filters.priority?.length) {
        filters.priority.forEach(priority => params.append('priority', priority));
      }
      if (filters.organization_id) {
        params.append('organization_id', filters.organization_id.toString());
      }
      if (filters.skip !== undefined) {
        params.append('skip', filters.skip.toString());
      }
      if (filters.limit !== undefined) {
        params.append('limit', filters.limit.toString());
      }

      const queryString = params.toString();
      const response = await apiClient.get<ProjectList>(
        `/projects${queryString ? `?${queryString}` : ''}`
      );
      
      return response;
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      throw error;
    }
  }

  /**
   * Get a specific project by ID
   */
  async getProject(projectId: number): Promise<Project> {
    try {
      const response = await apiClient.get<Project>(`/projects/${projectId}`);
      return response;
    } catch (error) {
      console.error(`Failed to fetch project ${projectId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new project
   */
  async createProject(projectData: ProjectCreate): Promise<Project> {
    try {
      const response = await apiClient.post<Project>('/projects', projectData);
      return response;
    } catch (error) {
      console.error('Failed to create project:', error);
      throw error;
    }
  }

  /**
   * Update an existing project
   */
  async updateProject(projectId: number, projectData: ProjectUpdate): Promise<Project> {
    try {
      const response = await apiClient.put<Project>(`/projects/${projectId}`, projectData);
      return response;
    } catch (error) {
      console.error(`Failed to update project ${projectId}:`, error);
      throw error;
    }
  }

  /**
   * Delete a project (soft delete)
   */
  async deleteProject(projectId: number): Promise<void> {
    try {
      await apiClient.delete(`/projects/${projectId}`);
    } catch (error) {
      console.error(`Failed to delete project ${projectId}:`, error);
      throw error;
    }
  }

  /**
   * Get project members
   */
  async getProjectMembers(projectId: number): Promise<ProjectMember[]> {
    try {
      const response = await apiClient.get<ProjectMember[]>(`/projects/${projectId}/members`);
      return response;
    } catch (error) {
      console.error(`Failed to fetch project ${projectId} members:`, error);
      throw error;
    }
  }

  /**
   * Add member to project
   */
  async addProjectMember(projectId: number, memberData: ProjectMemberCreate): Promise<ProjectMember> {
    try {
      const response = await apiClient.post<ProjectMember>(
        `/projects/${projectId}/members`,
        memberData
      );
      return response;
    } catch (error) {
      console.error(`Failed to add member to project ${projectId}:`, error);
      throw error;
    }
  }

  /**
   * Update project member role
   */
  async updateProjectMember(
    projectId: number,
    memberId: number,
    memberData: ProjectMemberUpdate
  ): Promise<ProjectMember> {
    try {
      const response = await apiClient.put<ProjectMember>(
        `/projects/${projectId}/members/${memberId}`,
        memberData
      );
      return response;
    } catch (error) {
      console.error(`Failed to update project ${projectId} member ${memberId}:`, error);
      throw error;
    }
  }

  /**
   * Remove member from project
   */
  async removeProjectMember(projectId: number, memberId: number): Promise<void> {
    try {
      await apiClient.delete(`/projects/${projectId}/members/${memberId}`);
    } catch (error) {
      console.error(`Failed to remove member ${memberId} from project ${projectId}:`, error);
      throw error;
    }
  }

  /**
   * Get user's projects
   */
  async getMyProjects(): Promise<Project[]> {
    try {
      const projectList = await this.getProjects({ limit: 100 });
      return projectList.projects;
    } catch (error) {
      console.error('Failed to fetch my projects:', error);
      // Fallback data for development
      return [];
    }
  }
}

// Export singleton instance
export const projectApi = new ProjectApiService();