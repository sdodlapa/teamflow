#!/usr/bin/env python3
"""
Day 25 Analytics Dashboard Validation Script
Tests the analytics API endpoints and dashboard functionality
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any

class AnalyticsDashboardValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_prefix = "/api/v1/analytics"
        
    async def test_dashboard_endpoint(self) -> Dict[str, Any]:
        """Test the main analytics dashboard endpoint"""
        print("📊 Testing analytics dashboard endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{self.api_prefix}/dashboard?days=30"
                async with session.get(url) as response:
                    
                    result = {
                        "status": "PASS" if response.status == 200 else "FAIL",
                        "http_status": response.status,
                        "response": None,
                        "error": None
                    }
                    
                    if response.status == 200:
                        data = await response.json()
                        result["response"] = data
                        print("   ✅ Dashboard endpoint responding")
                        print(f"   📈 Dashboard Stats: {data.get('dashboard_stats', {})}")
                        print(f"   📋 Recent Activity: {len(data.get('recent_activity', []))} items")
                        print(f"   💡 Key Insights: {len(data.get('key_insights', []))} insights")
                    else:
                        error_text = await response.text()
                        result["error"] = error_text
                        print(f"   ❌ Dashboard endpoint failed: HTTP {response.status}")
                        print(f"   📝 Error: {error_text}")
                        
                    return result
                    
        except Exception as e:
            result = {
                "status": "FAIL",
                "http_status": 0,
                "response": None,
                "error": str(e)
            }
            print(f"   ❌ Dashboard endpoint error: {e}")
            return result
    
    async def test_task_analytics_endpoint(self) -> Dict[str, Any]:
        """Test the task analytics endpoint"""
        print("📝 Testing task analytics endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{self.api_prefix}/tasks?days=30"
                async with session.get(url) as response:
                    
                    result = {
                        "status": "PASS" if response.status == 200 else "FAIL",
                        "http_status": response.status,
                        "response": None,
                        "error": None
                    }
                    
                    if response.status == 200:
                        data = await response.json()
                        result["response"] = data
                        print("   ✅ Task analytics endpoint responding")
                        print(f"   📊 Total Tasks: {data.get('total_tasks', 0)}")
                        print(f"   ✅ Completed: {data.get('completed_tasks', 0)}")
                        print(f"   📈 Completion Rate: {data.get('completion_rate', 0)}%")
                    else:
                        error_text = await response.text()
                        result["error"] = error_text
                        print(f"   ❌ Task analytics failed: HTTP {response.status}")
                        
                    return result
                    
        except Exception as e:
            result = {
                "status": "FAIL",
                "http_status": 0,
                "response": None,
                "error": str(e)
            }
            print(f"   ❌ Task analytics error: {e}")
            return result
    
    async def test_project_analytics_endpoint(self) -> Dict[str, Any]:
        """Test the project analytics endpoint"""
        print("🏗️ Testing project analytics endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{self.api_prefix}/projects?days=30"
                async with session.get(url) as response:
                    
                    result = {
                        "status": "PASS" if response.status == 200 else "FAIL",
                        "http_status": response.status,
                        "response": None,
                        "error": None
                    }
                    
                    if response.status == 200:
                        data = await response.json()
                        result["response"] = data
                        print("   ✅ Project analytics endpoint responding")
                        print(f"   📊 Total Projects: {data.get('total_projects', 0)}")
                        print(f"   🚀 Active: {data.get('active_projects', 0)}")
                        print(f"   ✅ Completed: {data.get('completed_projects', 0)}")
                    else:
                        error_text = await response.text()
                        result["error"] = error_text
                        print(f"   ❌ Project analytics failed: HTTP {response.status}")
                        
                    return result
                    
        except Exception as e:
            result = {
                "status": "FAIL",
                "http_status": 0,
                "response": None,
                "error": str(e)
            }
            print(f"   ❌ Project analytics error: {e}")
            return result
    
    async def test_team_analytics_endpoint(self) -> Dict[str, Any]:
        """Test the team analytics endpoint"""
        print("👥 Testing team analytics endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{self.api_prefix}/team?days=30"
                async with session.get(url) as response:
                    
                    result = {
                        "status": "PASS" if response.status == 200 else "FAIL",
                        "http_status": response.status,
                        "response": None,
                        "error": None
                    }
                    
                    if response.status == 200:
                        data = await response.json()
                        result["response"] = data
                        print("   ✅ Team analytics endpoint responding")
                        print(f"   👥 Team Size: {data.get('team_size', 0)}")
                        print(f"   🟢 Active Members: {data.get('active_members', 0)}")
                        productivity = data.get('productivity_metrics', {})
                        print(f"   📈 Team Velocity: {productivity.get('team_velocity', 0)}%")
                    else:
                        error_text = await response.text()
                        result["error"] = error_text
                        print(f"   ❌ Team analytics failed: HTTP {response.status}")
                        
                    return result
                    
        except Exception as e:
            result = {
                "status": "FAIL",
                "http_status": 0,
                "response": None,
                "error": str(e)
            }
            print(f"   ❌ Team analytics error: {e}")
            return result
    
    async def test_export_functionality(self) -> Dict[str, Any]:
        """Test the analytics export endpoint"""
        print("📤 Testing analytics export functionality...")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{self.api_prefix}/export?format=csv&days=30"
                async with session.get(url) as response:
                    
                    result = {
                        "status": "PASS" if response.status == 200 else "FAIL",
                        "http_status": response.status,
                        "response": None,
                        "error": None
                    }
                    
                    if response.status == 200:
                        data = await response.json()
                        result["response"] = data
                        print("   ✅ Export endpoint responding")
                        print(f"   📊 Export Status: {data.get('status', 'unknown')}")
                        print(f"   📄 Format: {data.get('format', 'unknown')}")
                    else:
                        error_text = await response.text()
                        result["error"] = error_text
                        print(f"   ❌ Export failed: HTTP {response.status}")
                        
                    return result
                    
        except Exception as e:
            result = {
                "status": "FAIL",
                "http_status": 0,
                "response": None,
                "error": str(e)
            }
            print(f"   ❌ Export error: {e}")
            return result
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of analytics dashboard system"""
        print("🧪 TEAMFLOW ANALYTICS DASHBOARD VALIDATION")
        print("=" * 55)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "tests": {}
        }
        
        # Run individual tests
        validation_results["tests"]["dashboard"] = await self.test_dashboard_endpoint()
        print()
        
        validation_results["tests"]["task_analytics"] = await self.test_task_analytics_endpoint()
        print()
        
        validation_results["tests"]["project_analytics"] = await self.test_project_analytics_endpoint()
        print()
        
        validation_results["tests"]["team_analytics"] = await self.test_team_analytics_endpoint()
        print()
        
        validation_results["tests"]["export"] = await self.test_export_functionality()
        print()
        
        # Determine overall status
        all_tests = validation_results["tests"]
        passed_tests = sum(1 for test in all_tests.values() if test["status"] == "PASS")
        total_tests = len(all_tests)
        
        if passed_tests == total_tests:
            validation_results["overall_status"] = "PASS"
            print("🚀 OVERALL STATUS: ✅ ALL ANALYTICS TESTS PASSED")
            print("🎉 Day 25 Analytics Dashboard is ready for use!")
            print("📊 Business intelligence system operational")
        elif passed_tests > 0:
            validation_results["overall_status"] = "PARTIAL"
            print("⚠️ OVERALL STATUS: 🟡 SOME ANALYTICS TESTS PASSED")
            print(f"📊 {passed_tests}/{total_tests} analytics endpoints working")
        else:
            validation_results["overall_status"] = "FAIL"
            print("❌ OVERALL STATUS: 🔴 ANALYTICS TESTS FAILED")
            print("🔧 Check if backend server is running on localhost:8000")
        
        print()
        print("📱 Frontend Testing:")
        print("   🌐 Analytics Dashboard: http://localhost:3000/analytics")
        print("   🧪 API Test Mode: Click 'Show API Test' button")
        print("   📊 Full Dashboard: Main analytics interface")
        
        return validation_results

async def main():
    """Main validation function"""
    validator = AnalyticsDashboardValidator()
    results = await validator.run_full_validation()
    
    # Save results to file
    results_file = "day25_analytics_validation_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    if results["overall_status"] == "PASS":
        exit(0)
    elif results["overall_status"] == "PARTIAL":
        exit(1)
    else:
        exit(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Analytics validation interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n💥 Analytics validation failed with error: {e}")
        exit(3)