/**
 * Project Data Hooks
 * React Query hooks for project data management
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../utils/apiClient';
import { queryKeys } from '../lib/queryClient';
import { useToast } from '../contexts/ToastContext';

// Types
export interface Project {
  id: number;
  name: string;
  description?: string;
  status: 'active' | 'completed' | 'on_hold' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  start_date?: string;
  due_date?: string;
  completion_percentage: number;
  budget?: number;
  spent_amount?: number;
  team_members: ProjectMember[];
  task_count: number;
  completed_tasks: number;
  created_at: string;
  updated_at: string;
  created_by: number;
  organization_id: number;
}

export interface ProjectMember {
  id: number;
  user_id: number;
  user_email: string;
  user_name: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  joined_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  priority: Project['priority'];
  start_date?: string;
  due_date?: string;
  budget?: number;
  team_members?: Array<{
    user_email: string;
    role: ProjectMember['role'];
  }>;
}

export interface ProjectUpdate extends Partial<ProjectCreate> {
  status?: Project['status'];
  completion_percentage?: number;
  spent_amount?: number;
}

export interface ProjectFilters {
  status?: Project['status'][];
  priority?: Project['priority'][];
  team_member_id?: number;
  due_date_from?: string;
  due_date_to?: string;
  search?: string;
}

// API functions
const projectApi = {
  // Get all projects with filtering
  getProjects: async (filters?: ProjectFilters): Promise<Project[]> => {
    const params = new URLSearchParams();
    
    if (filters?.status?.length) {
      filters.status.forEach(status => params.append('status', status));
    }
    if (filters?.priority?.length) {
      filters.priority.forEach(priority => params.append('priority', priority));
    }
    if (filters?.team_member_id) {
      params.append('team_member_id', filters.team_member_id.toString());
    }
    if (filters?.due_date_from) {
      params.append('due_date_from', filters.due_date_from);
    }
    if (filters?.due_date_to) {
      params.append('due_date_to', filters.due_date_to);
    }
    if (filters?.search) {
      params.append('search', filters.search);
    }
    
    const queryString = params.toString();
    const url = `/projects${queryString ? `?${queryString}` : ''}`;
    
    const response = await apiClient.get<Project[]>(url);
    return response.data;
  },
  
  // Get single project
  getProject: async (id: number): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${id}`);
    return response.data;
  },
  
  // Create new project
  createProject: async (data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', data);
    return response.data;
  },
  
  // Update project
  updateProject: async (id: number, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.put<Project>(`/projects/${id}`, data);
    return response.data;
  },
  
  // Delete project
  deleteProject: async (id: number): Promise<void> => {
    await apiClient.delete(`/projects/${id}`);
  },
  
  // Get project tasks
  getProjectTasks: async (projectId: number): Promise<any[]> => {
    const response = await apiClient.get(`/projects/${projectId}/tasks`);
    return response.data;
  },
  
  // Add team member to project
  addTeamMember: async (
    projectId: number,
    data: { user_email: string; role: ProjectMember['role'] }
  ): Promise<ProjectMember> => {
    const response = await apiClient.post(`/projects/${projectId}/members`, data);
    return response.data;
  },
  
  // Remove team member from project
  removeTeamMember: async (projectId: number, memberId: number): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/members/${memberId}`);
  },
  
  // Update team member role
  updateTeamMemberRole: async (
    projectId: number,
    memberId: number,
    role: ProjectMember['role']
  ): Promise<ProjectMember> => {
    const response = await apiClient.patch(`/projects/${projectId}/members/${memberId}`, { role });
    return response.data;
  },
  
  // Get project statistics
  getProjectStats: async (): Promise<{
    total: number;
    by_status: Record<Project['status'], number>;
    by_priority: Record<Project['priority'], number>;
    overdue: number;
    due_this_week: number;
    completion_average: number;
  }> => {
    const response = await apiClient.get('/projects/stats');
    return response.data;
  },
};

// React Query Hooks

/**
 * Hook to fetch all projects
 */
export const useProjects = (filters?: ProjectFilters) => {
  return useQuery({
    queryKey: queryKeys.projects.list(filters),
    queryFn: () => projectApi.getProjects(filters),
    staleTime: 3 * 60 * 1000, // 3 minutes
    select: (data) => {
      // Sort projects by priority and due date
      return data.sort((a, b) => {
        const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
        const aPriority = priorityOrder[a.priority];
        const bPriority = priorityOrder[b.priority];
        
        if (aPriority !== bPriority) {
          return aPriority - bPriority;
        }
        
        // If same priority, sort by due date (earliest first)
        if (a.due_date && b.due_date) {
          return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
        }
        
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
    },
  });
};

/**
 * Hook to fetch a single project
 */
export const useProject = (id: number, enabled = true) => {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => projectApi.getProject(id),
    enabled: enabled && !!id,
  });
};

/**
 * Hook to fetch project tasks
 */
export const useProjectTasks = (projectId: number, enabled = true) => {
  return useQuery({
    queryKey: queryKeys.projects.tasks(projectId),
    queryFn: () => projectApi.getProjectTasks(projectId),
    enabled: enabled && !!projectId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook to fetch project statistics
 */
export const useProjectStats = () => {
  return useQuery({
    queryKey: [...queryKeys.projects.all, 'stats'],
    queryFn: projectApi.getProjectStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to create a new project
 */
export const useCreateProject = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: projectApi.createProject,
    onSuccess: (_data) => {
      toast.success('Project created successfully!');
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.lists() });
      queryClient.invalidateQueries({ queryKey: [...queryKeys.projects.all, 'stats'] });
    },
    onError: () => {
      toast.error('Failed to create project');
    },
  });
};

/**
 * Hook to update a project
 */
export const useUpdateProject = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProjectUpdate }) =>
      projectApi.updateProject(id, data),
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.projects.detail(id) });
      
      // Snapshot current value
      const previousProject = queryClient.getQueryData(queryKeys.projects.detail(id));
      
      // Optimistically update
      queryClient.setQueryData(queryKeys.projects.detail(id), (old: any) => ({
        ...old,
        ...data,
        updated_at: new Date().toISOString(),
      }));
      
      return { previousProject, id };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousProject) {
        queryClient.setQueryData(
          queryKeys.projects.detail(context.id),
          context.previousProject
        );
      }
      toast.error('Failed to update project');
    },
    onSuccess: () => {
      toast.success('Project updated successfully!');
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.lists() });
    },
  });
};

/**
 * Hook to delete a project
 */
export const useDeleteProject = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: projectApi.deleteProject,
    onSuccess: () => {
      toast.success('Project deleted successfully');
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.lists() });
      queryClient.invalidateQueries({ queryKey: [...queryKeys.projects.all, 'stats'] });
    },
    onError: () => {
      toast.error('Failed to delete project');
    },
  });
};

/**
 * Hook to add a team member to a project
 */
export const useAddTeamMember = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: ({ 
      projectId, 
      data 
    }: { 
      projectId: number; 
      data: { user_email: string; role: ProjectMember['role'] } 
    }) => projectApi.addTeamMember(projectId, data),
    onSuccess: (_data, variables) => {
      toast.success('Team member added successfully!');
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.projects.detail(variables.projectId) 
      });
    },
    onError: () => {
      toast.error('Failed to add team member');
    },
  });
};

/**
 * Hook to remove a team member from a project
 */
export const useRemoveTeamMember = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: ({ projectId, memberId }: { projectId: number; memberId: number }) =>
      projectApi.removeTeamMember(projectId, memberId),
    onSuccess: (_data, variables) => {
      toast.success('Team member removed successfully');
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.projects.detail(variables.projectId) 
      });
    },
    onError: () => {
      toast.error('Failed to remove team member');
    },
  });
};

/**
 * Hook to update team member role
 */
export const useUpdateTeamMemberRole = () => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  return useMutation({
    mutationFn: ({ 
      projectId, 
      memberId, 
      role 
    }: { 
      projectId: number; 
      memberId: number; 
      role: ProjectMember['role'] 
    }) => projectApi.updateTeamMemberRole(projectId, memberId, role),
    onSuccess: (_data, variables) => {
      toast.success('Team member role updated successfully!');
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.projects.detail(variables.projectId) 
      });
    },
    onError: () => {
      toast.error('Failed to update team member role');
    },
  });
};