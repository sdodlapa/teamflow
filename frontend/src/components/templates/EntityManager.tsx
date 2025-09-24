import React, { useState } from 'react';
import { Plus, Edit3, Trash2, Database, Link, Settings } from 'lucide-react';
import { Entity, Field, Relationship } from '../../types/template';
import EntityForm from './EntityForm';
import FieldManager from './FieldManager';

interface EntityManagerProps {
  entities: Entity[];
  onEntitiesChange: (entities: Entity[]) => void;
  onFieldsChange: (entityId: string, fields: Field[]) => void;
  relationships: Relationship[];
  onRelationshipsChange: (relationships: Relationship[]) => void;
}

interface EntityWithStats extends Entity {
  fieldCount: number;
  relationshipCount: number;
}

const EntityManager: React.FC<EntityManagerProps> = ({
  entities,
  onEntitiesChange,
  onFieldsChange,
  relationships,
  onRelationshipsChange,
}) => {
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [showEntityForm, setShowEntityForm] = useState(false);
  const [editingEntity, setEditingEntity] = useState<Entity | null>(null);
  const [showFieldManager, setShowFieldManager] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'core' | 'lookup'>('all');

  // Calculate entity statistics
  const entitiesWithStats: EntityWithStats[] = entities.map(entity => ({
    ...entity,
    fieldCount: entity.fields.length,
    relationshipCount: relationships.filter(
      rel => rel.sourceEntityId === entity.id || rel.targetEntityId === entity.id
    ).length,
  }));

  // Filter entities based on search and type
  const filteredEntities = entitiesWithStats.filter(entity => {
    const matchesSearch = entity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entity.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || entity.type === filterType;
    return matchesSearch && matchesType;
  });

  const handleCreateEntity = () => {
    setEditingEntity(null);
    setShowEntityForm(true);
  };

  const handleEditEntity = (entity: Entity) => {
    setEditingEntity(entity);
    setShowEntityForm(true);
  };

  const handleDeleteEntity = (entityId: string) => {
    if (window.confirm('Are you sure you want to delete this entity? This will also remove all related relationships.')) {
      // Remove entity
      const updatedEntities = entities.filter(e => e.id !== entityId);
      onEntitiesChange(updatedEntities);

      // Remove related relationships
      const updatedRelationships = relationships.filter(
        rel => rel.sourceEntityId !== entityId && rel.targetEntityId !== entityId
      );
      onRelationshipsChange(updatedRelationships);

      // Clear selection if deleted entity was selected
      if (selectedEntity === entityId) {
        setSelectedEntity(null);
      }
    }
  };

  const handleEntitySave = (entityData: Omit<Entity, 'id'>) => {
    if (editingEntity) {
      // Update existing entity
      const updatedEntities = entities.map(e =>
        e.id === editingEntity.id ? { ...entityData, id: editingEntity.id } : e
      );
      onEntitiesChange(updatedEntities);
    } else {
      // Create new entity
      const newEntity: Entity = {
        ...entityData,
        id: `entity_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      onEntitiesChange([...entities, newEntity]);
    }
    setShowEntityForm(false);
    setEditingEntity(null);
  };

  const handleManageFields = (entity: Entity) => {
    setSelectedEntity(entity.id);
    setShowFieldManager(true);
  };

  const getEntityTypeColor = (type: string) => {
    switch (type) {
      case 'core':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'lookup':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getEntityIcon = (type: string) => {
    switch (type) {
      case 'core':
        return <Database className="h-4 w-4" />;
      case 'lookup':
        return <Link className="h-4 w-4" />;
      default:
        return <Database className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Entity Management</h3>
          <p className="text-sm text-gray-500">
            Define the data structures for your application
          </p>
        </div>
        <button
          onClick={handleCreateEntity}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Entity
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search entities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="sm:w-40">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as 'all' | 'core' | 'lookup')}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Types</option>
            <option value="core">Core Entities</option>
            <option value="lookup">Lookup Tables</option>
          </select>
        </div>
      </div>

      {/* Entity Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredEntities.map((entity) => (
          <div
            key={entity.id}
            className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200"
          >
            <div className="p-4">
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {getEntityIcon(entity.type)}
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {entity.name}
                  </h4>
                </div>
                <span
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getEntityTypeColor(
                    entity.type
                  )}`}
                >
                  {entity.type}
                </span>
              </div>

              {/* Description */}
              {entity.description && (
                <p className="text-xs text-gray-500 mb-3 line-clamp-2">
                  {entity.description}
                </p>
              )}

              {/* Stats */}
              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <div className="flex items-center space-x-4">
                  <span>{entity.fieldCount} fields</span>
                  <span>{entity.relationshipCount} relations</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleManageFields(entity)}
                    title="Manage Fields"
                    className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                  >
                    <Settings className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleEditEntity(entity)}
                    title="Edit Entity"
                    className="p-1 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded"
                  >
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteEntity(entity.id)}
                    title="Delete Entity"
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <button
                  onClick={() => setSelectedEntity(entity.id)}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  View Details
                </button>
              </div>
            </div>

            {/* Selected Entity Details */}
            {selectedEntity === entity.id && (
              <div className="border-t border-gray-200 bg-gray-50 px-4 py-3">
                <div className="text-xs text-gray-600 space-y-1">
                  <div>
                    <strong>Table Name:</strong> {entity.tableName || entity.name.toLowerCase()}
                  </div>
                  <div>
                    <strong>Primary Key:</strong> {entity.primaryKey || 'id'}
                  </div>
                  {entity.displayField && (
                    <div>
                      <strong>Display Field:</strong> {entity.displayField}
                    </div>
                  )}
                  {entity.timestamps && (
                    <div>
                      <strong>Timestamps:</strong> Enabled
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredEntities.length === 0 && (
        <div className="text-center py-12">
          <Database className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {searchTerm || filterType !== 'all' ? 'No entities found' : 'No entities yet'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || filterType !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Get started by creating your first entity'
            }
          </p>
          {!searchTerm && filterType === 'all' && (
            <div className="mt-6">
              <button
                onClick={handleCreateEntity}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Entity
              </button>
            </div>
          )}
        </div>
      )}

      {/* Entity Form Modal */}
      {showEntityForm && (
        <EntityForm
          entity={editingEntity}
          onSave={handleEntitySave}
          onCancel={() => {
            setShowEntityForm(false);
            setEditingEntity(null);
          }}
          existingEntityNames={entities.map(e => e.name)}
        />
      )}

      {/* Field Manager Modal */}
      {showFieldManager && selectedEntity && (
        <FieldManager
          entity={entities.find(e => e.id === selectedEntity)!}
          onFieldsChange={(fields: Field[]) => onFieldsChange(selectedEntity, fields)}
          onClose={() => {
            setShowFieldManager(false);
            setSelectedEntity(null);
          }}
          relationships={relationships}
          entities={entities}
        />
      )}
    </div>
  );
};

export default EntityManager;