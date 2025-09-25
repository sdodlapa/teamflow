import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { 
  templateApi, 
  TemplateConfigResponse, 
  TemplateConfigCreate, 
  TemplateMetadata 
} from '../services/templateApi';
import { DomainConfig, ValidationResult } from '../types/template';

interface UseTemplateManager {
  templates: TemplateMetadata[];
  loading: boolean;
  currentTemplate: TemplateConfigResponse | null;
  
  // Template operations
  createTemplate: (data: TemplateConfigCreate) => Promise<TemplateConfigResponse | null>;
  updateTemplate: (id: string, data: Partial<TemplateConfigCreate>) => Promise<TemplateConfigResponse | null>;
  deleteTemplate: (id: string) => Promise<boolean>;
  loadTemplate: (id: string) => Promise<TemplateConfigResponse | null>;
  cloneTemplate: (id: string, newName: string) => Promise<TemplateConfigResponse | null>;
  
  // Template validation
  validateTemplate: (config: DomainConfig) => Promise<ValidationResult | null>;
  
  // Template list operations
  refreshTemplates: () => Promise<void>;
  searchTemplates: (query: string) => Promise<void>;
}

export const useTemplateManager = (): UseTemplateManager => {
  const [templates, setTemplates] = useState<TemplateMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentTemplate, setCurrentTemplate] = useState<TemplateConfigResponse | null>(null);

  // Load templates on mount
  useEffect(() => {
    refreshTemplates();
  }, []);

  const refreshTemplates = async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await templateApi.listTemplates({ limit: 50 });
      setTemplates(response.templates);
    } catch (error: any) {
      console.error('Failed to load templates:', error);
      toast.error('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const searchTemplates = async (query: string): Promise<void> => {
    try {
      setLoading(true);
      const response = await templateApi.listTemplates({ 
        search: query, 
        limit: 50 
      });
      setTemplates(response.templates);
    } catch (error: any) {
      console.error('Failed to search templates:', error);
      toast.error('Failed to search templates');
    } finally {
      setLoading(false);
    }
  };

  const createTemplate = async (data: TemplateConfigCreate): Promise<TemplateConfigResponse | null> => {
    try {
      setLoading(true);
      const newTemplate = await templateApi.createTemplate(data);
      // Convert to TemplateMetadata for the list
      const templateMetadata: TemplateMetadata = {
        id: newTemplate.id,
        name: newTemplate.name,
        title: newTemplate.title,
        description: newTemplate.description,
        domain_type: newTemplate.config.domain_type || 'custom',
        version: newTemplate.config.version || '1.0.0',
        tags: newTemplate.tags,
        created_at: newTemplate.created_at,
        updated_at: newTemplate.updated_at,
        created_by: newTemplate.created_by,
        downloads: newTemplate.downloads,
        rating: newTemplate.rating,
        is_public: newTemplate.is_public
      };
      setTemplates(prev => [templateMetadata, ...prev]);
      setCurrentTemplate(newTemplate);
      toast.success('Template created successfully!');
      return newTemplate;
    } catch (error: any) {
      console.error('Failed to create template:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to create template';
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateTemplate = async (id: string, data: Partial<TemplateConfigCreate>): Promise<TemplateConfigResponse | null> => {
    try {
      setLoading(true);
      const updatedTemplate = await templateApi.updateTemplate(id, data);
      // Convert to TemplateMetadata for the list
      const templateMetadata: TemplateMetadata = {
        id: updatedTemplate.id,
        name: updatedTemplate.name,
        title: updatedTemplate.title,
        description: updatedTemplate.description,
        domain_type: updatedTemplate.config.domain_type || 'custom',
        version: updatedTemplate.config.version || '1.0.0',
        tags: updatedTemplate.tags,
        created_at: updatedTemplate.created_at,
        updated_at: updatedTemplate.updated_at,
        created_by: updatedTemplate.created_by,
        downloads: updatedTemplate.downloads,
        rating: updatedTemplate.rating,
        is_public: updatedTemplate.is_public
      };
      setTemplates(prev => prev.map(t => t.id === id ? templateMetadata : t));
      if (currentTemplate?.id === id) {
        setCurrentTemplate(updatedTemplate);
      }
      toast.success('Template updated successfully!');
      return updatedTemplate;
    } catch (error: any) {
      console.error('Failed to update template:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to update template';
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteTemplate = async (id: string): Promise<boolean> => {
    try {
      setLoading(true);
      await templateApi.deleteTemplate(id);
      setTemplates(prev => prev.filter(t => t.id !== id));
      if (currentTemplate?.id === id) {
        setCurrentTemplate(null);
      }
      toast.success('Template deleted successfully!');
      return true;
    } catch (error: any) {
      console.error('Failed to delete template:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to delete template';
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = async (id: string): Promise<TemplateConfigResponse | null> => {
    try {
      setLoading(true);
      const template = await templateApi.getTemplate(id);
      setCurrentTemplate(template);
      return template;
    } catch (error: any) {
      console.error('Failed to load template:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to load template';
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const cloneTemplate = async (id: string, newName: string): Promise<TemplateConfigResponse | null> => {
    try {
      setLoading(true);
      const clonedTemplate = await templateApi.cloneTemplate(id, newName);
      // Convert to TemplateMetadata for the list
      const templateMetadata: TemplateMetadata = {
        id: clonedTemplate.id,
        name: clonedTemplate.name,
        title: clonedTemplate.title,
        description: clonedTemplate.description,
        domain_type: clonedTemplate.config.domain_type || 'custom',
        version: clonedTemplate.config.version || '1.0.0',
        tags: clonedTemplate.tags,
        created_at: clonedTemplate.created_at,
        updated_at: clonedTemplate.updated_at,
        created_by: clonedTemplate.created_by,
        downloads: clonedTemplate.downloads,
        rating: clonedTemplate.rating,
        is_public: clonedTemplate.is_public
      };
      setTemplates(prev => [templateMetadata, ...prev]);
      toast.success('Template cloned successfully!');
      return clonedTemplate;
    } catch (error: any) {
      console.error('Failed to clone template:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to clone template';
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const validateTemplate = async (config: DomainConfig): Promise<ValidationResult | null> => {
    try {
      const result = await templateApi.validateTemplate(config);
      return {
        is_valid: result.is_valid,
        errors: result.errors,
        warnings: result.warnings
      };
    } catch (error: any) {
      console.error('Failed to validate template:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to validate template';
      toast.error(errorMessage);
      return null;
    }
  };

  return {
    templates,
    loading,
    currentTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    loadTemplate,
    cloneTemplate,
    validateTemplate,
    refreshTemplates,
    searchTemplates,
  };
};