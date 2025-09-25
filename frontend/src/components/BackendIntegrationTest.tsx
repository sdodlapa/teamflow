import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTemplateManager } from '../hooks/useTemplateManager';
import { templateApi } from '../services/templateApi';
import { DomainConfig } from '../types/template';

const BackendIntegrationTest: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const { 
    templates, 
    loading, 
    currentTemplate, 
    createTemplate, 
    validateTemplate 
  } = useTemplateManager();
  
  const [testResults, setTestResults] = useState<{
    apiConnection: 'pending' | 'success' | 'error';
    templateValidation: 'pending' | 'success' | 'error';
    templateCreation: 'pending' | 'success' | 'error';
    message: string;
  }>({
    apiConnection: 'pending',
    templateValidation: 'pending',
    templateCreation: 'pending',
    message: ''
  });

  const runIntegrationTests = async () => {
    setTestResults(prev => ({ ...prev, message: 'Starting integration tests...' }));
    
    // Test 1: API Connection
    try {
      await templateApi.checkNameAvailability('test-template');
      setTestResults(prev => ({ 
        ...prev, 
        apiConnection: 'success',
        message: 'API connection successful' 
      }));
    } catch (error) {
      setTestResults(prev => ({ 
        ...prev, 
        apiConnection: 'error',
        message: 'API connection failed' 
      }));
      return;
    }

    // Test 2: Template Validation
    const testConfig: DomainConfig = {
      name: 'test_domain',
      title: 'Test Domain',
      description: 'A test domain configuration',
      domain_type: 'custom',
      version: '1.0.0',
      logo: '',
      color_scheme: 'blue',
      theme: 'modern',
      entities: [{
        name: 'test_entity',
        title: 'Test Entity',
        description: 'A test entity',
        fields: [{
          name: 'test_field',
          title: 'Test Field',
          type: 'string',
          required: true
        }]
      }]
    };

    try {
      const validationResult = await validateTemplate(testConfig);
      if (validationResult?.is_valid) {
        setTestResults(prev => ({ 
          ...prev, 
          templateValidation: 'success',
          message: 'Template validation successful' 
        }));
      } else {
        setTestResults(prev => ({ 
          ...prev, 
          templateValidation: 'error',
          message: `Template validation failed: ${validationResult?.errors?.[0]?.message || 'Unknown error'}` 
        }));
        return;
      }
    } catch (error) {
      setTestResults(prev => ({ 
        ...prev, 
        templateValidation: 'error',
        message: 'Template validation request failed' 
      }));
      return;
    }

    // Test 3: Template Creation (if authenticated)
    if (isAuthenticated) {
      try {
        const newTemplate = await createTemplate({
          name: `test_template_${Date.now()}`,
          title: 'Integration Test Template',
          description: 'This template was created during integration testing',
          tags: ['test', 'integration'],
          is_public: false,
          config: testConfig
        });

        if (newTemplate) {
          setTestResults(prev => ({ 
            ...prev, 
            templateCreation: 'success',
            message: 'Template creation successful! Full integration working.' 
          }));
        } else {
          setTestResults(prev => ({ 
            ...prev, 
            templateCreation: 'error',
            message: 'Template creation failed' 
          }));
        }
      } catch (error) {
        setTestResults(prev => ({ 
          ...prev, 
          templateCreation: 'error',
          message: 'Template creation request failed' 
        }));
      }
    } else {
      setTestResults(prev => ({ 
        ...prev, 
        templateCreation: 'pending',
        message: 'Template creation test skipped - user not authenticated' 
      }));
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'pending': return '⏳';
      default: return '❓';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#10b981';
      case 'error': return '#ef4444';
      case 'pending': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  return (
    <div style={{
      padding: '2rem',
      background: 'white',
      borderRadius: '0.5rem',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      maxWidth: '800px',
      margin: '2rem auto'
    }}>
      <h2 style={{ marginBottom: '1.5rem', color: '#1f2937' }}>
        🔧 Backend Integration Test
      </h2>
      
      {isAuthenticated ? (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#f0fdf4', borderRadius: '0.5rem' }}>
          <p>✅ Authenticated as: {user?.name || user?.full_name || user?.email} ({user?.email})</p>
        </div>
      ) : (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#fef3c7', borderRadius: '0.5rem' }}>
          <p>⚠️ Not authenticated - some tests will be limited</p>
        </div>
      )}

      <div style={{ marginBottom: '1.5rem' }}>
        <h3>Test Status:</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>{getStatusIcon(testResults.apiConnection)}</span>
            <span>API Connection</span>
            <span style={{ color: getStatusColor(testResults.apiConnection), fontWeight: 'bold' }}>
              {testResults.apiConnection}
            </span>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>{getStatusIcon(testResults.templateValidation)}</span>
            <span>Template Validation</span>
            <span style={{ color: getStatusColor(testResults.templateValidation), fontWeight: 'bold' }}>
              {testResults.templateValidation}
            </span>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>{getStatusIcon(testResults.templateCreation)}</span>
            <span>Template Creation</span>
            <span style={{ color: getStatusColor(testResults.templateCreation), fontWeight: 'bold' }}>
              {testResults.templateCreation}
            </span>
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#f8fafc', borderRadius: '0.5rem' }}>
        <strong>Status:</strong> {testResults.message}
      </div>

      <button
        onClick={runIntegrationTests}
        disabled={loading}
        style={{
          padding: '0.75rem 1.5rem',
          background: loading ? '#9ca3af' : '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '0.5rem',
          cursor: loading ? 'not-allowed' : 'pointer',
          marginRight: '1rem'
        }}
      >
        {loading ? 'Running Tests...' : 'Run Integration Tests'}
      </button>

      {templates.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Available Templates ({templates.length}):</h3>
          <div style={{ maxHeight: '200px', overflowY: 'auto', marginTop: '1rem' }}>
            {templates.slice(0, 5).map((template) => (
              <div key={template.id} style={{
                padding: '0.5rem',
                background: '#f9fafb',
                margin: '0.25rem 0',
                borderRadius: '0.25rem',
                borderLeft: '3px solid #3b82f6'
              }}>
                <strong>{template.title}</strong> ({template.domain_type})
                <br />
                <small>{template.description}</small>
              </div>
            ))}
            {templates.length > 5 && (
              <p style={{ fontStyle: 'italic', color: '#6b7280', marginTop: '0.5rem' }}>
                ... and {templates.length - 5} more
              </p>
            )}
          </div>
        </div>
      )}

      {currentTemplate && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Current Template:</h3>
          <div style={{ 
            padding: '1rem', 
            background: '#f0f9ff', 
            borderRadius: '0.5rem',
            marginTop: '1rem'
          }}>
            <strong>{currentTemplate.title}</strong>
            <p>{currentTemplate.description}</p>
            <p><small>Created: {new Date(currentTemplate.created_at).toLocaleDateString()}</small></p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackendIntegrationTest;