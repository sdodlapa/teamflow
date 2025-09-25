import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { DomainConfig } from '../../types/template';
import { validateDomainConfig } from '../../services/templateValidation';
import { templateApi } from '../../services/templateApi';
import './EnhancedDomainConfigForm.css';

interface EnhancedDomainConfigFormProps {
  initialConfig?: Partial<DomainConfig>;
  onConfigChange: (config: DomainConfig) => void;
  onValidationChange: (isValid: boolean, errors: string[]) => void;
  showPreview?: boolean;
  autoSave?: boolean;
}

interface ValidationState {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

interface AvailabilityState {
  checking: boolean;
  available: boolean | null;
  lastChecked?: string;
}

const DOMAIN_TYPES = [
  { value: 'task_management', label: 'Task Management', icon: '📋', description: 'Project and task organization systems' },
  { value: 'e_commerce', label: 'E-Commerce', icon: '🛒', description: 'Online store and marketplace platforms' },
  { value: 'crm', label: 'Customer Relationship Management', icon: '👥', description: 'Customer data and relationship tools' },
  { value: 'healthcare', label: 'Healthcare Management', icon: '🏥', description: 'Medical records and patient care systems' },
  { value: 'real_estate', label: 'Real Estate', icon: '🏠', description: 'Property management and real estate tools' },
  { value: 'education', label: 'Education Platform', icon: '🎓', description: 'Learning management and education tools' },
  { value: 'finance', label: 'Financial Services', icon: '💰', description: 'Banking, accounting, and finance tools' },
  { value: 'business', label: 'Business Management', icon: '🏢', description: 'General business process automation' },
  { value: 'custom', label: 'Custom Domain', icon: '⚙️', description: 'Specialized or unique business requirements' }
];

const COLOR_SCHEMES = [
  { value: 'blue', label: 'Professional Blue', color: '#3B82F6', accent: '#1E40AF' },
  { value: 'green', label: 'Growth Green', color: '#10B981', accent: '#047857' },
  { value: 'purple', label: 'Creative Purple', color: '#8B5CF6', accent: '#6D28D9' },
  { value: 'red', label: 'Dynamic Red', color: '#EF4444', accent: '#DC2626' },
  { value: 'orange', label: 'Energy Orange', color: '#F97316', accent: '#EA580C' },
  { value: 'pink', label: 'Modern Pink', color: '#EC4899', accent: '#DB2777' },
  { value: 'teal', label: 'Tech Teal', color: '#14B8A6', accent: '#0F766E' },
  { value: 'indigo', label: 'Corporate Indigo', color: '#6366F1', accent: '#4F46E5' }
];

const LOGO_OPTIONS = [
  { category: 'Business', icons: ['🏢', '💼', '📊', '📈', '🎯', '⚡'] },
  { category: 'Technology', icons: ['💻', '📱', '⚙️', '🔧', '🛠️', '🚀'] },
  { category: 'Commerce', icons: ['🛒', '💳', '📦', '🏪', '💰', '📋'] },
  { category: 'Services', icons: ['🏥', '🎓', '🏠', '✈️', '🚗', '📞'] }
];

const THEMES = [
  { value: 'default', label: 'Default', description: 'Clean and professional design' },
  { value: 'modern', label: 'Modern', description: 'Contemporary with bold elements' },
  { value: 'minimal', label: 'Minimal', description: 'Simple and focused interface' },
  { value: 'corporate', label: 'Corporate', description: 'Traditional business styling' },
  { value: 'creative', label: 'Creative', description: 'Vibrant and artistic design' }
];

export const EnhancedDomainConfigForm: React.FC<EnhancedDomainConfigFormProps> = ({
  initialConfig,
  onConfigChange,
  onValidationChange,
  showPreview = true,
  autoSave = false
}) => {
  // Enhanced state management
  const [config, setConfig] = useState<Partial<DomainConfig>>({
    name: '',
    title: '',
    description: '',
    domain_type: 'business',
    version: '1.0.0',
    logo: '🏢',
    color_scheme: 'blue',
    theme: 'default',
    ...initialConfig
  });

  const [validation, setValidation] = useState<ValidationState>({
    isValid: false,
    errors: [],
    warnings: []
  });

  const [availability, setAvailability] = useState<AvailabilityState>({
    checking: false,
    available: null
  });

  const [isValidating, setIsValidating] = useState(false);
  const [activeSection, setActiveSection] = useState<string>('basic');
  const [expandedLogoCategory, setExpandedLogoCategory] = useState<string>('Business');

  // Memoized computed values
  const selectedDomainType = useMemo(() => 
    DOMAIN_TYPES.find(type => type.value === config.domain_type) || DOMAIN_TYPES[0], 
    [config.domain_type]
  );

  const selectedColorScheme = useMemo(() => 
    COLOR_SCHEMES.find(scheme => scheme.value === config.color_scheme) || COLOR_SCHEMES[0], 
    [config.color_scheme]
  );

  const selectedTheme = useMemo(() => 
    THEMES.find(theme => theme.value === config.theme) || THEMES[0], 
    [config.theme]
  );

  // Enhanced validation with domain availability
  const validateConfiguration = useCallback(async (configToValidate: Partial<DomainConfig>) => {
    if (!configToValidate.name || !configToValidate.title) {
      setValidation({ isValid: false, errors: [], warnings: [] });
      onValidationChange(false, []);
      return;
    }

    setIsValidating(true);

    try {
      // Validate domain configuration
      const validationResult = await validateDomainConfig(configToValidate as DomainConfig);
      const errors = validationResult.errors || [];
      
      // Add client-side warnings
      const warnings: string[] = [];
      if (!configToValidate.description || configToValidate.description.length < 50) {
        warnings.push('Consider adding a more detailed description for better user understanding');
      }
      if (configToValidate.name && configToValidate.name.length < 3) {
        warnings.push('Domain name should be at least 3 characters long');
      }
      if (configToValidate.title && configToValidate.title.length > 50) {
        warnings.push('Consider shortening the title for better display');
      }

      const isValid = errors.length === 0;
      
      setValidation({
        isValid,
        errors: errors.map(e => typeof e === 'string' ? e : e.message),
        warnings
      });

      onValidationChange(isValid, errors.map(e => typeof e === 'string' ? e : e.message));

      if (isValid) {
        onConfigChange(configToValidate as DomainConfig);
      }
    } catch (error) {
      console.error('Validation error:', error);
      setValidation({
        isValid: false,
        errors: ['Validation service unavailable. Please check your connection.'],
        warnings: []
      });
      onValidationChange(false, ['Validation service unavailable']);
    } finally {
      setIsValidating(false);
    }
  }, [onConfigChange, onValidationChange]);

  // Check domain name availability
  const checkAvailability = useCallback(async (domainName: string) => {
    if (!domainName || domainName.length < 3) {
      setAvailability({ checking: false, available: null });
      return;
    }

    setAvailability({ checking: true, available: null });

    try {
      // Check if domain name is available
      const response = await templateApi.checkNameAvailability(domainName);
      setAvailability({
        checking: false,
        available: response.available,
        lastChecked: domainName
      });
    } catch (error) {
      console.error('Availability check error:', error);
      setAvailability({ checking: false, available: null });
    }
  }, []);

  // Debounced validation effect
  useEffect(() => {
    const debounceTimeout = setTimeout(() => {
      validateConfiguration(config);
    }, 500);

    return () => clearTimeout(debounceTimeout);
  }, [config, validateConfiguration]);

  // Debounced availability check
  useEffect(() => {
    if (config.name && config.name !== availability.lastChecked) {
      const availabilityTimeout = setTimeout(() => {
        checkAvailability(config.name || '');
      }, 800);

      return () => clearTimeout(availabilityTimeout);
    }
  }, [config.name, availability.lastChecked, checkAvailability]);

  // Enhanced config update function
  const updateConfig = useCallback((field: keyof DomainConfig, value: any) => {
    setConfig(prevConfig => {
      const newConfig = { ...prevConfig, [field]: value };
      
      // Auto-save if enabled
      if (autoSave && validation.isValid) {
        setTimeout(() => onConfigChange(newConfig as DomainConfig), 100);
      }
      
      return newConfig;
    });
  }, [autoSave, validation.isValid, onConfigChange]);

  // Smart domain name generation
  const generateDomainName = useCallback((title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 50);
  }, []);

  const handleTitleChange = useCallback((title: string) => {
    updateConfig('title', title);
    
    // Auto-generate name if not manually set
    if (!config.name || config.name === generateDomainName(config.title || '')) {
      const newName = generateDomainName(title);
      updateConfig('name', newName);
    }
  }, [config.name, config.title, generateDomainName, updateConfig]);

  // Get character count styling
  const getCharacterCountClass = (current: number, max: number) => {
    const percentage = (current / max) * 100;
    if (percentage >= 90) return 'character-count danger';
    if (percentage >= 75) return 'character-count warning';
    return 'character-count';
  };

  // Error helper
  const getFieldError = (field: string): string | undefined => {
    return validation.errors.find(error => error.toLowerCase().includes(field.toLowerCase()));
  };

  return (
    <div className="enhanced-domain-config-form">
      <div className="form-header">
        <h2 className="form-title">
          <span className="form-icon">⚙️</span>
          Enhanced Domain Configuration
        </h2>
        <p className="form-description">
          Configure your business domain with advanced validation and real-time feedback
        </p>
      </div>

      {/* Section Navigation */}
      <div className="section-nav">
        {[
          { key: 'basic', label: 'Basic Info', icon: '📝' },
          { key: 'branding', label: 'Branding', icon: '🎨' },
          { key: 'advanced', label: 'Advanced', icon: '⚙️' }
        ].map(section => (
          <button
            key={section.key}
            className={`nav-button ${activeSection === section.key ? 'active' : ''}`}
            onClick={() => setActiveSection(section.key)}
            type="button"
          >
            <span className="nav-icon">{section.icon}</span>
            {section.label}
          </button>
        ))}
      </div>

      <div className="form-content">
        {/* Basic Information Section */}
        {activeSection === 'basic' && (
          <div className="form-section">
            <h3 className="section-title">
              📝 Basic Information
            </h3>

            {/* Domain Title */}
            <div className="form-field">
              <label htmlFor="title" className="field-label required">
                Domain Title
              </label>
              <input
                type="text"
                id="title"
                value={config.title || ''}
                onChange={(e) => handleTitleChange(e.target.value)}
                className={`field-input ${getFieldError('title') ? 'error' : ''}`}
                placeholder="e.g., E-Commerce Management Platform"
                maxLength={100}
                autoComplete="off"
              />
              <div className="field-footer">
                <span className={getCharacterCountClass((config.title || '').length, 100)}>
                  {(config.title || '').length}/100 characters
                </span>
                {getFieldError('title') && (
                  <span className="field-error">{getFieldError('title')}</span>
                )}
              </div>
            </div>

            {/* Domain Name with Availability */}
            <div className="form-field">
              <label htmlFor="name" className="field-label required">
                Domain Name (Technical Identifier)
              </label>
              <div className="field-input-group">
                <input
                  type="text"
                  id="name"
                  value={config.name || ''}
                  onChange={(e) => updateConfig('name', e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                  className={`field-input ${getFieldError('name') ? 'error' : ''}`}
                  placeholder="e.g., e_commerce_platform"
                  pattern="[a-z0-9_]+"
                  maxLength={50}
                  autoComplete="off"
                />
                <div className="availability-indicator">
                  {availability.checking && (
                    <span className="availability-status checking">
                      <div className="spinner"></div>
                      Checking...
                    </span>
                  )}
                  {!availability.checking && availability.available === true && (
                    <span className="availability-status available">
                      ✅ Available
                    </span>
                  )}
                  {!availability.checking && availability.available === false && (
                    <span className="availability-status unavailable">
                      ❌ Taken
                    </span>
                  )}
                </div>
              </div>
              <div className="field-footer">
                <span className={getCharacterCountClass((config.name || '').length, 50)}>
                  {(config.name || '').length}/50 characters
                </span>
                <span className="field-hint">Lowercase letters, numbers, and underscores only</span>
                {getFieldError('name') && (
                  <span className="field-error">{getFieldError('name')}</span>
                )}
              </div>
            </div>

            {/* Description */}
            <div className="form-field">
              <label htmlFor="description" className="field-label">
                Description
              </label>
              <textarea
                id="description"
                value={config.description || ''}
                onChange={(e) => updateConfig('description', e.target.value)}
                className="field-textarea"
                placeholder="Describe what this domain template will be used for, its main features, and target use cases..."
                rows={4}
                maxLength={500}
              />
              <div className="field-footer">
                <span className={getCharacterCountClass((config.description || '').length, 500)}>
                  {(config.description || '').length}/500 characters
                </span>
                <span className="field-hint">A detailed description helps users understand the template's purpose</span>
              </div>
            </div>

            {/* Domain Type */}
            <div className="form-field">
              <label htmlFor="domain_type" className="field-label">
                Domain Category
              </label>
              <div className="domain-type-grid">
                {DOMAIN_TYPES.map(type => (
                  <div
                    key={type.value}
                    className={`domain-type-card ${config.domain_type === type.value ? 'selected' : ''}`}
                    onClick={() => updateConfig('domain_type', type.value)}
                  >
                    <div className="domain-type-icon">{type.icon}</div>
                    <div className="domain-type-content">
                      <h4 className="domain-type-label">{type.label}</h4>
                      <p className="domain-type-description">{type.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Version */}
            <div className="form-field">
              <label htmlFor="version" className="field-label">
                Version
              </label>
              <input
                type="text"
                id="version"
                value={config.version || '1.0.0'}
                onChange={(e) => updateConfig('version', e.target.value)}
                className="field-input"
                pattern="\\d+\\.\\d+\\.\\d+"
                placeholder="1.0.0"
                autoComplete="off"
              />
              <div className="field-footer">
                <span className="field-hint">Semantic versioning (major.minor.patch)</span>
              </div>
            </div>
          </div>
        )}

        {/* Branding Section */}
        {activeSection === 'branding' && (
          <div className="form-section">
            <h3 className="section-title">
              🎨 Branding & Visual Identity
            </h3>

            {/* Logo Selection */}
            <div className="form-field">
              <label className="field-label">
                Logo/Icon
              </label>
              <div className="logo-selector">
                <div className="logo-categories">
                  {LOGO_OPTIONS.map(category => (
                    <div key={category.category} className="logo-category">
                      <button
                        type="button"
                        className={`category-header ${expandedLogoCategory === category.category ? 'expanded' : ''}`}
                        onClick={() => setExpandedLogoCategory(
                          expandedLogoCategory === category.category ? '' : category.category
                        )}
                      >
                        {category.category}
                        <span className="category-arrow">
                          {expandedLogoCategory === category.category ? '▼' : '▶'}
                        </span>
                      </button>
                      {expandedLogoCategory === category.category && (
                        <div className="logo-grid">
                          {category.icons.map(emoji => (
                            <button
                              key={emoji}
                              type="button"
                              onClick={() => updateConfig('logo', emoji)}
                              className={`logo-option ${config.logo === emoji ? 'selected' : ''}`}
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                {/* Custom Logo Input */}
                <div className="custom-logo-input">
                  <input
                    type="text"
                    value={config.logo || ''}
                    onChange={(e) => updateConfig('logo', e.target.value)}
                    className="field-input"
                    placeholder="Or enter custom emoji/icon"
                    maxLength={10}
                  />
                </div>
              </div>
            </div>

            {/* Color Scheme */}
            <div className="form-field">
              <label className="field-label">
                Color Scheme
              </label>
              <div className="color-scheme-grid">
                {COLOR_SCHEMES.map(scheme => (
                  <div
                    key={scheme.value}
                    className={`color-scheme-card ${config.color_scheme === scheme.value ? 'selected' : ''}`}
                    onClick={() => updateConfig('color_scheme', scheme.value)}
                  >
                    <div className="color-preview">
                      <div 
                        className="color-primary" 
                        style={{ backgroundColor: scheme.color }}
                      ></div>
                      <div 
                        className="color-accent" 
                        style={{ backgroundColor: scheme.accent }}
                      ></div>
                    </div>
                    <div className="color-info">
                      <h4 className="color-name">{scheme.label}</h4>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Theme Selection */}
            <div className="form-field">
              <label className="field-label">
                UI Theme
              </label>
              <div className="theme-grid">
                {THEMES.map(theme => (
                  <div
                    key={theme.value}
                    className={`theme-card ${config.theme === theme.value ? 'selected' : ''}`}
                    onClick={() => updateConfig('theme', theme.value)}
                  >
                    <h4 className="theme-name">{theme.label}</h4>
                    <p className="theme-description">{theme.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Advanced Section */}
        {activeSection === 'advanced' && (
          <div className="form-section">
            <h3 className="section-title">
              ⚙️ Advanced Configuration
            </h3>
            
            <div className="coming-soon">
              <div className="coming-soon-icon">🚧</div>
              <h4>Advanced Features Coming Soon</h4>
              <p>Custom metadata, API configuration, and integration settings will be available in future updates.</p>
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Preview */}
      {showPreview && (
        <div className="form-section">
          <h3 className="section-title">
            👁️ Live Preview
          </h3>
          <div className="preview-container">
            <div className="preview-card" style={{ 
              borderColor: selectedColorScheme.color,
              backgroundColor: `${selectedColorScheme.color}10`
            }}>
              <div className="preview-header">
                <span className="preview-logo">{config.logo}</span>
                <div className="preview-content">
                  <h3 className="preview-title" style={{ color: selectedColorScheme.accent }}>
                    {config.title || 'Domain Title'}
                  </h3>
                  <p className="preview-type">{selectedDomainType.label}</p>
                </div>
              </div>
              <p className="preview-description">
                {config.description || 'Add a description to see how it will appear to users...'}
              </p>
              <div className="preview-footer">
                <span className="preview-version">v{config.version}</span>
                <span className="preview-theme">{selectedTheme.label} theme</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Validation Status */}
      <div className="validation-panel">
        <div className="validation-header">
          {isValidating ? (
            <div className="validation-status validating">
              <div className="spinner"></div>
              <span>Validating configuration...</span>
            </div>
          ) : validation.isValid ? (
            <div className="validation-status valid">
              <span className="status-icon">✅</span>
              <span>Configuration is valid and ready to use</span>
            </div>
          ) : (
            <div className="validation-status invalid">
              <span className="status-icon">❌</span>
              <span>Configuration has {validation.errors.length} error{validation.errors.length !== 1 ? 's' : ''}</span>
            </div>
          )}
        </div>

        {/* Validation Errors */}
        {validation.errors.length > 0 && (
          <div className="validation-messages errors">
            <h4 className="messages-title">❌ Errors to Fix:</h4>
            <ul className="messages-list">
              {validation.errors.map((error, index) => (
                <li key={index} className="message-item error">
                  {error}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Validation Warnings */}
        {validation.warnings.length > 0 && (
          <div className="validation-messages warnings">
            <h4 className="messages-title">⚠️ Recommendations:</h4>
            <ul className="messages-list">
              {validation.warnings.map((warning, index) => (
                <li key={index} className="message-item warning">
                  {warning}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Success Actions */}
        {validation.isValid && (
          <div className="success-actions">
            <button 
              type="button" 
              className="action-button primary"
              onClick={() => onConfigChange(config as DomainConfig)}
            >
              Save Configuration
            </button>
            <button 
              type="button" 
              className="action-button secondary"
              onClick={() => {
                // Export config as JSON
                const dataStr = JSON.stringify(config, null, 2);
                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${config.name || 'domain'}-config.json`;
                link.click();
                URL.revokeObjectURL(url);
              }}
            >
              Export Config
            </button>
          </div>
        )}
      </div>
    </div>
  );
};