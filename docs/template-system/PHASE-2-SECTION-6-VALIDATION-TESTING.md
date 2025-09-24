# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## Section 6: Validation & Testing Framework

---

## 🧪 VALIDATION & TESTING FRAMEWORK

### **Automated Test Generation Engine**

The testing framework automatically generates comprehensive test suites for all generated components, ensuring reliability and maintainability of template-generated applications.

#### **Test Generator** (`backend/app/core/test_generator.py`)
```python
from typing import Dict, List, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.domain_config import DomainConfig, EntityConfig

class TestGenerator:
    """Generate comprehensive test suites from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.unit_test_template = self.env.get_template('unit_test.py.j2')
        self.api_test_template = self.env.get_template('api_test.py.j2')
        self.integration_test_template = self.env.get_template('integration_test.py.j2')
        self.frontend_test_template = self.env.get_template('frontend_test.tsx.j2')
    
    def generate_model_tests(self, entity_name: str, entity_config: EntityConfig, 
                           domain_config: DomainConfig) -> str:
        """Generate unit tests for SQLAlchemy models"""
        
        class_name = entity_name.title()
        snake_name = entity_name.lower()
        
        # Extract test scenarios from field configurations
        test_scenarios = self._generate_model_test_scenarios(entity_config)
        
        # Extract validation test cases
        validation_tests = self._generate_validation_tests(entity_config)
        
        # Extract relationship tests
        relationship_tests = self._generate_relationship_tests(entity_config)
        
        return self.unit_test_template.render(
            class_name=class_name,
            snake_name=snake_name,
            test_scenarios=test_scenarios,
            validation_tests=validation_tests,
            relationship_tests=relationship_tests,
            domain_name=domain_config.domain.name,
            required_fields=self._get_required_fields(entity_config),
            optional_fields=self._get_optional_fields(entity_config)
        )
    
    def generate_api_tests(self, entity_name: str, entity_config: EntityConfig, 
                          domain_config: DomainConfig) -> str:
        """Generate API endpoint tests"""
        
        class_name = entity_name.title()
        snake_name = entity_name.lower()
        plural_name = f"{snake_name}s"
        
        # Generate test cases for each operation
        operations = entity_config.operations or ['create', 'read', 'update', 'delete', 'list']
        
        # Authentication test scenarios
        auth_tests = self._generate_auth_test_scenarios(entity_config)
        
        # Validation test scenarios
        validation_tests = self._generate_api_validation_tests(entity_config)
        
        # Business logic test scenarios
        business_logic_tests = self._generate_business_logic_tests(entity_config)
        
        return self.api_test_template.render(
            class_name=class_name,
            snake_name=snake_name,
            plural_name=plural_name,
            operations=operations,
            auth_tests=auth_tests,
            validation_tests=validation_tests,
            business_logic_tests=business_logic_tests,
            domain_name=domain_config.domain.name,
            api_endpoint=f"/api/v1/{plural_name}",
            auth_required=entity_config.security.get('authentication', True)
        )
    
    def generate_integration_tests(self, domain_config: DomainConfig) -> str:
        """Generate integration tests for the entire domain"""
        
        domain_name = domain_config.domain.name
        entities = list(domain_config.entities.keys())
        
        # Generate workflow tests
        workflow_tests = self._generate_workflow_tests(domain_config)
        
        # Generate cross-entity tests
        cross_entity_tests = self._generate_cross_entity_tests(domain_config)
        
        # Generate performance tests
        performance_tests = self._generate_performance_tests(domain_config)
        
        return self.integration_test_template.render(
            domain_name=domain_name,
            entities=entities,
            workflow_tests=workflow_tests,
            cross_entity_tests=cross_entity_tests,
            performance_tests=performance_tests
        )
    
    def generate_frontend_tests(self, entity_name: str, entity_config: EntityConfig) -> str:
        """Generate React component tests"""
        
        class_name = entity_name.title()
        camel_name = self._to_camel_case(entity_name)
        
        # Component test scenarios
        component_tests = self._generate_component_test_scenarios(entity_config)
        
        # Form validation tests
        form_tests = self._generate_form_test_scenarios(entity_config)
        
        # API integration tests
        api_integration_tests = self._generate_frontend_api_tests(entity_config)
        
        return self.frontend_test_template.render(
            class_name=class_name,
            camel_name=camel_name,
            component_tests=component_tests,
            form_tests=form_tests,
            api_integration_tests=api_integration_tests
        )
    
    def _generate_model_test_scenarios(self, entity_config: EntityConfig) -> List[Dict]:
        """Generate model test scenarios"""
        scenarios = []
        
        # Basic creation test
        scenarios.append({
            'name': 'test_create_with_valid_data',
            'description': 'Test model creation with valid data',
            'type': 'positive',
            'test_data': self._generate_valid_test_data(entity_config)
        })
        
        # Required field validation tests
        for field in entity_config.fields:
            if field.required:
                scenarios.append({
                    'name': f'test_create_without_{field.name}',
                    'description': f'Test model creation fails without required {field.name}',
                    'type': 'negative',
                    'missing_field': field.name
                })
        
        # Field validation tests
        for field in entity_config.fields:
            if field.max_length:
                scenarios.append({
                    'name': f'test_{field.name}_max_length',
                    'description': f'Test {field.name} respects max_length constraint',
                    'type': 'negative',
                    'field': field.name,
                    'invalid_value': 'x' * (field.max_length + 1)
                })
        
        return scenarios
    
    def _generate_validation_tests(self, entity_config: EntityConfig) -> List[Dict]:
        """Generate field validation tests"""
        tests = []
        
        for field in entity_config.fields:
            field_tests = []
            
            # Type validation
            if field.type == 'email':
                field_tests.extend([
                    {'value': 'invalid-email', 'should_pass': False},
                    {'value': 'valid@email.com', 'should_pass': True}
                ])
            
            elif field.type == 'integer':
                field_tests.extend([
                    {'value': 'not-a-number', 'should_pass': False},
                    {'value': 42, 'should_pass': True}
                ])
            
            # Range validation
            if field.min_value is not None:
                field_tests.append({
                    'value': field.min_value - 1,
                    'should_pass': False,
                    'constraint': 'min_value'
                })
            
            if field.max_value is not None:
                field_tests.append({
                    'value': field.max_value + 1,
                    'should_pass': False,
                    'constraint': 'max_value'
                })
            
            if field_tests:
                tests.append({
                    'field_name': field.name,
                    'field_type': field.type,
                    'test_cases': field_tests
                })
        
        return tests
```

#### **Unit Test Template** (`templates/backend/unit_test.py.j2`)
```python
"""
Unit tests for {{ class_name }} model
Auto-generated test suite for {{ domain_name }} domain
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from decimal import Decimal

from app.models.{{ snake_name }} import {{ class_name }}
from app.schemas.{{ snake_name }} import {{ class_name }}Create


class Test{{ class_name }}Model:
    """Test suite for {{ class_name }} model operations"""
    
    {% for scenario in test_scenarios %}
    {% if scenario.type == 'positive' %}
    async def {{ scenario.name }}(self, db_session: AsyncSession):
        """{{ scenario.description }}"""
        
        # Arrange
        test_data = {
            {% for field_name, field_value in scenario.test_data.items() %}
            "{{ field_name }}": {{ field_value | tojson }},
            {% endfor %}
        }
        
        # Act
        {{ snake_name }} = {{ class_name }}(**test_data)
        db_session.add({{ snake_name }})
        await db_session.commit()
        await db_session.refresh({{ snake_name }})
        
        # Assert
        assert {{ snake_name }}.id is not None
        {% for field_name in scenario.test_data.keys() %}
        assert {{ snake_name }}.{{ field_name }} == test_data["{{ field_name }}"]
        {% endfor %}
        assert {{ snake_name }}.created_at is not None
        assert {{ snake_name }}.updated_at is not None
    
    {% else %}
    async def {{ scenario.name }}(self, db_session: AsyncSession):
        """{{ scenario.description }}"""
        
        # Arrange
        test_data = {
            {% for field_name, field_value in scenario.test_data.items() %}
            {% if field_name != scenario.missing_field %}
            "{{ field_name }}": {{ field_value | tojson }},
            {% endif %}
            {% endfor %}
        }
        
        # Act & Assert
        with pytest.raises((IntegrityError, ValueError)):
            {{ snake_name }} = {{ class_name }}(**test_data)
            db_session.add({{ snake_name }})
            await db_session.commit()
    {% endif %}
    
    {% endfor %}
    
    {% for validation_test in validation_tests %}
    class Test{{ validation_test.field_name.title() }}Validation:
        """Validation tests for {{ validation_test.field_name }} field"""
        
        {% for test_case in validation_test.test_cases %}
        async def test_{{ validation_test.field_name }}_{{ loop.index }}(self, db_session: AsyncSession):
            """Test {{ validation_test.field_name }} with value: {{ test_case.value }}"""
            
            # Arrange
            test_data = {
                {% for field in required_fields %}
                "{{ field.name }}": {% if field.type == 'string' %}"test_value"{% elif field.type == 'integer' %}1{% elif field.type == 'boolean' %}True{% else %}None{% endif %},
                {% endfor %}
                "{{ validation_test.field_name }}": {{ test_case.value | tojson }}
            }
            
            {% if test_case.should_pass %}
            # Act - should succeed
            {{ snake_name }} = {{ class_name }}(**test_data)
            db_session.add({{ snake_name }})
            await db_session.commit()
            
            # Assert
            assert {{ snake_name }}.{{ validation_test.field_name }} == {{ test_case.value | tojson }}
            {% else %}
            # Act & Assert - should fail
            with pytest.raises((IntegrityError, ValueError)):
                {{ snake_name }} = {{ class_name }}(**test_data)
                db_session.add({{ snake_name }})
                await db_session.commit()
            {% endif %}
        
        {% endfor %}
    {% endfor %}
    
    {% for relationship_test in relationship_tests %}
    async def test_{{ relationship_test.name }}_relationship(self, db_session: AsyncSession):
        """Test {{ relationship_test.name }} relationship"""
        
        # This test would be generated based on relationship configuration
        # Implementation depends on specific relationship type and entities
        pass
    {% endfor %}
    
    async def test_model_repr(self, db_session: AsyncSession):
        """Test model string representation"""
        
        # Arrange
        test_data = {
            {% for field in required_fields %}
            "{{ field.name }}": {% if field.type == 'string' %}"test_{{ field.name }}"{% elif field.type == 'integer' %}{{ loop.index }}{% elif field.type == 'boolean' %}True{% else %}None{% endif %},
            {% endfor %}
        }
        
        # Act
        {{ snake_name }} = {{ class_name }}(**test_data)
        db_session.add({{ snake_name }})
        await db_session.commit()
        await db_session.refresh({{ snake_name }})
        
        # Assert
        repr_str = repr({{ snake_name }})
        assert "{{ class_name }}" in repr_str
        assert str({{ snake_name }}.id) in repr_str
    
    async def test_model_timestamps(self, db_session: AsyncSession):
        """Test automatic timestamp creation and updates"""
        
        # Arrange
        test_data = {
            {% for field in required_fields %}
            "{{ field.name }}": {% if field.type == 'string' %}"test_{{ field.name }}"{% elif field.type == 'integer' %}{{ loop.index }}{% elif field.type == 'boolean' %}True{% else %}None{% endif %},
            {% endfor %}
        }
        
        # Act - Create
        {{ snake_name }} = {{ class_name }}(**test_data)
        db_session.add({{ snake_name }})
        await db_session.commit()
        await db_session.refresh({{ snake_name }})
        
        created_at = {{ snake_name }}.created_at
        updated_at = {{ snake_name }}.updated_at
        
        # Assert creation timestamps
        assert created_at is not None
        assert updated_at is not None
        assert created_at == updated_at
        
        # Act - Update
        {% if optional_fields %}
        {% set first_optional = optional_fields[0] %}
        {{ snake_name }}.{{ first_optional.name }} = {% if first_optional.type == 'string' %}"updated_value"{% elif first_optional.type == 'integer' %}999{% elif first_optional.type == 'boolean' %}False{% else %}None{% endif %}
        await db_session.commit()
        await db_session.refresh({{ snake_name }})
        
        # Assert update timestamp changed
        assert {{ snake_name }}.updated_at > updated_at
        assert {{ snake_name }}.created_at == created_at  # Should not change
        {% endif %}
```

#### **API Test Template** (`templates/backend/api_test.py.j2`)
```python
"""
API tests for {{ class_name }} endpoints
Auto-generated test suite for {{ domain_name }} domain
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.models.{{ snake_name }} import {{ class_name }}
from app.models.user import User


class Test{{ class_name }}API:
    """Test suite for {{ class_name }} API endpoints"""
    
    {% if 'create' in operations %}
    async def test_create_{{ snake_name }}_success(
        self, 
        client: AsyncClient, 
        {% if auth_required %}auth_headers: dict,{% endif %}
        db_session: AsyncSession
    ):
        """Test successful {{ snake_name }} creation"""
        
        # Arrange
        {{ snake_name }}_data = {
            {% for field in required_fields %}
            "{{ field.name }}": {% if field.type == 'string' %}"test_{{ field.name }}"{% elif field.type == 'integer' %}{{ loop.index }}{% elif field.type == 'boolean' %}True{% elif field.type == 'date' %}"2023-01-01"{% elif field.type == 'datetime' %}"2023-01-01T10:00:00"{% else %}"test_value"{% endif %},
            {% endfor %}
        }
        
        # Act
        response = await client.post(
            "{{ api_endpoint }}",
            json={{ snake_name }}_data{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] is not None
        {% for field in required_fields %}
        assert data["{{ field.name }}"] == {{ snake_name }}_data["{{ field.name }}"]
        {% endfor %}
        assert data["created_at"] is not None
        assert data["updated_at"] is not None
    
    {% for validation_test in validation_tests %}
    async def test_create_{{ snake_name }}_validation_{{ loop.index }}(
        self, 
        client: AsyncClient,
        {% if auth_required %}auth_headers: dict{% endif %}
    ):
        """Test {{ snake_name }} creation validation: {{ validation_test.description }}"""
        
        # Arrange
        invalid_data = {
            {% for field_name, field_value in validation_test.invalid_data.items() %}
            "{{ field_name }}": {{ field_value | tojson }},
            {% endfor %}
        }
        
        # Act
        response = await client.post(
            "{{ api_endpoint }}",
            json=invalid_data{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
    {% endfor %}
    
    {% if auth_required %}
    async def test_create_{{ snake_name }}_unauthorized(self, client: AsyncClient):
        """Test {{ snake_name }} creation without authentication"""
        
        # Arrange
        {{ snake_name }}_data = {
            {% for field in required_fields %}
            "{{ field.name }}": {% if field.type == 'string' %}"test_{{ field.name }}"{% else %}1{% endif %},
            {% endfor %}
        }
        
        # Act
        response = await client.post("{{ api_endpoint }}", json={{ snake_name }}_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    {% endif %}
    {% endif %}
    
    {% if 'read' in operations %}
    async def test_get_{{ snake_name }}_success(
        self, 
        client: AsyncClient,
        {% if auth_required %}auth_headers: dict,{% endif %}
        db_session: AsyncSession
    ):
        """Test successful {{ snake_name }} retrieval"""
        
        # Arrange - Create test {{ snake_name }}
        test_{{ snake_name }} = {{ class_name }}(
            {% for field in required_fields %}
            {{ field.name }}={% if field.type == 'string' %}"test_{{ field.name }}"{% else %}1{% endif %},
            {% endfor %}
        )
        db_session.add(test_{{ snake_name }})
        await db_session.commit()
        await db_session.refresh(test_{{ snake_name }})
        
        # Act
        response = await client.get(
            f"{{ api_endpoint }}/{test_{{ snake_name }}.id}"{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_{{ snake_name }}.id
        {% for field in required_fields %}
        assert data["{{ field.name }}"] == test_{{ snake_name }}.{{ field.name }}
        {% endfor %}
    
    async def test_get_{{ snake_name }}_not_found(
        self, 
        client: AsyncClient{% if auth_required %},
        auth_headers: dict{% endif %}
    ):
        """Test {{ snake_name }} retrieval with non-existent ID"""
        
        # Act
        response = await client.get(
            "{{ api_endpoint }}/99999"{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
    {% endif %}
    
    {% if 'list' in operations %}
    async def test_list_{{ plural_name }}_success(
        self, 
        client: AsyncClient,
        {% if auth_required %}auth_headers: dict,{% endif %}
        db_session: AsyncSession
    ):
        """Test successful {{ plural_name }} list retrieval"""
        
        # Arrange - Create test {{ plural_name }}
        test_{{ plural_name }} = [
            {{ class_name }}(
                {% for field in required_fields %}
                {{ field.name }}={% if field.type == 'string' %}f"test_{{ field.name }}_{i}"{% else %}i{% endif %},
                {% endfor %}
            )
            for i in range(3)
        ]
        db_session.add_all(test_{{ plural_name }})
        await db_session.commit()
        
        # Act
        response = await client.get(
            "{{ api_endpoint }}"{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert len(data["items"]) == 3
        assert data["total"] == 3
    
    async def test_list_{{ plural_name }}_pagination(
        self, 
        client: AsyncClient,
        {% if auth_required %}auth_headers: dict,{% endif %}
        db_session: AsyncSession
    ):
        """Test {{ plural_name }} list pagination"""
        
        # Arrange - Create test {{ plural_name }}
        test_{{ plural_name }} = [
            {{ class_name }}(
                {% for field in required_fields %}
                {{ field.name }}={% if field.type == 'string' %}f"test_{{ field.name }}_{i}"{% else %}i{% endif %},
                {% endfor %}
            )
            for i in range(5)
        ]
        db_session.add_all(test_{{ plural_name }})
        await db_session.commit()
        
        # Act
        response = await client.get(
            "{{ api_endpoint }}?skip=2&limit=2"{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["skip"] == 2
        assert data["limit"] == 2
    {% endif %}
    
    {% if 'update' in operations %}
    async def test_update_{{ snake_name }}_success(
        self, 
        client: AsyncClient,
        {% if auth_required %}auth_headers: dict,{% endif %}
        db_session: AsyncSession
    ):
        """Test successful {{ snake_name }} update"""
        
        # Arrange - Create test {{ snake_name }}
        test_{{ snake_name }} = {{ class_name }}(
            {% for field in required_fields %}
            {{ field.name }}={% if field.type == 'string' %}"original_{{ field.name }}"{% else %}1{% endif %},
            {% endfor %}
        )
        db_session.add(test_{{ snake_name }})
        await db_session.commit()
        await db_session.refresh(test_{{ snake_name }})
        
        # Arrange - Update data
        update_data = {
            {% if optional_fields %}
            {% set first_optional = optional_fields[0] %}
            "{{ first_optional.name }}": {% if first_optional.type == 'string' %}"updated_{{ first_optional.name }}"{% else %}999{% endif %}
            {% else %}
            {% set first_required = required_fields[0] %}
            "{{ first_required.name }}": {% if first_required.type == 'string' %}"updated_{{ first_required.name }}"{% else %}999{% endif %}
            {% endif %}
        }
        
        # Act
        response = await client.put(
            f"{{ api_endpoint }}/{test_{{ snake_name }}.id}",
            json=update_data{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_{{ snake_name }}.id
        {% if optional_fields %}
        {% set first_optional = optional_fields[0] %}
        assert data["{{ first_optional.name }}"] == update_data["{{ first_optional.name }}"]
        {% endif %}
    {% endif %}
    
    {% if 'delete' in operations %}
    async def test_delete_{{ snake_name }}_success(
        self, 
        client: AsyncClient,
        {% if auth_required %}auth_headers: dict,{% endif %}
        db_session: AsyncSession
    ):
        """Test successful {{ snake_name }} deletion"""
        
        # Arrange - Create test {{ snake_name }}
        test_{{ snake_name }} = {{ class_name }}(
            {% for field in required_fields %}
            {{ field.name }}={% if field.type == 'string' %}"test_{{ field.name }}"{% else %}1{% endif %},
            {% endfor %}
        )
        db_session.add(test_{{ snake_name }})
        await db_session.commit()
        await db_session.refresh(test_{{ snake_name }})
        
        # Act
        response = await client.delete(
            f"{{ api_endpoint }}/{test_{{ snake_name }}.id}"{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_response = await client.get(
            f"{{ api_endpoint }}/{test_{{ snake_name }}.id}"{% if auth_required %},
            headers=auth_headers{% endif %}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    {% endif %}
```

### **Performance Testing Framework**

#### **Load Test Generator** (`templates/backend/load_test.py.j2`)
```python
"""
Load tests for {{ class_name }} API
Auto-generated performance tests for {{ domain_name }} domain
"""

import asyncio
import time
from typing import List
import pytest
from httpx import AsyncClient
from concurrent.futures import ThreadPoolExecutor


class Test{{ class_name }}Performance:
    """Performance test suite for {{ class_name }} API"""
    
    @pytest.mark.performance
    async def test_create_{{ snake_name }}_load(self, client: AsyncClient, auth_headers: dict):
        """Test {{ snake_name }} creation under load"""
        
        concurrent_requests = 50
        total_requests = 200
        
        async def create_{{ snake_name }}(session_id: int):
            """Create a {{ snake_name }} with unique data"""
            {{ snake_name }}_data = {
                {% for field in required_fields %}
                "{{ field.name }}": {% if field.type == 'string' %}f"load_test_{{ field.name }}_{session_id}"{% else %}session_id{% endif %},
                {% endfor %}
            }
            
            start_time = time.time()
            response = await client.post(
                "{{ api_endpoint }}",
                json={{ snake_name }}_data,
                headers=auth_headers
            )
            end_time = time.time()
            
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'session_id': session_id
            }
        
        # Execute load test
        start_time = time.time()
        
        # Create batches of concurrent requests
        results = []
        for batch_start in range(0, total_requests, concurrent_requests):
            batch_end = min(batch_start + concurrent_requests, total_requests)
            batch_tasks = [
                create_{{ snake_name }}(i) 
                for i in range(batch_start, batch_end)
            ]
            
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r['status_code'] == 201]
        failed_requests = [r for r in results if r['status_code'] != 201]
        
        response_times = [r['response_time'] for r in successful_requests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Assertions
        assert len(successful_requests) >= total_requests * 0.95  # 95% success rate
        assert avg_response_time < 1.0  # Average response time under 1 second
        assert max_response_time < 5.0  # Max response time under 5 seconds
        
        # Performance metrics
        throughput = len(successful_requests) / total_time
        assert throughput > 10  # At least 10 requests per second
        
        print(f"\n{{ class_name }} Load Test Results:")
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {len(successful_requests)}")
        print(f"Failed: {len(failed_requests)}")
        print(f"Success Rate: {len(successful_requests) / total_requests * 100:.2f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Throughput: {throughput:.2f} req/s")
        print(f"Avg Response Time: {avg_response_time:.3f}s")
        print(f"Min Response Time: {min_response_time:.3f}s")
        print(f"Max Response Time: {max_response_time:.3f}s")
```

---

*Continue to Section 7: Integration & Deployment...*