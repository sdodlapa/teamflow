# 🚀 PHASE 3: IMPLEMENTATION GUIDE
## Section 5: Integration & Testing Implementation

---

## 🧪 INTEGRATION & TESTING IMPLEMENTATION

### **Implementation Strategy**

Comprehensive integration and testing framework ensures reliability, performance, and quality of generated applications while providing automated validation at every stage of the generation process.

### **Testing Architecture Overview**

```
Testing Pyramid:
1. Unit Tests (Generated code validation)
2. Integration Tests (Component interaction)
3. API Tests (End-to-end functionality)
4. Performance Tests (Load and stress testing)
5. Security Tests (Vulnerability assessment)
6. User Acceptance Tests (Business logic validation)
```

### **Step 1: Automated Test Generation System**

#### **File: `backend/app/template_system/testing/test_generator.py`**

**Implementation Strategy:**
- Generate comprehensive test suites for all generated code
- Create realistic test data factories
- Implement edge case testing scenarios
- Support multiple testing frameworks and patterns

**Test Generation Core:**
```python
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import ast
import inspect
from app.template_system.core.domain_config import DomainConfig, EntityConfig
from app.template_system.core.generation_result import GenerationResult

@dataclass
class TestScenario:
    name: str
    description: str
    test_type: str  # 'positive', 'negative', 'edge_case', 'performance'
    setup_data: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    validation_rules: List[str]

class ComprehensiveTestGenerator:
    """Generate comprehensive test suites for generated applications"""
    
    def __init__(self, template_engine: TemplateEngine, test_config: TestConfiguration):
        self.template_engine = template_engine
        self.test_config = test_config
        self.scenario_generator = TestScenarioGenerator()
        self.data_factory_generator = TestDataFactoryGenerator()
        self.coverage_analyzer = CoverageAnalyzer()
        
    def generate_complete_test_suite(self, domain_config: DomainConfig, 
                                   generation_result: GenerationResult) -> TestSuiteResult:
        """Generate complete test suite for generated application"""
        
        test_suite_result = TestSuiteResult(domain_config.domain.name)
        
        # Generate test data factories first
        data_factories = self.data_factory_generator.generate_factories(domain_config)
        test_suite_result.add_data_factories(data_factories)
        
        # Generate tests for each entity
        for entity_name, entity_config in domain_config.entities.items():
            
            # Unit Tests
            unit_tests = self._generate_entity_unit_tests(
                entity_name, entity_config, domain_config
            )
            test_suite_result.add_unit_tests(entity_name, unit_tests)
            
            # API Tests
            api_tests = self._generate_entity_api_tests(
                entity_name, entity_config, domain_config
            )
            test_suite_result.add_api_tests(entity_name, api_tests)
            
            # Integration Tests
            integration_tests = self._generate_entity_integration_tests(
                entity_name, entity_config, domain_config
            )
            test_suite_result.add_integration_tests(entity_name, integration_tests)
        
        # Generate cross-entity relationship tests
        relationship_tests = self._generate_relationship_tests(domain_config)
        test_suite_result.add_relationship_tests(relationship_tests)
        
        # Generate performance tests
        performance_tests = self._generate_performance_tests(domain_config)
        test_suite_result.add_performance_tests(performance_tests)
        
        # Generate security tests
        security_tests = self._generate_security_tests(domain_config)
        test_suite_result.add_security_tests(security_tests)
        
        # Generate end-to-end workflow tests
        e2e_tests = self._generate_e2e_workflow_tests(domain_config)
        test_suite_result.add_e2e_tests(e2e_tests)
        
        return test_suite_result
    
    def _generate_entity_unit_tests(self, entity_name: str, entity_config: EntityConfig,
                                   domain_config: DomainConfig) -> List[TestFile]:
        """Generate comprehensive unit tests for an entity"""
        
        test_files = []
        
        # Model Tests
        model_tests = self._generate_model_unit_tests(entity_name, entity_config)
        test_files.append(model_tests)
        
        # Schema Tests
        schema_tests = self._generate_schema_unit_tests(entity_name, entity_config)
        test_files.append(schema_tests)
        
        # Service Tests (if applicable)
        if entity_config.has_custom_business_logic:
            service_tests = self._generate_service_unit_tests(entity_name, entity_config)
            test_files.append(service_tests)
        
        return test_files
    
    def _generate_model_unit_tests(self, entity_name: str, 
                                  entity_config: EntityConfig) -> TestFile:
        """Generate unit tests for SQLAlchemy model"""
        
        # Generate test scenarios
        scenarios = []
        
        # Basic CRUD scenarios
        scenarios.extend(self._generate_crud_scenarios(entity_name, entity_config))
        
        # Validation scenarios
        scenarios.extend(self._generate_validation_scenarios(entity_name, entity_config))
        
        # Relationship scenarios
        scenarios.extend(self._generate_relationship_scenarios(entity_name, entity_config))
        
        # Edge case scenarios
        scenarios.extend(self._generate_edge_case_scenarios(entity_name, entity_config))
        
        # Build test file context
        context = {
            'entity_name': entity_name,
            'class_name': self._to_pascal_case(entity_name),
            'test_scenarios': scenarios,
            'imports': self._generate_test_imports(entity_config),
            'fixtures': self._generate_test_fixtures(entity_config),
            'helper_methods': self._generate_test_helpers(entity_config)
        }
        
        # Render test template
        test_template = self.template_engine.get_template('tests/model_test.py.j2')
        test_code = test_template.render(context)
        
        return TestFile(
            file_path=f"tests/unit/test_{entity_name.lower()}_model.py",
            content=test_code,
            test_count=len(scenarios),
            coverage_targets=['model', 'validation', 'relationships']
        )
    
    def _generate_crud_scenarios(self, entity_name: str, 
                                entity_config: EntityConfig) -> List[TestScenario]:
        """Generate CRUD test scenarios"""
        
        scenarios = []
        
        # Create scenario
        scenarios.append(TestScenario(
            name=f"test_create_{entity_name.lower()}_success",
            description=f"Test successful creation of {entity_name}",
            test_type="positive",
            setup_data=self._generate_valid_entity_data(entity_config),
            expected_outcome={
                'status': 'success',
                'entity_created': True,
                'fields_populated': True
            },
            validation_rules=[
                'entity.id is not None',
                'entity.created_at is not None',
                'all required fields are populated'
            ]
        ))
        
        # Read scenario
        scenarios.append(TestScenario(
            name=f"test_read_{entity_name.lower()}_success",
            description=f"Test successful retrieval of {entity_name}",
            test_type="positive",
            setup_data={'create_entity': True},
            expected_outcome={
                'status': 'success',
                'entity_found': True,
                'data_matches': True
            },
            validation_rules=[
                'entity is not None',
                'entity.id matches created entity',
                'all fields match original data'
            ]
        ))
        
        # Update scenario
        scenarios.append(TestScenario(
            name=f"test_update_{entity_name.lower()}_success",
            description=f"Test successful update of {entity_name}",
            test_type="positive",
            setup_data={
                'create_entity': True,
                'update_data': self._generate_update_data(entity_config)
            },
            expected_outcome={
                'status': 'success',
                'entity_updated': True,
                'updated_at_changed': True
            },
            validation_rules=[
                'entity.updated_at > entity.created_at',
                'updated fields reflect new values',
                'unchanged fields remain same'
            ]
        ))
        
        # Delete scenario
        scenarios.append(TestScenario(
            name=f"test_delete_{entity_name.lower()}_success", 
            description=f"Test successful deletion of {entity_name}",
            test_type="positive",
            setup_data={'create_entity': True},
            expected_outcome={
                'status': 'success',
                'entity_deleted': True
            },
            validation_rules=[
                'entity no longer exists in database',
                'related entities handled correctly'
            ]
        ))
        
        return scenarios
    
    def _generate_validation_scenarios(self, entity_name: str,
                                     entity_config: EntityConfig) -> List[TestScenario]:
        """Generate validation test scenarios"""
        
        scenarios = []
        
        for field in entity_config.fields:
            if field.required:
                # Missing required field scenario
                scenarios.append(TestScenario(
                    name=f"test_{entity_name.lower()}_missing_{field.name}_fails",
                    description=f"Test creation fails when {field.name} is missing",
                    test_type="negative",
                    setup_data=self._generate_data_missing_field(entity_config, field.name),
                    expected_outcome={
                        'status': 'error',
                        'error_type': 'validation_error',
                        'field_error': field.name
                    },
                    validation_rules=[
                        f'ValidationError raised for {field.name}',
                        'entity not created in database'
                    ]
                ))
            
            if field.validation:
                # Field validation scenarios
                for validation_rule in field.validation:
                    scenarios.append(self._generate_field_validation_scenario(
                        entity_name, field, validation_rule
                    ))
        
        return scenarios
```

### **Step 2: Integration Testing Framework**

#### **File: `backend/app/template_system/testing/integration_tester.py`**

**Implementation Strategy:**
- Test component interactions across the generated application
- Validate data flow between frontend and backend
- Test authentication and authorization integration
- Verify database transaction handling

**Integration Testing System:**
```python
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from dataclasses import dataclass

@dataclass 
class IntegrationTestSuite:
    name: str
    setup_scripts: List[str]
    test_cases: List[IntegrationTestCase]
    teardown_scripts: List[str]
    dependencies: List[str]

class IntegrationTestingFramework:
    """Comprehensive integration testing framework"""
    
    def __init__(self, test_environment: TestEnvironment):
        self.test_environment = test_environment
        self.database_manager = TestDatabaseManager()
        self.api_client = TestAPIClient()
        self.frontend_tester = FrontendIntegrationTester()
        
    async def run_integration_test_suite(self, domain_config: DomainConfig) -> IntegrationTestResult:
        """Run complete integration test suite for generated application"""
        
        result = IntegrationTestResult(domain_config.domain.name)
        
        try:
            # Setup test environment
            await self._setup_test_environment(domain_config)
            
            # Run database integration tests
            db_tests = await self._run_database_integration_tests(domain_config)
            result.add_test_results('database', db_tests)
            
            # Run API integration tests
            api_tests = await self._run_api_integration_tests(domain_config)
            result.add_test_results('api', api_tests)
            
            # Run frontend-backend integration tests
            frontend_tests = await self._run_frontend_integration_tests(domain_config)
            result.add_test_results('frontend', frontend_tests)
            
            # Run authentication integration tests
            auth_tests = await self._run_authentication_integration_tests(domain_config)
            result.add_test_results('authentication', auth_tests)
            
            # Run workflow integration tests
            workflow_tests = await self._run_workflow_integration_tests(domain_config)
            result.add_test_results('workflows', workflow_tests)
            
        finally:
            # Cleanup test environment
            await self._cleanup_test_environment()
        
        return result
    
    async def _run_database_integration_tests(self, domain_config: DomainConfig) -> List[TestResult]:
        """Run database integration tests"""
        
        test_results = []
        
        # Test database connections
        connection_test = await self._test_database_connections()
        test_results.append(connection_test)
        
        # Test entity relationships
        for entity_name, entity_config in domain_config.entities.items():
            if entity_config.relationships:
                relationship_tests = await self._test_entity_relationships(
                    entity_name, entity_config
                )
                test_results.extend(relationship_tests)
        
        # Test database constraints
        constraint_tests = await self._test_database_constraints(domain_config)
        test_results.extend(constraint_tests)
        
        # Test database transactions
        transaction_tests = await self._test_database_transactions(domain_config)
        test_results.extend(transaction_tests)
        
        return test_results
    
    async def _run_api_integration_tests(self, domain_config: DomainConfig) -> List[TestResult]:
        """Run API integration tests"""
        
        test_results = []
        
        # Test API authentication flow
        auth_flow_test = await self._test_api_authentication_flow()
        test_results.append(auth_flow_test)
        
        # Test CRUD operations for each entity
        for entity_name, entity_config in domain_config.entities.items():
            crud_tests = await self._test_entity_crud_operations(entity_name, entity_config)
            test_results.extend(crud_tests)
        
        # Test API error handling
        error_handling_tests = await self._test_api_error_handling(domain_config)
        test_results.extend(error_handling_tests)
        
        # Test API rate limiting
        rate_limiting_tests = await self._test_api_rate_limiting(domain_config)
        test_results.extend(rate_limiting_tests)
        
        return test_results
    
    async def _test_entity_crud_operations(self, entity_name: str, 
                                         entity_config: EntityConfig) -> List[TestResult]:
        """Test CRUD operations for an entity via API"""
        
        test_results = []
        base_url = f"/api/v1/{entity_name.lower()}s"
        
        # Test CREATE operation
        create_data = self._generate_test_entity_data(entity_config)
        create_response = await self.api_client.post(base_url, json=create_data)
        
        create_test = TestResult(
            name=f"test_api_create_{entity_name.lower()}",
            passed=create_response.status == 201,
            details={
                'status_code': create_response.status,
                'response_data': await create_response.json() if create_response.status == 201 else None,
                'error': await create_response.text() if create_response.status != 201 else None
            }
        )
        test_results.append(create_test)
        
        if create_response.status == 201:
            created_entity = await create_response.json()
            entity_id = created_entity['id']
            
            # Test READ operation
            read_response = await self.api_client.get(f"{base_url}/{entity_id}")
            read_test = TestResult(
                name=f"test_api_read_{entity_name.lower()}",
                passed=read_response.status == 200,
                details={
                    'status_code': read_response.status,
                    'data_matches': self._verify_entity_data_matches(
                        created_entity, await read_response.json() if read_response.status == 200 else None
                    )
                }
            )
            test_results.append(read_test)
            
            # Test UPDATE operation
            update_data = self._generate_update_entity_data(entity_config)
            update_response = await self.api_client.put(f"{base_url}/{entity_id}", json=update_data)
            update_test = TestResult(
                name=f"test_api_update_{entity_name.lower()}",
                passed=update_response.status == 200,
                details={
                    'status_code': update_response.status,
                    'updated_fields': update_data.keys()
                }
            )
            test_results.append(update_test)
            
            # Test DELETE operation
            delete_response = await self.api_client.delete(f"{base_url}/{entity_id}")
            delete_test = TestResult(
                name=f"test_api_delete_{entity_name.lower()}",
                passed=delete_response.status == 204,
                details={'status_code': delete_response.status}
            )
            test_results.append(delete_test)
            
            # Verify entity is deleted
            verify_delete_response = await self.api_client.get(f"{base_url}/{entity_id}")
            verify_delete_test = TestResult(
                name=f"test_api_verify_delete_{entity_name.lower()}",
                passed=verify_delete_response.status == 404,
                details={'status_code': verify_delete_response.status}
            )
            test_results.append(verify_delete_test)
        
        return test_results
```

### **Step 3: Performance Testing System**

#### **File: `backend/app/template_system/testing/performance_tester.py`**

**Implementation Strategy:**
- Automated load testing for generated APIs
- Database performance benchmarking
- Frontend performance monitoring
- Scalability testing and bottleneck identification

**Performance Testing Framework:**
```python
import asyncio
import time
import statistics
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import psutil

@dataclass
class PerformanceMetrics:
    response_time_ms: float
    throughput_rps: float
    memory_usage_mb: float
    cpu_usage_percent: float
    database_query_time_ms: float
    error_rate_percent: float

class PerformanceTestingFramework:
    """Comprehensive performance testing for generated applications"""
    
    def __init__(self, test_config: PerformanceTestConfig):
        self.test_config = test_config
        self.load_generator = LoadGenerator()
        self.metrics_collector = MetricsCollector()
        self.bottleneck_analyzer = BottleneckAnalyzer()
        
    async def run_performance_test_suite(self, domain_config: DomainConfig) -> PerformanceTestResult:
        """Run comprehensive performance test suite"""
        
        result = PerformanceTestResult(domain_config.domain.name)
        
        # Run baseline performance tests
        baseline_metrics = await self._run_baseline_tests(domain_config)
        result.add_baseline_metrics(baseline_metrics)
        
        # Run load testing
        load_test_results = await self._run_load_tests(domain_config)
        result.add_load_test_results(load_test_results)
        
        # Run stress testing
        stress_test_results = await self._run_stress_tests(domain_config)
        result.add_stress_test_results(stress_test_results)
        
        # Run scalability testing
        scalability_results = await self._run_scalability_tests(domain_config)
        result.add_scalability_results(scalability_results)
        
        # Analyze bottlenecks
        bottleneck_analysis = await self.bottleneck_analyzer.analyze_performance_data(result)
        result.add_bottleneck_analysis(bottleneck_analysis)
        
        # Generate performance recommendations
        recommendations = self._generate_performance_recommendations(result)
        result.add_recommendations(recommendations)
        
        return result
    
    async def _run_load_tests(self, domain_config: DomainConfig) -> Dict[str, LoadTestResult]:
        """Run load tests for all entities"""
        
        load_test_results = {}
        
        for entity_name, entity_config in domain_config.entities.items():
            
            # Test different load levels
            load_levels = [10, 50, 100, 250, 500]  # concurrent users
            entity_results = {}
            
            for load_level in load_levels:
                print(f"Running load test for {entity_name} with {load_level} concurrent users...")
                
                # Generate test scenarios
                scenarios = self._generate_load_test_scenarios(entity_name, entity_config)
                
                # Run load test
                load_result = await self._execute_load_test(
                    entity_name, scenarios, load_level
                )
                
                entity_results[f"{load_level}_users"] = load_result
                
                # Break if error rate exceeds threshold
                if load_result.error_rate > self.test_config.max_error_rate:
                    print(f"Breaking load test for {entity_name} - error rate too high: {load_result.error_rate}%")
                    break
            
            load_test_results[entity_name] = entity_results
        
        return load_test_results
    
    async def _execute_load_test(self, entity_name: str, scenarios: List[LoadTestScenario],
                               concurrent_users: int) -> LoadTestResult:
        """Execute load test with specified concurrent users"""
        
        # Start metrics collection
        metrics_task = asyncio.create_task(self._collect_performance_metrics())
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_users)
        
        # Execute test scenarios
        start_time = time.time()
        tasks = []
        
        for _ in range(self.test_config.requests_per_user):
            for scenario in scenarios:
                task = asyncio.create_task(
                    self._execute_load_test_scenario(scenario, semaphore)
                )
                tasks.append(task)
        
        # Wait for all requests to complete
        scenario_results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Stop metrics collection
        metrics_task.cancel()
        
        # Analyze results
        total_requests = len(scenario_results)
        successful_requests = len([r for r in scenario_results if isinstance(r, ScenarioResult) and r.success])
        failed_requests = total_requests - successful_requests
        
        response_times = [r.response_time for r in scenario_results if isinstance(r, ScenarioResult) and r.success]
        
        return LoadTestResult(
            entity_name=entity_name,
            concurrent_users=concurrent_users,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            error_rate=(failed_requests / total_requests) * 100,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            median_response_time=statistics.median(response_times) if response_times else 0,
            p95_response_time=self._calculate_percentile(response_times, 95) if response_times else 0,
            p99_response_time=self._calculate_percentile(response_times, 99) if response_times else 0,
            throughput_rps=successful_requests / (end_time - start_time),
            test_duration=end_time - start_time
        )
    
    async def _execute_load_test_scenario(self, scenario: LoadTestScenario, 
                                        semaphore: asyncio.Semaphore) -> ScenarioResult:
        """Execute a single load test scenario"""
        
        async with semaphore:
            start_time = time.time()
            
            try:
                # Execute HTTP request
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=scenario.method,
                        url=scenario.url,
                        json=scenario.payload,
                        headers=scenario.headers
                    ) as response:
                        response_data = await response.text()
                        end_time = time.time()
                        
                        return ScenarioResult(
                            scenario_name=scenario.name,
                            success=200 <= response.status < 400,
                            response_time=(end_time - start_time) * 1000,  # ms
                            status_code=response.status,
                            response_size=len(response_data)
                        )
                        
            except Exception as e:
                end_time = time.time()
                return ScenarioResult(
                    scenario_name=scenario.name,
                    success=False,
                    response_time=(end_time - start_time) * 1000,
                    status_code=0,
                    error=str(e)
                )
```

### **Step 4: Security Testing Framework**

#### **File: `backend/app/template_system/testing/security_tester.py`**

**Implementation Strategy:**
- Automated vulnerability scanning
- Authentication and authorization testing
- Input validation and injection testing
- Security compliance verification

**Security Testing System:**
```python
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from dataclasses import dataclass

@dataclass
class SecurityVulnerability:
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'injection', 'authentication', 'authorization', etc.
    description: str
    affected_endpoint: str
    proof_of_concept: str
    remediation: str

class SecurityTestingFramework:
    """Comprehensive security testing for generated applications"""
    
    def __init__(self, security_config: SecurityTestConfig):
        self.security_config = security_config
        self.vulnerability_scanner = VulnerabilityScanner()
        self.auth_tester = AuthenticationTester()
        self.injection_tester = InjectionTester()
        
    async def run_security_test_suite(self, domain_config: DomainConfig) -> SecurityTestResult:
        """Run comprehensive security test suite"""
        
        result = SecurityTestResult(domain_config.domain.name)
        
        # Authentication and authorization tests
        auth_results = await self._run_authentication_tests(domain_config)
        result.add_auth_test_results(auth_results)
        
        # Input validation tests
        validation_results = await self._run_input_validation_tests(domain_config)
        result.add_validation_test_results(validation_results)
        
        # Injection attack tests
        injection_results = await self._run_injection_tests(domain_config)
        result.add_injection_test_results(injection_results)
        
        # Access control tests
        access_control_results = await self._run_access_control_tests(domain_config)
        result.add_access_control_test_results(access_control_results)
        
        # Data exposure tests
        data_exposure_results = await self._run_data_exposure_tests(domain_config)
        result.add_data_exposure_test_results(data_exposure_results)
        
        # Generate security report
        security_report = self._generate_security_report(result)
        result.add_security_report(security_report)
        
        return result
    
    async def _run_injection_tests(self, domain_config: DomainConfig) -> Dict[str, List[SecurityTestResult]]:
        """Run SQL injection and other injection tests"""
        
        injection_results = {}
        
        for entity_name, entity_config in domain_config.entities.items():
            entity_results = []
            
            # SQL Injection tests
            sql_injection_tests = await self._test_sql_injection(entity_name, entity_config)
            entity_results.extend(sql_injection_tests)
            
            # NoSQL Injection tests (if applicable)
            if entity_config.uses_nosql:
                nosql_injection_tests = await self._test_nosql_injection(entity_name, entity_config)
                entity_results.extend(nosql_injection_tests)
            
            # Command Injection tests
            command_injection_tests = await self._test_command_injection(entity_name, entity_config)
            entity_results.extend(command_injection_tests)
            
            # XSS tests (for text fields)
            xss_tests = await self._test_xss_vulnerabilities(entity_name, entity_config)
            entity_results.extend(xss_tests)
            
            injection_results[entity_name] = entity_results
        
        return injection_results
    
    async def _test_sql_injection(self, entity_name: str, 
                                entity_config: EntityConfig) -> List[SecurityTestResult]:
        """Test for SQL injection vulnerabilities"""
        
        test_results = []
        base_url = f"/api/v1/{entity_name.lower()}s"
        
        # Common SQL injection payloads
        sql_payloads = [
            "1' OR '1'='1",
            "1'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users --",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables) > 0 --"
        ]
        
        # Test each field that might be vulnerable
        for field in entity_config.fields:
            if field.type in ['string', 'text']:
                
                for payload in sql_payloads:
                    # Test in query parameters
                    query_test = await self._test_sql_injection_in_query(
                        base_url, field.name, payload
                    )
                    test_results.append(query_test)
                    
                    # Test in request body
                    body_test = await self._test_sql_injection_in_body(
                        base_url, field.name, payload
                    )
                    test_results.append(body_test)
        
        return test_results
    
    async def _test_sql_injection_in_query(self, base_url: str, field_name: str, 
                                         payload: str) -> SecurityTestResult:
        """Test SQL injection in query parameters"""
        
        url = f"{base_url}?{field_name}={payload}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    response_text = await response.text()
                    
                    # Check for SQL error messages that might indicate vulnerability
                    sql_error_indicators = [
                        'sql syntax',
                        'mysql_fetch',
                        'ora-01756',
                        'microsoft ole db',
                        'sqlite_step'
                    ]
                    
                    vulnerability_detected = any(
                        indicator in response_text.lower() 
                        for indicator in sql_error_indicators
                    )
                    
                    return SecurityTestResult(
                        test_name=f"sql_injection_query_{field_name}",
                        vulnerability_detected=vulnerability_detected,
                        severity='high' if vulnerability_detected else 'none',
                        details={
                            'payload': payload,
                            'response_status': response.status,
                            'response_contains_sql_errors': vulnerability_detected,
                            'url': url
                        }
                    )
                    
            except Exception as e:
                return SecurityTestResult(
                    test_name=f"sql_injection_query_{field_name}",
                    vulnerability_detected=False,
                    severity='none',
                    details={'error': str(e), 'payload': payload}
                )
```

### **Step 5: Continuous Integration Pipeline**

#### **File: `backend/app/template_system/ci/pipeline_generator.py`**

**Implementation Strategy:**
- Generate CI/CD pipelines for generated applications
- Automated testing on every commit
- Security scanning integration
- Performance regression testing

**CI Pipeline Generation:**
```python
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

@dataclass
class CIPipelineConfig:
    stages: List[str]
    test_frameworks: List[str]
    deployment_targets: List[str]
    security_scanning: bool
    performance_testing: bool

class CIPipelineGenerator:
    """Generate CI/CD pipelines for generated applications"""
    
    def __init__(self, template_engine: TemplateEngine):
        self.template_engine = template_engine
        
    def generate_github_actions_pipeline(self, domain_config: DomainConfig, 
                                       pipeline_config: CIPipelineConfig) -> str:
        """Generate GitHub Actions workflow"""
        
        context = {
            'domain_name': domain_config.domain.name,
            'python_version': '3.11',
            'node_version': '18',
            'stages': pipeline_config.stages,
            'test_frameworks': pipeline_config.test_frameworks,
            'deployment_targets': pipeline_config.deployment_targets,
            'security_scanning': pipeline_config.security_scanning,
            'performance_testing': pipeline_config.performance_testing,
            'database_services': self._get_database_services(domain_config),
            'environment_variables': self._get_environment_variables(domain_config)
        }
        
        pipeline_template = self.template_engine.get_template('ci/github_actions.yml.j2')
        return pipeline_template.render(context)
    
    def generate_docker_compose_test(self, domain_config: DomainConfig) -> str:
        """Generate Docker Compose configuration for testing"""
        
        context = {
            'domain_name': domain_config.domain.name,
            'services': self._get_test_services(domain_config),
            'networks': self._get_test_networks(domain_config),
            'volumes': self._get_test_volumes(domain_config)
        }
        
        compose_template = self.template_engine.get_template('ci/docker-compose.test.yml.j2')
        return compose_template.render(context)
```

---

*Continue to Section 6: CLI Development Implementation...*