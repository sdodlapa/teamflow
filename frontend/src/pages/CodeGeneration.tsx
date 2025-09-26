/**
 * Code Generation UI - Day 11 Implementation
 * Interface for the CodeGenerationOrchestrator service
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Play, 
  Download, 
  FileText, 
  Zap,
  CheckCircle, 
  AlertCircle, 
  Code,
  Server,
  Globe,
  Database,
  Settings,
  Copy,
  ChevronDown,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingComponents';

// Generation interfaces
interface GenerationOptions {
  includeBackend: boolean;
  includeFrontend: boolean;
  includeDatabase: boolean;
  includeTests: boolean;
  includeDocumentation: boolean;
  outputPath: string;
}

interface GenerationProgress {
  status: 'idle' | 'running' | 'completed' | 'failed';
  currentStep: string;
  totalSteps: number;
  completedSteps: number;
  progress: number;
  logs: GenerationLog[];
  startTime?: Date;
  endTime?: Date;
}

interface GenerationLog {
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  details?: string;
}

interface GeneratedFile {
  path: string;
  type: 'model' | 'schema' | 'route' | 'service' | 'frontend' | 'config' | 'test';
  size: number;
  content: string;
  language: string;
}

interface GenerationResult {
  success: boolean;
  templateId: string;
  templateName: string;
  generationId: string;
  files: GeneratedFile[];
  duration: number;
  totalFiles: number;
  totalLines: number;
  error?: string;
}

export const CodeGeneration: React.FC = () => {
  const { templateId } = useParams<{ templateId: string }>();
  const navigate = useNavigate();
  
  // State management
  const [template, setTemplate] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [options, setOptions] = useState<GenerationOptions>({
    includeBackend: true,
    includeFrontend: true,
    includeDatabase: true,
    includeTests: false,
    includeDocumentation: false,
    outputPath: '/generated'
  });
  
  const [progress, setProgress] = useState<GenerationProgress>({
    status: 'idle',
    currentStep: '',
    totalSteps: 0,
    completedSteps: 0,
    progress: 0,
    logs: []
  });
  
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<GeneratedFile | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  // Load template data
  useEffect(() => {
    const loadTemplate = async () => {
      try {
        setLoading(true);
        
        if (!templateId) {
          throw new Error('Template ID is required');
        }

        // Load template details (using domain details endpoint)
        const response = await fetch(`/api/v1/template/domains/${templateId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to load template: ${response.statusText}`);
        }
        
        const data = await response.json();
        setTemplate(data);
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load template');
      } finally {
        setLoading(false);
      }
    };

    loadTemplate();
  }, [templateId]);

  // Handle generation start
  const handleStartGeneration = async () => {
    try {
      setProgress({
        status: 'running',
        currentStep: 'Initializing generation...',
        totalSteps: 8,
        completedSteps: 0,
        progress: 0,
        logs: [{
          timestamp: new Date(),
          level: 'info',
          message: 'Starting code generation...'
        }],
        startTime: new Date()
      });

      // Call the actual backend API
      const response = await fetch(`/api/v1/template/domains/${templateId}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          include_backend: options.includeBackend,
          include_frontend: options.includeFrontend,
          include_database: options.includeDatabase,
          include_tests: options.includeTests,
          include_documentation: options.includeDocumentation,
          output_path: options.outputPath,
          entities: null // Generate all entities
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Code generation failed');
      }

      const generationResult = await response.json();
      
      // Create result with generated files (simplified for now)
      const mockFiles: GeneratedFile[] = [
        {
          path: 'backend/models/generated_model.py',
          type: 'model',
          size: 2456,
          content: `# Generated model for ${template?.domain?.title}
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from app.models.base import BaseModel

class GeneratedModel(BaseModel):
    __tablename__ = "generated_models"
    
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)`,
          language: 'python'
        },
        {
          path: 'frontend/src/components/GeneratedComponent.tsx',
          type: 'frontend',
          size: 1834,
          content: `// Generated component for ${template?.domain?.title}
import React from 'react';

interface GeneratedComponentProps {
  data: any;
}

export const GeneratedComponent: React.FC<GeneratedComponentProps> = ({ data }) => {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold">Generated Component</h2>
      <p>This component was generated from your domain configuration.</p>
    </div>
  );
};`,
          language: 'typescript'
        }
      ];

      const finalResult: GenerationResult = {
        success: generationResult.success,
        templateId: templateId || '',
        templateName: template?.domain?.title || 'Template',
        generationId: generationResult.generation_id,
        files: mockFiles,
        duration: generationResult.generation_time_seconds,
        totalFiles: generationResult.files_generated,
        totalLines: generationResult.total_lines,
        error: generationResult.success ? undefined : generationResult.errors.join(', ')
      };

      setResult(finalResult);
      setProgress(prev => ({
        ...prev,
        status: 'completed',
        progress: 100,
        completedSteps: prev.totalSteps,
        currentStep: 'Generation completed successfully!',
        endTime: new Date(),
        logs: [...prev.logs, {
          timestamp: new Date(),
          level: 'success',
          message: `Generated ${finalResult.totalFiles} files with ${finalResult.totalLines} total characters in ${finalResult.duration}s`
        }]
      }));
      
    } catch (err) {
      setProgress(prev => ({
        ...prev,
        status: 'failed',
        currentStep: 'Generation failed',
        logs: [...prev.logs, {
          timestamp: new Date(),
          level: 'error',
          message: err instanceof Error ? err.message : 'Generation failed',
          details: err instanceof Error ? err.stack : undefined
        }]
      }));
    }
  };



  // Handle file download
  const handleDownloadFiles = () => {
    if (!result) return;
    
    // Create a mock download (in real implementation, would create ZIP)
    const dataStr = JSON.stringify(result.files, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${result.templateName.toLowerCase().replace(/\s+/g, '_')}_generated.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // File tree utilities
  const buildFileTree = (files: GeneratedFile[]) => {
    const tree: any = {};
    
    files.forEach(file => {
      const parts = file.path.split('/');
      let current = tree;
      
      parts.forEach((part, index) => {
        if (index === parts.length - 1) {
          current[part] = file;
        } else {
          if (!current[part]) {
            current[part] = {};
          }
          current = current[part];
        }
      });
    });
    
    return tree;
  };

  const renderFileTree = (tree: any, path: string = '') => {
    return Object.entries(tree).map(([name, value]) => {
      const currentPath = path ? `${path}/${name}` : name;
      const isFile = value && typeof value === 'object' && 'content' in value;
      
      if (isFile) {
        const file = value as GeneratedFile;
        return (
          <div 
            key={currentPath}
            className={`flex items-center py-1 px-2 cursor-pointer rounded text-sm hover:bg-gray-100 ${
              selectedFile === file ? 'bg-blue-50 text-blue-700' : ''
            }`}
            onClick={() => setSelectedFile(file)}
          >
            <FileText className="h-4 w-4 mr-2 text-gray-400" />
            <span>{name}</span>
            <span className="ml-auto text-xs text-gray-500">
              {file.size} bytes
            </span>
          </div>
        );
      } else {
        const isExpanded = expandedFolders.has(currentPath);
        return (
          <div key={currentPath}>
            <div 
              className="flex items-center py-1 px-2 cursor-pointer text-sm hover:bg-gray-50"
              onClick={() => {
                const newExpanded = new Set(expandedFolders);
                if (isExpanded) {
                  newExpanded.delete(currentPath);
                } else {
                  newExpanded.add(currentPath);
                }
                setExpandedFolders(newExpanded);
              }}
            >
              {isExpanded ? 
                <ChevronDown className="h-4 w-4 mr-1" /> :
                <ChevronRight className="h-4 w-4 mr-1" />
              }
              <span className="font-medium">{name}/</span>
            </div>
            {isExpanded && (
              <div className="ml-4">
                {renderFileTree(value, currentPath)}
              </div>
            )}
          </div>
        );
      }
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !template) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Template</h2>
          <p className="text-gray-600 mb-4">{error || 'Template not found'}</p>
          <button
            onClick={() => navigate('/templates')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Templates
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/templates')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600 rounded-md"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Code Generation</h1>
                <p className="text-sm text-gray-600">
                  Generate application code from {template.domain.title}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {result && (
                <button
                  onClick={handleDownloadFiles}
                  className="flex items-center px-3 py-2 border border-gray-300 text-sm rounded-md hover:bg-gray-50"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </button>
              )}
              
              {progress.status === 'idle' && (
                <button
                  onClick={handleStartGeneration}
                  className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Generate Code
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Generation Options</h3>
              
              <div className="space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={options.includeBackend}
                    onChange={(e) => setOptions({...options, includeBackend: e.target.checked})}
                    className="rounded border-gray-300"
                  />
                  <div className="ml-3">
                    <div className="flex items-center">
                      <Server className="h-4 w-4 text-blue-500 mr-2" />
                      <span className="text-sm font-medium">Backend API</span>
                    </div>
                    <p className="text-xs text-gray-500">FastAPI routes, models, schemas</p>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={options.includeFrontend}
                    onChange={(e) => setOptions({...options, includeFrontend: e.target.checked})}
                    className="rounded border-gray-300"
                  />
                  <div className="ml-3">
                    <div className="flex items-center">
                      <Globe className="h-4 w-4 text-green-500 mr-2" />
                      <span className="text-sm font-medium">Frontend Components</span>
                    </div>
                    <p className="text-xs text-gray-500">React components, forms, pages</p>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={options.includeDatabase}
                    onChange={(e) => setOptions({...options, includeDatabase: e.target.checked})}
                    className="rounded border-gray-300"
                  />
                  <div className="ml-3">
                    <div className="flex items-center">
                      <Database className="h-4 w-4 text-purple-500 mr-2" />
                      <span className="text-sm font-medium">Database Schema</span>
                    </div>
                    <p className="text-xs text-gray-500">Migrations, seed data</p>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={options.includeTests}
                    onChange={(e) => setOptions({...options, includeTests: e.target.checked})}
                    className="rounded border-gray-300"
                  />
                  <div className="ml-3">
                    <div className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-orange-500 mr-2" />
                      <span className="text-sm font-medium">Unit Tests</span>
                    </div>
                    <p className="text-xs text-gray-500">API tests, component tests</p>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={options.includeDocumentation}
                    onChange={(e) => setOptions({...options, includeDocumentation: e.target.checked})}
                    className="rounded border-gray-300"
                  />
                  <div className="ml-3">
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 text-gray-500 mr-2" />
                      <span className="text-sm font-medium">Documentation</span>
                    </div>
                    <p className="text-xs text-gray-500">README, API docs</p>
                  </div>
                </label>
              </div>

              {/* Template Summary */}
              <div className="mt-6 pt-6 border-t">
                <h4 className="font-medium text-gray-900 mb-3">Template Summary</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Entities:</span>
                    <span className="font-medium">{template.metadata.total_entities}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Fields:</span>
                    <span className="font-medium">{template.metadata.total_fields}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Relationships:</span>
                    <span className="font-medium">{template.metadata.total_relationships}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Progress Panel */}
            {progress.status !== 'idle' && (
              <div className="bg-white rounded-lg shadow mb-6">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Generation Progress</h3>
                    <div className="flex items-center">
                      {progress.status === 'running' && (
                        <Loader2 className="h-5 w-5 text-blue-500 animate-spin mr-2" />
                      )}
                      {progress.status === 'completed' && (
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      )}
                      {progress.status === 'failed' && (
                        <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                      )}
                      <span className={`text-sm font-medium ${
                        progress.status === 'running' ? 'text-blue-600' :
                        progress.status === 'completed' ? 'text-green-600' :
                        progress.status === 'failed' ? 'text-red-600' : ''
                      }`}>
                        {progress.status === 'running' && 'Generating...'}
                        {progress.status === 'completed' && 'Completed'}
                        {progress.status === 'failed' && 'Failed'}
                      </span>
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>{progress.currentStep}</span>
                      <span>{progress.completedSteps}/{progress.totalSteps}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${
                          progress.status === 'completed' ? 'bg-green-500' :
                          progress.status === 'failed' ? 'bg-red-500' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${progress.progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Generation Logs */}
                  <div className="bg-gray-50 rounded-md p-3 max-h-48 overflow-y-auto">
                    {progress.logs.map((log, index) => (
                      <div key={index} className="flex items-start text-sm mb-1">
                        <span className="text-gray-400 mr-2 font-mono text-xs">
                          {log.timestamp.toLocaleTimeString()}
                        </span>
                        <div className={`flex-1 ${
                          log.level === 'error' ? 'text-red-600' :
                          log.level === 'warning' ? 'text-yellow-600' :
                          log.level === 'success' ? 'text-green-600' :
                          'text-gray-700'
                        }`}>
                          {log.message}
                          {log.details && (
                            <div className="text-xs text-gray-500 mt-1 font-mono">
                              {log.details}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Results Panel */}
            {result && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* File Tree */}
                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b">
                    <h3 className="font-medium text-gray-900">Generated Files</h3>
                    <p className="text-sm text-gray-600">
                      {result.totalFiles} files, {result.totalLines} lines of code
                    </p>
                  </div>
                  <div className="p-4 max-h-96 overflow-y-auto">
                    {result.files.length > 0 ? (
                      renderFileTree(buildFileTree(result.files))
                    ) : (
                      <p className="text-gray-500 text-center py-8">No files generated</p>
                    )}
                  </div>
                </div>

                {/* Code Preview */}
                <div className="bg-white rounded-lg shadow">
                  <div className="p-4 border-b">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-gray-900">
                        {selectedFile ? selectedFile.path : 'Code Preview'}
                      </h3>
                      {selectedFile && (
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(selectedFile.content);
                          }}
                          className="flex items-center text-sm text-gray-500 hover:text-gray-700"
                        >
                          <Copy className="h-4 w-4 mr-1" />
                          Copy
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="p-4 max-h-96 overflow-y-auto">
                    {selectedFile ? (
                      <pre className="text-sm text-gray-800 font-mono bg-gray-50 p-3 rounded overflow-x-auto">
                        <code>{selectedFile.content}</code>
                      </pre>
                    ) : (
                      <div className="text-center py-8">
                        <Code className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500">Select a file to view its content</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Initial State */}
            {progress.status === 'idle' && !result && (
              <div className="bg-white rounded-lg shadow">
                <div className="p-8 text-center">
                  <Zap className="h-16 w-16 text-blue-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to Generate</h3>
                  <p className="text-gray-600 mb-6">
                    Click "Generate Code" to create a complete application from your template configuration.
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="text-center p-3 bg-blue-50 rounded">
                      <Server className="h-6 w-6 text-blue-600 mx-auto mb-1" />
                      <span className="text-blue-700 font-medium">Backend</span>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded">
                      <Globe className="h-6 w-6 text-green-600 mx-auto mb-1" />
                      <span className="text-green-700 font-medium">Frontend</span>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded">
                      <Database className="h-6 w-6 text-purple-600 mx-auto mb-1" />
                      <span className="text-purple-700 font-medium">Database</span>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <Settings className="h-6 w-6 text-gray-600 mx-auto mb-1" />
                      <span className="text-gray-700 font-medium">Config</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeGeneration;