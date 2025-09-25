import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EnhancedDomainConfigForm } from '../EnhancedDomainConfigForm';
import { DomainConfig } from '../../../types/template';

// Mock the validation service
jest.mock('../../../services/templateValidation', () => ({
  validateDomainConfig: jest.fn().mockResolvedValue({
    isValid: true,
    errors: [],
    warnings: []
  })
}));

// Mock the template API service
jest.mock('../../../services/templateApi', () => ({
  templateApi: {
    checkNameAvailability: jest.fn().mockResolvedValue({ available: true })
  }
}));

describe('EnhancedDomainConfigForm', () => {
  const mockOnConfigChange = jest.fn();
  const mockOnValidationChange = jest.fn();

  const defaultProps = {
    onConfigChange: mockOnConfigChange,
    onValidationChange: mockOnValidationChange
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders enhanced domain configuration form', () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    expect(screen.getByText('Enhanced Domain Configuration')).toBeInTheDocument();
    expect(screen.getByText('Basic Info')).toBeInTheDocument();
    expect(screen.getByText('Branding')).toBeInTheDocument();
    expect(screen.getByText('Advanced')).toBeInTheDocument();
  });

  test('displays form fields in basic info section', () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    expect(screen.getByLabelText('Domain Title')).toBeInTheDocument();
    expect(screen.getByLabelText('Domain Name (Technical Identifier)')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByLabelText('Version')).toBeInTheDocument();
  });

  test('auto-generates domain name from title', async () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    const titleInput = screen.getByLabelText('Domain Title');
    const nameInput = screen.getByLabelText('Domain Name (Technical Identifier)');
    
    fireEvent.change(titleInput, { target: { value: 'My Test Domain' } });
    
    await waitFor(() => {
      expect(nameInput).toHaveValue('my_test_domain');
    });
  });

  test('displays character counters', () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    // Check for character counters
    expect(screen.getByText('0/100 characters')).toBeInTheDocument(); // Title counter
    expect(screen.getByText('0/50 characters')).toBeInTheDocument(); // Name counter
    expect(screen.getByText('0/500 characters')).toBeInTheDocument(); // Description counter
  });

  test('updates character count when typing', async () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    const titleInput = screen.getByLabelText('Domain Title');
    fireEvent.change(titleInput, { target: { value: 'Test Title' } });
    
    await waitFor(() => {
      expect(screen.getByText('10/100 characters')).toBeInTheDocument();
    });
  });

  test('switches between form sections', () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    // Initially on Basic Info section
    expect(screen.getByText('📝 Basic Information')).toBeInTheDocument();
    
    // Switch to Branding section
    fireEvent.click(screen.getByText('Branding'));
    expect(screen.getByText('🎨 Branding & Visual Identity')).toBeInTheDocument();
    
    // Switch to Advanced section
    fireEvent.click(screen.getByText('Advanced'));
    expect(screen.getByText('⚙️ Advanced Configuration')).toBeInTheDocument();
  });

  test('displays domain type selection in basic section', () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    // Check for domain type cards
    expect(screen.getByText('Business Management')).toBeInTheDocument();
    expect(screen.getByText('E-Commerce')).toBeInTheDocument();
    expect(screen.getByText('Customer Relationship Management')).toBeInTheDocument();
  });

  test('displays color schemes in branding section', () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    // Switch to branding section
    fireEvent.click(screen.getByText('Branding'));
    
    // Check for color schemes
    expect(screen.getByText('Professional Blue')).toBeInTheDocument();
    expect(screen.getByText('Growth Green')).toBeInTheDocument();
    expect(screen.getByText('Creative Purple')).toBeInTheDocument();
  });

  test('calls onConfigChange when form values change', async () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    const titleInput = screen.getByLabelText('Domain Title');
    fireEvent.change(titleInput, { target: { value: 'Test Domain' } });
    
    // Wait for debounced validation
    await waitFor(() => {
      expect(mockOnValidationChange).toHaveBeenCalled();
    }, { timeout: 1000 });
  });

  test('displays live preview with default values', () => {
    render(<EnhancedDomainConfigForm {...defaultProps} showPreview={true} />);
    
    expect(screen.getByText('👁️ Live Preview')).toBeInTheDocument();
    expect(screen.getByText('Domain Title')).toBeInTheDocument(); // Preview placeholder
  });

  test('loads with initial configuration', () => {
    const initialConfig: Partial<DomainConfig> = {
      name: 'test_domain',
      title: 'Test Domain',
      description: 'Test description',
      domain_type: 'e_commerce',
      version: '2.0.0',
      logo: '🛒',
      color_scheme: 'green',
      theme: 'modern'
    };

    render(<EnhancedDomainConfigForm {...defaultProps} initialConfig={initialConfig} />);
    
    expect(screen.getByDisplayValue('Test Domain')).toBeInTheDocument();
    expect(screen.getByDisplayValue('test_domain')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test description')).toBeInTheDocument();
    expect(screen.getByDisplayValue('2.0.0')).toBeInTheDocument();
  });

  test('displays validation status', async () => {
    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    // Add some content to trigger validation
    const titleInput = screen.getByLabelText('Domain Title');
    fireEvent.change(titleInput, { target: { value: 'Valid Domain' } });
    
    await waitFor(() => {
      expect(screen.getByText('Configuration is valid and ready to use')).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  test('export functionality works', async () => {
    // Mock URL.createObjectURL and related DOM APIs
    (window.URL.createObjectURL as any) = jest.fn(() => 'mock-url');
    (window.URL.revokeObjectURL as any) = jest.fn();
    const mockClick = jest.fn();
    const mockCreateElement = jest.spyOn(document, 'createElement').mockImplementation((tagName) => {
      if (tagName === 'a') {
        return { 
          click: mockClick,
          href: '',
          download: ''
        } as any;
      }
      return document.createElement(tagName);
    });

    render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    // Add valid content to enable export
    const titleInput = screen.getByLabelText('Domain Title');
    fireEvent.change(titleInput, { target: { value: 'Valid Domain' } });
    
    await waitFor(() => {
      const exportButton = screen.getByText('Export Config');
      fireEvent.click(exportButton);
      expect(mockClick).toHaveBeenCalled();
    }, { timeout: 1000 });

    mockCreateElement.mockRestore();
  });

  test('responsive design classes are applied', () => {
    const { container } = render(<EnhancedDomainConfigForm {...defaultProps} />);
    
    const formElement = container.querySelector('.enhanced-domain-config-form');
    expect(formElement).toBeInTheDocument();
    expect(formElement).toHaveClass('enhanced-domain-config-form');
  });
});