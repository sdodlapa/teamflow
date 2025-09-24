import React, { useState, useEffect } from 'react';
import {
  GitBranch,
  Tag,
  CheckCircle,
  XCircle,
  AlertTriangle,
  TrendingUp,
  Clock,
  Settings,
  Code,
  Database,
  Layers,
  Shield,
  Zap,
  FileText,
  Activity,
  BarChart3,
  Target,
  Lightbulb,
  RefreshCw,
  Download,
  Eye,
  Plus,
  ArrowRight
} from 'lucide-react';
import { DomainConfig, Entity, Relationship } from '../../types/template';

interface TemplateVersion {
  id: string;
  version: string;
  name: string;
  description: string;
  author: string;
  created_at: string;
  status: 'draft' | 'published' | 'deprecated';
  changes: TemplateChange[];
  performance_score: number;
  validation_status: 'passed' | 'failed' | 'warning';
  download_count: number;
  is_current: boolean;
}

interface TemplateChange {
  type: 'added' | 'modified' | 'removed';
  category: 'entity' | 'field' | 'relationship' | 'config';
  item: string;
  description: string;
}

interface ValidationResult {
  category: 'structure' | 'performance' | 'security' | 'best_practices';
  level: 'error' | 'warning' | 'info' | 'success';
  title: string;
  description: string;
  suggestion?: string;
  auto_fixable: boolean;
}

interface OptimizationSuggestion {
  id: string;
  category: 'performance' | 'structure' | 'naming' | 'relationships';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
  effort: 'low' | 'medium' | 'high';
  auto_applicable: boolean;
}

interface AdvancedTemplateFeaturesProps {
  domainConfig: DomainConfig;
  entities: Entity[];
  relationships: Relationship[];
  onClose?: () => void;
}

const AdvancedTemplateFeatures: React.FC<AdvancedTemplateFeaturesProps> = ({
  entities,
  relationships,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'versions' | 'validation' | 'optimization' | 'testing'>('versions');
  const [versions, setVersions] = useState<TemplateVersion[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<TemplateVersion | null>(null);
  const [validationResults, setValidationResults] = useState<ValidationResult[]>([]);
  const [optimizations, setOptimizations] = useState<OptimizationSuggestion[]>([]);
  const [isRunningValidation, setIsRunningValidation] = useState(false);
  const [isGeneratingOptimizations, setIsGeneratingOptimizations] = useState(false);

  useEffect(() => {
    loadVersions();
    runValidation();
    generateOptimizations();
  }, []);

  const loadVersions = () => {
    // Mock version data
    const mockVersions: TemplateVersion[] = [
      {
        id: '1',
        version: '2.1.0',
        name: 'Enhanced User Management',
        description: 'Added advanced user roles and permissions system with audit logging',
        author: 'John Doe',
        created_at: '2024-12-02T10:30:00Z',
        status: 'published',
        changes: [
          { type: 'added', category: 'entity', item: 'UserRole', description: 'New user role management entity' },
          { type: 'added', category: 'entity', item: 'AuditLog', description: 'System audit logging' },
          { type: 'modified', category: 'entity', item: 'User', description: 'Enhanced with role relationships' },
          { type: 'added', category: 'relationship', item: 'User-UserRole', description: 'Many-to-many relationship' }
        ],
        performance_score: 94,
        validation_status: 'passed',
        download_count: 1247,
        is_current: true
      },
      {
        id: '2',
        version: '2.0.1',
        name: 'Bug Fix Release',
        description: 'Fixed field validation issues and improved error handling',
        author: 'Jane Smith',
        created_at: '2024-11-28T14:15:00Z',
        status: 'published',
        changes: [
          { type: 'modified', category: 'field', item: 'User.email', description: 'Fixed email validation regex' },
          { type: 'modified', category: 'config', item: 'Validation Rules', description: 'Updated validation configuration' }
        ],
        performance_score: 92,
        validation_status: 'passed',
        download_count: 856,
        is_current: false
      },
      {
        id: '3',
        version: '2.0.0',
        name: 'Major Refactor',
        description: 'Complete restructure of the data model with improved relationships',
        author: 'John Doe',
        created_at: '2024-11-20T09:00:00Z',
        status: 'published',
        changes: [
          { type: 'modified', category: 'entity', item: 'Task', description: 'Restructured task entity' },
          { type: 'added', category: 'entity', item: 'Project', description: 'New project management entity' },
          { type: 'removed', category: 'entity', item: 'Category', description: 'Merged into Task entity' },
          { type: 'modified', category: 'relationship', item: 'Task-User', description: 'Changed to many-to-many' }
        ],
        performance_score: 89,
        validation_status: 'warning',
        download_count: 2134,
        is_current: false
      },
      {
        id: '4',
        version: '1.9.5',
        name: 'Performance Improvements',
        description: 'Database optimizations and query performance enhancements',
        author: 'Mike Johnson',
        created_at: '2024-11-15T16:45:00Z',
        status: 'deprecated',
        changes: [
          { type: 'modified', category: 'config', item: 'Database Indexes', description: 'Added composite indexes' },
          { type: 'modified', category: 'field', item: 'Task.status', description: 'Optimized enum field' }
        ],
        performance_score: 87,
        validation_status: 'passed',
        download_count: 1678,
        is_current: false
      }
    ];

    setVersions(mockVersions);
    setSelectedVersion(mockVersions[0]);
  };

  const runValidation = async () => {
    setIsRunningValidation(true);
    
    // Simulate validation process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const mockResults: ValidationResult[] = [
      {
        category: 'structure',
        level: 'success',
        title: 'Entity Structure',
        description: 'All entities have valid structures with proper field definitions',
        auto_fixable: false
      },
      {
        category: 'performance',
        level: 'warning',
        title: 'Large Text Fields',
        description: `Entity "Task" has ${entities.filter(e => e.name === 'Task')[0]?.fields.filter(f => f.type === 'text').length || 2} large text fields that may impact performance`,
        suggestion: 'Consider using separate content entities for large text data',
        auto_fixable: false
      },
      {
        category: 'security',
        level: 'error',
        title: 'Missing Password Hashing',
        description: 'User entity password field lacks proper hashing configuration',
        suggestion: 'Configure bcrypt or similar password hashing mechanism',
        auto_fixable: true
      },
      {
        category: 'best_practices',
        level: 'info',
        title: 'Naming Conventions',
        description: 'All entities follow proper naming conventions (PascalCase)',
        auto_fixable: false
      },
      {
        category: 'structure',
        level: 'warning',
        title: 'Relationship Complexity',
        description: `Template has ${relationships.length} relationships. Consider simplifying if > 15`,
        suggestion: 'Group related entities or use composition patterns',
        auto_fixable: false
      },
      {
        category: 'performance',
        level: 'success',
        title: 'Field Optimization',
        description: 'All fields use appropriate data types for optimal storage',
        auto_fixable: false
      }
    ];

    setValidationResults(mockResults);
    setIsRunningValidation(false);
  };

  const generateOptimizations = async () => {
    setIsGeneratingOptimizations(true);
    
    // Simulate optimization analysis
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const mockOptimizations: OptimizationSuggestion[] = [
      {
        id: '1',
        category: 'performance',
        priority: 'high',
        title: 'Add Database Indexes',
        description: 'Add composite indexes on frequently queried field combinations',
        impact: 'Query performance improvement up to 300%',
        effort: 'low',
        auto_applicable: true
      },
      {
        id: '2',
        category: 'structure',
        priority: 'medium',
        title: 'Normalize User Preferences',
        description: 'Extract user preferences into separate entity to reduce User table size',
        impact: 'Improved data organization and reduced entity complexity',
        effort: 'medium',
        auto_applicable: false
      },
      {
        id: '3',
        category: 'naming',
        priority: 'low',
        title: 'Standardize Field Names',
        description: 'Use consistent naming pattern for timestamp fields (created_at, updated_at)',
        impact: 'Better code consistency and developer experience',
        effort: 'low',
        auto_applicable: true
      },
      {
        id: '4',
        category: 'relationships',
        priority: 'high',
        title: 'Optimize Many-to-Many Relations',
        description: 'Add junction table metadata for complex many-to-many relationships',
        impact: 'Better relationship management and query optimization',
        effort: 'medium',
        auto_applicable: false
      },
      {
        id: '5',
        category: 'performance',
        priority: 'medium',
        title: 'Implement Soft Deletes',
        description: 'Add soft delete functionality to maintain data integrity',
        impact: 'Data recovery capability and audit trail preservation',
        effort: 'low',
        auto_applicable: true
      }
    ];

    setOptimizations(mockOptimizations);
    setIsGeneratingOptimizations(false);
  };

  const createNewVersion = () => {
    const newVersion: TemplateVersion = {
      id: Date.now().toString(),
      version: '2.2.0',
      name: 'New Version',
      description: 'New version based on current template state',
      author: 'Current User',
      created_at: new Date().toISOString(),
      status: 'draft',
      changes: [],
      performance_score: 0,
      validation_status: 'passed',
      download_count: 0,
      is_current: false
    };

    setVersions([newVersion, ...versions]);
    setSelectedVersion(newVersion);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'text-green-700 bg-green-100';
      case 'draft':
        return 'text-yellow-700 bg-yellow-100';
      case 'deprecated':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-700 bg-gray-100';
    }
  };

  const getValidationIcon = (level: string) => {
    switch (level) {
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <Shield className="h-5 w-5 text-blue-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-700 bg-red-100 border-red-300';
      case 'medium':
        return 'text-yellow-700 bg-yellow-100 border-yellow-300';
      case 'low':
        return 'text-green-700 bg-green-100 border-green-300';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-300';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Advanced Template Features</h2>
            <p className="text-gray-600 mt-1">Version control, validation, and optimization tools</p>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <Settings className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'versions', label: 'Version Control', icon: GitBranch },
              { id: 'validation', label: 'Validation & Testing', icon: Shield },
              { id: 'optimization', label: 'Optimization', icon: TrendingUp },
              { id: 'testing', label: 'Performance Testing', icon: Activity }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'versions' && (
            <div className="flex h-full">
              {/* Version List */}
              <div className="w-1/3 border-r border-gray-200 overflow-auto">
                <div className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Template Versions</h3>
                    <button
                      onClick={createNewVersion}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  
                  <div className="space-y-3">
                    {versions.map(version => (
                      <div
                        key={version.id}
                        onClick={() => setSelectedVersion(version)}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedVersion?.id === version.id
                            ? 'border-blue-300 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Tag className="h-4 w-4 text-gray-400" />
                            <span className="font-medium">{version.version}</span>
                            {version.is_current && (
                              <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded">
                                Current
                              </span>
                            )}
                          </div>
                          <span className={`px-2 py-0.5 text-xs rounded ${getStatusColor(version.status)}`}>
                            {version.status}
                          </span>
                        </div>
                        
                        <h4 className="font-medium text-sm text-gray-900 mb-1">{version.name}</h4>
                        <p className="text-xs text-gray-600 line-clamp-2">{version.description}</p>
                        
                        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                          <span>{formatDate(version.created_at)}</span>
                          <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1">
                              <Download className="h-3 w-3" />
                              <span>{version.download_count}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <BarChart3 className="h-3 w-3" />
                              <span>{version.performance_score}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Version Details */}
              <div className="flex-1 p-6 overflow-auto">
                {selectedVersion ? (
                  <div className="space-y-6">
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-semibold text-gray-900">
                            {selectedVersion.name} ({selectedVersion.version})
                          </h3>
                          <p className="text-gray-600">{selectedVersion.description}</p>
                        </div>
                        
                        <div className="flex space-x-2">
                          <button className="px-3 py-1 text-sm border border-gray-300 hover:border-gray-400 rounded-lg transition-colors">
                            <Eye className="h-4 w-4 inline mr-1" />
                            Compare
                          </button>
                          <button className="px-3 py-1 text-sm border border-gray-300 hover:border-gray-400 rounded-lg transition-colors">
                            <Download className="h-4 w-4 inline mr-1" />
                            Export
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-4 gap-4 mb-6">
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">Author</div>
                          <div className="font-medium">{selectedVersion.author}</div>
                        </div>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">Status</div>
                          <span className={`px-2 py-1 text-xs rounded ${getStatusColor(selectedVersion.status)}`}>
                            {selectedVersion.status}
                          </span>
                        </div>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">Performance</div>
                          <div className="font-medium">{selectedVersion.performance_score}/100</div>
                        </div>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <div className="text-sm text-gray-600">Downloads</div>
                          <div className="font-medium">{selectedVersion.download_count}</div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Changes ({selectedVersion.changes.length})</h4>
                      <div className="space-y-2">
                        {selectedVersion.changes.map((change, index) => (
                          <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                            <div className={`w-2 h-2 rounded-full ${
                              change.type === 'added' ? 'bg-green-500' :
                              change.type === 'modified' ? 'bg-yellow-500' : 'bg-red-500'
                            }`} />
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <span className="font-medium capitalize">{change.type}</span>
                                <span className="text-sm text-gray-600">
                                  {change.category}: {change.item}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600">{change.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    Select a version to view details
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'validation' && (
            <div className="p-6 h-full overflow-auto">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Template Validation</h3>
                    <p className="text-gray-600">Validate structure, performance, security, and best practices</p>
                  </div>
                  
                  <button
                    onClick={runValidation}
                    disabled={isRunningValidation}
                    className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <RefreshCw className={`h-4 w-4 ${isRunningValidation ? 'animate-spin' : ''}`} />
                    <span>{isRunningValidation ? 'Running...' : 'Run Validation'}</span>
                  </button>
                </div>

                {isRunningValidation ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Analyzing template structure and configuration...</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {validationResults.map((result, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-start space-x-3">
                          {getValidationIcon(result.level)}
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium text-gray-900">{result.title}</h4>
                              <div className="flex items-center space-x-2">
                                <span className={`px-2 py-1 text-xs rounded ${
                                  result.level === 'error' ? 'bg-red-100 text-red-700' :
                                  result.level === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                                  result.level === 'success' ? 'bg-green-100 text-green-700' :
                                  'bg-blue-100 text-blue-700'
                                }`}>
                                  {result.category}
                                </span>
                                {result.auto_fixable && (
                                  <button className="px-2 py-1 text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 rounded transition-colors">
                                    Auto Fix
                                  </button>
                                )}
                              </div>
                            </div>
                            <p className="text-gray-600 mt-1">{result.description}</p>
                            {result.suggestion && (
                              <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-800">
                                <Lightbulb className="h-4 w-4 inline mr-1" />
                                {result.suggestion}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'optimization' && (
            <div className="p-6 h-full overflow-auto">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Template Optimization</h3>
                    <p className="text-gray-600">AI-powered suggestions to improve your template</p>
                  </div>
                  
                  <button
                    onClick={generateOptimizations}
                    disabled={isGeneratingOptimizations}
                    className="px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <Zap className={`h-4 w-4 ${isGeneratingOptimizations ? 'animate-pulse' : ''}`} />
                    <span>{isGeneratingOptimizations ? 'Analyzing...' : 'Generate Suggestions'}</span>
                  </button>
                </div>

                {isGeneratingOptimizations ? (
                  <div className="text-center py-12">
                    <div className="animate-pulse rounded-full h-8 w-8 bg-purple-200 mx-auto mb-4"></div>
                    <p className="text-gray-600">AI is analyzing your template for optimization opportunities...</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {optimizations.map((suggestion) => (
                      <div key={suggestion.id} className={`border rounded-lg p-4 ${getPriorityColor(suggestion.priority)} border`}>
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-start space-x-3">
                            <div className={`p-2 rounded-lg ${
                              suggestion.category === 'performance' ? 'bg-green-100 text-green-600' :
                              suggestion.category === 'structure' ? 'bg-blue-100 text-blue-600' :
                              suggestion.category === 'naming' ? 'bg-purple-100 text-purple-600' :
                              'bg-orange-100 text-orange-600'
                            }`}>
                              {suggestion.category === 'performance' ? <TrendingUp className="h-4 w-4" /> :
                               suggestion.category === 'structure' ? <Database className="h-4 w-4" /> :
                               suggestion.category === 'naming' ? <FileText className="h-4 w-4" /> :
                               <Layers className="h-4 w-4" />}
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900">{suggestion.title}</h4>
                              <p className="text-gray-600 text-sm mt-1">{suggestion.description}</p>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 text-xs rounded ${getPriorityColor(suggestion.priority)}`}>
                              {suggestion.priority} priority
                            </span>
                            {suggestion.auto_applicable && (
                              <button className="px-3 py-1 text-xs bg-green-600 text-white hover:bg-green-700 rounded transition-colors">
                                Apply
                              </button>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-4">
                            <span className="text-gray-600">
                              <Target className="h-4 w-4 inline mr-1" />
                              Impact: {suggestion.impact}
                            </span>
                            <span className="text-gray-600">
                              <Clock className="h-4 w-4 inline mr-1" />
                              Effort: {suggestion.effort}
                            </span>
                          </div>
                          
                          <button className="text-blue-600 hover:text-blue-700 flex items-center space-x-1">
                            <span>Learn more</span>
                            <ArrowRight className="h-3 w-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'testing' && (
            <div className="p-6 h-full overflow-auto">
              <div className="max-w-4xl mx-auto">
                <div className="text-center py-12">
                  <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Performance Testing</h3>
                  <p className="text-gray-600 mb-4">
                    Test your template's performance under various load conditions
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                    <div className="border border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-blue-400 hover:bg-blue-50 transition-colors cursor-pointer">
                      <Database className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                      <h4 className="font-medium text-gray-900">Database Load Test</h4>
                      <p className="text-sm text-gray-600 mt-1">Test database performance with large datasets</p>
                    </div>
                    
                    <div className="border border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-green-400 hover:bg-green-50 transition-colors cursor-pointer">
                      <Code className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <h4 className="font-medium text-gray-900">API Performance</h4>
                      <p className="text-sm text-gray-600 mt-1">Benchmark API response times and throughput</p>
                    </div>
                    
                    <div className="border border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-purple-400 hover:bg-purple-50 transition-colors cursor-pointer">
                      <Layers className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                      <h4 className="font-medium text-gray-900">UI Stress Test</h4>
                      <p className="text-sm text-gray-600 mt-1">Test frontend performance with complex data</p>
                    </div>
                  </div>
                  
                  <div className="mt-8">
                    <button className="px-6 py-3 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors">
                      Start Performance Analysis
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedTemplateFeatures;