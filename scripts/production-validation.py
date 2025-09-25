#!/usr/bin/env python3
"""
Production Validation Script for TeamFlow
Tests all critical endpoints and validates production readiness
"""

import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime
import concurrent.futures

class ProductionValidator:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.results = []
        
    def test_endpoint(self, method: str, endpoint: str, 
                     expected_status: int = 200, 
                     payload: Dict = None,
                     headers: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            duration = (time.time() - start_time) * 1000
            
            try:
                data = response.json()
            except:
                data = {"raw_response": response.text}
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "duration_ms": round(duration, 2),
                "success": response.status_code == expected_status,
                "data": data
            }
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "expected_status": expected_status,
                "duration_ms": (time.time() - start_time) * 1000,
                "success": False,
                "error": str(e)
            }
        
        self.results.append(result)
        return result
    
    def run_health_checks(self):
        """Run all health check tests"""
        print("🔍 Running Health Check Tests...")
        
        tests = [
            ("GET", "/health", 200),
            ("GET", "/api/v1/health", 200),
            ("GET", "/api/v1/auth/health", 200),
        ]
        
        for method, endpoint, expected_status in tests:
            result = self.test_endpoint(method, endpoint, expected_status)
            status = "✅" if result["success"] else "❌"
            print(f"{status} {method} {endpoint} - {result['status_code']} ({result['duration_ms']}ms)")
    
    def run_api_tests(self):
        """Run core API endpoint tests"""
        print("\n🚀 Running API Endpoint Tests...")
        
        # Test core API endpoints (should return 401 for unauthorized)
        auth_tests = [
            ("GET", "/api/v1/users/me", 401),
            ("GET", "/api/v1/organizations", 401),
            ("GET", "/api/v1/tasks", 401),
        ]
        
        for method, endpoint, expected_status in auth_tests:
            result = self.test_endpoint(method, endpoint, expected_status)
            status = "✅" if result["success"] else "❌"
            print(f"{status} {method} {endpoint} - {result['status_code']} ({result['duration_ms']}ms)")
        
        # Test public endpoints
        public_tests = [
            ("GET", "/docs", 200),
            ("GET", "/openapi.json", 200),
        ]
        
        for method, endpoint, expected_status in public_tests:
            result = self.test_endpoint(method, endpoint, expected_status)
            status = "✅" if result["success"] else "❌"
            print(f"{status} {method} {endpoint} - {result['status_code']} ({result['duration_ms']}ms)")
    
    def test_auth_flow(self):
        """Test authentication flow"""
        print("\n🔐 Testing Authentication Flow...")
        
        # Test registration
        register_payload = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpassword123",
            "username": f"testuser_{int(time.time())}"
        }
        
        result = self.test_endpoint(
            "POST", 
            "/api/v1/auth/register", 
            201,  # Expecting 201 Created
            register_payload
        )
        
        status = "✅" if result["success"] else "❌"
        print(f"{status} POST /api/v1/auth/register - {result['status_code']} ({result['duration_ms']}ms)")
        
        if result["success"]:
            # Test login with the same credentials
            login_payload = {
                "email": register_payload["email"],
                "password": register_payload["password"]
            }
            
            result = self.test_endpoint(
                "POST",
                "/api/v1/auth/login",
                200,
                login_payload
            )
            
            status = "✅" if result["success"] else "❌"
            print(f"{status} POST /api/v1/auth/login - {result['status_code']} ({result['duration_ms']}ms)")
            
            if result["success"] and "access_token" in result.get("data", {}):
                # Test authenticated endpoint
                token = result["data"]["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                result = self.test_endpoint(
                    "GET",
                    "/api/v1/users/me",
                    200,
                    headers=headers
                )
                
                status = "✅" if result["success"] else "❌"
                print(f"{status} GET /api/v1/users/me (authenticated) - {result['status_code']} ({result['duration_ms']}ms)")
    
    def test_performance(self):
        """Test performance characteristics"""
        print("\n⚡ Running Performance Tests...")
        
        # Test multiple concurrent requests
        def test_single():
            return self.test_endpoint("GET", "/health")
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(test_single) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if r["success"])
        avg_response_time = sum(r["duration_ms"] for r in results) / len(results)
        
        print(f"✅ Concurrent Requests: {successful}/{len(results)} successful")
        print(f"✅ Average Response Time: {avg_response_time:.2f}ms")
        print(f"✅ Total Test Duration: {total_time * 1000:.2f}ms")
    
    def generate_report(self):
        """Generate validation report"""
        successful_tests = sum(1 for r in self.results if r["success"])
        total_tests = len(self.results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        avg_response_time = sum(r["duration_ms"] for r in self.results if "duration_ms" in r) / len(self.results)
        
        print(f"\n📊 PRODUCTION VALIDATION REPORT")
        print(f"=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Average Response Time: {avg_response_time:.2f}ms")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        if success_rate >= 90:
            print(f"\n🎉 PRODUCTION READY! Success rate: {success_rate:.1f}%")
            return True
        else:
            print(f"\n⚠️  NEEDS ATTENTION! Success rate: {success_rate:.1f}%")
            return False

def main():
    print("🚀 TEAMFLOW PRODUCTION VALIDATION")
    print("=" * 50)
    
    validator = ProductionValidator()
    validator.run_health_checks()
    validator.run_api_tests() 
    validator.test_auth_flow()
    validator.test_performance()
    
    is_ready = validator.generate_report()
    
    if is_ready:
        print("\n✅ All systems operational - Ready for production deployment!")
    else:
        print("\n❌ Some issues detected - Review before deployment")

if __name__ == "__main__":
    main()