import { DomainConfig, ValidationResult, ValidationError } from '../types/template';

// Helper function to get API base URL
function getApiBaseUrl(): string {
  // Try to get from environment or use default
  if (typeof window !== 'undefined' && (window as any).__ENV__?.REACT_APP_API_URL) {
    return (window as any).__ENV__.REACT_APP_API_URL;
  }
  return 'http://localhost:8000';
}

/**
 * Validate a domain configuration against the template system rules
 */
export async function validateDomainConfig(config: DomainConfig): Promise<ValidationResult> {
  try {
    const API_BASE_URL = getApiBaseUrl();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add auth header if available
    const authHeader = getAuthHeader();
    if (authHeader) {
      headers.Authorization = authHeader;
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/templates/validate`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ config }),
    });

    if (!response.ok) {
      // If auth is required but not provided, fall back to client-side validation
      if (response.status === 401 || response.status === 403) {
        console.warn('API authentication required, falling back to client-side validation');
        return validateDomainConfigClientSide(config);
      }
      throw new Error(`Validation request failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Domain config validation error:', error);
    // Fallback to client-side validation
    return validateDomainConfigClientSide(config);
  }
}

/**
 * Get auth header if available
 */
function getAuthHeader(): string | null {
  // In a real app, get from localStorage or context
  // For demo purposes, return null to use client-side validation
  return null;
}

/**
 * Client-side validation fallback
 */
function validateDomainConfigClientSide(config: DomainConfig): ValidationResult {
  const errors: ValidationError[] = [];

  // Required field validation
  if (!config.name || config.name.trim().length === 0) {
    errors.push({
      field: 'name',
      message: 'Domain name is required',
      code: 'required'
    });
  }

  if (!config.title || config.title.trim().length === 0) {
    errors.push({
      field: 'title',
      message: 'Domain title is required',
      code: 'required'
    });
  }

  // Name format validation
  if (config.name && !/^[a-z][a-z0-9_]*$/.test(config.name)) {
    errors.push({
      field: 'name',
      message: 'Domain name must start with a letter and contain only lowercase letters, numbers, and underscores',
      code: 'invalid_format'
    });
  }

  // Length validation
  if (config.name && config.name.length > 50) {
    errors.push({
      field: 'name',
      message: 'Domain name cannot exceed 50 characters',
      code: 'max_length'
    });
  }

  if (config.title && config.title.length > 100) {
    errors.push({
      field: 'title',
      message: 'Domain title cannot exceed 100 characters',
      code: 'max_length'
    });
  }

  if (config.description && config.description.length > 500) {
    errors.push({
      field: 'description',
      message: 'Domain description cannot exceed 500 characters',
      code: 'max_length'
    });
  }

  // Version format validation
  if (config.version && !/^\d+\.\d+\.\d+$/.test(config.version)) {
    errors.push({
      field: 'version',
      message: 'Version must follow semantic versioning format (e.g., 1.0.0)',
      code: 'invalid_format'
    });
  }

  // Domain type validation
  const validDomainTypes = [
    'task_management', 'e_commerce', 'crm', 'healthcare', 
    'real_estate', 'education', 'finance', 'custom'
  ];
  
  if (config.domain_type && !validDomainTypes.includes(config.domain_type)) {
    errors.push({
      field: 'domain_type',
      message: 'Invalid domain type selected',
      code: 'invalid_choice'
    });
  }

  // Color scheme validation
  const validColorSchemes = ['blue', 'green', 'purple', 'red', 'orange', 'pink', 'gray', 'dark'];
  if (config.color_scheme && !validColorSchemes.includes(config.color_scheme)) {
    errors.push({
      field: 'color_scheme',
      message: 'Invalid color scheme selected',
      code: 'invalid_choice'
    });
  }

  // Theme validation
  const validThemes = ['default', 'modern', 'minimal', 'dark', 'colorful'];
  if (config.theme && !validThemes.includes(config.theme)) {
    errors.push({
      field: 'theme',
      message: 'Invalid theme selected',
      code: 'invalid_choice'
    });
  }

  return {
    is_valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  };
}

/**
 * Validate entity configuration
 */
export function validateEntityConfig(entityConfig: any): ValidationResult {
  const errors: ValidationError[] = [];

  if (!entityConfig.name || entityConfig.name.trim().length === 0) {
    errors.push({
      field: 'entity.name',
      message: 'Entity name is required',
      code: 'required'
    });
  }

  if (!entityConfig.title || entityConfig.title.trim().length === 0) {
    errors.push({
      field: 'entity.title',
      message: 'Entity title is required',
      code: 'required'
    });
  }

  if (entityConfig.name && !/^[a-z][a-z0-9_]*$/.test(entityConfig.name)) {
    errors.push({
      field: 'entity.name',
      message: 'Entity name must start with a letter and contain only lowercase letters, numbers, and underscores',
      code: 'invalid_format'
    });
  }

  if (!entityConfig.fields || !Array.isArray(entityConfig.fields) || entityConfig.fields.length === 0) {
    errors.push({
      field: 'entity.fields',
      message: 'Entity must have at least one field',
      code: 'required'
    });
  }

  return {
    is_valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  };
}

/**
 * Validate field configuration
 */
export function validateFieldConfig(fieldConfig: any): ValidationResult {
  const errors: ValidationError[] = [];

  if (!fieldConfig.name || fieldConfig.name.trim().length === 0) {
    errors.push({
      field: 'field.name',
      message: 'Field name is required',
      code: 'required'
    });
  }

  if (!fieldConfig.title || fieldConfig.title.trim().length === 0) {
    errors.push({
      field: 'field.title',
      message: 'Field title is required',
      code: 'required'
    });
  }

  if (!fieldConfig.type || fieldConfig.type.trim().length === 0) {
    errors.push({
      field: 'field.type',
      message: 'Field type is required',
      code: 'required'
    });
  }

  const validFieldTypes = [
    'string', 'text', 'integer', 'float', 'decimal', 'boolean',
    'date', 'datetime', 'time', 'email', 'url', 'uuid',
    'json', 'file', 'image', 'enum', 'array'
  ];

  if (fieldConfig.type && !validFieldTypes.includes(fieldConfig.type)) {
    errors.push({
      field: 'field.type',
      message: 'Invalid field type selected',
      code: 'invalid_choice'
    });
  }

  if (fieldConfig.name && !/^[a-z][a-z0-9_]*$/.test(fieldConfig.name)) {
    errors.push({
      field: 'field.name',
      message: 'Field name must start with a letter and contain only lowercase letters, numbers, and underscores',
      code: 'invalid_format'
    });
  }

  return {
    is_valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  };
}

/**
 * Validate complete domain configuration including entities
 */
export function validateCompleteConfig(config: DomainConfig): ValidationResult {
  const errors: ValidationError[] = [];

  // Validate basic domain config
  const domainValidation = validateDomainConfigClientSide(config);
  if (domainValidation.errors) {
    errors.push(...domainValidation.errors);
  }

  // Validate entities if present
  if (config.entities) {
    config.entities.forEach((entity, index) => {
      const entityValidation = validateEntityConfig(entity);
      if (entityValidation.errors) {
        entityValidation.errors.forEach(error => {
          errors.push({
            ...error,
            field: `entities[${index}].${error.field}`,
          });
        });
      }

      // Validate fields
      if (entity.fields) {
        entity.fields.forEach((field, fieldIndex) => {
          const fieldValidation = validateFieldConfig(field);
          if (fieldValidation.errors) {
            fieldValidation.errors.forEach(error => {
              errors.push({
                ...error,
                field: `entities[${index}].fields[${fieldIndex}].${error.field}`,
              });
            });
          }
        });
      }
    });
  }

  return {
    is_valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined
  };
}

/**
 * Check if domain name is available
 */
export async function checkDomainNameAvailability(name: string): Promise<boolean> {
  try {
    const API_BASE_URL = getApiBaseUrl();
    const response = await fetch(`${API_BASE_URL}/api/v1/templates/check-name/${encodeURIComponent(name)}`);
    if (!response.ok) {
      return false;
    }
    const result = await response.json();
    return result.available;
  } catch (error) {
    console.error('Domain name availability check error:', error);
    return false;
  }
}

/**
 * Get validation suggestions for improving configuration
 */
export function getValidationSuggestions(config: DomainConfig): string[] {
  const suggestions: string[] = [];

  if (!config.description || config.description.length < 20) {
    suggestions.push('Consider adding a more detailed description to help users understand the purpose of this domain.');
  }

  if (!config.logo || config.logo.length === 0) {
    suggestions.push('Adding a logo or icon will make your domain more visually appealing.');
  }

  if (!config.entities || config.entities.length === 0) {
    suggestions.push('Add at least one entity to define the data structure for your domain.');
  }

  if (config.entities && config.entities.length < 2) {
    suggestions.push('Consider adding more entities to create a richer domain model.');
  }

  if (config.version === '1.0.0' && config.entities && config.entities.length > 0) {
    suggestions.push('Since you have entities defined, you might want to increment the version number.');
  }

  return suggestions;
}