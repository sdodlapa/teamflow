import React, { useState, useRef, useEffect } from 'react';
import { Plus, Trash2, Edit3, ArrowRight, ArrowLeftRight, ArrowUpDown, Link2 } from 'lucide-react';
import { Entity, Relationship, RelationshipType } from '../../types/template';
import RelationshipForm from './RelationshipForm';

interface RelationshipDesignerProps {
  entities: Entity[];
  relationships: Relationship[];
  onRelationshipsChange: (relationships: Relationship[]) => void;
}

interface EntityPosition {
  id: string;
  x: number;
  y: number;
}

const RelationshipDesigner: React.FC<RelationshipDesignerProps> = ({
  entities,
  relationships,
  onRelationshipsChange,
}) => {
  const [entityPositions, setEntityPositions] = useState<EntityPosition[]>([]);
  const [selectedRelationship, setSelectedRelationship] = useState<string | null>(null);
  const [showRelationshipForm, setShowRelationshipForm] = useState(false);
  const [editingRelationship, setEditingRelationship] = useState<Relationship | null>(null);
  const [draggedEntity, setDraggedEntity] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'visual' | 'list'>('visual');
  const canvasRef = useRef<HTMLDivElement>(null);

  // Initialize entity positions
  useEffect(() => {
    if (entities.length > 0 && entityPositions.length === 0) {
      const positions: EntityPosition[] = entities.map((entity, index) => {
        const angle = (index * 2 * Math.PI) / entities.length;
        const radius = Math.min(200, 50 + entities.length * 30);
        return {
          id: entity.id,
          x: 300 + radius * Math.cos(angle),
          y: 250 + radius * Math.sin(angle),
        };
      });
      setEntityPositions(positions);
    }
  }, [entities, entityPositions]);

  const handleCreateRelationship = () => {
    setEditingRelationship(null);
    setShowRelationshipForm(true);
  };

  const handleEditRelationship = (relationship: Relationship) => {
    setEditingRelationship(relationship);
    setShowRelationshipForm(true);
  };

  const handleDeleteRelationship = (relationshipId: string) => {
    if (window.confirm('Are you sure you want to delete this relationship?')) {
      const updatedRelationships = relationships.filter(r => r.id !== relationshipId);
      onRelationshipsChange(updatedRelationships);
      if (selectedRelationship === relationshipId) {
        setSelectedRelationship(null);
      }
    }
  };

  const handleRelationshipSave = (relationshipData: Omit<Relationship, 'id'>) => {
    if (editingRelationship) {
      // Update existing relationship
      const updatedRelationships = relationships.map(r =>
        r.id === editingRelationship.id 
          ? { ...relationshipData, id: editingRelationship.id }
          : r
      );
      onRelationshipsChange(updatedRelationships);
    } else {
      // Create new relationship
      const newRelationship: Relationship = {
        ...relationshipData,
        id: `rel_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      };
      onRelationshipsChange([...relationships, newRelationship]);
    }
    setShowRelationshipForm(false);
    setEditingRelationship(null);
  };

  const handleEntityDrag = (entityId: string, newX: number, newY: number) => {
    setEntityPositions(prev => 
      prev.map(pos => 
        pos.id === entityId ? { ...pos, x: newX, y: newY } : pos
      )
    );
  };

  const getEntityPosition = (entityId: string): EntityPosition => {
    return entityPositions.find(p => p.id === entityId) || { id: entityId, x: 0, y: 0 };
  };

  const getRelationshipIcon = (type: RelationshipType) => {
    switch (type) {
      case 'one_to_one':
        return <ArrowRight className="h-4 w-4" />;
      case 'one_to_many':
        return <ArrowUpDown className="h-4 w-4" />;
      case 'many_to_one':
        return <ArrowUpDown className="h-4 w-4 rotate-180" />;
      case 'many_to_many':
        return <ArrowLeftRight className="h-4 w-4" />;
      default:
        return <Link2 className="h-4 w-4" />;
    }
  };

  const getRelationshipColor = (type: RelationshipType) => {
    switch (type) {
      case 'one_to_one':
        return '#3B82F6'; // Blue
      case 'one_to_many':
        return '#10B981'; // Green
      case 'many_to_one':
        return '#F59E0B'; // Yellow
      case 'many_to_many':
        return '#EF4444'; // Red
      default:
        return '#6B7280'; // Gray
    }
  };

  const renderVisualDesigner = () => (
    <div className="relative">
      {/* Canvas */}
      <div
        ref={canvasRef}
        className="relative w-full h-[500px] bg-gray-50 border border-gray-200 rounded-lg overflow-hidden"
        style={{ backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)', backgroundSize: '20px 20px' }}
      >
        {/* Relationships (Lines) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
          {relationships.map((relationship) => {
            const sourcePos = getEntityPosition(relationship.sourceEntityId);
            const targetPos = getEntityPosition(relationship.targetEntityId);
            const color = getRelationshipColor(relationship.type);
            
            return (
              <g key={relationship.id}>
                <line
                  x1={sourcePos.x + 60}
                  y1={sourcePos.y + 30}
                  x2={targetPos.x + 60}
                  y2={targetPos.y + 30}
                  stroke={color}
                  strokeWidth={selectedRelationship === relationship.id ? 3 : 2}
                  strokeDasharray={relationship.type === 'many_to_many' ? '5,5' : '0'}
                  className="cursor-pointer"
                  onClick={() => setSelectedRelationship(relationship.id)}
                />
                {/* Relationship label */}
                <text
                  x={(sourcePos.x + targetPos.x) / 2 + 60}
                  y={(sourcePos.y + targetPos.y) / 2 + 25}
                  fill={color}
                  fontSize="12"
                  textAnchor="middle"
                  className="cursor-pointer pointer-events-auto"
                  onClick={() => setSelectedRelationship(relationship.id)}
                >
                  {relationship.name}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Entities */}
        {entities.map((entity) => {
          const position = getEntityPosition(entity.id);
          const relatedRelationships = relationships.filter(
            r => r.sourceEntityId === entity.id || r.targetEntityId === entity.id
          );

          return (
            <div
              key={entity.id}
              className={`absolute bg-white border-2 rounded-lg p-3 cursor-move shadow-sm hover:shadow-md transition-shadow ${
                entity.type === 'core' ? 'border-blue-300' : 'border-green-300'
              }`}
              style={{ 
                left: position.x, 
                top: position.y, 
                width: 120, 
                zIndex: 2 
              }}
              draggable
              onDragStart={(e) => {
                setDraggedEntity(entity.id);
                e.dataTransfer.effectAllowed = 'move';
              }}
              onDragEnd={(e) => {
                if (canvasRef.current && draggedEntity) {
                  const rect = canvasRef.current.getBoundingClientRect();
                  const newX = Math.max(0, Math.min(e.clientX - rect.left - 60, rect.width - 120));
                  const newY = Math.max(0, Math.min(e.clientY - rect.top - 30, rect.height - 60));
                  handleEntityDrag(draggedEntity, newX, newY);
                }
                setDraggedEntity(null);
              }}
            >
              <div className="text-xs font-medium text-gray-900 truncate">
                {entity.name}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {entity.fields.length} fields
              </div>
              <div className="text-xs text-gray-500">
                {relatedRelationships.length} relations
              </div>
            </div>
          );
        })}

        {/* Empty state */}
        {entities.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <Link2 className="h-12 w-12 mx-auto mb-2" />
              <p className="text-sm">No entities to design relationships</p>
              <p className="text-xs">Add entities first to create relationships</p>
            </div>
          </div>
        )}
      </div>

      {/* Canvas Controls */}
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCreateRelationship}
            disabled={entities.length < 2}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Relationship
          </button>
          
          {entities.length < 2 && (
            <p className="text-xs text-gray-500">
              Need at least 2 entities to create relationships
            </p>
          )}
        </div>

        <div className="text-xs text-gray-500">
          Drag entities to reposition • Click relationships to select
        </div>
      </div>
    </div>
  );

  const renderListView = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-900">Relationships List</h4>
        <button
          onClick={handleCreateRelationship}
          disabled={entities.length < 2}
          className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="h-4 w-4 mr-1" />
          Add Relationship
        </button>
      </div>

      <div className="space-y-2">
        {relationships.map((relationship) => {
          const sourceEntity = entities.find(e => e.id === relationship.sourceEntityId);
          const targetEntity = entities.find(e => e.id === relationship.targetEntityId);
          
          return (
            <div
              key={relationship.id}
              className={`border rounded-lg p-4 ${
                selectedRelationship === relationship.id 
                  ? 'border-blue-300 bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="flex items-center justify-center w-8 h-8 rounded border"
                    style={{ 
                      backgroundColor: `${getRelationshipColor(relationship.type)}20`,
                      borderColor: getRelationshipColor(relationship.type)
                    }}
                  >
                    {getRelationshipIcon(relationship.type)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h5 className="text-sm font-medium text-gray-900">
                        {relationship.name}
                      </h5>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {relationship.type.replace('_', '-')}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {sourceEntity?.name} → {targetEntity?.name}
                    </p>
                    {relationship.description && (
                      <p className="text-xs text-gray-600 mt-1">
                        {relationship.description}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleEditRelationship(relationship)}
                    className="p-1 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded"
                    title="Edit Relationship"
                  >
                    <Edit3 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteRelationship(relationship.id)}
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                    title="Delete Relationship"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Relationship Details */}
              {selectedRelationship === relationship.id && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <strong>Foreign Key:</strong> {relationship.foreignKey || 'Auto-generated'}
                    </div>
                    <div>
                      <strong>Back Populates:</strong> {relationship.backPopulates || 'None'}
                    </div>
                    <div>
                      <strong>Cascade Delete:</strong> {relationship.cascade ? 'Yes' : 'No'}
                    </div>
                    <div>
                      <strong>Created:</strong> Just now
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty state */}
      {relationships.length === 0 && (
        <div className="text-center py-12">
          <Link2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No relationships yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            {entities.length < 2 
              ? 'Add at least 2 entities to create relationships'
              : 'Get started by creating your first relationship'
            }
          </p>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Relationship Designer</h3>
          <p className="text-sm text-gray-500">
            Define how your entities connect and relate to each other
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="inline-flex rounded-md shadow-sm">
            <button
              onClick={() => setViewMode('visual')}
              className={`px-3 py-2 text-sm font-medium border ${
                viewMode === 'visual'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              } rounded-l-md`}
            >
              Visual
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 text-sm font-medium border-t border-b border-r ${
                viewMode === 'list'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              } rounded-r-md`}
            >
              List
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="text-sm font-medium text-blue-900">Total Entities</div>
          <div className="text-2xl font-bold text-blue-600">{entities.length}</div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="text-sm font-medium text-green-900">Total Relationships</div>
          <div className="text-2xl font-bold text-green-600">{relationships.length}</div>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
          <div className="text-sm font-medium text-purple-900">Coverage</div>
          <div className="text-2xl font-bold text-purple-600">
            {entities.length > 0 ? Math.round((relationships.length / Math.max(entities.length - 1, 1)) * 100) : 0}%
          </div>
        </div>
      </div>

      {/* Main Content */}
      {viewMode === 'visual' ? renderVisualDesigner() : renderListView()}

      {/* Relationship Form Modal */}
      {showRelationshipForm && (
        <RelationshipForm
          relationship={editingRelationship}
          entities={entities}
          existingRelationships={relationships}
          onSave={handleRelationshipSave}
          onCancel={() => {
            setShowRelationshipForm(false);
            setEditingRelationship(null);
          }}
        />
      )}
    </div>
  );
};

export default RelationshipDesigner;