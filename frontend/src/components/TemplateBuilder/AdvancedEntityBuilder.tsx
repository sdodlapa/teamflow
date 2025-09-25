import React, { useState, useCallback } from 'react';
import { 
  Plus, Trash2, Edit3, Save, X, Settings, Type, Hash, 
  Calendar, ToggleLeft, List, Image, FileText, 
  AlertCircle, GripVertical
} from 'lucide-react';
import { Entity, Field, FieldType } from '../../types/template';
import './AdvancedEntityBuilder.css';

interface AdvancedEntityBuilderProps {
  entity?: Entity;
  onSave: (entity: Entity) => void;
  onCancel: () => void;
}

const FIELD_TYPES: Array<{ value: FieldType; label: string; icon: React.ReactNode; description: string }> = [
  { value: 'string', label: 'Text', icon: <Type size={16} />, description: 'Short text input' },
  { value: 'integer', label: 'Integer', icon: <Hash size={16} />, description: 'Whole number' },
  { value: 'float', label: 'Float', icon: <Hash size={16} />, description: 'Decimal number' },
  { value: 'boolean', label: 'Boolean', icon: <ToggleLeft size={16} />, description: 'True/false toggle' },
  { value: 'date', label: 'Date', icon: <Calendar size={16} />, description: 'Date picker' },
  { value: 'enum', label: 'Options', icon: <List size={16} />, description: 'Dropdown selection' },
  { value: 'file', label: 'File', icon: <Image size={16} />, description: 'File upload' },
  { value: 'text', label: 'Long Text', icon: <FileText size={16} />, description: 'Multi-line text area' }
];

export const AdvancedEntityBuilder: React.FC<AdvancedEntityBuilderProps> = ({
  entity,
  onSave,
  onCancel
}) => {
  const [activeTab, setActiveTab] = useState<'basic' | 'fields'>('basic');
  const [entityData, setEntityData] = useState<Entity>(() => entity || {
    id: `entity_${Date.now()}`,
    name: '',
    description: '',
    type: 'core',
    fields: []
  });

  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});
  const [editingField, setEditingField] = useState<string | null>(null);

  // Field management
  const addField = useCallback((type: FieldType = 'string') => {
    const newField: Field = {
      id: `field_${Date.now()}`,
      name: '',
      title: '',
      type,
      required: false,
      validation: {}
    };
    setEntityData(prev => ({
      ...prev,
      fields: [...prev.fields, newField]
    }));
    setEditingField(newField.id);
  }, []);

  const updateField = useCallback((fieldId: string, updates: Partial<Field>) => {
    setEntityData(prev => ({
      ...prev,
      fields: prev.fields.map(field => 
        field.id === fieldId ? { ...field, ...updates } : field
      )
    }));
  }, []);

  const removeField = useCallback((fieldId: string) => {
    setEntityData(prev => ({
      ...prev,
      fields: prev.fields.filter(field => field.id !== fieldId)
    }));
    setEditingField(null);
  }, []);

  // Validation
  const validateEntity = useCallback((): Record<string, string[]> => {
    const errors: Record<string, string[]> = {};
    
    if (!entityData.name.trim()) {
      errors.entity = ['Entity name is required'];
    }
    
    entityData.fields.forEach(field => {
      const fieldErrors: string[] = [];
      if (!field.name.trim()) {
        fieldErrors.push('Field name is required');
      }
      if (!field.title.trim()) {
        fieldErrors.push('Field title is required');
      }
      if (fieldErrors.length > 0) {
        errors[field.id] = fieldErrors;
      }
    });
    
    return errors;
  }, [entityData]);

  // Handle save
  const handleSave = useCallback(() => {
    const errors = validateEntity();
    setFieldErrors(errors);
    
    if (Object.keys(errors).length === 0) {
      onSave(entityData);
    }
  }, [entityData, validateEntity, onSave]);

  return (
    <div className="advanced-entity-builder">
      <div className="builder-header">
        <div className="header-content">
          <div className="header-info">
            <h2 className="builder-title">
              {entity ? 'Edit Entity' : 'Create New Entity'}
            </h2>
            <p className="builder-subtitle">
              Design and configure your data structure
            </p>
          </div>
          <div className="header-actions">
            <button className="action-button secondary" onClick={onCancel}>
              <X size={16} />
              Cancel
            </button>
            <button className="action-button primary" onClick={handleSave}>
              <Save size={16} />
              Save Entity
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'basic' ? 'active' : ''}`}
            onClick={() => setActiveTab('basic')}
          >
            <Settings size={16} />
            Basic Info
          </button>
          <button 
            className={`tab-button ${activeTab === 'fields' ? 'active' : ''}`}
            onClick={() => setActiveTab('fields')}
          >
            <Type size={16} />
            Fields ({entityData.fields.length})
          </button>
        </div>
      </div>

      <div className="builder-content">
        {/* Basic Info Tab */}
        {activeTab === 'basic' && (
          <div className="tab-content">
            <div className="form-section">
              <h3 className="section-title">Entity Information</h3>
              
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">
                    Entity Name <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-input ${fieldErrors.entity ? 'error' : ''}`}
                    value={entityData.name}
                    onChange={(e) => setEntityData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter entity name"
                  />
                  {fieldErrors.entity && (
                    <div className="field-error">
                      {fieldErrors.entity.map((error, i) => (
                        <div key={i} className="error-message">
                          <AlertCircle size={14} />
                          {error}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Entity Type</label>
                  <select
                    className="form-select"
                    value={entityData.type}
                    onChange={(e) => setEntityData(prev => ({ 
                      ...prev, 
                      type: e.target.value as 'core' | 'lookup'
                    }))}
                  >
                    <option value="core">Core Entity</option>
                    <option value="lookup">Lookup Table</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-textarea"
                  value={entityData.description || ''}
                  onChange={(e) => setEntityData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe the purpose of this entity"
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Table Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={entityData.tableName || ''}
                  onChange={(e) => setEntityData(prev => ({ ...prev, tableName: e.target.value }))}
                  placeholder="Custom table name (optional)"
                />
              </div>
            </div>
          </div>
        )}

        {/* Fields Tab */}
        {activeTab === 'fields' && (
          <div className="tab-content">
            <div className="fields-section">
              <div className="section-header">
                <div className="header-left">
                  <h3 className="section-title">Entity Fields</h3>
                  <div className="field-statistics">
                    <span className="stat-item">
                      <span className="stat-value">{entityData.fields.length}</span> Total
                    </span>
                    <span className="stat-item">
                      <span className="stat-value">{entityData.fields.filter(f => f.required).length}</span> Required
                    </span>
                  </div>
                </div>
                
                <div className="section-actions">
                  <button 
                    className="add-field-button"
                    onClick={() => addField('string')}
                  >
                    <Plus size={16} />
                    Add Field
                  </button>
                </div>
              </div>

              <div className="fields-list">
                {entityData.fields.length === 0 ? (
                  <div className="empty-fields">
                    <div className="empty-icon">
                      <Type size={48} />
                    </div>
                    <h4>No fields yet</h4>
                    <p>Add fields to define your entity structure</p>
                    <button 
                      className="action-button primary"
                      onClick={() => addField('string')}
                    >
                      <Plus size={16} />
                      Add First Field
                    </button>
                  </div>
                ) : (
                  entityData.fields.map((field) => (
                    <FieldEditor
                      key={field.id}
                      field={field}
                      isEditing={editingField === field.id}
                      errors={fieldErrors[field.id] || []}
                      onUpdate={(updates) => updateField(field.id, updates)}
                      onEdit={() => setEditingField(editingField === field.id ? null : field.id)}
                      onRemove={() => removeField(field.id)}
                    />
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Field Editor Component
interface FieldEditorProps {
  field: Field;
  isEditing: boolean;
  errors: string[];
  onUpdate: (updates: Partial<Field>) => void;
  onEdit: () => void;
  onRemove: () => void;
}

const FieldEditor: React.FC<FieldEditorProps> = ({
  field,
  isEditing,
  errors,
  onUpdate,
  onEdit,
  onRemove
}) => {
  const fieldTypeInfo = FIELD_TYPES.find(t => t.value === field.type);

  return (
    <div className={`field-editor ${isEditing ? 'editing' : ''} ${errors.length > 0 ? 'has-errors' : ''}`}>
      <div className="field-header">
        <div className="field-drag-handle">
          <GripVertical size={16} />
        </div>
        
        <div className="field-info">
          <div className="field-type-badge">
            {fieldTypeInfo?.icon}
            {fieldTypeInfo?.label}
          </div>
          <div className="field-identity">
            {isEditing ? (
              <div className="field-name-inputs">
                <input
                  type="text"
                  className="field-name-input"
                  value={field.name}
                  onChange={(e) => onUpdate({ name: e.target.value })}
                  placeholder="Field name (database)"
                />
                <input
                  type="text"
                  className="field-title-input"
                  value={field.title}
                  onChange={(e) => onUpdate({ title: e.target.value })}
                  placeholder="Field title (display)"
                />
              </div>
            ) : (
              <span className="field-name">
                {field.title || field.name || 'Untitled Field'}
                {field.required && <span className="required-indicator">*</span>}
              </span>
            )}
          </div>
        </div>

        <div className="field-actions">
          <button className="field-action-btn" onClick={onEdit}>
            <Edit3 size={14} />
          </button>
          <button className="field-action-btn danger" onClick={onRemove}>
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {isEditing && (
        <div className="field-editor-content">
          <div className="field-settings">
            <div className="setting-row">
              <div className="setting-group">
                <label className="form-label">Field Type</label>
                <select
                  className="form-select"
                  value={field.type}
                  onChange={(e) => onUpdate({ type: e.target.value as FieldType })}
                >
                  {FIELD_TYPES.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="setting-group">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={field.required}
                    onChange={(e) => onUpdate({ required: e.target.checked })}
                  />
                  Required Field
                </label>
              </div>

              <div className="setting-group">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={field.unique}
                    onChange={(e) => onUpdate({ unique: e.target.checked })}
                  />
                  Unique Field
                </label>
              </div>
            </div>

            <div className="setting-row">
              <div className="setting-group">
                <label className="form-label">Default Value</label>
                <input
                  type="text"
                  className="form-input"
                  value={field.defaultValue || ''}
                  onChange={(e) => onUpdate({ defaultValue: e.target.value })}
                  placeholder="Default value (optional)"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {errors.length > 0 && (
        <div className="field-errors">
          {errors.map((error, i) => (
            <div key={i} className="error-message">
              <AlertCircle size={14} />
              {error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};