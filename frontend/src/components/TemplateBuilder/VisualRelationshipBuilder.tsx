import React, { useState, useCallback, useRef, useMemo } from 'react';
import { 
  Trash2, X, ZoomIn, ZoomOut, 
  RotateCcw, Move, Link, ArrowRight, ArrowLeft, 
  GitBranch, Database
} from 'lucide-react';
import { Entity, Relationship, RelationshipType } from '../../types/template';
import './VisualRelationshipBuilder.css';

interface VisualRelationshipBuilderProps {
  entities: Entity[];
  relationships: Relationship[];
  onRelationshipAdd: (relationship: Omit<Relationship, 'id'>) => void;
  onRelationshipUpdate: (id: string, updates: Partial<Relationship>) => void;
  onRelationshipDelete: (id: string) => void;
  onClose: () => void;
}

interface Position {
  x: number;
  y: number;
}

interface EntityNode extends Entity {
  position: Position;
  isDragging?: boolean;
}

interface ConnectionPoint {
  entityId: string;
  side: 'left' | 'right' | 'top' | 'bottom';
  position: Position;
}

const RELATIONSHIP_TYPES: Array<{
  value: RelationshipType;
  label: string;
  icon: React.ReactNode;
  description: string;
}> = [
  {
    value: 'one_to_one',
    label: 'One to One',
    icon: <ArrowRight size={16} />,
    description: 'Each record relates to exactly one record'
  },
  {
    value: 'one_to_many',
    label: 'One to Many',
    icon: <GitBranch size={16} />,
    description: 'One record relates to multiple records'
  },
  {
    value: 'many_to_one',
    label: 'Many to One',
    icon: <ArrowLeft size={16} />,
    description: 'Multiple records relate to one record'
  },
  {
    value: 'many_to_many',
    label: 'Many to Many',
    icon: <Link size={16} />,
    description: 'Multiple records relate to multiple records'
  }
];

export const VisualRelationshipBuilder: React.FC<VisualRelationshipBuilderProps> = ({
  entities,
  relationships,
  onRelationshipAdd,
  onRelationshipDelete,
  onClose
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [entityNodes, setEntityNodes] = useState<EntityNode[]>(() =>
    entities.map((entity, index) => ({
      ...entity,
      position: {
        x: 100 + (index % 3) * 300,
        y: 100 + Math.floor(index / 3) * 200
      }
    }))
  );

  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState<Position>({ x: 0, y: 0 });
  const [selectedRelationship, setSelectedRelationship] = useState<string | null>(null);
  const [isCreatingRelationship, setIsCreatingRelationship] = useState(false);
  const [connectionStart, setConnectionStart] = useState<ConnectionPoint | null>(null);
  const [showRelationshipModal, setShowRelationshipModal] = useState(false);
  const [tempRelationship, setTempRelationship] = useState<Partial<Relationship> | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<Position>({ x: 0, y: 0 });

  // Auto-layout entities
  const autoLayout = useCallback(() => {
    const radius = 200;
    const centerX = 400;
    const centerY = 300;
    
    setEntityNodes(prev => prev.map((node, index) => {
      const angle = (2 * Math.PI * index) / prev.length;
      return {
        ...node,
        position: {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle)
        }
      };
    }));
  }, []);

  // Handle entity drag
  const handleEntityDragStart = useCallback((entityId: string, event: React.MouseEvent) => {
    const entity = entityNodes.find(n => n.id === entityId);
    if (!entity) return;

    setIsDragging(true);
    setDragStart({
      x: event.clientX - entity.position.x * zoom,
      y: event.clientY - entity.position.y * zoom
    });

    setEntityNodes(prev => prev.map(node =>
      node.id === entityId ? { ...node, isDragging: true } : node
    ));
  }, [entityNodes, zoom]);

  const handleEntityDrag = useCallback((event: React.MouseEvent) => {
    if (!isDragging) return;

    const draggingEntity = entityNodes.find(n => n.isDragging);
    if (!draggingEntity) return;

    const newX = (event.clientX - dragStart.x) / zoom;
    const newY = (event.clientY - dragStart.y) / zoom;

    setEntityNodes(prev => prev.map(node =>
      node.isDragging
        ? { ...node, position: { x: newX, y: newY } }
        : node
    ));
  }, [isDragging, dragStart, entityNodes, zoom]);

  const handleEntityDragEnd = useCallback(() => {
    setIsDragging(false);
    setEntityNodes(prev => prev.map(node => ({ ...node, isDragging: false })));
  }, []);

  // Handle connection creation
  const handleConnectionStart = useCallback((entityId: string, side: 'left' | 'right' | 'top' | 'bottom', position: Position) => {
    if (!isCreatingRelationship) return;

    setConnectionStart({ entityId, side, position });
  }, [isCreatingRelationship]);

  const handleConnectionEnd = useCallback((entityId: string) => {
    if (!connectionStart || connectionStart.entityId === entityId) return;

    setTempRelationship({
      sourceEntityId: connectionStart.entityId,
      targetEntityId: entityId,
      type: 'one_to_many',
      name: `${connectionStart.entityId}_${entityId}`,
      cascade: false
    });
    setShowRelationshipModal(true);
    setIsCreatingRelationship(false);
  }, [connectionStart]);

  // Create relationship
  const handleCreateRelationship = useCallback(() => {
    if (!tempRelationship) return;

    onRelationshipAdd({
      ...tempRelationship,
      id: `rel_${Date.now()}`
    } as Omit<Relationship, 'id'>);

    setTempRelationship(null);
    setConnectionStart(null);
    setShowRelationshipModal(false);
  }, [tempRelationship, onRelationshipAdd]);

  // Calculate relationship path
  const calculateRelationshipPath = useCallback((rel: Relationship): string => {
    const sourceNode = entityNodes.find(n => n.id === rel.sourceEntityId);
    const targetNode = entityNodes.find(n => n.id === rel.targetEntityId);
    
    if (!sourceNode || !targetNode) return '';

    const sourceCenter = {
      x: sourceNode.position.x + 150,
      y: sourceNode.position.y + 60
    };
    
    const targetCenter = {
      x: targetNode.position.x + 150,
      y: targetNode.position.y + 60
    };

    // Simple straight line for now - could be enhanced with curved paths
    return `M ${sourceCenter.x} ${sourceCenter.y} L ${targetCenter.x} ${targetCenter.y}`;
  }, [entityNodes]);

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev * 1.2, 3));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev / 1.2, 0.3));
  }, []);

  const handleResetView = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  // Relationship statistics
  const relationshipStats = useMemo(() => ({
    total: relationships.length,
    oneToOne: relationships.filter(r => r.type === 'one_to_one').length,
    oneToMany: relationships.filter(r => r.type === 'one_to_many').length,
    manyToOne: relationships.filter(r => r.type === 'many_to_one').length,
    manyToMany: relationships.filter(r => r.type === 'many_to_many').length
  }), [relationships]);

  return (
    <div className="visual-relationship-builder">
      {/* Header */}
      <div className="builder-header">
        <div className="header-content">
          <div className="header-info">
            <h2 className="builder-title">
              <Database size={24} />
              Visual Relationship Builder
            </h2>
            <p className="builder-subtitle">
              Design and manage entity relationships visually
            </p>
          </div>
          
          <div className="header-stats">
            <div className="stat-item">
              <span className="stat-value">{entities.length}</span>
              <span className="stat-label">Entities</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{relationshipStats.total}</span>
              <span className="stat-label">Relationships</span>
            </div>
          </div>

          <div className="header-actions">
            <button className="action-button secondary" onClick={onClose}>
              <X size={16} />
              Close
            </button>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="builder-toolbar">
        <div className="toolbar-section">
          <h3>Canvas Controls</h3>
          <div className="control-group">
            <button className="control-button" onClick={handleZoomIn}>
              <ZoomIn size={16} />
              Zoom In
            </button>
            <button className="control-button" onClick={handleZoomOut}>
              <ZoomOut size={16} />
              Zoom Out
            </button>
            <button className="control-button" onClick={handleResetView}>
              <RotateCcw size={16} />
              Reset View
            </button>
            <button className="control-button" onClick={autoLayout}>
              <Move size={16} />
              Auto Layout
            </button>
          </div>
        </div>

        <div className="toolbar-section">
          <h3>Relationships</h3>
          <div className="control-group">
            <button 
              className={`control-button ${isCreatingRelationship ? 'active' : ''}`}
              onClick={() => setIsCreatingRelationship(!isCreatingRelationship)}
            >
              <Link size={16} />
              {isCreatingRelationship ? 'Cancel Connection' : 'Create Relationship'}
            </button>
          </div>
        </div>

        <div className="toolbar-section">
          <h3>Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card small">
              <div className="stat-icon one-to-one">
                <ArrowRight size={14} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{relationshipStats.oneToOne}</div>
                <div className="stat-label">One to One</div>
              </div>
            </div>
            <div className="stat-card small">
              <div className="stat-icon one-to-many">
                <GitBranch size={14} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{relationshipStats.oneToMany}</div>
                <div className="stat-label">One to Many</div>
              </div>
            </div>
            <div className="stat-card small">
              <div className="stat-icon many-to-many">
                <Link size={14} />
              </div>
              <div className="stat-content">
                <div className="stat-value">{relationshipStats.manyToMany}</div>
                <div className="stat-label">Many to Many</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Canvas */}
      <div 
        className="relationship-canvas"
        ref={canvasRef}
        onMouseMove={handleEntityDrag}
        onMouseUp={handleEntityDragEnd}
        onMouseLeave={handleEntityDragEnd}
      >
        <div 
          className="canvas-content"
          style={{
            transform: `scale(${zoom}) translate(${pan.x}px, ${pan.y}px)`
          }}
        >
          {/* Entity Nodes */}
          {entityNodes.map(entity => (
            <EntityNode
              key={entity.id}
              entity={entity}
              isCreatingRelationship={isCreatingRelationship}
              onDragStart={handleEntityDragStart}
              onConnectionStart={handleConnectionStart}
              onConnectionEnd={handleConnectionEnd}
            />
          ))}

          {/* Relationship Lines */}
          <svg className="relationship-svg">
            {relationships.map(relationship => (
              <RelationshipLine
                key={relationship.id}
                relationship={relationship}
                path={calculateRelationshipPath(relationship)}
                isSelected={selectedRelationship === relationship.id}
                onSelect={() => setSelectedRelationship(relationship.id)}
                onDelete={() => onRelationshipDelete(relationship.id)}
              />
            ))}
          </svg>
        </div>
      </div>

      {/* Relationship Modal */}
      {showRelationshipModal && tempRelationship && (
        <div className="modal-overlay" onClick={() => setShowRelationshipModal(false)}>
          <div className="relationship-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create Relationship</h3>
              <button 
                className="modal-close"
                onClick={() => setShowRelationshipModal(false)}
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="modal-content">
              <div className="form-group">
                <label className="form-label">Relationship Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={tempRelationship.name || ''}
                  onChange={(e) => setTempRelationship(prev => ({ 
                    ...prev, 
                    name: e.target.value 
                  }))}
                  placeholder="Enter relationship name"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Relationship Type</label>
                <div className="relationship-type-selector">
                  {RELATIONSHIP_TYPES.map(type => (
                    <button
                      key={type.value}
                      className={`type-option ${tempRelationship.type === type.value ? 'selected' : ''}`}
                      onClick={() => setTempRelationship(prev => ({ 
                        ...prev, 
                        type: type.value 
                      }))}
                    >
                      <div className="type-icon">{type.icon}</div>
                      <div className="type-info">
                        <div className="type-name">{type.label}</div>
                        <div className="type-description">{type.description}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-textarea"
                  value={tempRelationship.description || ''}
                  onChange={(e) => setTempRelationship(prev => ({ 
                    ...prev, 
                    description: e.target.value 
                  }))}
                  placeholder="Describe this relationship"
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={tempRelationship.cascade || false}
                    onChange={(e) => setTempRelationship(prev => ({ 
                      ...prev, 
                      cascade: e.target.checked 
                    }))}
                  />
                  Enable cascade delete
                </label>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="action-button secondary"
                onClick={() => setShowRelationshipModal(false)}
              >
                Cancel
              </button>
              <button 
                className="action-button primary"
                onClick={handleCreateRelationship}
              >
                Create Relationship
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Entity Node Component
interface EntityNodeProps {
  entity: EntityNode;
  isCreatingRelationship: boolean;
  onDragStart: (entityId: string, event: React.MouseEvent) => void;
  onConnectionStart: (entityId: string, side: 'left' | 'right' | 'top' | 'bottom', position: Position) => void;
  onConnectionEnd: (entityId: string) => void;
}

const EntityNode: React.FC<EntityNodeProps> = ({
  entity,
  isCreatingRelationship,
  onDragStart,
  onConnectionStart,
  onConnectionEnd
}) => {
  return (
    <div
      className={`entity-node ${entity.isDragging ? 'dragging' : ''} ${entity.type}`}
      style={{
        transform: `translate(${entity.position.x}px, ${entity.position.y}px)`
      }}
      onMouseDown={(e) => !isCreatingRelationship && onDragStart(entity.id, e)}
    >
      <div className="entity-header">
        <div className="entity-icon">
          <Database size={20} />
        </div>
        <div className="entity-info">
          <div className="entity-name">{entity.name}</div>
          <div className="entity-type-label">{entity.type}</div>
        </div>
      </div>

      <div className="entity-fields">
        {entity.fields.slice(0, 5).map(field => (
          <div key={field.id} className="field-item">
            <div className="field-name">{field.title || field.name}</div>
            <div className="field-type">{field.type}</div>
          </div>
        ))}
        {entity.fields.length > 5 && (
          <div className="field-item more">
            +{entity.fields.length - 5} more fields
          </div>
        )}
      </div>

      {/* Connection Points */}
      {isCreatingRelationship && (
        <>
          <div 
            className="connection-point left"
            onClick={() => onConnectionStart(entity.id, 'left', { 
              x: entity.position.x, 
              y: entity.position.y + 60 
            })}
          />
          <div 
            className="connection-point right"
            onClick={() => onConnectionEnd(entity.id)}
          />
          <div 
            className="connection-point top"
            onClick={() => onConnectionStart(entity.id, 'top', { 
              x: entity.position.x + 150, 
              y: entity.position.y 
            })}
          />
          <div 
            className="connection-point bottom"
            onClick={() => onConnectionEnd(entity.id)}
          />
        </>
      )}
    </div>
  );
};

// Relationship Line Component
interface RelationshipLineProps {
  relationship: Relationship;
  path: string;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const RelationshipLine: React.FC<RelationshipLineProps> = ({
  relationship,
  path,
  isSelected,
  onSelect,
  onDelete
}) => {
  const getRelationshipIcon = (type: RelationshipType) => {
    switch (type) {
      case 'one_to_one': return <ArrowRight size={12} />;
      case 'one_to_many': return <GitBranch size={12} />;
      case 'many_to_one': return <ArrowLeft size={12} />;
      case 'many_to_many': return <Link size={12} />;
      default: return <Link size={12} />;
    }
  };

  return (
    <g className={`relationship-line ${isSelected ? 'selected' : ''}`}>
      <path
        d={path}
        stroke={isSelected ? '#3b82f6' : '#6b7280'}
        strokeWidth={isSelected ? 3 : 2}
        fill="none"
        markerEnd="url(#arrowhead)"
        onClick={onSelect}
        className="relationship-path"
      />
      {isSelected && (
        <g>
          <foreignObject x="50%" y="50%" width="200" height="40">
            <div className="relationship-label">
              <div className="label-content">
                {getRelationshipIcon(relationship.type)}
                <span>{relationship.name}</span>
                <button 
                  className="delete-relationship"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                  }}
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          </foreignObject>
        </g>
      )}
    </g>
  );
};