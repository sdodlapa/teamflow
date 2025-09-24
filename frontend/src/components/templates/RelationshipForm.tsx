import React, { useState, useEffect } from 'react';
import { X, AlertCircle, ArrowRight, ArrowLeftRight, ArrowUpDown } from 'lucide-react';
import { Entity, Relationship, RelationshipType } from '../../types/template';

interface RelationshipFormProps {
  relationship: Relationship | null;
  entities: Entity[];
  existingRelationships: Relationship[];
  onSave: (relationship: Omit<Relationship, 'id'>) => void;
  onCancel: () => void;
}

interface RelationshipTypeOption {
  value: RelationshipType;
  label: string;
  description: string;
  icon: React.ReactNode;
  example: string;
}

const RelationshipForm: React.FC<RelationshipFormProps> = ({
  relationship,
  entities,
  existingRelationships,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'one_to_many' as RelationshipType,
    sourceEntityId: '',
    targetEntityId: '',
    foreignKey: '',
    backPopulates: '',
    cascade: false,
    description: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [currentStep, setCurrentStep] = useState(1);

  const relationshipTypes: RelationshipTypeOption[] = [
    {
      value: 'one_to_one',
      label: 'One-to-One',
      description: 'Each record in the first entity relates to exactly one record in the second entity',
      icon: <ArrowRight className="h-5 w-5" />,
      example: 'User ↔ Profile',
    },
    {
      value: 'one_to_many',
      label: 'One-to-Many',
      description: 'Each record in the first entity can relate to multiple records in the second entity',
      icon: <ArrowUpDown className="h-5 w-5" />,
      example: 'User → Posts',
    },
    {
      value: 'many_to_one',
      label: 'Many-to-One',
      description: 'Multiple records in the first entity relate to one record in the second entity',
      icon: <ArrowUpDown className="h-5 w-5 rotate-180" />,
      example: 'Posts → Category',
    },
    {
      value: 'many_to_many',
      label: 'Many-to-Many',
      description: 'Records in both entities can relate to multiple records in the other entity',
      icon: <ArrowLeftRight className="h-5 w-5" />,
      example: 'Users ↔ Roles',
    },
  ];

  useEffect(() => {
    if (relationship) {
      setFormData({
        name: relationship.name,
        type: relationship.type,
        sourceEntityId: relationship.sourceEntityId,
        targetEntityId: relationship.targetEntityId,
        foreignKey: relationship.foreignKey || '',
        backPopulates: relationship.backPopulates || '',
        cascade: relationship.cascade || false,
        description: relationship.description || '',
      });
    } else {
      // Reset form for new relationship
      setFormData({
        name: '',
        type: 'one_to_many',
        sourceEntityId: '',
        targetEntityId: '',
        foreignKey: '',
        backPopulates: '',
        cascade: false,
        description: '',
      });
    }
    setErrors({});
    setCurrentStep(1);
  }, [relationship]);

  // Auto-generate relationship name
  useEffect(() => {
    if (formData.sourceEntityId && formData.targetEntityId && !relationship) {
      const sourceEntity = entities.find(e => e.id === formData.sourceEntityId);
      const targetEntity = entities.find(e => e.id === formData.targetEntityId);
      
      if (sourceEntity && targetEntity) {
        let relationshipName = '';
        switch (formData.type) {
          case 'one_to_one':
            relationshipName = `${sourceEntity.name.toLowerCase()}_${targetEntity.name.toLowerCase()}`;
            break;
          case 'one_to_many':
            relationshipName = `${sourceEntity.name.toLowerCase()}_${targetEntity.name.toLowerCase()}s`;
            break;
          case 'many_to_one':
            relationshipName = `${sourceEntity.name.toLowerCase()}s_${targetEntity.name.toLowerCase()}`;
            break;
          case 'many_to_many':
            relationshipName = `${sourceEntity.name.toLowerCase()}_${targetEntity.name.toLowerCase()}_associations`;
            break;
        }
        setFormData(prev => ({ ...prev, name: relationshipName }));
      }
    }
  }, [formData.sourceEntityId, formData.targetEntityId, formData.type, entities, relationship]);

  // Auto-generate foreign key
  useEffect(() => {
    if (formData.targetEntityId && !relationship) {
      const targetEntity = entities.find(e => e.id === formData.targetEntityId);
      if (targetEntity) {
        const foreignKey = `${targetEntity.name.toLowerCase()}_${targetEntity.primaryKey || 'id'}`;
        setFormData(prev => ({ ...prev, foreignKey }));
      }
    }
  }, [formData.targetEntityId, entities, relationship]);

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!formData.sourceEntityId) {
        newErrors.sourceEntityId = 'Source entity is required';
      }
      if (!formData.targetEntityId) {
        newErrors.targetEntityId = 'Target entity is required';
      }
      if (formData.sourceEntityId && formData.targetEntityId && formData.sourceEntityId === formData.targetEntityId) {
        newErrors.targetEntityId = 'Source and target entities must be different';
      }

      // Check for duplicate relationships
      if (formData.sourceEntityId && formData.targetEntityId) {
        const isDuplicate = existingRelationships
          .filter(rel => relationship ? rel.id !== relationship.id : true)
          .some(rel => 
            rel.sourceEntityId === formData.sourceEntityId && 
            rel.targetEntityId === formData.targetEntityId
          );
        
        if (isDuplicate) {
          newErrors.targetEntityId = 'A relationship between these entities already exists';
        }
      }
    }

    if (step === 2) {
      if (!formData.name.trim()) {
        newErrors.name = 'Relationship name is required';
      } else if (!/^[a-z][a-z0-9_]*$/.test(formData.name)) {
        newErrors.name = 'Name must be lowercase, start with a letter, and contain only letters, numbers, and underscores';
      }

      if (!formData.foreignKey.trim()) {
        newErrors.foreignKey = 'Foreign key field name is required';
      } else if (!/^[a-z][a-z0-9_]*$/.test(formData.foreignKey)) {
        newErrors.foreignKey = 'Foreign key must be a valid field name';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSave = () => {
    if (validateStep(currentStep)) {
      const relationshipData: Omit<Relationship, 'id'> = {
        name: formData.name.trim(),
        type: formData.type,
        sourceEntityId: formData.sourceEntityId,
        targetEntityId: formData.targetEntityId,
        foreignKey: formData.foreignKey.trim() || undefined,
        backPopulates: formData.backPopulates.trim() || undefined,
        cascade: formData.cascade,
        description: formData.description.trim() || undefined,
      };
      onSave(relationshipData);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const getEntityName = (entityId: string) => {
    const entity = entities.find(e => e.id === entityId);
    return entity?.name || 'Unknown Entity';
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-4">Select Entities</h4>
        
        {/* Relationship Type */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Relationship Type
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {relationshipTypes.map((type) => (
              <label key={type.value} className="relative">
                <input
                  type="radio"
                  name="type"
                  value={type.value}
                  checked={formData.type === type.value}
                  onChange={(e) => handleChange('type', e.target.value)}
                  className="sr-only"
                />
                <div className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                  formData.type === type.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}>
                  <div className="flex items-center mb-2">
                    {type.icon}
                    <span className="ml-2 text-sm font-medium">{type.label}</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-1">{type.description}</p>
                  <p className="text-xs font-mono text-blue-600">{type.example}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Source Entity */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Source Entity *
          </label>
          <select
            value={formData.sourceEntityId}
            onChange={(e) => handleChange('sourceEntityId', e.target.value)}
            className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
              errors.sourceEntityId ? 'border-red-300' : 'border-gray-300'
            }`}
          >
            <option value="">Select source entity...</option>
            {entities.map((entity) => (
              <option key={entity.id} value={entity.id}>
                {entity.name} ({entity.type})
              </option>
            ))}
          </select>
          {errors.sourceEntityId && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {errors.sourceEntityId}
            </p>
          )}
        </div>

        {/* Target Entity */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Entity *
          </label>
          <select
            value={formData.targetEntityId}
            onChange={(e) => handleChange('targetEntityId', e.target.value)}
            className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
              errors.targetEntityId ? 'border-red-300' : 'border-gray-300'
            }`}
          >
            <option value="">Select target entity...</option>
            {entities
              .filter(entity => entity.id !== formData.sourceEntityId)
              .map((entity) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name} ({entity.type})
                </option>
              ))}
          </select>
          {errors.targetEntityId && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {errors.targetEntityId}
            </p>
          )}
        </div>

        {/* Relationship Preview */}
        {formData.sourceEntityId && formData.targetEntityId && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 className="text-sm font-medium text-blue-900 mb-2">Relationship Preview</h5>
            <div className="flex items-center justify-center space-x-4 text-sm text-blue-800">
              <div className="bg-white rounded px-3 py-1 border border-blue-200">
                {getEntityName(formData.sourceEntityId)}
              </div>
              <div className="flex items-center">
                {relationshipTypes.find(t => t.value === formData.type)?.icon}
              </div>
              <div className="bg-white rounded px-3 py-1 border border-blue-200">
                {getEntityName(formData.targetEntityId)}
              </div>
            </div>
            <p className="text-xs text-blue-600 mt-2 text-center">
              {relationshipTypes.find(t => t.value === formData.type)?.label}
            </p>
          </div>
        )}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-4">Relationship Configuration</h4>
        
        {/* Relationship Name */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Relationship Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., user_posts, product_categories"
            className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
              errors.name ? 'border-red-300' : 'border-gray-300'
            }`}
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {errors.name}
            </p>
          )}
          <p className="text-xs text-gray-500 mt-1">
            Used as the database relationship name
          </p>
        </div>

        {/* Foreign Key */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Foreign Key Field *
          </label>
          <input
            type="text"
            value={formData.foreignKey}
            onChange={(e) => handleChange('foreignKey', e.target.value)}
            placeholder="e.g., user_id, category_id"
            className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
              errors.foreignKey ? 'border-red-300' : 'border-gray-300'
            }`}
          />
          {errors.foreignKey && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="h-4 w-4 mr-1" />
              {errors.foreignKey}
            </p>
          )}
          <p className="text-xs text-gray-500 mt-1">
            The field that will store the reference to the related entity
          </p>
        </div>

        {/* Back Populates */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Back Populates (Optional)
          </label>
          <input
            type="text"
            value={formData.backPopulates}
            onChange={(e) => handleChange('backPopulates', e.target.value)}
            placeholder="e.g., posts, user"
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">
            The field name on the related entity that references back to this entity
          </p>
        </div>

        {/* Description */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={3}
            placeholder="Describe the purpose of this relationship..."
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Cascade Delete */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="cascade"
            checked={formData.cascade}
            onChange={(e) => handleChange('cascade', e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="cascade" className="ml-2 text-sm text-gray-700">
            Enable cascade delete
          </label>
        </div>
        <p className="text-xs text-gray-500 mt-1 ml-6">
          When the parent entity is deleted, automatically delete related entities
        </p>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {relationship ? 'Edit Relationship' : 'Create New Relationship'}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              {[1, 2].map((step) => (
                <div
                  key={step}
                  className={`w-8 h-2 rounded-full ${
                    step === currentStep
                      ? 'bg-blue-600'
                      : step < currentStep
                      ? 'bg-green-600'
                      : 'bg-gray-200'
                  }`}
                />
              ))}
              <span className="text-sm text-gray-500 ml-2">
                Step {currentStep} of 2
              </span>
            </div>
          </div>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-500">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            
            {currentStep < 2 ? (
              <button
                onClick={handleNext}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSave}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                {relationship ? 'Update Relationship' : 'Create Relationship'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RelationshipForm;