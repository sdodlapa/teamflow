// Template API service for backend integration
import apiClient from './apiClient';
import { DomainConfig, Entity, Relationship } from '../types/template';

// Backend API types (matching Pydantic schemas)
export interface TemplateConfigCreate {
  name: string;
  title: string;
  description?: string;
  tags?: string[];
  is_public?: boolean;
  config: DomainConfig;
}

export interface TemplateConfigUpdate {
  title?: string;
  description?: string;
  tags?: string[];
  is_public?: boolean;
  config?: DomainConfig;
}

export interface TemplateConfigResponse {
  id: string;
  name: string;
  title: string;
  description?: string;
  tags: string[];
  is_public: boolean;
  config: DomainConfig;
  created_at: string;
  updated_at: string;
  created_by: string;
  downloads: number;
  rating?: number;
}

export interface TemplateListResponse {
  templates: TemplateMetadata[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface TemplateMetadata {
  id: string;
  name: string;
  title: string;
  description?: string;
  domain_type: string;
  version: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  created_by: string;
  downloads: number;
  rating?: number;
  is_public: boolean;
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface ValidationResponse {
  is_valid: boolean;
  errors?: ValidationError[];
  warnings?: ValidationError[];
}

export interface GenerationRequest {
  domain_config: DomainConfig;
  generate_backend?: boolean;
  generate_frontend?: boolean;
  target_directory?: string;
}

export interface GeneratedFile {
  path: string;
  type: string;
  size: number;
  checksum: string;
}

export interface GenerationResponse {
  success: boolean;
  files_generated: GeneratedFile[];
  errors?: string[];
  warnings?: string[];
  task_id?: string;
  message?: string;
}

export interface GenerationStatus {
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  total_steps: number;
  files_generated: number;
  errors: string[];
  started_at?: string;
  completed_at?: string;
}

export interface ListTemplatesParams {
  skip?: number;
  limit?: number;
  domain_type?: string;
  search?: string;
}

class TemplateApiService {
  private readonly basePath = '/templates';
  
  // Template CRUD operations
  async createTemplate(templateData: TemplateConfigCreate): Promise<TemplateConfigResponse> {
    return apiClient.post(this.basePath, templateData);
  }
  
  async getTemplate(templateId: string): Promise<TemplateConfigResponse> {
    return apiClient.get(`${this.basePath}/${templateId}`);
  }
  
  async updateTemplate(templateId: string, templateData: TemplateConfigUpdate): Promise<TemplateConfigResponse> {
    return apiClient.put(`${this.basePath}/${templateId}`, templateData);
  }
  
  async deleteTemplate(templateId: string): Promise<{ message: string }> {
    return apiClient.delete(`${this.basePath}/${templateId}`);
  }
  
  async listTemplates(params: ListTemplatesParams = {}): Promise<TemplateListResponse> {
    const queryParams = new URLSearchParams();
    if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params.domain_type) queryParams.append('domain_type', params.domain_type);
    if (params.search) queryParams.append('search', params.search);
    
    const url = queryParams.toString() ? `${this.basePath}?${queryParams}` : this.basePath;
    return apiClient.get(url);
  }
  
  // Template validation
  async validateTemplate(config: DomainConfig): Promise<ValidationResponse> {
    return apiClient.post(`${this.basePath}/validate`, { config });
  }
  
  // Code generation
  async generateCode(request: GenerationRequest): Promise<GenerationResponse> {
    return apiClient.post(`${this.basePath}/generate`, request);
  }
  
  async getGenerationStatus(taskId: string): Promise<GenerationStatus> {
    return apiClient.get(`${this.basePath}/generate/${taskId}/status`);
  }
  
  // Template utility operations
  async checkNameAvailability(name: string): Promise<{ available: boolean }> {
    return apiClient.get(`${this.basePath}/check-name/${encodeURIComponent(name)}`);
  }
  
  async cloneTemplate(templateId: string, newName: string): Promise<TemplateConfigResponse> {
    return apiClient.post(`${this.basePath}/${templateId}/clone?new_name=${encodeURIComponent(newName)}`);
  }
  
  async getTemplatePreview(templateId: string): Promise<any> {
    return apiClient.get(`${this.basePath}/${templateId}/preview`);
  }
  
  // Import/Export operations
  async importTemplate(fileContent: any): Promise<TemplateConfigResponse> {
    return apiClient.post(`${this.basePath}/import`, fileContent);
  }
  
  async exportTemplate(templateId: string): Promise<any> {
    return apiClient.get(`${this.basePath}/${templateId}/export`);
  }
  
  // Helper method to convert frontend template data to backend format
  convertToBackendFormat(
    domainConfig: DomainConfig,
    entities: Entity[],
    relationships: Relationship[]
  ): DomainConfig {
    // Transform entities to backend format
    const backendEntities = entities.map(entity => ({
      name: entity.name.toLowerCase().replace(/\s+/g, '_'),
      title: entity.name,
      description: entity.description,
      fields: entity.fields.map(field => ({
        name: field.name.toLowerCase().replace(/\s+/g, '_'),
        title: field.title || field.name,
        type: field.type,
        required: field.required || false,
        default_value: field.defaultValue,
        validation: field.validation ? {
          min_length: field.validation.min_length,
          max_length: field.validation.max_length,
          pattern: field.validation.pattern,
          min_value: field.validation.min_value,
          max_value: field.validation.max_value,
          choices: field.validation.choices,
          custom_validator: field.validation.custom_validator
        } : undefined,
        ui_config: field.uiConfig ? {
          widget: field.uiConfig.widget,
          placeholder: field.uiConfig.placeholder,
          help_text: field.uiConfig.help_text,
          grid_column: field.uiConfig.grid_column,
          hide_in_list: field.uiConfig.hide_in_list,
          hide_in_form: field.uiConfig.hide_in_form
        } : undefined
      })),
      relationships: relationships
        .filter(rel => rel.sourceEntityId === entity.id)
        .map(rel => ({
          name: rel.name,
          type: rel.type,
          target_entity: entities.find(e => e.id === rel.targetEntityId)?.name.toLowerCase().replace(/\s+/g, '_') || '',
          foreign_key: rel.foreignKey,
          back_populates: rel.backPopulates,
          cascade: rel.cascade ? ['all'] : []
        }))
    }));

    return {
      ...domainConfig,
      entities: backendEntities
    };
  }
  
  // Helper method to convert backend data to frontend format
  convertToFrontendFormat(backendConfig: DomainConfig): {
    domainConfig: DomainConfig;
    entities: Entity[];
    relationships: Relationship[];
  } {
    if (!backendConfig.entities) {
      return {
        domainConfig: backendConfig,
        entities: [],
        relationships: []
      };
    }

    const entities: Entity[] = backendConfig.entities.map((entity, index) => ({
      id: `entity_${index}`,
      name: entity.title || entity.name,
      description: entity.description,
      type: 'core' as const,
      fields: entity.fields?.map((field, fieldIndex) => ({
        id: `field_${index}_${fieldIndex}`,
        name: field.name,
        title: field.title || field.name,
        type: field.type as any,
        required: field.required,
        defaultValue: field.default_value,
        validation: field.validation ? {
          min_length: field.validation.min_length,
          max_length: field.validation.max_length,
          pattern: field.validation.pattern,
          min_value: field.validation.min_value,
          max_value: field.validation.max_value,
          choices: field.validation.choices,
          custom_validator: field.validation.custom_validator
        } : undefined,
        uiConfig: field.ui_config ? {
          widget: field.ui_config.widget,
          placeholder: field.ui_config.placeholder,
          help_text: field.ui_config.help_text,
          grid_column: field.ui_config.grid_column,
          hide_in_list: field.ui_config.hide_in_list,
          hide_in_form: field.ui_config.hide_in_form
        } : undefined
      })) || []
    }));

    const relationships: Relationship[] = [];
    backendConfig.entities.forEach((entity, entityIndex) => {
      entity.relationships?.forEach((rel, relIndex) => {
        const sourceEntity = entities[entityIndex];
        const targetEntity = entities.find(e => 
          e.name.toLowerCase().replace(/\s+/g, '_') === rel.target_entity
        );
        
        if (sourceEntity && targetEntity) {
          relationships.push({
            id: `rel_${entityIndex}_${relIndex}`,
            name: rel.name,
            type: rel.type as any,
            sourceEntityId: sourceEntity.id,
            targetEntityId: targetEntity.id,
            foreignKey: rel.foreign_key,
            backPopulates: rel.back_populates,
            cascade: rel.cascade?.includes('all') || false
          });
        }
      });
    });

    return {
      domainConfig: {
        ...backendConfig,
        entities: undefined // Remove entities from domain config as we handle them separately
      },
      entities,
      relationships
    };
  }
}

export const templateApi = new TemplateApiService();
export default templateApi;