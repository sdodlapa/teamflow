import React, { useState, useCallback } from 'react';
import { Settings, Users, BarChart3 } from 'lucide-react';
import { SimpleDomainConfigForm } from '../components/TemplateBuilder/SimpleDomainConfigForm';
import EntityManager from '../components/templates/EntityManager';
import RelationshipDesigner from '../components/templates/RelationshipDesigner';
import ConfigurationPreview from '../components/template-builder/ConfigurationPreview';
import TemplateManager from '../components/template-builder/TemplateManager';
import CodeGenerationDashboard from '../components/template-builder/CodeGenerationDashboard';
import AdvancedTemplateFeatures from '../components/template-builder/AdvancedTemplateFeatures';
import CollaborationTools from '../components/template-builder/CollaborationTools';
import TemplateAnalytics from '../components/template-builder/TemplateAnalytics';
import TemplateMarketplace from '../components/template-builder/TemplateMarketplace';
import RealTimeCollaborationPanel from '../components/RealTimeCollaborationPanel';
import RealTimeStatus from '../components/RealTimeStatus';
import { Entity, Field, Relationship } from '../types/template';
import { CollaborativeUser } from '../hooks/useRealTimeCollaboration';
import { useRealTimeCollaboration } from '../hooks/useRealTimeCollaboration';

interface DomainConfig {
  name: string;
  title: string;
  description: string;
  domain_type: string;
  version: string;
  logo: string;
  color_scheme: string;
  theme: string;
}

export const TemplateBuilderPage: React.FC = () => {
  const collaboration = useRealTimeCollaboration();
  const [currentConfig, setCurrentConfig] = useState<DomainConfig | null>(null);
  const [isValid, setIsValid] = useState(false);
  const [step, setStep] = useState(1);
  
  // Entity management state
  const [entities, setEntities] = useState<Entity[]>([]);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  
  // Template manager state
  const [showTemplateManager, setShowTemplateManager] = useState(false);
  
  // Code generation dashboard state
  const [showCodeGenDashboard, setShowCodeGenDashboard] = useState(false);
  
  // Template marketplace state
  const [showMarketplace, setShowMarketplace] = useState(false);
  
  // Advanced template features state
  const [showAdvancedFeatures, setShowAdvancedFeatures] = useState(false);
  
  // Collaboration tools state
  const [showCollaborationTools, setShowCollaborationTools] = useState(false);
  
  // Template analytics state
  const [showTemplateAnalytics, setShowTemplateAnalytics] = useState(false);
  
    // State management
  
  // Handle collaborative user changes
  const handleUserPresenceChange = useCallback((users: CollaborativeUser[]) => {
    console.log('User presence changed:', users);
    // Update local state with collaboration.collaborativeUsers if needed
  }, []);

  // Handle real-time template updates
  const handleTemplateUpdate = useCallback((templateId: string, data: any) => {
    console.log('Template updated in real-time:', templateId, data);
    // Apply the updates to local state
    if (data.entities) {
      setEntities(data.entities);
    }
    if (data.relationships) {
      setRelationships(data.relationships);
    }
    if (data.config) {
      setCurrentConfig(data.config);
    }
  }, []);

  const handleConfigChange = (config: DomainConfig) => {
    setCurrentConfig(config);
  };

  const handleValidationChange = (valid: boolean) => {
    setIsValid(valid);
  };

  const handleEntitiesChange = (newEntities: Entity[]) => {
    setEntities(newEntities);
  };

  const handleFieldsChange = (entityId: string, fields: Field[]) => {
    setEntities(prev => 
      prev.map(entity => 
        entity.id === entityId 
          ? { ...entity, fields } 
          : entity
      )
    );
  };

  const handleRelationshipsChange = (newRelationships: Relationship[]) => {
    setRelationships(newRelationships);
  };

  const nextStep = () => {
    if (step === 1 && isValid) {
      setStep(step + 1);
    } else if (step === 2 && entities.length > 0) {
      setStep(step + 1);
    } else if (step >= 3) {
      setStep(step + 1);
    }
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  const handleGenerateCode = async () => {
    if (!currentConfig) return;
    
    console.log('Generating code for config:', currentConfig);
    console.log('Entities:', entities);
    console.log('Relationships:', relationships);
    
    // Open the Code Generation Dashboard
    setShowCodeGenDashboard(true);
  };

  const handleSaveTemplate = async (templateData: any) => {
    console.log('Saving template:', templateData);
    // TODO: Implement actual template saving to backend
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    alert('Template saved successfully!');
  };

  const handleOpenTemplateManager = () => {
    setShowTemplateManager(true);
  };

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <div>
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Create New Template
              </h1>
              <p className="text-gray-600">
                Step 1 of 5: Configure your domain template
              </p>
              
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-blue-900">Need inspiration?</h3>
                    <p className="text-sm text-blue-700">Browse our marketplace of professional templates</p>
                  </div>
                  <button
                    onClick={() => setShowMarketplace(true)}
                    className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors text-sm"
                  >
                    🏪 Browse Marketplace
                  </button>
                </div>
              </div>
            </div>
            
            <SimpleDomainConfigForm
              onConfigChange={handleConfigChange}
              onValidationChange={handleValidationChange}
            />
          </div>
        );
      
      case 2:
        return (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Entity Management
              </h1>
                            <p className="text-gray-600">
                Step 2 of 5: Define your domain entities and their properties
              </p>
            </div>
            
            {currentConfig && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-blue-900 mb-2">Current Domain:</h3>
                <div className="text-sm text-blue-800">
                  <p><strong>{currentConfig.title}</strong> ({currentConfig.domain_type})</p>
                  <p>{currentConfig.description}</p>
                </div>
              </div>
            )}
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <EntityManager
                entities={entities}
                onEntitiesChange={handleEntitiesChange}
                onFieldsChange={handleFieldsChange}
                relationships={relationships}
                onRelationshipsChange={handleRelationshipsChange}
              />
            </div>
          </div>
        );
      
      case 3:
        return (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Relationship Designer
              </h1>
              <p className="text-gray-600">
                Step 3 of 5: Define how your entities connect and relate to each other
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <RelationshipDesigner
                entities={entities}
                relationships={relationships}
                onRelationshipsChange={handleRelationshipsChange}
              />
            </div>
          </div>
        );
      
      case 4:
        return (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  Configuration Preview
                </h1>
                <p className="text-gray-600">
                  Step 4 of 5: Review your template configuration before generating code
                </p>
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowAdvancedFeatures(true)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <Settings className="h-4 w-4" />
                  <span>Advanced Features</span>
                </button>
                
                <button
                  onClick={() => setShowCollaborationTools(true)}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <Users className="h-4 w-4" />
                  <span>Collaborate</span>
                </button>
                
                <button
                  onClick={() => setShowTemplateAnalytics(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>Analytics</span>
                </button>
              </div>
            </div>
            
            {currentConfig && (
              <ConfigurationPreview
                domainConfig={currentConfig}
                entities={entities}
                relationships={relationships}
                onExport={(format) => {
                  console.log(`Exporting as ${format}`);
                  // TODO: Implement export functionality
                }}
                onShare={() => {
                  console.log('Sharing template');
                  // TODO: Implement share functionality
                }}
                onValidate={() => {
                  console.log('Re-validating template');
                  // TODO: Implement validation functionality
                }}
              />
            )}
          </div>
        );
      
      case 5:
        return (
          <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Step 5: Generate & Deploy
            </h2>
            <p className="text-gray-600 mb-6">
              Review your configuration and generate the code
            </p>
            
            {currentConfig && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-green-900 mb-4">Final Configuration Review:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-green-800">
                  <div>
                    <p><strong>Domain Name:</strong> {currentConfig.name}</p>
                    <p><strong>Title:</strong> {currentConfig.title}</p>
                    <p><strong>Type:</strong> {currentConfig.domain_type}</p>
                    <p><strong>Version:</strong> {currentConfig.version}</p>
                  </div>
                  <div>
                    <p><strong>Logo:</strong> {currentConfig.logo}</p>
                    <p><strong>Color Scheme:</strong> {currentConfig.color_scheme}</p>
                    <p><strong>Theme:</strong> {currentConfig.theme}</p>
                    <p><strong>Description:</strong> {currentConfig.description.substring(0, 50)}...</p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="text-center space-y-4">
              <div className="flex justify-center space-x-4">
                <button
                  onClick={handleOpenTemplateManager}
                  className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center space-x-2"
                >
                  <span>💾</span>
                  <span>Save Template</span>
                </button>
                
                <button
                  onClick={handleGenerateCode}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center space-x-2"
                >
                  <span>🚀</span>
                  <span>Generate Code</span>
                </button>
              </div>
              
              <p className="text-sm text-gray-500">
                Save your template for reuse or generate the complete application code
              </p>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Progress Bar */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-4">
            {[1, 2, 3, 4, 5].map((stepNumber) => (
              <div
                key={stepNumber}
                className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold ${
                  stepNumber <= step
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {stepNumber}
              </div>
            ))}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / 5) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        {renderStepContent()}

        {/* Navigation */}
        <div className="max-w-4xl mx-auto mt-8 flex justify-between">
          <button
            onClick={prevStep}
            disabled={step === 1}
            className={`px-6 py-2 rounded-md font-medium ${
              step === 1
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            Previous
          </button>
          
          <div className="text-sm text-gray-500 flex items-center">
            Step {step} of 5
          </div>
          
          {step < 5 ? (
            <button
              onClick={nextStep}
              disabled={
                (step === 1 && !isValid) ||
                (step === 2 && entities.length === 0)
              }
              className={`px-6 py-2 rounded-md font-medium ${
                (step === 1 && !isValid) || (step === 2 && entities.length === 0)
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              Next
            </button>
          ) : (
            <button
              onClick={() => setStep(1)}
              className="px-6 py-2 rounded-md font-medium bg-green-600 text-white hover:bg-green-700"
            >
              Start Over
            </button>
          )}
        </div>
      </div>

      {/* Template Manager Modal */}
      {currentConfig && (
        <TemplateManager
          domainConfig={currentConfig}
          entities={entities}
          relationships={relationships}
          isVisible={showTemplateManager}
          onClose={() => setShowTemplateManager(false)}
          onSave={handleSaveTemplate}
        />
      )}

      {/* Code Generation Dashboard Modal */}
      {currentConfig && showCodeGenDashboard && (
        <CodeGenerationDashboard
          domainConfig={currentConfig}
          entities={entities}
          relationships={relationships}
          onClose={() => setShowCodeGenDashboard(false)}
        />
      )}

      {/* Template Marketplace Modal */}
      {showMarketplace && (
        <TemplateMarketplace
          onImportTemplate={(template) => {
            console.log('Importing template from marketplace:', template);
            // This would populate the form with the imported template data
            alert(`Template "${template.title}" imported! This would populate the form with template data.`);
            setShowMarketplace(false);
          }}
          onClose={() => setShowMarketplace(false)}
        />
      )}

      {/* Advanced Template Features Modal */}
      {showAdvancedFeatures && currentConfig && (
        <AdvancedTemplateFeatures
          domainConfig={currentConfig}
          entities={entities}
          relationships={relationships}
          onClose={() => setShowAdvancedFeatures(false)}
        />
      )}

      {/* Collaboration Tools Modal */}
      {showCollaborationTools && currentConfig && (
        <CollaborationTools
          domainConfig={currentConfig}
          entities={entities}
          relationships={relationships}
          onClose={() => setShowCollaborationTools(false)}
        />
      )}

      {/* Template Analytics Modal */}
      {showTemplateAnalytics && currentConfig && (
        <TemplateAnalytics
          domainConfig={currentConfig}
          entities={entities}
          relationships={relationships}
          onClose={() => setShowTemplateAnalytics(false)}
        />
      )}

      
      {/* Real-time Collaboration Components */}
      <RealTimeCollaborationPanel
        templateId={currentConfig ? 'current-template' : undefined}
        onUserPresenceChange={handleUserPresenceChange}
        onTemplateUpdate={handleTemplateUpdate}
      />
      <RealTimeStatus
        isConnected={collaboration.isConnected}
        connectionState={collaboration.connectionState}
        activeUsersCount={collaboration.activeUsersCount}
        lastSyncTime={Date.now()}
        isSyncing={false}
      />
    </div>
  );
};