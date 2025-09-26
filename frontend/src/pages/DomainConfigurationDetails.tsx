/**
 * Domain Configuration Details - Day 9 Implementation
 * Detailed view of domain configuration with entities, fields, and relationships
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Database,
  Settings,
  Eye,
  Code,
  Link,
  FileText,
  CheckCircle,
  AlertCircle,
  Package,
  Layers,
  Zap,
  Hash,
  Calendar,
  Globe
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingComponents';

// Interfaces for domain configuration
interface DomainField {
  name: string;
  type: string;
  nullable: boolean;
  description: string;
  max_length?: number;
  choices?: string[] | null;
}

interface DomainRelationship {
  name: string;
  target_entity: string;
  relationship_type: string;
  foreign_key?: string;
}

interface DomainEntity {
  name: string;
  table_name: string;
  description: string;
  fields: DomainField[];
  relationships: DomainRelationship[];
  field_count: number;
  relationship_count: number;
  business_rules_count: number;
}

interface DomainInfo {
  name: string;
  title: string;
  description: string;
  type: string;
  version: string;
  logo: string;
  color_scheme: string;
}

interface DomainConfiguration {
  domain: DomainInfo;
  entities: Record<string, DomainEntity>;
  navigation: any[];
  dashboard: any[];
  features: Record<string, any>;
  metadata: {
    total_entities: number;
    total_fields: number;
    total_relationships: number;
    total_business_rules: number;
    enabled_features: number;
  };
}

const DomainConfigurationDetails: React.FC = () => {
  const { domainId } = useParams<{ domainId: string }>();
  const navigate = useNavigate();
  const [config, setConfig] = useState<DomainConfiguration | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'entities' | 'features'>('overview');

  useEffect(() => {
    if (!domainId) return;
    
    const loadDomainConfig = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/api/v1/template/domains/${domainId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to load domain configuration: ${response.statusText}`);
        }
        
        const data = await response.json();
        setConfig(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load domain configuration');
      } finally {
        setLoading(false);
      }
    };
    
    loadDomainConfig();
  }, [domainId]);

  const getFieldTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'string': case 'text': return <FileText className="h-4 w-4" />;
      case 'integer': case 'decimal': return <Hash className="h-4 w-4" />;
      case 'date': case 'datetime': return <Calendar className="h-4 w-4" />;
      case 'enum': return <Settings className="h-4 w-4" />;
      case 'boolean': return <CheckCircle className="h-4 w-4" />;
      default: return <Database className="h-4 w-4" />;
    }
  };

  const getRelationshipIcon = (type: string) => {
    switch (type) {
      case 'one_to_one': return '1:1';
      case 'one_to_many': return '1:N';
      case 'many_to_one': return 'N:1';
      case 'many_to_many': return 'N:N';
      default: return '?';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !config) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Configuration Not Found</h3>
          <p className="text-gray-600 mb-4">{error || 'Domain configuration could not be loaded'}</p>
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
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => navigate('/templates')}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div className="text-4xl">{config.domain.logo}</div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{config.domain.title}</h1>
              <p className="text-gray-600">{config.domain.description}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6 text-sm text-gray-500">
            <span className="flex items-center">
              <Globe className="h-4 w-4 mr-1" />
              Domain: {config.domain.name}
            </span>
            <span className="flex items-center">
              <Package className="h-4 w-4 mr-1" />
              Version: {config.domain.version}
            </span>
            <span className="flex items-center">
              <Zap className="h-4 w-4 mr-1" />
              Type: {config.domain.type}
            </span>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{config.metadata.total_entities}</div>
              <div className="text-sm text-blue-800">Entities</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{config.metadata.total_fields}</div>
              <div className="text-sm text-green-800">Fields</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{config.metadata.total_relationships}</div>
              <div className="text-sm text-purple-800">Relationships</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">{config.metadata.enabled_features}</div>
              <div className="text-sm text-yellow-800">Features</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: Eye },
              { id: 'entities', label: 'Entities', icon: Database },
              { id: 'features', label: 'Features', icon: Settings }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Domain Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Domain Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <p className="mt-1 text-sm text-gray-900">{config.domain.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Title</label>
                  <p className="mt-1 text-sm text-gray-900">{config.domain.title}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Type</label>
                  <p className="mt-1 text-sm text-gray-900 capitalize">{config.domain.type}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Version</label>
                  <p className="mt-1 text-sm text-gray-900">{config.domain.version}</p>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <p className="mt-1 text-sm text-gray-900">{config.domain.description}</p>
                </div>
              </div>
            </div>

            {/* Entity Overview */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Entity Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.values(config.entities).map((entity) => (
                  <div key={entity.name} className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">{entity.name}</h4>
                    <p className="text-sm text-gray-600 mb-3">{entity.description}</p>
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>{entity.field_count} fields</span>
                      <span>{entity.relationship_count} relations</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'entities' && (
          <div className="space-y-6">
            {Object.values(config.entities).map((entity) => (
              <div key={entity.name} className="bg-white rounded-lg shadow-sm border border-gray-200">
                {/* Entity Header */}
                <div className="border-b border-gray-200 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{entity.name}</h3>
                      <p className="text-sm text-gray-600">{entity.description}</p>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center">
                        <Code className="h-4 w-4 mr-1" />
                        {entity.table_name}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-6">
                  {/* Fields */}
                  <div className="mb-6">
                    <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                      <Layers className="h-4 w-4 mr-2" />
                      Fields ({entity.field_count})
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Required</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {entity.fields.map((field) => (
                            <tr key={field.name} className="hover:bg-gray-50">
                              <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                                <div className="flex items-center">
                                  {getFieldTypeIcon(field.type)}
                                  <span className="ml-2">{field.name}</span>
                                </div>
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                                <span className="inline-flex px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                                  {field.type}
                                </span>
                                {field.choices && field.choices.length > 0 && (
                                  <div className="text-xs text-gray-400 mt-1">
                                    Options: {field.choices.join(', ')}
                                  </div>
                                )}
                              </td>
                              <td className="px-3 py-2 whitespace-nowrap text-sm">
                                {!field.nullable ? (
                                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                    Required
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                    Optional
                                  </span>
                                )}
                              </td>
                              <td className="px-3 py-2 text-sm text-gray-600">
                                {field.description || '-'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Relationships */}
                  {entity.relationships.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                        <Link className="h-4 w-4 mr-2" />
                        Relationships ({entity.relationship_count})
                      </h4>
                      <div className="space-y-2">
                        {entity.relationships.map((rel, idx) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center space-x-3">
                              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                {getRelationshipIcon(rel.relationship_type)}
                              </span>
                              <span className="font-medium text-gray-900">{rel.name}</span>
                              <span className="text-gray-500">→</span>
                              <span className="text-gray-700">{rel.target_entity}</span>
                            </div>
                            {rel.foreign_key && (
                              <span className="text-xs text-gray-500">FK: {rel.foreign_key}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'features' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Domain Features</h3>
            {Object.keys(config.features).length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Settings className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No features configured for this domain</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(config.features).map(([name, enabled]) => (
                  <div key={name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <span className="font-medium text-gray-900 capitalize">{name.replace('_', ' ')}</span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      enabled 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Day 9 Completion Footer */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-t border-green-200 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-start space-x-3">
            <CheckCircle className="h-6 w-6 text-green-600 mt-1" />
            <div>
              <h4 className="text-lg font-semibold text-green-900">
                ✅ Day 9: Domain Configuration UI Complete
              </h4>
              <p className="text-green-700">
                Successfully displaying detailed domain configuration for <strong>{config.domain.name}</strong> 
                with {config.metadata.total_entities} entities, {config.metadata.total_fields} fields, 
                and {config.metadata.total_relationships} relationships.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DomainConfigurationDetails;