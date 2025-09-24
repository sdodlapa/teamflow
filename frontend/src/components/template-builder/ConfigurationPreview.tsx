import React, { useState } from 'react';
import {
  Eye,
  Code,
  Database,
  FileText,
  Download,
  Share2,
  CheckCircle,
  AlertTriangle,
  Info,
  GitBranch,
  Layers,
  Settings,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { DomainConfig, Entity, Relationship } from '../../types/template';

interface ConfigurationPreviewProps {
  domainConfig: DomainConfig;
  entities: Entity[];
  relationships: Relationship[];
  onExport?: (format: 'json' | 'yaml' | 'sql' | 'pdf') => void;
  onShare?: () => void;
  onValidate?: () => void;
}

interface ValidationIssue {
  type: 'error' | 'warning' | 'info';
  category: 'entity' | 'relationship' | 'field' | 'domain';
  message: string;
  suggestion?: string;
}

interface PreviewSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  expanded: boolean;
}

const ConfigurationPreview: React.FC<ConfigurationPreviewProps> = ({
  domainConfig,
  entities,
  relationships,
  onExport,
  onShare,
  onValidate
}) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'code' | 'validation'>('summary');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    domain: true,
    entities: true,
    relationships: true,
    statistics: true
  });

  // Validation logic
  const validateConfiguration = (): ValidationIssue[] => {
    const issues: ValidationIssue[] = [];

    // Domain validation
    if (!domainConfig.name.trim()) {
      issues.push({
        type: 'error',
        category: 'domain',
        message: 'Domain name is required',
        suggestion: 'Provide a descriptive name for your domain'
      });
    }

    // Entity validation
    if (entities.length === 0) {
      issues.push({
        type: 'warning',
        category: 'entity',
        message: 'No entities defined',
        suggestion: 'Add at least one entity to create a meaningful template'
      });
    }

    entities.forEach(entity => {
      if (entity.fields.length === 0) {
        issues.push({
          type: 'warning',
          category: 'entity',
          message: `Entity "${entity.name}" has no fields`,
          suggestion: 'Add fields to define the entity structure'
        });
      }

      // Check for primary key - using entity.primaryKey instead of field.isPrimaryKey
      if (!entity.primaryKey) {
        issues.push({
          type: 'info',
          category: 'entity',
          message: `Entity "${entity.name}" has no primary key defined`,
          suggestion: 'Consider setting a primary key field for better data integrity'
        });
      }
    });

    // Relationship validation
    relationships.forEach(rel => {
      const sourceEntity = entities.find(e => e.id === rel.sourceEntityId);
      const targetEntity = entities.find(e => e.id === rel.targetEntityId);

      if (!sourceEntity || !targetEntity) {
        issues.push({
          type: 'error',
          category: 'relationship',
          message: `Invalid relationship: missing entity reference`,
          suggestion: 'Remove invalid relationships or add missing entities'
        });
      }
    });

    return issues;
  };

  const validationIssues = validateConfiguration();
  const errorCount = validationIssues.filter(i => i.type === 'error').length;
  const warningCount = validationIssues.filter(i => i.type === 'warning').length;

  // Statistics
  const statistics = {
    totalEntities: entities.length,
    totalFields: entities.reduce((sum, entity) => sum + entity.fields.length, 0),
    totalRelationships: relationships.length,
    primaryKeys: entities.filter(entity => entity.primaryKey).length,
    requiredFields: entities.reduce((sum, entity) => 
      sum + entity.fields.filter(field => field.required).length, 0),
    uniqueFields: entities.reduce((sum, entity) => 
      sum + entity.fields.filter(field => field.unique).length, 0)
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  const renderSectionHeader = (section: PreviewSection) => (
    <button
      onClick={() => toggleSection(section.id)}
      className="flex items-center justify-between w-full p-4 bg-gray-50 hover:bg-gray-100 
                 rounded-lg transition-colors group"
    >
      <div className="flex items-center space-x-3">
        {section.icon}
        <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
      </div>
      {expandedSections[section.id] ? (
        <ChevronDown className="h-5 w-5 text-gray-500 group-hover:text-gray-700" />
      ) : (
        <ChevronRight className="h-5 w-5 text-gray-500 group-hover:text-gray-700" />
      )}
    </button>
  );

  const renderDomainSection = () => (
    <div className="space-y-4">
      {renderSectionHeader({
        id: 'domain',
        title: 'Domain Configuration',
        icon: <Settings className="h-5 w-5 text-blue-600" />,
        expanded: expandedSections.domain
      })}
      
      {expandedSections.domain && (
        <div className="bg-white rounded-lg border p-6 space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Basic Information</h4>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-500">Name:</span>
                  <p className="font-medium text-gray-900">{domainConfig.name}</p>
                </div>
                {domainConfig.description && (
                  <div>
                    <span className="text-sm text-gray-500">Description:</span>
                    <p className="text-gray-700">{domainConfig.description}</p>
                  </div>
                )}
                <div>
                  <span className="text-sm text-gray-500">Category:</span>
                  <p className="text-gray-700">{domainConfig.domain_type}</p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Configuration</h4>
              <div className="space-y-3">
                {domainConfig.version && (
                  <div>
                    <span className="text-sm text-gray-500">Version:</span>
                    <p className="text-gray-700">{domainConfig.version}</p>
                  </div>
                )}
                {domainConfig.metadata?.tags && Array.isArray(domainConfig.metadata.tags) && domainConfig.metadata.tags.length > 0 && (
                  <div>
                    <span className="text-sm text-gray-500">Tags:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {domainConfig.metadata.tags.map((tag: string) => (
                        <span key={tag} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div>
                  <span className="text-sm text-gray-500">Theme:</span>
                  <p className="text-gray-700 capitalize">{domainConfig.theme || 'default'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderEntitiesSection = () => (
    <div className="space-y-4">
      {renderSectionHeader({
        id: 'entities',
        title: `Entities (${entities.length})`,
        icon: <Layers className="h-5 w-5 text-green-600" />,
        expanded: expandedSections.entities
      })}
      
      {expandedSections.entities && (
        <div className="space-y-4">
          {entities.map(entity => (
            <div key={entity.id} className="bg-white rounded-lg border p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">{entity.name}</h4>
                  {entity.description && (
                    <p className="text-gray-600 mt-1">{entity.description}</p>
                  )}
                </div>
                <div className="text-right text-sm text-gray-500">
                  <div>{entity.fields.length} fields</div>
                  <div className="text-xs">
                    {entity.primaryKey ? '1 PK' : '0 PK'}, {' '}
                    {entity.fields.filter(f => f.required).length} required
                  </div>
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 font-medium text-gray-900">Field</th>
                      <th className="text-left py-2 font-medium text-gray-900">Type</th>
                      <th className="text-left py-2 font-medium text-gray-900">Constraints</th>
                      <th className="text-left py-2 font-medium text-gray-900">Default</th>
                    </tr>
                  </thead>
                  <tbody>
                    {entity.fields.map(field => (
                      <tr key={field.id} className="border-b border-gray-100">
                        <td className="py-2">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-gray-900">{field.name}</span>
                            {field.name === entity.primaryKey && (
                              <span className="px-1 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded">
                                PK
                              </span>
                            )}
                          </div>
                          {field.uiConfig?.help_text && (
                            <p className="text-xs text-gray-500 mt-1">{field.uiConfig.help_text}</p>
                          )}
                        </td>
                        <td className="py-2 text-gray-700">{field.type}</td>
                        <td className="py-2">
                          <div className="flex flex-wrap gap-1">
                            {field.required && (
                              <span className="px-1 py-0.5 text-xs bg-red-100 text-red-800 rounded">
                                Required
                              </span>
                            )}
                            {field.unique && (
                              <span className="px-1 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">
                                Unique
                              </span>
                            )}
                            {field.validation?.max_length && (
                              <span className="px-1 py-0.5 text-xs bg-gray-100 text-gray-700 rounded">
                                Max: {field.validation.max_length}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-2 text-gray-600">
                          {field.defaultValue || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
          
          {entities.length === 0 && (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No entities defined yet</p>
              <p className="text-sm text-gray-500 mt-1">
                Go back to Step 2 to add entities to your template
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderRelationshipsSection = () => (
    <div className="space-y-4">
      {renderSectionHeader({
        id: 'relationships',
        title: `Relationships (${relationships.length})`,
        icon: <GitBranch className="h-5 w-5 text-purple-600" />,
        expanded: expandedSections.relationships
      })}
      
      {expandedSections.relationships && (
        <div className="space-y-4">
          {relationships.map(relationship => {
            const sourceEntity = entities.find(e => e.id === relationship.sourceEntityId);
            const targetEntity = entities.find(e => e.id === relationship.targetEntityId);
            
            return (
              <div key={relationship.id} className="bg-white rounded-lg border p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <p className="font-semibold text-gray-900">{sourceEntity?.name}</p>
                      <p className="text-sm text-gray-500">{relationship.foreignKey || 'id'}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="h-px bg-gray-300 w-8"></div>
                      <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                        {relationship.type.replace(/_/g, '-')}
                      </span>
                      <div className="h-px bg-gray-300 w-8"></div>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-gray-900">{targetEntity?.name}</p>
                      <p className="text-sm text-gray-500">{relationship.backPopulates || 'related'}</p>
                    </div>
                  </div>
                </div>
                
                {relationship.description && (
                  <p className="text-gray-600 text-sm">{relationship.description}</p>
                )}
              </div>
            );
          })}
          
          {relationships.length === 0 && (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <GitBranch className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No relationships defined yet</p>
              <p className="text-sm text-gray-500 mt-1">
                Go back to Step 3 to add relationships between entities
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderStatisticsSection = () => (
    <div className="space-y-4">
      {renderSectionHeader({
        id: 'statistics',
        title: 'Template Statistics',
        icon: <Info className="h-5 w-5 text-indigo-600" />,
        expanded: expandedSections.statistics
      })}
      
      {expandedSections.statistics && (
        <div className="bg-white rounded-lg border p-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{statistics.totalEntities}</div>
              <div className="text-sm text-gray-500">Entities</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{statistics.totalFields}</div>
              <div className="text-sm text-gray-500">Fields</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{statistics.totalRelationships}</div>
              <div className="text-sm text-gray-500">Relationships</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{statistics.primaryKeys}</div>
              <div className="text-sm text-gray-500">Primary Keys</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{statistics.requiredFields}</div>
              <div className="text-sm text-gray-500">Required</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">{statistics.uniqueFields}</div>
              <div className="text-sm text-gray-500">Unique</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderValidationTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Validation Report</h3>
          <p className="text-gray-600 mt-1">Review issues and recommendations for your template</p>
        </div>
        <button
          onClick={onValidate}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                     transition-colors flex items-center space-x-2"
        >
          <CheckCircle className="h-4 w-4" />
          <span>Re-validate</span>
        </button>
      </div>

      {validationIssues.length === 0 ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-green-900 mb-2">Template is Valid!</h3>
          <p className="text-green-700">
            Your template configuration looks great. No issues found.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 bg-red-500 rounded-full"></div>
              <span>{errorCount} Errors</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 bg-yellow-500 rounded-full"></div>
              <span>{warningCount} Warnings</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 bg-blue-500 rounded-full"></div>
              <span>{validationIssues.length - errorCount - warningCount} Info</span>
            </div>
          </div>

          {validationIssues.map((issue, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 ${
                issue.type === 'error'
                  ? 'bg-red-50 border-red-200'
                  : issue.type === 'warning'
                  ? 'bg-yellow-50 border-yellow-200'
                  : 'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex items-start space-x-3">
                {issue.type === 'error' ? (
                  <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                ) : issue.type === 'warning' ? (
                  <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                ) : (
                  <Info className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h4 className={`font-medium ${
                      issue.type === 'error'
                        ? 'text-red-900'
                        : issue.type === 'warning'
                        ? 'text-yellow-900'
                        : 'text-blue-900'
                    }`}>
                      {issue.message}
                    </h4>
                    <span className={`px-2 py-1 text-xs rounded ${
                      issue.type === 'error'
                        ? 'bg-red-100 text-red-800'
                        : issue.type === 'warning'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {issue.category}
                    </span>
                  </div>
                  {issue.suggestion && (
                    <p className={`mt-1 text-sm ${
                      issue.type === 'error'
                        ? 'text-red-700'
                        : issue.type === 'warning'
                        ? 'text-yellow-700'
                        : 'text-blue-700'
                    }`}>
                      💡 {issue.suggestion}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderCodeTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Generated Code Preview</h3>
          <p className="text-gray-600 mt-1">Preview the generated code for your template</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onExport?.('json')}
            className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Export JSON
          </button>
          <button
            onClick={() => onExport?.('sql')}
            className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Export SQL
          </button>
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
        <pre className="text-green-400 text-sm">
          <code>{`// Generated Template Configuration
{
  "domain": {
    "name": "${domainConfig.name}",
    "title": "${domainConfig.title}",
    "description": "${domainConfig.description || ''}",
    "domain_type": "${domainConfig.domain_type}",
    "version": "${domainConfig.version || '1.0.0'}",
    "theme": "${domainConfig.theme || 'default'}"
  },
  "entities": [
${entities.map(entity => `    {
      "name": "${entity.name}",
      "description": "${entity.description || ''}",
      "primaryKey": "${entity.primaryKey || 'id'}",
      "fields": [
${entity.fields.map(field => `        {
          "name": "${field.name}",
          "title": "${field.title}",
          "type": "${field.type}",
          "required": ${field.required || false},
          "unique": ${field.unique || false},
          "defaultValue": "${field.defaultValue || ''}"
        }`).join(',\n')}
      ]
    }`).join(',\n')}
  ],
  "relationships": [
${relationships.map(rel => `    {
      "name": "${rel.name}",
      "type": "${rel.type}",
      "sourceEntity": "${entities.find(e => e.id === rel.sourceEntityId)?.name}",
      "targetEntity": "${entities.find(e => e.id === rel.targetEntityId)?.name}",
      "foreignKey": "${rel.foreignKey || 'id'}",
      "backPopulates": "${rel.backPopulates || 'related'}"
    }`).join(',\n')}
  ]
}`}</code>
        </pre>
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Configuration Preview</h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Review your template configuration before finalizing. Validate the structure, 
          export the configuration, or share it with your team.
        </p>
      </div>

      {/* Action Bar */}
      <div className="flex flex-wrap justify-center gap-4 p-6 bg-gray-50 rounded-lg">
        <button
          onClick={() => onExport?.('json')}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 
                     hover:bg-gray-50 rounded-lg transition-colors"
        >
          <Download className="h-4 w-4" />
          <span>Export JSON</span>
        </button>
        <button
          onClick={() => onExport?.('sql')}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 
                     hover:bg-gray-50 rounded-lg transition-colors"
        >
          <Database className="h-4 w-4" />
          <span>Export SQL</span>
        </button>
        <button
          onClick={() => onExport?.('pdf')}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 
                     hover:bg-gray-50 rounded-lg transition-colors"
        >
          <FileText className="h-4 w-4" />
          <span>Export PDF</span>
        </button>
        <button
          onClick={onShare}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white 
                     hover:bg-blue-700 rounded-lg transition-colors"
        >
          <Share2 className="h-4 w-4" />
          <span>Share Template</span>
        </button>
      </div>

      {/* Status Indicator */}
      {errorCount > 0 ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          <div>
            <p className="font-medium text-red-900">Template has validation errors</p>
            <p className="text-red-700 text-sm">
              Please fix {errorCount} error{errorCount > 1 ? 's' : ''} before proceeding
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <CheckCircle className="h-5 w-5 text-green-500" />
          <div>
            <p className="font-medium text-green-900">Template is ready</p>
            <p className="text-green-700 text-sm">
              Configuration looks good! Ready to proceed to the next step.
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('summary')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'summary'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Eye className="h-4 w-4" />
              <span>Summary</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('validation')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'validation'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4" />
              <span>Validation</span>
              {(errorCount > 0 || warningCount > 0) && (
                <span className="ml-2 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                  {errorCount + warningCount}
                </span>
              )}
            </div>
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'code'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Code className="h-4 w-4" />
              <span>Code Preview</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'summary' && (
          <div className="space-y-8">
            {renderDomainSection()}
            {renderEntitiesSection()}
            {renderRelationshipsSection()}
            {renderStatisticsSection()}
          </div>
        )}
        {activeTab === 'validation' && renderValidationTab()}
        {activeTab === 'code' && renderCodeTab()}
      </div>
    </div>
  );
};

export default ConfigurationPreview;