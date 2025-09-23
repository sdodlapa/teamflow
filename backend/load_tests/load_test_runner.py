"""
Comprehensive load testing suite for TeamFlow API
"""
import asyncio
import aiohttp
import json
import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import random
import string


@dataclass
class LoadTestResult:
    """Load test result data structure"""
    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    errors: List[str]
    duration: float


class LoadTestRunner:
    """Comprehensive load testing framework"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.results = []
    
    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()
        await self.authenticate()
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Authenticate and get access token"""
        try:
            # Create test user and authenticate
            auth_data = {
                "email": "loadtest@teamflow.com",
                "password": "loadtest123"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Authentication successful")
                else:
                    print("⚠️ Authentication failed, some tests may not work")
        except Exception as e:
            print(f"⚠️ Authentication error: {e}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request and measure performance"""
        url = f"{self.base_url}{endpoint}"
        request_headers = self.get_auth_headers()
        if headers:
            request_headers.update(headers)
        
        start_time = time.time()
        
        try:
            async with self.session.request(
                method, 
                url, 
                json=data,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = (time.time() - start_time) * 1000  # ms
                content = await response.text()
                
                return {
                    "success": True,
                    "status_code": response.status,
                    "response_time": response_time,
                    "content_length": len(content),
                    "error": None
                }
        
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": 408,
                "response_time": response_time,
                "content_length": 0,
                "error": "Request timeout"
            }
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": 0,
                "response_time": response_time,
                "content_length": 0,
                "error": str(e)
            }
    
    async def run_load_test(
        self,
        endpoint: str,
        method: str = "GET",
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        data_generator=None,
        test_name: str = None
    ) -> LoadTestResult:
        """Run load test for specific endpoint"""
        
        test_name = test_name or f"{method} {endpoint}"
        print(f"\n🚀 Starting load test: {test_name}")
        print(f"   Concurrent users: {concurrent_users}")
        print(f"   Requests per user: {requests_per_user}")
        print(f"   Total requests: {concurrent_users * requests_per_user}")
        
        start_time = time.time()
        tasks = []
        
        # Create tasks for concurrent execution
        for user_id in range(concurrent_users):
            task = asyncio.create_task(
                self.user_session(endpoint, method, requests_per_user, data_generator, user_id)
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Aggregate results
        all_responses = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                all_responses.extend(result)
        
        # Calculate statistics
        response_times = [r["response_time"] for r in all_responses]
        successful_requests = len([r for r in all_responses if r["success"]])
        failed_requests = len(all_responses) - successful_requests
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        total_requests = len(all_responses)
        requests_per_second = total_requests / duration if duration > 0 else 0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Collect error messages
        error_messages = list(set([r["error"] for r in all_responses if r["error"]]))
        
        result = LoadTestResult(
            endpoint=endpoint,
            method=method,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=round(avg_response_time, 2),
            min_response_time=round(min_response_time, 2),
            max_response_time=round(max_response_time, 2),
            p95_response_time=round(p95_response_time, 2),
            p99_response_time=round(p99_response_time, 2),
            requests_per_second=round(requests_per_second, 2),
            error_rate=round(error_rate, 2),
            errors=error_messages,
            duration=round(duration, 2)
        )
        
        self.results.append(result)
        self.print_test_result(result)
        
        return result
    
    async def user_session(
        self, 
        endpoint: str, 
        method: str, 
        requests_count: int, 
        data_generator, 
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Simulate individual user session"""
        responses = []
        
        for i in range(requests_count):
            # Generate request data if generator provided
            data = None
            if data_generator:
                data = data_generator(user_id, i)
            
            response = await self.make_request(method, endpoint, data)
            responses.append(response)
            
            # Small delay between requests to simulate real usage
            await asyncio.sleep(0.1)
        
        return responses
    
    def print_test_result(self, result: LoadTestResult):
        """Print formatted test results"""
        print(f"\n📊 Results for {result.method} {result.endpoint}:")
        print(f"   Total Requests: {result.total_requests}")
        print(f"   Successful: {result.successful_requests}")
        print(f"   Failed: {result.failed_requests}")
        print(f"   Error Rate: {result.error_rate}%")
        print(f"   Duration: {result.duration}s")
        print(f"   Requests/sec: {result.requests_per_second}")
        print(f"   Avg Response Time: {result.avg_response_time}ms")
        print(f"   P95 Response Time: {result.p95_response_time}ms")
        print(f"   P99 Response Time: {result.p99_response_time}ms")
        
        if result.errors:
            print(f"   Errors: {', '.join(result.errors[:3])}")
    
    def generate_test_data(self, endpoint: str):
        """Generate test data based on endpoint"""
        def data_generator(user_id: int, request_id: int):
            if "/tasks" in endpoint and "POST" in endpoint:
                return {
                    "title": f"Load Test Task {user_id}-{request_id}",
                    "description": f"Test task created by user {user_id}",
                    "priority": random.choice(["low", "medium", "high"]),
                    "status": "todo"
                }
            elif "/users" in endpoint and "POST" in endpoint:
                return {
                    "email": f"testuser{user_id}-{request_id}@loadtest.com",
                    "password": "testpass123",
                    "full_name": f"Test User {user_id}-{request_id}"
                }
            elif "/organizations" in endpoint and "POST" in endpoint:
                return {
                    "name": f"Load Test Org {user_id}-{request_id}",
                    "description": f"Test organization {user_id}-{request_id}"
                }
            return None
        
        return data_generator
    
    async def run_comprehensive_load_test(self):
        """Run comprehensive load test suite"""
        print("🚀 Starting Comprehensive Load Test Suite")
        print("=" * 50)
        
        # Test scenarios with different load patterns
        test_scenarios = [
            # Basic health checks
            {
                "name": "Health Check - Light Load",
                "endpoint": "/health",
                "method": "GET",
                "concurrent_users": 5,
                "requests_per_user": 10
            },
            {
                "name": "Health Check - Heavy Load", 
                "endpoint": "/health",
                "method": "GET",
                "concurrent_users": 50,
                "requests_per_user": 20
            },
            
            # API documentation
            {
                "name": "API Docs Load Test",
                "endpoint": "/docs",
                "method": "GET", 
                "concurrent_users": 10,
                "requests_per_user": 5
            },
            
            # Performance endpoints
            {
                "name": "Performance Dashboard",
                "endpoint": "/api/v1/performance/dashboard",
                "method": "GET",
                "concurrent_users": 10,
                "requests_per_user": 5
            },
            
            # Security endpoints
            {
                "name": "Security Dashboard",
                "endpoint": "/api/v1/security/dashboard",
                "method": "GET",
                "concurrent_users": 5,
                "requests_per_user": 10
            },
            
            # Task operations
            {
                "name": "List Tasks - Moderate Load",
                "endpoint": "/api/v1/tasks",
                "method": "GET",
                "concurrent_users": 20,
                "requests_per_user": 15
            },
            
            # User operations
            {
                "name": "User Profile - High Load",
                "endpoint": "/api/v1/users/me",
                "method": "GET",
                "concurrent_users": 30,
                "requests_per_user": 20
            },
            
            # Database intensive operations
            {
                "name": "Search Operations",
                "endpoint": "/api/v1/search/tasks?q=test",
                "method": "GET",
                "concurrent_users": 15,
                "requests_per_user": 10
            }
        ]
        
        # Run all test scenarios
        for scenario in test_scenarios:
            data_gen = self.generate_test_data(scenario["endpoint"])
            await self.run_load_test(
                endpoint=scenario["endpoint"],
                method=scenario["method"],
                concurrent_users=scenario["concurrent_users"],
                requests_per_user=scenario["requests_per_user"],
                data_generator=data_gen,
                test_name=scenario["name"]
            )
            
            # Wait between tests
            await asyncio.sleep(2)
        
        self.print_summary_report()
    
    def print_summary_report(self):
        """Print comprehensive summary report"""
        print("\n" + "=" * 70)
        print("📋 LOAD TEST SUMMARY REPORT")
        print("=" * 70)
        
        if not self.results:
            print("No test results available")
            return
        
        total_requests = sum(r.total_requests for r in self.results)
        total_successful = sum(r.successful_requests for r in self.results)
        total_failed = sum(r.failed_requests for r in self.results)
        
        avg_response_times = [r.avg_response_time for r in self.results]
        avg_rps = [r.requests_per_second for r in self.results]
        
        print(f"Total Tests Run: {len(self.results)}")
        print(f"Total Requests: {total_requests}")
        print(f"Total Successful: {total_successful}")
        print(f"Total Failed: {total_failed}")
        print(f"Overall Success Rate: {(total_successful/total_requests*100):.2f}%")
        print(f"Average Response Time: {statistics.mean(avg_response_times):.2f}ms")
        print(f"Average RPS: {statistics.mean(avg_rps):.2f}")
        
        print("\n📊 DETAILED RESULTS:")
        print("-" * 70)
        
        for result in self.results:
            status = "✅" if result.error_rate < 5 else "⚠️" if result.error_rate < 15 else "❌"
            print(f"{status} {result.endpoint} | "
                  f"RPS: {result.requests_per_second:.1f} | "
                  f"Avg: {result.avg_response_time:.0f}ms | "
                  f"P95: {result.p95_response_time:.0f}ms | "
                  f"Errors: {result.error_rate:.1f}%")
        
        print("\n🎯 PERFORMANCE BENCHMARKS:")
        print("-" * 70)
        
        # Performance benchmarks
        excellent_tests = [r for r in self.results if r.avg_response_time < 200 and r.error_rate < 1]
        good_tests = [r for r in self.results if r.avg_response_time < 500 and r.error_rate < 5]
        poor_tests = [r for r in self.results if r.avg_response_time >= 500 or r.error_rate >= 5]
        
        print(f"🏆 Excellent Performance: {len(excellent_tests)} tests")
        print(f"✅ Good Performance: {len(good_tests)} tests") 
        print(f"⚠️ Poor Performance: {len(poor_tests)} tests")
        
        if poor_tests:
            print("\n🔍 TESTS NEEDING OPTIMIZATION:")
            for test in poor_tests:
                print(f"   • {test.endpoint}: {test.avg_response_time:.0f}ms avg, {test.error_rate:.1f}% errors")
        
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 70)
        
        recommendations = []
        
        if statistics.mean(avg_response_times) > 500:
            recommendations.append("• Overall response times are high - consider caching and optimization")
        
        if total_failed / total_requests > 0.05:
            recommendations.append("• Error rate is above 5% - investigate error causes")
        
        if statistics.mean(avg_rps) < 10:
            recommendations.append("• Low throughput detected - consider connection pooling optimization")
        
        slow_endpoints = [r for r in self.results if r.avg_response_time > 1000]
        if slow_endpoints:
            recommendations.append("• Some endpoints are very slow (>1s) - prioritize optimization")
        
        if not recommendations:
            recommendations.append("• Performance looks good! Consider stress testing with higher loads")
        
        for rec in recommendations:
            print(rec)
        
        print("=" * 70)
    
    def export_results(self, filename: str = None):
        """Export results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "total_tests": len(self.results),
                "total_requests": sum(r.total_requests for r in self.results),
                "total_successful": sum(r.successful_requests for r in self.results),
                "total_failed": sum(r.failed_requests for r in self.results)
            },
            "results": [asdict(result) for result in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📄 Results exported to {filename}")


async def main():
    """Main load testing function"""
    runner = LoadTestRunner("http://localhost:8000")
    
    try:
        await runner.setup()
        await runner.run_comprehensive_load_test()
        runner.export_results()
    finally:
        await runner.teardown()


if __name__ == "__main__":
    print("🚀 TeamFlow Load Testing Suite")
    print("=" * 50)
    asyncio.run(main())