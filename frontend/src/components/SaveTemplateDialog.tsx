/**
 * Save Template Dialog - Day 17 Implementation
 * Dialog component for saving templates created in the builder
 */

import React, { useState } from 'react';
import { X, Save, AlertCircle, Tag } from 'lucide-react';
import uiTemplateService, { SaveUITemplateRequest } from '../services/uiTemplateService';

interface SaveTemplateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (template: SaveUITemplateRequest) => void;
  components: any[];
  initialData?: Partial<SaveUITemplateRequest>;
}

const SaveTemplateDialog: React.FC<SaveTemplateDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  components,
  initialData
}) => {
  const [formData, setFormData] = useState<SaveUITemplateRequest>({
    name: initialData?.name || '',
    description: initialData?.description || '',
    category: initialData?.category || 'general',
    tags: initialData?.tags || [],
    components: components,
    is_public: initialData?.is_public || false
  });

  const [tagInput, setTagInput] = useState('');
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setSaving] = useState(false);

  const categories = [
    { value: 'general', label: 'General' },
    { value: 'forms', label: 'Forms' },
    { value: 'dashboards', label: 'Dashboards' },
    { value: 'layouts', label: 'Layouts' },
    { value: 'components', label: 'Components' },
    { value: 'landing_pages', label: 'Landing Pages' },
    { value: 'admin', label: 'Admin Panels' },
    { value: 'ecommerce', label: 'E-commerce' }
  ];

  const handleInputChange = (field: keyof SaveUITemplateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear errors when user starts typing
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  const addTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase();
    if (trimmedTag && !formData.tags.includes(trimmedTag)) {
      handleInputChange('tags', [...formData.tags, trimmedTag]);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    handleInputChange('tags', formData.tags.filter(tag => tag !== tagToRemove));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  const validateForm = (): boolean => {
    const validation = uiTemplateService.validateUITemplate(formData);
    setErrors(validation.errors);
    return validation.isValid;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setSaving(true);
    try {
      const templateToSave = {
        ...formData,
        components: components // Use the latest components from props
      };
      
      onSave(templateToSave);
      onClose();
    } catch (error) {
      console.error('Failed to save template:', error);
      setErrors(['Failed to save template. Please try again.']);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Save Template</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* Error Display */}
          {errors.length > 0 && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center mb-2">
                <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
                <span className="text-sm font-medium text-red-800">Please fix the following errors:</span>
              </div>
              <ul className="list-disc list-inside space-y-1">
                {errors.map((error, index) => (
                  <li key={index} className="text-sm text-red-700">{error}</li>
                ))}
              </ul>
            </div>
          )}

          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="space-y-4">
            {/* Template Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter template name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                maxLength={100}
              />
              <p className="text-xs text-gray-500 mt-1">{formData.name.length}/100 characters</p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe your template"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
                maxLength={500}
              />
              <p className="text-xs text-gray-500 mt-1">{(formData.description || '').length}/500 characters</p>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {categories.map(category => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {formData.tags.map(tag => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-blue-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Add tags (press Enter)"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={addTag}
                  className="px-4 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-lg hover:bg-gray-200 transition-colors"
                >
                  Add
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Tags help others find your template. {formData.tags.length}/10 tags
              </p>
            </div>

            {/* Public/Private Toggle */}
            <div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={formData.is_public}
                  onChange={(e) => handleInputChange('is_public', e.target.checked)}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <label htmlFor="is_public" className="ml-2 text-sm text-gray-700">
                  Make this template public
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Public templates can be used by other users in your organization
              </p>
            </div>

            {/* Template Summary */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Template Summary</h4>
              <div className="text-xs text-gray-600 space-y-1">
                <div>Components: {components.length}</div>
                <div>Category: {categories.find(c => c.value === formData.category)?.label}</div>
                <div>Tags: {formData.tags.length}</div>
                <div>Visibility: {formData.is_public ? 'Public' : 'Private'}</div>
              </div>
            </div>
          </form>

          {/* Actions */}
          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Saving...' : 'Save Template'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SaveTemplateDialog;