import React, { useState } from 'react';
import { X, Plus, Edit3, Trash2, Type, Key, ArrowUp, ArrowDown } from 'lucide-react';
import { Entity, Field, Relationship, FieldType } from '../../types/template';
import FieldWizard from './FieldWizard';

interface FieldManagerProps {
  entity: Entity;
  onFieldsChange: (fields: Field[]) => void;
  onClose: () => void;
  relationships: Relationship[];
  entities: Entity[];
}

const FieldManager: React.FC<FieldManagerProps> = ({
  entity,
  onFieldsChange,
  onClose,
  relationships,
  entities,
}) => {
  const [showFieldWizard, setShowFieldWizard] = useState(false);
  const [editingField, setEditingField] = useState<Field | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | FieldType | 'system'>('all');

  // Get system fields (created_at, updated_at, primary key)
  const systemFields: (Field & { system?: boolean })[] = [
    {
      id: 'system_pk',
      name: entity.primaryKey || 'id',
      title: 'ID',
      type: 'uuid' as FieldType,
      required: true,
      unique: true,
      system: true,
    },
    ...(entity.timestamps
      ? [
          {
            id: 'system_created_at',
            name: 'created_at',
            title: 'Created At',
            type: 'datetime' as FieldType,
            required: true,
            system: true,
          },
          {
            id: 'system_updated_at',
            name: 'updated_at',
            title: 'Updated At',
            type: 'datetime' as FieldType,
            required: true,
            system: true,
          },
        ]
      : []),
  ];

  // Combine user fields with system fields
  const allFields = [...systemFields, ...entity.fields];

  // Filter fields
  const filteredFields = allFields.filter((field) => {
    const matchesSearch = field.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         field.title.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesType = true;
    if (filterType === 'system') {
      matchesType = 'system' in field;
    } else if (filterType !== 'all') {
      matchesType = field.type === filterType && !('system' in field);
    }

    return matchesSearch && matchesType;
  });

  const handleAddField = () => {
    setEditingField(null);
    setShowFieldWizard(true);
  };

  const handleEditField = (field: Field) => {
    setEditingField(field);
    setShowFieldWizard(true);
  };

  const handleDeleteField = (fieldId: string) => {
    if (window.confirm('Are you sure you want to delete this field?')) {
      const updatedFields = entity.fields.filter(f => f.id !== fieldId);
      onFieldsChange(updatedFields);
    }
  };

  const handleFieldSave = (fieldData: Omit<Field, 'id'>) => {
    if (editingField) {
      // Update existing field
      const updatedFields = entity.fields.map(f =>
        f.id === editingField.id ? { ...fieldData, id: editingField.id } : f
      );
      onFieldsChange(updatedFields);
    } else {
      // Add new field
      const newField: Field = {
        ...fieldData,
        id: `field_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      onFieldsChange([...entity.fields, newField]);
    }
    setShowFieldWizard(false);
    setEditingField(null);
  };

  const handleMoveField = (fieldId: string, direction: 'up' | 'down') => {
    const currentIndex = entity.fields.findIndex(f => f.id === fieldId);
    if (currentIndex === -1) return;

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= entity.fields.length) return;

    const reorderedFields = [...entity.fields];
    [reorderedFields[currentIndex], reorderedFields[newIndex]] = 
    [reorderedFields[newIndex], reorderedFields[currentIndex]];
    
    onFieldsChange(reorderedFields);
  };

  const getFieldTypeIcon = (type: FieldType) => {
    switch (type) {
      case 'string':
      case 'text':
        return <Type className="h-4 w-4" />;
      case 'integer':
      case 'float':
      case 'decimal':
        return <span className="text-xs font-mono">#</span>;
      case 'boolean':
        return <span className="text-xs">✓</span>;
      case 'date':
      case 'datetime':
      case 'time':
        return <span className="text-xs">📅</span>;
      case 'email':
        return <span className="text-xs">@</span>;
      case 'uuid':
        return <Key className="h-4 w-4" />;
      default:
        return <Type className="h-4 w-4" />;
    }
  };

  const getFieldTypeColor = (type: FieldType) => {
    switch (type) {
      case 'string':
      case 'text':
      case 'email':
      case 'url':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'integer':
      case 'float':
      case 'decimal':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'boolean':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'date':
      case 'datetime':
      case 'time':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'uuid':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get unique field types for filter
  const availableTypes = Array.from(new Set(allFields.map(f => f.type)));

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Manage Fields - {entity.name}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {entity.fields.length} custom fields, {systemFields.length} system fields
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleAddField}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Field
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search fields..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="sm:w-40">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as any)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Fields</option>
                <option value="system">System Fields</option>
                {availableTypes.map(type => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Fields List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            <div className="space-y-3">
              {filteredFields.map((field, index) => {
                const isSystemField = 'system' in field;
                return (
                  <div
                    key={field.id}
                    className={`border rounded-lg p-4 ${
                      isSystemField 
                        ? 'bg-gray-50 border-gray-200' 
                        : 'bg-white border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {/* Field Icon */}
                        <div className={`flex items-center justify-center w-8 h-8 rounded border ${getFieldTypeColor(field.type)}`}>
                          {getFieldTypeIcon(field.type)}
                        </div>

                        {/* Field Info */}
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="text-sm font-medium text-gray-900">
                              {field.title}
                            </h4>
                            <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                              {field.name}
                            </code>
                            {field.required && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                Required
                              </span>
                            )}
                            {field.unique && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                Unique
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getFieldTypeColor(field.type)}`}>
                              {field.type}
                            </span>
                            {('defaultValue' in field && field.defaultValue !== undefined) && (
                              <span>Default: {String(field.defaultValue)}</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-1">
                        {!isSystemField && (
                          <>
                            {/* Move buttons */}
                            <button
                              onClick={() => handleMoveField(field.id, 'up')}
                              disabled={index === 0}
                              className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                              title="Move Up"
                            >
                              <ArrowUp className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleMoveField(field.id, 'down')}
                              disabled={index === entity.fields.length - 1}
                              className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                              title="Move Down"
                            >
                              <ArrowDown className="h-4 w-4" />
                            </button>
                            
                            {/* Edit button */}
                            <button
                              onClick={() => handleEditField(field)}
                              className="p-1 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded"
                              title="Edit Field"
                            >
                              <Edit3 className="h-4 w-4" />
                            </button>
                            
                            {/* Delete button */}
                            <button
                              onClick={() => handleDeleteField(field.id)}
                              className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                              title="Delete Field"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </>
                        )}
                        
                        {isSystemField && (
                          <span className="text-xs text-gray-400 px-2">System Field</span>
                        )}
                      </div>
                    </div>

                    {/* Field Details */}
                    {(('validation' in field && field.validation) || ('uiConfig' in field && field.uiConfig)) && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="text-xs text-gray-500 space-y-1">
                          {'validation' in field && field.validation && (
                            <div>
                              <strong>Validation:</strong> {JSON.stringify(field.validation, null, 2)}
                            </div>
                          )}
                          {'uiConfig' in field && field.uiConfig && (
                            <div>
                              <strong>UI Config:</strong> {JSON.stringify(field.uiConfig, null, 2)}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Empty State */}
            {filteredFields.length === 0 && (
              <div className="text-center py-12">
                <Type className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No fields found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {searchTerm || filterType !== 'all'
                    ? 'Try adjusting your search or filters'
                    : 'Get started by adding your first field'
                  }
                </p>
                {!searchTerm && filterType === 'all' && (
                  <div className="mt-6">
                    <button
                      onClick={handleAddField}
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Field
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Total: {allFields.length} fields ({entity.fields.length} custom, {systemFields.length} system)
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Done
            </button>
          </div>
        </div>
      </div>

      {/* Field Wizard Modal */}
      {showFieldWizard && (
        <FieldWizard
          field={editingField}
          entity={entity}
          onSave={handleFieldSave}
          onCancel={() => {
            setShowFieldWizard(false);
            setEditingField(null);
          }}
          existingFieldNames={entity.fields.map(f => f.name)}
          relationships={relationships}
          entities={entities}
        />
      )}
    </div>
  );
};

export default FieldManager;