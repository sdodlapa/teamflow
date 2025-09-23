"""
Stress testing scenarios for TeamFlow API
"""
import asyncio
import aiohttp
import time
import random
from typing import Dict, List, Any
from load_test_runner import LoadTestRunner


class StressTestRunner(LoadTestRunner):
    """Extended load test runner for stress testing scenarios"""
    
    async def run_stress_test_suite(self):
        """Run comprehensive stress test scenarios"""
        print("💪 Starting Stress Test Suite")
        print("⚠️  Warning: These tests will put high load on the system")
        print("=" * 60)
        
        # Stress test scenarios
        stress_scenarios = [
            {
                "name": "🔥 Extreme Load - Health Check",
                "endpoint": "/health", 
                "method": "GET",
                "concurrent_users": 100,
                "requests_per_user": 50,
                "description": "Test system stability under extreme load"
            },
            {
                "name": "🌊 Spike Test - API Docs",
                "endpoint": "/docs",
                "method": "GET", 
                "concurrent_users": 200,
                "requests_per_user": 10,
                "description": "Test response to sudden traffic spikes"
            },
            {
                "name": "💥 Database Stress - User Operations",
                "endpoint": "/api/v1/users/me",
                "method": "GET",
                "concurrent_users": 75,
                "requests_per_user": 30,
                "description": "Stress test database connections"
            },
            {
                "name": "🚀 Performance Dashboard Load",
                "endpoint": "/api/v1/performance/dashboard",
                "method": "GET",
                "concurrent_users": 25,
                "requests_per_user": 20,
                "description": "Test performance monitoring under load"
            },
            {
                "name": "🔐 Security Dashboard Stress",
                "endpoint": "/api/v1/security/dashboard", 
                "method": "GET",
                "concurrent_users": 20,
                "requests_per_user": 25,
                "description": "Test security monitoring performance"
            },
            {
                "name": "📊 Analytics Heavy Load",
                "endpoint": "/api/v1/performance/metrics",
                "method": "GET",
                "concurrent_users": 30,
                "requests_per_user": 15,
                "description": "Test analytics query performance"
            }
        ]
        
        print("Running stress test scenarios...")
        print("Each test will progressively increase system load\n")
        
        for i, scenario in enumerate(stress_scenarios, 1):
            print(f"[{i}/{len(stress_scenarios)}] {scenario['name']}")
            print(f"Description: {scenario['description']}")
            
            data_gen = self.generate_test_data(scenario["endpoint"])
            result = await self.run_load_test(
                endpoint=scenario["endpoint"],
                method=scenario["method"],
                concurrent_users=scenario["concurrent_users"],
                requests_per_user=scenario["requests_per_user"],
                data_generator=data_gen,
                test_name=scenario["name"]
            )
            
            # Check if system is still responsive
            await self.health_check_between_tests()
            
            # Longer wait between stress tests
            print("⏳ Cooling down system...")
            await asyncio.sleep(5)
        
        self.print_stress_test_summary()
    
    async def health_check_between_tests(self):
        """Quick health check between stress tests"""
        try:
            start_time = time.time()
            response = await self.make_request("GET", "/health")
            response_time = (time.time() - start_time) * 1000
            
            if response["success"] and response_time < 1000:
                print(f"✅ System responsive ({response_time:.0f}ms)")
            elif response["success"]:
                print(f"⚠️ System slow but responsive ({response_time:.0f}ms)")
            else:
                print(f"❌ System not responding properly")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    def print_stress_test_summary(self):
        """Print stress test specific summary"""
        print("\n" + "=" * 70)
        print("💪 STRESS TEST SUMMARY")
        print("=" * 70)
        
        if not self.results:
            print("No stress test results available")
            return
        
        # Analyze stress test results
        high_load_tests = [r for r in self.results if r.total_requests > 1000]
        failed_tests = [r for r in self.results if r.error_rate > 10]
        slow_tests = [r for r in self.results if r.avg_response_time > 1000]
        
        print(f"🔥 High Load Tests (>1000 requests): {len(high_load_tests)}")
        print(f"❌ Failed Tests (>10% error rate): {len(failed_tests)}")
        print(f"🐌 Slow Tests (>1000ms avg): {len(slow_tests)}")
        
        # System resilience metrics
        total_requests = sum(r.total_requests for r in self.results)
        total_successful = sum(r.successful_requests for r in self.results)
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        print(f"\n📊 SYSTEM RESILIENCE METRICS:")
        print(f"Total Stress Requests: {total_requests:,}")
        print(f"Overall Success Rate: {overall_success_rate:.2f}%")
        
        # Categorize system performance under stress
        if overall_success_rate >= 95:
            resilience_rating = "🏆 EXCELLENT - System handles stress very well"
        elif overall_success_rate >= 90:
            resilience_rating = "✅ GOOD - System handles stress well"
        elif overall_success_rate >= 80:
            resilience_rating = "⚠️ FAIR - System shows strain under stress"
        else:
            resilience_rating = "❌ POOR - System struggles under stress"
        
        print(f"Resilience Rating: {resilience_rating}")
        
        # Stress test specific recommendations
        print(f"\n💡 STRESS TEST RECOMMENDATIONS:")
        print("-" * 70)
        
        if failed_tests:
            print("• High error rates detected - implement circuit breakers and rate limiting")
        
        if slow_tests:
            print("• Slow responses under load - optimize database queries and add caching")
        
        if len(high_load_tests) > 0 and overall_success_rate < 90:
            print("• System struggles with high concurrent load - consider horizontal scaling")
        
        max_concurrent = max(r.total_requests for r in self.results) if self.results else 0
        if max_concurrent > 5000 and overall_success_rate >= 95:
            print("• System handles high load well - ready for production scaling")
        
        print("=" * 70)


class EnduranceTestRunner(LoadTestRunner):
    """Extended runner for endurance/soak testing"""
    
    async def run_endurance_test(self, duration_minutes: int = 30):
        """Run endurance test for specified duration"""
        print(f"⏰ Starting Endurance Test ({duration_minutes} minutes)")
        print("This test will run continuous load to check for memory leaks and stability")
        print("=" * 70)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        test_cycles = []
        cycle_count = 0
        
        while time.time() < end_time:
            cycle_count += 1
            cycle_start = time.time()
            
            print(f"\n🔄 Endurance Cycle {cycle_count}")
            
            # Run a moderate load cycle
            result = await self.run_load_test(
                endpoint="/health",
                method="GET",
                concurrent_users=10,
                requests_per_user=20,
                test_name=f"Endurance Cycle {cycle_count}"
            )
            
            cycle_duration = time.time() - cycle_start
            test_cycles.append({
                "cycle": cycle_count,
                "duration": cycle_duration,
                "avg_response_time": result.avg_response_time,
                "error_rate": result.error_rate,
                "requests_per_second": result.requests_per_second
            })
            
            # Check for performance degradation
            if len(test_cycles) > 1:
                prev_cycle = test_cycles[-2]
                current_cycle = test_cycles[-1]
                
                response_time_increase = (
                    (current_cycle["avg_response_time"] - prev_cycle["avg_response_time"]) 
                    / prev_cycle["avg_response_time"] * 100
                )
                
                if response_time_increase > 20:
                    print(f"⚠️ Performance degradation detected: {response_time_increase:.1f}% slower")
                elif response_time_increase > 50:
                    print(f"❌ Significant performance degradation: {response_time_increase:.1f}% slower")
            
            # Short break between cycles
            await asyncio.sleep(10)
        
        self.print_endurance_summary(test_cycles, duration_minutes)
    
    def print_endurance_summary(self, cycles: List[Dict], duration_minutes: int):
        """Print endurance test summary"""
        print(f"\n⏰ ENDURANCE TEST SUMMARY ({duration_minutes} minutes)")
        print("=" * 70)
        
        if not cycles:
            print("No endurance test data available")
            return
        
        # Calculate performance trends
        first_cycle = cycles[0]
        last_cycle = cycles[-1]
        
        response_time_trend = (
            (last_cycle["avg_response_time"] - first_cycle["avg_response_time"]) 
            / first_cycle["avg_response_time"] * 100
        )
        
        rps_trend = (
            (last_cycle["requests_per_second"] - first_cycle["requests_per_second"])
            / first_cycle["requests_per_second"] * 100
        )
        
        avg_error_rate = sum(c["error_rate"] for c in cycles) / len(cycles)
        
        print(f"Total Cycles: {len(cycles)}")
        print(f"Response Time Trend: {response_time_trend:+.1f}%")
        print(f"Throughput Trend: {rps_trend:+.1f}%")
        print(f"Average Error Rate: {avg_error_rate:.2f}%")
        
        # Stability assessment
        if abs(response_time_trend) < 10 and avg_error_rate < 1:
            stability_rating = "🏆 EXCELLENT - System is very stable over time"
        elif abs(response_time_trend) < 25 and avg_error_rate < 5:
            stability_rating = "✅ GOOD - System maintains stability"
        elif abs(response_time_trend) < 50 and avg_error_rate < 10:
            stability_rating = "⚠️ FAIR - Some performance drift detected"
        else:
            stability_rating = "❌ POOR - Significant performance degradation"
        
        print(f"Stability Rating: {stability_rating}")
        
        # Memory leak indicators
        if response_time_trend > 30:
            print("⚠️ Possible memory leak - response times increasing over time")
        
        if rps_trend < -20:
            print("⚠️ Throughput degradation - system may be accumulating load")
        
        print("=" * 70)


async def run_comprehensive_performance_tests():
    """Run all performance test suites"""
    print("🎯 TeamFlow Comprehensive Performance Testing")
    print("=" * 60)
    
    # Standard load tests
    print("Phase 1: Standard Load Tests")
    runner = LoadTestRunner("http://localhost:8000")
    await runner.setup()
    await runner.run_comprehensive_load_test()
    await runner.teardown()
    
    print("\n" + "="*60)
    
    # Stress tests
    print("Phase 2: Stress Tests")
    stress_runner = StressTestRunner("http://localhost:8000")
    await stress_runner.setup()
    await stress_runner.run_stress_test_suite()
    await stress_runner.teardown()
    
    print("\n" + "="*60)
    
    # Short endurance test (5 minutes for demo)
    print("Phase 3: Endurance Test")
    endurance_runner = EnduranceTestRunner("http://localhost:8000")
    await endurance_runner.setup()
    await endurance_runner.run_endurance_test(duration_minutes=5)
    await endurance_runner.teardown()
    
    print("\n🏁 All performance tests completed!")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_performance_tests())