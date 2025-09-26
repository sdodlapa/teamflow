/**
 * Template Marketplace - Day 12 Implementation
 * Browse, search, filter, and install templates from the marketplace
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  Star, 
  Download, 
  Eye,
  Heart,
  Clock,
  Users,
  Tag,
  CheckCircle,
  AlertCircle,
  Loader2,
  Grid,
  List,
  SlidersHorizontal,
  TrendingUp,
  Award,
  Zap
} from 'lucide-react';
import { LoadingSpinner } from '../components/LoadingComponents';

// Marketplace interfaces  
interface MarketplaceTemplate {
  id: string;
  name: string;
  title: string;
  description: string;
  category: 'business' | 'ecommerce' | 'healthcare' | 'education' | 'finance' | 'technology' | 'government';
  author: {
    name: string;
    avatar?: string;
    verified: boolean;
    organization?: string;
  };
  version: string;
  rating: number;
  totalRatings: number;
  downloads: number;
  price: number; // 0 for free
  tags: string[];
  features: string[];
  screenshots: string[];
  complexity: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  lastUpdated: string;
  demoUrl?: string;
  documentation?: string;
  entities: number;
  isPopular: boolean;
  isFeatured: boolean;
  isNew: boolean;
}

interface InstallationProgress {
  templateId: string;
  status: 'preparing' | 'downloading' | 'configuring' | 'installing' | 'completed' | 'failed';
  progress: number;
  currentStep: string;
  error?: string;
}

const CATEGORIES = [
  { id: 'all', name: 'All Templates', icon: Grid },
  { id: 'business', name: 'Business', icon: Users },
  { id: 'ecommerce', name: 'E-commerce', icon: Tag },
  { id: 'healthcare', name: 'Healthcare', icon: Heart },
  { id: 'education', name: 'Education', icon: Award },
  { id: 'finance', name: 'Finance', icon: TrendingUp },
  { id: 'technology', name: 'Technology', icon: Zap },
  { id: 'government', name: 'Government', icon: CheckCircle }
];

const SORT_OPTIONS = [
  { value: 'popular', label: 'Most Popular' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'downloads', label: 'Most Downloaded' },
  { value: 'newest', label: 'Newest First' },
  { value: 'updated', label: 'Recently Updated' },
  { value: 'name', label: 'Alphabetical' }
];

export const TemplateMarketplace: React.FC = () => {
  const navigate = useNavigate();
  
  // State management
  const [templates, setTemplates] = useState<MarketplaceTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<MarketplaceTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  
  // Filters and search
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('popular');
  const [priceFilter, setPriceFilter] = useState<'all' | 'free' | 'paid'>('all');
  const [complexityFilter, setComplexityFilter] = useState<'all' | 'beginner' | 'intermediate' | 'advanced'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  
  // Installation tracking
  const [installingTemplates, setInstallingTemplates] = useState<Map<string, InstallationProgress>>(new Map());

  // Load marketplace templates
  useEffect(() => {
    const loadMarketplaceTemplates = async () => {
      try {
        setLoading(true);
        
        // Simulate loading marketplace templates
        // In real implementation, this would be: await fetch('/api/v1/marketplace/templates')
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const mockTemplates: MarketplaceTemplate[] = [
          {
            id: 'task-management-pro',
            name: 'task_management_pro',
            title: 'Task Management Pro',
            description: 'Advanced task management system with team collaboration, time tracking, and project analytics. Perfect for growing teams.',
            category: 'business',
            author: {
              name: 'TeamFlow',
              verified: true,
              organization: 'TeamFlow Inc.'
            },
            version: '2.1.0',
            rating: 4.9,
            totalRatings: 234,
            downloads: 1250,
            price: 0,
            tags: ['tasks', 'projects', 'collaboration', 'analytics'],
            features: ['Team Collaboration', 'Time Tracking', 'Analytics Dashboard', 'Mobile App'],
            screenshots: [],
            complexity: 'intermediate',
            estimatedTime: '30 minutes',
            lastUpdated: '2025-09-20',
            entities: 8,
            isPopular: true,
            isFeatured: true,
            isNew: false
          },
          {
            id: 'ecommerce-store',
            name: 'ecommerce_store',
            title: 'E-commerce Store',
            description: 'Complete e-commerce solution with product catalog, shopping cart, payment processing, and order management.',
            category: 'ecommerce',
            author: {
              name: 'Commerce Labs',
              verified: true,
              organization: 'Commerce Labs'
            },
            version: '1.8.2',
            rating: 4.7,
            totalRatings: 189,
            downloads: 890,
            price: 49,
            tags: ['ecommerce', 'shopping', 'payments', 'inventory'],
            features: ['Product Catalog', 'Shopping Cart', 'Payment Gateway', 'Order Tracking'],
            screenshots: [],
            complexity: 'advanced',
            estimatedTime: '45 minutes',
            lastUpdated: '2025-09-18',
            entities: 12,
            isPopular: true,
            isFeatured: false,
            isNew: false
          },
          {
            id: 'healthcare-clinic',
            name: 'healthcare_clinic',
            title: 'Healthcare Clinic Management',
            description: 'Comprehensive clinic management system with patient records, appointments, billing, and medical history tracking.',
            category: 'healthcare',
            author: {
              name: 'MedTech Solutions',
              verified: true,
              organization: 'MedTech Inc.'
            },
            version: '3.0.1',
            rating: 4.8,
            totalRatings: 156,
            downloads: 650,
            price: 99,
            tags: ['healthcare', 'patients', 'appointments', 'medical'],
            features: ['Patient Records', 'Appointment Scheduling', 'Billing System', 'Medical History'],
            screenshots: [],
            complexity: 'advanced',
            estimatedTime: '60 minutes',
            lastUpdated: '2025-09-22',
            entities: 15,
            isPopular: false,
            isFeatured: true,
            isNew: false
          },
          {
            id: 'student-portal',
            name: 'student_portal',
            title: 'Student Portal',
            description: 'Modern student management system with course enrollment, grade tracking, and communication tools.',
            category: 'education',
            author: {
              name: 'EduTech',
              verified: false,
              organization: 'EduTech Solutions'
            },
            version: '1.5.0',
            rating: 4.5,
            totalRatings: 98,
            downloads: 420,
            price: 0,
            tags: ['education', 'students', 'courses', 'grades'],
            features: ['Course Management', 'Grade Tracking', 'Student Communication', 'Assignment Submission'],
            screenshots: [],
            complexity: 'beginner',
            estimatedTime: '25 minutes',
            lastUpdated: '2025-09-15',
            entities: 6,
            isPopular: false,
            isFeatured: false,
            isNew: true
          },
          {
            id: 'property-management',
            name: 'property_management',
            title: 'Property Management',
            description: 'Complete property management solution with tenant tracking, maintenance requests, and rent collection.',
            category: 'business',
            author: {
              name: 'PropTech',
              verified: true,
              organization: 'PropTech Solutions'
            },
            version: '2.3.1',
            rating: 4.6,
            totalRatings: 167,
            downloads: 780,
            price: 0,
            tags: ['property', 'tenants', 'maintenance', 'rent'],
            features: ['Tenant Management', 'Maintenance Tracking', 'Rent Collection', 'Property Analytics'],
            screenshots: [],
            complexity: 'intermediate',
            estimatedTime: '35 minutes',
            lastUpdated: '2025-09-10',
            entities: 10,
            isPopular: true,
            isFeatured: false,
            isNew: false
          },
          {
            id: 'financial-tracker',
            name: 'financial_tracker',
            title: 'Personal Finance Tracker',
            description: 'Personal finance management with expense tracking, budgeting, investment monitoring, and financial goals.',
            category: 'finance',
            author: {
              name: 'FinTech Pro',
              verified: true,
              organization: 'FinTech Pro Ltd.'
            },
            version: '1.2.0',
            rating: 4.4,
            totalRatings: 72,
            downloads: 315,
            price: 29,
            tags: ['finance', 'budgeting', 'expenses', 'investments'],
            features: ['Expense Tracking', 'Budget Planning', 'Investment Monitor', 'Financial Goals'],
            screenshots: [],
            complexity: 'beginner',
            estimatedTime: '20 minutes',
            lastUpdated: '2025-09-25',
            entities: 7,
            isPopular: false,
            isFeatured: false,
            isNew: true
          }
        ];
        
        setTemplates(mockTemplates);
        setFilteredTemplates(mockTemplates);
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load marketplace templates');
      } finally {
        setLoading(false);
      }
    };

    loadMarketplaceTemplates();
  }, []);

  // Filter and search templates
  useEffect(() => {
    let filtered = templates;
    
    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(template => template.category === selectedCategory);
    }
    
    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(template => 
        template.title.toLowerCase().includes(query) ||
        template.description.toLowerCase().includes(query) ||
        template.tags.some(tag => tag.toLowerCase().includes(query)) ||
        template.author.name.toLowerCase().includes(query)
      );
    }
    
    // Price filter
    if (priceFilter === 'free') {
      filtered = filtered.filter(template => template.price === 0);
    } else if (priceFilter === 'paid') {
      filtered = filtered.filter(template => template.price > 0);
    }
    
    // Complexity filter
    if (complexityFilter !== 'all') {
      filtered = filtered.filter(template => template.complexity === complexityFilter);
    }
    
    // Sort templates
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'downloads':
          return b.downloads - a.downloads;
        case 'newest':
          return new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
        case 'updated':
          return new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
        case 'name':
          return a.title.localeCompare(b.title);
        case 'popular':
        default:
          // Popular combines downloads, ratings, and featured status
          const aScore = (a.downloads * 0.4) + (a.rating * a.totalRatings * 0.4) + (a.isFeatured ? 1000 : 0) + (a.isPopular ? 500 : 0);
          const bScore = (b.downloads * 0.4) + (b.rating * b.totalRatings * 0.4) + (b.isFeatured ? 1000 : 0) + (b.isPopular ? 500 : 0);
          return bScore - aScore;
      }
    });
    
    setFilteredTemplates(filtered);
  }, [templates, searchQuery, selectedCategory, sortBy, priceFilter, complexityFilter]);

  // Handle template installation
  const handleInstallTemplate = async (template: MarketplaceTemplate) => {
    try {
      const installProgress: InstallationProgress = {
        templateId: template.id,
        status: 'preparing',
        progress: 0,
        currentStep: 'Preparing installation...'
      };
      
      setInstallingTemplates(prev => new Map(prev).set(template.id, installProgress));
      
      // Simulate installation process
      const steps = [
        { status: 'downloading' as const, progress: 25, step: 'Downloading template files...' },
        { status: 'configuring' as const, progress: 50, step: 'Configuring template settings...' },
        { status: 'installing' as const, progress: 75, step: 'Installing template components...' },
        { status: 'completed' as const, progress: 100, step: 'Installation completed successfully!' }
      ];
      
      for (const step of steps) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        setInstallingTemplates(prev => {
          const updated = new Map(prev);
          updated.set(template.id, {
            templateId: template.id,
            status: step.status,
            progress: step.progress,
            currentStep: step.step
          });
          return updated;
        });
      }
      
      // Remove from installing after completion
      setTimeout(() => {
        setInstallingTemplates(prev => {
          const updated = new Map(prev);
          updated.delete(template.id);
          return updated;
        });
      }, 3000);
      
    } catch (err) {
      setInstallingTemplates(prev => {
        const updated = new Map(prev);
        updated.set(template.id, {
          templateId: template.id,
          status: 'failed',
          progress: 0,
          currentStep: 'Installation failed',
          error: err instanceof Error ? err.message : 'Installation failed'
        });
        return updated;
      });
    }
  };

  // Render template card
  const renderTemplateCard = (template: MarketplaceTemplate) => {
    const installation = installingTemplates.get(template.id);
    const isInstalling = !!installation;
    
    return (
      <div key={template.id} className={`bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow ${
        viewMode === 'list' ? 'flex' : ''
      }`}>
        {/* Template Header */}
        <div className={`${viewMode === 'list' ? 'w-48 flex-shrink-0' : ''} p-6`}>
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">{template.title}</h3>
              {template.isFeatured && (
                <Award className="h-4 w-4 text-yellow-500" />
              )}
              {template.isNew && (
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">New</span>
              )}
            </div>
            <div className="text-right">
              {template.price === 0 ? (
                <span className="text-green-600 font-medium">Free</span>
              ) : (
                <span className="text-gray-900 font-medium">${template.price}</span>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-4 mb-3 text-sm text-gray-600">
            <div className="flex items-center">
              <Star className="h-4 w-4 text-yellow-400 mr-1" />
              <span>{template.rating}</span>
              <span className="ml-1">({template.totalRatings})</span>
            </div>
            <div className="flex items-center">
              <Download className="h-4 w-4 mr-1" />
              <span>{template.downloads.toLocaleString()}</span>
            </div>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              <span>{template.estimatedTime}</span>
            </div>
          </div>
        </div>

        {/* Template Content */}
        <div className={`${viewMode === 'list' ? 'flex-1' : ''} px-6 pb-6`}>
          <p className="text-gray-600 mb-4 line-clamp-2">{template.description}</p>
          
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-xs font-medium text-blue-600">
                  {template.author.name.charAt(0)}
                </span>
              </div>
              <div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-700">{template.author.name}</span>
                  {template.author.verified && (
                    <CheckCircle className="h-3 w-3 text-blue-500 ml-1" />
                  )}
                </div>
                {template.author.organization && (
                  <span className="text-xs text-gray-500">{template.author.organization}</span>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-1">
              <span className={`px-2 py-1 text-xs rounded-full ${
                template.complexity === 'beginner' ? 'bg-green-100 text-green-800' :
                template.complexity === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {template.complexity}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-1 mb-4">
            {template.tags.slice(0, 4).map(tag => (
              <span key={tag} className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                {tag}
              </span>
            ))}
            {template.tags.length > 4 && (
              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded">
                +{template.tags.length - 4} more
              </span>
            )}
          </div>

          {/* Installation Progress */}
          {isInstalling && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">
                  {installation.currentStep}
                </span>
                <span className="text-sm text-blue-700">{installation.progress}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${installation.progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => navigate(`/templates/details/${template.id}`)}
              className="flex-1 flex items-center justify-center px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              <Eye className="h-4 w-4 mr-2" />
              View Details
            </button>
            
            <button
              onClick={() => handleInstallTemplate(template)}
              disabled={isInstalling}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md ${
                isInstalling 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isInstalling ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Installing...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Install
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Marketplace</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
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
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Template Marketplace</h1>
              <p className="text-sm text-gray-600">
                Discover and install professional templates for your projects
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
              >
                {viewMode === 'grid' ? <List className="h-5 w-5" /> : <Grid className="h-5 w-5" />}
              </button>
              
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-3 py-2 border border-gray-300 text-sm rounded-md hover:bg-gray-50"
              >
                <SlidersHorizontal className="h-4 w-4 mr-2" />
                Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <div className={`w-64 flex-shrink-0 ${showFilters ? 'block' : 'hidden lg:block'}`}>
            {/* Search */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Categories */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <h3 className="font-medium text-gray-900 mb-3">Categories</h3>
              <div className="space-y-1">
                {CATEGORIES.map(category => {
                  const Icon = category.icon;
                  const isSelected = selectedCategory === category.id;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`w-full flex items-center px-3 py-2 text-sm rounded-md ${
                        isSelected 
                          ? 'bg-blue-100 text-blue-700' 
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {category.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <h3 className="font-medium text-gray-900 mb-3">Filters</h3>
              
              <div className="space-y-4">
                {/* Price Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Price</label>
                  <select
                    value={priceFilter}
                    onChange={(e) => setPriceFilter(e.target.value as 'all' | 'free' | 'paid')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All Templates</option>
                    <option value="free">Free Only</option>
                    <option value="paid">Paid Only</option>
                  </select>
                </div>

                {/* Complexity Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Complexity</label>
                  <select
                    value={complexityFilter}
                    onChange={(e) => setComplexityFilter(e.target.value as 'all' | 'beginner' | 'intermediate' | 'advanced')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All Levels</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-medium text-gray-900">
                  {filteredTemplates.length} templates found
                </h2>
                {searchQuery && (
                  <p className="text-sm text-gray-600">
                    Results for "{searchQuery}"
                  </p>
                )}
              </div>
              
              <div className="flex items-center space-x-3">
                <label className="text-sm text-gray-600">Sort by:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {SORT_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Templates Grid/List */}
            {filteredTemplates.length === 0 ? (
              <div className="text-center py-12">
                <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
                <p className="text-gray-600">
                  Try adjusting your search or filters to find more templates.
                </p>
              </div>
            ) : (
              <div className={`${
                viewMode === 'grid' 
                  ? 'grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6' 
                  : 'space-y-4'
              }`}>
                {filteredTemplates.map(renderTemplateCard)}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateMarketplace;