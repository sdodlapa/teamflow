import React, { useState, useEffect, useMemo } from 'react';
import {
  Search, Star, Download, Eye, Share2,
  Grid, List, User,
  Heart, MessageSquare, Zap, Award,
  CheckCircle
} from 'lucide-react';
import './TemplateMarketplace.css';

interface Template {
  id: string;
  name: string;
  description: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
    verified: boolean;
  };
  category: string;
  tags: string[];
  version: string;
  downloads: number;
  rating: number;
  reviews: number;
  likes: number;
  createdAt: string;
  updatedAt: string;
  price: number; // 0 for free
  isPremium: boolean;
  isVerified: boolean;
  previewImages: string[];
  demoUrl?: string;
  complexity: 'beginner' | 'intermediate' | 'advanced';
  entities: number;
  relationships: number;
  features: string[];
  compatibility: string[];
  license: string;
}

interface TemplateMarketplaceProps {
  onTemplateSelect?: (template: Template) => void;
  onTemplatePreview?: (template: Template) => void;
  onTemplateDownload?: (template: Template) => void;
}

type ViewMode = 'grid' | 'list';
type SortBy = 'popular' | 'newest' | 'rating' | 'downloads' | 'name';
type FilterBy = 'all' | 'free' | 'premium' | 'verified';

export const TemplateMarketplace: React.FC<TemplateMarketplaceProps> = ({
  onTemplateSelect,
  onTemplatePreview,
  onTemplateDownload
}) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedTags] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortBy, setSortBy] = useState<SortBy>('popular');
  const [filterBy, setFilterBy] = useState<FilterBy>('all');
  const [priceRange] = useState<[number, number]>([0, 1000]);
  const [complexityFilter] = useState<string[]>([]);

  // Mock data for demonstration
  const mockTemplates: Template[] = [
    {
      id: '1',
      name: 'E-commerce Platform',
      description: 'Complete e-commerce solution with product management, shopping cart, and payment integration.',
      author: {
        id: 'author1',
        name: 'Alex Johnson',
        avatar: '/avatars/alex.jpg',
        verified: true
      },
      category: 'E-commerce',
      tags: ['react', 'typescript', 'stripe', 'inventory', 'payments'],
      version: '2.1.0',
      downloads: 15420,
      rating: 4.8,
      reviews: 342,
      likes: 1205,
      createdAt: '2025-01-15T10:00:00Z',
      updatedAt: '2025-09-20T14:30:00Z',
      price: 0,
      isPremium: false,
      isVerified: true,
      previewImages: ['/previews/ecommerce1.jpg', '/previews/ecommerce2.jpg'],
      demoUrl: 'https://demo-ecommerce.example.com',
      complexity: 'intermediate',
      entities: 12,
      relationships: 18,
      features: ['Authentication', 'Product Catalog', 'Shopping Cart', 'Payment Processing', 'Order Management'],
      compatibility: ['PostgreSQL', 'MySQL', 'SQLite'],
      license: 'MIT'
    },
    {
      id: '2',
      name: 'CRM System',
      description: 'Customer relationship management system with lead tracking, pipeline management, and analytics.',
      author: {
        id: 'author2',
        name: 'Sarah Chen',
        avatar: '/avatars/sarah.jpg',
        verified: true
      },
      category: 'Business',
      tags: ['crm', 'analytics', 'sales', 'pipeline', 'reports'],
      version: '1.5.2',
      downloads: 8930,
      rating: 4.6,
      reviews: 156,
      likes: 743,
      createdAt: '2025-03-10T09:15:00Z',
      updatedAt: '2025-09-18T11:45:00Z',
      price: 49.99,
      isPremium: true,
      isVerified: true,
      previewImages: ['/previews/crm1.jpg'],
      complexity: 'advanced',
      entities: 8,
      relationships: 15,
      features: ['Lead Management', 'Pipeline Tracking', 'Analytics Dashboard', 'Email Integration'],
      compatibility: ['PostgreSQL', 'MySQL'],
      license: 'Commercial'
    },
    {
      id: '3',
      name: 'Blog Platform',
      description: 'Modern blogging platform with markdown support, commenting system, and SEO optimization.',
      author: {
        id: 'author3',
        name: 'Mike Rodriguez',
        verified: false
      },
      category: 'Content',
      tags: ['blog', 'markdown', 'seo', 'comments', 'cms'],
      version: '1.0.3',
      downloads: 5670,
      rating: 4.3,
      reviews: 89,
      likes: 432,
      createdAt: '2025-07-22T16:20:00Z',
      updatedAt: '2025-09-15T13:10:00Z',
      price: 0,
      isPremium: false,
      isVerified: false,
      previewImages: ['/previews/blog1.jpg', '/previews/blog2.jpg'],
      demoUrl: 'https://demo-blog.example.com',
      complexity: 'beginner',
      entities: 5,
      relationships: 8,
      features: ['Markdown Editor', 'Comment System', 'SEO Tools', 'Tag Management'],
      compatibility: ['PostgreSQL', 'MySQL', 'SQLite'],
      license: 'MIT'
    },
    {
      id: '4',
      name: 'Project Management',
      description: 'Comprehensive project management tool with task tracking, team collaboration, and time management.',
      author: {
        id: 'author4',
        name: 'Lisa Wang',
        avatar: '/avatars/lisa.jpg',
        verified: true
      },
      category: 'Productivity',
      tags: ['project-management', 'tasks', 'collaboration', 'time-tracking', 'teams'],
      version: '3.2.1',
      downloads: 12340,
      rating: 4.9,
      reviews: 287,
      likes: 956,
      createdAt: '2024-11-05T12:00:00Z',
      updatedAt: '2025-09-22T10:15:00Z',
      price: 29.99,
      isPremium: true,
      isVerified: true,
      previewImages: ['/previews/pm1.jpg', '/previews/pm2.jpg', '/previews/pm3.jpg'],
      demoUrl: 'https://demo-pm.example.com',
      complexity: 'intermediate',
      entities: 10,
      relationships: 14,
      features: ['Task Management', 'Time Tracking', 'Team Collaboration', 'Gantt Charts', 'Reports'],
      compatibility: ['PostgreSQL', 'MySQL'],
      license: 'Commercial'
    }
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setTemplates(mockTemplates);
      setLoading(false);
    }, 1000);
  }, []);

  // Get unique categories and tags for filters
  const categories = useMemo(() => {
    const cats = ['all', ...new Set(templates.map(t => t.category))];
    return cats;
  }, [templates]);

  // Filter and sort templates
  const filteredTemplates = useMemo(() => {
    let filtered = templates.filter(template => {
      // Text search
      const matchesSearch = !searchQuery || 
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      // Category filter
      const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;

      // Tags filter
      const matchesTags = selectedTags.length === 0 || 
        selectedTags.some(tag => template.tags.includes(tag));

      // Price filter
      const matchesPrice = filterBy === 'all' || 
        (filterBy === 'free' && template.price === 0) ||
        (filterBy === 'premium' && template.price > 0) ||
        (filterBy === 'verified' && template.isVerified);

      // Price range
      const matchesPriceRange = template.price >= priceRange[0] && template.price <= priceRange[1];

      // Complexity filter
      const matchesComplexity = complexityFilter.length === 0 || 
        complexityFilter.includes(template.complexity);

      return matchesSearch && matchesCategory && matchesTags && 
             matchesPrice && matchesPriceRange && matchesComplexity;
    });

    // Sort templates
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return b.downloads - a.downloads;
        case 'newest':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'rating':
          return b.rating - a.rating;
        case 'downloads':
          return b.downloads - a.downloads;
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

    return filtered;
  }, [templates, searchQuery, selectedCategory, selectedTags, sortBy, filterBy, priceRange, complexityFilter]);

  const handleTemplateClick = (template: Template) => {
    onTemplateSelect?.(template);
  };

  const handlePreviewClick = (template: Template, e: React.MouseEvent) => {
    e.stopPropagation();
    onTemplatePreview?.(template);
  };

  const handleDownloadClick = (template: Template, e: React.MouseEvent) => {
    e.stopPropagation();
    onTemplateDownload?.(template);
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getComplexityColor = (complexity: string): string => {
    switch (complexity) {
      case 'beginner': return '#10b981';
      case 'intermediate': return '#f59e0b';
      case 'advanced': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="template-marketplace loading">
        <div className="loading-spinner">
          <Zap className="loading-icon" />
          <p>Loading templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="template-marketplace">
      <div className="marketplace-header">
        <div className="header-content">
          <h1 className="marketplace-title">
            <Award className="title-icon" />
            Template Marketplace
          </h1>
          <p className="marketplace-subtitle">
            Discover and download professional templates to accelerate your development
          </p>
        </div>

        <div className="marketplace-stats">
          <div className="stat-item">
            <span className="stat-number">{formatNumber(templates.reduce((sum, t) => sum + t.downloads, 0))}</span>
            <span className="stat-label">Downloads</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{templates.length}</span>
            <span className="stat-label">Templates</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{templates.filter(t => t.isVerified).length}</span>
            <span className="stat-label">Verified</span>
          </div>
        </div>
      </div>

      <div className="marketplace-controls">
        <div className="search-section">
          <div className="search-box">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-controls">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="filter-select"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category}
                </option>
              ))}
            </select>

            <select
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value as FilterBy)}
              className="filter-select"
            >
              <option value="all">All Templates</option>
              <option value="free">Free Only</option>
              <option value="premium">Premium Only</option>
              <option value="verified">Verified Only</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortBy)}
              className="sort-select"
            >
              <option value="popular">Most Popular</option>
              <option value="newest">Newest First</option>
              <option value="rating">Highest Rated</option>
              <option value="downloads">Most Downloaded</option>
              <option value="name">Name A-Z</option>
            </select>
          </div>
        </div>

        <div className="view-controls">
          <button
            className={`view-button ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
          >
            <Grid size={16} />
            Grid
          </button>
          <button
            className={`view-button ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
          >
            <List size={16} />
            List
          </button>
        </div>
      </div>

      <div className="marketplace-content">
        <div className="templates-section">
          <div className="templates-header">
            <h2>Templates ({filteredTemplates.length})</h2>
          </div>

          <div className={`templates-grid ${viewMode}`}>
            {filteredTemplates.map(template => (
              <div
                key={template.id}
                className="template-card"
                onClick={() => handleTemplateClick(template)}
              >
                <div className="template-preview">
                  {template.previewImages.length > 0 ? (
                    <img
                      src={template.previewImages[0]}
                      alt={template.name}
                      className="preview-image"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/placeholder-template.jpg';
                      }}
                    />
                  ) : (
                    <div className="preview-placeholder">
                      <Zap size={32} />
                    </div>
                  )}

                  <div className="template-badges">
                    {template.isPremium && (
                      <span className="badge premium">Premium</span>
                    )}
                    {template.isVerified && (
                      <span className="badge verified">
                        <CheckCircle size={12} />
                        Verified
                      </span>
                    )}
                    <span 
                      className="badge complexity"
                      style={{ backgroundColor: getComplexityColor(template.complexity) }}
                    >
                      {template.complexity}
                    </span>
                  </div>

                  <div className="template-actions">
                    <button
                      className="action-button preview"
                      onClick={(e) => handlePreviewClick(template, e)}
                      title="Preview"
                    >
                      <Eye size={14} />
                    </button>
                    <button
                      className="action-button download"
                      onClick={(e) => handleDownloadClick(template, e)}
                      title="Download"
                    >
                      <Download size={14} />
                    </button>
                    <button className="action-button share" title="Share">
                      <Share2 size={14} />
                    </button>
                  </div>
                </div>

                <div className="template-info">
                  <div className="template-header">
                    <h3 className="template-name">{template.name}</h3>
                    <div className="template-price">
                      {template.price === 0 ? 'Free' : `$${template.price}`}
                    </div>
                  </div>

                  <p className="template-description">{template.description}</p>

                  <div className="template-author">
                    <div className="author-info">
                      {template.author.avatar ? (
                        <img
                          src={template.author.avatar}
                          alt={template.author.name}
                          className="author-avatar"
                        />
                      ) : (
                        <div className="author-avatar placeholder">
                          <User size={12} />
                        </div>
                      )}
                      <span className="author-name">
                        {template.author.name}
                        {template.author.verified && (
                          <CheckCircle size={12} className="verified-icon" />
                        )}
                      </span>
                    </div>
                    <span className="template-version">v{template.version}</span>
                  </div>

                  <div className="template-tags">
                    {template.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                    {template.tags.length > 3 && (
                      <span className="tag-more">+{template.tags.length - 3}</span>
                    )}
                  </div>

                  <div className="template-metrics">
                    <div className="metric">
                      <Star size={12} />
                      <span>{template.rating}</span>
                    </div>
                    <div className="metric">
                      <Download size={12} />
                      <span>{formatNumber(template.downloads)}</span>
                    </div>
                    <div className="metric">
                      <Heart size={12} />
                      <span>{formatNumber(template.likes)}</span>
                    </div>
                    <div className="metric">
                      <MessageSquare size={12} />
                      <span>{template.reviews}</span>
                    </div>
                  </div>

                  <div className="template-details">
                    <div className="detail-item">
                      <span className="detail-label">Entities:</span>
                      <span className="detail-value">{template.entities}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Relations:</span>
                      <span className="detail-value">{template.relationships}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Updated:</span>
                      <span className="detail-value">
                        {new Date(template.updatedAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredTemplates.length === 0 && (
            <div className="no-templates">
              <Search size={48} />
              <h3>No templates found</h3>
              <p>Try adjusting your filters or search criteria</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};