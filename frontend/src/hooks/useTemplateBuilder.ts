import { useState, useCallback } from 'react';
import { DomainConfig, ValidationResult, GenerationRequest, GenerationResult } from '../types/template';
import { validateCompleteConfig } from '../services/templateValidation';

interface UseTemplateBuilderState {
  currentConfig: Partial<DomainConfig>;
  isValid: boolean;
  validationResult: ValidationResult | null;
  isGenerating: boolean;
  generationProgress: number;
  generationStatus: string;
  lastGenerationResult: GenerationResult | null;
}

interface UseTemplateBuilderActions {
  updateConfig: (config: Partial<DomainConfig>) => void;
  validateConfig: () => Promise<ValidationResult>;
  generateCode: (request: GenerationRequest) => Promise<GenerationResult>;
  resetBuilder: () => void;
  loadTemplate: (templateId: string) => Promise<void>;
  saveTemplate: (name: string) => Promise<boolean>;
}

export function useTemplateBuilder(): UseTemplateBuilderState & UseTemplateBuilderActions {
  const [state, setState] = useState<UseTemplateBuilderState>({
    currentConfig: {
      name: '',
      title: '',
      description: '',
      domain_type: 'custom',
      version: '1.0.0',
      logo: '🏢',
      color_scheme: 'blue',
      theme: 'default',
      entities: [],
      features: []
    },
    isValid: false,
    validationResult: null,
    isGenerating: false,
    generationProgress: 0,
    generationStatus: '',
    lastGenerationResult: null
  });

  const updateConfig = useCallback((newConfig: Partial<DomainConfig>) => {
    setState(prev => ({
      ...prev,
      currentConfig: {
        ...prev.currentConfig,
        ...newConfig
      },
      validationResult: null, // Clear previous validation
      isValid: false // Reset validation status
    }));
  }, []);

  const validateConfig = useCallback(async (): Promise<ValidationResult> => {
    try {
      const result = validateCompleteConfig(state.currentConfig as DomainConfig);
      
      setState(prev => ({
        ...prev,
        validationResult: result,
        isValid: result.is_valid
      }));

      return result;
    } catch (error) {
      console.error('Validation error:', error);
      const errorResult: ValidationResult = {
        is_valid: false,
        errors: [{
          field: 'general',
          message: 'Validation failed due to an unexpected error'
        }]
      };

      setState(prev => ({
        ...prev,
        validationResult: errorResult,
        isValid: false
      }));

      return errorResult;
    }
  }, [state.currentConfig]);

  const generateCode = useCallback(async (request: GenerationRequest): Promise<GenerationResult> => {
    setState(prev => ({
      ...prev,
      isGenerating: true,
      generationProgress: 0,
      generationStatus: 'Starting code generation...'
    }));

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setState(prev => ({
          ...prev,
          generationProgress: Math.min(prev.generationProgress + Math.random() * 20, 95),
          generationStatus: getRandomGenerationStatus(prev.generationProgress)
        }));
      }, 500);

      // Make actual API call
      const API_BASE_URL = getApiBaseUrl();
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error(`Code generation failed: ${response.statusText}`);
      }

      const result: GenerationResult = await response.json();

      setState(prev => ({
        ...prev,
        isGenerating: false,
        generationProgress: 100,
        generationStatus: 'Code generation completed successfully!',
        lastGenerationResult: result
      }));

      return result;
    } catch (error) {
      console.error('Code generation error:', error);
      const errorResult: GenerationResult = {
        success: false,
        files_generated: [],
        errors: [error instanceof Error ? error.message : 'Unknown error occurred']
      };

      setState(prev => ({
        ...prev,
        isGenerating: false,
        generationProgress: 0,
        generationStatus: 'Code generation failed',
        lastGenerationResult: errorResult
      }));

      return errorResult;
    }
  }, []);

  const resetBuilder = useCallback(() => {
    setState({
      currentConfig: {
        name: '',
        title: '',
        description: '',
        domain_type: 'custom',
        version: '1.0.0',
        logo: '🏢',
        color_scheme: 'blue',
        theme: 'default',
        entities: [],
        features: []
      },
      isValid: false,
      validationResult: null,
      isGenerating: false,
      generationProgress: 0,
      generationStatus: '',
      lastGenerationResult: null
    });
  }, []);

  const loadTemplate = useCallback(async (templateId: string): Promise<void> => {
    try {
      const API_BASE_URL = getApiBaseUrl();
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/${templateId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load template: ${response.statusText}`);
      }

      const templateConfig = await response.json();
      
      setState(prev => ({
        ...prev,
        currentConfig: templateConfig,
        validationResult: null,
        isValid: false
      }));
    } catch (error) {
      console.error('Failed to load template:', error);
      throw error;
    }
  }, []);

  const saveTemplate = useCallback(async (name: string): Promise<boolean> => {
    try {
      const API_BASE_URL = getApiBaseUrl();
      const response = await fetch(`${API_BASE_URL}/api/v1/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...state.currentConfig,
          name
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save template: ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Failed to save template:', error);
      return false;
    }
  }, [state.currentConfig]);

  return {
    ...state,
    updateConfig,
    validateConfig,
    generateCode,
    resetBuilder,
    loadTemplate,
    saveTemplate
  };
}

// Helper functions
function getApiBaseUrl(): string {
  // Try to get from environment or use default
  if (typeof window !== 'undefined' && (window as any).__ENV__?.REACT_APP_API_URL) {
    return (window as any).__ENV__.REACT_APP_API_URL;
  }
  return 'http://localhost:8000';
}

function getRandomGenerationStatus(progress: number): string {
  if (progress < 20) {
    return 'Validating configuration...';
  } else if (progress < 40) {
    return 'Generating database models...';
  } else if (progress < 60) {
    return 'Creating API endpoints...';
  } else if (progress < 80) {
    return 'Building frontend components...';
  } else if (progress < 95) {
    return 'Finalizing code structure...';
  } else {
    return 'Almost done...';
  }
}