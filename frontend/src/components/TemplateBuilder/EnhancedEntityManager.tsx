import React, { useState, useMemo, useCallback } from 'react';
import { 
  Plus, Edit3, Trash2, Database, Link, Settings, Search, 
  BarChart3, Download, Grid, List, 
  ChevronDown, ChevronRight, Package
} from 'lucide-react';
import { Entity, Field, Relationship } from '../../types/template';
import './EnhancedEntityManager.css';

interface EnhancedEntityManagerProps {
  entities: Entity[];
  relationships: Relationship[];
  onEntitiesChange: (entities: Entity[]) => void;
  onRelationshipsChange: (relationships: Relationship[]) => void;
  onEntityEdit?: (entity: Entity) => void;
  onEntityCreate?: () => void;
  onFieldsManage?: (entityId: string) => void;
  showRelationshipBuilder?: boolean;
  allowBulkOperations?: boolean;
  templates?: EntityTemplate[];
}

interface EntityTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  fields: Partial<Field>[];
  color: string;
}

interface EntityWithStats extends Entity {
  fieldCount: number;
  relationshipCount: number;
  lastModified?: Date;
  status: 'draft' | 'published' | 'archived';
}

interface FilterOptions {
  search: string;
  type: 'all' | 'core' | 'lookup';
  status: 'all' | 'draft' | 'published' | 'archived';
  category: string;
}

// Pre-built entity templates
const ENTITY_TEMPLATES: EntityTemplate[] = [
  {
    id: 'user',
    name: 'User',
    description: 'Standard user entity with authentication fields',
    icon: '👤',
    category: 'Core',
    color: '#3B82F6',
    fields: [
      { name: 'email', type: 'email', required: true, unique: true },
      { name: 'username', type: 'string', required: true, unique: true },
      { name: 'firstName', type: 'string', required: true },
      { name: 'lastName', type: 'string', required: true },
      { name: 'isActive', type: 'boolean', defaultValue: true }
    ]
  },
  {
    id: 'product',
    name: 'Product',
    description: 'E-commerce product with inventory tracking',
    icon: '📦',
    category: 'E-commerce',
    color: '#10B981',
    fields: [
      { name: 'name', type: 'string', required: true },
      { name: 'description', type: 'text' },
      { name: 'price', type: 'decimal', required: true },
      { name: 'sku', type: 'string', required: true, unique: true },
      { name: 'inventory', type: 'integer', defaultValue: 0 }
    ]
  },
  {
    id: 'order',
    name: 'Order',
    description: 'Order management with status tracking',
    icon: '🛒',
    category: 'E-commerce', 
    color: '#F97316',
    fields: [
      { name: 'orderNumber', type: 'string', required: true, unique: true },
      { name: 'status', type: 'string', required: true },
      { name: 'total', type: 'decimal', required: true },
      { name: 'orderDate', type: 'datetime', required: true },
      { name: 'notes', type: 'text' }
    ]
  },
  {
    id: 'category',
    name: 'Category',
    description: 'Hierarchical category system',
    icon: '📁',
    category: 'Lookup',
    color: '#8B5CF6',
    fields: [
      { name: 'name', type: 'string', required: true },
      { name: 'slug', type: 'string', required: true, unique: true },
      { name: 'description', type: 'text' },
      { name: 'isActive', type: 'boolean', defaultValue: true }
    ]
  }
];

const VIEW_MODES = {
  GRID: 'grid',
  LIST: 'list',
  STATS: 'stats'
} as const;

type ViewMode = typeof VIEW_MODES[keyof typeof VIEW_MODES];

export const EnhancedEntityManager: React.FC<EnhancedEntityManagerProps> = ({
  entities,
  relationships,
  onEntitiesChange,
  onRelationshipsChange,
  onEntityEdit,
  onEntityCreate,
  onFieldsManage,
  allowBulkOperations = true,
  templates = ENTITY_TEMPLATES
}) => {
  // Enhanced state management
  const [filters, setFilters] = useState<FilterOptions>({
    search: '',
    type: 'all',
    status: 'all',
    category: 'all'
  });

  const [viewMode, setViewMode] = useState<ViewMode>(VIEW_MODES.GRID);
  const [selectedEntities, setSelectedEntities] = useState<Set<string>>(new Set());
  const [showTemplates, setShowTemplates] = useState(false);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['Core']));

  // Calculate enhanced entity statistics
  const entitiesWithStats = useMemo((): EntityWithStats[] => {
    return entities.map(entity => ({
      ...entity,
      fieldCount: entity.fields?.length || 0,
      relationshipCount: relationships.filter(
        rel => rel.sourceEntityId === entity.id || rel.targetEntityId === entity.id
      ).length,
      lastModified: new Date(), // TODO: Get from actual data
      status: 'published' as const // TODO: Get from actual data
    }));
  }, [entities, relationships]);

  // Advanced filtering and search
  const filteredEntities = useMemo(() => {
    return entitiesWithStats.filter(entity => {
      // Text search
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const matchesSearch = 
          entity.name.toLowerCase().includes(searchLower) ||
          entity.description?.toLowerCase().includes(searchLower) ||
          entity.fields.some(field => 
            field.name.toLowerCase().includes(searchLower) ||
            field.title?.toLowerCase().includes(searchLower)
          );
        if (!matchesSearch) return false;
      }

      // Type filter
      if (filters.type !== 'all' && entity.type !== filters.type) {
        return false;
      }

      // Status filter  
      if (filters.status !== 'all' && entity.status !== filters.status) {
        return false;
      }

      return true;
    });
  }, [entitiesWithStats, filters]);

  // Statistics calculations
  const statistics = useMemo(() => {
    const totalFields = entitiesWithStats.reduce((sum, entity) => sum + entity.fieldCount, 0);
    const totalRelationships = relationships.length;
    const avgFieldsPerEntity = entitiesWithStats.length > 0 
      ? Math.round(totalFields / entitiesWithStats.length * 10) / 10 
      : 0;

    return {
      totalEntities: entitiesWithStats.length,
      coreEntities: entitiesWithStats.filter(e => e.type === 'core').length,
      lookupEntities: entitiesWithStats.filter(e => e.type === 'lookup').length,
      totalFields,
      totalRelationships,
      avgFieldsPerEntity
    };
  }, [entitiesWithStats, relationships]);

  // Event handlers
  const handleEntitySelect = useCallback((entityId: string, selected: boolean) => {
    setSelectedEntities(prev => {
      const newSet = new Set(prev);
      if (selected) {
        newSet.add(entityId);
      } else {
        newSet.delete(entityId);
      }
      return newSet;
    });
  }, []);

  const handleSelectAll = useCallback(() => {
    if (selectedEntities.size === filteredEntities.length) {
      setSelectedEntities(new Set());
    } else {
      setSelectedEntities(new Set(filteredEntities.map(e => e.id)));
    }
  }, [selectedEntities.size, filteredEntities]);

  const handleBulkDelete = useCallback(() => {
    if (selectedEntities.size === 0) return;

    const entityNames = Array.from(selectedEntities)
      .map(id => entities.find(e => e.id === id)?.name)
      .filter(Boolean)
      .join(', ');

    if (window.confirm(`Are you sure you want to delete ${selectedEntities.size} entities (${entityNames})? This will also remove all related relationships.`)) {
      const remainingEntities = entities.filter(e => !selectedEntities.has(e.id));
      const remainingRelationships = relationships.filter(rel => 
        !selectedEntities.has(rel.sourceEntityId) && 
        !selectedEntities.has(rel.targetEntityId)
      );

      onEntitiesChange(remainingEntities);
      onRelationshipsChange(remainingRelationships);
      setSelectedEntities(new Set());
    }
  }, [selectedEntities, entities, relationships, onEntitiesChange, onRelationshipsChange]);

  const handleCreateFromTemplate = useCallback((template: EntityTemplate) => {
    const newEntity: Entity = {
      id: `entity_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: template.name,
      description: template.description,
      type: template.category === 'Lookup' ? 'lookup' : 'core',
      tableName: template.name.toLowerCase(),
      primaryKey: 'id',
      displayField: template.fields[0]?.name || 'name',
      timestamps: true,
      fields: template.fields.map((field, index) => ({
        id: `field_${Date.now()}_${index}`,
        name: field.name || '',
        title: field.title || field.name || '',
        type: field.type || 'string',
        required: field.required || false,
        unique: field.unique || false,
        defaultValue: field.defaultValue
      })) as Field[]
    };

    onEntitiesChange([...entities, newEntity]);
    setShowTemplates(false);
  }, [entities, onEntitiesChange]);

  const handleExportEntities = useCallback(() => {
    const dataToExport = selectedEntities.size > 0 
      ? entities.filter(e => selectedEntities.has(e.id))
      : entities;

    const dataStr = JSON.stringify(dataToExport, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `entities_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [entities, selectedEntities]);

  const getEntityTypeColor = (type: string) => {
    switch (type) {
      case 'core':
        return 'entity-core';
      case 'lookup':
        return 'entity-lookup';
      default:
        return 'entity-default';
    }
  };

  const getEntityIcon = (type: string) => {
    switch (type) {
      case 'core':
        return <Database className="h-5 w-5" />;
      case 'lookup':
        return <Link className="h-5 w-5" />;
      default:
        return <Database className="h-5 w-5" />;
    }
  };

  return (
    <div className="enhanced-entity-manager">
      {/* Header Section */}
      <div className="entity-manager-header">
        <div className="header-content">
          <div className="header-info">
            <h2 className="manager-title">
              <Database className="h-6 w-6" />
              Entity Management
            </h2>
            <p className="manager-description">
              Define and manage your application's data structures with advanced tooling
            </p>
          </div>
          
          <div className="header-actions">
            <button
              className="action-button secondary"
              onClick={() => setShowTemplates(!showTemplates)}
            >
              <Package className="h-4 w-4" />
              Templates
            </button>
            
            <button
              className="action-button primary"
              onClick={onEntityCreate}
            >
              <Plus className="h-4 w-4" />
              Create Entity
            </button>
          </div>
        </div>

        {/* Statistics Dashboard */}
        <div className="statistics-dashboard">
          <div className="stat-card">
            <div className="stat-icon entity-core">
              <Database className="h-5 w-5" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{statistics.totalEntities}</div>
              <div className="stat-label">Total Entities</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon entity-lookup">
              <Link className="h-5 w-5" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{statistics.totalFields}</div>
              <div className="stat-label">Total Fields</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon entity-relationship">
              <BarChart3 className="h-5 w-5" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{statistics.totalRelationships}</div>
              <div className="stat-label">Relationships</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon entity-average">
              <Settings className="h-5 w-5" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{statistics.avgFieldsPerEntity}</div>
              <div className="stat-label">Avg Fields/Entity</div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Search and Filters */}
      <div className="search-and-filters">
        <div className="search-section">
          <div className="search-input-wrapper">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Search entities, fields, descriptions..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="search-input"
            />
          </div>
        </div>

        <div className="filters-section">
          <select
            value={filters.type}
            onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value as any }))}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value="core">Core Entities</option>
            <option value="lookup">Lookup Tables</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value as any }))}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        <div className="view-controls">
          <div className="view-mode-toggle">
            <button
              className={`view-button ${viewMode === VIEW_MODES.GRID ? 'active' : ''}`}
              onClick={() => setViewMode(VIEW_MODES.GRID)}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              className={`view-button ${viewMode === VIEW_MODES.LIST ? 'active' : ''}`}
              onClick={() => setViewMode(VIEW_MODES.LIST)}
            >
              <List className="h-4 w-4" />
            </button>
          </div>

          {allowBulkOperations && (
            <div className="bulk-actions">
              <button
                className="action-button secondary small"
                onClick={() => setShowBulkActions(!showBulkActions)}
                disabled={selectedEntities.size === 0}
              >
                <Settings className="h-4 w-4" />
                Actions ({selectedEntities.size})
              </button>
              
              {showBulkActions && selectedEntities.size > 0 && (
                <div className="bulk-actions-dropdown">
                  <button onClick={handleBulkDelete} className="bulk-action-item danger">
                    <Trash2 className="h-4 w-4" />
                    Delete Selected
                  </button>
                  <button onClick={handleExportEntities} className="bulk-action-item">
                    <Download className="h-4 w-4" />
                    Export Selected
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Template Selection Modal */}
      {showTemplates && (
        <div className="modal-overlay">
          <div className="template-modal">
            <div className="modal-header">
              <h3>Choose Entity Template</h3>
              <button
                onClick={() => setShowTemplates(false)}
                className="modal-close"
              >
                ×
              </button>
            </div>
            
            <div className="template-categories">
              {['Core', 'E-commerce', 'Lookup'].map(category => {
                const categoryTemplates = templates.filter(t => t.category === category);
                if (categoryTemplates.length === 0) return null;

                return (
                  <div key={category} className="template-category">
                    <button
                      className="category-header"
                      onClick={() => {
                        const newExpanded = new Set(expandedCategories);
                        if (newExpanded.has(category)) {
                          newExpanded.delete(category);
                        } else {
                          newExpanded.add(category);
                        }
                        setExpandedCategories(newExpanded);
                      }}
                    >
                      {expandedCategories.has(category) ? <ChevronDown /> : <ChevronRight />}
                      {category} ({categoryTemplates.length})
                    </button>
                    
                    {expandedCategories.has(category) && (
                      <div className="template-grid">
                        {categoryTemplates.map(template => (
                          <div
                            key={template.id}
                            className="template-card"
                            onClick={() => handleCreateFromTemplate(template)}
                          >
                            <div className="template-icon" style={{ color: template.color }}>
                              {template.icon}
                            </div>
                            <div className="template-content">
                              <h4 className="template-name">{template.name}</h4>
                              <p className="template-description">{template.description}</p>
                              <div className="template-fields">
                                {template.fields.length} fields included
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Entity Display */}
      <div className={`entities-container view-${viewMode}`}>
        {allowBulkOperations && filteredEntities.length > 0 && (
          <div className="bulk-select-header">
            <label className="bulk-select-all">
              <input
                type="checkbox"
                checked={selectedEntities.size === filteredEntities.length && filteredEntities.length > 0}
                onChange={handleSelectAll}
              />
              Select All ({filteredEntities.length})
            </label>
          </div>
        )}

        {filteredEntities.length === 0 ? (
          <div className="empty-state">
            <Database className="empty-icon" />
            <h3>No entities found</h3>
            <p>
              {filters.search || filters.type !== 'all' || filters.status !== 'all'
                ? 'No entities match your current filters'
                : 'Start by creating your first entity or using a template'
              }
            </p>
            {!filters.search && filters.type === 'all' && filters.status === 'all' && (
              <div className="empty-actions">
                <button
                  onClick={() => setShowTemplates(true)}
                  className="action-button secondary"
                >
                  <Package className="h-4 w-4" />
                  Browse Templates
                </button>
                <button
                  onClick={onEntityCreate}
                  className="action-button primary"
                >
                  <Plus className="h-4 w-4" />
                  Create First Entity
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className={`entities-grid ${viewMode}`}>
            {filteredEntities.map(entity => (
              <div
                key={entity.id}
                className={`entity-card ${getEntityTypeColor(entity.type)} ${
                  selectedEntities.has(entity.id) ? 'selected' : ''
                }`}
              >
                {allowBulkOperations && (
                  <div className="entity-select">
                    <input
                      type="checkbox"
                      checked={selectedEntities.has(entity.id)}
                      onChange={(e) => handleEntitySelect(entity.id, e.target.checked)}
                    />
                  </div>
                )}

                <div className="entity-header">
                  <div className="entity-info">
                    <div className="entity-icon">
                      {getEntityIcon(entity.type)}
                    </div>
                    <div className="entity-identity">
                      <h3 className="entity-name">{entity.name}</h3>
                      <span className="entity-type">{entity.type}</span>
                    </div>
                  </div>
                  
                  <div className="entity-status">
                    <span className={`status-badge ${entity.status}`}>
                      {entity.status}
                    </span>
                  </div>
                </div>

                <div className="entity-content">
                  <p className="entity-description">
                    {entity.description || 'No description provided'}
                  </p>

                  <div className="entity-stats">
                    <div className="stat-item">
                      <span className="stat-value">{entity.fieldCount}</span>
                      <span className="stat-label">Fields</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{entity.relationshipCount}</span>
                      <span className="stat-label">Relations</span>
                    </div>
                  </div>
                </div>

                <div className="entity-actions">
                  <button
                    onClick={() => onFieldsManage?.(entity.id)}
                    className="entity-action-btn"
                    title="Manage Fields"
                  >
                    <Settings className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onEntityEdit?.(entity)}
                    className="entity-action-btn"
                    title="Edit Entity"
                  >
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (window.confirm(`Are you sure you want to delete "${entity.name}"?`)) {
                        const updatedEntities = entities.filter(e => e.id !== entity.id);
                        const updatedRelationships = relationships.filter(
                          rel => rel.sourceEntityId !== entity.id && rel.targetEntityId !== entity.id
                        );
                        onEntitiesChange(updatedEntities);
                        onRelationshipsChange(updatedRelationships);
                      }
                    }}
                    className="entity-action-btn danger"
                    title="Delete Entity"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};