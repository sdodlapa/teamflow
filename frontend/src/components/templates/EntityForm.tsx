import React, { useState, useEffect } from 'react';
import { X, AlertCircle, Database, Link } from 'lucide-react';
import { Entity } from '../../types/template';

interface EntityFormProps {
  entity: Entity | null;
  onSave: (entity: Omit<Entity, 'id'>) => void;
  onCancel: () => void;
  existingEntityNames: string[];
}

const EntityForm: React.FC<EntityFormProps> = ({
  entity,
  onSave,
  onCancel,
  existingEntityNames,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'core' as 'core' | 'lookup',
    tableName: '',
    primaryKey: 'id',
    displayField: '',
    timestamps: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    if (entity) {
      setFormData({
        name: entity.name,
        description: entity.description || '',
        type: entity.type,
        tableName: entity.tableName || '',
        primaryKey: entity.primaryKey || 'id',
        displayField: entity.displayField || '',
        timestamps: entity.timestamps ?? true,
      });
    } else {
      // Reset form for new entity
      setFormData({
        name: '',
        description: '',
        type: 'core',
        tableName: '',
        primaryKey: 'id',
        displayField: '',
        timestamps: true,
      });
    }
    setErrors({});
  }, [entity]);

  // Auto-generate table name from entity name
  useEffect(() => {
    if (formData.name && !formData.tableName) {
      const tableName = formData.name
        .toLowerCase()
        .replace(/\s+/g, '_')
        .replace(/[^a-z0-9_]/g, '');
      setFormData(prev => ({ ...prev, tableName }));
    }
  }, [formData.name, formData.tableName]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Required fields
    if (!formData.name.trim()) {
      newErrors.name = 'Entity name is required';
    } else {
      // Check for duplicate names (excluding current entity if editing)
      const isDuplicate = existingEntityNames
        .filter(name => entity ? name !== entity.name : true)
        .some(name => name.toLowerCase() === formData.name.toLowerCase());
      
      if (isDuplicate) {
        newErrors.name = 'An entity with this name already exists';
      }

      // Validate entity name format
      if (!/^[a-zA-Z][a-zA-Z0-9\s]*$/.test(formData.name)) {
        newErrors.name = 'Entity name must start with a letter and contain only letters, numbers, and spaces';
      }
    }

    if (!formData.tableName.trim()) {
      newErrors.tableName = 'Table name is required';
    } else if (!/^[a-z][a-z0-9_]*$/.test(formData.tableName)) {
      newErrors.tableName = 'Table name must be lowercase, start with a letter, and contain only letters, numbers, and underscores';
    }

    if (!formData.primaryKey.trim()) {
      newErrors.primaryKey = 'Primary key field name is required';
    } else if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(formData.primaryKey)) {
      newErrors.primaryKey = 'Primary key must be a valid field name';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const entityData: Omit<Entity, 'id'> = {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      type: formData.type,
      tableName: formData.tableName.trim() || formData.name.toLowerCase().replace(/\s+/g, '_'),
      primaryKey: formData.primaryKey.trim(),
      displayField: formData.displayField.trim() || undefined,
      timestamps: formData.timestamps,
      fields: entity?.fields || [], // Preserve existing fields when editing
    };

    onSave(entityData);
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {entity ? 'Edit Entity' : 'Create New Entity'}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Define the data structure for your application
            </p>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium text-gray-900">Basic Information</h4>
            
            {/* Entity Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Entity Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="e.g., User, Product, Order"
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
            </div>

            {/* Entity Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Entity Type *
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label className="relative">
                  <input
                    type="radio"
                    name="type"
                    value="core"
                    checked={formData.type === 'core'}
                    onChange={(e) => handleChange('type', e.target.value)}
                    className="sr-only"
                  />
                  <div className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                    formData.type === 'core'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}>
                    <div className="flex items-center">
                      <Database className="h-4 w-4 mr-2 text-blue-600" />
                      <span className="text-sm font-medium">Core Entity</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Main business entities (Users, Orders, etc.)
                    </p>
                  </div>
                </label>

                <label className="relative">
                  <input
                    type="radio"
                    name="type"
                    value="lookup"
                    checked={formData.type === 'lookup'}
                    onChange={(e) => handleChange('type', e.target.value)}
                    className="sr-only"
                  />
                  <div className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                    formData.type === 'lookup'
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}>
                    <div className="flex items-center">
                      <Link className="h-4 w-4 mr-2 text-green-600" />
                      <span className="text-sm font-medium">Lookup Table</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Reference data (Categories, Statuses, etc.)
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                placeholder="Brief description of this entity..."
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="border-t border-gray-200 pt-6">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              Advanced Settings
              <svg
                className={`ml-2 h-4 w-4 transform transition-transform ${
                  showAdvanced ? 'rotate-180' : ''
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showAdvanced && (
              <div className="mt-4 space-y-4">
                {/* Table Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Database Table Name *
                  </label>
                  <input
                    type="text"
                    value={formData.tableName}
                    onChange={(e) => handleChange('tableName', e.target.value)}
                    placeholder="e.g., users, products, order_items"
                    className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                      errors.tableName ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.tableName && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.tableName}
                    </p>
                  )}
                </div>

                {/* Primary Key */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Key Field *
                  </label>
                  <input
                    type="text"
                    value={formData.primaryKey}
                    onChange={(e) => handleChange('primaryKey', e.target.value)}
                    placeholder="id"
                    className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                      errors.primaryKey ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.primaryKey && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="h-4 w-4 mr-1" />
                      {errors.primaryKey}
                    </p>
                  )}
                </div>

                {/* Display Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Display Field
                  </label>
                  <input
                    type="text"
                    value={formData.displayField}
                    onChange={(e) => handleChange('displayField', e.target.value)}
                    placeholder="e.g., name, title, email"
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Field to use as the display name for this entity
                  </p>
                </div>

                {/* Timestamps */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="timestamps"
                    checked={formData.timestamps}
                    onChange={(e) => handleChange('timestamps', e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="timestamps" className="ml-2 text-sm text-gray-700">
                    Include created_at and updated_at timestamps
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {entity ? 'Update Entity' : 'Create Entity'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EntityForm;