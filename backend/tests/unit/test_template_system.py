"""
Unit tests for Phase 1 template system implementation.
"""
import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime
import yaml

from app.models.base import BaseModel
from app.models.template import (
    DomainTemplate, 
    DomainInstance,
    TemplateUsage,
    TemplateStatus,
    TemplateRegistry
)
from app.core.template_config import (
    TemplateConfigLoader,
    DomainConfig,
    EntityDefinition,
    DomainType
)
from app.services.universal_service import (
    UniversalEntityService,
    UniversalAnalyticsService
)


class TestBaseModelTemplateEnhancements:
    """Test the template-enhanced BaseModel functionality."""
    
    def test_base_model_has_template_fields(self):
        """Test that BaseModel has the new template fields."""
        # Create a mock model that inherits from BaseModel
        class TestModel(BaseModel):
            __tablename__ = 'test_model'
            name: str = 'test'
        
        # Check that template fields exist
        model_instance = TestModel()
        assert hasattr(model_instance, 'is_template_generated')
        assert hasattr(model_instance, 'template_version')
        assert hasattr(model_instance, 'domain_config')
        
        # Check default values
        assert model_instance.is_template_generated is False
        assert model_instance.template_version is None
        assert model_instance.domain_config is None
    
    def test_template_metadata_assignment(self):
        """Test that template metadata can be assigned and retrieved."""
        class TestModel(BaseModel):
            __tablename__ = 'test_model'
            name: str = 'test'
        
        model_instance = TestModel()
        model_instance.is_template_generated = True
        model_instance.template_version = "1.0.0"
        model_instance.domain_config = {"domain": "test", "version": "1.0"}
        
        assert model_instance.is_template_generated is True
        assert model_instance.template_version == "1.0.0"
        assert model_instance.domain_config == {"domain": "test", "version": "1.0"}


class TestTemplateModels:
    """Test the new template tracking models."""
    
    def test_domain_template_creation(self):
        """Test DomainTemplate model creation."""
        template = DomainTemplate(
            name="test_template",
            title="Test Template",
            description="A test template for validation",
            domain_type="project_management",
            version="1.0.0",
            status=TemplateStatus.ACTIVE,
            config_schema={"key": "value"},
            entities_config={"User": {"fields": {"name": "string"}}},
            features={"analytics": True}
        )
        
        assert template.name == "test_template"
        assert template.title == "Test Template"
        assert template.domain_type == "project_management"
        assert template.version == "1.0.0"
        assert template.status == TemplateStatus.ACTIVE
        assert template.config_schema == {"key": "value"}
        assert template.entities_config == {"User": {"fields": {"name": "string"}}}
        assert template.features == {"analytics": True}
    
    def test_domain_instance_creation(self):
        """Test DomainInstance model creation."""
        instance = DomainInstance(
            name="test_instance",
            title="Test Instance", 
            description="A test instance",
            template_id=1,
            template_version="1.0.0",
            instance_config={"custom": "config"},
            organization_id=1
        )
        
        assert instance.name == "test_instance"
        assert instance.title == "Test Instance"
        assert instance.template_id == 1
        assert instance.template_version == "1.0.0"
        assert instance.instance_config == {"custom": "config"}
        assert instance.organization_id == 1
        assert instance.is_active is True
    
    def test_template_usage_creation(self):
        """Test TemplateUsage model creation."""
        usage = TemplateUsage(
            template_id=1,
            instance_id=1,
            action="create",
            user_id="user123",
            context_data={"test": "data"}
        )
        
        assert usage.template_id == 1
        assert usage.instance_id == 1
        assert usage.action == "create"
        assert usage.user_id == "user123"
        assert usage.context_data == {"test": "data"}
    
    def test_template_registry_functionality(self):
        """Test TemplateRegistry functionality."""
        registry = TemplateRegistry()
        
        template = DomainTemplate(
            name="registry_test",
            title="Registry Test",
            domain_type="test",
            version="1.0.0",
            config_schema={},
            entities_config={}
        )
        
        # Test registration
        registry.register_template(template)
        retrieved = registry.get_template("registry_test")
        assert retrieved is not None
        assert retrieved.name == "registry_test"
        
        # Test listing
        templates = registry.list_templates()
        assert len(templates) >= 1
        assert any(t.name == "registry_test" for t in templates)


class TestTemplateConfigLoader:
    """Test the template configuration loading system."""
    
    @pytest.fixture
    def mock_yaml_data(self):
        """Mock YAML configuration data."""
        return {
            'domain_info': {
                'name': 'test_domain',
                'type': 'project_management',
                'version': '1.0.0'
            },
            'entities': {
                'User': {
                    'fields': {
                        'name': {'type': 'string', 'required': True},
                        'email': {'type': 'string', 'required': True}
                    }
                },
                'Task': {
                    'fields': {
                        'title': {'type': 'string', 'required': True},
                        'description': {'type': 'text', 'required': False}
                    },
                    'relationships': {
                        'assignee': {'target': 'User', 'type': 'many_to_one'}
                    }
                }
            },
            'navigation': {
                'main_menu': [
                    {'label': 'Users', 'path': '/users'},
                    {'label': 'Tasks', 'path': '/tasks'}
                ]
            }
        }
    
    def test_domain_config_creation(self, mock_yaml_data):
        """Test DomainConfig creation from YAML data."""
        config = DomainConfig(**mock_yaml_data)
        
        assert config.domain_info['name'] == 'test_domain'
        assert config.domain_info['type'] == 'project_management'
        assert len(config.entities) == 2
        assert 'User' in config.entities
        assert 'Task' in config.entities
    
    def test_entity_definition_validation(self, mock_yaml_data):
        """Test EntityDefinition validation."""
        user_entity = EntityDefinition(**mock_yaml_data['entities']['User'])
        
        assert len(user_entity.fields) == 2
        assert user_entity.fields['name']['type'] == 'string'
        assert user_entity.fields['name']['required'] is True
        
        task_entity = EntityDefinition(**mock_yaml_data['entities']['Task'])
        assert len(task_entity.relationships) == 1
        assert task_entity.relationships['assignee']['target'] == 'User'
    
    def test_template_config_loader_init(self):
        """Test TemplateConfigLoader initialization."""
        loader = TemplateConfigLoader()
        assert hasattr(loader, 'config_dir')
        assert hasattr(loader, '_config_cache')
    
    def test_domain_type_enum(self):
        """Test DomainType enum values."""
        assert DomainType.PROJECT_MANAGEMENT == "project_management"
        assert DomainType.CRM == "crm"
        assert DomainType.E_COMMERCE == "e_commerce"
        assert DomainType.HEALTHCARE == "healthcare"
        assert DomainType.EDUCATION == "education"
        assert DomainType.FINANCE == "finance"
        assert DomainType.REAL_ESTATE == "real_estate"
        assert DomainType.CUSTOM == "custom"


class TestUniversalServices:
    """Test the universal service implementations."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def universal_entity_service(self, mock_db_session):
        """Universal entity service with mocked database."""
        return UniversalEntityService(mock_db_session)
    
    @pytest.fixture
    def universal_analytics_service(self, mock_db_session):
        """Universal analytics service with mocked database."""
        return UniversalAnalyticsService(mock_db_session)
    
    def test_universal_entity_service_init(self, universal_entity_service):
        """Test UniversalEntityService initialization."""
        assert hasattr(universal_entity_service, 'db')
        assert hasattr(universal_entity_service, '_model_registry')
    
    def test_universal_analytics_service_init(self, universal_analytics_service):
        """Test UniversalAnalyticsService initialization."""
        assert hasattr(universal_analytics_service, 'db')
    
    def test_entity_service_model_registration(self, universal_entity_service):
        """Test model registration in universal entity service."""
        # Test register_model method exists
        assert hasattr(universal_entity_service, 'register_model')
        
        # Test get_model method exists
        assert hasattr(universal_entity_service, 'get_model')
    
    def test_analytics_service_methods(self, universal_analytics_service):
        """Test analytics service has required methods."""
        # Check that analytics service has the expected methods
        assert hasattr(universal_analytics_service, 'get_entity_count')
        assert hasattr(universal_analytics_service, 'get_entity_growth')
        assert hasattr(universal_analytics_service, 'get_cross_domain_metrics')
        assert hasattr(universal_analytics_service, 'generate_domain_report')


class TestTemplateSystemIntegration:
    """Integration tests for the complete template system."""
    
    def test_template_config_and_models_integration(self):
        """Test integration between config loading and model creation."""
        # Create a domain config
        domain_config = {
            'domain_info': {
                'name': 'integration_test',
                'type': 'project_management',
                'version': '1.0.0'
            },
            'entities': {
                'TestEntity': {
                    'fields': {
                        'name': {'type': 'string', 'required': True}
                    }
                }
            }
        }
        
        config = DomainConfig(**domain_config)
        
        # Create a template that references this config
        template = DomainTemplate(
            name="integration_template",
            title="Integration Template",
            domain_type="project_management",
            version="1.0.0",
            config_schema=domain_config,
            entities_config=domain_config['entities']
        )
        
        # Verify the integration
        assert template.domain_type == config.domain_info['type']
        assert template.config_schema == domain_config
    
    def test_base_model_template_tracking_integration(self):
        """Test integration between BaseModel and template tracking."""
        class TestEntity(BaseModel):
            __tablename__ = 'test_entity'
            name: str = 'test'
        
        # Create entity with template metadata
        entity = TestEntity()
        entity.is_template_generated = True
        entity.template_version = "1.0.0"
        entity.domain_config = {"domain": "test"}
        
        # Create usage tracking for this entity
        tracking = TemplateUsage(
            template_id=1,
            action="create",
            context_data={"entity_type": "TestEntity", "entity_id": str(entity.id)}
        )
        
        # Verify the integration
        assert tracking.action == "create"
        assert entity.is_template_generated is True


class TestTemplateSystemErrorHandling:
    """Test error handling in the template system."""
    
    def test_invalid_domain_config(self):
        """Test handling of invalid domain configuration."""
        invalid_config = {
            'domain_info': {
                # Missing required fields
            }
        }
        
        with pytest.raises((ValueError, TypeError)):
            DomainConfig(**invalid_config)
    
    def test_template_instance_validation(self):
        """Test template instance validation."""
        # Test with missing required fields
        with pytest.raises((ValueError, TypeError)):
            DomainTemplate()
    
    def test_universal_service_error_handling(self):
        """Test error handling in universal services."""
        mock_db = Mock()
        service = UniversalEntityService(mock_db)
        
        # Test that service handles None model gracefully
        result = service.get_model("NonExistentModel")
        assert result is None or isinstance(result, type(None))


if __name__ == "__main__":
    pytest.main([__file__])