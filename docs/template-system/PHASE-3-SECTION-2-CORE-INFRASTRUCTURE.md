# 🚀 PHASE 3: IMPLEMENTATION GUIDE
## Section 2: Core Infrastructure Implementation

---

## 🏗️ CORE INFRASTRUCTURE IMPLEMENTATION

### **Implementation Order & Dependencies**

The core infrastructure forms the foundation of the template system. Each component builds upon the previous, requiring careful sequencing to maintain system integrity.

```
Implementation Dependency Graph:

1. Configuration Parser ────→ 2. Domain Validator
                         ├──→ 3. Template Registry
                         └──→ 4. Template Engine Core
                              ├──→ 5. Code Generation Base
                              └──→ 6. CLI Foundation
```

### **Step 1: Configuration Parser Implementation**

#### **File: `backend/app/template_system/core/config_parser.py`**

**Implementation Strategy:**
- Create robust YAML/JSON parser with validation
- Implement schema validation using Pydantic
- Add comprehensive error handling and user feedback
- Support configuration inheritance and composition

**Key Implementation Details:**
```python
# Primary class structure
class DomainConfigParser:
    def __init__(self, schema_validator: Optional[DomainValidator] = None)
    def parse_config_file(self, config_path: Path) -> DomainConfig
    def parse_config_dict(self, config_dict: Dict[str, Any]) -> DomainConfig
    def validate_config(self, config: DomainConfig) -> ValidationResult
    def resolve_inheritance(self, config: DomainConfig) -> DomainConfig
```

**Implementation Priority:**
1. **Day 1 Morning**: Basic YAML/JSON parsing functionality
2. **Day 1 Afternoon**: Pydantic model integration and validation
3. **Day 2 Morning**: Error handling and user-friendly messages
4. **Day 2 Afternoon**: Configuration inheritance and composition features

**Testing Requirements:**
- Unit tests for all parsing scenarios
- Error handling tests with malformed configurations
- Performance tests with large configuration files
- Integration tests with domain validator

### **Step 2: Domain Validator Implementation**

#### **File: `backend/app/template_system/core/domain_validator.py`**

**Implementation Strategy:**
- Implement comprehensive domain configuration validation
- Create semantic validation beyond syntax checking
- Add business rule validation for domain consistency
- Provide detailed validation reports with suggestions

**Key Implementation Details:**
```python
# Primary validation components
class DomainValidator:
    def validate_domain_config(self, config: DomainConfig) -> ValidationResult
    def validate_entity_relationships(self, entities: Dict[str, EntityConfig]) -> List[ValidationError]
    def validate_field_constraints(self, entity: EntityConfig) -> List[ValidationError]
    def validate_security_configuration(self, config: DomainConfig) -> List[ValidationError]
    def generate_validation_report(self, results: List[ValidationResult]) -> ValidationReport
```

**Critical Validation Rules:**
1. **Entity Relationships**: Foreign keys reference existing entities
2. **Field Constraints**: Compatible types and constraints
3. **Security Rules**: Authentication/authorization consistency
4. **Business Logic**: Workflow rules are implementable
5. **Performance**: Configuration won't create performance issues

**Implementation Priority:**
1. **Day 1**: Core validation framework and entity validation
2. **Day 2**: Relationship validation and security rule checking

### **Step 3: Template Registry Implementation**

#### **File: `backend/app/template_system/core/template_registry.py`**

**Implementation Strategy:**
- Create centralized template management system
- Implement template discovery and loading
- Add template versioning and compatibility checking
- Support custom template extensions

**Key Implementation Details:**
```python
class TemplateRegistry:
    def __init__(self, template_dirs: List[Path])
    def register_template_directory(self, path: Path, priority: int = 0)
    def get_template(self, template_name: str, template_type: str) -> Template
    def list_available_templates(self, filter_type: Optional[str] = None) -> List[TemplateInfo]
    def validate_template_syntax(self, template_path: Path) -> ValidationResult
```

**Template Organization:**
```
templates/
├── backend/
│   ├── model.py.j2          # SQLAlchemy models
│   ├── schema.py.j2         # Pydantic schemas  
│   ├── routes.py.j2         # FastAPI routes
│   └── service.py.j2        # Business logic services
├── frontend/
│   ├── component.tsx.j2     # React components
│   ├── form.tsx.j2          # Form components
│   ├── list.tsx.j2          # List components
│   └── hooks.ts.j2          # Custom hooks
├── deployment/
│   ├── Dockerfile.j2        # Docker configurations
│   ├── docker-compose.yml.j2
│   └── kubernetes.yml.j2
└── testing/
    ├── unit_test.py.j2      # Unit tests
    ├── api_test.py.j2       # API tests
    └── frontend_test.tsx.j2 # Frontend tests
```

### **Step 4: Template Engine Core Implementation**

#### **File: `backend/app/template_system/core/template_engine.py`**

**Implementation Strategy:**
- Build upon Jinja2 with custom extensions
- Implement context generation for templates
- Add template preprocessing and optimization
- Create template inheritance and composition system

**Key Implementation Details:**
```python
class TemplateEngine:
    def __init__(self, registry: TemplateRegistry, validator: DomainValidator)
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str
    def generate_template_context(self, domain_config: DomainConfig) -> Dict[str, Any]
    def batch_render_templates(self, templates: List[str], context: Dict[str, Any]) -> Dict[str, str]
    def optimize_template_rendering(self, templates: List[str]) -> None
```

**Custom Jinja2 Extensions:**
1. **Domain Context**: Access domain configuration in templates
2. **Code Formatting**: Automatic code formatting and indentation
3. **Import Management**: Intelligent import statement generation
4. **Type Conversion**: Automatic type mapping between systems
5. **Validation Helpers**: Template-level validation functions

**Implementation Priority:**
1. **Day 1**: Basic template rendering with Jinja2 integration
2. **Day 2**: Custom extensions and context generation
3. **Day 3**: Template optimization and batch rendering

### **Step 5: Code Generation Base Implementation**

#### **File: `backend/app/template_system/core/generation_base.py`**

**Implementation Strategy:**
- Create abstract base classes for all generators
- Implement common generation patterns and utilities
- Add file management and output organization
- Create generation pipeline coordination

**Key Implementation Details:**
```python
class BaseGenerator(ABC):
    def __init__(self, template_engine: TemplateEngine, output_dir: Path)
    
    @abstractmethod
    def generate(self, domain_config: DomainConfig) -> GenerationResult
    
    def prepare_output_directory(self, domain_name: str) -> Path
    def write_generated_file(self, file_path: Path, content: str) -> None
    def validate_generated_code(self, file_path: Path) -> ValidationResult
    def format_generated_code(self, content: str, language: str) -> str

class GenerationOrchestrator:
    def __init__(self, generators: List[BaseGenerator])
    def generate_full_application(self, domain_config: DomainConfig) -> ApplicationGenerationResult
    def generate_incremental_update(self, changes: DomainConfigChanges) -> UpdateResult
    def rollback_generation(self, generation_id: str) -> RollbackResult
```

**Generation Pipeline:**
```
Domain Config → Validation → Context Generation → Template Rendering → 
Code Formatting → File Writing → Validation → Result Reporting
```

### **Implementation File Structure**

#### **Create Directory Structure**
```bash
# Execute during implementation
mkdir -p backend/app/template_system/{core,generators,migration,templates}
mkdir -p backend/app/template_system/templates/{backend,frontend,deployment,testing}
mkdir -p backend/cli/commands
mkdir -p templates/{domains,generated}
```

#### **Core Module Dependencies**
```python
# backend/app/template_system/__init__.py
from .core.config_parser import DomainConfigParser
from .core.domain_validator import DomainValidator  
from .core.template_registry import TemplateRegistry
from .core.template_engine import TemplateEngine
from .core.generation_base import BaseGenerator, GenerationOrchestrator

__all__ = [
    'DomainConfigParser',
    'DomainValidator', 
    'TemplateRegistry',
    'TemplateEngine',
    'BaseGenerator',
    'GenerationOrchestrator'
]
```

### **Step 6: CLI Foundation Implementation**

#### **File: `backend/cli/main.py`**

**Implementation Strategy:**
- Create extensible CLI using Click framework
- Implement command discovery and registration
- Add comprehensive help and error handling
- Support configuration file-based operations

**Key Implementation Details:**
```python
import click
from pathlib import Path
from app.template_system import (
    DomainConfigParser, DomainValidator, 
    TemplateEngine, GenerationOrchestrator
)

@click.group()
@click.option('--config', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """TeamFlow Template System CLI"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose

@cli.command()
@click.argument('domain_config', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), default='./generated', help='Output directory')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing files')
@click.pass_context
def generate(ctx, domain_config, output, force):
    """Generate application from domain configuration"""
    # Implementation will call GenerationOrchestrator
    pass

@cli.command()
@click.argument('domain_config', type=click.Path(exists=True))
@click.pass_context  
def validate(ctx, domain_config):
    """Validate domain configuration"""
    # Implementation will call DomainValidator
    pass
```

### **Integration Testing Strategy**

#### **Core Infrastructure Tests**
```python
# tests/template_system/test_core_integration.py
class TestCoreInfrastructureIntegration:
    def test_full_pipeline_integration(self):
        """Test complete pipeline from config to generation"""
        # Test config parsing → validation → template rendering → output
        
    def test_error_handling_chain(self):
        """Test error propagation through the system"""
        # Test how errors flow from config to final output
        
    def test_performance_benchmarks(self):
        """Test system performance with various config sizes"""
        # Benchmark config parsing, validation, and generation
```

### **Configuration Management**

#### **Environment Configuration**
```yaml
# backend/app/template_system/config/development.yaml
template_system:
  template_directories:
    - "backend/app/template_system/templates"
    - "templates/custom"  # For user custom templates
  
  generation:
    output_base_directory: "templates/generated"
    backup_on_overwrite: true
    validate_generated_code: true
    
  validation:
    strict_mode: false  # Allow warnings in development
    check_security_rules: true
    validate_performance_implications: true
    
  performance:
    template_cache_size: 100
    parallel_generation: true
    batch_size: 50
```

### **Error Handling Strategy**

#### **Comprehensive Error Categories**
```python
class TemplateSystemError(Exception):
    """Base exception for template system"""
    
class ConfigurationError(TemplateSystemError):
    """Configuration parsing or validation errors"""
    
class TemplateError(TemplateSystemError):
    """Template loading or rendering errors"""
    
class GenerationError(TemplateSystemError):
    """Code generation errors"""
    
class ValidationError(TemplateSystemError):
    """Domain or code validation errors"""
```

#### **User-Friendly Error Messages**
```python
# Example error message formatting
def format_validation_error(error: ValidationError) -> str:
    return f"""
❌ Configuration Error in {error.location}

Problem: {error.message}
Suggestion: {error.suggestion}

Example:
{error.example_fix}

Documentation: {error.docs_link}
"""
```

### **Performance Optimization**

#### **Caching Strategy**
- **Template Caching**: Parsed templates cached in memory
- **Configuration Caching**: Validated configs cached with file modification tracking
- **Generation Caching**: Generated code cached to avoid regeneration
- **Context Caching**: Template contexts cached for similar configurations

#### **Parallel Processing**
- **Batch Generation**: Multiple files generated in parallel
- **Template Rendering**: Independent templates rendered concurrently
- **Validation**: Entity validation parallelized where possible

---

*Continue to Section 3: Code Generators Implementation...*