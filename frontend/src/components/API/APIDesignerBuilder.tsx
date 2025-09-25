import React, { useState } from 'react';
import { 
  Plus, Save, Play, Download, X, Search,
  Code, Copy, Edit3,
  ChevronDown, ChevronRight, Check, AlertCircle,
  Shield,
  BookOpen, TestTube2, Send, Trash2,
  SortAsc, SortDesc, RefreshCw, ExternalLink
} from 'lucide-react';

// Types for API Designer
interface APIEndpoint {
  id: string;
  name: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  description: string;
  tags: string[];
  parameters: APIParameter[];
  requestBody?: APIRequestBody;
  responses: APIResponse[];
  authentication: 'none' | 'apikey' | 'bearer' | 'basic' | 'oauth';
  rateLimit?: number;
  deprecated?: boolean;
  version: string;
  lastModified: string;
  author: string;
  testResults?: TestResult[];
}

interface APIParameter {
  id: string;
  name: string;
  in: 'query' | 'path' | 'header' | 'cookie';
  type: string;
  required: boolean;
  description: string;
  example?: any;
  schema?: any;
  enum?: string[];
}

interface APIRequestBody {
  required: boolean;
  contentType: 'application/json' | 'application/xml' | 'text/plain' | 'multipart/form-data';
  schema: any;
  examples: Record<string, any>;
}

interface APIResponse {
  statusCode: number;
  description: string;
  contentType: string;
  schema?: any;
  examples: Record<string, any>;
  headers?: Record<string, string>;
}

interface TestResult {
  id: string;
  timestamp: string;
  status: 'success' | 'error' | 'timeout';
  responseTime: number;
  statusCode: number;
  response?: any;
  error?: string;
}

interface APIProject {
  id: string;
  name: string;
  description: string;
  version: string;
  baseUrl: string;
  endpoints: APIEndpoint[];
  environments: Environment[];
  tags: string[];
  authentication: AuthConfig;
  documentation: DocumentationConfig;
  createdAt: string;
  updatedAt: string;
  author: string;
}

interface Environment {
  id: string;
  name: string;
  baseUrl: string;
  variables: Record<string, string>;
  headers: Record<string, string>;
}

interface AuthConfig {
  type: 'none' | 'apikey' | 'bearer' | 'basic' | 'oauth';
  config: Record<string, any>;
}

interface DocumentationConfig {
  title: string;
  description: string;
  version: string;
  contact: {
    name: string;
    email: string;
    url: string;
  };
  license: {
    name: string;
    url: string;
  };
  servers: Array<{
    url: string;
    description: string;
  }>;
}

const APIDesignerBuilder: React.FC = () => {
  // Core state
  const [project, setProject] = useState<APIProject>({
    id: '1',
    name: 'TeamFlow API v2',
    description: 'Advanced task management and collaboration platform API',
    version: '2.0.0',
    baseUrl: 'https://api.teamflow.com/v2',
    endpoints: [
      {
        id: '1',
        name: 'Get Tasks',
        method: 'GET',
        path: '/tasks',
        description: 'Retrieve a list of tasks with filtering and pagination',
        tags: ['tasks', 'core'],
        parameters: [
          {
            id: '1',
            name: 'limit',
            in: 'query',
            type: 'integer',
            required: false,
            description: 'Maximum number of tasks to return',
            example: 20
          },
          {
            id: '2',
            name: 'status',
            in: 'query',
            type: 'string',
            required: false,
            description: 'Filter tasks by status',
            enum: ['todo', 'in-progress', 'completed', 'cancelled']
          }
        ],
        responses: [
          {
            statusCode: 200,
            description: 'Successfully retrieved tasks',
            contentType: 'application/json',
            examples: {
              default: {
                tasks: [
                  {
                    id: 'task_123',
                    title: 'Complete API documentation',
                    status: 'in-progress',
                    priority: 'high',
                    assignee: 'user_456',
                    created_at: '2024-01-15T10:30:00Z'
                  }
                ],
                total: 1,
                page: 1,
                limit: 20
              }
            }
          },
          {
            statusCode: 400,
            description: 'Invalid query parameters',
            contentType: 'application/json',
            examples: {
              error: {
                error: 'invalid_parameter',
                message: 'The status parameter must be one of: todo, in-progress, completed, cancelled'
              }
            }
          }
        ],
        authentication: 'bearer',
        version: '2.0.0',
        lastModified: '2024-01-15T14:30:00Z',
        author: 'API Team'
      },
      {
        id: '2',
        name: 'Create Task',
        method: 'POST',
        path: '/tasks',
        description: 'Create a new task in the system',
        tags: ['tasks', 'core'],
        parameters: [],
        requestBody: {
          required: true,
          contentType: 'application/json',
          schema: {
            type: 'object',
            properties: {
              title: { type: 'string', description: 'Task title' },
              description: { type: 'string', description: 'Task description' },
              priority: { type: 'string', enum: ['low', 'medium', 'high', 'urgent'] },
              assignee_id: { type: 'string', description: 'User ID of assignee' },
              due_date: { type: 'string', format: 'date-time' }
            },
            required: ['title']
          },
          examples: {
            default: {
              title: 'Complete API documentation',
              description: 'Write comprehensive API documentation for v2 endpoints',
              priority: 'high',
              assignee_id: 'user_456',
              due_date: '2024-02-01T12:00:00Z'
            }
          }
        },
        responses: [
          {
            statusCode: 201,
            description: 'Task created successfully',
            contentType: 'application/json',
            examples: {
              success: {
                id: 'task_789',
                title: 'Complete API documentation',
                status: 'todo',
                created_at: '2024-01-15T15:00:00Z'
              }
            }
          }
        ],
        authentication: 'bearer',
        version: '2.0.0',
        lastModified: '2024-01-15T15:00:00Z',
        author: 'API Team'
      }
    ],
    environments: [
      {
        id: '1',
        name: 'Development',
        baseUrl: 'https://dev-api.teamflow.com/v2',
        variables: { version: 'v2', timeout: '30000' },
        headers: { 'X-Environment': 'development' }
      },
      {
        id: '2',
        name: 'Production',
        baseUrl: 'https://api.teamflow.com/v2',
        variables: { version: 'v2', timeout: '10000' },
        headers: { 'X-Environment': 'production' }
      }
    ],
    tags: ['tasks', 'users', 'projects', 'core', 'auth'],
    authentication: {
      type: 'bearer',
      config: { tokenPrefix: 'Bearer', headerName: 'Authorization' }
    },
    documentation: {
      title: 'TeamFlow API',
      description: 'Enterprise task management and collaboration platform',
      version: '2.0.0',
      contact: {
        name: 'API Support',
        email: 'api-support@teamflow.com',
        url: 'https://teamflow.com/support'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      },
      servers: [
        { url: 'https://api.teamflow.com/v2', description: 'Production server' },
        { url: 'https://staging-api.teamflow.com/v2', description: 'Staging server' }
      ]
    },
    createdAt: '2024-01-10T09:00:00Z',
    updatedAt: '2024-01-15T15:00:00Z',
    author: 'API Team'
  });

  // UI state
  const [selectedEndpoint, setSelectedEndpoint] = useState<string | null>('1');
  const [selectedTab, setSelectedTab] = useState<'design' | 'test' | 'docs' | 'export'>('design');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<'name' | 'method' | 'modified'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showEndpointModal, setShowEndpointModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [isExecutingTest, setIsExecutingTest] = useState(false);
  const [selectedEnvironment, setSelectedEnvironment] = useState('1');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    parameters: true,
    requestBody: true,
    responses: true,
    authentication: false
  });

  // Get selected endpoint
  const selectedEndpointData = selectedEndpoint 
    ? project.endpoints.find(e => e.id === selectedEndpoint)
    : null;

  // Get selected environment
  const selectedEnvironmentData = project.environments.find(e => e.id === selectedEnvironment);

  // Filter and sort endpoints
  const filteredEndpoints = project.endpoints
    .filter(endpoint => {
      const matchesSearch = endpoint.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           endpoint.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           endpoint.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesTags = selectedTags.length === 0 || 
                         selectedTags.some(tag => endpoint.tags.includes(tag));
      return matchesSearch && matchesTags;
    })
    .sort((a, b) => {
      let aValue: any, bValue: any;
      switch (sortBy) {
        case 'name':
          aValue = a.name;
          bValue = b.name;
          break;
        case 'method':
          aValue = a.method;
          bValue = b.method;
          break;
        case 'modified':
          aValue = new Date(a.lastModified);
          bValue = new Date(b.lastModified);
          break;
        default:
          return 0;
      }
      
      if (sortOrder === 'desc') {
        return aValue < bValue ? 1 : -1;
      }
      return aValue > bValue ? 1 : -1;
    });

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Execute API test
  const executeTest = async (endpoint: APIEndpoint) => {
    setIsExecutingTest(true);
    
    // Simulate API test execution
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const testResult: TestResult = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      status: Math.random() > 0.3 ? 'success' : 'error',
      responseTime: Math.floor(Math.random() * 1000) + 100,
      statusCode: Math.random() > 0.3 ? 200 : 404,
      response: Math.random() > 0.3 ? { success: true, data: [] } : undefined,
      error: Math.random() > 0.3 ? undefined : 'Connection timeout after 5000ms'
    };

    // Update endpoint with test result
    setProject(prev => ({
      ...prev,
      endpoints: prev.endpoints.map(ep =>
        ep.id === endpoint.id
          ? { ...ep, testResults: [testResult, ...(ep.testResults || [])].slice(0, 10) }
          : ep
      )
    }));

    setIsExecutingTest(false);
    setShowTestModal(true);
  };

  // Get method color
  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return '#10b981';
      case 'POST': return '#3b82f6';
      case 'PUT': return '#f59e0b';
      case 'DELETE': return '#ef4444';
      case 'PATCH': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#10b981';
      case 'error': return '#ef4444';
      case 'timeout': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  return (
    <div className="api-designer-builder">
      {/* Header */}
      <div className="designer-header">
        <div className="header-left">
          <div className="project-info">
            <input
              type="text"
              value={project.name}
              onChange={(e) => setProject(prev => ({ ...prev, name: e.target.value }))}
              className="project-title-input"
              placeholder="API Project Name"
            />
            <div className="project-meta">
              <span className="version-badge">v{project.version}</span>
              <span className="endpoint-count">{project.endpoints.length} endpoints</span>
              <span className="last-updated">Updated {new Date(project.updatedAt).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        <div className="header-actions">
          <button 
            className="action-btn secondary"
            onClick={() => setShowEndpointModal(true)}
          >
            <Plus size={16} />
            New Endpoint
          </button>
          
          <div className="action-divider"></div>
          
          <select
            value={selectedEnvironment}
            onChange={(e) => setSelectedEnvironment(e.target.value)}
            className="env-selector"
          >
            {project.environments.map(env => (
              <option key={env.id} value={env.id}>{env.name}</option>
            ))}
          </select>

          <button className="action-btn secondary">
            <Save size={16} />
            Save
          </button>

          <button 
            className="action-btn primary"
            onClick={() => selectedEndpointData && executeTest(selectedEndpointData)}
            disabled={!selectedEndpointData || isExecutingTest}
          >
            {isExecutingTest ? (
              <>
                <div className="spinner small" />
                Testing...
              </>
            ) : (
              <>
                <Play size={16} />
                Test
              </>
            )}
          </button>

          <button 
            className="action-btn secondary"
            onClick={() => setShowExportModal(true)}
          >
            <Download size={16} />
            Export
          </button>

          <div className="action-divider"></div>

          <button className="close-btn">
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="designer-workspace">
        {/* Endpoint Sidebar */}
        <div className="endpoints-sidebar">
          <div className="sidebar-header">
            <div className="sidebar-tabs">
              <button 
                className={`tab ${selectedTab === 'design' ? 'active' : ''}`}
                onClick={() => setSelectedTab('design')}
              >
                <Code size={16} />
                Design
              </button>
              <button 
                className={`tab ${selectedTab === 'test' ? 'active' : ''}`}
                onClick={() => setSelectedTab('test')}
              >
                <TestTube2 size={16} />
                Test
              </button>
              <button 
                className={`tab ${selectedTab === 'docs' ? 'active' : ''}`}
                onClick={() => setSelectedTab('docs')}
              >
                <BookOpen size={16} />
                Docs
              </button>
            </div>
          </div>

          <div className="sidebar-filters">
            <div className="search-box">
              <Search size={16} />
              <input
                type="text"
                placeholder="Search endpoints..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="filter-controls">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="sort-select"
              >
                <option value="name">Sort by Name</option>
                <option value="method">Sort by Method</option>
                <option value="modified">Sort by Modified</option>
              </select>
              
              <button
                className="sort-order-btn"
                onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
              </button>
            </div>

            <div className="tag-filters">
              {project.tags.map(tag => (
                <button
                  key={tag}
                  className={`tag-filter ${selectedTags.includes(tag) ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedTags(prev =>
                      prev.includes(tag)
                        ? prev.filter(t => t !== tag)
                        : [...prev, tag]
                    );
                  }}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          <div className="endpoints-list">
            {filteredEndpoints.map(endpoint => (
              <div
                key={endpoint.id}
                className={`endpoint-item ${selectedEndpoint === endpoint.id ? 'selected' : ''}`}
                onClick={() => setSelectedEndpoint(endpoint.id)}
              >
                <div className="endpoint-header">
                  <div 
                    className="method-badge"
                    style={{ backgroundColor: getMethodColor(endpoint.method) }}
                  >
                    {endpoint.method}
                  </div>
                  <div className="endpoint-info">
                    <div className="endpoint-name">{endpoint.name}</div>
                    <div className="endpoint-path">{endpoint.path}</div>
                  </div>
                  {endpoint.deprecated && (
                    <div className="deprecated-badge">Deprecated</div>
                  )}
                </div>
                
                <div className="endpoint-meta">
                  <div className="endpoint-tags">
                    {endpoint.tags.slice(0, 2).map(tag => (
                      <span key={tag} className="endpoint-tag">{tag}</span>
                    ))}
                    {endpoint.tags.length > 2 && (
                      <span className="endpoint-tag more">+{endpoint.tags.length - 2}</span>
                    )}
                  </div>
                  <div className="endpoint-status">
                    {endpoint.testResults && endpoint.testResults[0] && (
                      <div 
                        className="test-status"
                        style={{ color: getStatusColor(endpoint.testResults[0].status) }}
                      >
                        {endpoint.testResults[0].status === 'success' ? <Check size={12} /> : <AlertCircle size={12} />}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Editor */}
        <div className="main-editor">
          {selectedTab === 'design' && selectedEndpointData && (
            <div className="endpoint-designer">
              <div className="designer-header-section">
                <div className="endpoint-title">
                  <div 
                    className="method-badge large"
                    style={{ backgroundColor: getMethodColor(selectedEndpointData.method) }}
                  >
                    {selectedEndpointData.method}
                  </div>
                  <div className="title-info">
                    <input
                      type="text"
                      value={selectedEndpointData.name}
                      className="endpoint-name-input"
                      placeholder="Endpoint Name"
                    />
                    <input
                      type="text"
                      value={selectedEndpointData.path}
                      className="endpoint-path-input"
                      placeholder="/api/endpoint"
                    />
                  </div>
                </div>
                
                <div className="endpoint-description">
                  <textarea
                    value={selectedEndpointData.description}
                    placeholder="Endpoint description..."
                    className="description-input"
                  />
                </div>

                <div className="endpoint-tags">
                  {selectedEndpointData.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                  <button className="add-tag-btn">
                    <Plus size={12} />
                    Add Tag
                  </button>
                </div>
              </div>

              <div className="designer-sections">
                {/* Parameters Section */}
                <div className="designer-section">
                  <div 
                    className="section-header"
                    onClick={() => toggleSection('parameters')}
                  >
                    <div className="section-title">
                      {expandedSections.parameters ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                      Parameters
                      <span className="param-count">({selectedEndpointData.parameters.length})</span>
                    </div>
                    <button className="add-param-btn">
                      <Plus size={14} />
                    </button>
                  </div>
                  
                  {expandedSections.parameters && (
                    <div className="section-content">
                      {selectedEndpointData.parameters.map(param => (
                        <div key={param.id} className="parameter-item">
                          <div className="param-header">
                            <div className="param-info">
                              <span className="param-name">{param.name}</span>
                              <span className={`param-location ${param.in}`}>{param.in}</span>
                              <span className="param-type">{param.type}</span>
                              {param.required && <span className="required-badge">required</span>}
                            </div>
                            <div className="param-actions">
                              <button className="param-action-btn">
                                <Edit3 size={12} />
                              </button>
                              <button className="param-action-btn delete">
                                <Trash2 size={12} />
                              </button>
                            </div>
                          </div>
                          <div className="param-description">{param.description}</div>
                          {param.example && (
                            <div className="param-example">
                              <code>{JSON.stringify(param.example)}</code>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Request Body Section */}
                {selectedEndpointData.requestBody && (
                  <div className="designer-section">
                    <div 
                      className="section-header"
                      onClick={() => toggleSection('requestBody')}
                    >
                      <div className="section-title">
                        {expandedSections.requestBody ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                        Request Body
                        {selectedEndpointData.requestBody.required && (
                          <span className="required-badge">required</span>
                        )}
                      </div>
                    </div>
                    
                    {expandedSections.requestBody && (
                      <div className="section-content">
                        <div className="content-type-selector">
                          <label>Content Type:</label>
                          <select value={selectedEndpointData.requestBody.contentType}>
                            <option value="application/json">application/json</option>
                            <option value="application/xml">application/xml</option>
                            <option value="text/plain">text/plain</option>
                            <option value="multipart/form-data">multipart/form-data</option>
                          </select>
                        </div>

                        <div className="schema-editor">
                          <div className="schema-header">
                            <span>Schema</span>
                            <div className="schema-actions">
                              <button className="schema-btn">
                                <Code size={14} />
                                Edit Schema
                              </button>
                            </div>
                          </div>
                          <pre className="schema-preview">
                            {JSON.stringify(selectedEndpointData.requestBody.schema, null, 2)}
                          </pre>
                        </div>

                        <div className="examples-section">
                          <div className="examples-header">
                            <span>Examples</span>
                            <button className="add-example-btn">
                              <Plus size={14} />
                              Add Example
                            </button>
                          </div>
                          {Object.entries(selectedEndpointData.requestBody.examples).map(([name, example]) => (
                            <div key={name} className="example-item">
                              <div className="example-header">
                                <span className="example-name">{name}</span>
                                <div className="example-actions">
                                  <button className="example-action-btn">
                                    <Copy size={12} />
                                  </button>
                                  <button className="example-action-btn">
                                    <Edit3 size={12} />
                                  </button>
                                </div>
                              </div>
                              <pre className="example-content">
                                {JSON.stringify(example, null, 2)}
                              </pre>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Responses Section */}
                <div className="designer-section">
                  <div 
                    className="section-header"
                    onClick={() => toggleSection('responses')}
                  >
                    <div className="section-title">
                      {expandedSections.responses ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                      Responses
                      <span className="response-count">({selectedEndpointData.responses.length})</span>
                    </div>
                    <button className="add-response-btn">
                      <Plus size={14} />
                    </button>
                  </div>
                  
                  {expandedSections.responses && (
                    <div className="section-content">
                      {selectedEndpointData.responses.map((response, index) => (
                        <div key={index} className="response-item">
                          <div className="response-header">
                            <div className="response-info">
                              <span 
                                className="status-code"
                                style={{ 
                                  color: response.statusCode < 300 ? '#10b981' : 
                                         response.statusCode < 400 ? '#f59e0b' : '#ef4444' 
                                }}
                              >
                                {response.statusCode}
                              </span>
                              <span className="response-description">{response.description}</span>
                            </div>
                            <div className="response-actions">
                              <button className="response-action-btn">
                                <Edit3 size={12} />
                              </button>
                              <button className="response-action-btn delete">
                                <Trash2 size={12} />
                              </button>
                            </div>
                          </div>
                          
                          <div className="response-details">
                            <div className="content-type">
                              Content-Type: <code>{response.contentType}</code>
                            </div>
                            
                            {Object.entries(response.examples).map(([name, example]) => (
                              <div key={name} className="response-example">
                                <div className="example-header">
                                  <span className="example-name">{name}</span>
                                  <button className="copy-btn">
                                    <Copy size={12} />
                                  </button>
                                </div>
                                <pre className="example-content">
                                  {JSON.stringify(example, null, 2)}
                                </pre>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Authentication Section */}
                <div className="designer-section">
                  <div 
                    className="section-header"
                    onClick={() => toggleSection('authentication')}
                  >
                    <div className="section-title">
                      {expandedSections.authentication ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                      Authentication
                      <span className="auth-type">{selectedEndpointData.authentication}</span>
                    </div>
                  </div>
                  
                  {expandedSections.authentication && (
                    <div className="section-content">
                      <div className="auth-selector">
                        <select value={selectedEndpointData.authentication}>
                          <option value="none">No Authentication</option>
                          <option value="apikey">API Key</option>
                          <option value="bearer">Bearer Token</option>
                          <option value="basic">Basic Auth</option>
                          <option value="oauth">OAuth 2.0</option>
                        </select>
                      </div>

                      {selectedEndpointData.authentication !== 'none' && (
                        <div className="auth-config">
                          <div className="config-info">
                            <Shield size={16} />
                            This endpoint requires {selectedEndpointData.authentication} authentication.
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {selectedTab === 'test' && selectedEndpointData && (
            <div className="endpoint-tester">
              <div className="tester-header">
                <h3>Test Endpoint</h3>
                <div className="test-actions">
                  <button 
                    className="test-btn primary"
                    onClick={() => executeTest(selectedEndpointData)}
                    disabled={isExecutingTest}
                  >
                    {isExecutingTest ? (
                      <>
                        <div className="spinner small" />
                        Testing...
                      </>
                    ) : (
                      <>
                        <Send size={16} />
                        Send Request
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="test-configuration">
                <div className="config-section">
                  <h4>Request URL</h4>
                  <div className="url-builder">
                    <span className="base-url">{selectedEnvironmentData?.baseUrl}</span>
                    <span className="endpoint-path">{selectedEndpointData.path}</span>
                  </div>
                </div>

                <div className="config-section">
                  <h4>Headers</h4>
                  <div className="headers-editor">
                    <div className="header-item">
                      <input type="text" placeholder="Header name" />
                      <input type="text" placeholder="Header value" />
                      <button className="remove-header-btn">
                        <X size={14} />
                      </button>
                    </div>
                    <button className="add-header-btn">
                      <Plus size={14} />
                      Add Header
                    </button>
                  </div>
                </div>

                {selectedEndpointData.requestBody && (
                  <div className="config-section">
                    <h4>Request Body</h4>
                    <textarea 
                      className="request-body-editor"
                      placeholder="Enter request body..."
                      defaultValue={JSON.stringify(selectedEndpointData.requestBody.examples.default, null, 2)}
                    />
                  </div>
                )}
              </div>

              <div className="test-results-section">
                <h4>Test History</h4>
                {selectedEndpointData.testResults && selectedEndpointData.testResults.length > 0 ? (
                  <div className="test-history">
                    {selectedEndpointData.testResults.map(result => (
                      <div key={result.id} className="test-result-item">
                        <div className="result-header">
                          <div className="result-status" style={{ color: getStatusColor(result.status) }}>
                            {result.status === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
                            <span className="status-code">{result.statusCode}</span>
                            <span className="response-time">{result.responseTime}ms</span>
                          </div>
                          <div className="result-time">
                            {new Date(result.timestamp).toLocaleString()}
                          </div>
                        </div>
                        {result.response && (
                          <div className="result-content">
                            <pre>{JSON.stringify(result.response, null, 2)}</pre>
                          </div>
                        )}
                        {result.error && (
                          <div className="result-error">
                            <AlertCircle size={16} />
                            {result.error}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-test-results">
                    <TestTube2 size={32} />
                    <p>No test results yet. Run your first test to see results here.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {selectedTab === 'docs' && (
            <div className="documentation-generator">
              <div className="docs-header">
                <h3>API Documentation</h3>
                <div className="docs-actions">
                  <button className="docs-btn secondary">
                    <RefreshCw size={16} />
                    Regenerate
                  </button>
                  <button className="docs-btn primary">
                    <ExternalLink size={16} />
                    Preview
                  </button>
                </div>
              </div>

              <div className="docs-config">
                <div className="config-tabs">
                  <button className="config-tab active">General</button>
                  <button className="config-tab">Endpoints</button>
                  <button className="config-tab">Schemas</button>
                  <button className="config-tab">Examples</button>
                </div>

                <div className="config-content">
                  <div className="config-section">
                    <div className="form-grid">
                      <div className="form-field">
                        <label>API Title</label>
                        <input 
                          type="text" 
                          value={project.documentation.title}
                          onChange={(e) => setProject(prev => ({
                            ...prev,
                            documentation: { ...prev.documentation, title: e.target.value }
                          }))}
                        />
                      </div>
                      
                      <div className="form-field">
                        <label>Version</label>
                        <input 
                          type="text" 
                          value={project.documentation.version}
                          onChange={(e) => setProject(prev => ({
                            ...prev,
                            documentation: { ...prev.documentation, version: e.target.value }
                          }))}
                        />
                      </div>

                      <div className="form-field full-width">
                        <label>Description</label>
                        <textarea 
                          value={project.documentation.description}
                          onChange={(e) => setProject(prev => ({
                            ...prev,
                            documentation: { ...prev.documentation, description: e.target.value }
                          }))}
                        />
                      </div>

                      <div className="form-field">
                        <label>Contact Name</label>
                        <input 
                          type="text" 
                          value={project.documentation.contact.name}
                        />
                      </div>

                      <div className="form-field">
                        <label>Contact Email</label>
                        <input 
                          type="email" 
                          value={project.documentation.contact.email}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="docs-preview">
                <h4>Documentation Preview</h4>
                <div className="preview-content">
                  <div className="api-doc-preview">
                    <h1>{project.documentation.title}</h1>
                    <p className="version">Version {project.documentation.version}</p>
                    <p className="description">{project.documentation.description}</p>
                    
                    <h2>Endpoints</h2>
                    {project.endpoints.map(endpoint => (
                      <div key={endpoint.id} className="endpoint-doc">
                        <div className="endpoint-title">
                          <span 
                            className="method-badge"
                            style={{ backgroundColor: getMethodColor(endpoint.method) }}
                          >
                            {endpoint.method}
                          </span>
                          <span className="endpoint-path">{endpoint.path}</span>
                        </div>
                        <p className="endpoint-description">{endpoint.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Test Results Modal */}
      {showTestModal && (
        <div className="modal-overlay" onClick={() => setShowTestModal(false)}>
          <div className="test-results-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Test Results</h3>
              <button className="close-btn" onClick={() => setShowTestModal(false)}>
                <X size={16} />
              </button>
            </div>
            
            <div className="modal-content">
              {selectedEndpointData?.testResults && selectedEndpointData.testResults[0] && (
                <div className="test-result-detail">
                  <div className="result-summary">
                    <div className="summary-item">
                      <span className="label">Status:</span>
                      <span 
                        className="value status"
                        style={{ color: getStatusColor(selectedEndpointData.testResults[0].status) }}
                      >
                        {selectedEndpointData.testResults[0].status}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Response Time:</span>
                      <span className="value">{selectedEndpointData.testResults[0].responseTime}ms</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Status Code:</span>
                      <span className="value">{selectedEndpointData.testResults[0].statusCode}</span>
                    </div>
                  </div>

                  {selectedEndpointData.testResults[0].response && (
                    <div className="response-content">
                      <h4>Response</h4>
                      <pre>{JSON.stringify(selectedEndpointData.testResults[0].response, null, 2)}</pre>
                    </div>
                  )}

                  {selectedEndpointData.testResults[0].error && (
                    <div className="error-content">
                      <h4>Error</h4>
                      <div className="error-message">{selectedEndpointData.testResults[0].error}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APIDesignerBuilder;