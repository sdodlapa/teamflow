import React, { useState, useRef, useCallback } from 'react';
import {
  Upload, X, FileText,
  Star, Tag, Globe, Shield, Zap, Package,
  Eye, Edit3, Save, ArrowLeft, Plus, Minus,
  Camera, Link, Code, Database, Settings, ChevronRight
} from 'lucide-react';
import './TemplateUpload.css';

interface TemplateUploadData {
  name: string;
  description: string;
  longDescription: string;
  category: string;
  tags: string[];
  price: number;
  isPremium: boolean;
  complexity: 'beginner' | 'intermediate' | 'advanced';
  version: string;
  license: string;
  previewImages: File[];
  templateFile?: File;
  demoUrl?: string;
  repositoryUrl?: string;
  features: string[];
  compatibility: string[];
  requirements: string[];
  documentation?: string;
  support?: {
    email?: string;
    discord?: string;
    github?: string;
  };
}

interface TemplateUploadProps {
  onClose: () => void;
  onSubmit: (data: TemplateUploadData) => void;
  isSubmitting?: boolean;
}

const CATEGORIES = [
  'E-commerce',
  'Blog & Content',
  'Portfolio',
  'Business',
  'Education',
  'Healthcare',
  'Finance',
  'Real Estate',
  'Technology',
  'Creative',
  'Other'
];

const LICENSES = [
  'MIT License',
  'Apache 2.0',
  'GPL-3.0',
  'BSD 3-Clause',
  'Creative Commons',
  'Proprietary',
  'Other'
];

const COMMON_TAGS = [
  'React', 'Vue', 'Angular', 'Node.js', 'TypeScript', 'JavaScript',
  'Python', 'Django', 'Flask', 'Express', 'MongoDB', 'PostgreSQL',
  'MySQL', 'Redis', 'Docker', 'AWS', 'Azure', 'GCP', 'Responsive',
  'Mobile', 'API', 'GraphQL', 'REST', 'Authentication', 'Payment'
];

const COMPATIBILITY_OPTIONS = [
  'React 18+', 'Vue 3+', 'Angular 15+', 'Node.js 16+', 'TypeScript 4.5+',
  'Next.js 13+', 'Nuxt 3+', 'Express 4+', 'FastAPI', 'Django 4+',
  'MongoDB 5+', 'PostgreSQL 13+', 'MySQL 8+', 'Redis 6+', 'Docker'
];

export const TemplateUpload: React.FC<TemplateUploadProps> = ({
  onClose,
  onSubmit,
  isSubmitting = false
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<TemplateUploadData>({
    name: '',
    description: '',
    longDescription: '',
    category: '',
    tags: [],
    price: 0,
    isPremium: false,
    complexity: 'beginner',
    version: '1.0.0',
    license: 'MIT License',
    previewImages: [],
    features: [''],
    compatibility: [],
    requirements: [''],
    support: {}
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [dragActive, setDragActive] = useState(false);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const templateFileInputRef = useRef<HTMLInputElement>(null);

  const totalSteps = 4;

  // Handle drag and drop for images
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files).filter(file =>
        file.type.startsWith('image/')
      );
      handleImageFiles(files);
    }
  }, []);

  const handleImageFiles = (files: File[]) => {
    const newImages = [...formData.previewImages, ...files].slice(0, 5);
    setFormData(prev => ({ ...prev, previewImages: newImages }));

    // Create preview URLs
    const urls = newImages.map(file => URL.createObjectURL(file));
    setPreviewUrls(urls);
  };

  const removeImage = (index: number) => {
    const newImages = formData.previewImages.filter((_, i) => i !== index);
    const newUrls = previewUrls.filter((_, i) => i !== index);
    
    // Revoke URL for removed image
    URL.revokeObjectURL(previewUrls[index]);
    
    setFormData(prev => ({ ...prev, previewImages: newImages }));
    setPreviewUrls(newUrls);
  };

  const updateFormData = (field: keyof TemplateUploadData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const addTag = (tag: string) => {
    if (tag && !formData.tags.includes(tag) && formData.tags.length < 10) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const addFeature = () => {
    setFormData(prev => ({
      ...prev,
      features: [...prev.features, '']
    }));
  };

  const updateFeature = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.map((feature, i) => i === index ? value : feature)
    }));
  };

  const removeFeature = (index: number) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.filter((_, i) => i !== index)
    }));
  };

  const addRequirement = () => {
    setFormData(prev => ({
      ...prev,
      requirements: [...prev.requirements, '']
    }));
  };

  const updateRequirement = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      requirements: prev.requirements.map((req, i) => i === index ? value : req)
    }));
  };

  const removeRequirement = (index: number) => {
    setFormData(prev => ({
      ...prev,
      requirements: prev.requirements.filter((_, i) => i !== index)
    }));
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.name) newErrors.name = 'Template name is required';
        if (!formData.description) newErrors.description = 'Description is required';
        if (!formData.category) newErrors.category = 'Category is required';
        if (formData.tags.length === 0) newErrors.tags = 'At least one tag is required';
        break;
      case 2:
        if (formData.previewImages.length === 0) {
          newErrors.previewImages = 'At least one preview image is required';
        }
        break;
      case 3:
        if (formData.features.some(f => !f.trim())) {
          newErrors.features = 'All feature fields must be filled';
        }
        if (formData.requirements.some(r => !r.trim())) {
          newErrors.requirements = 'All requirement fields must be filled';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = () => {
    if (validateStep(currentStep)) {
      const cleanedData = {
        ...formData,
        features: formData.features.filter(f => f.trim()),
        requirements: formData.requirements.filter(r => r.trim())
      };
      onSubmit(cleanedData);
    }
  };

  const getStepTitle = (step: number): string => {
    switch (step) {
      case 1: return 'Basic Information';
      case 2: return 'Media & Assets';
      case 3: return 'Features & Requirements';
      case 4: return 'Review & Submit';
      default: return '';
    }
  };

  const renderStep1 = () => (
    <div className="upload-step">
      <div className="step-content">
        <div className="form-group">
          <label className="form-label">
            <Package size={16} />
            Template Name *
          </label>
          <input
            type="text"
            className={`form-input ${errors.name ? 'error' : ''}`}
            value={formData.name}
            onChange={(e) => updateFormData('name', e.target.value)}
            placeholder="Enter template name"
          />
          {errors.name && <span className="error-message">{errors.name}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">
            <FileText size={16} />
            Short Description *
          </label>
          <textarea
            className={`form-textarea ${errors.description ? 'error' : ''}`}
            value={formData.description}
            onChange={(e) => updateFormData('description', e.target.value)}
            placeholder="Brief description of your template"
            rows={3}
          />
          {errors.description && <span className="error-message">{errors.description}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">
            <Edit3 size={16} />
            Detailed Description
          </label>
          <textarea
            className="form-textarea"
            value={formData.longDescription}
            onChange={(e) => updateFormData('longDescription', e.target.value)}
            placeholder="Detailed description with features, use cases, and benefits"
            rows={6}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">
              <Tag size={16} />
              Category *
            </label>
            <select
              className={`form-select ${errors.category ? 'error' : ''}`}
              value={formData.category}
              onChange={(e) => updateFormData('category', e.target.value)}
            >
              <option value="">Select category</option>
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            {errors.category && <span className="error-message">{errors.category}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">
              <Zap size={16} />
              Complexity
            </label>
            <select
              className="form-select"
              value={formData.complexity}
              onChange={(e) => updateFormData('complexity', e.target.value as any)}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">
            <Tag size={16} />
            Tags * (Select up to 10)
          </label>
          <div className="tags-section">
            <div className="common-tags">
              {COMMON_TAGS.map(tag => (
                <button
                  key={tag}
                  type="button"
                  className={`tag-button ${formData.tags.includes(tag) ? 'selected' : ''}`}
                  onClick={() => formData.tags.includes(tag) ? removeTag(tag) : addTag(tag)}
                  disabled={!formData.tags.includes(tag) && formData.tags.length >= 10}
                >
                  {tag}
                </button>
              ))}
            </div>
            
            <div className="selected-tags">
              {formData.tags.map(tag => (
                <span key={tag} className="selected-tag">
                  {tag}
                  <button type="button" onClick={() => removeTag(tag)}>
                    <X size={12} />
                  </button>
                </span>
              ))}
            </div>
          </div>
          {errors.tags && <span className="error-message">{errors.tags}</span>}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">
              <Code size={16} />
              Version
            </label>
            <input
              type="text"
              className="form-input"
              value={formData.version}
              onChange={(e) => updateFormData('version', e.target.value)}
              placeholder="1.0.0"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <Shield size={16} />
              License
            </label>
            <select
              className="form-select"
              value={formData.license}
              onChange={(e) => updateFormData('license', e.target.value)}
            >
              {LICENSES.map(license => (
                <option key={license} value={license}>{license}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="upload-step">
      <div className="step-content">
        <div className="form-group">
          <label className="form-label">
            <Camera size={16} />
            Preview Images * (Up to 5 images)
          </label>
          
          <div
            className={`image-upload-zone ${dragActive ? 'drag-active' : ''} ${errors.previewImages ? 'error' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={(e) => {
                if (e.target.files) {
                  handleImageFiles(Array.from(e.target.files));
                }
              }}
              style={{ display: 'none' }}
            />
            
            <div className="upload-content">
              <Upload size={32} />
              <p>Drag & drop images here or click to browse</p>
              <span className="upload-hint">PNG, JPG, WEBP up to 10MB each</span>
            </div>
            
            <button
              type="button"
              className="upload-button"
              onClick={() => fileInputRef.current?.click()}
            >
              Choose Files
            </button>
          </div>
          
          {errors.previewImages && <span className="error-message">{errors.previewImages}</span>}

          {previewUrls.length > 0 && (
            <div className="image-previews">
              {previewUrls.map((url, index) => (
                <div key={index} className="image-preview">
                  <img src={url} alt={`Preview ${index + 1}`} />
                  <button
                    type="button"
                    className="remove-image"
                    onClick={() => removeImage(index)}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">
            <Upload size={16} />
            Template File (Optional)
          </label>
          <input
            ref={templateFileInputRef}
            type="file"
            accept=".zip,.json,.xml"
            onChange={(e) => {
              if (e.target.files?.[0]) {
                updateFormData('templateFile', e.target.files[0]);
              }
            }}
            className="form-file"
          />
          <span className="form-hint">Upload your template file (.zip, .json, .xml)</span>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">
              <Eye size={16} />
              Demo URL (Optional)
            </label>
            <input
              type="url"
              className="form-input"
              value={formData.demoUrl || ''}
              onChange={(e) => updateFormData('demoUrl', e.target.value)}
              placeholder="https://demo.example.com"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <Link size={16} />
              Repository URL (Optional)
            </label>
            <input
              type="url"
              className="form-input"
              value={formData.repositoryUrl || ''}
              onChange={(e) => updateFormData('repositoryUrl', e.target.value)}
              placeholder="https://github.com/username/repo"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="upload-step">
      <div className="step-content">
        <div className="form-group">
          <label className="form-label">
            <Star size={16} />
            Key Features
          </label>
          <div className="dynamic-list">
            {formData.features.map((feature, index) => (
              <div key={index} className="dynamic-item">
                <input
                  type="text"
                  className="form-input"
                  value={feature}
                  onChange={(e) => updateFeature(index, e.target.value)}
                  placeholder="Describe a key feature"
                />
                <button
                  type="button"
                  className="remove-button"
                  onClick={() => removeFeature(index)}
                  disabled={formData.features.length === 1}
                >
                  <Minus size={16} />
                </button>
              </div>
            ))}
            <button type="button" className="add-button" onClick={addFeature}>
              <Plus size={16} />
              Add Feature
            </button>
          </div>
          {errors.features && <span className="error-message">{errors.features}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">
            <Database size={16} />
            Compatibility
          </label>
          <div className="checkbox-grid">
            {COMPATIBILITY_OPTIONS.map(option => (
              <label key={option} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={formData.compatibility.includes(option)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      updateFormData('compatibility', [...formData.compatibility, option]);
                    } else {
                      updateFormData('compatibility', formData.compatibility.filter(c => c !== option));
                    }
                  }}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">
            <Settings size={16} />
            Requirements
          </label>
          <div className="dynamic-list">
            {formData.requirements.map((requirement, index) => (
              <div key={index} className="dynamic-item">
                <input
                  type="text"
                  className="form-input"
                  value={requirement}
                  onChange={(e) => updateRequirement(index, e.target.value)}
                  placeholder="System or dependency requirement"
                />
                <button
                  type="button"
                  className="remove-button"
                  onClick={() => removeRequirement(index)}
                  disabled={formData.requirements.length === 1}
                >
                  <Minus size={16} />
                </button>
              </div>
            ))}
            <button type="button" className="add-button" onClick={addRequirement}>
              <Plus size={16} />
              Add Requirement
            </button>
          </div>
          {errors.requirements && <span className="error-message">{errors.requirements}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">
            <Globe size={16} />
            Documentation (Optional)
          </label>
          <textarea
            className="form-textarea"
            value={formData.documentation || ''}
            onChange={(e) => updateFormData('documentation', e.target.value)}
            placeholder="Installation instructions, usage guide, API documentation..."
            rows={6}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Support Contact (Optional)</label>
          <div className="form-row">
            <div className="form-group">
              <input
                type="email"
                className="form-input"
                value={formData.support?.email || ''}
                onChange={(e) => updateFormData('support', { ...formData.support, email: e.target.value })}
                placeholder="support@example.com"
              />
            </div>
            <div className="form-group">
              <input
                type="text"
                className="form-input"
                value={formData.support?.discord || ''}
                onChange={(e) => updateFormData('support', { ...formData.support, discord: e.target.value })}
                placeholder="Discord server invite"
              />
            </div>
            <div className="form-group">
              <input
                type="url"
                className="form-input"
                value={formData.support?.github || ''}
                onChange={(e) => updateFormData('support', { ...formData.support, github: e.target.value })}
                placeholder="GitHub issues URL"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="upload-step">
      <div className="step-content">
        <div className="review-section">
          <h3>Template Information</h3>
          <div className="review-grid">
            <div className="review-item">
              <span className="review-label">Name:</span>
              <span className="review-value">{formData.name}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Category:</span>
              <span className="review-value">{formData.category}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Complexity:</span>
              <span className="review-value">{formData.complexity}</span>
            </div>
            <div className="review-item">
              <span className="review-label">Version:</span>
              <span className="review-value">{formData.version}</span>
            </div>
            <div className="review-item">
              <span className="review-label">License:</span>
              <span className="review-value">{formData.license}</span>
            </div>
          </div>
        </div>

        <div className="review-section">
          <h3>Description</h3>
          <p className="review-description">{formData.description}</p>
        </div>

        <div className="review-section">
          <h3>Tags ({formData.tags.length})</h3>
          <div className="review-tags">
            {formData.tags.map(tag => (
              <span key={tag} className="review-tag">{tag}</span>
            ))}
          </div>
        </div>

        <div className="review-section">
          <h3>Preview Images ({formData.previewImages.length})</h3>
          <div className="review-images">
            {previewUrls.map((url, index) => (
              <img key={index} src={url} alt={`Preview ${index + 1}`} className="review-image" />
            ))}
          </div>
        </div>

        <div className="review-section">
          <h3>Features ({formData.features.filter(f => f.trim()).length})</h3>
          <ul className="review-list">
            {formData.features.filter(f => f.trim()).map((feature, index) => (
              <li key={index}>{feature}</li>
            ))}
          </ul>
        </div>

        {formData.compatibility.length > 0 && (
          <div className="review-section">
            <h3>Compatibility</h3>
            <div className="review-tags">
              {formData.compatibility.map(comp => (
                <span key={comp} className="review-tag">{comp}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="template-upload-overlay">
      <div className="template-upload">
        <div className="upload-header">
          <h2>Share Your Template</h2>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="upload-progress">
          <div className="progress-steps">
            {Array.from({ length: totalSteps }, (_, i) => i + 1).map(step => (
              <div key={step} className={`progress-step ${step <= currentStep ? 'active' : ''}`}>
                <div className="step-number">{step}</div>
                <div className="step-title">{getStepTitle(step)}</div>
              </div>
            ))}
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        <div className="upload-body">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}
        </div>

        <div className="upload-footer">
          <div className="footer-actions">
            {currentStep > 1 && (
              <button className="action-button secondary" onClick={handlePrevious}>
                <ArrowLeft size={16} />
                Previous
              </button>
            )}
            
            {currentStep < totalSteps ? (
              <button className="action-button primary" onClick={handleNext}>
                Next
                <ChevronRight size={16} />
              </button>
            ) : (
              <button
                className="action-button primary"
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="spinner" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Save size={16} />
                    Submit Template
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};