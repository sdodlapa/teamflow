/**
 * Template Creation UI - Day 10 Implementation
 * Multi-step wizard for creating new domain templates
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  ArrowRight, 
  Check, 
  Plus, 
  Save,
  AlertCircle,
  Database,
  Trash2,
  Zap
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingComponents';

// Interfaces for template creation
interface DomainInfo {
  name: string;
  title: string;
  description: string;
  type: string;
  version: string;
  logo: string;
  color_scheme: string;
  author: string;
  tags: string[];
}

interface EntityField {
  name: string;
  type: string;
  nullable: boolean;
  description: string;
  max_length?: number;
  choices?: string[];
}

interface EntityRelationship {
  name: string;
  target_entity: string;
  relationship_type: string;
  foreign_key?: string;
}

interface EntityDefinition {
  name: string;
  table_name: string;
  description: string;
  fields: EntityField[];
  relationships: EntityRelationship[];
}

interface TemplateConfig {
  domain: DomainInfo;
  entities: EntityDefinition[];
  features: Record<string, boolean>;
}

const FIELD_TYPES = [
  { value: 'string', label: 'String', icon: '📝' },
  { value: 'text', label: 'Text', icon: '📄' },
  { value: 'integer', label: 'Integer', icon: '#️⃣' },
  { value: 'decimal', label: 'Decimal', icon: '💰' },
  { value: 'boolean', label: 'Boolean', icon: '✅' },
  { value: 'date', label: 'Date', icon: '📅' },
  { value: 'datetime', label: 'DateTime', icon: '🕐' },
  { value: 'enum', label: 'Choice', icon: '🎯' }
];

const DOMAIN_TYPES = [
  'business', 'healthcare', 'e-commerce', 'education', 
  'finance', 'real-estate', 'logistics', 'other'
];

const COLOR_SCHEMES = [
  { value: 'blue', label: 'Blue', color: '#3B82F6' },
  { value: 'green', label: 'Green', color: '#10B981' },
  { value: 'purple', label: 'Purple', color: '#8B5CF6' },
  { value: 'red', label: 'Red', color: '#EF4444' },
  { value: 'orange', label: 'Orange', color: '#F59E0B' },
  { value: 'pink', label: 'Pink', color: '#EC4899' }
];

const EMOJI_OPTIONS = [
  '🚀', '📊', '🏢', '💼', '🎯', '⚡', '🔧', '📱', 
  '🌟', '🎨', '📈', '🔥', '💡', '🎪', '🏆', '🎭'
];

const TemplateCreation: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  
  // Template configuration state
  const [config, setConfig] = useState<TemplateConfig>({
    domain: {
      name: '',
      title: '',
      description: '',
      type: 'business',
      version: '1.0.0',
      logo: '🚀',
      color_scheme: 'blue',
      author: 'Custom Template',
      tags: []
    },
    entities: [],
    features: {
      file_management: true,
      real_time_notifications: true,
      workflow_automation: false,
      advanced_search: true,
      reporting_analytics: false,
      webhook_integration: false,
      audit_logging: true,
      multi_tenant: true
    }
  });

  const steps = [
    { id: 0, title: 'Domain Info', description: 'Basic domain configuration' },
    { id: 1, title: 'Entities', description: 'Define data entities' },
    { id: 2, title: 'Features', description: 'Select features' },
    { id: 3, title: 'Preview', description: 'Review and create' }
  ];

  // Validation
  const validateStep = (stepId: number): boolean => {
    switch (stepId) {
      case 0: // Domain Info
        return !!(config.domain.name && config.domain.title && config.domain.description);
      case 1: // Entities
        return config.entities.length > 0 && config.entities.every(e => 
          e.name && e.fields.length > 0 && e.fields.every(f => f.name && f.type)
        );
      case 2: // Features
        return true; // Features are optional
      case 3: // Preview
        return true;
      default:
        return false;
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1 && validateStep(currentStep)) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const updateDomainInfo = (field: keyof DomainInfo, value: any) => {
    setConfig(prev => ({
      ...prev,
      domain: {
        ...prev.domain,
        [field]: value
      }
    }));
  };

  const addEntity = () => {
    const newEntity: EntityDefinition = {
      name: '',
      table_name: '',
      description: '',
      fields: [
        { name: 'id', type: 'integer', nullable: false, description: 'Primary key' }
      ],
      relationships: []
    };
    setConfig(prev => ({
      ...prev,
      entities: [...prev.entities, newEntity]
    }));
  };

  const updateEntity = (index: number, field: keyof EntityDefinition, value: any) => {
    setConfig(prev => ({
      ...prev,
      entities: prev.entities.map((entity, i) => 
        i === index ? { ...entity, [field]: value } : entity
      )
    }));
  };

  const removeEntity = (index: number) => {
    setConfig(prev => ({
      ...prev,
      entities: prev.entities.filter((_, i) => i !== index)
    }));
  };

  const addField = (entityIndex: number) => {
    const newField: EntityField = {
      name: '',
      type: 'string',
      nullable: true,
      description: ''
    };
    
    setConfig(prev => ({
      ...prev,
      entities: prev.entities.map((entity, i) => 
        i === entityIndex 
          ? { ...entity, fields: [...entity.fields, newField] }
          : entity
      )
    }));
  };

  const updateField = (entityIndex: number, fieldIndex: number, field: keyof EntityField, value: any) => {
    setConfig(prev => ({
      ...prev,
      entities: prev.entities.map((entity, i) => 
        i === entityIndex
          ? {
              ...entity,
              fields: entity.fields.map((f, j) => 
                j === fieldIndex ? { ...f, [field]: value } : f
              )
            }
          : entity
      )
    }));
  };

  const removeField = (entityIndex: number, fieldIndex: number) => {
    setConfig(prev => ({
      ...prev,
      entities: prev.entities.map((entity, i) => 
        i === entityIndex
          ? { ...entity, fields: entity.fields.filter((_, j) => j !== fieldIndex) }
          : entity
      )
    }));
  };

  const saveTemplate = async () => {
    try {
      setIsSubmitting(true);
      setError(null);

      // Create template payload
      const templatePayload = {
        name: config.domain.name,
        title: config.domain.title,
        description: config.domain.description,
        domain_type: config.domain.type,
        version: config.domain.version,
        logo: config.domain.logo,
        color_scheme: config.domain.color_scheme,
        entities: config.entities.map(entity => ({
          name: entity.name,
          table_name: entity.table_name,
          description: entity.description,
          fields: entity.fields,
          relationships: entity.relationships
        })),
        features: config.features,
        tags: config.domain.tags
      };

      // Call the API to create the template
      const response = await fetch('/api/v1/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(templatePayload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create template');
      }

      const result = await response.json();
      
      if (result.validation_errors && result.validation_errors.length > 0) {
        throw new Error(`Validation failed: ${result.validation_errors.join(', ')}`);
      }

      setSubmitSuccess(true);
      
      // Navigate to template details after short delay
      setTimeout(() => {
        navigate(`/templates`);
      }, 2000);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create template');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-between mb-8">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
              index < currentStep
                ? 'bg-green-500 text-white'
                : index === currentStep
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-500'
            }`}
          >
            {index < currentStep ? <Check className="h-6 w-6" /> : index + 1}
          </div>
          <div className="ml-3 flex-1">
            <h3 className={`text-sm font-medium ${
              index <= currentStep ? 'text-gray-900' : 'text-gray-500'
            }`}>
              {step.title}
            </h3>
            <p className="text-xs text-gray-500">{step.description}</p>
          </div>
          {index < steps.length - 1 && (
            <div className={`w-12 h-0.5 mx-4 ${
              index < currentStep ? 'bg-green-500' : 'bg-gray-200'
            }`} />
          )}
        </div>
      ))}
    </div>
  );

  const renderDomainInfoStep = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Domain Information</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Domain Name *
          </label>
          <input
            type="text"
            value={config.domain.name}
            onChange={(e) => updateDomainInfo('name', e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '_'))}
            placeholder="my_awesome_domain"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
          <p className="text-xs text-gray-500 mt-1">Lowercase letters, numbers, and underscores only</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Display Title *
          </label>
          <input
            type="text"
            value={config.domain.title}
            onChange={(e) => updateDomainInfo('title', e.target.value)}
            placeholder="My Awesome Domain"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <textarea
            value={config.domain.description}
            onChange={(e) => updateDomainInfo('description', e.target.value)}
            placeholder="Describe what this domain template is for..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Domain Type
          </label>
          <select
            value={config.domain.type}
            onChange={(e) => updateDomainInfo('type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {DOMAIN_TYPES.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Version
          </label>
          <input
            type="text"
            value={config.domain.version}
            onChange={(e) => updateDomainInfo('version', e.target.value)}
            placeholder="1.0.0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Logo
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {EMOJI_OPTIONS.map(emoji => (
              <button
                key={emoji}
                type="button"
                onClick={() => updateDomainInfo('logo', emoji)}
                className={`w-12 h-12 text-xl border-2 rounded-md hover:bg-gray-50 ${
                  config.domain.logo === emoji ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
              >
                {emoji}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Color Scheme
          </label>
          <div className="flex flex-wrap gap-2">
            {COLOR_SCHEMES.map(scheme => (
              <button
                key={scheme.value}
                type="button"
                onClick={() => updateDomainInfo('color_scheme', scheme.value)}
                className={`flex items-center px-3 py-2 border-2 rounded-md hover:bg-gray-50 ${
                  config.domain.color_scheme === scheme.value 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200'
                }`}
              >
                <div
                  className="w-4 h-4 rounded-full mr-2"
                  style={{ backgroundColor: scheme.color }}
                />
                {scheme.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderEntitiesStep = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Domain Entities</h2>
        <button
          type="button"
          onClick={addEntity}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Entity
        </button>
      </div>

      {config.entities.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
          <Database className="h-16 w-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No entities yet</h3>
          <p className="text-gray-600 mb-4">Add your first entity to get started</p>
          <button
            type="button"
            onClick={addEntity}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Add Entity
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {config.entities.map((entity, entityIndex) => (
            <div key={entityIndex} className="bg-gray-50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Entity {entityIndex + 1}</h3>
                <button
                  type="button"
                  onClick={() => removeEntity(entityIndex)}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Entity Name *
                  </label>
                  <input
                    type="text"
                    value={entity.name}
                    onChange={(e) => {
                      const name = e.target.value;
                      updateEntity(entityIndex, 'name', name);
                      updateEntity(entityIndex, 'table_name', name.toLowerCase().replace(/[^a-z0-9]/g, '_'));
                    }}
                    placeholder="Product"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Table Name
                  </label>
                  <input
                    type="text"
                    value={entity.table_name}
                    onChange={(e) => updateEntity(entityIndex, 'table_name', e.target.value)}
                    placeholder="products"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <input
                    type="text"
                    value={entity.description}
                    onChange={(e) => updateEntity(entityIndex, 'description', e.target.value)}
                    placeholder="Describe this entity..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-gray-900">Fields ({entity.fields.length})</h4>
                  <button
                    type="button"
                    onClick={() => addField(entityIndex)}
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add Field
                  </button>
                </div>

                {entity.fields.map((field, fieldIndex) => (
                  <div key={fieldIndex} className="flex items-center space-x-2 bg-white p-3 rounded border">
                    <div className="flex-1">
                      <input
                        type="text"
                        value={field.name}
                        onChange={(e) => updateField(entityIndex, fieldIndex, 'name', e.target.value)}
                        placeholder="field_name"
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                        disabled={fieldIndex === 0} // Don't allow editing the ID field
                      />
                    </div>
                    <div>
                      <select
                        value={field.type}
                        onChange={(e) => updateField(entityIndex, fieldIndex, 'type', e.target.value)}
                        className="px-2 py-1 text-sm border border-gray-300 rounded"
                        disabled={fieldIndex === 0} // Don't allow editing the ID field type
                      >
                        {FIELD_TYPES.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.icon} {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={!field.nullable}
                        onChange={(e) => updateField(entityIndex, fieldIndex, 'nullable', !e.target.checked)}
                        className="mr-1"
                        disabled={fieldIndex === 0} // ID field must be required
                      />
                      <span className="text-sm text-gray-600">Required</span>
                    </div>
                    {fieldIndex > 0 && (
                      <button
                        type="button"
                        onClick={() => removeField(entityIndex, fieldIndex)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderFeaturesStep = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Template Features</h2>
      <p className="text-gray-600">Select which features to enable for this template</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(config.features).map(([feature, enabled]) => (
          <div key={feature} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">
                {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </h3>
              <p className="text-sm text-gray-500">
                {getFeatureDescription(feature)}
              </p>
            </div>
            <div className="ml-4">
              <input
                type="checkbox"
                checked={enabled}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  features: { ...prev.features, [feature]: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const getFeatureDescription = (feature: string): string => {
    const descriptions: Record<string, string> = {
      file_management: 'Upload and manage files within entities',
      real_time_notifications: 'Real-time updates and notifications',
      workflow_automation: 'Automated workflows and triggers',
      advanced_search: 'Advanced search and filtering capabilities',
      reporting_analytics: 'Analytics and reporting dashboard',
      webhook_integration: 'External webhook integrations',
      audit_logging: 'Track all changes and actions',
      multi_tenant: 'Support for multiple organizations'
    };
    return descriptions[feature] || 'Feature description not available';
  };

  const renderPreviewStep = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Template Preview</h2>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Domain Information</h3>
            <div className="space-y-2 text-sm">
              <div><strong>Name:</strong> {config.domain.name}</div>
              <div><strong>Title:</strong> {config.domain.title}</div>
              <div><strong>Type:</strong> {config.domain.type}</div>
              <div><strong>Version:</strong> {config.domain.version}</div>
              <div className="flex items-center">
                <strong>Logo:</strong> 
                <span className="ml-2 text-lg">{config.domain.logo}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Statistics</h3>
            <div className="space-y-2 text-sm">
              <div><strong>Entities:</strong> {config.entities.length}</div>
              <div><strong>Total Fields:</strong> {config.entities.reduce((sum, e) => sum + e.fields.length, 0)}</div>
              <div><strong>Features Enabled:</strong> {Object.values(config.features).filter(Boolean).length}</div>
            </div>
          </div>
        </div>
        
        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
          <p className="text-gray-700">{config.domain.description}</p>
        </div>

        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 mb-2">Entities ({config.entities.length})</h3>
          <div className="space-y-3">
            {config.entities.map((entity, index) => (
              <div key={index} className="bg-white p-4 rounded border">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{entity.name}</h4>
                  <span className="text-sm text-gray-500">{entity.fields.length} fields</span>
                </div>
                {entity.description && (
                  <p className="text-sm text-gray-600 mb-2">{entity.description}</p>
                )}
                <div className="text-sm text-gray-500">
                  Fields: {entity.fields.map(f => f.name).join(', ')}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-900 mb-2">Enabled Features</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(config.features)
              .filter(([_, enabled]) => enabled)
              .map(([feature, _]) => (
                <span
                  key={feature}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                >
                  {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
              ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/templates')}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Create Template</h1>
              <p className="text-gray-600">Build a custom domain configuration</p>
            </div>
          </div>
        </div>

        {/* Step Indicator */}
        {renderStepIndicator()}

        {/* Success/Error Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {submitSuccess && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <Check className="h-5 w-5 text-green-600 mr-2" />
              <p className="text-green-700">Template created successfully! Redirecting...</p>
            </div>
          </div>
        )}

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          {currentStep === 0 && renderDomainInfoStep()}
          {currentStep === 1 && renderEntitiesStep()}
          {currentStep === 2 && renderFeaturesStep()}
          {currentStep === 3 && renderPreviewStep()}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className={`flex items-center px-4 py-2 rounded-md font-medium ${
              currentStep === 0
                ? 'text-gray-400 cursor-not-allowed'
                : 'text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous
          </button>

          <div className="flex space-x-3">
            {currentStep < steps.length - 1 ? (
              <button
                onClick={nextStep}
                disabled={!validateStep(currentStep)}
                className={`flex items-center px-6 py-2 rounded-md font-medium ${
                  validateStep(currentStep)
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }`}
              >
                Next
                <ArrowRight className="h-4 w-4 ml-2" />
              </button>
            ) : (
              <button
                onClick={saveTemplate}
                disabled={isSubmitting || !validateStep(currentStep)}
                className={`flex items-center px-6 py-2 rounded-md font-medium ${
                  isSubmitting || !validateStep(currentStep)
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : submitSuccess
                    ? 'bg-green-600 text-white'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {isSubmitting ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span className="ml-2">Creating...</span>
                  </>
                ) : submitSuccess ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Template Created!
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Create Template
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Day 10 Progress Footer */}
      <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border-t border-orange-200 mt-12">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <div className="flex items-start space-x-3">
            <Zap className="h-6 w-6 text-orange-600 mt-1" />
            <div>
              <h4 className="text-lg font-semibold text-orange-900">
                🛠️ Day 10: Template Creation UI in Progress
              </h4>
              <p className="text-orange-700">
                Multi-step wizard for creating domain templates - Domain Info, Entities, Features, and Preview steps implemented.
                Backend integration pending.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateCreation;