/**
 * Workflow Automation Builder - Day 18 Implementation
 * Visual workflow designer with drag-and-drop node-based interface
 */

import React, { useState, useCallback } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import {
  Play,
  Square,
  Save,
  Settings,
  Trash2,
  GitBranch,
  Clock,
  Zap,
  Filter,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  Circle,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import './WorkflowAutomationBuilder.css';

// Workflow node types and interfaces
export interface WorkflowNode {
  id: string;
  type: 'trigger' | 'condition' | 'action' | 'delay' | 'branch' | 'merge';
  position: { x: number; y: number };
  config: Record<string, any>;
  status: 'idle' | 'running' | 'success' | 'error' | 'waiting';
  title: string;
  description?: string;
}

export interface WorkflowConnection {
  id: string;
  source: string;
  target: string;
  sourceHandle: string;
  targetHandle: string;
  label?: string;
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  isActive: boolean;
  created: string;
  modified: string;
}

// Node type definitions
const NODE_TYPES = {
  trigger: {
    label: 'Trigger',
    icon: Zap,
    color: '#10B981',
    subtypes: ['webhook', 'schedule', 'manual', 'event']
  },
  condition: {
    label: 'Condition',
    icon: Filter,
    color: '#F59E0B',
    subtypes: ['if', 'switch', 'exists', 'compare']
  },
  action: {
    label: 'Action',
    icon: Circle,
    color: '#3B82F6',
    subtypes: ['api_call', 'email', 'database', 'notification']
  },
  delay: {
    label: 'Delay',
    icon: Clock,
    color: '#8B5CF6',
    subtypes: ['wait', 'schedule']
  },
  branch: {
    label: 'Branch',
    icon: GitBranch,
    color: '#EF4444',
    subtypes: ['split', 'parallel']
  },
  merge: {
    label: 'Merge',
    icon: ArrowRight,
    color: '#6B7280',
    subtypes: ['join', 'collect']
  }
};

// Draggable Node Library Component
const NodeLibraryItem: React.FC<{
  nodeType: keyof typeof NODE_TYPES;
  onAddNode: (nodeType: keyof typeof NODE_TYPES) => void;
}> = ({ nodeType, onAddNode }) => {
  const nodeConfig = NODE_TYPES[nodeType];
  const Icon = nodeConfig.icon;

  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'nodeType',
    item: { nodeType },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  return (
    <div
      ref={drag}
      className={`node-library-item ${isDragging ? 'dragging' : ''}`}
      style={{ '--node-color': nodeConfig.color } as React.CSSProperties}
      onClick={() => onAddNode(nodeType)}
    >
      <Icon className="node-icon" size={20} />
      <span className="node-label">{nodeConfig.label}</span>
    </div>
  );
};

// Workflow Node Component
const WorkflowNodeComponent: React.FC<{
  node: WorkflowNode;
  isSelected: boolean;
  onSelect: (nodeId: string) => void;
  onUpdatePosition: (nodeId: string, position: { x: number; y: number }) => void;
  onDelete: (nodeId: string) => void;
}> = ({ node, isSelected, onSelect, onDelete }) => {
  const nodeConfig = NODE_TYPES[node.type];
  const Icon = nodeConfig.icon;

  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'workflowNode',
    item: { nodeId: node.id, offset: { x: 0, y: 0 } },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  const getStatusIcon = () => {
    switch (node.status) {
      case 'running':
        return <div className="status-spinner" />;
      case 'success':
        return <CheckCircle className="status-icon success" size={16} />;
      case 'error':
        return <XCircle className="status-icon error" size={16} />;
      case 'waiting':
        return <AlertCircle className="status-icon waiting" size={16} />;
      default:
        return null;
    }
  };

  return (
    <div
      ref={drag}
      className={`workflow-node ${node.type} ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
      style={{
        left: node.position.x,
        top: node.position.y,
        '--node-color': nodeConfig.color
      } as React.CSSProperties}
      onClick={() => onSelect(node.id)}
    >
      <div className="node-header">
        <Icon className="node-icon" size={18} />
        <span className="node-title">{node.title}</span>
        <div className="node-actions">
          {getStatusIcon()}
          <button
            className="delete-button"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(node.id);
            }}
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
      {node.description && (
        <div className="node-description">{node.description}</div>
      )}
      <div className="node-handles">
        <div className="input-handle" />
        <div className="output-handle" />
      </div>
    </div>
  );
};

// Node Inspector Panel
const NodeInspector: React.FC<{
  node: WorkflowNode | null;
  onUpdateNode: (nodeId: string, updates: Partial<WorkflowNode>) => void;
}> = ({ node, onUpdateNode }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['general']));

  if (!node) {
    return (
      <div className="node-inspector empty">
        <div className="empty-state">
          <Settings className="empty-icon" size={48} />
          <h3>Node Inspector</h3>
          <p>Select a node to view and edit its properties</p>
        </div>
      </div>
    );
  }

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  const updateNodeConfig = (key: string, value: any) => {
    onUpdateNode(node.id, {
      config: { ...node.config, [key]: value }
    });
  };

  const renderConfigField = (key: string, value: any, type: string = 'text') => {
    switch (type) {
      case 'select':
        return (
          <select
            value={value || ''}
            onChange={(e) => updateNodeConfig(key, e.target.value)}
            className="config-input"
          >
            <option value="">Select...</option>
            {/* Add options based on node type */}
          </select>
        );
      case 'textarea':
        return (
          <textarea
            value={value || ''}
            onChange={(e) => updateNodeConfig(key, e.target.value)}
            className="config-input"
            rows={3}
          />
        );
      case 'number':
        return (
          <input
            type="number"
            value={value || ''}
            onChange={(e) => updateNodeConfig(key, parseFloat(e.target.value))}
            className="config-input"
          />
        );
      case 'checkbox':
        return (
          <input
            type="checkbox"
            checked={value || false}
            onChange={(e) => updateNodeConfig(key, e.target.checked)}
            className="config-checkbox"
          />
        );
      default:
        return (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => updateNodeConfig(key, e.target.value)}
            className="config-input"
          />
        );
    }
  };

  return (
    <div className="node-inspector">
      <div className="inspector-header">
        <h3>Node Inspector</h3>
        <div className="node-type-badge" style={{ '--node-color': NODE_TYPES[node.type].color } as React.CSSProperties}>
          {NODE_TYPES[node.type].label}
        </div>
      </div>

      <div className="inspector-content">
        {/* General Section */}
        <div className="inspector-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('general')}
          >
            {expandedSections.has('general') ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <span>General</span>
          </div>
          {expandedSections.has('general') && (
            <div className="section-content">
              <div className="config-field">
                <label>Title</label>
                {renderConfigField('title', node.title)}
              </div>
              <div className="config-field">
                <label>Description</label>
                {renderConfigField('description', node.description, 'textarea')}
              </div>
            </div>
          )}
        </div>

        {/* Configuration Section */}
        <div className="inspector-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('config')}
          >
            {expandedSections.has('config') ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <span>Configuration</span>
          </div>
          {expandedSections.has('config') && (
            <div className="section-content">
              {renderNodeTypeSpecificFields(node)}
            </div>
          )}
        </div>

        {/* Advanced Section */}
        <div className="inspector-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('advanced')}
          >
            {expandedSections.has('advanced') ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <span>Advanced</span>
          </div>
          {expandedSections.has('advanced') && (
            <div className="section-content">
              <div className="config-field">
                <label>Retry on Error</label>
                {renderConfigField('retryOnError', node.config.retryOnError, 'checkbox')}
              </div>
              <div className="config-field">
                <label>Max Retries</label>
                {renderConfigField('maxRetries', node.config.maxRetries || 3, 'number')}
              </div>
              <div className="config-field">
                <label>Timeout (seconds)</label>
                {renderConfigField('timeout', node.config.timeout || 30, 'number')}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  function renderNodeTypeSpecificFields(node: WorkflowNode) {
    // This would be expanded based on each node type
    switch (node.type) {
      case 'trigger':
        return (
          <>
            <div className="config-field">
              <label>Trigger Type</label>
              <select
                value={node.config.triggerType || ''}
                onChange={(e) => updateNodeConfig('triggerType', e.target.value)}
                className="config-input"
              >
                <option value="">Select trigger type...</option>
                <option value="webhook">Webhook</option>
                <option value="schedule">Schedule</option>
                <option value="manual">Manual</option>
                <option value="event">Event</option>
              </select>
            </div>
            {node.config.triggerType === 'webhook' && (
              <div className="config-field">
                <label>Webhook URL</label>
                {renderConfigField('webhookUrl', node.config.webhookUrl)}
              </div>
            )}
            {node.config.triggerType === 'schedule' && (
              <div className="config-field">
                <label>Cron Expression</label>
                {renderConfigField('cronExpression', node.config.cronExpression)}
              </div>
            )}
          </>
        );
      case 'condition':
        return (
          <>
            <div className="config-field">
              <label>Condition Type</label>
              <select
                value={node.config.conditionType || ''}
                onChange={(e) => updateNodeConfig('conditionType', e.target.value)}
                className="config-input"
              >
                <option value="">Select condition type...</option>
                <option value="if">If Statement</option>
                <option value="switch">Switch</option>
                <option value="exists">Value Exists</option>
                <option value="compare">Compare Values</option>
              </select>
            </div>
            <div className="config-field">
              <label>Condition Expression</label>
              {renderConfigField('expression', node.config.expression, 'textarea')}
            </div>
          </>
        );
      case 'action':
        return (
          <>
            <div className="config-field">
              <label>Action Type</label>
              <select
                value={node.config.actionType || ''}
                onChange={(e) => updateNodeConfig('actionType', e.target.value)}
                className="config-input"
              >
                <option value="">Select action type...</option>
                <option value="api_call">API Call</option>
                <option value="email">Send Email</option>
                <option value="database">Database Operation</option>
                <option value="notification">Send Notification</option>
              </select>
            </div>
            {node.config.actionType === 'api_call' && (
              <>
                <div className="config-field">
                  <label>API Endpoint</label>
                  {renderConfigField('apiEndpoint', node.config.apiEndpoint)}
                </div>
                <div className="config-field">
                  <label>HTTP Method</label>
                  <select
                    value={node.config.httpMethod || 'GET'}
                    onChange={(e) => updateNodeConfig('httpMethod', e.target.value)}
                    className="config-input"
                  >
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="DELETE">DELETE</option>
                  </select>
                </div>
              </>
            )}
          </>
        );
      case 'delay':
        return (
          <>
            <div className="config-field">
              <label>Delay Duration (seconds)</label>
              {renderConfigField('duration', node.config.duration || 5, 'number')}
            </div>
            <div className="config-field">
              <label>Delay Type</label>
              <select
                value={node.config.delayType || 'fixed'}
                onChange={(e) => updateNodeConfig('delayType', e.target.value)}
                className="config-input"
              >
                <option value="fixed">Fixed Delay</option>
                <option value="dynamic">Dynamic Delay</option>
                <option value="until">Wait Until</option>
              </select>
            </div>
          </>
        );
      default:
        return (
          <div className="config-field">
            <label>Custom Configuration</label>
            {renderConfigField('customConfig', JSON.stringify(node.config, null, 2), 'textarea')}
          </div>
        );
    }
  }
};

// Main Workflow Builder Component
const WorkflowAutomationBuilder: React.FC = () => {
  const [workflow, setWorkflow] = useState<Workflow>({
    id: 'workflow-1',
    name: 'Untitled Workflow',
    nodes: [],
    connections: [],
    isActive: false,
    created: new Date().toISOString(),
    modified: new Date().toISOString()
  });

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionLog, setExecutionLog] = useState<string[]>([]);
  const [canvasElement, setCanvasElement] = useState<HTMLDivElement | null>(null);

  const selectedNode = workflow.nodes.find(node => node.id === selectedNodeId) || null;

  const handleAddNode = useCallback((nodeType: keyof typeof NODE_TYPES) => {
    const newNode: WorkflowNode = {
      id: `node_${Date.now()}`,
      type: nodeType,
      position: { x: 200 + Math.random() * 400, y: 100 + Math.random() * 300 },
      config: {},
      status: 'idle',
      title: `${NODE_TYPES[nodeType].label} ${workflow.nodes.length + 1}`,
      description: `New ${NODE_TYPES[nodeType].label.toLowerCase()} node`
    };

    setWorkflow(prev => ({
      ...prev,
      nodes: [...prev.nodes, newNode],
      modified: new Date().toISOString()
    }));

    setSelectedNodeId(newNode.id);
  }, [workflow.nodes.length]);

  const handleUpdateNode = useCallback((nodeId: string, updates: Partial<WorkflowNode>) => {
    setWorkflow(prev => ({
      ...prev,
      nodes: prev.nodes.map(node => 
        node.id === nodeId ? { ...node, ...updates } : node
      ),
      modified: new Date().toISOString()
    }));
  }, []);

  const handleDeleteNode = useCallback((nodeId: string) => {
    setWorkflow(prev => ({
      ...prev,
      nodes: prev.nodes.filter(node => node.id !== nodeId),
      connections: prev.connections.filter(
        conn => conn.source !== nodeId && conn.target !== nodeId
      ),
      modified: new Date().toISOString()
    }));

    if (selectedNodeId === nodeId) {
      setSelectedNodeId(null);
    }
  }, [selectedNodeId]);

  const handleUpdateNodePosition = useCallback((nodeId: string, position: { x: number; y: number }) => {
    handleUpdateNode(nodeId, { position });
  }, [handleUpdateNode]);

  const executeWorkflow = useCallback(async () => {
    if (workflow.nodes.length === 0) {
      alert('No nodes to execute');
      return;
    }

    setIsExecuting(true);
    setExecutionLog([]);

    const log = (message: string) => {
      setExecutionLog(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
    };

    log('Starting workflow execution...');

    // Reset all node statuses
    setWorkflow(prev => ({
      ...prev,
      nodes: prev.nodes.map(node => ({ ...node, status: 'idle' as const }))
    }));

    // Simple execution simulation
    const triggerNodes = workflow.nodes.filter(node => node.type === 'trigger');
    
    if (triggerNodes.length === 0) {
      log('Warning: No trigger nodes found');
      setIsExecuting(false);
      return;
    }

    for (const node of workflow.nodes) {
      log(`Executing ${node.title}...`);
      
      // Update node status to running
      setWorkflow(prev => ({
        ...prev,
        nodes: prev.nodes.map(n => 
          n.id === node.id ? { ...n, status: 'running' } : n
        )
      }));

      // Simulate execution delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

      // Simulate success/failure
      const success = Math.random() > 0.1; // 90% success rate
      const newStatus = success ? 'success' : 'error';

      setWorkflow(prev => ({
        ...prev,
        nodes: prev.nodes.map(n => 
          n.id === node.id ? { ...n, status: newStatus } : n
        )
      }));

      log(`${node.title} ${success ? 'completed successfully' : 'failed with error'}`);

      if (!success && !node.config.continueOnError) {
        log('Workflow stopped due to error');
        break;
      }
    }

    log('Workflow execution completed');
    setIsExecuting(false);
  }, [workflow.nodes]);

  const stopExecution = useCallback(() => {
    setIsExecuting(false);
    setExecutionLog(prev => [...prev, `${new Date().toLocaleTimeString()}: Workflow execution stopped by user`]);
    
    // Reset all running nodes to idle
    setWorkflow(prev => ({
      ...prev,
      nodes: prev.nodes.map(node => 
        node.status === 'running' ? { ...node, status: 'idle' } : node
      )
    }));
  }, []);

  const saveWorkflow = useCallback(() => {
    const workflowData = JSON.stringify(workflow, null, 2);
    const blob = new Blob([workflowData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${workflow.name.replace(/\s+/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [workflow]);

  // Canvas drop handling
  const [{ isOver }, drop] = useDrop(() => ({
    accept: ['nodeType', 'workflowNode'],
    drop: (item: any, monitor) => {
      const offset = monitor.getSourceClientOffset();
      if (!offset || !canvasElement) return;

      const canvasRect = canvasElement.getBoundingClientRect();
      const position = {
        x: offset.x - canvasRect.left,
        y: offset.y - canvasRect.top
      };

      if (item.nodeType) {
        // Adding new node from library
        const nodeType = item.nodeType as keyof typeof NODE_TYPES;
        const newNode: WorkflowNode = {
          id: `node_${Date.now()}`,
          type: nodeType,
          position,
          config: {},
          status: 'idle',
          title: `${NODE_TYPES[nodeType].label} ${workflow.nodes.length + 1}`,
          description: `New ${NODE_TYPES[nodeType].label.toLowerCase()} node`
        };

        setWorkflow(prev => ({
          ...prev,
          nodes: [...prev.nodes, newNode],
          modified: new Date().toISOString()
        }));

        setSelectedNodeId(newNode.id);
      } else if (item.nodeId) {
        // Moving existing node
        handleUpdateNodePosition(item.nodeId, position);
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }));

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="workflow-automation-builder">
        {/* Header */}
        <div className="builder-header">
          <div className="header-left">
            <h1>Workflow Automation Builder</h1>
            <input
              type="text"
              value={workflow.name}
              onChange={(e) => setWorkflow(prev => ({ ...prev, name: e.target.value }))}
              className="workflow-name-input"
            />
          </div>
          <div className="header-actions">
            <button
              onClick={isExecuting ? stopExecution : executeWorkflow}
              className={`action-button ${isExecuting ? 'stop' : 'play'}`}
              disabled={workflow.nodes.length === 0}
            >
              {isExecuting ? (
                <>
                  <Square size={16} />
                  Stop
                </>
              ) : (
                <>
                  <Play size={16} />
                  Execute
                </>
              )}
            </button>
            <button onClick={saveWorkflow} className="action-button save">
              <Save size={16} />
              Save
            </button>
          </div>
        </div>

        <div className="builder-content">
          {/* Node Library */}
          <div className="node-library">
            <h3>Node Library</h3>
            <div className="library-grid">
              {(Object.keys(NODE_TYPES) as Array<keyof typeof NODE_TYPES>).map(nodeType => (
                <NodeLibraryItem
                  key={nodeType}
                  nodeType={nodeType}
                  onAddNode={handleAddNode}
                />
              ))}
            </div>
          </div>

          {/* Workflow Canvas */}
          <div className="workflow-canvas-container">
            <div
              ref={(node) => {
                drop(node);
                setCanvasElement(node);
              }}
              className={`workflow-canvas ${isOver ? 'drag-over' : ''}`}
            >
              {workflow.nodes.map(node => (
                <WorkflowNodeComponent
                  key={node.id}
                  node={node}
                  isSelected={selectedNodeId === node.id}
                  onSelect={setSelectedNodeId}
                  onUpdatePosition={handleUpdateNodePosition}
                  onDelete={handleDeleteNode}
                />
              ))}

              {workflow.nodes.length === 0 && (
                <div className="empty-canvas">
                  <GitBranch size={48} className="empty-icon" />
                  <h3>Start Building Your Workflow</h3>
                  <p>Drag nodes from the library to begin creating your automation workflow</p>
                </div>
              )}
            </div>
          </div>

          {/* Node Inspector */}
          <NodeInspector
            node={selectedNode}
            onUpdateNode={handleUpdateNode}
          />
        </div>

        {/* Execution Log */}
        {(isExecuting || executionLog.length > 0) && (
          <div className="execution-log">
            <div className="log-header">
              <h3>Execution Log</h3>
              <button
                onClick={() => setExecutionLog([])}
                className="clear-log-button"
              >
                Clear
              </button>
            </div>
            <div className="log-content">
              {executionLog.map((entry, index) => (
                <div key={index} className="log-entry">
                  {entry}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DndProvider>
  );
};

export default WorkflowAutomationBuilder;