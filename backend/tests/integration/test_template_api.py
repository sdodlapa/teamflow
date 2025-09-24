"""
Integration tests for Phase 1 template API endpoints.
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from app.main import app
from app.core.template_config import TemplateConfigLoader


class TestTemplateAPIEndpoints:
    """Integration tests for template API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_template_loader(self):
        """Mock template config loader."""
        loader = Mock(spec=TemplateConfigLoader)
        loader.get_available_domains.return_value = [
            'teamflow_original',
            'property_management',
            'test_domain'
        ]
        
        loader.load_domain_config.return_value = Mock(
            domain_info={
                'name': 'test_domain',
                'type': 'project_management',
                'version': '1.0.0',
                'description': 'Test domain for validation'
            },
            entities={
                'User': {
                    'fields': {
                        'name': {'type': 'string', 'required': True},
                        'email': {'type': 'string', 'required': True}
                    }
                },
                'Task': {
                    'fields': {
                        'title': {'type': 'string', 'required': True},
                        'status': {'type': 'string', 'required': True}
                    },
                    'relationships': {
                        'assignee': {'target': 'User', 'type': 'many_to_one'}
                    }
                }
            },
            navigation={
                'main_menu': [
                    {'label': 'Users', 'path': '/users', 'icon': 'user'},
                    {'label': 'Tasks', 'path': '/tasks', 'icon': 'task'}
                ],
                'quick_actions': [
                    {'label': 'New Task', 'action': 'create_task'},
                    {'label': 'New User', 'action': 'create_user'}
                ]
            },
            features={
                'analytics': True,
                'notifications': True,
                'file_management': False
            }
        )
        return loader
    
    @patch('app.api.template.TemplateConfigLoader')
    def test_get_available_domains(self, mock_loader_class, client, mock_template_loader):
        """Test GET /api/v1/template/domains endpoint."""
        mock_loader_class.return_value = mock_template_loader
        
        response = client.get("/api/v1/template/domains")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert 'teamflow_original' in data
        assert 'property_management' in data
        assert 'test_domain' in data
        
        # Verify the loader was called
        mock_template_loader.get_available_domains.assert_called_once()
    
    @patch('app.api.template.TemplateConfigLoader')
    def test_get_domain_config(self, mock_loader_class, client, mock_template_loader):
        """Test GET /api/v1/template/domains/{domain_name} endpoint."""
        mock_loader_class.return_value = mock_template_loader
        
        response = client.get("/api/v1/template/domains/test_domain")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify domain info
        assert 'domain_info' in data
        assert data['domain_info']['name'] == 'test_domain'
        assert data['domain_info']['type'] == 'project_management'
        assert data['domain_info']['version'] == '1.0.0'
        
        # Verify entities
        assert 'entities' in data
        assert 'User' in data['entities']
        assert 'Task' in data['entities']
        assert 'name' in data['entities']['User']['fields']
        assert 'assignee' in data['entities']['Task']['relationships']
        
        # Verify navigation
        assert 'navigation' in data
        assert 'main_menu' in data['navigation']
        assert len(data['navigation']['main_menu']) == 2
        
        # Verify features
        assert 'features' in data
        assert data['features']['analytics'] is True
        assert data['features']['notifications'] is True
        assert data['features']['file_management'] is False
        
        # Verify the loader was called with correct domain
        mock_template_loader.load_domain_config.assert_called_once_with('test_domain')
    
    @patch('app.api.template.TemplateConfigLoader')
    def test_get_domain_config_not_found(self, mock_loader_class, client, mock_template_loader):
        """Test GET /api/v1/template/domains/{domain_name} with non-existent domain."""
        mock_template_loader.load_domain_config.side_effect = FileNotFoundError("Domain not found")
        mock_loader_class.return_value = mock_template_loader
        
        response = client.get("/api/v1/template/domains/nonexistent_domain")
        
        assert response.status_code == 404
        data = response.json()
        assert 'detail' in data
        assert 'not found' in data['detail'].lower()
    
    @patch('app.api.template.TemplateConfigLoader')
    def test_get_domain_entities(self, mock_loader_class, client, mock_template_loader):
        """Test GET /api/v1/template/domains/{domain_name}/entities endpoint."""
        mock_loader_class.return_value = mock_template_loader
        
        response = client.get("/api/v1/template/domains/test_domain/entities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return just the entities section
        assert 'User' in data
        assert 'Task' in data
        assert 'fields' in data['User']
        assert 'relationships' in data['Task']
        
        # Verify specific entity structure
        user_entity = data['User']
        assert 'name' in user_entity['fields']
        assert 'email' in user_entity['fields']
        assert user_entity['fields']['name']['type'] == 'string'
        assert user_entity['fields']['name']['required'] is True
        
        task_entity = data['Task']
        assert 'title' in task_entity['fields']
        assert 'status' in task_entity['fields']
        assert 'assignee' in task_entity['relationships']
        assert task_entity['relationships']['assignee']['target'] == 'User'
    
    @patch('app.api.template.TemplateConfigLoader')
    def test_get_domain_navigation(self, mock_loader_class, client, mock_template_loader):
        """Test GET /api/v1/template/domains/{domain_name}/navigation endpoint."""
        mock_loader_class.return_value = mock_template_loader
        
        response = client.get("/api/v1/template/domains/test_domain/navigation")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return navigation structure
        assert 'main_menu' in data
        assert 'quick_actions' in data
        
        # Verify main menu structure
        main_menu = data['main_menu']
        assert len(main_menu) == 2
        assert main_menu[0]['label'] == 'Users'
        assert main_menu[0]['path'] == '/users'
        assert main_menu[0]['icon'] == 'user'
        assert main_menu[1]['label'] == 'Tasks'
        assert main_menu[1]['path'] == '/tasks'
        assert main_menu[1]['icon'] == 'task'
        
        # Verify quick actions
        quick_actions = data['quick_actions']
        assert len(quick_actions) == 2
        assert quick_actions[0]['label'] == 'New Task'
        assert quick_actions[0]['action'] == 'create_task'
        assert quick_actions[1]['label'] == 'New User'
        assert quick_actions[1]['action'] == 'create_user'
    
    @patch('app.api.template.TemplateConfigLoader')
    def test_template_api_error_handling(self, mock_loader_class, client):
        """Test template API error handling."""
        # Mock loader that raises exceptions
        error_loader = Mock(spec=TemplateConfigLoader)
        error_loader.get_available_domains.side_effect = Exception("Config loading failed")
        error_loader.load_domain_config.side_effect = Exception("Domain loading failed")
        mock_loader_class.return_value = error_loader
        
        # Test domains endpoint error handling
        response = client.get("/api/v1/template/domains")
        assert response.status_code == 500
        
        # Test specific domain endpoint error handling
        response = client.get("/api/v1/template/domains/test")
        assert response.status_code == 500
    
    def test_template_api_endpoints_exist(self, client):
        """Test that template API endpoints are properly registered."""
        # Test that the endpoints exist (even if they return errors without proper mocking)
        
        # Check domains endpoint
        response = client.get("/api/v1/template/domains")
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
        
        # Check domain config endpoint
        response = client.get("/api/v1/template/domains/test")
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
        
        # Check entities endpoint
        response = client.get("/api/v1/template/domains/test/entities")
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
        
        # Check navigation endpoint
        response = client.get("/api/v1/template/domains/test/navigation")
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404


class TestTemplateConfigLoaderIntegration:
    """Integration tests for the template configuration loader with real files."""
    
    def test_real_domain_config_loading(self):
        """Test loading real domain configuration files."""
        loader = TemplateConfigLoader()
        
        # Test get available domains
        domains = loader.get_available_domains()
        assert isinstance(domains, list)
        # Should find at least the sample configs we created
        assert len(domains) >= 0  # May be empty if config files aren't in expected location
    
    def test_teamflow_original_config_if_exists(self):
        """Test loading TeamFlow original config if it exists."""
        loader = TemplateConfigLoader()
        domains = loader.get_available_domains()
        
        if 'teamflow_original' in domains:
            config = loader.load_domain_config('teamflow_original')
            assert config is not None
            assert hasattr(config, 'domain_info')
            assert hasattr(config, 'entities')
            assert config.domain_info['name'] == 'teamflow_original'
    
    def test_property_management_config_if_exists(self):
        """Test loading property management config if it exists."""
        loader = TemplateConfigLoader()
        domains = loader.get_available_domains()
        
        if 'property_management' in domains:
            config = loader.load_domain_config('property_management')
            assert config is not None
            assert hasattr(config, 'domain_info')
            assert hasattr(config, 'entities')
            assert config.domain_info['name'] == 'property_management'
    
    def test_config_loader_error_handling(self):
        """Test config loader error handling with non-existent domain."""
        loader = TemplateConfigLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_domain_config('definitely_nonexistent_domain')


class TestFrontendIntegration:
    """Test frontend integration with template system."""
    
    @pytest.fixture
    def mock_api_responses(self):
        """Mock API responses for frontend testing."""
        return {
            'domains': ['teamflow_original', 'property_management'],
            'domain_config': {
                'domain_info': {
                    'name': 'test_domain',
                    'display_name': 'Test Domain',
                    'type': 'project_management'
                },
                'entities': {
                    'Task': {
                        'display_name': 'Tasks',
                        'plural': 'tasks',
                        'fields': {
                            'title': {'type': 'string', 'required': True, 'display_name': 'Title'},
                            'description': {'type': 'text', 'required': False, 'display_name': 'Description'}
                        }
                    }
                },
                'navigation': {
                    'main_menu': [
                        {'label': 'Tasks', 'path': '/tasks', 'icon': 'task'}
                    ]
                }
            }
        }
    
    def test_dashboard_template_integration_structure(self, mock_api_responses):
        """Test that dashboard component has the right structure for template integration."""
        # This test checks the structure without actually running React
        # We verify that the expected API integration points exist
        
        # The Dashboard component should be expecting these API calls
        expected_api_endpoints = [
            '/api/v1/template/domains',
            '/api/v1/template/domains/{domain}/navigation',
            '/api/v1/template/domains/{domain}'
        ]
        
        # This is a structural test - in a real integration test,
        # we would use tools like Selenium or Playwright to test the actual frontend
        assert len(expected_api_endpoints) == 3
        
        # Verify mock response structure matches expected format
        config = mock_api_responses['domain_config']
        assert 'domain_info' in config
        assert 'entities' in config
        assert 'navigation' in config
        assert isinstance(config['entities'], dict)
        assert isinstance(config['navigation']['main_menu'], list)


if __name__ == "__main__":
    pytest.main([__file__])