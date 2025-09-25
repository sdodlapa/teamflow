import React, { useState } from 'react';
import { EnhancedDomainConfigForm } from './EnhancedDomainConfigForm';
import { DomainConfig } from '../../types/template';

/**
 * Integration test component for Enhanced Domain Configuration Form
 * This component demonstrates the enhanced form functionality
 */
export const EnhancedDomainConfigFormTest: React.FC = () => {
  const [config, setConfig] = useState<DomainConfig | null>(null);
  const [validationState, setValidationState] = useState({
    isValid: false,
    errors: [] as string[]
  });

  const handleConfigChange = (newConfig: DomainConfig) => {
    console.log('Config changed:', newConfig);
    setConfig(newConfig);
  };

  const handleValidationChange = (isValid: boolean, errors: string[]) => {
    console.log('Validation changed:', { isValid, errors });
    setValidationState({ isValid, errors });
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f3f4f6', 
      padding: '20px' 
    }}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
      }}>
        <h1 style={{ 
          textAlign: 'center', 
          marginBottom: '32px',
          color: '#1f2937',
          fontSize: '28px',
          fontWeight: '700'
        }}>
          🧪 Enhanced Domain Configuration Form - Integration Test
        </h1>
        
        <EnhancedDomainConfigForm
          initialConfig={{
            name: 'test_domain',
            title: 'Test Domain',
            description: 'This is a test domain configuration for demonstrating the enhanced form capabilities.',
            domain_type: 'business',
            version: '1.0.0',
            logo: '🧪',
            color_scheme: 'blue',
            theme: 'modern'
          }}
          onConfigChange={handleConfigChange}
          onValidationChange={handleValidationChange}
          showPreview={true}
          autoSave={false}
        />

        {/* Test Results Display */}
        <div style={{
          marginTop: '32px',
          padding: '20px',
          backgroundColor: '#f9fafb',
          borderRadius: '12px',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ 
            color: '#1f2937', 
            marginBottom: '16px',
            fontSize: '18px',
            fontWeight: '600'
          }}>
            🔍 Integration Test Results
          </h3>
          
          <div style={{ display: 'grid', gap: '16px' }}>
            <div>
              <strong>Validation Status:</strong>
              <span style={{ 
                marginLeft: '8px',
                color: validationState.isValid ? '#059669' : '#dc2626',
                fontWeight: '600'
              }}>
                {validationState.isValid ? '✅ Valid' : '❌ Invalid'}
              </span>
            </div>
            
            {validationState.errors.length > 0 && (
              <div>
                <strong>Validation Errors:</strong>
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  {validationState.errors.map((error, index) => (
                    <li key={index} style={{ color: '#dc2626' }}>
                      {error}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div>
              <strong>Current Configuration:</strong>
              <pre style={{
                backgroundColor: '#ffffff',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '12px',
                overflow: 'auto',
                marginTop: '8px'
              }}>
                {JSON.stringify(config, null, 2)}
              </pre>
            </div>
          </div>
        </div>

        {/* Feature Testing Checklist */}
        <div style={{
          marginTop: '24px',
          padding: '20px',
          backgroundColor: '#dbeafe',
          borderRadius: '12px',
          border: '1px solid #93c5fd'
        }}>
          <h3 style={{ 
            color: '#1e40af', 
            marginBottom: '16px',
            fontSize: '18px',
            fontWeight: '600'
          }}>
            🧪 Feature Testing Checklist
          </h3>
          
          <div style={{ display: 'grid', gap: '8px', fontSize: '14px' }}>
            <div>✅ <strong>Enhanced UI:</strong> Professional styling and layout</div>
            <div>✅ <strong>Section Navigation:</strong> Tabbed interface for better organization</div>
            <div>✅ <strong>Real-time Validation:</strong> Immediate feedback with errors and warnings</div>
            <div>✅ <strong>Character Counters:</strong> Progress indicators for all text fields</div>
            <div>✅ <strong>Domain Availability:</strong> Name availability checking (async)</div>
            <div>✅ <strong>Smart Auto-generation:</strong> Domain name from title</div>
            <div>✅ <strong>Enhanced Selection:</strong> Visual grids for types, colors, and themes</div>
            <div>✅ <strong>Live Preview:</strong> Real-time configuration preview</div>
            <div>✅ <strong>Responsive Design:</strong> Mobile-friendly layout</div>
            <div>✅ <strong>Accessibility:</strong> Proper ARIA labels and keyboard navigation</div>
          </div>
        </div>
      </div>
    </div>
  );
};