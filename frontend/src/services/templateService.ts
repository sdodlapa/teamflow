import { DomainConfig, EntityConfig, FieldConfig } from '../types/template';

const API_BASE_URL = 'http://localhost:8000';

export interface TemplateService {
  validateConfig: (config: DomainConfig) => Promise<boolean>;
  generateCode: (config: DomainConfig) => Promise<void>;
  saveTemplate: (config: DomainConfig) => Promise<void>;
  loadTemplate: (name: string) => Promise<DomainConfig>;
  listTemplates: () => Promise<string[]>;
}

export const templateService: TemplateService = {
  async validateConfig(config: DomainConfig): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      const result = await response.json();
      return result.is_valid;
    } catch (error) {
      console.error('Validation error:', error);
      return false;
    }
  },

  async generateCode(config: DomainConfig): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error('Code generation failed');
      }
    } catch (error) {
      console.error('Code generation error:', error);
      throw error;
    }
  },

  async saveTemplate(config: DomainConfig): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error('Template save failed');
      }
    } catch (error) {
      console.error('Template save error:', error);
      throw error;
    }
  },

  async loadTemplate(name: string): Promise<DomainConfig> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/${name}`);
      if (!response.ok) {
        throw new Error('Template load failed');
      }
      return await response.json();
    } catch (error) {
      console.error('Template load error:', error);
      throw error;
    }
  },

  async listTemplates(): Promise<string[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates`);
      if (!response.ok) {
        throw new Error('Template list failed');
      }
      const result = await response.json();
      return result.templates.map((t: any) => t.name);
    } catch (error) {
      console.error('Template list error:', error);
      return [];
    }
  },
};

// Helper functions for template creation
export const createDefaultEntityConfig = (name: string): EntityConfig => ({
  name: name.toLowerCase().replace(/\s+/g, '_'),
  title: name,
  description: `${name} entity configuration`,
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'uuid',
      required: true,
    },
    {
      name: 'name',
      title: 'Name',
      type: 'string',
      required: true,
    },
    {
      name: 'created_at',
      title: 'Created At',
      type: 'datetime',
      required: true,
    },
  ],
  relationships: [],
  permissions: [
    {
      role: 'admin',
      permissions: ['create', 'read', 'update', 'delete', 'list'],
    },
    {
      role: 'user',
      permissions: ['read', 'list'],
    },
  ],
});

export const createDefaultFieldConfig = (name: string, type: string): FieldConfig => ({
  name: name.toLowerCase().replace(/\s+/g, '_'),
  title: name,
  type: type as any,
  required: false,
});

export const createDefaultDomainConfig = (name: string): DomainConfig => ({
  name: name.toLowerCase().replace(/\s+/g, '_'),
  title: name,
  description: `${name} domain configuration`,
  domain_type: 'custom',
  version: '1.0.0',
  logo: '🏢',
  color_scheme: 'blue',
  theme: 'default',
  entities: [],
  features: [],
});

// Domain templates for common use cases
export const domainTemplates = {
  e_commerce: {
    name: 'e_commerce',
    title: 'E-Commerce Platform',
    description: 'Complete e-commerce solution with products, orders, and customers',
    domain_type: 'e_commerce',
    entities: ['Product', 'Order', 'Customer', 'Category'],
  },
  task_management: {
    name: 'task_management',
    title: 'Task Management System',
    description: 'Project and task management with teams and assignments',
    domain_type: 'task_management',
    entities: ['Project', 'Task', 'User', 'Team'],
  },
  crm: {
    name: 'crm',
    title: 'Customer Relationship Management',
    description: 'Manage customer relationships, leads, and sales pipeline',
    domain_type: 'crm',
    entities: ['Customer', 'Lead', 'Opportunity', 'Contact'],
  },
};