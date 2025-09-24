import React, { useState } from 'react';
import {
  Play,
  Download,
  Eye,
  Folder,
  File,
  Check,
  X,
  Clock,
  Code,
  Database,
  Globe,
  Server,
  Layers,
  Settings,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Copy
} from 'lucide-react';
import { DomainConfig, Entity, Relationship, CodeGenerationProgress } from '../../types/template';

interface CodeGenerationDashboardProps {
  domainConfig: DomainConfig;
  entities: Entity[];
  relationships: Relationship[];
  onClose?: () => void;
}

interface GeneratedFile {
  path: string;
  type: 'model' | 'schema' | 'api' | 'component' | 'config' | 'migration' | 'test';
  size: number;
  status: 'generating' | 'completed' | 'error';
  content?: string;
  preview?: string;
}

interface FileTreeNode {
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileTreeNode[];
  size?: number;
  fileType?: string;
}

const CodeGenerationDashboard: React.FC<CodeGenerationDashboardProps> = ({
  domainConfig,
  entities,
  onClose
}) => {
  const [generationStatus, setGenerationStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState<CodeGenerationProgress>({
    status: 'pending',
    progress: 0,
    current_step: 'Initializing...',
    total_steps: 12,
    files_generated: 0,
    errors: []
  });

  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>([]);
  const [fileTree, setFileTree] = useState<FileTreeNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<GeneratedFile | null>(null);
  const [activeTab, setActiveTab] = useState<'progress' | 'files' | 'preview' | 'deploy'>('progress');
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [generationOptions, setGenerationOptions] = useState({
    generateBackend: true,
    generateFrontend: true,
    generateDatabase: true,
    generateTests: true,
    generateDocs: true,
    targetFramework: 'fastapi-react'
  });

  const startGeneration = async () => {
    setGenerationStatus('running');
    setProgress({
      status: 'running',
      progress: 0,
      current_step: 'Preparing generation environment...',
      total_steps: 12,
      files_generated: 0,
      errors: []
    });

    // Simulate code generation process
    const steps = [
      'Analyzing domain configuration...',
      'Generating data models...',
      'Creating database schemas...',
      'Building API endpoints...',
      'Generating frontend components...',
      'Creating authentication system...',
      'Setting up routing...',
      'Generating tests...',
      'Creating documentation...',
      'Optimizing code...',
      'Building project structure...',
      'Finalizing generation...'
    ];

    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const newProgress = {
        status: 'running' as const,
        progress: Math.round((i + 1) / steps.length * 100),
        current_step: steps[i],
        total_steps: steps.length,
        files_generated: Math.round((i + 1) * 4.2),
        errors: []
      };

      setProgress(newProgress);

      // Generate mock files during process
      if (i === 1) generateMockFiles('models');
      if (i === 2) generateMockFiles('schemas');
      if (i === 3) generateMockFiles('api');
      if (i === 4) generateMockFiles('components');
      if (i === 7) generateMockFiles('tests');
    }

    setGenerationStatus('completed');
    setProgress(prev => ({
      ...prev,
      status: 'completed',
      current_step: 'Generation completed successfully!'
    }));

    buildFileTree();
  };

  const generateMockFiles = (type: 'models' | 'schemas' | 'api' | 'components' | 'tests') => {
    const newFiles: GeneratedFile[] = [];

    if (type === 'models') {
      entities.forEach(entity => {
        newFiles.push({
          path: `backend/app/models/${entity.name.toLowerCase()}.py`,
          type: 'model',
          size: 2500 + Math.random() * 1000,
          status: 'completed',
          content: generateModelCode(entity),
          preview: `class ${entity.name}(BaseModel):\n    # Generated model for ${entity.name}\n    ${entity.fields.slice(0, 3).map(f => `${f.name}: ${f.type}`).join('\n    ')}`
        });
      });
    }

    if (type === 'schemas') {
      entities.forEach(entity => {
        newFiles.push({
          path: `backend/app/schemas/${entity.name.toLowerCase()}.py`,
          type: 'schema',
          size: 1800 + Math.random() * 800,
          status: 'completed',
          content: generateSchemaCode(entity),
          preview: `class ${entity.name}Schema(BaseSchema):\n    # Pydantic schema for ${entity.name}\n    ${entity.fields.slice(0, 3).map(f => `${f.name}: ${f.type}`).join('\n    ')}`
        });
      });
    }

    if (type === 'api') {
      entities.forEach(entity => {
        newFiles.push({
          path: `backend/app/api/routes/${entity.name.toLowerCase()}.py`,
          type: 'api',
          size: 3200 + Math.random() * 1200,
          status: 'completed',
          content: generateApiCode(entity),
          preview: `@router.get("/${entity.name.toLowerCase()}")\ndef get_${entity.name.toLowerCase()}():\n    # API endpoint for ${entity.name}`
        });
      });
    }

    if (type === 'components') {
      entities.forEach(entity => {
        newFiles.push({
          path: `frontend/src/components/${entity.name}/${entity.name}List.tsx`,
          type: 'component',
          size: 2800 + Math.random() * 1000,
          status: 'completed',
          content: generateComponentCode(entity),
          preview: `export const ${entity.name}List: React.FC = () => {\n  // React component for ${entity.name} list\n  return <div>...</div>;\n};`
        });
      });
    }

    if (type === 'tests') {
      entities.forEach(entity => {
        newFiles.push({
          path: `backend/tests/test_${entity.name.toLowerCase()}.py`,
          type: 'test',
          size: 1500 + Math.random() * 700,
          status: 'completed',
          content: generateTestCode(entity),
          preview: `def test_${entity.name.toLowerCase()}_creation():\n    # Test for ${entity.name} creation\n    assert True`
        });
      });
    }

    setGeneratedFiles(prev => [...prev, ...newFiles]);
  };

  const generateModelCode = (entity: Entity) => {
    return `from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ${entity.name}(Base):
    """
    Generated model for ${entity.name}
    Description: ${entity.description || 'No description provided'}
    """
    __tablename__ = "${entity.name.toLowerCase()}s"
    
    id = Column(Integer, primary_key=True, index=True)
${entity.fields.map(field => `    ${field.name} = Column(${getPythonType(field.type)}, ${field.required ? 'nullable=False' : 'nullable=True'}${field.unique ? ', unique=True' : ''})`).join('\n')}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<${entity.name}(id={self.id}, ${entity.fields[0]?.name || 'name'}={getattr(self, '${entity.fields[0]?.name || 'name'}', None)})>"
`;
  };

  const generateSchemaCode = (entity: Entity) => {
    return `from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ${entity.name}Base(BaseModel):
    """Base schema for ${entity.name}"""
${entity.fields.map(field => `    ${field.name}: ${field.required ? '' : 'Optional['}${getPydanticType(field.type)}${field.required ? '' : '] = None'}`).join('\n')}

class ${entity.name}Create(${entity.name}Base):
    """Schema for creating ${entity.name}"""
    pass

class ${entity.name}Update(${entity.name}Base):
    """Schema for updating ${entity.name}"""
${entity.fields.map(field => `    ${field.name}: Optional[${getPydanticType(field.type)}] = None`).join('\n')}

class ${entity.name}(${entity.name}Base):
    """Schema for ${entity.name} response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
`;
  };

  const generateApiCode = (entity: Entity) => {
    return `from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.${entity.name.toLowerCase()} import ${entity.name}
from ..schemas.${entity.name.toLowerCase()} import ${entity.name}Create, ${entity.name}Update, ${entity.name} as ${entity.name}Schema
from ..services.${entity.name.toLowerCase()}_service import ${entity.name}Service

router = APIRouter(prefix="/${entity.name.toLowerCase()}s", tags=["${entity.name.toLowerCase()}s"])

@router.get("/", response_model=List[${entity.name}Schema])
async def get_${entity.name.toLowerCase()}s(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all ${entity.name.toLowerCase()}s"""
    service = ${entity.name}Service(db)
    return service.get_all(skip=skip, limit=limit)

@router.post("/", response_model=${entity.name}Schema)
async def create_${entity.name.toLowerCase()}(
    ${entity.name.toLowerCase()}_data: ${entity.name}Create,
    db: Session = Depends(get_db)
):
    """Create a new ${entity.name.toLowerCase()}"""
    service = ${entity.name}Service(db)
    return service.create(${entity.name.toLowerCase()}_data)

@router.get("/{${entity.name.toLowerCase()}_id}", response_model=${entity.name}Schema)
async def get_${entity.name.toLowerCase()}(
    ${entity.name.toLowerCase()}_id: int,
    db: Session = Depends(get_db)
):
    """Get ${entity.name.toLowerCase()} by ID"""
    service = ${entity.name}Service(db)
    ${entity.name.toLowerCase()} = service.get_by_id(${entity.name.toLowerCase()}_id)
    if not ${entity.name.toLowerCase()}:
        raise HTTPException(status_code=404, detail="${entity.name} not found")
    return ${entity.name.toLowerCase()}

@router.put("/{${entity.name.toLowerCase()}_id}", response_model=${entity.name}Schema)
async def update_${entity.name.toLowerCase()}(
    ${entity.name.toLowerCase()}_id: int,
    ${entity.name.toLowerCase()}_data: ${entity.name}Update,
    db: Session = Depends(get_db)
):
    """Update ${entity.name.toLowerCase()}"""
    service = ${entity.name}Service(db)
    return service.update(${entity.name.toLowerCase()}_id, ${entity.name.toLowerCase()}_data)

@router.delete("/{${entity.name.toLowerCase()}_id}")
async def delete_${entity.name.toLowerCase()}(
    ${entity.name.toLowerCase()}_id: int,
    db: Session = Depends(get_db)
):
    """Delete ${entity.name.toLowerCase()}"""
    service = ${entity.name}Service(db)
    service.delete(${entity.name.toLowerCase()}_id)
    return {"message": "${entity.name} deleted successfully"}
`;
  };

  const generateComponentCode = (entity: Entity) => {
    return `import React, { useState, useEffect } from 'react';
import { ${entity.name} } from '../../types/${entity.name.toLowerCase()}';
import { ${entity.name}Service } from '../../services/${entity.name.toLowerCase()}Service';

interface ${entity.name}ListProps {
  onSelect?: (${entity.name.toLowerCase()}: ${entity.name}) => void;
}

export const ${entity.name}List: React.FC<${entity.name}ListProps> = ({ onSelect }) => {
  const [${entity.name.toLowerCase()}s, set${entity.name}s] = useState<${entity.name}[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetch${entity.name}s = async () => {
      try {
        const data = await ${entity.name}Service.getAll();
        set${entity.name}s(data);
      } catch (err) {
        setError('Failed to fetch ${entity.name.toLowerCase()}s');
      } finally {
        setLoading(false);
      }
    };

    fetch${entity.name}s();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">${entity.name} List</h2>
      <div className="grid gap-4">
        {${entity.name.toLowerCase()}s.map((${entity.name.toLowerCase()}) => (
          <div
            key={${entity.name.toLowerCase()}.id}
            className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
            onClick={() => onSelect?.(${entity.name.toLowerCase()})}
          >
${entity.fields.slice(0, 3).map(field => `            <p><strong>${field.title || field.name}:</strong> {${entity.name.toLowerCase()}.${field.name}}</p>`).join('\n')}
          </div>
        ))}
      </div>
    </div>
  );
};
`;
  };

  const generateTestCode = (entity: Entity) => {
    return `import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.${entity.name.toLowerCase()} import ${entity.name}
from app.schemas.${entity.name.toLowerCase()} import ${entity.name}Create

client = TestClient(app)

def test_create_${entity.name.toLowerCase()}(db: Session):
    """Test creating a ${entity.name.toLowerCase()}"""
    ${entity.name.toLowerCase()}_data = {
${entity.fields.slice(0, 3).map(field => `        "${field.name}": ${getTestValue(field.type)}`).join(',\n')}
    }
    
    response = client.post("/${entity.name.toLowerCase()}s/", json=${entity.name.toLowerCase()}_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["${entity.fields[0]?.name || 'name'}"] == ${entity.name.toLowerCase()}_data["${entity.fields[0]?.name || 'name'}"]

def test_get_${entity.name.toLowerCase()}s(db: Session):
    """Test getting all ${entity.name.toLowerCase()}s"""
    response = client.get("/${entity.name.toLowerCase()}s/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_${entity.name.toLowerCase()}_by_id(db: Session):
    """Test getting ${entity.name.toLowerCase()} by ID"""
    # Create a ${entity.name.toLowerCase()} first
    ${entity.name.toLowerCase()}_data = {
${entity.fields.slice(0, 2).map(field => `        "${field.name}": ${getTestValue(field.type)}`).join(',\n')}
    }
    create_response = client.post("/${entity.name.toLowerCase()}s/", json=${entity.name.toLowerCase()}_data)
    ${entity.name.toLowerCase()}_id = create_response.json()["id"]
    
    response = client.get(f"/${entity.name.toLowerCase()}s/{${entity.name.toLowerCase()}_id}")
    assert response.status_code == 200
`;
  };

  const getPythonType = (fieldType: string) => {
    const typeMap: Record<string, string> = {
      'string': 'String',
      'integer': 'Integer',
      'boolean': 'Boolean',
      'date': 'DateTime',
      'datetime': 'DateTime',
      'text': 'Text',
      'email': 'String',
      'url': 'String'
    };
    return typeMap[fieldType] || 'String';
  };

  const getPydanticType = (fieldType: string) => {
    const typeMap: Record<string, string> = {
      'string': 'str',
      'integer': 'int',
      'boolean': 'bool',
      'date': 'datetime',
      'datetime': 'datetime',
      'text': 'str',
      'email': 'str',
      'url': 'str'
    };
    return typeMap[fieldType] || 'str';
  };

  const getTestValue = (fieldType: string) => {
    const valueMap: Record<string, string> = {
      'string': '"Test Value"',
      'integer': '123',
      'boolean': 'true',
      'email': '"test@example.com"',
      'text': '"Test text content"'
    };
    return valueMap[fieldType] || '"test"';
  };

  const buildFileTree = () => {
    const tree: FileTreeNode[] = [
      {
        name: 'backend',
        type: 'folder',
        path: 'backend',
        children: [
          {
            name: 'app',
            type: 'folder',
            path: 'backend/app',
            children: [
              {
                name: 'models',
                type: 'folder',
                path: 'backend/app/models',
                children: entities.map(entity => ({
                  name: `${entity.name.toLowerCase()}.py`,
                  type: 'file' as const,
                  path: `backend/app/models/${entity.name.toLowerCase()}.py`,
                  fileType: 'model',
                  size: 2500
                }))
              },
              {
                name: 'schemas',
                type: 'folder',
                path: 'backend/app/schemas',
                children: entities.map(entity => ({
                  name: `${entity.name.toLowerCase()}.py`,
                  type: 'file' as const,
                  path: `backend/app/schemas/${entity.name.toLowerCase()}.py`,
                  fileType: 'schema',
                  size: 1800
                }))
              },
              {
                name: 'api',
                type: 'folder',
                path: 'backend/app/api',
                children: [
                  {
                    name: 'routes',
                    type: 'folder',
                    path: 'backend/app/api/routes',
                    children: entities.map(entity => ({
                      name: `${entity.name.toLowerCase()}.py`,
                      type: 'file' as const,
                      path: `backend/app/api/routes/${entity.name.toLowerCase()}.py`,
                      fileType: 'api',
                      size: 3200
                    }))
                  }
                ]
              }
            ]
          },
          {
            name: 'tests',
            type: 'folder',
            path: 'backend/tests',
            children: entities.map(entity => ({
              name: `test_${entity.name.toLowerCase()}.py`,
              type: 'file' as const,
              path: `backend/tests/test_${entity.name.toLowerCase()}.py`,
              fileType: 'test',
              size: 1500
            }))
          }
        ]
      },
      {
        name: 'frontend',
        type: 'folder',
        path: 'frontend',
        children: [
          {
            name: 'src',
            type: 'folder',
            path: 'frontend/src',
            children: [
              {
                name: 'components',
                type: 'folder',
                path: 'frontend/src/components',
                children: entities.map(entity => ({
                  name: entity.name,
                  type: 'folder' as const,
                  path: `frontend/src/components/${entity.name}`,
                  children: [
                    {
                      name: `${entity.name}List.tsx`,
                      type: 'file' as const,
                      path: `frontend/src/components/${entity.name}/${entity.name}List.tsx`,
                      fileType: 'component',
                      size: 2800
                    },
                    {
                      name: `${entity.name}Form.tsx`,
                      type: 'file' as const,
                      path: `frontend/src/components/${entity.name}/${entity.name}Form.tsx`,
                      fileType: 'component',
                      size: 2400
                    }
                  ]
                }))
              }
            ]
          }
        ]
      }
    ];

    setFileTree(tree);
    setExpandedFolders(new Set(['backend', 'frontend', 'backend/app', 'frontend/src']));
  };

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const renderFileTree = (nodes: FileTreeNode[], depth = 0) => {
    return nodes.map(node => (
      <div key={node.path} className={`${depth > 0 ? 'ml-4' : ''}`}>
        <div
          className="flex items-center space-x-2 py-1 px-2 rounded hover:bg-gray-100 cursor-pointer"
          onClick={() => {
            if (node.type === 'folder') {
              toggleFolder(node.path);
            } else {
              const file = generatedFiles.find(f => f.path === node.path);
              if (file) setSelectedFile(file);
            }
          }}
        >
          {node.type === 'folder' ? (
            <>
              {expandedFolders.has(node.path) ? (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
              <Folder className="h-4 w-4 text-blue-500" />
            </>
          ) : (
            <>
              <div className="w-4" />
              <File className="h-4 w-4 text-gray-500" />
            </>
          )}
          <span className="text-sm text-gray-700">{node.name}</span>
          {node.size && (
            <span className="text-xs text-gray-500 ml-auto">
              {(node.size / 1024).toFixed(1)} KB
            </span>
          )}
        </div>
        {node.type === 'folder' && expandedFolders.has(node.path) && node.children && (
          <div>
            {renderFileTree(node.children, depth + 1)}
          </div>
        )}
      </div>
    ));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
      case 'completed':
        return <Check className="h-4 w-4 text-green-500" />;
      case 'error':
        return <X className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getFileTypeIcon = (type: string) => {
    const icons = {
      model: <Database className="h-4 w-4 text-blue-500" />,
      schema: <Code className="h-4 w-4 text-green-500" />,
      api: <Server className="h-4 w-4 text-purple-500" />,
      component: <Layers className="h-4 w-4 text-orange-500" />,
      test: <Check className="h-4 w-4 text-red-500" />,
      config: <Settings className="h-4 w-4 text-gray-500" />
    };
    return icons[type as keyof typeof icons] || <File className="h-4 w-4 text-gray-400" />;
  };

  const downloadGeneratedCode = () => {
    // Create a zip-like structure simulation
    const projectStructure = {
      [`${domainConfig.name || 'generated-project'}.zip`]: {
        backend: generatedFiles.filter(f => f.path.startsWith('backend')),
        frontend: generatedFiles.filter(f => f.path.startsWith('frontend'))
      }
    };

    console.log('Downloading generated project:', projectStructure);
    alert(`Generated project "${domainConfig.name || 'generated-project'}" ready for download!\n\nFiles: ${generatedFiles.length}\nSize: ~${Math.round(generatedFiles.reduce((sum, f) => sum + f.size, 0) / 1024)} KB`);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">
              Code Generation Dashboard
            </h2>
            <p className="text-gray-600 mt-1">
              Generate and manage code for "{domainConfig.title || domainConfig.name}"
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {generationStatus === 'completed' && (
              <button
                onClick={downloadGeneratedCode}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white 
                         hover:bg-green-700 rounded-lg transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>Download Project</span>
              </button>
            )}
            
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'progress', label: 'Generation Progress', icon: RefreshCw },
              { id: 'files', label: 'Generated Files', icon: Folder },
              { id: 'preview', label: 'Code Preview', icon: Eye },
              { id: 'deploy', label: 'Deployment', icon: Globe }
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
          {activeTab === 'progress' && (
            <div className="p-6 h-full overflow-auto">
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Generation Options */}
                {generationStatus === 'idle' && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      Generation Options
                    </h3>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                      {Object.entries(generationOptions).map(([key, value]) => {
                        if (key === 'targetFramework') return null;
                        
                        return (
                          <label key={key} className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={value as boolean}
                              onChange={(e) => setGenerationOptions(prev => ({
                                ...prev,
                                [key]: e.target.checked
                              }))}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700 capitalize">
                              {key.replace(/([A-Z])/g, ' $1').replace('generate', '').trim()}
                            </span>
                          </label>
                        );
                      })}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Target Framework
                      </label>
                      <select
                        value={generationOptions.targetFramework}
                        onChange={(e) => setGenerationOptions(prev => ({
                          ...prev,
                          targetFramework: e.target.value
                        }))}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                                 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="fastapi-react">FastAPI + React</option>
                        <option value="django-vue">Django + Vue.js</option>
                        <option value="express-react">Express.js + React</option>
                        <option value="flask-svelte">Flask + Svelte</option>
                      </select>
                    </div>
                  </div>
                )}

                {/* Start Generation Button */}
                {generationStatus === 'idle' && (
                  <div className="text-center">
                    <button
                      onClick={startGeneration}
                      className="px-8 py-3 bg-blue-600 text-white hover:bg-blue-700 
                               rounded-lg font-semibold transition-colors flex items-center 
                               space-x-2 mx-auto"
                    >
                      <Play className="h-5 w-5" />
                      <span>Start Code Generation</span>
                    </button>
                  </div>
                )}

                {/* Progress Display */}
                {(generationStatus === 'running' || generationStatus === 'completed') && (
                  <div className="space-y-6">
                    {/* Progress Bar */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          {progress.current_step}
                        </span>
                        <span className="text-sm text-gray-500">
                          {progress.progress}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${progress.progress}%` }}
                        />
                      </div>
                    </div>

                    {/* Statistics */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-white border rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {progress.files_generated}
                        </div>
                        <div className="text-sm text-gray-500">Files Generated</div>
                      </div>
                      <div className="bg-white border rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {Math.floor(progress.files_generated * 2.3)} KB
                        </div>
                        <div className="text-sm text-gray-500">Code Size</div>
                      </div>
                      <div className="bg-white border rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-purple-600">
                          {entities.length}
                        </div>
                        <div className="text-sm text-gray-500">Entities</div>
                      </div>
                    </div>

                    {/* Recent Files */}
                    {generatedFiles.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-3">Recent Files Generated</h4>
                        <div className="space-y-2 max-h-64 overflow-auto">
                          {generatedFiles.slice(-8).reverse().map(file => (
                            <div key={file.path} className="flex items-center space-x-3 p-3 bg-white border rounded-lg">
                              {getFileTypeIcon(file.type)}
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">{file.path}</p>
                                <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                              </div>
                              {getStatusIcon(file.status)}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Completion Status */}
                {generationStatus === 'completed' && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                    <Check className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-green-900 mb-2">
                      Code Generation Complete!
                    </h3>
                    <p className="text-green-700 mb-4">
                      Successfully generated {progress.files_generated} files for your {domainConfig.domain_type} application.
                    </p>
                    <button
                      onClick={() => setActiveTab('files')}
                      className="px-4 py-2 bg-green-600 text-white hover:bg-green-700 
                               rounded-lg transition-colors"
                    >
                      View Generated Files
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'files' && (
            <div className="flex h-full">
              {/* File Tree */}
              <div className="w-1/3 border-r border-gray-200 p-4 overflow-auto">
                <h3 className="font-medium text-gray-900 mb-3">Project Structure</h3>
                {fileTree.length > 0 ? (
                  <div className="text-sm">
                    {renderFileTree(fileTree)}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No files generated yet</p>
                )}
              </div>

              {/* File List */}
              <div className="flex-1 p-4 overflow-auto">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-medium text-gray-900">Generated Files ({generatedFiles.length})</h3>
                  <div className="text-sm text-gray-500">
                    Total: {(generatedFiles.reduce((sum, f) => sum + f.size, 0) / 1024).toFixed(1)} KB
                  </div>
                </div>
                
                <div className="space-y-2">
                  {generatedFiles.map(file => (
                    <div
                      key={file.path}
                      className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedFile(file)}
                    >
                      {getFileTypeIcon(file.type)}
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{file.path}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>{(file.size / 1024).toFixed(1)} KB</span>
                          <span className="capitalize">{file.type}</span>
                        </div>
                      </div>
                      {getStatusIcon(file.status)}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigator.clipboard.writeText(file.content || '');
                          alert('File content copied to clipboard!');
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'preview' && (
            <div className="flex h-full">
              {/* File Selector */}
              <div className="w-1/4 border-r border-gray-200 p-4 overflow-auto">
                <h3 className="font-medium text-gray-900 mb-3">Select File</h3>
                <div className="space-y-1">
                  {generatedFiles.map(file => (
                    <button
                      key={file.path}
                      onClick={() => setSelectedFile(file)}
                      className={`w-full text-left p-2 text-sm rounded ${
                        selectedFile?.path === file.path
                          ? 'bg-blue-50 text-blue-700'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        {getFileTypeIcon(file.type)}
                        <span className="truncate">{file.path.split('/').pop()}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Code Preview */}
              <div className="flex-1 p-4 overflow-auto">
                {selectedFile ? (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-medium text-gray-900">{selectedFile.path}</h3>
                        <p className="text-sm text-gray-500 capitalize">{selectedFile.type} • {(selectedFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                      <button
                        onClick={() => navigator.clipboard.writeText(selectedFile.content || '')}
                        className="flex items-center space-x-2 px-3 py-1 text-sm border border-gray-300 
                                 hover:bg-gray-50 rounded"
                      >
                        <Copy className="h-4 w-4" />
                        <span>Copy</span>
                      </button>
                    </div>
                    
                    <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                      <pre className="text-green-400 text-sm">
                        <code>{selectedFile.content}</code>
                      </pre>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    <div className="text-center">
                      <Eye className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Select a file to preview its content</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'deploy' && (
            <div className="p-6 h-full overflow-auto">
              <div className="max-w-4xl mx-auto space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Deployment Options
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Deploy your generated application to various platforms.
                  </p>
                </div>

                <div className="grid gap-6">
                  {[
                    {
                      name: 'Vercel',
                      icon: '▲',
                      description: 'Deploy frontend instantly with automatic builds',
                      status: 'available',
                      features: ['Automatic deployments', 'Edge functions', 'Analytics']
                    },
                    {
                      name: 'Heroku',
                      icon: '🟣',
                      description: 'Full-stack deployment with database support',
                      status: 'available',
                      features: ['Auto scaling', 'Add-ons marketplace', 'Metrics']
                    },
                    {
                      name: 'AWS',
                      icon: '🌐',
                      description: 'Enterprise deployment with comprehensive services',
                      status: 'coming-soon',
                      features: ['Load balancing', 'Auto scaling', 'Multi-region']
                    },
                    {
                      name: 'Docker',
                      icon: '🐳',
                      description: 'Containerized deployment for any environment',
                      status: 'available',
                      features: ['Container orchestration', 'Health checks', 'Scaling']
                    }
                  ].map(platform => (
                    <div key={platform.name} className="border rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl">{platform.icon}</div>
                          <div>
                            <h4 className="font-semibold text-gray-900">{platform.name}</h4>
                            <p className="text-sm text-gray-600">{platform.description}</p>
                          </div>
                        </div>
                        
                        <button
                          disabled={platform.status === 'coming-soon'}
                          className={`px-4 py-2 rounded-lg font-medium ${
                            platform.status === 'available'
                              ? 'bg-blue-600 text-white hover:bg-blue-700'
                              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          }`}
                        >
                          {platform.status === 'available' ? 'Deploy' : 'Coming Soon'}
                        </button>
                      </div>
                      
                      <div className="flex flex-wrap gap-2">
                        {platform.features.map(feature => (
                          <span
                            key={feature}
                            className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {generationStatus === 'completed' && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <div className="flex items-start space-x-3">
                      <ExternalLink className="h-5 w-5 text-blue-500 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-900 mb-2">Ready to Deploy</h4>
                        <p className="text-blue-700 text-sm mb-4">
                          Your application is generated and ready for deployment. Choose a platform above to get started.
                        </p>
                        <div className="space-y-2 text-sm text-blue-700">
                          <p>• Backend: FastAPI application with {entities.length} models</p>
                          <p>• Frontend: React application with component library</p>
                          <p>• Database: PostgreSQL with migrations</p>
                          <p>• Tests: {entities.length * 3} test files generated</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeGenerationDashboard;