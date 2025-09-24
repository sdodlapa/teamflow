import React, { useState, useEffect } from 'react';
import {
  Search,
  Grid,
  List,
  Star,
  Download,
  Share2,
  Edit,
  Trash2,
  Plus,
  Eye,
  Clock,
  User,
  Bookmark,
  BookmarkCheck,
  Copy,
  ExternalLink,
  MoreVertical
} from 'lucide-react';
import { TemplateMetadata, DomainType } from '../../types/template';

interface TemplateLibraryProps {
  onSelectTemplate?: (template: TemplateMetadata) => void;
  onCreateNew?: () => void;
  onImportTemplate?: (template: any) => void;
  currentUserId?: string;
}

interface FilterOptions {
  search: string;
  domainType: DomainType | 'all';
  sortBy: 'name' | 'created_at' | 'updated_at' | 'downloads' | 'rating';
  sortOrder: 'asc' | 'desc';
  showFavorites: boolean;
  showMyTemplates: boolean;
}

const TemplateLibrary: React.FC<TemplateLibraryProps> = ({
  onSelectTemplate,
  onCreateNew,
  onImportTemplate,
  currentUserId = 'demo-user'
}) => {
  const [templates, setTemplates] = useState<TemplateMetadata[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<TemplateMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateMetadata | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [filters, setFilters] = useState<FilterOptions>({
    search: '',
    domainType: 'all',
    sortBy: 'updated_at',
    sortOrder: 'desc',
    showFavorites: false,
    showMyTemplates: false
  });

  // Mock data - in real app, this would come from API
  const mockTemplates: TemplateMetadata[] = [
    {
      id: '1',
      name: 'task-management-starter',
      title: 'Task Management Starter',
      domain_type: 'task_management',
      version: '1.0.0',
      author: 'TeamFlow Team',
      created_at: '2025-09-20T10:00:00Z',
      updated_at: '2025-09-24T15:30:00Z',
      downloads: 245,
      rating: 4.8,
      tags: ['productivity', 'collaboration', 'agile']
    },
    {
      id: '2',
      name: 'ecommerce-foundation',
      title: 'E-Commerce Foundation',
      domain_type: 'e_commerce',
      version: '2.1.0',
      author: 'Commerce Pro',
      created_at: '2025-09-18T14:20:00Z',
      updated_at: '2025-09-23T09:15:00Z',
      downloads: 189,
      rating: 4.6,
      tags: ['ecommerce', 'payments', 'inventory']
    },
    {
      id: '3',
      name: 'crm-essentials',
      title: 'CRM Essentials',
      domain_type: 'crm',
      version: '1.5.2',
      author: 'CRM Experts',
      created_at: '2025-09-15T11:45:00Z',
      updated_at: '2025-09-22T16:00:00Z',
      downloads: 156,
      rating: 4.7,
      tags: ['sales', 'leads', 'pipeline']
    },
    {
      id: '4',
      name: 'healthcare-records',
      title: 'Healthcare Records System',
      domain_type: 'healthcare',
      version: '1.0.3',
      author: currentUserId,
      created_at: '2025-09-10T08:30:00Z',
      updated_at: '2025-09-21T14:20:00Z',
      downloads: 67,
      rating: 4.9,
      tags: ['healthcare', 'privacy', 'compliance']
    },
    {
      id: '5',
      name: 'real-estate-management',
      title: 'Real Estate Management',
      domain_type: 'real_estate',
      version: '1.2.0',
      author: 'PropTech Solutions',
      created_at: '2025-09-12T16:15:00Z',
      updated_at: '2025-09-20T11:30:00Z',
      downloads: 98,
      rating: 4.4,
      tags: ['properties', 'listings', 'agents']
    },
    {
      id: '6',
      name: 'education-portal',
      title: 'Education Portal',
      domain_type: 'education',
      version: '1.8.0',
      author: 'EduTech Innovations',
      created_at: '2025-09-08T13:00:00Z',
      updated_at: '2025-09-19T10:45:00Z',
      downloads: 234,
      rating: 4.5,
      tags: ['learning', 'courses', 'students']
    }
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setTemplates(mockTemplates);
      setLoading(false);
    }, 500);

    // Load favorites from localStorage
    const savedFavorites = localStorage.getItem('template-favorites');
    if (savedFavorites) {
      setFavorites(new Set(JSON.parse(savedFavorites)));
    }
  }, []);

  useEffect(() => {
    applyFilters();
  }, [templates, filters]);

  const applyFilters = () => {
    let filtered = [...templates];

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(template =>
        template.title.toLowerCase().includes(searchLower) ||
        template.name.toLowerCase().includes(searchLower) ||
        template.tags.some(tag => tag.toLowerCase().includes(searchLower)) ||
        template.author.toLowerCase().includes(searchLower)
      );
    }

    // Domain type filter
    if (filters.domainType !== 'all') {
      filtered = filtered.filter(template => template.domain_type === filters.domainType);
    }

    // Favorites filter
    if (filters.showFavorites) {
      filtered = filtered.filter(template => favorites.has(template.id));
    }

    // My templates filter
    if (filters.showMyTemplates) {
      filtered = filtered.filter(template => template.author === currentUserId);
    }

    // Sort
    filtered.sort((a, b) => {
      const aVal = a[filters.sortBy];
      const bVal = b[filters.sortBy];
      
      let comparison = 0;
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal);
      } else {
        comparison = Number(aVal) - Number(bVal);
      }
      
      return filters.sortOrder === 'desc' ? -comparison : comparison;
    });

    setFilteredTemplates(filtered);
  };

  const toggleFavorite = (templateId: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(templateId)) {
      newFavorites.delete(templateId);
    } else {
      newFavorites.add(templateId);
    }
    setFavorites(newFavorites);
    localStorage.setItem('template-favorites', JSON.stringify([...newFavorites]));
  };

  const handleTemplateAction = (action: string, template: TemplateMetadata) => {
    switch (action) {
      case 'view':
        setSelectedTemplate(template);
        setShowPreview(true);
        break;
      case 'use':
        onSelectTemplate?.(template);
        break;
      case 'download':
        console.log('Downloading template:', template.name);
        // TODO: Implement actual download
        break;
      case 'share':
        navigator.clipboard.writeText(`https://teamflow.com/templates/${template.id}`);
        // TODO: Show success notification
        break;
      case 'duplicate':
        console.log('Duplicating template:', template.name);
        // TODO: Implement template duplication
        break;
      case 'edit':
        console.log('Editing template:', template.name);
        // TODO: Open template editor
        break;
      case 'delete':
        if (confirm('Are you sure you want to delete this template?')) {
          setTemplates(prev => prev.filter(t => t.id !== template.id));
        }
        break;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else if (diffInHours < 24 * 7) {
      return `${Math.floor(diffInHours / 24)} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getDomainTypeIcon = (domainType: DomainType) => {
    const icons = {
      task_management: '📋',
      e_commerce: '🛒',
      crm: '👥',
      healthcare: '🏥',
      real_estate: '🏠',
      education: '🎓',
      finance: '💰',
      custom: '⚙️'
    };
    return icons[domainType] || '📄';
  };

  const renderTemplateCard = (template: TemplateMetadata) => (
    <div
      key={template.id}
      className="bg-white rounded-lg border border-gray-200 hover:border-blue-300 
                 transition-all duration-200 hover:shadow-md group"
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">{getDomainTypeIcon(template.domain_type)}</div>
            <div>
              <h3 className="font-semibold text-gray-900 group-hover:text-blue-600">
                {template.title}
              </h3>
              <p className="text-sm text-gray-500">{template.name}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(template.id);
              }}
              className="p-1 text-gray-400 hover:text-yellow-500 transition-colors"
            >
              {favorites.has(template.id) ? (
                <BookmarkCheck className="h-4 w-4 text-yellow-500" />
              ) : (
                <Bookmark className="h-4 w-4" />
              )}
            </button>
            
            <div className="relative group/menu">
              <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                <MoreVertical className="h-4 w-4" />
              </button>
              
              <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 
                            rounded-lg shadow-lg opacity-0 invisible group-hover/menu:opacity-100 
                            group-hover/menu:visible transition-all z-10">
                <div className="py-1">
                  <button
                    onClick={() => handleTemplateAction('view', template)}
                    className="w-full px-4 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 
                             flex items-center space-x-2"
                  >
                    <Eye className="h-4 w-4" />
                    <span>Preview</span>
                  </button>
                  <button
                    onClick={() => handleTemplateAction('use', template)}
                    className="w-full px-4 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 
                             flex items-center space-x-2"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>Use Template</span>
                  </button>
                  <button
                    onClick={() => handleTemplateAction('duplicate', template)}
                    className="w-full px-4 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 
                             flex items-center space-x-2"
                  >
                    <Copy className="h-4 w-4" />
                    <span>Duplicate</span>
                  </button>
                  <button
                    onClick={() => handleTemplateAction('share', template)}
                    className="w-full px-4 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 
                             flex items-center space-x-2"
                  >
                    <Share2 className="h-4 w-4" />
                    <span>Share</span>
                  </button>
                  {template.author === currentUserId && (
                    <>
                      <div className="border-t border-gray-100 my-1" />
                      <button
                        onClick={() => handleTemplateAction('edit', template)}
                        className="w-full px-4 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 
                                 flex items-center space-x-2"
                      >
                        <Edit className="h-4 w-4" />
                        <span>Edit</span>
                      </button>
                      <button
                        onClick={() => handleTemplateAction('delete', template)}
                        className="w-full px-4 py-2 text-sm text-left text-red-600 hover:bg-red-50 
                                 flex items-center space-x-2"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Delete</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <Star className="h-4 w-4 text-yellow-500" />
              <span>{template.rating}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Download className="h-4 w-4" />
              <span>{template.downloads}</span>
            </div>
          </div>
          <span className="text-xs text-gray-400">v{template.version}</span>
        </div>

        {/* Tags */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {template.tags.slice(0, 3).map(tag => (
              <span
                key={tag}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
              >
                {tag}
              </span>
            ))}
            {template.tags.length > 3 && (
              <span className="px-2 py-1 text-xs text-gray-500">
                +{template.tags.length - 3}
              </span>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <User className="h-4 w-4" />
            <span>{template.author}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="h-4 w-4" />
            <span>{formatDate(template.updated_at)}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-4 flex space-x-2">
          <button
            onClick={() => handleTemplateAction('view', template)}
            className="flex-1 px-3 py-2 text-sm border border-gray-300 text-gray-700 
                     hover:bg-gray-50 rounded transition-colors"
          >
            Preview
          </button>
          <button
            onClick={() => handleTemplateAction('use', template)}
            className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 
                     rounded transition-colors"
          >
            Use Template
          </button>
        </div>
      </div>
    </div>
  );

  const renderTemplateList = (template: TemplateMetadata) => (
    <div
      key={template.id}
      className="bg-white border border-gray-200 hover:border-blue-300 rounded-lg p-4 
                 transition-all duration-200 hover:shadow-sm"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="text-2xl">{getDomainTypeIcon(template.domain_type)}</div>
          
          <div>
            <h3 className="font-semibold text-gray-900 hover:text-blue-600">
              {template.title}
            </h3>
            <p className="text-sm text-gray-500">{template.name} • v{template.version}</p>
            <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
              <span>{template.author}</span>
              <span>{formatDate(template.updated_at)}</span>
              <div className="flex items-center space-x-1">
                <Star className="h-3 w-3 text-yellow-500" />
                <span>{template.rating}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Download className="h-3 w-3" />
                <span>{template.downloads}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex flex-wrap gap-1 max-w-xs">
            {template.tags.slice(0, 2).map(tag => (
              <span
                key={tag}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
          
          <button
            onClick={() => toggleFavorite(template.id)}
            className="p-2 text-gray-400 hover:text-yellow-500 transition-colors"
          >
            {favorites.has(template.id) ? (
              <BookmarkCheck className="h-4 w-4 text-yellow-500" />
            ) : (
              <Bookmark className="h-4 w-4" />
            )}
          </button>
          
          <button
            onClick={() => handleTemplateAction('view', template)}
            className="px-3 py-1 text-sm border border-gray-300 text-gray-700 
                     hover:bg-gray-50 rounded transition-colors"
          >
            Preview
          </button>
          
          <button
            onClick={() => handleTemplateAction('use', template)}
            className="px-3 py-1 text-sm bg-blue-600 text-white hover:bg-blue-700 
                     rounded transition-colors"
          >
            Use
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Template Library</h1>
          <p className="text-gray-600">
            Discover, save, and share domain templates for faster development
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={onCreateNew}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white 
                     hover:bg-blue-700 rounded-lg transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>Create Template</span>
          </button>
          
          <button
            onClick={() => {
              const input = document.createElement('input');
              input.type = 'file';
              input.accept = '.json';
              input.onchange = (e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = (e) => {
                    try {
                      const template = JSON.parse(e.target?.result as string);
                      onImportTemplate?.(template);
                    } catch (error) {
                      alert('Invalid template file');
                    }
                  };
                  reader.readAsText(file);
                }
              };
              input.click();
            }}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 
                     text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Import</span>
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg 
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* View Toggle */}
          <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${
                viewMode === 'grid' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${
                viewMode === 'list' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Domain Type Filter */}
          <select
            value={filters.domainType}
            onChange={(e) => setFilters(prev => ({ 
              ...prev, 
              domainType: e.target.value as DomainType | 'all' 
            }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                     focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Domains</option>
            <option value="task_management">Task Management</option>
            <option value="e_commerce">E-Commerce</option>
            <option value="crm">CRM</option>
            <option value="healthcare">Healthcare</option>
            <option value="real_estate">Real Estate</option>
            <option value="education">Education</option>
            <option value="finance">Finance</option>
            <option value="custom">Custom</option>
          </select>

          {/* Sort */}
          <select
            value={`${filters.sortBy}-${filters.sortOrder}`}
            onChange={(e) => {
              const [sortBy, sortOrder] = e.target.value.split('-');
              setFilters(prev => ({ 
                ...prev, 
                sortBy: sortBy as any,
                sortOrder: sortOrder as 'asc' | 'desc'
              }));
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 
                     focus:ring-blue-500 focus:border-transparent"
          >
            <option value="updated_at-desc">Recently Updated</option>
            <option value="created_at-desc">Newest First</option>
            <option value="name-asc">Name A-Z</option>
            <option value="name-desc">Name Z-A</option>
            <option value="downloads-desc">Most Downloaded</option>
            <option value="rating-desc">Highest Rated</option>
          </select>

          {/* Quick Filters */}
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={filters.showFavorites}
                onChange={(e) => setFilters(prev => ({ 
                  ...prev, 
                  showFavorites: e.target.checked 
                }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span>Favorites</span>
            </label>
            
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={filters.showMyTemplates}
                onChange={(e) => setFilters(prev => ({ 
                  ...prev, 
                  showMyTemplates: e.target.checked 
                }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span>My Templates</span>
            </label>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between mb-6">
        <p className="text-gray-600">
          {loading ? 'Loading...' : `${filteredTemplates.length} template${filteredTemplates.length !== 1 ? 's' : ''} found`}
        </p>
        
        {favorites.size > 0 && (
          <p className="text-sm text-gray-500">
            {favorites.size} favorite{favorites.size !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      {/* Templates Grid/List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="bg-gray-200 animate-pulse rounded-lg h-64" />
          ))}
        </div>
      ) : filteredTemplates.length > 0 ? (
        <div className={
          viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            : "space-y-4"
        }>
          {filteredTemplates.map(template => 
            viewMode === 'grid' 
              ? renderTemplateCard(template)
              : renderTemplateList(template)
          )}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📄</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search or filters, or create a new template.
          </p>
          <button
            onClick={onCreateNew}
            className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 
                     rounded-lg transition-colors"
          >
            Create New Template
          </button>
        </div>
      )}

      {/* Template Preview Modal */}
      {showPreview && selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedTemplate.title}
                  </h2>
                  <p className="text-gray-600">Template Preview</p>
                </div>
                
                <button
                  onClick={() => setShowPreview(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
                >
                  ✕
                </button>
              </div>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <div className="text-6xl mb-4">
                  {getDomainTypeIcon(selectedTemplate.domain_type)}
                </div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Template Preview
                </h3>
                <p className="text-gray-500 mb-4">
                  Detailed template preview would be shown here with entities, 
                  relationships, and configuration details.
                </p>
                
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => {
                      setShowPreview(false);
                      handleTemplateAction('use', selectedTemplate);
                    }}
                    className="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 
                             rounded-lg transition-colors"
                  >
                    Use This Template
                  </button>
                  <button
                    onClick={() => handleTemplateAction('duplicate', selectedTemplate)}
                    className="px-6 py-2 border border-gray-300 text-gray-700 
                             hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    Duplicate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateLibrary;