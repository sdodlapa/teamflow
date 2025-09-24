/**
 * TeamFlow Template API Service
 * Handles all template-related API operations with backend persistence
 */

import { apiClient } from './apiClient';
import { DomainConfig, Entity, Relationship } from '../types/template';

export interface TemplateData {
  id: string;
  name: string;
  description: string;
  domainConfig: DomainConfig;
  entities: Entity[];
  relationships: Relationship[];
  metadata: {
    version: number;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    collaborators: string[];
    tags: string[];
    isPublic: boolean;
  };
  status: 'draft' | 'published' | 'archived';
}

export interface TemplateVersion {
  id: string;
  templateId: string;
  version: number;
  changes: {
    entities?: Partial<Entity>[];
    relationships?: Partial<Relationship>[];
    config?: Partial<DomainConfig>;
  };
  changeDescription: string;
  createdAt: string;
  createdBy: string;
}

export interface TemplateCollaborationHistory {
  id: string;
  templateId: string;
  userId: string;
  userName: string;
  action: 'join' | 'leave' | 'edit' | 'comment' | 'save';
  timestamp: string;
  data?: any;
}

export interface CreateTemplateRequest {
  name: string;
  description?: string;
  domainConfig: DomainConfig;
  entities?: Entity[];
  relationships?: Relationship[];
  tags?: string[];
  isPublic?: boolean;
}

export interface UpdateTemplateRequest {
  name?: string;
  description?: string;
  domainConfig?: DomainConfig;
  entities?: Entity[];
  relationships?: Relationship[];
  tags?: string[];
  isPublic?: boolean;
  changeDescription?: string;
}

class TemplateApiService {
  private baseUrl = '/templates';

  /**
   * Get all templates for the current user
   */
  async getTemplates(options?: {
    page?: number;
    limit?: number;
    search?: string;
    tags?: string[];
    status?: 'draft' | 'published' | 'archived';
    sortBy?: 'name' | 'createdAt' | 'updatedAt';
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    templates: TemplateData[];
    total: number;
    page: number;
    limit: number;
  }> {
    const params = new URLSearchParams();
    
    if (options?.page) params.append('page', options.page.toString());
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.search) params.append('search', options.search);
    if (options?.tags) options.tags.forEach(tag => params.append('tags', tag));
    if (options?.status) params.append('status', options.status);
    if (options?.sortBy) params.append('sortBy', options.sortBy);
    if (options?.sortOrder) params.append('sortOrder', options.sortOrder);

    const response = await apiClient.get(`${this.baseUrl}?${params.toString()}`);
    return response.data;
  }

  /**
   * Get a specific template by ID
   */
  async getTemplate(templateId: string): Promise<TemplateData> {
    const response = await apiClient.get(`${this.baseUrl}/${templateId}`);
    return response.data;
  }

  /**
   * Create a new template
   */
  async createTemplate(templateData: CreateTemplateRequest): Promise<TemplateData> {
    const response = await apiClient.post(this.baseUrl, templateData);
    return response.data;
  }

  /**
   * Update an existing template
   */
  async updateTemplate(
    templateId: string, 
    updateData: UpdateTemplateRequest
  ): Promise<TemplateData> {
    const response = await apiClient.put(`${this.baseUrl}/${templateId}`, updateData);
    return response.data;
  }

  /**
   * Delete a template
   */
  async deleteTemplate(templateId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${templateId}`);
  }

  /**
   * Duplicate a template
   */
  async duplicateTemplate(
    templateId: string, 
    newName: string
  ): Promise<TemplateData> {
    const response = await apiClient.post(`${this.baseUrl}/${templateId}/duplicate`, {
      name: newName
    });
    return response.data;
  }

  /**
   * Save template as draft (auto-save functionality)
   */
  async saveDraft(
    templateId: string,
    draftData: {
      entities: Entity[];
      relationships: Relationship[];
      config: DomainConfig;
    }
  ): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${templateId}/draft`, draftData);
  }

  /**
   * Publish a draft template
   */
  async publishTemplate(templateId: string): Promise<TemplateData> {
    const response = await apiClient.post(`${this.baseUrl}/${templateId}/publish`);
    return response.data;
  }

  /**
   * Archive a template
   */
  async archiveTemplate(templateId: string): Promise<TemplateData> {
    const response = await apiClient.post(`${this.baseUrl}/${templateId}/archive`);
    return response.data;
  }

  /**
   * Get template version history
   */
  async getTemplateVersions(templateId: string): Promise<TemplateVersion[]> {
    const response = await apiClient.get(`${this.baseUrl}/${templateId}/versions`);
    return response.data;
  }

  /**
   * Get a specific template version
   */
  async getTemplateVersion(
    templateId: string, 
    version: number
  ): Promise<TemplateVersion> {
    const response = await apiClient.get(`${this.baseUrl}/${templateId}/versions/${version}`);
    return response.data;
  }

  /**
   * Revert template to a specific version
   */
  async revertToVersion(
    templateId: string, 
    version: number
  ): Promise<TemplateData> {
    const response = await apiClient.post(`${this.baseUrl}/${templateId}/revert/${version}`);
    return response.data;
  }

  /**
   * Get collaboration history for a template
   */
  async getCollaborationHistory(
    templateId: string,
    limit?: number
  ): Promise<TemplateCollaborationHistory[]> {
    const params = limit ? `?limit=${limit}` : '';
    const response = await apiClient.get(`${this.baseUrl}/${templateId}/collaboration${params}`);
    return response.data;
  }

  /**
   * Add collaborator to template
   */
  async addCollaborator(
    templateId: string,
    userId: string,
    permissions: 'read' | 'write' | 'admin' = 'write'
  ): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${templateId}/collaborators`, {
      userId,
      permissions
    });
  }

  /**
   * Remove collaborator from template
   */
  async removeCollaborator(templateId: string, userId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${templateId}/collaborators/${userId}`);
  }

  /**
   * Search templates across all public templates
   */
  async searchPublicTemplates(options: {
    query: string;
    tags?: string[];
    limit?: number;
    sortBy?: 'relevance' | 'popularity' | 'recent';
  }): Promise<TemplateData[]> {
    const params = new URLSearchParams();
    params.append('q', options.query);
    if (options.tags) options.tags.forEach(tag => params.append('tags', tag));
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.sortBy) params.append('sortBy', options.sortBy);

    const response = await apiClient.get(`${this.baseUrl}/search?${params.toString()}`);
    return response.data;
  }

  /**
   * Get template analytics and usage statistics
   */
  async getTemplateAnalytics(templateId: string): Promise<{
    views: number;
    clones: number;
    collaborators: number;
    versions: number;
    lastActivity: string;
    popularEntities: string[];
    usageByDate: { date: string; views: number; edits: number }[];
  }> {
    const response = await apiClient.get(`${this.baseUrl}/${templateId}/analytics`);
    return response.data;
  }

  /**
   * Export template to various formats
   */
  async exportTemplate(
    templateId: string,
    format: 'json' | 'yaml' | 'sql' | 'typescript' | 'python'
  ): Promise<Blob> {
    const response = await apiClient.get(`${this.baseUrl}/${templateId}/export/${format}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  /**
   * Import template from file
   */
  async importTemplate(file: File): Promise<TemplateData> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${this.baseUrl}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

// Export singleton instance
export const templateApiService = new TemplateApiService();
export default templateApiService;