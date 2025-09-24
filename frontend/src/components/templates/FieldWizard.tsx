import React, { useState, useEffect } from 'react';
import { X, AlertCircle, Type, Database, Calendar, Mail, Link as LinkIcon, Key, Hash, CheckSquare } from 'lucide-react';
import { Entity, Field, Relationship, FieldType, ValidationConfig, FieldUIConfig } from '../../types/template';

interface FieldWizardProps {
  field: Field | null;
  entity: Entity;
  onSave: (field: Omit<Field, 'id'>) => void;
  onCancel: () => void;
  existingFieldNames: string[];
  relationships: Relationship[];
  entities: Entity[];
}

interface FieldTypeOption {
  type: FieldType;
  label: string;
  description: string;
  icon: React.ReactNode;
  category: 'basic' | 'numeric' | 'date' | 'special';
}

const FieldWizard: React.FC<FieldWizardProps> = ({
  field,
  entity,
  onSave,
  onCancel,
  existingFieldNames,
  // relationships and entities are reserved for future relationship field support
  // relationships,
  // entities,
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    title: '',
    type: 'string' as FieldType,
    required: false,
    unique: false,
    defaultValue: '',
  });
  const [validation, setValidation] = useState<ValidationConfig>({});
  const [uiConfig, setUiConfig] = useState<FieldUIConfig>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const fieldTypes: FieldTypeOption[] = [
    // Basic Types
    { type: 'string', label: 'Text (Short)', description: 'Short text field, up to 255 characters', icon: <Type className="h-5 w-5" />, category: 'basic' },
    { type: 'text', label: 'Text (Long)', description: 'Long text field for paragraphs', icon: <Type className="h-5 w-5" />, category: 'basic' },
    { type: 'boolean', label: 'Boolean', description: 'True/false checkbox', icon: <CheckSquare className="h-5 w-5" />, category: 'basic' },
    { type: 'enum', label: 'Choice', description: 'Select from predefined options', icon: <Database className="h-5 w-5" />, category: 'basic' },
    
    // Numeric Types
    { type: 'integer', label: 'Integer', description: 'Whole numbers', icon: <Hash className="h-5 w-5" />, category: 'numeric' },
    { type: 'float', label: 'Float', description: 'Decimal numbers', icon: <Hash className="h-5 w-5" />, category: 'numeric' },
    { type: 'decimal', label: 'Decimal', description: 'Precise decimal numbers', icon: <Hash className="h-5 w-5" />, category: 'numeric' },
    
    // Date/Time Types
    { type: 'date', label: 'Date', description: 'Date picker', icon: <Calendar className="h-5 w-5" />, category: 'date' },
    { type: 'datetime', label: 'DateTime', description: 'Date and time picker', icon: <Calendar className="h-5 w-5" />, category: 'date' },
    { type: 'time', label: 'Time', description: 'Time picker', icon: <Calendar className="h-5 w-5" />, category: 'date' },
    
    // Special Types
    { type: 'email', label: 'Email', description: 'Email address with validation', icon: <Mail className="h-5 w-5" />, category: 'special' },
    { type: 'url', label: 'URL', description: 'Web address with validation', icon: <LinkIcon className="h-5 w-5" />, category: 'special' },
    { type: 'uuid', label: 'UUID', description: 'Unique identifier', icon: <Key className="h-5 w-5" />, category: 'special' },
    { type: 'json', label: 'JSON', description: 'Structured data object', icon: <Database className="h-5 w-5" />, category: 'special' },
    { type: 'file', label: 'File', description: 'File upload field', icon: <Database className="h-5 w-5" />, category: 'special' },
    { type: 'image', label: 'Image', description: 'Image upload field', icon: <Database className="h-5 w-5" />, category: 'special' },
  ];

  useEffect(() => {
    if (field) {
      setFormData({
        name: field.name,
        title: field.title,
        type: field.type,
        required: field.required || false,
        unique: field.unique || false,
        defaultValue: field.defaultValue || '',
      });
      setValidation(field.validation || {});
      setUiConfig(field.uiConfig || {});
    }
  }, [field]);

  // Auto-generate field name from title
  useEffect(() => {
    if (formData.title && !field) {
      const fieldName = formData.title
        .toLowerCase()
        .replace(/\s+/g, '_')
        .replace(/[^a-z0-9_]/g, '');
      setFormData(prev => ({ ...prev, name: fieldName }));
    }
  }, [formData.title, field]);

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!formData.title.trim()) {
        newErrors.title = 'Field title is required';
      }

      if (!formData.name.trim()) {
        newErrors.name = 'Field name is required';
      } else {
        // Check for duplicate names (excluding current field if editing)
        const isDuplicate = existingFieldNames
          .filter(name => field ? name !== field.name : true)
          .some(name => name.toLowerCase() === formData.name.toLowerCase());
        
        if (isDuplicate) {
          newErrors.name = 'A field with this name already exists';
        }

        // Validate field name format
        if (!/^[a-z][a-z0-9_]*$/.test(formData.name)) {
          newErrors.name = 'Field name must be lowercase, start with a letter, and contain only letters, numbers, and underscores';
        }
      }
    }

    if (step === 3 && formData.type === 'enum') {
      if (!validation.choices || validation.choices.length === 0) {
        newErrors.choices = 'At least one choice is required for enum fields';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSave = () => {
    if (validateStep(currentStep)) {
      const fieldData: Omit<Field, 'id'> = {
        name: formData.name.trim(),
        title: formData.title.trim(),
        type: formData.type,
        required: formData.required,
        unique: formData.unique,
        defaultValue: formData.defaultValue || undefined,
        validation: Object.keys(validation).length > 0 ? validation : undefined,
        uiConfig: Object.keys(uiConfig).length > 0 ? uiConfig : undefined,
      };
      onSave(fieldData);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleValidationChange = (field: string, value: any) => {
    setValidation(prev => ({ ...prev, [field]: value }));
  };

  const handleUIConfigChange = (field: string, value: any) => {
    setUiConfig(prev => ({ ...prev, [field]: value }));
  };

  const addChoice = () => {
    const choices = validation.choices || [];
    setValidation(prev => ({ ...prev, choices: [...choices, ''] }));
  };

  const updateChoice = (index: number, value: string) => {
    const choices = [...(validation.choices || [])];
    choices[index] = value;
    setValidation(prev => ({ ...prev, choices }));
  };

  const removeChoice = (index: number) => {
    const choices = [...(validation.choices || [])];
    choices.splice(index, 1);
    setValidation(prev => ({ ...prev, choices }));
  };

  const groupedFieldTypes = fieldTypes.reduce((acc, fieldType) => {
    if (!acc[fieldType.category]) {
      acc[fieldType.category] = [];
    }
    acc[fieldType.category].push(fieldType);
    return acc;
  }, {} as Record<string, FieldTypeOption[]>);

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-4">Basic Information</h4>
        
        {/* Field Title */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Field Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => handleChange('title', e.target.value)}
            placeholder="e.g., First Name, Email Address, Price"
            className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
              errors.title ? 'border-red-300' : 'border-gray-300'
            }`}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {errors.title}
            </p>
          )}
        </div>

        {/* Field Name */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Field Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., first_name, email, price"
            className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
              errors.name ? 'border-red-300' : 'border-gray-300'
            }`}
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {errors.name}
            </p>
          )}
          <p className="text-xs text-gray-500 mt-1">
            Used as the database column name
          </p>
        </div>

        {/* Field Flags */}
        <div className="space-y-3">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="required"
              checked={formData.required}
              onChange={(e) => handleChange('required', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="required" className="ml-2 text-sm text-gray-700">
              Required field
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="unique"
              checked={formData.unique}
              onChange={(e) => handleChange('unique', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="unique" className="ml-2 text-sm text-gray-700">
              Unique values only
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-4">Field Type</h4>
        
        {Object.entries(groupedFieldTypes).map(([category, types]) => (
          <div key={category} className="mb-6">
            <h5 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
              {category.replace('_', ' ')} Types
            </h5>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {types.map((fieldType) => (
                <label key={fieldType.type} className="relative">
                  <input
                    type="radio"
                    name="fieldType"
                    value={fieldType.type}
                    checked={formData.type === fieldType.type}
                    onChange={(e) => handleChange('type', e.target.value)}
                    className="sr-only"
                  />
                  <div className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                    formData.type === fieldType.type
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}>
                    <div className="flex items-center mb-2">
                      {fieldType.icon}
                      <span className="ml-2 text-sm font-medium">{fieldType.label}</span>
                    </div>
                    <p className="text-xs text-gray-500">{fieldType.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-4">Validation & Configuration</h4>

        {/* Default Value */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Default Value
          </label>
          <input
            type="text"
            value={formData.defaultValue}
            onChange={(e) => handleChange('defaultValue', e.target.value)}
            placeholder="Optional default value"
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Type-specific validation */}
        {(formData.type === 'string' || formData.type === 'text') && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Length
                </label>
                <input
                  type="number"
                  value={validation.min_length || ''}
                  onChange={(e) => handleValidationChange('min_length', parseInt(e.target.value) || undefined)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Length
                </label>
                <input
                  type="number"
                  value={validation.max_length || ''}
                  onChange={(e) => handleValidationChange('max_length', parseInt(e.target.value) || undefined)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Pattern (Regex)
              </label>
              <input
                type="text"
                value={validation.pattern || ''}
                onChange={(e) => handleValidationChange('pattern', e.target.value || undefined)}
                placeholder="e.g., ^[A-Z][a-z]+$"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        )}

        {(formData.type === 'integer' || formData.type === 'float' || formData.type === 'decimal') && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Value
              </label>
              <input
                type="number"
                value={validation.min_value || ''}
                onChange={(e) => handleValidationChange('min_value', parseFloat(e.target.value) || undefined)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Value
              </label>
              <input
                type="number"
                value={validation.max_value || ''}
                onChange={(e) => handleValidationChange('max_value', parseFloat(e.target.value) || undefined)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        )}

        {formData.type === 'enum' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Choices *
            </label>
            <div className="space-y-2">
              {(validation.choices || ['']).map((choice, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={choice}
                    onChange={(e) => updateChoice(index, e.target.value)}
                    placeholder={`Choice ${index + 1}`}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => removeChoice(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={addChoice}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                + Add Choice
              </button>
            </div>
            {errors.choices && (
              <p className="mt-1 text-sm text-red-600 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.choices}
              </p>
            )}
          </div>
        )}

        {/* UI Configuration */}
        <div className="border-t border-gray-200 pt-6">
          <h5 className="text-sm font-medium text-gray-900 mb-3">UI Configuration</h5>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Placeholder Text
              </label>
              <input
                type="text"
                value={uiConfig.placeholder || ''}
                onChange={(e) => handleUIConfigChange('placeholder', e.target.value || undefined)}
                placeholder="Placeholder text for input field"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Help Text
              </label>
              <input
                type="text"
                value={uiConfig.help_text || ''}
                onChange={(e) => handleUIConfigChange('help_text', e.target.value || undefined)}
                placeholder="Helpful description for users"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="hideInList"
                  checked={uiConfig.hide_in_list || false}
                  onChange={(e) => handleUIConfigChange('hide_in_list', e.target.checked || undefined)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="hideInList" className="ml-2 text-sm text-gray-700">
                  Hide in list view
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="hideInForm"
                  checked={uiConfig.hide_in_form || false}
                  onChange={(e) => handleUIConfigChange('hide_in_form', e.target.checked || undefined)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="hideInForm" className="ml-2 text-sm text-gray-700">
                  Hide in forms
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {field ? 'Edit Field' : 'Add New Field'} - {entity.name}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              {[1, 2, 3].map((step) => (
                <div
                  key={step}
                  className={`w-8 h-2 rounded-full ${
                    step === currentStep
                      ? 'bg-blue-600'
                      : step < currentStep
                      ? 'bg-green-600'
                      : 'bg-gray-200'
                  }`}
                />
              ))}
              <span className="text-sm text-gray-500 ml-2">
                Step {currentStep} of 3
              </span>
            </div>
          </div>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-500">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            
            {currentStep < 3 ? (
              <button
                onClick={handleNext}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSave}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                {field ? 'Update Field' : 'Create Field'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FieldWizard;