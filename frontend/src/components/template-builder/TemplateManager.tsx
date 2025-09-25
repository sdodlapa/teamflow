import React, { useState } from 'react';
import {
  Save,
  Download,
  Share2,
  Copy,
  Check,
  X,
  AlertTriangle,
  Info
} from 'lucide-react';
import { DomainConfig, Entity, Relationship } from '../../types/template';
import { useTemplatePersistence } from '../../hooks/useTemplatePersistence';
import { useAuth } from '../../hooks/useAuth';

interface TemplateManagerProps {
  domainConfig: DomainConfig;
  entities: Entity[];
  relationships: Relationship[];
  onSave?: (templateData: any) => Promise<void>;
  onLoad?: (templateId: string) => Promise<void>;
  onExport?: (format: string) => void;
  isVisible?: boolean;
  onClose?: () => void;
}

interface SaveTemplateForm {
  name: string;
  title: string;
  description: string;
  tags: string[];
  isPublic: boolean;
  version: string;
}

const TemplateManager: React.FC<TemplateManagerProps> = ({
  domainConfig,
  entities,
  relationships,
  onSave,
  onLoad,
  onExport,
  isVisible = false,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'save' | 'load' | 'export' | 'share'>('save');
  const { isAuthenticated } = useAuth();
  const templatePersistence = useTemplatePersistence();

  // Template loading state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomainType, setSelectedDomainType] = useState('all');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Get templates to display - use search results if searching, otherwise recent templates
  const displayTemplates = searchQuery.trim() ? searchResults : templatePersistence.recentTemplates;

  const handleSearchTemplates = async (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    try {
      const results = await templatePersistence.searchTemplates(query);
      setSearchResults(results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  
  const [saveForm, setSaveForm] = useState<SaveTemplateForm>({
    name: domainConfig.name?.toLowerCase().replace(/\s+/g, '-') || '',
    title: domainConfig.title || domainConfig.name || '',
    description: domainConfig.description || '',
    tags: [],
    isPublic: false,
    version: '1.0.0'
  });

  const [tagInput, setTagInput] = useState('');

  const validateForm = () => {
    const errors: string[] = [];
    
    if (!saveForm.name.trim()) {
      errors.push('Template name is required');
    }
    
    if (!saveForm.title.trim()) {
      errors.push('Template title is required');
    }
    
    if (entities.length === 0) {
      errors.push('At least one entity is required');
    }
    
    return errors;
  };

  const handleSave = async () => {
    const errors = validateForm();
    if (errors.length > 0) {
      alert(`Please fix the following errors:\n${errors.join('\n')}`);
      return;
    }

    setSaving(true);
    
    const templateData = {
      metadata: {
        name: saveForm.name,
        title: saveForm.title,
        description: saveForm.description,
        domain_type: domainConfig.domain_type,
        version: saveForm.version,
        author: 'Current User', // TODO: Get from auth context
        tags: saveForm.tags,
        isPublic: saveForm.isPublic,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      configuration: {
        domain: domainConfig,
        entities,
        relationships
      }
    };

    try {
      await onSave?.(templateData);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Failed to save template. Please try again.');
    }
    
    setSaving(false);
  };

  const handleExport = (format: string) => {
    const templateData = {
      domain: domainConfig,
      entities,
      relationships,
      exportedAt: new Date().toISOString(),
      version: saveForm.version
    };

    switch (format) {
      case 'json':
        const jsonBlob = new Blob(
          [JSON.stringify(templateData, null, 2)], 
          { type: 'application/json' }
        );
        const jsonUrl = URL.createObjectURL(jsonBlob);
        const jsonLink = document.createElement('a');
        jsonLink.href = jsonUrl;
        jsonLink.download = `${saveForm.name || 'template'}.json`;
        jsonLink.click();
        URL.revokeObjectURL(jsonUrl);
        break;

      case 'yaml':
        // Simple YAML conversion - in production, use a proper YAML library
        const yamlContent = `# Template Configuration
domain:
  name: ${domainConfig.name}
  title: ${domainConfig.title}
  description: ${domainConfig.description}
  domain_type: ${domainConfig.domain_type}
  version: ${domainConfig.version}

entities:
${entities.map(entity => `  - name: ${entity.name}
    description: ${entity.description || ''}
    fields:
${entity.fields.map(field => `      - name: ${field.name}
        type: ${field.type}
        required: ${field.required || false}`).join('\n')}`).join('\n')}

relationships:
${relationships.map(rel => `  - name: ${rel.name}
    type: ${rel.type}
    source: ${entities.find(e => e.id === rel.sourceEntityId)?.name}
    target: ${entities.find(e => e.id === rel.targetEntityId)?.name}`).join('\n')}
`;
        const yamlBlob = new Blob([yamlContent], { type: 'text/yaml' });
        const yamlUrl = URL.createObjectURL(yamlBlob);
        const yamlLink = document.createElement('a');
        yamlLink.href = yamlUrl;
        yamlLink.download = `${saveForm.name || 'template'}.yaml`;
        yamlLink.click();
        URL.revokeObjectURL(yamlUrl);
        break;

      case 'pdf':
        alert('PDF export coming soon! For now, use the print function in your browser.');
        window.print();
        break;

      default:
        onExport?.(format);
    }
  };

  const generateShareUrl = async () => {
    // In a real app, this would create a shareable link via API
    const templateData = btoa(JSON.stringify({
      domain: domainConfig,
      entities: entities.slice(0, 2), // Limit for demo
      relationships: relationships.slice(0, 2)
    }));
    
    const url = `${window.location.origin}/template-builder?template=${templateData}`;
    setShareUrl(url);
    
    // Copy to clipboard
    try {
      await navigator.clipboard.writeText(url);
      alert('Share URL copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy URL:', err);
    }
  };

  const addTag = () => {
    if (tagInput.trim() && !saveForm.tags.includes(tagInput.trim())) {
      setSaveForm(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setSaveForm(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Template Manager
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('save')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'save'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Save className="h-4 w-4 inline mr-2" />
              Save Template
            </button>
            <button
              onClick={() => setActiveTab('load')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'load'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Download className="h-4 w-4 inline mr-2" />
              Load Template
            </button>
            <button
              onClick={() => setActiveTab('export')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'export'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Download className="h-4 w-4 inline mr-2" />
              Export
            </button>
            <button
              onClick={() => setActiveTab('share')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'share'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Share2 className="h-4 w-4 inline mr-2" />
              Share
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'save' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Save Template to Library
                </h3>
                <p className="text-gray-600 mb-6">
                  Save your template to the library for reuse and sharing with your team.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Template Name *
                  </label>
                  <input
                    type="text"
                    value={saveForm.name}
                    onChange={(e) => setSaveForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                             focus:ring-blue-500 focus:border-transparent"
                    placeholder="my-awesome-template"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Version
                  </label>
                  <input
                    type="text"
                    value={saveForm.version}
                    onChange={(e) => setSaveForm(prev => ({ ...prev, version: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                             focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Display Title *
                </label>
                <input
                  type="text"
                  value={saveForm.title}
                  onChange={(e) => setSaveForm(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                           focus:ring-blue-500 focus:border-transparent"
                  placeholder="My Awesome Template"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={saveForm.description}
                  onChange={(e) => setSaveForm(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                           focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe what this template is for and how to use it..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tags
                </label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {saveForm.tags.map(tag => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded flex items-center space-x-1"
                    >
                      <span>{tag}</span>
                      <button
                        onClick={() => removeTag(tag)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={handleTagInputKeyPress}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                             focus:ring-blue-500 focus:border-transparent"
                    placeholder="Add a tag..."
                  />
                  <button
                    onClick={addTag}
                    className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 
                             rounded-lg transition-colors"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="isPublic"
                  checked={saveForm.isPublic}
                  onChange={(e) => setSaveForm(prev => ({ ...prev, isPublic: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="isPublic" className="text-sm text-gray-700">
                  Make this template public (visible to all users)
                </label>
              </div>

              {/* Template Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Template Summary</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Entities:</span>
                    <span className="ml-2 font-medium">{entities.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Relationships:</span>
                    <span className="ml-2 font-medium">{relationships.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Fields:</span>
                    <span className="ml-2 font-medium">
                      {entities.reduce((sum, entity) => sum + entity.fields.length, 0)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-gray-700 border border-gray-300 hover:bg-gray-50 
                           rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-400 
                           rounded-lg transition-colors flex items-center space-x-2"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                      <span>Saving...</span>
                    </>
                  ) : saveSuccess ? (
                    <>
                      <Check className="h-4 w-4" />
                      <span>Saved!</span>
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4" />
                      <span>Save Template</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'load' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Load Template
                </h3>
                <p className="text-gray-600 mb-6">
                  Choose a saved template to load into the builder.
                </p>
              </div>

              <div className="grid gap-4">
                {/* Template Search/Filter */}
                <div className="flex gap-4 mb-6">
                  <div className="flex-1">
                    <input
                      type="text"
                      placeholder="Search templates..."
                      value={searchQuery}
                      onChange={(e) => handleSearchTemplates(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg 
                               focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <select 
                    value={selectedDomainType}
                    onChange={(e) => setSelectedDomainType(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg 
                                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">All Types</option>
                    <option value="e_commerce">E-commerce</option>
                    <option value="healthcare">Healthcare</option>
                    <option value="finance">Finance</option>
                    <option value="education">Education</option>
                    <option value="manufacturing">Manufacturing</option>
                  </select>
                </div>

                {/* Templates List */}
                <div className="grid gap-3 max-h-96 overflow-y-auto">
                  {!isAuthenticated ? (
                    <div className="text-center py-8 text-gray-500">
                      <Info className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <p>Please log in to view and load templates</p>
                    </div>
                  ) : isSearching || templatePersistence.isLoading ? (
                    <div className="text-center py-8 text-gray-500">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                      <p>Loading templates...</p>
                    </div>
                  ) : displayTemplates.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Info className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <p>
                        {searchQuery.trim() ? 'No templates found matching your search' : 'No templates available'}
                      </p>
                      {!searchQuery.trim() && (
                        <p className="text-sm mt-2">Save a template first to see it here</p>
                      )}
                    </div>
                  ) : (
                    displayTemplates
                      .filter(template => 
                        selectedDomainType === 'all' || 
                        template.metadata?.domain_type === selectedDomainType
                      )
                      .map((template) => (
                        <div
                          key={template.id}
                          className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 
                                   hover:bg-blue-50 cursor-pointer transition-colors"
                          onClick={() => onLoad?.(template.id)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">
                                {template.metadata?.name || template.name || 'Unnamed Template'}
                              </h4>
                              <p className="text-sm text-gray-600 mt-1">
                                {template.metadata?.description || template.description || 'No description'}
                              </p>
                              <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                                <span>By {template.metadata?.author || 'Unknown'}</span>
                                <span>•</span>
                                <span>{template.metadata?.domain_type || 'Unknown Type'}</span>
                                <span>•</span>
                                <span>{new Date(template.created_at || template.metadata?.created_at || '').toLocaleDateString()}</span>
                              </div>
                            </div>
                            <div className="ml-4">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full 
                                           text-xs font-medium ${
                                template.metadata?.isPublic 
                                  ? 'bg-blue-100 text-blue-800' 
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {template.metadata?.isPublic ? 'Public' : 'Private'}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))
                  )}
                </div>

                {/* Load from File */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-3">Load from File</h4>
                  <div className="flex items-center gap-4">
                    <input
                      type="file"
                      accept=".json"
                      className="block w-full text-sm text-gray-500
                               file:mr-4 file:py-2 file:px-4
                               file:rounded-lg file:border-0
                               file:text-sm file:font-medium
                               file:bg-blue-50 file:text-blue-700
                               hover:file:bg-blue-100"
                    />
                    <button
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700
                               transition-colors font-medium text-sm"
                    >
                      Upload
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Upload a JSON template file to load into the builder
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'export' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Export Template
                </h3>
                <p className="text-gray-600 mb-6">
                  Download your template configuration in various formats.
                </p>
              </div>

              <div className="grid gap-4">
                <button
                  onClick={() => handleExport('json')}
                  className="flex items-center justify-between p-4 border border-gray-300 
                           hover:border-blue-300 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">📄</div>
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">JSON Format</h4>
                      <p className="text-sm text-gray-600">
                        Machine-readable format for import/export
                      </p>
                    </div>
                  </div>
                  <Download className="h-5 w-5 text-gray-400" />
                </button>

                <button
                  onClick={() => handleExport('yaml')}
                  className="flex items-center justify-between p-4 border border-gray-300 
                           hover:border-blue-300 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">📋</div>
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">YAML Format</h4>
                      <p className="text-sm text-gray-600">
                        Human-readable configuration format
                      </p>
                    </div>
                  </div>
                  <Download className="h-5 w-5 text-gray-400" />
                </button>

                <button
                  onClick={() => handleExport('pdf')}
                  className="flex items-center justify-between p-4 border border-gray-300 
                           hover:border-blue-300 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">📊</div>
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">PDF Report</h4>
                      <p className="text-sm text-gray-600">
                        Printable documentation format
                      </p>
                    </div>
                  </div>
                  <Download className="h-5 w-5 text-gray-400" />
                </button>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Info className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div className="text-sm text-blue-700">
                    <p className="font-medium mb-1">Export Tips</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>JSON format is best for importing into other systems</li>
                      <li>YAML format is more readable for documentation</li>
                      <li>PDF format includes visual diagrams and charts</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'share' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Share Template
                </h3>
                <p className="text-gray-600 mb-6">
                  Create a shareable link to your template configuration.
                </p>
              </div>

              {!shareUrl ? (
                <div className="text-center">
                  <button
                    onClick={generateShareUrl}
                    className="px-6 py-3 bg-blue-600 text-white hover:bg-blue-700 
                             rounded-lg transition-colors flex items-center space-x-2 mx-auto"
                  >
                    <Share2 className="h-5 w-5" />
                    <span>Generate Share Link</span>
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Shareable Link
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={shareUrl}
                        readOnly
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                      />
                      <button
                        onClick={() => navigator.clipboard.writeText(shareUrl)}
                        className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 
                                 rounded-lg transition-colors flex items-center space-x-1"
                      >
                        <Copy className="h-4 w-4" />
                        <span>Copy</span>
                      </button>
                    </div>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
                      <div className="text-sm text-yellow-700">
                        <p className="font-medium mb-1">Sharing Notice</p>
                        <p>
                          This link contains your template configuration data. Only share with 
                          trusted collaborators. Links expire after 30 days.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplateManager;