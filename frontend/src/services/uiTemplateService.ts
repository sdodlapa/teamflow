/**
 * UI Template Service - Day 17 Implementation
 * Service for saving, loading, and managing UI templates built with the drag-and-drop builder
 */

import apiClient from './apiClient';

export interface UITemplate {
  id?: string;
  name: string;
  description?: string;
  category: string;
  tags: string[];
  components: any[];
  preview_image?: string;
  is_public: boolean;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  usage_count?: number;
}

export interface UITemplateCategory {
  id: string;
  name: string;
  description: string;
  template_count: number;
}

export interface SaveUITemplateRequest {
  name: string;
  description?: string;
  category: string;
  tags: string[];
  components: any[];
  is_public: boolean;
}

export interface UITemplateFilters {
  category?: string;
  tags?: string[];
  search?: string;
  is_public?: boolean;
  created_by?: string;
  page?: number;
  limit?: number;
}

class UITemplateService {
  private readonly baseUrl = '/ui-templates';

  /**
   * Save a new UI template
   */
  async saveUITemplate(template: SaveUITemplateRequest): Promise<UITemplate> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/`, template);
      return response;
    } catch (error) {
      console.error('Failed to save UI template:', error);
      throw error;
    }
  }

  /**
   * Update an existing UI template
   */
  async updateUITemplate(id: string, template: Partial<SaveUITemplateRequest>): Promise<UITemplate> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/${id}`, template);
      return response;
    } catch (error) {
      console.error('Failed to update UI template:', error);
      throw error;
    }
  }

  /**
   * Get all UI templates with optional filters
   */
  async getUITemplates(filters: UITemplateFilters = {}): Promise<{
    templates: UITemplate[];
    total: number;
    page: number;
    pages: number;
  }> {
    try {
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, value.toString());
          }
        }
      });

      const response = await apiClient.get(`${this.baseUrl}/?${params.toString()}`);
      return response;
    } catch (error) {
      console.error('Failed to get UI templates:', error);
      throw error;
    }
  }

  /**
   * Get a specific UI template by ID
   */
  async getUITemplate(id: string): Promise<UITemplate> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${id}`);
      return response;
    } catch (error) {
      console.error('Failed to get UI template:', error);
      throw error;
    }
  }

  /**
   * Delete a UI template
   */
  async deleteUITemplate(id: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseUrl}/${id}`);
    } catch (error) {
      console.error('Failed to delete UI template:', error);
      throw error;
    }
  }

  /**
   * Clone a UI template (create a copy)
   */
  async cloneUITemplate(id: string, newName?: string): Promise<UITemplate> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/${id}/clone`, {
        name: newName
      });
      return response;
    } catch (error) {
      console.error('Failed to clone UI template:', error);
      throw error;
    }
  }

  /**
   * Get UI template categories
   */
  async getUITemplateCategories(): Promise<UITemplateCategory[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/categories/`);
      return response;
    } catch (error) {
      console.error('Failed to get UI template categories:', error);
      throw error;
    }
  }

  /**
   * Get popular UI templates
   */
  async getPopularUITemplates(limit: number = 10): Promise<UITemplate[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/popular/?limit=${limit}`);
      return response;
    } catch (error) {
      console.error('Failed to get popular UI templates:', error);
      throw error;
    }
  }

  /**
   * Get user's UI templates
   */
  async getMyUITemplates(page: number = 1, limit: number = 20): Promise<{
    templates: UITemplate[];
    total: number;
    page: number;
    pages: number;
  }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/my-templates/?page=${page}&limit=${limit}`);
      return response;
    } catch (error) {
      console.error('Failed to get my UI templates:', error);
      throw error;
    }
  }

  /**
   * Search UI templates
   */
  async searchUITemplates(query: string, filters: Omit<UITemplateFilters, 'search'> = {}): Promise<{
    templates: UITemplate[];
    total: number;
    suggestions: string[];
  }> {
    try {
      const params = new URLSearchParams({ search: query });
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, value.toString());
          }
        }
      });

      const response = await apiClient.get(`${this.baseUrl}/search/?${params.toString()}`);
      return response;
    } catch (error) {
      console.error('Failed to search UI templates:', error);
      throw error;
    }
  }

  /**
   * Generate preview image for UI template
   */
  async generatePreview(components: any[]): Promise<string> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/generate-preview/`, {
        components
      });
      return response.preview_url;
    } catch (error) {
      console.error('Failed to generate preview:', error);
      // Return placeholder preview for demo
      return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI2Y0ZjRmNCIvPjx0ZXh0IHg9IjEwMCIgeT0iNzUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IiM2NjY2NjYiPkNhbGVuZGFyIFRlbXBsYXRlPC90ZXh0Pjwvc3ZnPg==';
    }
  }

  /**
   * Export UI template to various formats
   */
  async exportUITemplate(id: string, format: 'json' | 'html' | 'pdf' = 'json'): Promise<Blob> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${id}/export/?format=${format}`, {
        responseType: 'blob'
      });
      return response;
    } catch (error) {
      console.error('Failed to export UI template:', error);
      throw error;
    }
  }

  /**
   * Import UI template from file
   */
  async importUITemplate(file: File): Promise<UITemplate> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post(`${this.baseUrl}/import/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response;
    } catch (error) {
      console.error('Failed to import UI template:', error);
      throw error;
    }
  }

  /**
   * Validate UI template structure
   */
  validateUITemplate(template: Partial<UITemplate>): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Required fields validation
    if (!template.name || template.name.trim().length === 0) {
      errors.push('Template name is required');
    }

    if (!template.category || template.category.trim().length === 0) {
      errors.push('Template category is required');
    }

    if (!template.components || !Array.isArray(template.components)) {
      errors.push('Template must have components array');
    } else if (template.components.length === 0) {
      warnings.push('Template has no components');
    }

    // Name length validation
    if (template.name && template.name.length > 100) {
      errors.push('Template name must be less than 100 characters');
    }

    // Description length validation
    if (template.description && template.description.length > 500) {
      errors.push('Template description must be less than 500 characters');
    }

    // Tags validation
    if (template.tags && template.tags.length > 10) {
      warnings.push('Template has more than 10 tags, consider reducing for better discoverability');
    }

    // Component validation
    if (template.components && Array.isArray(template.components)) {
      template.components.forEach((component, index) => {
        if (!component.type) {
          errors.push(`Component ${index + 1} is missing type`);
        }
        if (!component.id) {
          errors.push(`Component ${index + 1} is missing ID`);
        }
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Save template to local storage (fallback when API is not available)
   */
  saveToLocalStorage(template: UITemplate): void {
    try {
      const saved = this.getFromLocalStorage();
      const newTemplate = {
        ...template,
        id: template.id || Date.now().toString(),
        created_at: template.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      const existingIndex = saved.findIndex(t => t.id === newTemplate.id);
      if (existingIndex >= 0) {
        saved[existingIndex] = newTemplate;
      } else {
        saved.push(newTemplate);
      }
      
      localStorage.setItem('ui_templates', JSON.stringify(saved));
    } catch (error) {
      console.error('Failed to save to local storage:', error);
    }
  }

  /**
   * Load templates from local storage
   */
  getFromLocalStorage(): UITemplate[] {
    try {
      const saved = localStorage.getItem('ui_templates');
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.error('Failed to load from local storage:', error);
      return [];
    }
  }

  /**
   * Delete template from local storage
   */
  deleteFromLocalStorage(id: string): void {
    try {
      const saved = this.getFromLocalStorage();
      const filtered = saved.filter(t => t.id !== id);
      localStorage.setItem('ui_templates', JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete from local storage:', error);
    }
  }
}

// Create singleton instance
const uiTemplateService = new UITemplateService();

export default uiTemplateService;