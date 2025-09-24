import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Star,
  Download,
  Heart,
  TrendingUp,
  Award,
  ChevronDown,
  Grid,
  List,
  ArrowUp,
  ArrowDown,
  ExternalLink,
  Check,
  X,
  Plus
} from 'lucide-react';

interface MarketplaceTemplate {
  id: string;
  name: string;
  title: string;
  description: string;
  domain_type: string;
  version: string;
  author: {
    name: string;
    avatar: string;
    verified: boolean;
    reputation: number;
  };
  stats: {
    downloads: number;
    likes: number;
    rating: number;
    reviews: number;
    forks: number;
  };
  tags: string[];
  preview_images: string[];
  created_at: string;
  updated_at: string;
  license: string;
  price_type: 'free' | 'premium' | 'enterprise';
  price: number;
  featured: boolean;
  trending: boolean;
  category: string;
  complexity: 'beginner' | 'intermediate' | 'advanced';
  entities_count: number;
  features: string[];
  demo_url?: string;
  github_url?: string;
}

interface MarketplaceFilters {
  search: string;
  category: string;
  price_type: string;
  complexity: string;
  rating: number;
  sort_by: 'popularity' | 'rating' | 'recent' | 'downloads' | 'name';
  sort_order: 'asc' | 'desc';
  tags: string[];
}

interface TemplateMarketplaceProps {
  onSelectTemplate?: (template: MarketplaceTemplate) => void;
  onImportTemplate?: (template: MarketplaceTemplate) => void;
  onClose?: () => void;
}

const TemplateMarketplace: React.FC<TemplateMarketplaceProps> = ({
  onImportTemplate,
  onClose
}) => {
  const [templates, setTemplates] = useState<MarketplaceTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<MarketplaceTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedTemplate, setSelectedTemplate] = useState<MarketplaceTemplate | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  
  const [filters, setFilters] = useState<MarketplaceFilters>({
    search: '',
    category: '',
    price_type: '',
    complexity: '',
    rating: 0,
    sort_by: 'popularity',
    sort_order: 'desc',
    tags: []
  });

  const [showFilters, setShowFilters] = useState(false);
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [categories] = useState([
    'Task Management',
    'E-commerce',
    'CRM',
    'Healthcare',
    'Real Estate',
    'Education',
    'Finance',
    'Social Media',
    'Portfolio',
    'Blog',
    'Analytics',
    'Custom'
  ]);

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [templates, filters]);

  const loadTemplates = async () => {
    setLoading(true);
    
    // Mock data - in production, this would come from an API
    const mockTemplates: MarketplaceTemplate[] = [
      {
        id: '1',
        name: 'advanced-task-manager',
        title: 'Advanced Task Management System',
        description: 'A comprehensive task management system with team collaboration, time tracking, and advanced reporting features. Perfect for agile teams and project management.',
        domain_type: 'task_management',
        version: '2.1.0',
        author: {
          name: 'Sarah Chen',
          avatar: '👩‍💻',
          verified: true,
          reputation: 4.8
        },
        stats: {
          downloads: 12450,
          likes: 892,
          rating: 4.9,
          reviews: 156,
          forks: 234
        },
        tags: ['project-management', 'collaboration', 'agile', 'react', 'fastapi'],
        preview_images: ['/api/placeholder/400/300', '/api/placeholder/400/300'],
        created_at: '2024-08-15',
        updated_at: '2024-12-01',
        license: 'MIT',
        price_type: 'free',
        price: 0,
        featured: true,
        trending: true,
        category: 'Task Management',
        complexity: 'intermediate',
        entities_count: 8,
        features: ['User Management', 'Task Tracking', 'Time Tracking', 'Reports', 'API'],
        demo_url: 'https://demo.taskmanager.app',
        github_url: 'https://github.com/sarahchen/advanced-task-manager'
      },
      {
        id: '2',
        name: 'e-commerce-starter',
        title: 'Modern E-commerce Platform',
        description: 'Complete e-commerce solution with product catalog, shopping cart, payment integration, and admin dashboard. Built with modern technologies.',
        domain_type: 'e_commerce',
        version: '1.5.2',
        author: {
          name: 'Alex Rodriguez',
          avatar: '🧑‍💼',
          verified: true,
          reputation: 4.7
        },
        stats: {
          downloads: 8920,
          likes: 567,
          rating: 4.7,
          reviews: 89,
          forks: 145
        },
        tags: ['e-commerce', 'shopping', 'payments', 'stripe', 'nextjs'],
        preview_images: ['/api/placeholder/400/300', '/api/placeholder/400/300'],
        created_at: '2024-07-20',
        updated_at: '2024-11-28',
        license: 'MIT',
        price_type: 'premium',
        price: 49,
        featured: true,
        trending: false,
        category: 'E-commerce',
        complexity: 'advanced',
        entities_count: 12,
        features: ['Product Catalog', 'Cart', 'Payments', 'Admin Panel', 'Analytics'],
        demo_url: 'https://demo.ecommerce-starter.com'
      },
      {
        id: '3',
        name: 'simple-blog',
        title: 'Minimalist Blog Platform',
        description: 'Clean and simple blog platform with markdown support, SEO optimization, and responsive design. Perfect for personal blogs and content sites.',
        domain_type: 'blog',
        version: '1.2.0',
        author: {
          name: 'Maria Santos',
          avatar: '✍️',
          verified: false,
          reputation: 4.3
        },
        stats: {
          downloads: 5670,
          likes: 234,
          rating: 4.4,
          reviews: 45,
          forks: 89
        },
        tags: ['blog', 'markdown', 'seo', 'responsive', 'cms'],
        preview_images: ['/api/placeholder/400/300'],
        created_at: '2024-09-10',
        updated_at: '2024-11-30',
        license: 'Apache 2.0',
        price_type: 'free',
        price: 0,
        featured: false,
        trending: true,
        category: 'Blog',
        complexity: 'beginner',
        entities_count: 4,
        features: ['Markdown Editor', 'SEO', 'Comments', 'Media Library'],
        demo_url: 'https://demo.simple-blog.io',
        github_url: 'https://github.com/mariasantos/simple-blog'
      },
      {
        id: '4',
        name: 'crm-enterprise',
        title: 'Enterprise CRM System',
        description: 'Full-featured Customer Relationship Management system with lead tracking, sales pipeline, email automation, and comprehensive reporting.',
        domain_type: 'crm',
        version: '3.0.1',
        author: {
          name: 'TechCorp Solutions',
          avatar: '🏢',
          verified: true,
          reputation: 4.9
        },
        stats: {
          downloads: 3450,
          likes: 156,
          rating: 4.8,
          reviews: 67,
          forks: 23
        },
        tags: ['crm', 'sales', 'enterprise', 'automation', 'leads'],
        preview_images: ['/api/placeholder/400/300', '/api/placeholder/400/300', '/api/placeholder/400/300'],
        created_at: '2024-06-05',
        updated_at: '2024-12-02',
        license: 'Enterprise',
        price_type: 'enterprise',
        price: 299,
        featured: true,
        trending: false,
        category: 'CRM',
        complexity: 'advanced',
        entities_count: 15,
        features: ['Lead Management', 'Sales Pipeline', 'Email Automation', 'Reports', 'Integrations'],
        demo_url: 'https://demo.crm-enterprise.com'
      },
      {
        id: '5',
        name: 'healthcare-clinic',
        title: 'Healthcare Clinic Management',
        description: 'Comprehensive healthcare management system for clinics with patient records, appointment scheduling, and medical history tracking.',
        domain_type: 'healthcare',
        version: '2.3.0',
        author: {
          name: 'Dr. Emily Johnson',
          avatar: '👩‍⚕️',
          verified: true,
          reputation: 4.6
        },
        stats: {
          downloads: 2890,
          likes: 198,
          rating: 4.6,
          reviews: 34,
          forks: 67
        },
        tags: ['healthcare', 'clinic', 'patients', 'appointments', 'medical'],
        preview_images: ['/api/placeholder/400/300'],
        created_at: '2024-08-01',
        updated_at: '2024-11-25',
        license: 'GPL v3',
        price_type: 'premium',
        price: 149,
        featured: false,
        trending: true,
        category: 'Healthcare',
        complexity: 'advanced',
        entities_count: 10,
        features: ['Patient Records', 'Appointments', 'Medical History', 'Prescriptions', 'Reports']
      },
      {
        id: '6',
        name: 'portfolio-showcase',
        title: 'Creative Portfolio Showcase',
        description: 'Beautiful portfolio website template for designers, developers, and creative professionals. Fully customizable with modern animations.',
        domain_type: 'portfolio',
        version: '1.0.5',
        author: {
          name: 'Design Studio',
          avatar: '🎨',
          verified: false,
          reputation: 4.2
        },
        stats: {
          downloads: 7830,
          likes: 445,
          rating: 4.3,
          reviews: 78,
          forks: 123
        },
        tags: ['portfolio', 'design', 'creative', 'animations', 'showcase'],
        preview_images: ['/api/placeholder/400/300', '/api/placeholder/400/300'],
        created_at: '2024-10-15',
        updated_at: '2024-12-01',
        license: 'Creative Commons',
        price_type: 'free',
        price: 0,
        featured: false,
        trending: false,
        category: 'Portfolio',
        complexity: 'beginner',
        entities_count: 3,
        features: ['Gallery', 'Contact Form', 'About Page', 'Responsive Design'],
        demo_url: 'https://demo.portfolio-showcase.dev',
        github_url: 'https://github.com/designstudio/portfolio-showcase'
      }
    ];

    // Extract unique tags
    const tags = new Set<string>();
    mockTemplates.forEach(template => {
      template.tags.forEach(tag => tags.add(tag));
    });
    setAvailableTags(Array.from(tags));

    setTemplates(mockTemplates);
    setLoading(false);
  };

  const applyFilters = () => {
    let filtered = [...templates];

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(template =>
        template.title.toLowerCase().includes(searchLower) ||
        template.description.toLowerCase().includes(searchLower) ||
        template.tags.some(tag => tag.toLowerCase().includes(searchLower)) ||
        template.author.name.toLowerCase().includes(searchLower)
      );
    }

    // Category filter
    if (filters.category) {
      filtered = filtered.filter(template => template.category === filters.category);
    }

    // Price type filter
    if (filters.price_type) {
      filtered = filtered.filter(template => template.price_type === filters.price_type);
    }

    // Complexity filter
    if (filters.complexity) {
      filtered = filtered.filter(template => template.complexity === filters.complexity);
    }

    // Rating filter
    if (filters.rating > 0) {
      filtered = filtered.filter(template => template.stats.rating >= filters.rating);
    }

    // Tags filter
    if (filters.tags.length > 0) {
      filtered = filtered.filter(template =>
        filters.tags.every(tag => template.tags.includes(tag))
      );
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (filters.sort_by) {
        case 'popularity':
          comparison = a.stats.downloads - b.stats.downloads;
          break;
        case 'rating':
          comparison = a.stats.rating - b.stats.rating;
          break;
        case 'recent':
          comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
          break;
        case 'downloads':
          comparison = a.stats.downloads - b.stats.downloads;
          break;
        case 'name':
          comparison = a.title.localeCompare(b.title);
          break;
      }

      return filters.sort_order === 'asc' ? comparison : -comparison;
    });

    setFilteredTemplates(filtered);
  };

  const toggleFavorite = (templateId: string) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(templateId)) {
        newFavorites.delete(templateId);
      } else {
        newFavorites.add(templateId);
      }
      return newFavorites;
    });
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const getPriceDisplay = (template: MarketplaceTemplate): string => {
    switch (template.price_type) {
      case 'free':
        return 'Free';
      case 'premium':
        return `$${template.price}`;
      case 'enterprise':
        return `$${template.price}`;
      default:
        return 'Free';
    }
  };

  const getComplexityColor = (complexity: string): string => {
    switch (complexity) {
      case 'beginner':
        return 'text-green-600 bg-green-100';
      case 'intermediate':
        return 'text-yellow-600 bg-yellow-100';
      case 'advanced':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const renderTemplateCard = (template: MarketplaceTemplate) => {
    const isFavorite = favorites.has(template.id);

    if (viewMode === 'list') {
      return (
        <div key={template.id} className="bg-white border rounded-lg p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-start space-x-4">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-purple-500 rounded-lg flex items-center justify-center text-white text-2xl font-bold">
              {template.title.charAt(0)}
            </div>
            
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-gray-900">{template.title}</h3>
                    {template.featured && (
                      <Award className="h-4 w-4 text-yellow-500" />
                    )}
                    {template.trending && (
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{template.description}</p>
                  
                  <div className="flex items-center space-x-4 mt-2">
                    <div className="flex items-center space-x-1">
                      <span className="text-sm text-gray-500">{template.author.avatar}</span>
                      <span className="text-sm text-gray-600">{template.author.name}</span>
                      {template.author.verified && (
                        <Check className="h-4 w-4 text-blue-500" />
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600">{template.stats.rating}</span>
                      <span className="text-xs text-gray-500">({template.stats.reviews})</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Download className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-600">{formatNumber(template.stats.downloads)}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getComplexityColor(template.complexity)}`}>
                    {template.complexity}
                  </span>
                  <span className="text-lg font-semibold text-green-600">
                    {getPriceDisplay(template)}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between mt-4">
                <div className="flex flex-wrap gap-1">
                  {template.tags.slice(0, 4).map(tag => (
                    <span key={tag} className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                      {tag}
                    </span>
                  ))}
                  {template.tags.length > 4 && (
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                      +{template.tags.length - 4}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleFavorite(template.id)}
                    className={`p-2 rounded-lg transition-colors ${
                      isFavorite 
                        ? 'text-red-500 bg-red-50 hover:bg-red-100' 
                        : 'text-gray-400 hover:text-red-500 hover:bg-gray-50'
                    }`}
                  >
                    <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
                  </button>
                  
                  <button
                    onClick={() => {
                      setSelectedTemplate(template);
                      setShowPreview(true);
                    }}
                    className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 hover:border-blue-400 rounded-lg transition-colors"
                  >
                    Preview
                  </button>
                  
                  <button
                    onClick={() => onImportTemplate?.(template)}
                    className="px-3 py-1 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
                  >
                    Import
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div key={template.id} className="bg-white border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
        <div className="h-48 bg-gradient-to-br from-blue-400 to-purple-500 relative">
          <div className="absolute top-4 right-4 flex space-x-2">
            {template.featured && (
              <span className="px-2 py-1 bg-yellow-500 text-white text-xs font-medium rounded">
                Featured
              </span>
            )}
            {template.trending && (
              <span className="px-2 py-1 bg-green-500 text-white text-xs font-medium rounded flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                Trending
              </span>
            )}
          </div>
          
          <div className="absolute bottom-4 left-4 text-white">
            <div className="text-4xl font-bold mb-2">{template.title.charAt(0)}</div>
          </div>
          
          <button
            onClick={() => toggleFavorite(template.id)}
            className={`absolute top-4 left-4 p-2 rounded-full transition-colors ${
              isFavorite 
                ? 'text-red-500 bg-white' 
                : 'text-white hover:bg-white hover:bg-opacity-20'
            }`}
          >
            <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
        </div>
        
        <div className="p-6">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">{template.title}</h3>
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">{template.description}</p>
            </div>
            <span className="text-lg font-semibold text-green-600 ml-2">
              {getPriceDisplay(template)}
            </span>
          </div>
          
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-sm text-gray-500">{template.author.avatar}</span>
            <span className="text-sm text-gray-600">{template.author.name}</span>
            {template.author.verified && (
              <Check className="h-4 w-4 text-blue-500" />
            )}
          </div>
          
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                <span className="text-sm text-gray-600">{template.stats.rating}</span>
              </div>
              
              <div className="flex items-center space-x-1">
                <Download className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">{formatNumber(template.stats.downloads)}</span>
              </div>
            </div>
            
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getComplexityColor(template.complexity)}`}>
              {template.complexity}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-1 mb-4">
            {template.tags.slice(0, 3).map(tag => (
              <span key={tag} className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                {tag}
              </span>
            ))}
            {template.tags.length > 3 && (
              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                +{template.tags.length - 3}
              </span>
            )}
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => {
                setSelectedTemplate(template);
                setShowPreview(true);
              }}
              className="flex-1 px-3 py-2 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 hover:border-blue-400 rounded-lg transition-colors"
            >
              Preview
            </button>
            
            <button
              onClick={() => onImportTemplate?.(template)}
              className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
            >
              Import
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Template Marketplace</h2>
            <p className="text-gray-600 mt-1">Discover and import professional templates</p>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Search and Filters Bar */}
        <div className="p-6 border-b border-gray-200 space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search templates, authors, or tags..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 border border-gray-300 hover:border-gray-400 rounded-lg transition-colors flex items-center space-x-2"
            >
              <Filter className="h-4 w-4" />
              <span>Filters</span>
              <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="bg-gray-50 p-4 rounded-lg space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                  <select
                    value={filters.category}
                    onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Categories</option>
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Price</label>
                  <select
                    value={filters.price_type}
                    onChange={(e) => setFilters(prev => ({ ...prev, price_type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Prices</option>
                    <option value="free">Free</option>
                    <option value="premium">Premium</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Complexity</label>
                  <select
                    value={filters.complexity}
                    onChange={(e) => setFilters(prev => ({ ...prev, complexity: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Levels</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                  <div className="flex space-x-2">
                    <select
                      value={filters.sort_by}
                      onChange={(e) => setFilters(prev => ({ ...prev, sort_by: e.target.value as any }))}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="popularity">Popularity</option>
                      <option value="rating">Rating</option>
                      <option value="recent">Recent</option>
                      <option value="downloads">Downloads</option>
                      <option value="name">Name</option>
                    </select>
                    
                    <button
                      onClick={() => setFilters(prev => ({ 
                        ...prev, 
                        sort_order: prev.sort_order === 'asc' ? 'desc' : 'asc' 
                      }))}
                      className="px-3 py-2 text-gray-600 hover:text-gray-900 border border-gray-300 hover:border-gray-400 rounded-lg transition-colors"
                    >
                      {filters.sort_order === 'asc' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                <div className="flex flex-wrap gap-2">
                  {availableTags.slice(0, 10).map(tag => (
                    <button
                      key={tag}
                      onClick={() => {
                        setFilters(prev => ({
                          ...prev,
                          tags: prev.tags.includes(tag) 
                            ? prev.tags.filter(t => t !== tag)
                            : [...prev.tags, tag]
                        }));
                      }}
                      className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                        filters.tags.includes(tag)
                          ? 'bg-blue-100 text-blue-700 border border-blue-300'
                          : 'bg-white text-gray-600 border border-gray-300 hover:border-gray-400'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Summary */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <p className="text-sm text-gray-600">
            Showing {filteredTemplates.length} of {templates.length} templates
            {filters.search && ` for "${filters.search}"`}
          </p>
        </div>

        {/* Templates Grid/List */}
        <div className="flex-1 overflow-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredTemplates.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Search className="h-12 w-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
              <p className="text-gray-500">Try adjusting your search or filters</p>
            </div>
          ) : (
            <div className={`${
              viewMode === 'grid' 
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
                : 'space-y-4'
            }`}>
              {filteredTemplates.map(template => renderTemplateCard(template))}
            </div>
          )}
        </div>

        {/* Template Preview Modal */}
        {showPreview && selectedTemplate && (
          <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center z-10 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-auto">
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-2xl font-semibold text-gray-900">{selectedTemplate.title}</h3>
                    <p className="text-gray-600 mt-2">{selectedTemplate.description}</p>
                  </div>
                  
                  <button
                    onClick={() => setShowPreview(false)}
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Template Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Version:</span>
                        <span>{selectedTemplate.version}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">License:</span>
                        <span>{selectedTemplate.license}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Entities:</span>
                        <span>{selectedTemplate.entities_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Complexity:</span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getComplexityColor(selectedTemplate.complexity)}`}>
                          {selectedTemplate.complexity}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Statistics</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Downloads:</span>
                        <span>{formatNumber(selectedTemplate.stats.downloads)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Rating:</span>
                        <div className="flex items-center space-x-1">
                          <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span>{selectedTemplate.stats.rating}</span>
                          <span className="text-gray-500">({selectedTemplate.stats.reviews})</span>
                        </div>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Likes:</span>
                        <span>{formatNumber(selectedTemplate.stats.likes)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Forks:</span>
                        <span>{selectedTemplate.stats.forks}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">Features</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {selectedTemplate.features.map(feature => (
                      <div key={feature} className="flex items-center space-x-2 text-sm">
                        <Check className="h-4 w-4 text-green-500" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedTemplate.tags.map(tag => (
                      <span key={tag} className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <div className="flex space-x-2">
                    {selectedTemplate.demo_url && (
                      <button
                        onClick={() => window.open(selectedTemplate.demo_url, '_blank')}
                        className="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 hover:border-blue-400 rounded-lg transition-colors flex items-center space-x-2"
                      >
                        <ExternalLink className="h-4 w-4" />
                        <span>Live Demo</span>
                      </button>
                    )}
                    
                    {selectedTemplate.github_url && (
                      <button
                        onClick={() => window.open(selectedTemplate.github_url, '_blank')}
                        className="px-4 py-2 text-sm text-gray-600 hover:text-gray-700 border border-gray-300 hover:border-gray-400 rounded-lg transition-colors flex items-center space-x-2"
                      >
                        <ExternalLink className="h-4 w-4" />
                        <span>GitHub</span>
                      </button>
                    )}
                  </div>
                  
                  <button
                    onClick={() => {
                      onImportTemplate?.(selectedTemplate);
                      setShowPreview(false);
                    }}
                    className="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Import Template</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplateMarketplace;