"""
Comprehensive Performance Testing and Validation Suite for Phase 3 Day 6
"""
import asyncio
import aiohttp
import json
import time
import sys
import os
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PerformanceValidator:
    """Validate Phase 3 Day 6 performance optimization features"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = []
    
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
            # Try to get admin token for performance endpoints
            auth_data = {
                "email": "admin@teamflow.com",
                "password": "admin123"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Admin authentication successful")
                else:
                    print("⚠️ Admin authentication failed, trying user auth")
                    # Try regular user
                    auth_data["email"] = "user@teamflow.com"
                    auth_data["password"] = "user123"
                    
                    async with self.session.post(
                        f"{self.base_url}/api/v1/auth/login",
                        json=auth_data
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.auth_token = data.get("access_token")
                            print("✅ User authentication successful")
        except Exception as e:
            print(f"⚠️ Authentication error: {e}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_endpoint(self, endpoint: str, expected_status: int = 200, method: str = "GET") -> Dict[str, Any]:
        """Test a specific endpoint and measure performance"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_auth_headers()
        
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response_time = (time.time() - start_time) * 1000  # ms
                content = await response.text()
                
                # Try to parse JSON
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    data = {"content": content[:200]}  # First 200 chars if not JSON
                
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status,
                    "response_time_ms": round(response_time, 2),
                    "content_length": len(content),
                    "success": response.status == expected_status,
                    "data": data
                }
                
                return result
                
        except asyncio.TimeoutError:
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 408,
                "response_time_ms": 30000,
                "content_length": 0,
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time_ms": (time.time() - start_time) * 1000,
                "content_length": 0,
                "success": False,
                "error": str(e)
            }
    
    async def validate_performance_features(self):
        """Validate all performance optimization features"""
        print("🚀 Validating Phase 3 Day 6: Performance Optimization Features")
        print("=" * 70)
        
        # Test 1: Basic application health
        print("\n📋 Test 1: Application Health & Startup")
        health_result = await self.test_endpoint("/health")
        self.test_results.append(health_result)
        
        if health_result["success"]:
            print(f"✅ Application healthy ({health_result['response_time_ms']}ms)")
        else:
            print(f"❌ Application not healthy: {health_result.get('error', 'Unknown error')}")
            return  # Can't continue if app is not healthy
        
        # Test 2: Performance monitoring endpoints
        print("\n📊 Test 2: Performance Monitoring System")
        
        performance_endpoints = [
            "/api/v1/performance/dashboard",
            "/api/v1/performance/metrics",
            "/api/v1/performance/health",
            "/api/v1/performance/system/resources",
            "/api/v1/performance/api/endpoints"
        ]
        
        for endpoint in performance_endpoints:
            result = await self.test_endpoint(endpoint)
            self.test_results.append(result)
            
            if result["success"]:
                print(f"✅ {endpoint.split('/')[-1]} endpoint working ({result['response_time_ms']}ms)")
            else:
                print(f"❌ {endpoint.split('/')[-1]} endpoint failed: {result.get('error', f'Status {result['status_code']}')}")
        
        # Test 3: Database performance features
        print("\n🗃️ Test 3: Database Performance Features")
        
        database_endpoints = [
            "/api/v1/performance/database/analysis",
            "/api/v1/performance/database/slow-queries",
            "/api/v1/performance/database/indexes"
        ]
        
        for endpoint in database_endpoints:
            result = await self.test_endpoint(endpoint)
            self.test_results.append(result)
            
            if result["success"]:
                print(f"✅ Database {endpoint.split('/')[-1]} analysis working ({result['response_time_ms']}ms)")
                # Check if we got meaningful data
                if isinstance(result["data"], dict) and result["data"]:
                    print(f"   📊 Returned {len(str(result['data']))} chars of analysis data")
            else:
                print(f"❌ Database {endpoint.split('/')[-1]} analysis failed: {result.get('error', f'Status {result['status_code']}')}")
        
        # Test 4: Cache performance
        print("\n💾 Test 4: Cache Performance System")
        
        cache_result = await self.test_endpoint("/api/v1/performance/cache/statistics")
        self.test_results.append(cache_result)
        
        if cache_result["success"]:
            print(f"✅ Cache statistics endpoint working ({cache_result['response_time_ms']}ms)")
            cache_data = cache_result.get("data", {})
            if "cache_stats" in cache_data:
                print(f"   💾 Cache system operational")
        else:
            print(f"❌ Cache statistics failed: {cache_result.get('error', f'Status {cache_result['status_code']}')}")
        
        # Test 5: Performance optimization actions
        print("\n⚡ Test 5: Performance Optimization Actions")
        
        # Test database analysis trigger
        analyze_result = await self.test_endpoint("/api/v1/performance/database/analyze", method="POST")
        self.test_results.append(analyze_result)
        
        if analyze_result["success"]:
            print(f"✅ Database analysis trigger working ({analyze_result['response_time_ms']}ms)")
        else:
            print(f"❌ Database analysis trigger failed: {analyze_result.get('error', f'Status {analyze_result['status_code']}')}")
        
        # Test 6: Performance reports
        print("\n📄 Test 6: Performance Reporting")
        
        report_result = await self.test_endpoint("/api/v1/performance/report")
        self.test_results.append(report_result)
        
        if report_result["success"]:
            print(f"✅ Performance report generation working ({report_result['response_time_ms']}ms)")
            report_data = report_result.get("data", {})
            if "executive_summary" in report_data:
                print(f"   📊 Report contains executive summary and metrics")
        else:
            print(f"❌ Performance report failed: {report_result.get('error', f'Status {report_result['status_code']}')}")
        
        # Test 7: Response time validation
        print("\n⏱️ Test 7: Response Time Performance")
        
        fast_endpoints = ["/health", "/api/v1/performance/health"]
        for endpoint in fast_endpoints:
            result = await self.test_endpoint(endpoint)
            
            if result["success"] and result["response_time_ms"] < 200:
                print(f"✅ {endpoint} responds quickly ({result['response_time_ms']}ms)")
            elif result["success"]:
                print(f"⚠️ {endpoint} responds but slowly ({result['response_time_ms']}ms)")
            else:
                print(f"❌ {endpoint} failed to respond")
        
        # Test 8: Middleware functionality (check headers)
        print("\n🔧 Test 8: Performance Middleware Validation")
        
        # Test for performance headers
        url = f"{self.base_url}/health"
        async with self.session.get(url) as response:
            headers = dict(response.headers)
            
            middleware_features = []
            
            if 'X-Response-Time' in headers or 'X-Process-Time' in headers:
                middleware_features.append("Response timing headers")
            
            if 'content-encoding' in headers:
                middleware_features.append("Response compression")
            
            if any(header.startswith('X-') for header in headers):
                middleware_features.append("Custom performance headers")
            
            if middleware_features:
                print(f"✅ Performance middleware active: {', '.join(middleware_features)}")
            else:
                print("⚠️ Performance middleware headers not detected")
        
        self.print_validation_summary()
    
    def print_validation_summary(self):
        """Print comprehensive validation summary"""
        print("\n" + "=" * 70)
        print("📋 PHASE 3 DAY 6 VALIDATION SUMMARY")
        print("=" * 70)
        
        if not self.test_results:
            print("No test results available")
            return
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        response_times = [r["response_time_ms"] for r in successful_tests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"✅ Successful Tests: {len(successful_tests)}/{len(self.test_results)}")
        print(f"❌ Failed Tests: {len(failed_tests)}")
        print(f"⏱️ Average Response Time: {avg_response_time:.2f}ms")
        
        # Performance benchmarks
        fast_tests = [r for r in successful_tests if r["response_time_ms"] < 200]
        moderate_tests = [r for r in successful_tests if 200 <= r["response_time_ms"] < 500]
        slow_tests = [r for r in successful_tests if r["response_time_ms"] >= 500]
        
        print(f"\n📊 PERFORMANCE DISTRIBUTION:")
        print(f"🏃 Fast responses (<200ms): {len(fast_tests)}")
        print(f"🚶 Moderate responses (200-500ms): {len(moderate_tests)}")
        print(f"🐌 Slow responses (≥500ms): {len(slow_tests)}")
        
        # Feature validation
        print(f"\n🎯 FEATURE VALIDATION:")
        
        performance_endpoints = [r for r in successful_tests if "/performance/" in r["endpoint"]]
        cache_endpoints = [r for r in successful_tests if "/cache/" in r["endpoint"]]
        database_endpoints = [r for r in successful_tests if "/database/" in r["endpoint"]]
        
        print(f"📊 Performance Monitoring: {len(performance_endpoints)} endpoints working")
        print(f"💾 Cache System: {len(cache_endpoints)} endpoints working")
        print(f"🗃️ Database Optimization: {len(database_endpoints)} endpoints working")
        
        # Overall assessment
        success_rate = len(successful_tests) / len(self.test_results) * 100
        
        if success_rate >= 90 and avg_response_time < 300:
            assessment = "🏆 EXCELLENT - All performance features working optimally"
        elif success_rate >= 80 and avg_response_time < 500:
            assessment = "✅ GOOD - Performance features working well"
        elif success_rate >= 70:
            assessment = "⚠️ FAIR - Some performance issues detected"
        else:
            assessment = "❌ POOR - Significant performance issues"
        
        print(f"\n🎯 OVERALL ASSESSMENT: {assessment}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Failed tests details
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['endpoint']}: {test.get('error', f'Status {test['status_code']}')}")
        
        # Performance recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if slow_tests:
            print("• Some endpoints are slow - consider further optimization")
        
        if len(performance_endpoints) < 5:
            print("• Not all performance monitoring endpoints are accessible")
        
        if avg_response_time > 500:
            print("• Average response time is high - review performance optimizations")
        
        if success_rate < 90:
            print("• Some features are not working - check logs and configurations")
        
        if success_rate >= 90 and avg_response_time < 200:
            print("• Performance optimization is working excellently!")
            print("• System is ready for load testing and production use")
        
        print("=" * 70)
    
    async def run_mini_load_test(self):
        """Run a quick mini load test to validate performance under load"""
        print("\n⚡ Running Mini Load Test")
        print("-" * 40)
        
        # Test health endpoint with concurrent requests
        tasks = []
        num_requests = 20
        
        start_time = time.time()
        
        for i in range(num_requests):
            task = asyncio.create_task(self.test_endpoint("/health"))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        successful = [r for r in results if r["success"]]
        response_times = [r["response_time_ms"] for r in successful]
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"✅ Completed {num_requests} concurrent requests in {duration:.2f}s")
            print(f"   Success rate: {len(successful)}/{num_requests}")
            print(f"   Average response time: {avg_time:.2f}ms")
            print(f"   Min/Max response time: {min_time:.2f}ms / {max_time:.2f}ms")
            print(f"   Requests per second: {num_requests/duration:.2f}")
            
            if avg_time < 300 and len(successful) == num_requests:
                print("🏆 System handles concurrent load well!")
            elif avg_time < 500:
                print("✅ System handles concurrent load adequately")
            else:
                print("⚠️ System shows strain under concurrent load")
        else:
            print("❌ No successful requests during load test")


async def main():
    """Main validation function"""
    validator = PerformanceValidator("http://localhost:8000")
    
    try:
        await validator.setup()
        await validator.validate_performance_features()
        await validator.run_mini_load_test()
        
        print("\n🏁 Phase 3 Day 6 Performance Optimization validation completed!")
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await validator.teardown()


if __name__ == "__main__":
    print("🎯 TeamFlow Phase 3 Day 6: Performance Optimization Validator")
    print("=" * 70)
    asyncio.run(main())