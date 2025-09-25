import React, { useState, useRef, useCallback } from 'react';
import {
  Plus, Save, Trash2, Edit3, Copy, Link2, Settings,
  Database, Type, Hash, Calendar, FileText,
  Image, Mail, ExternalLink, Upload, Code, Search,
  Zap, Shield, Check, X
} from 'lucide-react';
import './VisualEntityDesigner.css';

interface EntityField {
  id: string;
  name: string;
  displayName: string;
  type: 'string' | 'text' | 'integer' | 'decimal' | 'boolean' | 'date' | 'datetime' | 'email' | 'url' | 'json' | 'file' | 'image';
  required: boolean;
  unique: boolean;
  indexed: boolean;
  defaultValue?: string;
  validation: {
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    minValue?: number;
    maxValue?: number;
    allowedValues?: string[];
  };
  uiConfig: {
    widget: string;
    placeholder?: string;
    helpText?: string;
    showInList: boolean;
    showInDetail: boolean;
    editable: boolean;
    searchable: boolean;
    sortable: boolean;
  };
}

interface EntityRelationship {
  id: string;
  type: 'one_to_one' | 'one_to_many' | 'many_to_many';
  fromEntity: string;
  toEntity: string;
  name: string;
  reverseName: string;
  cascadeDelete: boolean;
  required: boolean;
}

interface EntityDesign {
  id: string;
  name: string;
  displayName: string;
  description: string;
  icon: string;
  color: string;
  fields: EntityField[];
  relationships: EntityRelationship[];
  permissions: {
    role: string;
    actions: ('create' | 'read' | 'update' | 'delete')[];
  }[];
  uiConfig: {
    listView: boolean;
    detailView: boolean;
    createForm: boolean;
    editForm: boolean;
    bulkActions: string[];
  };
  position: { x: number; y: number };
  size: { width: number; height: number };
}

interface VisualEntityDesignerProps {
  entities?: EntityDesign[];
  onEntitiesChange?: (entities: EntityDesign[]) => void;
  readonly?: boolean;
}

export const VisualEntityDesigner: React.FC<VisualEntityDesignerProps> = ({
  entities = [],
  onEntitiesChange,
  readonly = false
}) => {
  const [designEntities, setDesignEntities] = useState<EntityDesign[]>(entities);
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [showFieldDialog, setShowFieldDialog] = useState(false);
  const [editingField, setEditingField] = useState<EntityField | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'design' | 'code'>('design');
  const canvasRef = useRef<HTMLDivElement>(null);

  const fieldTypeIcons = {
    string: Type,
    text: FileText,
    integer: Hash,
    decimal: Hash,
    boolean: Check,
    date: Calendar,
    datetime: Calendar,
    email: Mail,
    url: ExternalLink,
    json: Code,
    file: Upload,
    image: Image
  };

  const createNewEntity = useCallback(() => {
    if (readonly) return;

    const newEntity: EntityDesign = {
      id: `entity_${Date.now()}`,
      name: `entity_${designEntities.length + 1}`,
      displayName: `Entity ${designEntities.length + 1}`,
      description: '',
      icon: 'Database',
      color: '#3b82f6',
      fields: [
        {
          id: 'id',
          name: 'id',
          displayName: 'ID',
          type: 'string',
          required: true,
          unique: true,
          indexed: true,
          validation: {},
          uiConfig: {
            widget: 'text',
            showInList: true,
            showInDetail: true,
            editable: false,
            searchable: false,
            sortable: true
          }
        },
        {
          id: 'created_at',
          name: 'created_at',
          displayName: 'Created At',
          type: 'datetime',
          required: true,
          unique: false,
          indexed: true,
          validation: {},
          uiConfig: {
            widget: 'datetime',
            showInList: true,
            showInDetail: true,
            editable: false,
            searchable: false,
            sortable: true
          }
        }
      ],
      relationships: [],
      permissions: [
        { role: 'admin', actions: ['create', 'read', 'update', 'delete'] },
        { role: 'user', actions: ['read'] }
      ],
      uiConfig: {
        listView: true,
        detailView: true,
        createForm: true,
        editForm: true,
        bulkActions: ['delete', 'export']
      },
      position: { x: 100 + designEntities.length * 50, y: 100 + designEntities.length * 50 },
      size: { width: 250, height: 200 }
    };

    const updatedEntities = [...designEntities, newEntity];
    setDesignEntities(updatedEntities);
    setSelectedEntity(newEntity.id);
    
    if (onEntitiesChange) {
      onEntitiesChange(updatedEntities);
    }
  }, [designEntities, readonly, onEntitiesChange]);

  const updateEntity = useCallback((entityId: string, updates: Partial<EntityDesign>) => {
    if (readonly) return;

    const updatedEntities = designEntities.map(entity =>
      entity.id === entityId ? { ...entity, ...updates } : entity
    );
    setDesignEntities(updatedEntities);
    
    if (onEntitiesChange) {
      onEntitiesChange(updatedEntities);
    }
  }, [designEntities, readonly, onEntitiesChange]);

  const deleteEntity = useCallback((entityId: string) => {
    if (readonly) return;

    const updatedEntities = designEntities.filter(entity => entity.id !== entityId);
    setDesignEntities(updatedEntities);
    setSelectedEntity(null);
    
    if (onEntitiesChange) {
      onEntitiesChange(updatedEntities);
    }
  }, [designEntities, readonly, onEntitiesChange]);

  const addField = useCallback((entityId: string, field: EntityField) => {
    if (readonly) return;

    updateEntity(entityId, {
      fields: [...(designEntities.find(e => e.id === entityId)?.fields || []), field]
    });
  }, [designEntities, updateEntity, readonly]);

  const updateField = useCallback((entityId: string, fieldId: string, updates: Partial<EntityField>) => {
    if (readonly) return;

    const entity = designEntities.find(e => e.id === entityId);
    if (!entity) return;

    const updatedFields = entity.fields.map(field =>
      field.id === fieldId ? { ...field, ...updates } : field
    );

    updateEntity(entityId, { fields: updatedFields });
  }, [designEntities, updateEntity, readonly]);

  const deleteField = useCallback((entityId: string, fieldId: string) => {
    if (readonly) return;

    const entity = designEntities.find(e => e.id === entityId);
    if (!entity) return;

    const updatedFields = entity.fields.filter(field => field.id !== fieldId);
    updateEntity(entityId, { fields: updatedFields });
  }, [designEntities, updateEntity, readonly]);

  const handleMouseDown = useCallback((e: React.MouseEvent, entityId: string) => {
    if (readonly) return;

    e.preventDefault();
    const entity = designEntities.find(e => e.id === entityId);
    if (!entity) return;

    setIsDragging(entityId);
    setDragOffset({
      x: e.clientX - entity.position.x,
      y: e.clientY - entity.position.y
    });
  }, [designEntities, readonly]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging || readonly) return;

    e.preventDefault();
    const newPosition = {
      x: Math.max(0, e.clientX - dragOffset.x),
      y: Math.max(0, e.clientY - dragOffset.y)
    };

    updateEntity(isDragging, { position: newPosition });
  }, [isDragging, dragOffset, updateEntity, readonly]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(null);
    setDragOffset({ x: 0, y: 0 });
  }, []);

  const handleFieldSubmit = useCallback(() => {
    if (!editingField || !selectedEntity) return;

    if (editingField.id.startsWith('new_')) {
      const newField: EntityField = {
        ...editingField,
        id: `field_${Date.now()}`
      };
      addField(selectedEntity, newField);
    } else {
      updateField(selectedEntity, editingField.id, editingField);
    }

    setEditingField(null);
    setShowFieldDialog(false);
  }, [editingField, selectedEntity, addField, updateField]);

  const openFieldDialog = useCallback((entityId: string, field?: EntityField) => {
    setSelectedEntity(entityId);
    setEditingField(field || {
      id: `new_${Date.now()}`,
      name: '',
      displayName: '',
      type: 'string',
      required: false,
      unique: false,
      indexed: false,
      validation: {},
      uiConfig: {
        widget: 'text',
        showInList: true,
        showInDetail: true,
        editable: true,
        searchable: true,
        sortable: true
      }
    });
    setShowFieldDialog(true);
  }, []);

  const generateEntityCode = useCallback((entity: EntityDesign) => {
    const fieldDefinitions = entity.fields.map(field => {
      const typeMap = {
        string: 'String',
        text: 'Text',
        integer: 'Integer',
        decimal: 'Decimal',
        boolean: 'Boolean',
        date: 'Date',
        datetime: 'DateTime',
        email: 'String',
        url: 'String',
        json: 'JSON',
        file: 'String',
        image: 'String'
      };

      const constraints = [];
      if (field.required) constraints.push('nullable=False');
      if (field.unique) constraints.push('unique=True');
      if (field.indexed) constraints.push('index=True');
      if (field.defaultValue) constraints.push(`default="${field.defaultValue}"`);

      const constraintStr = constraints.length > 0 ? `, ${constraints.join(', ')}` : '';
      
      return `    ${field.name} = db.Column(db.${typeMap[field.type]}${constraintStr})`;
    }).join('\n');

    return `class ${entity.displayName.replace(/\s+/g, '')}(BaseModel):
    """${entity.description || entity.displayName}"""
    __tablename__ = '${entity.name}'

${fieldDefinitions}

    def __repr__(self):
        return f"<${entity.displayName.replace(/\s+/g, '')} {id=}>"`;
  }, []);

  const filteredEntities = designEntities.filter(entity =>
    entity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entity.displayName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entity.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedEntityData = selectedEntity ? designEntities.find(e => e.id === selectedEntity) : null;

  return (
    <div className="visual-entity-designer">
      <div className="designer-toolbar">
        <div className="toolbar-section">
          <button
            className="toolbar-btn primary"
            onClick={createNewEntity}
            disabled={readonly}
          >
            <Plus size={16} />
            Add Entity
          </button>
          
          <button className="toolbar-btn" disabled={readonly}>
            <Link2 size={16} />
            Add Relationship
          </button>
          
          <div className="toolbar-divider" />
          
          <button className="toolbar-btn" disabled={readonly}>
            <Save size={16} />
            Save
          </button>
          
          <button className="toolbar-btn" disabled={readonly}>
            <Copy size={16} />
            Copy
          </button>
        </div>

        <div className="toolbar-section">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search entities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="toolbar-section">
          <div className="view-toggle">
            <button
              className={`toggle-btn ${viewMode === 'design' ? 'active' : ''}`}
              onClick={() => setViewMode('design')}
            >
              <Database size={16} />
              Design
            </button>
            <button
              className={`toggle-btn ${viewMode === 'code' ? 'active' : ''}`}
              onClick={() => setViewMode('code')}
            >
              <Code size={16} />
              Code
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'design' ? (
        <div className="designer-workspace">
          <div
            ref={canvasRef}
            className="entity-canvas"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            {filteredEntities.map(entity => (
              <div
                key={entity.id}
                className={`entity-box ${selectedEntity === entity.id ? 'selected' : ''} ${isDragging === entity.id ? 'dragging' : ''}`}
                style={{
                  left: entity.position.x,
                  top: entity.position.y,
                  width: entity.size.width,
                  minHeight: entity.size.height,
                  borderColor: entity.color
                }}
                onClick={() => setSelectedEntity(entity.id)}
              >
                <div
                  className="entity-header"
                  onMouseDown={(e) => handleMouseDown(e, entity.id)}
                  style={{ backgroundColor: entity.color }}
                >
                  <div className="entity-info">
                    <Database size={16} />
                    <span className="entity-name">{entity.displayName}</span>
                  </div>
                  <div className="entity-actions">
                    <button
                      className="entity-action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        openFieldDialog(entity.id);
                      }}
                      disabled={readonly}
                    >
                      <Plus size={12} />
                    </button>
                    <button
                      className="entity-action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Open entity settings
                      }}
                      disabled={readonly}
                    >
                      <Settings size={12} />
                    </button>
                    <button
                      className="entity-action-btn delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteEntity(entity.id);
                      }}
                      disabled={readonly}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>

                <div className="entity-content">
                  <div className="field-list">
                    {entity.fields.slice(0, 5).map(field => {
                      const FieldIcon = fieldTypeIcons[field.type];
                      return (
                        <div
                          key={field.id}
                          className={`field-item ${selectedField === field.id ? 'selected' : ''}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedField(field.id);
                          }}
                          onDoubleClick={(e) => {
                            e.stopPropagation();
                            if (!readonly) openFieldDialog(entity.id, field);
                          }}
                        >
                          <div className="field-info">
                            <FieldIcon size={12} />
                            <span className="field-name">{field.displayName}</span>
                            <span className="field-type">{field.type}</span>
                          </div>
                          <div className="field-constraints">
                            {field.required && <div className="constraint required" data-tooltip="Required"><Check size={10} /></div>}
                            {field.unique && <div className="constraint unique" data-tooltip="Unique"><Shield size={10} /></div>}
                            {field.indexed && <div className="constraint indexed" data-tooltip="Indexed"><Zap size={10} /></div>}
                          </div>
                        </div>
                      );
                    })}
                    {entity.fields.length > 5 && (
                      <div className="field-item more">
                        <span>+{entity.fields.length - 5} more fields</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Relationship lines would be rendered here */}
          </div>

          {selectedEntityData && (
            <div className="entity-inspector">
              <div className="inspector-header">
                <h3>Entity Properties</h3>
                <button
                  className="close-btn"
                  onClick={() => setSelectedEntity(null)}
                >
                  <X size={16} />
                </button>
              </div>

              <div className="inspector-content">
                <div className="property-section">
                  <h4>Basic Information</h4>
                  <div className="property-grid">
                    <div className="property-field">
                      <label>Name</label>
                      <input
                        type="text"
                        value={selectedEntityData.name}
                        onChange={(e) => updateEntity(selectedEntity!, { name: e.target.value })}
                        disabled={readonly}
                      />
                    </div>
                    <div className="property-field">
                      <label>Display Name</label>
                      <input
                        type="text"
                        value={selectedEntityData.displayName}
                        onChange={(e) => updateEntity(selectedEntity!, { displayName: e.target.value })}
                        disabled={readonly}
                      />
                    </div>
                    <div className="property-field full-width">
                      <label>Description</label>
                      <textarea
                        value={selectedEntityData.description}
                        onChange={(e) => updateEntity(selectedEntity!, { description: e.target.value })}
                        disabled={readonly}
                        rows={2}
                      />
                    </div>
                    <div className="property-field">
                      <label>Color</label>
                      <input
                        type="color"
                        value={selectedEntityData.color}
                        onChange={(e) => updateEntity(selectedEntity!, { color: e.target.value })}
                        disabled={readonly}
                      />
                    </div>
                  </div>
                </div>

                <div className="property-section">
                  <h4>Fields ({selectedEntityData.fields.length})</h4>
                  <div className="field-list-detailed">
                    {selectedEntityData.fields.map(field => (
                      <div key={field.id} className="field-detail-item">
                        <div className="field-detail-header">
                          <div className="field-detail-info">
                            {React.createElement(fieldTypeIcons[field.type], { size: 14 })}
                            <span className="field-detail-name">{field.displayName}</span>
                            <span className="field-detail-type">{field.type}</span>
                          </div>
                          <div className="field-detail-actions">
                            <button
                              className="field-action-btn"
                              onClick={() => openFieldDialog(selectedEntity!, field)}
                              disabled={readonly}
                            >
                              <Edit3 size={12} />
                            </button>
                            <button
                              className="field-action-btn delete"
                              onClick={() => deleteField(selectedEntity!, field.id)}
                              disabled={readonly}
                            >
                              <Trash2 size={12} />
                            </button>
                          </div>
                        </div>
                        <div className="field-detail-constraints">
                          {field.required && <span className="constraint-badge required">Required</span>}
                          {field.unique && <span className="constraint-badge unique">Unique</span>}
                          {field.indexed && <span className="constraint-badge indexed">Indexed</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                  <button
                    className="add-field-btn"
                    onClick={() => openFieldDialog(selectedEntity!)}
                    disabled={readonly}
                  >
                    <Plus size={16} />
                    Add Field
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="code-view">
          <div className="code-tabs">
            {filteredEntities.map(entity => (
              <button
                key={entity.id}
                className={`code-tab ${selectedEntity === entity.id ? 'active' : ''}`}
                onClick={() => setSelectedEntity(entity.id)}
              >
                {entity.displayName}.py
              </button>
            ))}
          </div>
          {selectedEntityData && (
            <div className="code-editor">
              <pre className="code-content">
                <code>{generateEntityCode(selectedEntityData)}</code>
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Field Dialog */}
      {showFieldDialog && editingField && (
        <div className="modal-overlay">
          <div className="field-dialog">
            <div className="dialog-header">
              <h3>{editingField.id.startsWith('new_') ? 'Add New Field' : 'Edit Field'}</h3>
              <button
                className="close-btn"
                onClick={() => setShowFieldDialog(false)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="dialog-content">
              <div className="field-form">
                <div className="form-grid">
                  <div className="form-field">
                    <label>Field Name *</label>
                    <input
                      type="text"
                      value={editingField.name}
                      onChange={(e) => setEditingField({
                        ...editingField,
                        name: e.target.value,
                        displayName: editingField.displayName || e.target.value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                      })}
                      placeholder="e.g., first_name"
                    />
                  </div>

                  <div className="form-field">
                    <label>Display Name *</label>
                    <input
                      type="text"
                      value={editingField.displayName}
                      onChange={(e) => setEditingField({
                        ...editingField,
                        displayName: e.target.value
                      })}
                      placeholder="e.g., First Name"
                    />
                  </div>

                  <div className="form-field">
                    <label>Field Type *</label>
                    <select
                      value={editingField.type}
                      onChange={(e) => setEditingField({
                        ...editingField,
                        type: e.target.value as EntityField['type']
                      })}
                    >
                      <option value="string">String</option>
                      <option value="text">Text</option>
                      <option value="integer">Integer</option>
                      <option value="decimal">Decimal</option>
                      <option value="boolean">Boolean</option>
                      <option value="date">Date</option>
                      <option value="datetime">DateTime</option>
                      <option value="email">Email</option>
                      <option value="url">URL</option>
                      <option value="json">JSON</option>
                      <option value="file">File</option>
                      <option value="image">Image</option>
                    </select>
                  </div>

                  <div className="form-field">
                    <label>Default Value</label>
                    <input
                      type="text"
                      value={editingField.defaultValue || ''}
                      onChange={(e) => setEditingField({
                        ...editingField,
                        defaultValue: e.target.value
                      })}
                      placeholder="Optional default value"
                    />
                  </div>
                </div>

                <div className="field-constraints">
                  <h4>Constraints</h4>
                  <div className="constraint-checkboxes">
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.required}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          required: e.target.checked
                        })}
                      />
                      Required
                    </label>
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.unique}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          unique: e.target.checked
                        })}
                      />
                      Unique
                    </label>
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.indexed}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          indexed: e.target.checked
                        })}
                      />
                      Indexed
                    </label>
                  </div>
                </div>

                <div className="ui-configuration">
                  <h4>UI Configuration</h4>
                  <div className="ui-checkboxes">
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.uiConfig.showInList}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          uiConfig: {
                            ...editingField.uiConfig,
                            showInList: e.target.checked
                          }
                        })}
                      />
                      Show in List View
                    </label>
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.uiConfig.showInDetail}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          uiConfig: {
                            ...editingField.uiConfig,
                            showInDetail: e.target.checked
                          }
                        })}
                      />
                      Show in Detail View
                    </label>
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.uiConfig.editable}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          uiConfig: {
                            ...editingField.uiConfig,
                            editable: e.target.checked
                          }
                        })}
                      />
                      Editable
                    </label>
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.uiConfig.searchable}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          uiConfig: {
                            ...editingField.uiConfig,
                            searchable: e.target.checked
                          }
                        })}
                      />
                      Searchable
                    </label>
                    <label className="checkbox-field">
                      <input
                        type="checkbox"
                        checked={editingField.uiConfig.sortable}
                        onChange={(e) => setEditingField({
                          ...editingField,
                          uiConfig: {
                            ...editingField.uiConfig,
                            sortable: e.target.checked
                          }
                        })}
                      />
                      Sortable
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className="dialog-actions">
              <button
                className="dialog-btn secondary"
                onClick={() => setShowFieldDialog(false)}
              >
                Cancel
              </button>
              <button
                className="dialog-btn primary"
                onClick={handleFieldSubmit}
                disabled={!editingField.name || !editingField.displayName}
              >
                {editingField.id.startsWith('new_') ? 'Add Field' : 'Update Field'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};