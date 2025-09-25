#!/usr/bin/env python3
"""
Production validation script for TeamFlow
Comprehensive testing of production readiness
"""

import asyncio
import aiohttp
import time
import json
import sys
from pathlib import Path
import subprocess
from typing import Dict, Any, List, Tuple

class ProductionValidator:
    def __init__(self):
        self.results = []
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.session = None
    
    async def setup_session(self):
        """Setup HTTP client session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def cleanup_session(self):
        """Cleanup HTTP client session"""
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "timestamp": time.time(),
            "details": details or {}
        }
        self.results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        
        if details and status != "PASS":
            for key, value in details.items():
                print(f"   - {key}: {value}")
    
    async def test_backend_startup(self) -> bool:
        """Test if backend can start successfully"""
        try:
            # Check if backend is running
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Backend Startup", 
                        "PASS",
                        {"status": data.get("status"), "service": data.get("service")}
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Startup", 
                        "FAIL",
                        {"status_code": response.status}
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Backend Startup", 
                "FAIL",
                {"error": str(e)}
            )
            return False
    
    async def test_database_connectivity(self) -> bool:
        """Test database connectivity"""
        try:
            async with self.session.get(f"{self.base_url}/health/detailed") as response:
                if response.status == 200:
                    data = await response.json()
                    db_status = data.get("checks", {}).get("database", {})
                    
                    if db_status.get("status") == "healthy":
                        self.log_result(
                            "Database Connectivity",
                            "PASS",
                            {"response_time": db_status.get("response_time_ms")}
                        )
                        return True
                    else:
                        self.log_result(
                            "Database Connectivity",
                            "FAIL", 
                            {"db_status": db_status}
                        )
                        return False
                else:
                    self.log_result(
                        "Database Connectivity",
                        "FAIL",
                        {"status_code": response.status}
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Database Connectivity",
                "FAIL",
                {"error": str(e)}
            )
            return False
    
    async def test_api_endpoints(self) -> Tuple[int, int]:
        """Test critical API endpoints"""
        endpoints = [
            ("GET", "/health"),
            ("GET", "/health/live"),
            ("GET", "/health/ready"),
            ("GET", "/api/v1/auth/health"),
            ("GET", "/docs"),  # OpenAPI docs
        ]
        
        passed = 0
        failed = 0
        
        for method, endpoint in endpoints:
            try:
                start_time = time.time()
                async with self.session.request(method, f"{self.base_url}{endpoint}") as response:
                    duration = (time.time() - start_time) * 1000
                    
                    if response.status < 400:
                        self.log_result(
                            f"API {method} {endpoint}",
                            "PASS",
                            {"status_code": response.status, "response_time_ms": f"{duration:.1f}"}
                        )
                        passed += 1
                    else:
                        self.log_result(
                            f"API {method} {endpoint}",
                            "FAIL",
                            {"status_code": response.status}
                        )
                        failed += 1
                        
            except Exception as e:
                self.log_result(
                    f"API {method} {endpoint}",
                    "FAIL",
                    {"error": str(e)}
                )
                failed += 1
        
        return passed, failed
    
    async def test_performance_benchmarks(self) -> Dict[str, float]:
        """Test performance benchmarks"""
        performance_results = {}
        
        # Test API response times
        test_endpoints = [
            "/health",
            "/health/detailed",
            "/api/v1/auth/health"
        ]
        
        for endpoint in test_endpoints:
            times = []
            for _ in range(5):  # 5 requests per endpoint
                try:
                    start_time = time.time()
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        if response.status == 200:
                            times.append((time.time() - start_time) * 1000)
                        await asyncio.sleep(0.1)  # Small delay between requests
                except:
                    continue
            
            if times:
                avg_time = sum(times) / len(times)
                performance_results[endpoint] = avg_time
                
                status = "PASS" if avg_time < 2000 else "WARN" if avg_time < 5000 else "FAIL"
                self.log_result(
                    f"Performance {endpoint}",
                    status,
                    {"avg_response_time_ms": f"{avg_time:.1f}", "requests": len(times)}
                )
        
        return performance_results
    
    def test_frontend_build(self) -> bool:
        """Test frontend build"""
        try:
            frontend_path = Path(__file__).parent.parent / "frontend"
            
            if not (frontend_path / "dist").exists():
                # Try to build
                result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=frontend_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.log_result(
                        "Frontend Build",
                        "PASS",
                        {"build_output": "Build successful"}
                    )
                    return True
                else:
                    self.log_result(
                        "Frontend Build",
                        "FAIL",
                        {"error": result.stderr[:500]}
                    )
                    return False
            else:
                self.log_result(
                    "Frontend Build",
                    "PASS", 
                    {"build_output": "Dist folder exists"}
                )
                return True
                
        except Exception as e:
            self.log_result(
                "Frontend Build",
                "FAIL",
                {"error": str(e)}
            )
            return False
    
    def test_configuration_files(self) -> Dict[str, bool]:
        """Test configuration files"""
        config_files = {
            "backend/app/main.py": Path(__file__).parent.parent / "backend" / "app" / "main.py",
            "frontend/vercel.json": Path(__file__).parent.parent / "frontend" / "vercel.json",
            "backend/railway.json": Path(__file__).parent.parent / "backend" / "railway.json",
            "docker-compose.yml": Path(__file__).parent.parent / "docker-compose.yml",
        }
        
        results = {}
        
        for name, path in config_files.items():
            if path.exists():
                self.log_result(f"Config {name}", "PASS", {"path": str(path)})
                results[name] = True
            else:
                self.log_result(f"Config {name}", "FAIL", {"path": str(path), "exists": False})
                results[name] = False
        
        return results
    
    def test_security_configuration(self) -> Dict[str, Any]:
        """Test security configuration"""
        security_results = {}
        
        # Check environment variables (without exposing values)
        env_vars = [
            "SECRET_KEY",
            "DATABASE_URL", 
            "ENVIRONMENT"
        ]
        
        for var in env_vars:
            import os
            if os.getenv(var):
                self.log_result(f"Env Var {var}", "PASS", {"configured": True})
                security_results[var] = True
            else:
                self.log_result(f"Env Var {var}", "WARN", {"configured": False})
                security_results[var] = False
        
        return security_results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        print("🔍 Starting Production Validation Tests")
        print("=" * 50)
        
        await self.setup_session()
        
        try:
            # Infrastructure tests
            print("\n📊 INFRASTRUCTURE VALIDATION")
            print("-" * 30)
            backend_ok = await self.test_backend_startup()
            db_ok = await self.test_database_connectivity()
            
            # API tests
            print("\n🔌 API ENDPOINT VALIDATION")
            print("-" * 30)
            api_passed, api_failed = await self.test_api_endpoints()
            
            # Performance tests
            print("\n⚡ PERFORMANCE VALIDATION")
            print("-" * 30)
            performance_results = await self.test_performance_benchmarks()
            
            # Frontend tests
            print("\n🎨 FRONTEND VALIDATION")
            print("-" * 30)
            frontend_ok = self.test_frontend_build()
            
            # Configuration tests
            print("\n⚙️ CONFIGURATION VALIDATION")
            print("-" * 30)
            config_results = self.test_configuration_files()
            
            # Security tests
            print("\n🔒 SECURITY VALIDATION")
            print("-" * 30)
            security_results = self.test_security_configuration()
            
        finally:
            await self.cleanup_session()
        
        # Generate summary
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results if r["status"] == "FAIL"])
        warn_tests = len([r for r in self.results if r["status"] == "WARN"])
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warn_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "infrastructure_ready": backend_ok and db_ok,
            "api_endpoints": {"passed": api_passed, "failed": api_failed},
            "frontend_ready": frontend_ok,
            "performance_results": performance_results,
            "security_configured": all(security_results.values()),
            "overall_ready": failed_tests == 0 and backend_ok and db_ok and frontend_ok
        }
        
        return summary

async def main():
    """Main validation function"""
    validator = ProductionValidator()
    summary = await validator.run_all_tests()
    
    print("\n" + "=" * 50)
    print("📊 PRODUCTION VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"✅ Passed: {summary['passed']}")
    print(f"❌ Failed: {summary['failed']}")
    print(f"⚠️ Warnings: {summary['warnings']}")
    print(f"📈 Pass Rate: {summary['pass_rate']:.1f}%")
    
    print(f"\n🎯 PRODUCTION READINESS: {'✅ READY' if summary['overall_ready'] else '❌ NOT READY'}")
    
    if not summary['overall_ready']:
        print("\n🔧 Issues to resolve:")
        if summary['failed'] > 0:
            print(f"   - {summary['failed']} test(s) failed")
        if not summary['infrastructure_ready']:
            print("   - Infrastructure not ready")
        if not summary['frontend_ready']:
            print("   - Frontend build issues")
    
    # Save detailed results
    with open("production-validation-results.json", "w") as f:
        json.dump({
            "summary": summary,
            "detailed_results": validator.results,
            "timestamp": time.time()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: production-validation-results.json")
    
    # Return appropriate exit code
    sys.exit(0 if summary['overall_ready'] else 1)

if __name__ == "__main__":
    asyncio.run(main())