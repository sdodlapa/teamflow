import React, { useState, useEffect } from 'react';
import { validateDomainConfig } from '../../services/templateValidation';
import { DomainConfig, ValidationError } from '../../types/template';

interface DomainConfigFormProps {
  initialConfig?: Partial<DomainConfig>;
  onConfigChange: (config: DomainConfig) => void;
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

export const DomainConfigForm: React.FC<DomainConfigFormProps> = ({
  initialConfig,
  onConfigChange,
  onValidationChange
}) => {
  const [config, setConfig] = useState<Partial<DomainConfig>>({
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

  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [isValidating, setIsValidating] = useState(false);

  // Validate configuration on change
  useEffect(() => {
    const validateConfig = async () => {
      if (!config.name || !config.title) {
        onValidationChange(false);
        return;
      }

      setIsValidating(true);
      try {
        const validationResult = await validateDomainConfig(config as DomainConfig);
        setErrors(validationResult.errors || []);
        const isValid = !validationResult.errors || validationResult.errors.length === 0;
        onValidationChange(isValid);
        
        if (isValid) {
          onConfigChange(config as DomainConfig);
        }
      } catch (error) {
        console.error('Validation error:', error);
        onValidationChange(false);
      } finally {
        setIsValidating(false);
      }
    };

    const debounceTimeout = setTimeout(validateConfig, 500);
    return () => clearTimeout(debounceTimeout);
  }, [config, onConfigChange, onValidationChange]);

  const updateConfig = (field: keyof DomainConfig, value: any) => {
    setConfig((prev: Partial<DomainConfig>) => ({
      ...prev,
      [field]: value
    }));
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
    if (!config.name || config.name === generateDomainName(config.title || '')) {
      updateConfig('name', generateDomainName(title));
    }
  };

  const getErrorForField = (field: string): string | undefined => {
    return errors.find(error => error.field === field)?.message;
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
              value={config.title || ''}
              onChange={(e) => handleTitleChange(e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                getErrorForField('title') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., E-Commerce Platform"
              maxLength={100}
            />
            {getErrorForField('title') && (
              <p className="mt-1 text-sm text-red-600">{getErrorForField('title')}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              The display name for your domain ({(config.title || '').length}/100)
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
              value={config.name || ''}
              onChange={(e) => updateConfig('name', e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                getErrorForField('name') ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., e_commerce_platform"
              pattern="[a-z0-9_]+"
              maxLength={50}
            />
            {getErrorForField('name') && (
              <p className="mt-1 text-sm text-red-600">{getErrorForField('name')}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Technical name (lowercase, underscores only) ({(config.name || '').length}/50)
            </p>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              value={config.description || ''}
              onChange={(e) => updateConfig('description', e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe what this domain template is used for..."
              maxLength={500}
            />
            <p className="mt-1 text-sm text-gray-500">
              Optional detailed description ({(config.description || '').length}/500)
            </p>
          </div>

          {/* Domain Type */}
          <div>
            <label htmlFor="domain_type" className="block text-sm font-medium text-gray-700 mb-1">
              Domain Type
            </label>
            <select
              id="domain_type"
              value={config.domain_type || 'custom'}
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
              value={config.version || '1.0.0'}
              onChange={(e) => updateConfig('version', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              pattern="\\d+\\.\\d+\\.\\d+"
              placeholder="1.0.0"
            />
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
                value={config.logo || ''}
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
              value={config.theme || 'default'}
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
          {isValidating ? (
            <>
              <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
              <span className="text-sm text-gray-600">Validating configuration...</span>
            </>
          ) : errors.length === 0 ? (
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
        
        {errors.length > 0 && (
          <div className="space-y-1">
            {errors.map((error, index) => (
              <p key={index} className="text-sm text-red-600">
                • {error.message}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};