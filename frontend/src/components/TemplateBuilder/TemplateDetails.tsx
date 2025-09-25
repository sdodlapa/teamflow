import React, { useState, useEffect } from 'react';
import {
  X, Star, Download, Eye, Share2, Heart,
  Clock, User, Tag, Shield, Code, Database,
  Play, Check, Calendar, GitBranch,
  Zap, Box, FileText, ArrowLeft, CheckCircle
} from 'lucide-react';
import './TemplateDetails.css';

interface Template {
  id: string;
  name: string;
  description: string;
  longDescription?: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
    verified: boolean;
    bio?: string;
    templates?: number;
    followers?: number;
  };
  category: string;
  tags: string[];
  version: string;
  changelog?: { version: string; changes: string[]; date: string }[];
  downloads: number;
  rating: number;
  reviews: number;
  likes: number;
  createdAt: string;
  updatedAt: string;
  price: number;
  isPremium: boolean;
  isVerified: boolean;
  previewImages: string[];
  demoUrl?: string;
  repositoryUrl?: string;
  complexity: 'beginner' | 'intermediate' | 'advanced';
  entities: number;
  relationships: number;
  features: string[];
  compatibility: string[];
  license: string;
  requirements?: string[];
  documentation?: string;
  support?: {
    email?: string;
    discord?: string;
    github?: string;
  };
}

interface Review {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  rating: number;
  comment: string;
  date: string;
  helpful: number;
}

interface TemplateDetailsProps {
  template: Template;
  onClose: () => void;
  onDownload?: (template: Template) => void;
  onPreview?: (template: Template) => void;
}

export const TemplateDetails: React.FC<TemplateDetailsProps> = ({
  template,
  onClose,
  onDownload,
  onPreview
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'features' | 'reviews' | 'changelog'>('overview');
  const [selectedImage, setSelectedImage] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [showFullDescription, setShowFullDescription] = useState(false);
  const [copied, setCopied] = useState(false);

  // Mock reviews data
  const mockReviews: Review[] = [
    {
      id: '1',
      userId: 'user1',
      userName: 'John Developer',
      userAvatar: '/avatars/john.jpg',
      rating: 5,
      comment: 'Excellent template! Saved me weeks of development time. The code quality is outstanding and documentation is comprehensive.',
      date: '2025-09-20T10:00:00Z',
      helpful: 15
    },
    {
      id: '2',
      userId: 'user2',
      userName: 'Sarah Smith',
      rating: 4,
      comment: 'Great starting point for e-commerce projects. Well structured and easy to customize. Minor issues with some edge cases.',
      date: '2025-09-15T14:30:00Z',
      helpful: 8
    },
    {
      id: '3',
      userId: 'user3',
      userName: 'Mike Chen',
      userAvatar: '/avatars/mike.jpg',
      rating: 5,
      comment: 'Perfect template with modern best practices. The author provides excellent support too!',
      date: '2025-09-10T09:15:00Z',
      helpful: 12
    }
  ];

  useEffect(() => {
    setReviews(mockReviews);
  }, [template.id]);

  const handleDownload = () => {
    onDownload?.(template);
  };

  const handlePreview = () => {
    onPreview?.(template);
  };

  const handleShare = async () => {
    const url = `${window.location.origin}/templates/${template.id}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy URL:', err);
    }
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

  const renderStars = (rating: number): React.ReactNode => {
    return (
      <div className="stars">
        {[1, 2, 3, 4, 5].map(star => (
          <Star
            key={star}
            size={14}
            className={star <= rating ? 'star filled' : 'star'}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="template-details-overlay">
      <div className="template-details">
        <div className="details-header">
          <button className="back-button" onClick={onClose}>
            <ArrowLeft size={20} />
            Back to Marketplace
          </button>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="details-content">
          <div className="template-hero">
            <div className="hero-images">
              <div className="main-image">
                {template.previewImages.length > 0 ? (
                  <img
                    src={template.previewImages[selectedImage]}
                    alt={template.name}
                    className="preview-image"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/placeholder-template.jpg';
                    }}
                  />
                ) : (
                  <div className="preview-placeholder">
                    <Zap size={64} />
                  </div>
                )}
                
                <div className="image-overlay">
                  {template.demoUrl && (
                    <button className="demo-button" onClick={handlePreview}>
                      <Play size={16} />
                      Live Demo
                    </button>
                  )}
                </div>
              </div>

              {template.previewImages.length > 1 && (
                <div className="image-thumbnails">
                  {template.previewImages.map((image, index) => (
                    <button
                      key={index}
                      className={`thumbnail ${selectedImage === index ? 'active' : ''}`}
                      onClick={() => setSelectedImage(index)}
                    >
                      <img src={image} alt={`Preview ${index + 1}`} />
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="hero-info">
              <div className="template-header">
                <div className="header-main">
                  <h1 className="template-title">{template.name}</h1>
                  <div className="template-badges">
                    {template.isPremium && (
                      <span className="badge premium">Premium</span>
                    )}
                    {template.isVerified && (
                      <span className="badge verified">
                        <Shield size={12} />
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
                </div>

                <div className="template-price">
                  {template.price === 0 ? (
                    <span className="price free">Free</span>
                  ) : (
                    <span className="price paid">${template.price}</span>
                  )}
                </div>
              </div>

              <div className="template-meta">
                <div className="rating-section">
                  {renderStars(template.rating)}
                  <span className="rating-value">{template.rating}</span>
                  <span className="rating-count">({template.reviews} reviews)</span>
                </div>

                <div className="stats-section">
                  <div className="stat">
                    <Download size={16} />
                    <span>{formatNumber(template.downloads)} downloads</span>
                  </div>
                  <div className="stat">
                    <Heart size={16} />
                    <span>{formatNumber(template.likes)} likes</span>
                  </div>
                  <div className="stat">
                    <Calendar size={16} />
                    <span>Updated {new Date(template.updatedAt).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <p className="template-description">
                {showFullDescription ? template.longDescription || template.description : template.description}
                {template.longDescription && template.longDescription !== template.description && (
                  <button 
                    className="read-more"
                    onClick={() => setShowFullDescription(!showFullDescription)}
                  >
                    {showFullDescription ? 'Show less' : 'Read more'}
                  </button>
                )}
              </p>

              <div className="template-tags">
                {template.tags.map(tag => (
                  <span key={tag} className="tag">
                    <Tag size={12} />
                    {tag}
                  </span>
                ))}
              </div>

              <div className="template-actions">
                <button className="action-button primary" onClick={handleDownload}>
                  <Download size={16} />
                  Download Template
                </button>
                {template.demoUrl && (
                  <button className="action-button secondary" onClick={handlePreview}>
                    <Eye size={16} />
                    Preview
                  </button>
                )}
                <button className="action-button secondary" onClick={() => setIsLiked(!isLiked)}>
                  <Heart size={16} className={isLiked ? 'liked' : ''} />
                  {isLiked ? 'Liked' : 'Like'}
                </button>
                <button className="action-button secondary" onClick={handleShare}>
                  {copied ? <Check size={16} /> : <Share2 size={16} />}
                  {copied ? 'Copied!' : 'Share'}
                </button>
              </div>
            </div>
          </div>

          <div className="details-tabs">
            <div className="tab-nav">
              <button
                className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                Overview
              </button>
              <button
                className={`tab-button ${activeTab === 'features' ? 'active' : ''}`}
                onClick={() => setActiveTab('features')}
              >
                Features
              </button>
              <button
                className={`tab-button ${activeTab === 'reviews' ? 'active' : ''}`}
                onClick={() => setActiveTab('reviews')}
              >
                Reviews ({template.reviews})
              </button>
              <button
                className={`tab-button ${activeTab === 'changelog' ? 'active' : ''}`}
                onClick={() => setActiveTab('changelog')}
              >
                Changelog
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'overview' && (
                <div className="overview-content">
                  <div className="overview-grid">
                    <div className="overview-section">
                      <h3>Template Information</h3>
                      <div className="info-grid">
                        <div className="info-item">
                          <Code size={16} />
                          <div>
                            <span className="label">Entities</span>
                            <span className="value">{template.entities}</span>
                          </div>
                        </div>
                        <div className="info-item">
                          <Database size={16} />
                          <div>
                            <span className="label">Relationships</span>
                            <span className="value">{template.relationships}</span>
                          </div>
                        </div>
                        <div className="info-item">
                          <GitBranch size={16} />
                          <div>
                            <span className="label">Version</span>
                            <span className="value">v{template.version}</span>
                          </div>
                        </div>
                        <div className="info-item">
                          <FileText size={16} />
                          <div>
                            <span className="label">License</span>
                            <span className="value">{template.license}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="overview-section">
                      <h3>Author</h3>
                      <div className="author-card">
                        {template.author.avatar ? (
                          <img
                            src={template.author.avatar}
                            alt={template.author.name}
                            className="author-avatar"
                          />
                        ) : (
                          <div className="author-avatar placeholder">
                            <User size={24} />
                          </div>
                        )}
                        <div className="author-info">
                          <div className="author-name">
                            {template.author.name}
                            {template.author.verified && (
                              <Shield size={14} className="verified-badge" />
                            )}
                          </div>
                          {template.author.bio && (
                            <p className="author-bio">{template.author.bio}</p>
                          )}
                          <div className="author-stats">
                            {template.author.templates && (
                              <span>{template.author.templates} templates</span>
                            )}
                            {template.author.followers && (
                              <span>{formatNumber(template.author.followers)} followers</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="compatibility-section">
                    <h3>Compatibility</h3>
                    <div className="compatibility-list">
                      {template.compatibility.map(item => (
                        <span key={item} className="compatibility-item">
                          <Box size={12} />
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>

                  {template.requirements && (
                    <div className="requirements-section">
                      <h3>Requirements</h3>
                      <ul className="requirements-list">
                        {template.requirements.map((req, index) => (
                          <li key={index}>{req}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'features' && (
                <div className="features-content">
                  <div className="features-grid">
                    {template.features.map(feature => (
                      <div key={feature} className="feature-item">
                        <CheckCircle size={16} />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'reviews' && (
                <div className="reviews-content">
                  <div className="reviews-summary">
                    <div className="rating-overview">
                      <div className="overall-rating">
                        <span className="rating-number">{template.rating}</span>
                        {renderStars(template.rating)}
                        <span className="rating-text">({template.reviews} reviews)</span>
                      </div>
                    </div>
                  </div>

                  <div className="reviews-list">
                    {reviews.map(review => (
                      <div key={review.id} className="review-item">
                        <div className="review-header">
                          <div className="reviewer-info">
                            {review.userAvatar ? (
                              <img src={review.userAvatar} alt={review.userName} className="reviewer-avatar" />
                            ) : (
                              <div className="reviewer-avatar placeholder">
                                <User size={16} />
                              </div>
                            )}
                            <div>
                              <div className="reviewer-name">{review.userName}</div>
                              <div className="review-date">
                                {new Date(review.date).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                          {renderStars(review.rating)}
                        </div>
                        <p className="review-comment">{review.comment}</p>
                        <div className="review-actions">
                          <button className="helpful-button">
                            Helpful ({review.helpful})
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'changelog' && (
                <div className="changelog-content">
                  {template.changelog ? (
                    template.changelog.map(entry => (
                      <div key={entry.version} className="changelog-entry">
                        <div className="changelog-header">
                          <span className="changelog-version">v{entry.version}</span>
                          <span className="changelog-date">
                            {new Date(entry.date).toLocaleDateString()}
                          </span>
                        </div>
                        <ul className="changelog-changes">
                          {entry.changes.map((change, index) => (
                            <li key={index}>{change}</li>
                          ))}
                        </ul>
                      </div>
                    ))
                  ) : (
                    <div className="no-changelog">
                      <Clock size={32} />
                      <p>No changelog available</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};