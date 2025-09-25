# 🎨 WEEK 3-6: UI ENHANCEMENT IMPLEMENTATION GUIDE
## Visual Template Builder Enhancement Plan

> **Priority 2 Implementation**: Enhance existing template UI components  
> **Timeline**: 4 weeks  
> **Prerequisites**: Week 1-2 validation complete, gaps documented  
> **Objective**: Transform basic forms into comprehensive visual template builder

---

## 📋 **WEEK 3: ENHANCED DOMAIN CONFIGURATION INTERFACE**

### **DAY 11: Domain Configuration Form Enhancement**

#### **Task 11.1: Analyze Existing DomainConfigForm**
```bash
cd frontend/src/components/TemplateBuilder

# Analyze existing component structure
cat DomainConfigForm.tsx | head -50

# Document current functionality
echo "Current DomainConfigForm Analysis:" > ../../../docs/validation_reports/domain-form-analysis.md
echo "- Props interface: $(grep -n "interface.*Props" DomainConfigForm.tsx)" >> ../../../docs/validation_reports/domain-form-analysis.md
echo "- State management: $(grep -n "useState\|useEffect" DomainConfigForm.tsx | wc -l) hooks" >> ../../../docs/validation_reports/domain-form-analysis.md
echo "- API integration: $(grep -n "templateApi\|api" DomainConfigForm.tsx | wc -l) calls" >> ../../../docs/validation_reports/domain-form-analysis.md
```

#### **Task 11.2: Enhanced Domain Metadata Form**
Create enhanced domain configuration with better validation and UX:

**File: `frontend/src/components/TemplateBuilder/EnhancedDomainConfigForm.tsx`**
```typescript
import React, { useState, useEffect } from 'react';
import { DomainConfig } from '../../types/template';
import { templateApi } from '../../services/templateApi';

interface EnhancedDomainConfigFormProps {
  initialConfig?: DomainConfig;
  onConfigChange: (config: DomainConfig) => void;
  onValidationChange: (isValid: boolean, errors: string[]) => void;
}

export const EnhancedDomainConfigForm: React.FC<EnhancedDomainConfigFormProps> = ({
  initialConfig,
  onConfigChange,
  onValidationChange
}) => {
  const [config, setConfig] = useState<DomainConfig>(
    initialConfig || {
      domain: {
        name: '',
        title: '',
        description: '',
        type: 'business',
        version: '1.0.0'
      },
      entities: [],
      workflows: []
    }
  );

  const [validation, setValidation] = useState({
    isValid: false,
    errors: [] as string[],
    warnings: [] as string[]
  });

  const [isValidating, setIsValidating] = useState(false);

  // Real-time validation
  useEffect(() => {
    const validateConfig = async () => {
      if (!config.domain.name.trim()) return;
      
      setIsValidating(true);
      try {
        const result = await templateApi.validateTemplate(config);
        setValidation({
          isValid: result.isValid,
          errors: result.errors || [],
          warnings: result.warnings || []
        });
        onValidationChange(result.isValid, result.errors || []);
      } catch (error) {
        console.error('Validation error:', error);
      } finally {
        setIsValidating(false);
      }
    };

    const debounceTimer = setTimeout(validateConfig, 500);
    return () => clearTimeout(debounceTimer);
  }, [config, onValidationChange]);

  // Enhanced form fields with better UX
  return (
    <div className="enhanced-domain-config-form">
      <div className="form-section">
        <h3>Domain Information</h3>
        
        {/* Domain Name with availability check */}
        <div className="form-field">
          <label>Domain Name *</label>
          <input
            type="text"
            value={config.domain.name}
            onChange={(e) => {
              const newConfig = {
                ...config,
                domain: { ...config.domain, name: e.target.value }
              };
              setConfig(newConfig);
              onConfigChange(newConfig);
            }}
            placeholder="e.g., real_estate_management"
            className={validation.errors.some(e => e.includes('name')) ? 'error' : ''}
          />
          {isValidating && <span className="validating">Checking availability...</span>}
        </div>

        {/* Domain Title */}
        <div className="form-field">
          <label>Display Title *</label>
          <input
            type="text"
            value={config.domain.title}
            onChange={(e) => {
              const newConfig = {
                ...config,
                domain: { ...config.domain, title: e.target.value }
              };
              setConfig(newConfig);
              onConfigChange(newConfig);
            }}
            placeholder="e.g., Real Estate Management System"
          />
        </div>

        {/* Domain Description with character count */}
        <div className="form-field">
          <label>Description</label>
          <textarea
            value={config.domain.description}
            onChange={(e) => {
              const newConfig = {
                ...config,
                domain: { ...config.domain, description: e.target.value }
              };
              setConfig(newConfig);
              onConfigChange(newConfig);
            }}
            placeholder="Describe what this system will manage..."
            rows={3}
          />
          <span className="character-count">{config.domain.description?.length || 0}/500</span>
        </div>

        {/* Domain Type Selection */}
        <div className="form-field">
          <label>Domain Type</label>
          <select
            value={config.domain.type}
            onChange={(e) => {
              const newConfig = {
                ...config,
                domain: { ...config.domain, type: e.target.value }
              };
              setConfig(newConfig);
              onConfigChange(newConfig);
            }}
          >
            <option value="business">Business Management</option>
            <option value="ecommerce">E-commerce</option>
            <option value="healthcare">Healthcare</option>
            <option value="education">Education</option>
            <option value="real_estate">Real Estate</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      {/* Validation Results */}
      {validation.errors.length > 0 && (
        <div className="validation-errors">
          <h4>Configuration Errors:</h4>
          <ul>
            {validation.errors.map((error, index) => (
              <li key={index} className="error">{error}</li>
            ))}
          </ul>
        </div>
      )}

      {validation.warnings.length > 0 && (
        <div className="validation-warnings">
          <h4>Recommendations:</h4>
          <ul>
            {validation.warnings.map((warning, index) => (
              <li key={index} className="warning">{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
```

#### **Task 11.3: Form Styling and UX Enhancement**
**File: `frontend/src/components/TemplateBuilder/EnhancedDomainConfigForm.css`**
```css
.enhanced-domain-config-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
}

.form-section h3 {
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.form-field {
  margin-bottom: 1.5rem;
  position: relative;
}

.form-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-field input,
.form-field textarea,
.form-field select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-field input:focus,
.form-field textarea:focus,
.form-field select:focus {
  outline: none;
  border-color: #007bff;
}

.form-field input.error {
  border-color: #dc3545;
  background-color: #fff5f5;
}

.validating {
  position: absolute;
  right: 10px;
  top: 35px;
  color: #6c757d;
  font-size: 0.875rem;
}

.character-count {
  position: absolute;
  right: 10px;
  bottom: 10px;
  font-size: 0.75rem;
  color: #6c757d;
}

.validation-errors,
.validation-warnings {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
}

.validation-errors {
  background-color: #fff5f5;
  border: 1px solid #fed7d7;
}

.validation-warnings {
  background-color: #fffbeb;
  border: 1px solid #fbd38d;
}

.validation-errors h4 {
  color: #c53030;
  margin-bottom: 0.5rem;
}

.validation-warnings h4 {
  color: #c05621;
  margin-bottom: 0.5rem;
}

.validation-errors ul,
.validation-warnings ul {
  margin: 0;
  padding-left: 1.5rem;
}

.validation-errors li {
  color: #e53e3e;
}

.validation-warnings li {
  color: #c05621;
}
```

**Implementation Timeline: Day 11**
- Morning: Analyze existing form component
- Afternoon: Implement enhanced form with validation
- Evening: Add styling and UX improvements

---

### **DAY 12: Entity Management Interface**

#### **Task 12.1: Entity List Management**
**File: `frontend/src/components/TemplateBuilder/EntityManager.tsx`**
```typescript
import React, { useState, useEffect } from 'react';
import { Entity, Relationship } from '../../types/template';

interface EntityManagerProps {
  entities: Entity[];
  relationships: Relationship[];
  onEntitiesChange: (entities: Entity[]) => void;
  onRelationshipsChange: (relationships: Relationship[]) => void;
}

export const EntityManager: React.FC<EntityManagerProps> = ({
  entities,
  relationships,
  onEntitiesChange,
  onRelationshipsChange
}) => {
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [showAddEntity, setShowAddEntity] = useState(false);

  const addEntity = (entityData: Partial<Entity>) => {
    const newEntity: Entity = {
      id: `entity_${Date.now()}`,
      name: entityData.name || '',
      fields: entityData.fields || [],
      relationships: entityData.relationships || [],
      permissions: entityData.permissions || { create: true, read: true, update: true, delete: true }
    };
    
    onEntitiesChange([...entities, newEntity]);
  };

  const updateEntity = (entityId: string, updates: Partial<Entity>) => {
    const updatedEntities = entities.map(entity =>
      entity.id === entityId ? { ...entity, ...updates } : entity
    );
    onEntitiesChange(updatedEntities);
  };

  const deleteEntity = (entityId: string) => {
    // Remove entity
    const filteredEntities = entities.filter(e => e.id !== entityId);
    onEntitiesChange(filteredEntities);

    // Remove related relationships
    const filteredRelationships = relationships.filter(
      r => r.fromEntity !== entityId && r.toEntity !== entityId
    );
    onRelationshipsChange(filteredRelationships);
  };

  return (
    <div className="entity-manager">
      <div className="entity-manager-header">
        <h3>Entities ({entities.length})</h3>
        <button
          className="btn btn-primary"
          onClick={() => setShowAddEntity(true)}
        >
          + Add Entity
        </button>
      </div>

      <div className="entity-list">
        {entities.map(entity => (
          <div
            key={entity.id}
            className={`entity-card ${selectedEntity === entity.id ? 'selected' : ''}`}
            onClick={() => setSelectedEntity(entity.id)}
          >
            <div className="entity-header">
              <h4>{entity.name}</h4>
              <div className="entity-actions">
                <button onClick={(e) => {
                  e.stopPropagation();
                  // Edit entity logic
                }}>Edit</button>
                <button onClick={(e) => {
                  e.stopPropagation();
                  deleteEntity(entity.id);
                }}>Delete</button>
              </div>
            </div>
            
            <div className="entity-details">
              <span className="field-count">{entity.fields.length} fields</span>
              <span className="relationship-count">
                {entity.relationships?.length || 0} relationships
              </span>
            </div>
            
            {entity.fields.slice(0, 3).map(field => (
              <div key={field.name} className="field-preview">
                <span className="field-name">{field.name}</span>
                <span className="field-type">{field.type}</span>
              </div>
            ))}
            
            {entity.fields.length > 3 && (
              <div className="field-preview more">
                +{entity.fields.length - 3} more fields
              </div>
            )}
          </div>
        ))}
      </div>

      {showAddEntity && (
        <EntityEditor
          entity={null}
          onSave={addEntity}
          onCancel={() => setShowAddEntity(false)}
        />
      )}

      {selectedEntity && (
        <EntityDetailPanel
          entity={entities.find(e => e.id === selectedEntity)!}
          onUpdate={(updates) => updateEntity(selectedEntity, updates)}
          onClose={() => setSelectedEntity(null)}
        />
      )}
    </div>
  );
};
```

#### **Task 12.2: Entity Editor Modal**
**File: `frontend/src/components/TemplateBuilder/EntityEditor.tsx`**
```typescript
import React, { useState, useEffect } from 'react';
import { Entity, Field } from '../../types/template';

interface EntityEditorProps {
  entity: Entity | null; // null for new entity
  onSave: (entity: Partial<Entity>) => void;
  onCancel: () => void;
}

export const EntityEditor: React.FC<EntityEditorProps> = ({
  entity,
  onSave,
  onCancel
}) => {
  const [entityData, setEntityData] = useState<Partial<Entity>>({
    name: entity?.name || '',
    fields: entity?.fields || [],
    permissions: entity?.permissions || {
      create: true,
      read: true,
      update: true,
      delete: true
    }
  });

  const [showAddField, setShowAddField] = useState(false);

  const addField = (fieldData: Field) => {
    const updatedFields = [...(entityData.fields || []), fieldData];
    setEntityData({ ...entityData, fields: updatedFields });
  };

  const updateField = (index: number, updates: Partial<Field>) => {
    const updatedFields = (entityData.fields || []).map((field, i) =>
      i === index ? { ...field, ...updates } : field
    );
    setEntityData({ ...entityData, fields: updatedFields });
  };

  const deleteField = (index: number) => {
    const updatedFields = (entityData.fields || []).filter((_, i) => i !== index);
    setEntityData({ ...entityData, fields: updatedFields });
  };

  const fieldTypes = [
    'string', 'integer', 'decimal', 'boolean', 'date', 'datetime',
    'text', 'email', 'url', 'json', 'uuid', 'file'
  ];

  return (
    <div className="modal-overlay">
      <div className="modal-content entity-editor-modal">
        <div className="modal-header">
          <h3>{entity ? 'Edit Entity' : 'Create New Entity'}</h3>
          <button className="close-btn" onClick={onCancel}>×</button>
        </div>

        <div className="modal-body">
          <div className="form-section">
            <label>Entity Name *</label>
            <input
              type="text"
              value={entityData.name}
              onChange={(e) => setEntityData({ ...entityData, name: e.target.value })}
              placeholder="e.g., Property, User, Order"
            />
          </div>

          <div className="form-section">
            <div className="section-header">
              <h4>Fields ({entityData.fields?.length || 0})</h4>
              <button
                className="btn btn-secondary"
                onClick={() => setShowAddField(true)}
              >
                + Add Field
              </button>
            </div>

            <div className="fields-list">
              {(entityData.fields || []).map((field, index) => (
                <div key={index} className="field-item">
                  <div className="field-info">
                    <span className="field-name">{field.name}</span>
                    <span className="field-type">{field.type}</span>
                    {field.required && <span className="required-badge">Required</span>}
                  </div>
                  <div className="field-actions">
                    <button onClick={() => {/* Edit field logic */}}>Edit</button>
                    <button onClick={() => deleteField(index)}>Delete</button>
                  </div>
                </div>
              ))}
            </div>

            {showAddField && (
              <FieldEditor
                field={null}
                onSave={(fieldData) => {
                  addField(fieldData);
                  setShowAddField(false);
                }}
                onCancel={() => setShowAddField(false)}
              />
            )}
          </div>

          <div className="form-section">
            <h4>Permissions</h4>
            <div className="permissions-grid">
              {Object.entries(entityData.permissions || {}).map(([permission, enabled]) => (
                <label key={permission} className="permission-checkbox">
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(e) => setEntityData({
                      ...entityData,
                      permissions: {
                        ...entityData.permissions,
                        [permission]: e.target.checked
                      }
                    })}
                  />
                  {permission.charAt(0).toUpperCase() + permission.slice(1)}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={() => onSave(entityData)}
            disabled={!entityData.name?.trim()}
          >
            {entity ? 'Update Entity' : 'Create Entity'}
          </button>
        </div>
      </div>
    </div>
  );
};
```

**Implementation Timeline: Day 12**
- Morning: Build entity list management interface
- Afternoon: Create entity editor modal with field management
- Evening: Add entity validation and permissions UI

---

### **DAY 13: Field Configuration Interface**

#### **Task 13.1: Field Editor Component**
**File: `frontend/src/components/TemplateBuilder/FieldEditor.tsx`**
```typescript
import React, { useState } from 'react';
import { Field } from '../../types/template';

interface FieldEditorProps {
  field: Field | null; // null for new field
  onSave: (field: Field) => void;
  onCancel: () => void;
}

export const FieldEditor: React.FC<FieldEditorProps> = ({
  field,
  onSave,
  onCancel
}) => {
  const [fieldData, setFieldData] = useState<Field>({
    name: field?.name || '',
    type: field?.type || 'string',
    required: field?.required || false,
    unique: field?.unique || false,
    defaultValue: field?.defaultValue || '',
    validation: field?.validation || {},
    description: field?.description || ''
  });

  const fieldTypes = [
    { value: 'string', label: 'Text (String)', description: 'Short text field' },
    { value: 'text', label: 'Long Text', description: 'Multi-line text field' },
    { value: 'integer', label: 'Integer', description: 'Whole number' },
    { value: 'decimal', label: 'Decimal', description: 'Decimal number' },
    { value: 'boolean', label: 'Boolean', description: 'True/false value' },
    { value: 'date', label: 'Date', description: 'Date only' },
    { value: 'datetime', label: 'Date & Time', description: 'Date and time' },
    { value: 'email', label: 'Email', description: 'Email address' },
    { value: 'url', label: 'URL', description: 'Web address' },
    { value: 'json', label: 'JSON', description: 'Structured data' },
    { value: 'uuid', label: 'UUID', description: 'Unique identifier' },
    { value: 'file', label: 'File', description: 'File upload' }
  ];

  const handleValidationChange = (key: string, value: any) => {
    setFieldData({
      ...fieldData,
      validation: {
        ...fieldData.validation,
        [key]: value
      }
    });
  };

  const getValidationOptionsForType = (type: string) => {
    switch (type) {
      case 'string':
      case 'text':
        return (
          <div className="validation-options">
            <div className="validation-field">
              <label>Minimum Length</label>
              <input
                type="number"
                value={fieldData.validation?.minLength || ''}
                onChange={(e) => handleValidationChange('minLength', parseInt(e.target.value))}
              />
            </div>
            <div className="validation-field">
              <label>Maximum Length</label>
              <input
                type="number"
                value={fieldData.validation?.maxLength || ''}
                onChange={(e) => handleValidationChange('maxLength', parseInt(e.target.value))}
              />
            </div>
            <div className="validation-field">
              <label>Pattern (Regex)</label>
              <input
                type="text"
                value={fieldData.validation?.pattern || ''}
                onChange={(e) => handleValidationChange('pattern', e.target.value)}
                placeholder="^[A-Za-z]+$"
              />
            </div>
          </div>
        );
      
      case 'integer':
      case 'decimal':
        return (
          <div className="validation-options">
            <div className="validation-field">
              <label>Minimum Value</label>
              <input
                type="number"
                step={type === 'decimal' ? '0.01' : '1'}
                value={fieldData.validation?.min || ''}
                onChange={(e) => handleValidationChange('min', parseFloat(e.target.value))}
              />
            </div>
            <div className="validation-field">
              <label>Maximum Value</label>
              <input
                type="number"
                step={type === 'decimal' ? '0.01' : '1'}
                value={fieldData.validation?.max || ''}
                onChange={(e) => handleValidationChange('max', parseFloat(e.target.value))}
              />
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="field-editor">
      <div className="field-editor-header">
        <h4>{field ? 'Edit Field' : 'Add New Field'}</h4>
      </div>

      <div className="field-editor-body">
        <div className="form-grid">
          <div className="form-field">
            <label>Field Name *</label>
            <input
              type="text"
              value={fieldData.name}
              onChange={(e) => setFieldData({ ...fieldData, name: e.target.value })}
              placeholder="e.g., title, price, email"
            />
          </div>

          <div className="form-field">
            <label>Field Type *</label>
            <select
              value={fieldData.type}
              onChange={(e) => setFieldData({ ...fieldData, type: e.target.value as any })}
            >
              {fieldTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            <small className="field-description">
              {fieldTypes.find(t => t.value === fieldData.type)?.description}
            </small>
          </div>

          <div className="form-field full-width">
            <label>Description</label>
            <textarea
              value={fieldData.description}
              onChange={(e) => setFieldData({ ...fieldData, description: e.target.value })}
              placeholder="Describe the purpose of this field..."
              rows={2}
            />
          </div>

          <div className="form-field">
            <label>Default Value</label>
            <input
              type="text"
              value={fieldData.defaultValue}
              onChange={(e) => setFieldData({ ...fieldData, defaultValue: e.target.value })}
              placeholder="Optional default value"
            />
          </div>

          <div className="form-field">
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={fieldData.required}
                  onChange={(e) => setFieldData({ ...fieldData, required: e.target.checked })}
                />
                Required Field
              </label>
              
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={fieldData.unique}
                  onChange={(e) => setFieldData({ ...fieldData, unique: e.target.checked })}
                />
                Unique Value
              </label>
            </div>
          </div>
        </div>

        <div className="validation-section">
          <h5>Validation Rules</h5>
          {getValidationOptionsForType(fieldData.type)}
        </div>
      </div>

      <div className="field-editor-footer">
        <button className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button
          className="btn btn-primary"
          onClick={() => onSave(fieldData)}
          disabled={!fieldData.name.trim()}
        >
          {field ? 'Update Field' : 'Add Field'}
        </button>
      </div>
    </div>
  );
};
```

**Implementation Timeline: Day 13**
- Morning: Build comprehensive field editor with type-specific validation
- Afternoon: Add field validation options and rules
- Evening: Test field creation and editing workflows

---

### **DAY 14: Integration and Testing**

#### **Task 14.1: Component Integration Testing**
```bash
cd frontend

# Test component integration
npm run test -- --testPathPattern=TemplateBuilder

# Manual testing checklist:
echo "Integration Testing Checklist:" > integration-test-results.md
echo "- [ ] EnhancedDomainConfigForm renders without errors" >> integration-test-results.md
echo "- [ ] Real-time validation works" >> integration-test-results.md  
echo "- [ ] EntityManager creates and manages entities" >> integration-test-results.md
echo "- [ ] FieldEditor handles all field types correctly" >> integration-test-results.md
echo "- [ ] Form data persists across component interactions" >> integration-test-results.md
```

#### **Task 14.2: Backend Integration Testing**
Test enhanced UI components with existing backend APIs:

```bash
# Start backend server
cd backend
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend server  
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for servers to start
sleep 10

# Test API integration
curl -X POST http://localhost:8000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "domain": {
      "name": "test_domain",
      "title": "Test Domain",
      "description": "Integration test domain"
    },
    "entities": [
      {
        "name": "TestEntity",
        "fields": [
          {"name": "title", "type": "string", "required": true}
        ]
      }
    ]
  }' && echo "✅ Template creation API works" || echo "❌ Template creation API failed"

# Clean up
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
```

**Deliverable: `WEEK-3-UI-ENHANCEMENT-RESULTS.md`**

---

## 📋 **WEEK 4: VISUAL RELATIONSHIP DESIGNER**

### **DAY 15-16: Entity Relationship Canvas**

#### **Task 15.1: Visual Canvas Component**
**File: `frontend/src/components/TemplateBuilder/EntityCanvas.tsx`**

**Implementation Focus:**
- Drag-and-drop entity positioning
- Visual relationship lines between entities
- Entity cards with field previews
- Zoom and pan functionality
- Relationship creation via drag-and-drop

### **DAY 17-18: Relationship Management**

#### **Task 17.1: Relationship Designer**
**File: `frontend/src/components/TemplateBuilder/RelationshipDesigner.tsx`**

**Implementation Focus:**
- One-to-one, one-to-many, many-to-many relationships
- Foreign key configuration
- Cascade delete options
- Relationship validation

### **DAY 19: Live Configuration Preview**

#### **Task 19.1: Configuration Preview Panel**
**File: `frontend/src/components/TemplateBuilder/ConfigPreview.tsx`**

**Implementation Focus:**
- Live YAML generation from UI state
- Syntax highlighting
- Export functionality
- Configuration validation display

---

## 📊 **WEEK 3-6 SUCCESS CRITERIA**

### **Week 3: Enhanced Forms ✅**
- [ ] Enhanced domain configuration with real-time validation
- [ ] Complete entity management interface
- [ ] Comprehensive field editor with type-specific options
- [ ] Backend API integration working

### **Week 4: Visual Designer ✅**
- [ ] Drag-and-drop entity canvas
- [ ] Visual relationship designer
- [ ] Live configuration preview
- [ ] Export and import functionality

### **Week 5-6: Polish and Integration ✅**
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Comprehensive testing
- [ ] User experience refinement

---

## 📋 **DELIVERABLES**

By end of Week 6, we'll have:

1. **Enhanced Template Builder UI** - Professional, intuitive interface
2. **Visual Entity Modeling** - Drag-and-drop entity relationship design
3. **Comprehensive Field Management** - All field types with validation
4. **Live Configuration Preview** - Real-time YAML generation
5. **Backend Integration** - Full API connectivity
6. **Responsive Design** - Works on all device sizes
7. **User Experience Polish** - Professional UX/UI standards

This UI enhancement plan transforms existing basic forms into a comprehensive visual template builder that rivals commercial low-code platforms. 🎨

---

*Next: Week 7-10 Advanced Features Implementation Plan (to be created after UI enhancement complete)*