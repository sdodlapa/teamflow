/**
 * Template persistence hook for saving and loading templates
 */
import { useState, useCallback, useEffect } from 'react';
import { useAuth } from './useAuth';
import { 
  templateApiService, 
  TemplateData, 
  CreateTemplateRequest,
  UpdateTemplateRequest
} from '../services/templateApiService';
import { Entity, Relationship, DomainConfig } from '../types/template';

export interface UseTemplatePersistenceProps {
  initialTemplateId?: string;
}

export interface UseTemplatePersistenceResult {
  // Template data
  currentTemplate: TemplateData | null;
  isSaving: boolean;
  isLoading: boolean;
  saveError: string | null;
  loadError: string | null;
  
  // Template operations
  loadTemplate: (templateId: string) => Promise<TemplateData | null>;
  saveTemplate: (data: {
    name: string;
    description?: string;
    domainConfig: DomainConfig;
    entities: Entity[];
    relationships: Relationship[];
    isPublic?: boolean;
    tags?: string[];
    changeDescription?: string;
  }) => Promise<TemplateData | null>;
  createTemplate: (data: CreateTemplateRequest) => Promise<TemplateData | null>;
  duplicateTemplate: (templateId: string, newName: string) => Promise<TemplateData | null>;
  
  // Version management
  templateVersions: any[];
  loadVersions: (templateId: string) => Promise<any[]>;
  revertToVersion: (templateId: string, versionNumber: number) => Promise<TemplateData | null>;
  
  // Template status management
  publishTemplate: (templateId: string) => Promise<TemplateData | null>;
  archiveTemplate: (templateId: string) => Promise<TemplateData | null>;
  
  // Template search
  searchTemplates: (query: string) => Promise<TemplateData[]>;
  recentTemplates: TemplateData[];
}

/**
 * Hook for persisting templates to the backend API
 */
export const useTemplatePersistence = (
  props?: UseTemplatePersistenceProps
): UseTemplatePersistenceResult => {
  const { isAuthenticated, user } = useAuth();
  const [currentTemplate, setCurrentTemplate] = useState<TemplateData | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [templateVersions, setTemplateVersions] = useState<any[]>([]);
  const [recentTemplates, setRecentTemplates] = useState<TemplateData[]>([]);
  
  // Initialize with template ID if provided
  useEffect(() => {
    if (props?.initialTemplateId && isAuthenticated) {
      loadTemplate(props.initialTemplateId);
    }
  }, [props?.initialTemplateId, isAuthenticated]);
  
  // Load recent templates when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadRecentTemplates();
    }
  }, [isAuthenticated]);
  
  // Load recent templates
  const loadRecentTemplates = useCallback(async () => {
    try {
      const response = await templateApiService.getTemplates({
        page: 1,
        limit: 5,
        sortBy: 'updatedAt',
        sortOrder: 'desc'
      });
      
      setRecentTemplates(response.templates);
    } catch (error) {
      console.error('Failed to load recent templates', error);
    }
  }, []);
  
  // Load template by ID
  const loadTemplate = useCallback(async (templateId: string): Promise<TemplateData | null> => {
    if (!isAuthenticated) {
      setLoadError('Must be authenticated to load templates');
      return null;
    }
    
    setIsLoading(true);
    setLoadError(null);
    
    try {
      const template = await templateApiService.getTemplate(templateId);
      setCurrentTemplate(template);
      return template;
    } catch (error: any) {
      console.error('Failed to load template:', error);
      setLoadError(error.message || 'Failed to load template');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);
  
  // Save existing template
  const saveTemplate = useCallback(async (data: {
    name: string;
    description?: string;
    domainConfig: DomainConfig;
    entities: Entity[];
    relationships: Relationship[];
    isPublic?: boolean;
    tags?: string[];
    changeDescription?: string;
  }): Promise<TemplateData | null> => {
    if (!isAuthenticated) {
      setSaveError('Must be authenticated to save templates');
      return null;
    }
    
    if (!currentTemplate) {
      // If no current template, create a new one
      return createTemplate(data as CreateTemplateRequest);
    }
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      const updateData: UpdateTemplateRequest = {
        name: data.name,
        description: data.description,
        domainConfig: data.domainConfig,
        entities: data.entities,
        relationships: data.relationships,
        isPublic: data.isPublic,
        tags: data.tags,
        changeDescription: data.changeDescription || `Updated by ${user?.name || 'user'}`
      };
      
      const updatedTemplate = await templateApiService.updateTemplate(
        currentTemplate.id, 
        updateData
      );
      
      setCurrentTemplate(updatedTemplate);
      await loadRecentTemplates(); // Refresh recent templates
      return updatedTemplate;
    } catch (error: any) {
      console.error('Failed to save template:', error);
      setSaveError(error.message || 'Failed to save template');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [isAuthenticated, currentTemplate, user]);
  
  // Create new template
  const createTemplate = useCallback(async (data: CreateTemplateRequest): Promise<TemplateData | null> => {
    if (!isAuthenticated) {
      setSaveError('Must be authenticated to create templates');
      return null;
    }
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      const newTemplate = await templateApiService.createTemplate(data);
      setCurrentTemplate(newTemplate);
      await loadRecentTemplates(); // Refresh recent templates
      return newTemplate;
    } catch (error: any) {
      console.error('Failed to create template:', error);
      setSaveError(error.message || 'Failed to create template');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [isAuthenticated]);
  
  // Duplicate template
  const duplicateTemplate = useCallback(async (templateId: string, newName: string): Promise<TemplateData | null> => {
    if (!isAuthenticated) {
      setSaveError('Must be authenticated to duplicate templates');
      return null;
    }
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      const duplicatedTemplate = await templateApiService.duplicateTemplate(templateId, newName);
      setCurrentTemplate(duplicatedTemplate);
      await loadRecentTemplates(); // Refresh recent templates
      return duplicatedTemplate;
    } catch (error: any) {
      console.error('Failed to duplicate template:', error);
      setSaveError(error.message || 'Failed to duplicate template');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [isAuthenticated]);
  
  // Load template versions
  const loadVersions = useCallback(async (templateId: string): Promise<any[]> => {
    if (!isAuthenticated) {
      return [];
    }
    
    try {
      const versions = await templateApiService.getTemplateVersions(templateId);
      setTemplateVersions(versions);
      return versions;
    } catch (error) {
      console.error('Failed to load template versions', error);
      return [];
    }
  }, [isAuthenticated]);
  
  // Revert to a specific version
  const revertToVersion = useCallback(async (
    templateId: string, 
    versionNumber: number
  ): Promise<TemplateData | null> => {
    if (!isAuthenticated) {
      setSaveError('Must be authenticated to revert templates');
      return null;
    }
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      const revertedTemplate = await templateApiService.revertToVersion(templateId, versionNumber);
      setCurrentTemplate(revertedTemplate);
      return revertedTemplate;
    } catch (error: any) {
      console.error('Failed to revert template:', error);
      setSaveError(error.message || 'Failed to revert template');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [isAuthenticated]);
  
  // Publish template
  const publishTemplate = useCallback(async (templateId: string): Promise<TemplateData | null> => {
    if (!isAuthenticated) {
      setSaveError('Must be authenticated to publish templates');
      return null;
    }
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      const publishedTemplate = await templateApiService.publishTemplate(templateId);
      setCurrentTemplate(publishedTemplate);
      return publishedTemplate;
    } catch (error: any) {
      console.error('Failed to publish template:', error);
      setSaveError(error.message || 'Failed to publish template');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [isAuthenticated]);
  
  // Archive template
  const archiveTemplate = useCallback(async (templateId: string): Promise<TemplateData | null> => {
    if (!isAuthenticated) {
      setSaveError('Must be authenticated to archive templates');
      return null;
    }
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      const archivedTemplate = await templateApiService.archiveTemplate(templateId);
      setCurrentTemplate(archivedTemplate);
      return archivedTemplate;
    } catch (error: any) {
      console.error('Failed to archive template:', error);
      setSaveError(error.message || 'Failed to archive template');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [isAuthenticated]);
  
  // Search templates
  const searchTemplates = useCallback(async (query: string): Promise<TemplateData[]> => {
    if (!isAuthenticated) {
      return [];
    }
    
    try {
      const results = await templateApiService.searchPublicTemplates({
        query,
        limit: 10,
        sortBy: 'relevance'
      });
      return results;
    } catch (error) {
      console.error('Failed to search templates', error);
      return [];
    }
  }, [isAuthenticated]);
  
  return {
    currentTemplate,
    isSaving,
    isLoading,
    saveError,
    loadError,
    loadTemplate,
    saveTemplate,
    createTemplate,
    duplicateTemplate,
    templateVersions,
    loadVersions,
    revertToVersion,
    publishTemplate,
    archiveTemplate,
    searchTemplates,
    recentTemplates
  };
};

export default useTemplatePersistence;