import React, { useState, useCallback, useRef } from 'react';
import {
  Play, Save, Settings,
  Plus, Trash2, Edit3, Copy, Clock,
  Mail, Bell, Database, Code, Filter, Search, Users,
  GitBranch, RotateCcw, CheckCircle,
  AlertTriangle, X, Maximize2, Minimize2,
  Activity, Target, Timer, Send, Webhook
} from 'lucide-react';
import './WorkflowAutomationBuilder.css';

interface WorkflowNode {
  id: string;
  type: 'trigger' | 'condition' | 'action' | 'delay' | 'branch' | 'merge';
  name: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  position: { x: number; y: number };
  config: {
    [key: string]: any;
  };
  connections: {
    inputs: string[];
    outputs: string[];
  };
  status: 'idle' | 'running' | 'success' | 'error' | 'waiting';
  lastRun?: string;
  executionTime?: number;
  errorMessage?: string;
}

interface WorkflowConnection {
  id: string;
  from: string;
  to: string;
  fromPort: string;
  toPort: string;
  condition?: string;
  label?: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  category: 'automation' | 'notification' | 'data_processing' | 'integration' | 'approval';
  status: 'active' | 'inactive' | 'draft';
  trigger: {
    type: 'entity_create' | 'entity_update' | 'entity_delete' | 'schedule' | 'webhook' | 'manual';
    config: any;
  };
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  variables: { [key: string]: any };
  settings: {
    timeout: number;
    retryCount: number;
    errorHandling: 'stop' | 'continue' | 'retry';
    logging: boolean;
  };
  stats: {
    totalRuns: number;
    successfulRuns: number;
    failedRuns: number;
    averageExecutionTime: number;
    lastRun?: string;
  };
  created_at: string;
  updated_at: string;
  created_by: string;
}

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  preview: string;
  tags: string[];
  complexity: 'simple' | 'intermediate' | 'advanced';
  estimatedTime: string;
}

interface WorkflowAutomationBuilderProps {
  workflow?: Workflow;
  onSave?: (workflow: Workflow) => void;
  onTest?: (workflow: Workflow) => void;
  onClose?: () => void;
  readonly?: boolean;
  availableEntities?: string[];
  availableActions?: string[];
}

export const WorkflowAutomationBuilder: React.FC<WorkflowAutomationBuilderProps> = ({
  workflow,
  onSave,
  onClose,
  readonly = false
}) => {
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow>(
    workflow || {
      id: `workflow_${Date.now()}`,
      name: 'New Workflow',
      description: '',
      category: 'automation',
      status: 'draft',
      trigger: { type: 'entity_create', config: {} },
      nodes: [],
      connections: [],
      variables: {},
      settings: {
        timeout: 300,
        retryCount: 3,
        errorHandling: 'stop',
        logging: true
      },
      stats: {
        totalRuns: 0,
        successfulRuns: 0,
        failedRuns: 0,
        averageExecutionTime: 0
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: 'current_user'
    }
  );

  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedConnection, setSelectedConnection] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [showNodeLibrary, setShowNodeLibrary] = useState(false);
  const [showTestResults, setShowTestResults] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [zoomLevel, setZoomLevel] = useState(1);
  const canvasRef = useRef<HTMLDivElement>(null);

  const nodeTemplates: WorkflowTemplate[] = [
    {
      id: 'entity_created_trigger',
      name: 'Entity Created',
      description: 'Triggers when a new entity is created',
      category: 'triggers',
      nodes: [{
        id: 'trigger_1',
        type: 'trigger',
        name: 'entity_created',
        title: 'Entity Created',
        description: 'Triggers when a new entity is created',
        icon: 'Plus',
        color: '#10b981',
        position: { x: 100, y: 100 },
        config: { entity_type: 'task' },
        connections: { inputs: [], outputs: ['success'] },
        status: 'idle'
      }],
      connections: [],
      preview: '/previews/entity-created.png',
      tags: ['trigger', 'entity', 'create'],
      complexity: 'simple',
      estimatedTime: '2 minutes'
    },
    {
      id: 'send_email_action',
      name: 'Send Email',
      description: 'Sends an email notification',
      category: 'actions',
      nodes: [{
        id: 'action_1',
        type: 'action',
        name: 'send_email',
        title: 'Send Email',
        description: 'Sends an email notification',
        icon: 'Mail',
        color: '#3b82f6',
        position: { x: 300, y: 100 },
        config: {
          to: '{{user.email}}',
          subject: 'Notification',
          template: 'default'
        },
        connections: { inputs: ['trigger'], outputs: ['success', 'error'] },
        status: 'idle'
      }],
      connections: [],
      preview: '/previews/send-email.png',
      tags: ['action', 'email', 'notification'],
      complexity: 'simple',
      estimatedTime: '3 minutes'
    },
    {
      id: 'condition_check',
      name: 'Condition Check',
      description: 'Evaluates a condition and branches the workflow',
      category: 'conditions',
      nodes: [{
        id: 'condition_1',
        type: 'condition',
        name: 'condition_check',
        title: 'Condition Check',
        description: 'Evaluates a condition and branches the workflow',
        icon: 'GitBranch',
        color: '#f59e0b',
        position: { x: 200, y: 100 },
        config: {
          condition: '{{task.priority}} > 3',
          operator: 'greater_than'
        },
        connections: { inputs: ['trigger'], outputs: ['true', 'false'] },
        status: 'idle'
      }],
      connections: [],
      preview: '/previews/condition-check.png',
      tags: ['condition', 'branch', 'logic'],
      complexity: 'intermediate',
      estimatedTime: '5 minutes'
    },
    {
      id: 'delay_action',
      name: 'Delay',
      description: 'Waits for a specified amount of time',
      category: 'utilities',
      nodes: [{
        id: 'delay_1',
        type: 'delay',
        name: 'delay',
        title: 'Delay',
        description: 'Waits for a specified amount of time',
        icon: 'Clock',
        color: '#8b5cf6',
        position: { x: 250, y: 100 },
        config: {
          duration: 300,
          unit: 'seconds'
        },
        connections: { inputs: ['trigger'], outputs: ['complete'] },
        status: 'idle'
      }],
      connections: [],
      preview: '/previews/delay.png',
      tags: ['delay', 'wait', 'timing'],
      complexity: 'simple',
      estimatedTime: '2 minutes'
    },
    {
      id: 'webhook_action',
      name: 'Webhook',
      description: 'Sends HTTP request to external service',
      category: 'integrations',
      nodes: [{
        id: 'webhook_1',
        type: 'action',
        name: 'webhook',
        title: 'Webhook',
        description: 'Sends HTTP request to external service',
        icon: 'Webhook',
        color: '#ef4444',
        position: { x: 350, y: 100 },
        config: {
          url: 'https://api.example.com/webhook',
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: '{{entity}}'
        },
        connections: { inputs: ['trigger'], outputs: ['success', 'error'] },
        status: 'idle'
      }],
      connections: [],
      preview: '/previews/webhook.png',
      tags: ['webhook', 'http', 'integration'],
      complexity: 'advanced',
      estimatedTime: '10 minutes'
    }
  ];

  const getNodeIcon = (iconName: string) => {
    const iconMap: { [key: string]: any } = {
      Plus, Mail, GitBranch, Clock, Webhook, Database, Users,
      Bell, Target, Send, Activity, Timer, Code, Filter
    };
    return iconMap[iconName] || Activity;
  };

  const addNode = useCallback((template: WorkflowTemplate, position: { x: number; y: number }) => {
    if (readonly) return;

    const newNode: WorkflowNode = {
      ...template.nodes[0],
      id: `node_${Date.now()}`,
      position
    };

    setCurrentWorkflow(prev => ({
      ...prev,
      nodes: [...prev.nodes, newNode],
      updated_at: new Date().toISOString()
    }));

    setSelectedNode(newNode.id);
    setShowNodeLibrary(false);
  }, [readonly]);

  const updateNode = useCallback((nodeId: string, updates: Partial<WorkflowNode>) => {
    if (readonly) return;

    setCurrentWorkflow(prev => ({
      ...prev,
      nodes: prev.nodes.map(node =>
        node.id === nodeId ? { ...node, ...updates } : node
      ),
      updated_at: new Date().toISOString()
    }));
  }, [readonly]);

  const deleteNode = useCallback((nodeId: string) => {
    if (readonly) return;

    setCurrentWorkflow(prev => ({
      ...prev,
      nodes: prev.nodes.filter(node => node.id !== nodeId),
      connections: prev.connections.filter(conn => 
        conn.from !== nodeId && conn.to !== nodeId
      ),
      updated_at: new Date().toISOString()
    }));

    if (selectedNode === nodeId) {
      setSelectedNode(null);
    }
  }, [selectedNode, readonly]);

  const addConnection = useCallback((from: string, to: string, fromPort: string, toPort: string) => {
    if (readonly) return;

    const newConnection: WorkflowConnection = {
      id: `connection_${Date.now()}`,
      from,
      to,
      fromPort,
      toPort
    };

    setCurrentWorkflow(prev => ({
      ...prev,
      connections: [...prev.connections, newConnection],
      updated_at: new Date().toISOString()
    }));
  }, [readonly]);

  const deleteConnection = useCallback((connectionId: string) => {
    if (readonly) return;

    setCurrentWorkflow(prev => ({
      ...prev,
      connections: prev.connections.filter(conn => conn.id !== connectionId),
      updated_at: new Date().toISOString()
    }));
  }, [readonly]);

  const handleMouseDown = useCallback((e: React.MouseEvent, nodeId: string) => {
    if (readonly) return;

    e.preventDefault();
    const node = currentWorkflow.nodes.find(n => n.id === nodeId);
    if (!node) return;

    setIsDragging(nodeId);
    setDragOffset({
      x: e.clientX - node.position.x,
      y: e.clientY - node.position.y
    });
  }, [currentWorkflow.nodes, readonly]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging || readonly) return;

    e.preventDefault();
    const newPosition = {
      x: Math.max(0, (e.clientX - dragOffset.x) / zoomLevel),
      y: Math.max(0, (e.clientY - dragOffset.y) / zoomLevel)
    };

    updateNode(isDragging, { position: newPosition });
  }, [isDragging, dragOffset, zoomLevel, updateNode, readonly]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(null);
    setDragOffset({ x: 0, y: 0 });
  }, []);

  const runWorkflow = useCallback(async () => {
    if (readonly) return;

    setIsRunning(true);
    setShowTestResults(true);

    // Simulate workflow execution
    const nodes = [...currentWorkflow.nodes];
    
    for (let i = 0; i < nodes.length; i++) {
      updateNode(nodes[i].id, { status: 'running' });
      
      // Simulate execution time
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      // Random success/failure for demo
      const success = Math.random() > 0.2;
      updateNode(nodes[i].id, {
        status: success ? 'success' : 'error',
        lastRun: new Date().toISOString(),
        executionTime: Math.floor(1000 + Math.random() * 2000),
        errorMessage: success ? undefined : 'Simulated error for demonstration'
      });

      if (!success && currentWorkflow.settings.errorHandling === 'stop') {
        break;
      }
    }

    setIsRunning(false);
  }, [currentWorkflow, updateNode, readonly]);

  const filteredTemplates = nodeTemplates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const selectedNodeData = selectedNode ? currentWorkflow.nodes.find(n => n.id === selectedNode) : null;

  return (
    <div className="workflow-automation-builder">
      <div className="workflow-header">
        <div className="header-left">
          <div className="workflow-info">
            <input
              type="text"
              value={currentWorkflow.name}
              onChange={(e) => setCurrentWorkflow(prev => ({ ...prev, name: e.target.value }))}
              className="workflow-title-input"
              disabled={readonly}
              placeholder="Workflow Name"
            />
            <div className="workflow-meta">
              <span className={`status-badge ${currentWorkflow.status}`}>
                {currentWorkflow.status.toUpperCase()}
              </span>
              <span className="node-count">
                {currentWorkflow.nodes.length} nodes
              </span>
              <span className="last-updated">
                Updated {new Date(currentWorkflow.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        <div className="header-actions">
          <button
            className="action-btn secondary"
            onClick={() => setShowNodeLibrary(true)}
            disabled={readonly}
          >
            <Plus size={16} />
            Add Node
          </button>
          
          <button
            className="action-btn secondary"
            onClick={() => console.log('Settings opened')}
            disabled={readonly}
          >
            <Settings size={16} />
            Settings
          </button>
          
          <div className="action-divider" />
          
          <button
            className={`action-btn ${isRunning ? 'warning' : 'primary'}`}
            onClick={runWorkflow}
            disabled={readonly || isRunning || currentWorkflow.nodes.length === 0}
          >
            {isRunning ? (
              <>
                <div className="spinner" />
                Running...
              </>
            ) : (
              <>
                <Play size={16} />
                Test Run
              </>
            )}
          </button>
          
          <button
            className="action-btn primary"
            onClick={() => onSave?.(currentWorkflow)}
            disabled={readonly}
          >
            <Save size={16} />
            Save
          </button>

          {onClose && (
            <button className="close-btn" onClick={onClose}>
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      <div className="workflow-workspace">
        <div
          ref={canvasRef}
          className="workflow-canvas"
          style={{ transform: `scale(${zoomLevel})` }}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <div className="canvas-grid" />
          
          {/* Render connections */}
          <svg className="connections-layer" width="100%" height="100%">
            {currentWorkflow.connections.map(connection => {
              const fromNode = currentWorkflow.nodes.find(n => n.id === connection.from);
              const toNode = currentWorkflow.nodes.find(n => n.id === connection.to);
              
              if (!fromNode || !toNode) return null;
              
              const fromX = fromNode.position.x + 125; // Half of node width
              const fromY = fromNode.position.y + 100; // Node height
              const toX = toNode.position.x + 125;
              const toY = toNode.position.y;
              
              return (
                <g key={connection.id}>
                  <path
                    d={`M ${fromX} ${fromY} Q ${fromX} ${fromY + (toY - fromY) / 2} ${toX} ${toY}`}
                    stroke="#3b82f6"
                    strokeWidth="2"
                    fill="none"
                    className={`connection ${selectedConnection === connection.id ? 'selected' : ''}`}
                    onClick={() => setSelectedConnection(connection.id)}
                  />
                  <circle
                    cx={toX}
                    cy={toY}
                    r="4"
                    fill="#3b82f6"
                  />
                </g>
              );
            })}
          </svg>
          
          {/* Render nodes */}
          {currentWorkflow.nodes.map(node => {
            const NodeIcon = getNodeIcon(node.icon);
            
            return (
              <div
                key={node.id}
                className={`workflow-node ${node.type} ${selectedNode === node.id ? 'selected' : ''} ${isDragging === node.id ? 'dragging' : ''}`}
                style={{
                  left: node.position.x,
                  top: node.position.y,
                  borderColor: node.color
                }}
                onClick={() => setSelectedNode(node.id)}
                onMouseDown={(e) => handleMouseDown(e, node.id)}
              >
                <div className="node-header" style={{ backgroundColor: node.color }}>
                  <div className="node-icon">
                    <NodeIcon size={16} />
                  </div>
                  <span className="node-title">{node.title}</span>
                  <div className={`node-status ${node.status}`}>
                    {node.status === 'running' && <div className="spinner small" />}
                    {node.status === 'success' && <CheckCircle size={12} />}
                    {node.status === 'error' && <AlertTriangle size={12} />}
                    {node.status === 'waiting' && <Clock size={12} />}
                  </div>
                </div>
                
                <div className="node-content">
                  <p className="node-description">{node.description}</p>
                  
                  {node.lastRun && (
                    <div className="node-stats">
                      <span>Last run: {new Date(node.lastRun).toLocaleTimeString()}</span>
                      {node.executionTime && (
                        <span>Time: {node.executionTime}ms</span>
                      )}
                    </div>
                  )}
                  
                  {node.errorMessage && (
                    <div className="node-error">
                      <AlertTriangle size={12} />
                      <span>{node.errorMessage}</span>
                    </div>
                  )}
                </div>
                
                <div className="node-actions">
                  <button
                    className="node-action-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Edit node
                    }}
                    disabled={readonly}
                  >
                    <Edit3 size={12} />
                  </button>
                  <button
                    className="node-action-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Copy node
                    }}
                    disabled={readonly}
                  >
                    <Copy size={12} />
                  </button>
                  <button
                    className="node-action-btn delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNode(node.id);
                    }}
                    disabled={readonly}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            );
          })}
          
          {/* Empty state */}
          {currentWorkflow.nodes.length === 0 && (
            <div className="empty-canvas">
              <div className="empty-icon">
                <Activity size={48} />
              </div>
              <h3>Start Building Your Workflow</h3>
              <p>Add nodes from the library to create your automation workflow</p>
              <button
                className="action-btn primary"
                onClick={() => setShowNodeLibrary(true)}
                disabled={readonly}
              >
                <Plus size={16} />
                Add First Node
              </button>
            </div>
          )}
        </div>

        {/* Canvas Controls */}
        <div className="canvas-controls">
          <button
            className="control-btn"
            onClick={() => setZoomLevel(prev => Math.min(prev + 0.1, 2))}
          >
            <Maximize2 size={16} />
          </button>
          <span className="zoom-level">{Math.round(zoomLevel * 100)}%</span>
          <button
            className="control-btn"
            onClick={() => setZoomLevel(prev => Math.max(prev - 0.1, 0.5))}
          >
            <Minimize2 size={16} />
          </button>
          <button
            className="control-btn"
            onClick={() => setZoomLevel(1)}
          >
            <RotateCcw size={16} />
          </button>
        </div>

        {/* Node Inspector */}
        {selectedNodeData && (
          <div className="node-inspector">
            <div className="inspector-header">
              <h3>Node Configuration</h3>
              <button
                className="close-btn"
                onClick={() => setSelectedNode(null)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="inspector-content">
              <div className="inspector-section">
                <h4>Basic Information</h4>
                <div className="form-grid">
                  <div className="form-field">
                    <label>Title</label>
                    <input
                      type="text"
                      value={selectedNodeData.title}
                      onChange={(e) => updateNode(selectedNode!, { title: e.target.value })}
                      disabled={readonly}
                    />
                  </div>
                  <div className="form-field full-width">
                    <label>Description</label>
                    <textarea
                      value={selectedNodeData.description}
                      onChange={(e) => updateNode(selectedNode!, { description: e.target.value })}
                      disabled={readonly}
                      rows={2}
                    />
                  </div>
                </div>
              </div>

              <div className="inspector-section">
                <h4>Configuration</h4>
                <div className="config-form">
                  {Object.entries(selectedNodeData.config).map(([key, value]) => (
                    <div key={key} className="form-field">
                      <label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
                      <input
                        type="text"
                        value={String(value)}
                        onChange={(e) => updateNode(selectedNode!, {
                          config: { ...selectedNodeData.config, [key]: e.target.value }
                        })}
                        disabled={readonly}
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="inspector-section">
                <h4>Execution Status</h4>
                <div className="status-info">
                  <div className="status-item">
                    <span>Status:</span>
                    <span className={`status-value ${selectedNodeData.status}`}>
                      {selectedNodeData.status.toUpperCase()}
                    </span>
                  </div>
                  {selectedNodeData.lastRun && (
                    <div className="status-item">
                      <span>Last Run:</span>
                      <span>{new Date(selectedNodeData.lastRun).toLocaleString()}</span>
                    </div>
                  )}
                  {selectedNodeData.executionTime && (
                    <div className="status-item">
                      <span>Execution Time:</span>
                      <span>{selectedNodeData.executionTime}ms</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Node Library Modal */}
      {showNodeLibrary && (
        <div className="modal-overlay">
          <div className="node-library">
            <div className="library-header">
              <h3>Node Library</h3>
              <button
                className="close-btn"
                onClick={() => setShowNodeLibrary(false)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="library-filters">
              <div className="search-box">
                <Search size={16} />
                <input
                  type="text"
                  placeholder="Search nodes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="all">All Categories</option>
                <option value="triggers">Triggers</option>
                <option value="conditions">Conditions</option>
                <option value="actions">Actions</option>
                <option value="utilities">Utilities</option>
                <option value="integrations">Integrations</option>
              </select>
            </div>

            <div className="library-grid">
              {filteredTemplates.map(template => {
                const NodeIcon = getNodeIcon(template.nodes[0].icon);
                
                return (
                  <div
                    key={template.id}
                    className="library-node"
                    onClick={() => addNode(template, { x: 200, y: 200 })}
                  >
                    <div className="library-node-icon" style={{ backgroundColor: template.nodes[0].color }}>
                      <NodeIcon size={20} />
                    </div>
                    <div className="library-node-content">
                      <h4>{template.name}</h4>
                      <p>{template.description}</p>
                      <div className="library-node-meta">
                        <span className="complexity">{template.complexity}</span>
                        <span className="time">{template.estimatedTime}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Test Results Modal */}
      {showTestResults && (
        <div className="modal-overlay">
          <div className="test-results">
            <div className="results-header">
              <h3>Workflow Test Results</h3>
              <button
                className="close-btn"
                onClick={() => setShowTestResults(false)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="results-content">
              <div className="execution-summary">
                <div className="summary-stats">
                  <div className="stat">
                    <span className="stat-value">{currentWorkflow.nodes.filter(n => n.status === 'success').length}</span>
                    <span className="stat-label">Successful</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{currentWorkflow.nodes.filter(n => n.status === 'error').length}</span>
                    <span className="stat-label">Failed</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">
                      {currentWorkflow.nodes.reduce((sum, n) => sum + (n.executionTime || 0), 0)}ms
                    </span>
                    <span className="stat-label">Total Time</span>
                  </div>
                </div>
              </div>

              <div className="execution-log">
                <h4>Execution Log</h4>
                <div className="log-entries">
                  {currentWorkflow.nodes.map(node => (
                    <div key={node.id} className={`log-entry ${node.status}`}>
                      <div className="log-icon">
                        {React.createElement(getNodeIcon(node.icon), { size: 16 })}
                      </div>
                      <div className="log-content">
                        <span className="log-title">{node.title}</span>
                        <span className="log-status">{node.status}</span>
                        {node.executionTime && (
                          <span className="log-time">{node.executionTime}ms</span>
                        )}
                        {node.errorMessage && (
                          <span className="log-error">{node.errorMessage}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};