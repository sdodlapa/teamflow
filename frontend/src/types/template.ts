// Template system type definitions
export interface DomainConfig {
  name: string;
  title: string;
  description?: string;
  domain_type: string;
  version: string;
  logo?: string;
  color_scheme?: string;
  theme?: string;
  entities?: EntityConfig[];
  features?: FeatureConfig[];
  metadata?: Record<string, any>;
}

// Entity management types for the template builder
export interface Entity {
  id: string;
  name: string;
  description?: string;
  type: 'core' | 'lookup';
  tableName?: string;
  primaryKey?: string;
  displayField?: string;
  timestamps?: boolean;
  fields: Field[];
}

export interface Field {
  id: string;
  name: string;
  title: string;
  type: FieldType;
  required?: boolean;
  unique?: boolean;
  defaultValue?: any;
  validation?: ValidationConfig;
  uiConfig?: FieldUIConfig;
}

export interface Relationship {
  id: string;
  name: string;
  type: RelationshipType;
  sourceEntityId: string;
  targetEntityId: string;
  foreignKey?: string;
  backPopulates?: string;
  cascade?: boolean;
  description?: string;
}

export interface EntityConfig {
  name: string;
  title: string;
  description?: string;
  fields: FieldConfig[];
  relationships?: RelationshipConfig[];
  permissions?: PermissionConfig[];
  ui_config?: EntityUIConfig;
}

export interface FieldConfig {
  name: string;
  title: string;
  type: FieldType;
  required?: boolean;
  default_value?: any;
  validation?: ValidationConfig;
  ui_config?: FieldUIConfig;
}

export interface RelationshipConfig {
  name: string;
  type: RelationshipType;
  target_entity: string;
  foreign_key?: string;
  back_populates?: string;
  cascade?: string[];
}

export interface PermissionConfig {
  role: string;
  permissions: Permission[];
}

export interface FeatureConfig {
  name: string;
  enabled: boolean;
  config?: Record<string, any>;
}

export interface ValidationConfig {
  min_length?: number;
  max_length?: number;
  pattern?: string;
  min_value?: number;
  max_value?: number;
  choices?: string[];
  custom_validator?: string;
}

export interface EntityUIConfig {
  icon?: string;
  color?: string;
  list_display?: string[];
  search_fields?: string[];
  filter_fields?: string[];
  form_layout?: FormLayout[];
}

export interface FieldUIConfig {
  widget?: WidgetType;
  placeholder?: string;
  help_text?: string;
  grid_column?: number;
  hide_in_list?: boolean;
  hide_in_form?: boolean;
}

export interface FormLayout {
  section: string;
  fields: string[];
  columns?: number;
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  errors?: ValidationError[];
  warnings?: ValidationError[];
}

export interface GenerationRequest {
  domain_config: DomainConfig;
  generate_backend: boolean;
  generate_frontend: boolean;
  target_directory?: string;
}

export interface GenerationResult {
  success: boolean;
  files_generated: GeneratedFile[];
  errors?: string[];
  warnings?: string[];
}

export interface GeneratedFile {
  path: string;
  type: 'model' | 'schema' | 'api' | 'component' | 'config';
  size: number;
  checksum: string;
}

export interface TemplatePreview {
  domain_config: DomainConfig;
  preview_data: {
    entities: EntityPreview[];
    api_endpoints: string[];
    ui_components: string[];
  };
}

export interface EntityPreview {
  name: string;
  title: string;
  field_count: number;
  relationship_count: number;
  sample_data: Record<string, any>[];
}

// Enums
export type FieldType = 
  | 'string'
  | 'text'
  | 'integer'
  | 'float'
  | 'decimal'
  | 'boolean'
  | 'date'
  | 'datetime'
  | 'time'
  | 'email'
  | 'url'
  | 'uuid'
  | 'json'
  | 'file'
  | 'image'
  | 'enum'
  | 'array';

export type RelationshipType =
  | 'one_to_one'
  | 'one_to_many'
  | 'many_to_one'
  | 'many_to_many';

export type Permission =
  | 'create'
  | 'read'
  | 'update'
  | 'delete'
  | 'list'
  | 'detail';

export type WidgetType =
  | 'text_input'
  | 'textarea'
  | 'select'
  | 'multi_select'
  | 'checkbox'
  | 'radio'
  | 'date_picker'
  | 'datetime_picker'
  | 'file_upload'
  | 'image_upload'
  | 'rich_text'
  | 'color_picker'
  | 'number_input'
  | 'slider'
  | 'toggle';

export type DomainType =
  | 'task_management'
  | 'e_commerce'
  | 'crm'
  | 'healthcare'
  | 'real_estate'
  | 'education'
  | 'finance'
  | 'custom';

export type ColorScheme =
  | 'blue'
  | 'green'
  | 'purple'
  | 'red'
  | 'orange'
  | 'pink'
  | 'gray'
  | 'dark';

export type Theme =
  | 'default'
  | 'modern'
  | 'minimal'
  | 'dark'
  | 'colorful';

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: ValidationError[];
}

export interface TemplateListResponse {
  templates: TemplateMetadata[];
  total: number;
  page: number;
  per_page: number;
}

export interface TemplateMetadata {
  id: string;
  name: string;
  title: string;
  domain_type: DomainType;
  version: string;
  author: string;
  created_at: string;
  updated_at: string;
  downloads: number;
  rating: number;
  tags: string[];
}

export interface CodeGenerationProgress {
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  total_steps: number;
  files_generated: number;
  errors: string[];
}