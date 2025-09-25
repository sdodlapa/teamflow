import React, { useState, useEffect } from 'react';
import {
  Plus, Play, Eye, Settings, Download,
  Code, Database, Globe, Users, Zap, CheckCircle,
  Search, Layout, Box, Link2, ArrowRight, Maximize2,
  Grid3X3, Palette, Workflow, Star, Heart,
  Gauge, Clock
} from 'lucide-react';
import './IntegratedTemplateBuilder.css';

interface DomainTemplate {
  id: string;
  name: string;
  title: string;
  description: string;
  category: 'task_management' | 'crm' | 'ecommerce' | 'healthcare' | 'finance' | 'custom';
  author: {
    id: string;
    name: string;
    avatar?: string;
    verified: boolean;
  };
  version: string;
  entities: Entity[];
  workflows: Workflow[];
  integrations: Integration[];
  ui_components: UIComponent[];
  features: string[];
  complexity: 'beginner' | 'intermediate' | 'advanced';
  estimated_time: string;
  preview_url?: string;
  demo_data: boolean;
  created_at: string;
  updated_at: string;
  stats: {
    downloads: number;
    ratings: number;
    average_rating: number;
    likes: number;
    forks: number;
  };
  pricing: {
    type: 'free' | 'premium' | 'enterprise';
    price?: number;
    trial_days?: number;
  };
}

interface Entity {
  id: string;
  name: string;
  display_name: string;
  description: string;
  icon: string;
  color: string;
  fields: Field[];
  relationships: Relationship[];
  permissions: Permission[];
  ui_config: {
    list_view: boolean;
    detail_view: boolean;
    create_form: boolean;
    edit_form: boolean;
    bulk_actions: string[];
  };
  position: { x: number; y: number };
}

interface Field {
  id: string;
  name: string;
  display_name: string;
  type: 'string' | 'text' | 'integer' | 'decimal' | 'boolean' | 'date' | 'datetime' | 'email' | 'url' | 'json' | 'file' | 'image';
  required: boolean;
  unique: boolean;
  indexed: boolean;
  default_value?: string;
  validation: {
    min_length?: number;
    max_length?: number;
    pattern?: string;
    min_value?: number;
    max_value?: number;
    allowed_values?: string[];
  };
  ui_config: {
    widget: string;
    placeholder?: string;
    help_text?: string;
    show_in_list: boolean;
    show_in_detail: boolean;
    editable: boolean;
    searchable: boolean;
    sortable: boolean;
  };
}

interface Relationship {
  id: string;
  type: 'one_to_one' | 'one_to_many' | 'many_to_many';
  from_entity: string;
  to_entity: string;
  name: string;
  reverse_name: string;
  cascade_delete: boolean;
  required: boolean;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  trigger: {
    type: 'entity_create' | 'entity_update' | 'entity_delete' | 'schedule' | 'webhook' | 'manual';
    entity?: string;
    conditions?: any[];
  };
  actions: {
    type: string;
    config: any;
  }[];
  enabled: boolean;
}

interface Integration {
  id: string;
  name: string;
  type: 'api' | 'webhook' | 'database' | 'service';
  config: any;
  enabled: boolean;
}

interface UIComponent {
  id: string;
  name: string;
  type: 'dashboard' | 'list' | 'detail' | 'form' | 'chart' | 'widget';
  entity?: string;
  config: any;
}

interface Permission {
  role: string;
  actions: ('create' | 'read' | 'update' | 'delete')[];
  conditions?: any[];
}

interface IntegratedTemplateBuilderProps {
  onTemplateSelect?: (template: DomainTemplate) => void;
  onTemplateCreate?: (template: Partial<DomainTemplate>) => void;
  onClose?: () => void;
  currentProject?: {
    id: string;
    name: string;
    type: string;
  };
}

export const IntegratedTemplateBuilder: React.FC<IntegratedTemplateBuilderProps> = ({
  onTemplateSelect,
  onTemplateCreate,
  onClose,
  currentProject
}) => {
  const [activeTab, setActiveTab] = useState<'browse' | 'create' | 'customize' | 'deploy'>('browse');
  const [templates, setTemplates] = useState<DomainTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<DomainTemplate | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedComplexity, setSelectedComplexity] = useState<string>('all');
  const [customTemplate, setCustomTemplate] = useState<Partial<DomainTemplate>>({
    name: '',
    title: '',
    description: '',
    category: 'custom',
    entities: [],
    workflows: [],
    integrations: [],
    ui_components: []
  });
  const [isCreating, setIsCreating] = useState(false);
  const [deploymentStatus, setDeploymentStatus] = useState<'idle' | 'deploying' | 'success' | 'error'>('idle');

  // Mock templates data
  const generateMockTemplates = (): DomainTemplate[] => {
    return [
      {
        id: 'task-management-pro',
        name: 'task_management_pro',
        title: 'Advanced Task Management System',
        description: 'Complete task management platform with teams, projects, time tracking, and advanced analytics',
        category: 'task_management',
        author: {
          id: 'teamflow',
          name: 'TeamFlow Official',
          verified: true
        },
        version: '2.1.0',
        entities: [
          {
            id: 'task',
            name: 'task',
            display_name: 'Task',
            description: 'Individual work items with status tracking',
            icon: 'CheckCircle',
            color: '#3b82f6',
            fields: [],
            relationships: [],
            permissions: [],
            ui_config: {
              list_view: true,
              detail_view: true,
              create_form: true,
              edit_form: true,
              bulk_actions: ['assign', 'update_status', 'delete']
            },
            position: { x: 100, y: 100 }
          },
          {
            id: 'project',
            name: 'project',
            display_name: 'Project',
            description: 'Project containers for organizing tasks',
            icon: 'Folder',
            color: '#10b981',
            fields: [],
            relationships: [],
            permissions: [],
            ui_config: {
              list_view: true,
              detail_view: true,
              create_form: true,
              edit_form: true,
              bulk_actions: ['archive', 'delete']
            },
            position: { x: 300, y: 100 }
          },
          {
            id: 'user',
            name: 'user',
            display_name: 'User',
            description: 'Team members and collaborators',
            icon: 'User',
            color: '#8b5cf6',
            fields: [],
            relationships: [],
            permissions: [],
            ui_config: {
              list_view: true,
              detail_view: true,
              create_form: true,
              edit_form: true,
              bulk_actions: ['invite', 'deactivate']
            },
            position: { x: 200, y: 250 }
          }
        ],
        workflows: [],
        integrations: [],
        ui_components: [],
        features: [
          'Task Management', 'Project Organization', 'Team Collaboration',
          'Time Tracking', 'Advanced Analytics', 'File Attachments',
          'Comments & Discussion', 'Custom Fields', 'Automation Rules'
        ],
        complexity: 'intermediate',
        estimated_time: '15-20 minutes',
        demo_data: true,
        created_at: '2024-09-15T10:00:00Z',
        updated_at: '2024-09-24T15:30:00Z',
        stats: {
          downloads: 1247,
          ratings: 156,
          average_rating: 4.8,
          likes: 892,
          forks: 234
        },
        pricing: {
          type: 'free'
        }
      },
      {
        id: 'crm-starter',
        name: 'crm_starter',
        title: 'Customer Relationship Management',
        description: 'Complete CRM system with lead management, sales pipeline, and customer tracking',
        category: 'crm',
        author: {
          id: 'salesforce-dev',
          name: 'SalesTech Solutions',
          verified: true
        },
        version: '1.5.2',
        entities: [
          {
            id: 'lead',
            name: 'lead',
            display_name: 'Lead',
            description: 'Potential customers and prospects',
            icon: 'Target',
            color: '#f59e0b',
            fields: [],
            relationships: [],
            permissions: [],
            ui_config: {
              list_view: true,
              detail_view: true,
              create_form: true,
              edit_form: true,
              bulk_actions: ['convert', 'assign', 'delete']
            },
            position: { x: 150, y: 100 }
          },
          {
            id: 'contact',
            name: 'contact',
            display_name: 'Contact',
            description: 'Customer contacts and information',
            icon: 'Users',
            color: '#06b6d4',
            fields: [],
            relationships: [],
            permissions: [],
            ui_config: {
              list_view: true,
              detail_view: true,
              create_form: true,
              edit_form: true,
              bulk_actions: ['export', 'merge', 'delete']
            },
            position: { x: 350, y: 100 }
          }
        ],
        workflows: [],
        integrations: [],
        ui_components: [],
        features: [
          'Lead Management', 'Contact Database', 'Sales Pipeline',
          'Deal Tracking', 'Email Integration', 'Reporting Dashboard',
          'Activity Timeline', 'Task Management', 'Quote Generation'
        ],
        complexity: 'advanced',
        estimated_time: '25-30 minutes',
        demo_data: true,
        created_at: '2024-08-20T14:00:00Z',
        updated_at: '2024-09-18T09:45:00Z',
        stats: {
          downloads: 856,
          ratings: 89,
          average_rating: 4.6,
          likes: 645,
          forks: 178
        },
        pricing: {
          type: 'premium',
          price: 99,
          trial_days: 14
        }
      },
      {
        id: 'ecommerce-basic',
        name: 'ecommerce_basic',
        title: 'E-commerce Platform Starter',
        description: 'Basic e-commerce system with product catalog, shopping cart, and order management',
        category: 'ecommerce',
        author: {
          id: 'shopify-dev',
          name: 'E-Commerce Experts',
          verified: false
        },
        version: '1.2.0',
        entities: [
          {
            id: 'product',
            name: 'product',
            display_name: 'Product',
            description: 'Products in the catalog',
            icon: 'Box',
            color: '#ef4444',
            fields: [],
            relationships: [],
            permissions: [],
            ui_config: {
              list_view: true,
              detail_view: true,
              create_form: true,
              edit_form: true,
              bulk_actions: ['update_price', 'update_inventory', 'delete']
            },
            position: { x: 100, y: 150 }
          },
          {
            id: 'order',
            name: 'order',
            display_name: 'Order',
            description: 'Customer orders and transactions',
            icon: 'ShoppingCart',
            color: '#22c55e',
            fields: [],
            relationships: [],
            permissions: [],
            ui_config: {
              list_view: true,
              detail_view: true,
              create_form: false,
              edit_form: true,
              bulk_actions: ['fulfill', 'refund', 'export']
            },
            position: { x: 300, y: 150 }
          }
        ],
        workflows: [],
        integrations: [],
        ui_components: [],
        features: [
          'Product Catalog', 'Shopping Cart', 'Order Management',
          'Payment Processing', 'Inventory Tracking', 'Customer Accounts',
          'Basic Analytics', 'Shipping Integration', 'Tax Calculation'
        ],
        complexity: 'intermediate',
        estimated_time: '20-25 minutes',
        demo_data: true,
        created_at: '2024-07-30T16:20:00Z',
        updated_at: '2024-09-10T11:15:00Z',
        stats: {
          downloads: 2134,
          ratings: 267,
          average_rating: 4.4,
          likes: 1456,
          forks: 423
        },
        pricing: {
          type: 'free'
        }
      },
      {
        id: 'custom-builder',
        name: 'custom_builder',
        title: 'Start from Scratch',
        description: 'Create a completely custom domain template tailored to your specific business needs',
        category: 'custom',
        author: {
          id: 'teamflow',
          name: 'TeamFlow Builder',
          verified: true
        },
        version: '1.0.0',
        entities: [],
        workflows: [],
        integrations: [],
        ui_components: [],
        features: [
          'Visual Entity Designer', 'Custom Field Types', 'Relationship Builder',
          'Workflow Automation', 'Custom UI Components', 'API Integration',
          'Permission System', 'Multi-tenant Support', 'Advanced Validation'
        ],
        complexity: 'advanced',
        estimated_time: '45-60 minutes',
        demo_data: false,
        created_at: '2024-09-01T12:00:00Z',
        updated_at: '2024-09-24T18:00:00Z',
        stats: {
          downloads: 445,
          ratings: 78,
          average_rating: 4.9,
          likes: 334,
          forks: 89
        },
        pricing: {
          type: 'enterprise'
        }
      }
    ];
  };

  useEffect(() => {
    const mockTemplates = generateMockTemplates();
    setTemplates(mockTemplates);
  }, []);

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.features.some(feature => feature.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesComplexity = selectedComplexity === 'all' || template.complexity === selectedComplexity;

    return matchesSearch && matchesCategory && matchesComplexity;
  });

  const handleTemplateSelect = (template: DomainTemplate) => {
    setSelectedTemplate(template);
    if (template.id === 'custom-builder') {
      setActiveTab('create');
    } else {
      setActiveTab('customize');
    }
  };

  const handleDeployTemplate = async (template: DomainTemplate) => {
    setDeploymentStatus('deploying');
    
    // Simulate deployment process
    setTimeout(() => {
      setDeploymentStatus('success');
      if (onTemplateSelect) {
        onTemplateSelect(template);
      }
      
      // Reset after showing success
      setTimeout(() => {
        setDeploymentStatus('idle');
        if (onClose) {
          onClose();
        }
      }, 2000);
    }, 3000);
  };

  const handleCreateCustomTemplate = async () => {
    if (!customTemplate.name || !customTemplate.title) return;

    setIsCreating(true);
    
    // Simulate template creation
    setTimeout(() => {
      const newTemplate: DomainTemplate = {
        ...customTemplate,
        id: `custom-${Date.now()}`,
        author: {
          id: 'current-user',
          name: 'Current User',
          verified: false
        },
        version: '1.0.0',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        stats: {
          downloads: 0,
          ratings: 0,
          average_rating: 0,
          likes: 0,
          forks: 0
        },
        pricing: {
          type: 'free'
        }
      } as DomainTemplate;

      if (onTemplateCreate) {
        onTemplateCreate(newTemplate);
      }

      setIsCreating(false);
      setActiveTab('deploy');
      setSelectedTemplate(newTemplate);
    }, 2000);
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'task_management':
        return <CheckCircle size={20} />;
      case 'crm':
        return <Users size={20} />;
      case 'ecommerce':
        return <Globe size={20} />;
      case 'healthcare':
        return <Heart size={20} />;
      case 'finance':
        return <Gauge size={20} />;
      case 'custom':
        return <Plus size={20} />;
      default:
        return <Box size={20} />;
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'beginner':
        return '#10b981';
      case 'intermediate':
        return '#f59e0b';
      case 'advanced':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const renderBrowseTab = () => (
    <div className="browse-tab">
      <div className="browse-header">
        <div className="header-content">
          <h2>Browse Templates</h2>
          <p>Choose from our collection of pre-built domain templates or start from scratch</p>
        </div>

        <div className="search-filters">
          <div className="search-box">
            <Search size={20} />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="filter-controls">
            <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}>
              <option value="all">All Categories</option>
              <option value="task_management">Task Management</option>
              <option value="crm">CRM</option>
              <option value="ecommerce">E-commerce</option>
              <option value="healthcare">Healthcare</option>
              <option value="finance">Finance</option>
              <option value="custom">Custom</option>
            </select>

            <select value={selectedComplexity} onChange={(e) => setSelectedComplexity(e.target.value)}>
              <option value="all">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>
      </div>

      <div className="templates-grid">
        {filteredTemplates.map(template => (
          <div key={template.id} className="template-card">
            <div className="card-header">
              <div className="template-icon">
                {getCategoryIcon(template.category)}
              </div>
              <div className="template-meta">
                <div className="pricing-badge">
                  {template.pricing.type === 'free' && <span className="free">Free</span>}
                  {template.pricing.type === 'premium' && <span className="premium">Premium</span>}
                  {template.pricing.type === 'enterprise' && <span className="enterprise">Enterprise</span>}
                </div>
                <div className="complexity-indicator">
                  <div 
                    className="complexity-dot"
                    style={{ backgroundColor: getComplexityColor(template.complexity) }}
                  />
                  <span>{template.complexity}</span>
                </div>
              </div>
            </div>

            <div className="card-content">
              <h3>{template.title}</h3>
              <p className="template-description">{template.description}</p>

              <div className="template-stats">
                <div className="stat">
                  <Download size={14} />
                  <span>{template.stats.downloads.toLocaleString()}</span>
                </div>
                <div className="stat">
                  <Star size={14} />
                  <span>{template.stats.average_rating.toFixed(1)}</span>
                </div>
                <div className="stat">
                  <Clock size={14} />
                  <span>{template.estimated_time}</span>
                </div>
              </div>

              <div className="template-features">
                {template.features.slice(0, 3).map((feature, index) => (
                  <span key={index} className="feature-tag">{feature}</span>
                ))}
                {template.features.length > 3 && (
                  <span className="more-features">+{template.features.length - 3} more</span>
                )}
              </div>
            </div>

            <div className="card-actions">
              <button
                className="action-btn secondary"
                onClick={() => console.log('Preview:', template.title)}
              >
                <Eye size={16} />
                Preview
              </button>
              <button
                className="action-btn primary"
                onClick={() => handleTemplateSelect(template)}
              >
                <ArrowRight size={16} />
                Use Template
              </button>
            </div>

            <div className="template-author">
              <div className="author-info">
                <span className="author-name">{template.author.name}</span>
                {template.author.verified && (
                  <CheckCircle size={12} className="verified-badge" />
                )}
              </div>
              <span className="template-version">v{template.version}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCreateTab = () => (
    <div className="create-tab">
      <div className="create-header">
        <h2>Create Custom Template</h2>
        <p>Build a domain template from scratch tailored to your specific business needs</p>
      </div>

      <div className="create-form">
        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="form-grid">
            <div className="form-field">
              <label>Template Name *</label>
              <input
                type="text"
                placeholder="e.g., inventory_management"
                value={customTemplate.name || ''}
                onChange={(e) => setCustomTemplate({
                  ...customTemplate,
                  name: e.target.value
                })}
              />
            </div>

            <div className="form-field">
              <label>Display Title *</label>
              <input
                type="text"
                placeholder="e.g., Inventory Management System"
                value={customTemplate.title || ''}
                onChange={(e) => setCustomTemplate({
                  ...customTemplate,
                  title: e.target.value
                })}
              />
            </div>

            <div className="form-field full-width">
              <label>Description</label>
              <textarea
                placeholder="Describe what this template will manage and its key features..."
                value={customTemplate.description || ''}
                onChange={(e) => setCustomTemplate({
                  ...customTemplate,
                  description: e.target.value
                })}
                rows={3}
              />
            </div>

            <div className="form-field">
              <label>Category</label>
              <select
                value={customTemplate.category || 'custom'}
                onChange={(e) => setCustomTemplate({
                  ...customTemplate,
                  category: e.target.value as any
                })}
              >
                <option value="custom">Custom</option>
                <option value="task_management">Task Management</option>
                <option value="crm">CRM</option>
                <option value="ecommerce">E-commerce</option>
                <option value="healthcare">Healthcare</option>
                <option value="finance">Finance</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Quick Setup Options</h3>
          <p>Choose pre-configured components to get started faster</p>
          
          <div className="quick-options">
            <div className="option-card">
              <div className="option-header">
                <Database size={24} />
                <h4>Basic Entities</h4>
              </div>
              <p>Add common entity types like users, categories, and settings</p>
              <button className="add-option-btn">Add Basic Entities</button>
            </div>

            <div className="option-card">
              <div className="option-header">
                <Workflow size={24} />
                <h4>Common Workflows</h4>
              </div>
              <p>Include standard workflows like approval processes and notifications</p>
              <button className="add-option-btn">Add Workflows</button>
            </div>

            <div className="option-card">
              <div className="option-header">
                <Users size={24} />
                <h4>User Management</h4>
              </div>
              <p>Set up user roles, permissions, and authentication features</p>
              <button className="add-option-btn">Add User System</button>
            </div>

            <div className="option-card">
              <div className="option-header">
                <Layout size={24} />
                <h4>Dashboard Components</h4>
              </div>
              <p>Include charts, widgets, and reporting dashboards</p>
              <button className="add-option-btn">Add Dashboards</button>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button className="action-btn secondary" onClick={() => setActiveTab('browse')}>
            <ArrowRight size={16} style={{ transform: 'rotate(180deg)' }} />
            Back to Browse
          </button>
          <button
            className="action-btn primary"
            onClick={handleCreateCustomTemplate}
            disabled={!customTemplate.name || !customTemplate.title || isCreating}
          >
            {isCreating ? (
              <>
                <div className="spinner" />
                Creating Template...
              </>
            ) : (
              <>
                <Plus size={16} />
                Create Template
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );

  const renderCustomizeTab = () => {
    if (!selectedTemplate) return null;

    return (
      <div className="customize-tab">
        <div className="customize-header">
          <div className="template-info">
            <div className="template-icon">
              {getCategoryIcon(selectedTemplate.category)}
            </div>
            <div>
              <h2>{selectedTemplate.title}</h2>
              <p>Customize this template for your {currentProject?.name || 'project'}</p>
            </div>
          </div>

          <div className="template-actions">
            <button className="action-btn secondary">
              <Eye size={16} />
              Preview
            </button>
            <button className="action-btn secondary">
              <Code size={16} />
              View Code
            </button>
            <button className="action-btn secondary">
              <Download size={16} />
              Export
            </button>
          </div>
        </div>

        <div className="customize-content">
          <div className="customization-sidebar">
            <div className="sidebar-section">
              <h3>Template Components</h3>
              <div className="component-list">
                <div className="component-item active">
                  <Database size={16} />
                  <span>Entities ({selectedTemplate.entities.length})</span>
                  <Settings size={14} />
                </div>
                <div className="component-item">
                  <Link2 size={16} />
                  <span>Relationships</span>
                  <Settings size={14} />
                </div>
                <div className="component-item">
                  <Zap size={16} />
                  <span>Workflows</span>
                  <Settings size={14} />
                </div>
                <div className="component-item">
                  <Layout size={16} />
                  <span>UI Components</span>
                  <Settings size={14} />
                </div>
                <div className="component-item">
                  <Globe size={16} />
                  <span>Integrations</span>
                  <Settings size={14} />
                </div>
              </div>
            </div>

            <div className="sidebar-section">
              <h3>Customization Options</h3>
              <div className="customization-options">
                <label className="option-checkbox">
                  <input type="checkbox" defaultChecked />
                  Include demo data
                </label>
                <label className="option-checkbox">
                  <input type="checkbox" defaultChecked />
                  Enable API endpoints
                </label>
                <label className="option-checkbox">
                  <input type="checkbox" defaultChecked />
                  Generate admin interface
                </label>
                <label className="option-checkbox">
                  <input type="checkbox" />
                  Add user authentication
                </label>
                <label className="option-checkbox">
                  <input type="checkbox" />
                  Enable file uploads
                </label>
              </div>
            </div>
          </div>

          <div className="entity-canvas">
            <div className="canvas-header">
              <h3>Entity Relationships</h3>
              <div className="canvas-tools">
                <button className="tool-btn">
                  <Maximize2 size={16} />
                </button>
                <button className="tool-btn">
                  <Grid3X3 size={16} />
                </button>
                <button className="tool-btn">
                  <Palette size={16} />
                </button>
              </div>
            </div>

            <div className="canvas-area">
              <svg width="100%" height="400" className="entity-diagram">
                {selectedTemplate.entities.map((entity) => (
                  <g key={entity.id}>
                    <rect
                      x={entity.position.x}
                      y={entity.position.y}
                      width="120"
                      height="80"
                      rx="8"
                      fill={entity.color}
                      fillOpacity="0.1"
                      stroke={entity.color}
                      strokeWidth="2"
                      className="entity-box"
                    />
                    <text
                      x={entity.position.x + 60}
                      y={entity.position.y + 30}
                      textAnchor="middle"
                      className="entity-name"
                      fill={entity.color}
                    >
                      {entity.display_name}
                    </text>
                    <text
                      x={entity.position.x + 60}
                      y={entity.position.y + 50}
                      textAnchor="middle"
                      className="entity-fields"
                      fill="#666"
                    >
                      {entity.fields.length} fields
                    </text>
                  </g>
                ))}
                
                {/* Sample relationship lines */}
                <line
                  x1="220" y1="140"
                  x2="280" y2="140"
                  stroke="#666"
                  strokeWidth="2"
                  markerEnd="url(#arrowhead)"
                />
                <defs>
                  <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                   refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
                  </marker>
                </defs>
              </svg>
            </div>
          </div>
        </div>

        <div className="customize-actions">
          <button className="action-btn secondary" onClick={() => setActiveTab('browse')}>
            <ArrowRight size={16} style={{ transform: 'rotate(180deg)' }} />
            Back to Templates
          </button>
          <button
            className="action-btn primary"
            onClick={() => setActiveTab('deploy')}
          >
            <Play size={16} />
            Deploy Template
          </button>
        </div>
      </div>
    );
  };

  const renderDeployTab = () => {
    if (!selectedTemplate) return null;

    return (
      <div className="deploy-tab">
        <div className="deploy-header">
          <div className="template-summary">
            <div className="template-icon large">
              {getCategoryIcon(selectedTemplate.category)}
            </div>
            <div>
              <h2>Deploy {selectedTemplate.title}</h2>
              <p>Ready to deploy to your {currentProject?.name || 'project'} workspace</p>
            </div>
          </div>
        </div>

        <div className="deployment-preview">
          <div className="preview-section">
            <h3>What will be created:</h3>
            
            <div className="deployment-items">
              <div className="deployment-item">
                <Database size={20} />
                <div>
                  <strong>{selectedTemplate.entities.length} Database Entities</strong>
                  <span>Complete data models with relationships</span>
                </div>
              </div>
              
              <div className="deployment-item">
                <Code size={20} />
                <div>
                  <strong>{selectedTemplate.entities.length * 5} API Endpoints</strong>
                  <span>CRUD operations and custom endpoints</span>
                </div>
              </div>
              
              <div className="deployment-item">
                <Layout size={20} />
                <div>
                  <strong>{selectedTemplate.ui_components.length || selectedTemplate.entities.length * 3} UI Components</strong>
                  <span>Forms, lists, and dashboard widgets</span>
                </div>
              </div>
              
              <div className="deployment-item">
                <Workflow size={20} />
                <div>
                  <strong>{selectedTemplate.workflows.length || 3} Workflows</strong>
                  <span>Automated processes and rules</span>
                </div>
              </div>
            </div>
          </div>

          <div className="deployment-options">
            <h3>Deployment Options:</h3>
            
            <div className="option-group">
              <label className="deploy-option">
                <input type="radio" name="deployment" value="current" defaultChecked />
                <div>
                  <strong>Deploy to Current Project</strong>
                  <span>Add to "{currentProject?.name || 'Current Project'}"</span>
                </div>
              </label>
              
              <label className="deploy-option">
                <input type="radio" name="deployment" value="new" />
                <div>
                  <strong>Create New Project</strong>
                  <span>Start fresh with this template</span>
                </div>
              </label>
            </div>
          </div>
        </div>

        {deploymentStatus === 'deploying' && (
          <div className="deployment-progress">
            <div className="progress-header">
              <h3>Deploying Template...</h3>
              <div className="spinner large" />
            </div>
            <div className="progress-steps">
              <div className="progress-step active">
                <CheckCircle size={16} />
                <span>Validating template</span>
              </div>
              <div className="progress-step active">
                <CheckCircle size={16} />
                <span>Creating database models</span>
              </div>
              <div className="progress-step loading">
                <div className="spinner small" />
                <span>Generating API endpoints</span>
              </div>
              <div className="progress-step">
                <Clock size={16} />
                <span>Building UI components</span>
              </div>
              <div className="progress-step">
                <Clock size={16} />
                <span>Setting up workflows</span>
              </div>
            </div>
          </div>
        )}

        {deploymentStatus === 'success' && (
          <div className="deployment-success">
            <div className="success-icon">
              <CheckCircle size={48} />
            </div>
            <h3>Template Deployed Successfully!</h3>
            <p>Your {selectedTemplate.title} is now ready to use</p>
            <button className="action-btn primary" onClick={onClose}>
              <ArrowRight size={16} />
              Go to Project
            </button>
          </div>
        )}

        {deploymentStatus === 'idle' && (
          <div className="deploy-actions">
            <button className="action-btn secondary" onClick={() => setActiveTab('customize')}>
              <ArrowRight size={16} style={{ transform: 'rotate(180deg)' }} />
              Back to Customize
            </button>
            <button
              className="action-btn primary large"
              onClick={() => handleDeployTemplate(selectedTemplate)}
            >
              <Play size={20} />
              Deploy Template
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="integrated-template-builder">
      <div className="builder-header">
        <div className="header-content">
          <h1>Template Builder</h1>
          <p>Create and deploy domain templates for your business applications</p>
        </div>

        <div className="header-tabs">
          {[
            { id: 'browse', label: 'Browse Templates', icon: Search },
            { id: 'create', label: 'Create Custom', icon: Plus },
            { id: 'customize', label: 'Customize', icon: Settings },
            { id: 'deploy', label: 'Deploy', icon: Play }
          ].map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id as any)}
              disabled={(tab.id === 'customize' || tab.id === 'deploy') && !selectedTemplate}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {onClose && (
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        )}
      </div>

      <div className="builder-content">
        {activeTab === 'browse' && renderBrowseTab()}
        {activeTab === 'create' && renderCreateTab()}
        {activeTab === 'customize' && renderCustomizeTab()}
        {activeTab === 'deploy' && renderDeployTab()}
      </div>
    </div>
  );
};