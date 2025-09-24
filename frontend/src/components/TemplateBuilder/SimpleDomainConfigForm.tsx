import React, { useState } from 'react';

interface SimpleDomainConfig {
  name: string;
  title: string;
  description: string;
  domain_type: string;
  version: string;
  logo: string;
  color_scheme: string;
  theme: string;
}

interface SimpleDomainConfigFormProps {
  initialConfig?: Partial<SimpleDomainConfig>;
  onConfigChange: (config: SimpleDomainConfig) => void;
  onValidationChange: (isValid: boolean) => void;
}

const DOMAIN_TYPES = [
  { value: 'task_management', label: 'Task Management' },
  { value: 'e_commerce', label: 'E-Commerce' },
  { value: 'crm', label: 'Customer Relationship Management' },
  { value: 'healthcare', label: 'Healthcare Management' },
  { value: 'real_estate', label: 'Real Estate' },
  { value: 'education', label: 'Education Platform' },
  { value: 'finance', label: 'Financial Services' },
  { value: 'custom', label: 'Custom Domain' }
];

const COLOR_SCHEMES = [
  { value: 'blue', label: 'Blue', color: '#3B82F6' },
  { value: 'green', label: 'Green', color: '#10B981' },
  { value: 'purple', label: 'Purple', color: '#8B5CF6' },
  { value: 'red', label: 'Red', color: '#EF4444' },
  { value: 'orange', label: 'Orange', color: '#F97316' },
  { value: 'pink', label: 'Pink', color: '#EC4899' }
];

const LOGO_OPTIONS = [
  '🚀', '🏢', '💼', '🛒', '🏥', '🏠', '🎓', '💰', '📊', '⚡'
];

export const SimpleDomainConfigForm: React.FC<SimpleDomainConfigFormProps> = ({
  initialConfig,
  onConfigChange,
  onValidationChange
}) => {
  const [config, setConfig] = useState<SimpleDomainConfig>({
    name: '',
    title: '',
    description: '',
    domain_type: 'custom',
    version: '1.0.0',
    logo: '🏢',
    color_scheme: 'blue',
    theme: 'default',
    ...initialConfig
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateField = (field: keyof SimpleDomainConfig, value: string): string | null => {
    switch (field) {
      case 'name':
        if (!value.trim()) return 'Domain name is required';
        if (!/^[a-z][a-z0-9_]*$/.test(value)) return 'Must start with letter, lowercase, underscores only';
        if (value.length > 50) return 'Cannot exceed 50 characters';
        return null;
      case 'title':
        if (!value.trim()) return 'Domain title is required';
        if (value.length > 100) return 'Cannot exceed 100 characters';
        return null;
      case 'description':
        if (value.length > 500) return 'Cannot exceed 500 characters';
        return null;
      case 'version':
        if (!/^\d+\.\d+\.\d+$/.test(value)) return 'Must be in format x.y.z';
        return null;
      default:
        return null;
    }
  };

  const updateConfig = (field: keyof SimpleDomainConfig, value: string) => {
    const newConfig = { ...config, [field]: value };
    setConfig(newConfig);

    // Validate the field
    const error = validateField(field, value);
    const newErrors = { ...errors };
    if (error) {
      newErrors[field] = error;
    } else {
      delete newErrors[field];
    }
    setErrors(newErrors);

    // Check overall validity
    const isValid = Object.keys(newErrors).length === 0 && 
                   newConfig.name.trim() !== '' && 
                   newConfig.title.trim() !== '';
    
    onValidationChange(isValid);
    if (isValid) {
      onConfigChange(newConfig);
    }
  };

  const generateDomainName = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 50);
  };

  const handleTitleChange = (title: string) => {
    updateConfig('title', title);
    if (!config.name || config.name === generateDomainName(config.title)) {
      updateConfig('name', generateDomainName(title));
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Domain Configuration
        </h2>
        <p className="text-gray-600">
          Configure the basic information for your business domain template.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Information */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
            Basic Information
          </h3>

          {/* Domain Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
              Domain Title *
            </label>
            <input
              type="text"
              id="title"
              value={config.title}
              onChange={(e) => handleTitleChange(e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., E-Commerce Platform"
              maxLength={100}
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              The display name for your domain ({config.title.length}/100)
            </p>
          </div>

          {/* Domain Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Domain Name *
            </label>
            <input
              type="text"
              id="name"
              value={config.name}
              onChange={(e) => updateConfig('name', e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., e_commerce_platform"
              maxLength={50}
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Technical name (lowercase, underscores only) ({config.name.length}/50)
            </p>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              value={config.description}
              onChange={(e) => updateConfig('description', e.target.value)}
              rows={4}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Describe what this domain template is used for..."
              maxLength={500}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Optional detailed description ({config.description.length}/500)
            </p>
          </div>

          {/* Domain Type */}
          <div>
            <label htmlFor="domain_type" className="block text-sm font-medium text-gray-700 mb-1">
              Domain Type
            </label>
            <select
              id="domain_type"
              value={config.domain_type}
              onChange={(e) => updateConfig('domain_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {DOMAIN_TYPES.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-sm text-gray-500">
              Category that best describes your domain
            </p>
          </div>

          {/* Version */}
          <div>
            <label htmlFor="version" className="block text-sm font-medium text-gray-700 mb-1">
              Version
            </label>
            <input
              type="text"
              id="version"
              value={config.version}
              onChange={(e) => updateConfig('version', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.version ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="1.0.0"
            />
            {errors.version && (
              <p className="mt-1 text-sm text-red-600">{errors.version}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Semantic version (e.g., 1.0.0)
            </p>
          </div>
        </div>

        {/* Branding & UI */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
            Branding & UI
          </h3>

          {/* Logo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Logo/Icon
            </label>
            <div className="grid grid-cols-5 gap-2">
              {LOGO_OPTIONS.map(emoji => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => updateConfig('logo', emoji)}
                  className={`p-3 text-2xl border rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    config.logo === emoji ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                  }`}
                >
                  {emoji}
                </button>
              ))}
            </div>
            <div className="mt-2">
              <input
                type="text"
                value={config.logo}
                onChange={(e) => updateConfig('logo', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Or enter custom emoji/icon"
                maxLength={10}
              />
            </div>
          </div>

          {/* Color Scheme */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Color Scheme
            </label>
            <div className="grid grid-cols-3 gap-2">
              {COLOR_SCHEMES.map(scheme => (
                <button
                  key={scheme.value}
                  type="button"
                  onClick={() => updateConfig('color_scheme', scheme.value)}
                  className={`p-3 border rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    config.color_scheme === scheme.value ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: scheme.color }}
                    />
                    <span className="text-sm">{scheme.label}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Theme */}
          <div>
            <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-1">
              Theme
            </label>
            <select
              id="theme"
              value={config.theme}
              onChange={(e) => updateConfig('theme', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="default">Default</option>
              <option value="modern">Modern</option>
              <option value="minimal">Minimal</option>
              <option value="dark">Dark</option>
            </select>
          </div>

          {/* Preview */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Preview</h4>
            <div className="flex items-center space-x-3 p-3 bg-white rounded border">
              <span className="text-2xl">{config.logo}</span>
              <div>
                <h5 className="font-semibold text-gray-900">{config.title || 'Domain Title'}</h5>
                <p className="text-sm text-gray-600">{config.description || 'Domain description...'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Validation Status */}
      <div className="mt-8 p-4 rounded-lg border">
        <div className="flex items-center space-x-2 mb-2">
          {Object.keys(errors).length === 0 && config.name && config.title ? (
            <>
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-green-600">Configuration is valid</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-red-600">Configuration has errors</span>
            </>
          )}
        </div>
        
        {Object.keys(errors).length > 0 && (
          <div className="space-y-1">
            {Object.entries(errors).map(([field, error]) => (
              <p key={field} className="text-sm text-red-600">
                • {error}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};