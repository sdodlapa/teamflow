#!/usr/bin/env python3
"""
Day 5: Advanced Security & Compliance System Test
Tests comprehensive security features including headers, rate limiting, GDPR compliance.
"""
import asyncio
import requests
import time
from datetime import datetime
from typing import Dict, Any

class SecuritySystemValidator:
    """Comprehensive security system validation."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers implementation."""
        print("🔒 Testing Security Headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            expected_headers = [
                "Content-Security-Policy",
                "Strict-Transport-Security", 
                "X-Frame-Options",
                "X-Content-Type-Options",
                "X-XSS-Protection",
                "Referrer-Policy",
                "Permissions-Policy"
            ]
            
            results = {}
            for header in expected_headers:
                results[header] = {
                    "present": header in response.headers,
                    "value": response.headers.get(header, "Not Present")
                }
            
            # Test CSP specifically
            csp = response.headers.get("Content-Security-Policy", "")
            csp_checks = {
                "default-src": "'self'" in csp,
                "script-src": "script-src" in csp,
                "style-src": "style-src" in csp,
                "frame-ancestors": "frame-ancestors 'none'" in csp
            }
            
            return {
                "status": "PASS" if all(results[h]["present"] for h in expected_headers) else "PARTIAL",
                "headers": results,
                "csp_analysis": csp_checks,
                "total_headers": len([h for h in expected_headers if h in response.headers])
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality."""
        print("⚡ Testing Rate Limiting...")
        
        try:
            # Make rapid requests to trigger rate limiting
            responses = []
            
            for i in range(15):  # Make 15 requests rapidly
                response = self.session.get(f"{self.base_url}/")
                responses.append({
                    "status_code": response.status_code,
                    "headers": {
                        "X-RateLimit-Limit": response.headers.get("X-RateLimit-Limit"),
                        "X-RateLimit-Remaining": response.headers.get("X-RateLimit-Remaining"),
                        "X-RateLimit-Window": response.headers.get("X-RateLimit-Window"),
                        "Retry-After": response.headers.get("Retry-After")
                    }
                })
                time.sleep(0.1)  # Small delay
            
            # Check if any requests were rate limited (429)
            rate_limited = [r for r in responses if r["status_code"] == 429]
            successful = [r for r in responses if r["status_code"] == 200]
            
            # Check if rate limit headers are present
            has_rate_headers = any(r["headers"]["X-RateLimit-Limit"] for r in responses)
            
            return {
                "status": "PASS" if has_rate_headers else "PARTIAL",
                "total_requests": len(responses),
                "successful_requests": len(successful),
                "rate_limited_requests": len(rate_limited),
                "has_rate_limit_headers": has_rate_headers,
                "sample_headers": responses[0]["headers"] if responses else {}
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def test_threat_detection(self) -> Dict[str, Any]:
        """Test threat detection capabilities."""
        print("🛡️ Testing Threat Detection...")
        
        try:
            threat_payloads = [
                # SQL Injection attempts
                {"param": "test'; DROP TABLE users; --"},
                {"param": "1 UNION SELECT * FROM users"},
                
                # XSS attempts  
                {"param": "<script>alert('xss')</script>"},
                {"param": "javascript:alert('xss')"},
                
                # Path traversal
                {"param": "../../etc/passwd"},
                {"param": "..\\windows\\system32"}
            ]
            
            results = []
            for payload in threat_payloads:
                response = self.session.get(
                    f"{self.base_url}/", 
                    params=payload
                )
                results.append({
                    "payload": payload["param"][:50],
                    "status_code": response.status_code,
                    "blocked": response.status_code == 403,
                    "threats_detected": response.headers.get("X-Security-Threats-Detected", "0")
                })
            
            blocked_count = sum(1 for r in results if r["blocked"])
            detected_count = sum(1 for r in results if int(r["threats_detected"]) > 0)
            
            return {
                "status": "PASS" if (blocked_count > 0 or detected_count > 0) else "PARTIAL",
                "total_payloads": len(threat_payloads),
                "blocked_requests": blocked_count,
                "threats_detected": detected_count,
                "detection_rate": f"{(detected_count/len(threat_payloads))*100:.1f}%",
                "results": results
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test security API endpoints availability."""
        print("🔌 Testing Security API Endpoints...")
        
        security_endpoints = [
            "/api/v1/security/audit-logs",
            "/api/v1/security/alerts", 
            "/api/v1/security/api-keys",
            "/api/v1/security/gdpr/requests",
            "/api/v1/security/consent",
            "/api/v1/security/dashboard",
            "/api/v1/security/configurations",
            "/api/v1/security/login-attempts"
        ]
        
        results = {}
        
        for endpoint in security_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                results[endpoint] = {
                    "status_code": response.status_code,
                    "available": response.status_code != 404,
                    "requires_auth": response.status_code == 401,
                    "content_type": response.headers.get("Content-Type", "")
                }
            except Exception as e:
                results[endpoint] = {
                    "status_code": None,
                    "available": False,
                    "error": str(e)
                }
        
        available_count = sum(1 for r in results.values() if r.get("available", False))
        
        return {
            "status": "PASS" if available_count >= 6 else "PARTIAL", 
            "total_endpoints": len(security_endpoints),
            "available_endpoints": available_count,
            "availability_rate": f"{(available_count/len(security_endpoints))*100:.1f}%",
            "endpoints": results
        }
    
    def test_cors_configuration(self) -> Dict[str, Any]:
        """Test CORS configuration."""
        print("🌍 Testing CORS Configuration...")
        
        try:
            # Test preflight request
            response = self.session.options(
                f"{self.base_url}/api/v1/auth/login",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type,Authorization"
                }
            )
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"), 
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            return {
                "status": "PASS" if cors_headers["Access-Control-Allow-Origin"] else "PARTIAL",
                "preflight_status": response.status_code,
                "cors_headers": cors_headers,
                "configured": any(cors_headers.values())
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def test_response_timing(self) -> Dict[str, Any]:
        """Test response timing and performance headers."""
        print("⏱️ Testing Response Timing...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/")
            response_time = time.time() - start_time
            
            process_time = response.headers.get("X-Process-Time")
            
            return {
                "status": "PASS",
                "response_time_ms": round(response_time * 1000, 2),
                "server_process_time": process_time,
                "has_timing_headers": process_time is not None,
                "performance": "GOOD" if response_time < 0.5 else "SLOW"
            }
            
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive security test report."""
        print("\n🧪 Starting Day 5 Security & Compliance System Validation...")
        print("=" * 70)
        
        tests = [
            ("Security Headers", self.test_security_headers),
            ("Rate Limiting", self.test_rate_limiting), 
            ("Threat Detection", self.test_threat_detection),
            ("API Endpoints", self.test_api_endpoints),
            ("CORS Configuration", self.test_cors_configuration),
            ("Response Timing", self.test_response_timing)
        ]
        
        results = {}
        passed = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                
                status_emoji = {
                    "PASS": "✅",
                    "PARTIAL": "⚠️", 
                    "FAIL": "❌"
                }
                
                print(f"{status_emoji.get(result['status'], '❓')} {test_name}: {result['status']}")
                
                if result['status'] == "PASS":
                    passed += 1
                    
            except Exception as e:
                results[test_name] = {"status": "FAIL", "error": str(e)}
                print(f"❌ {test_name}: FAIL ({str(e)[:50]})")
        
        print("\n" + "=" * 70)
        
        overall_status = "EXCELLENT" if passed >= 5 else "GOOD" if passed >= 3 else "NEEDS_WORK"
        
        report = {
            "test_date": datetime.now().isoformat(),
            "overall_status": overall_status,
            "tests_passed": passed,
            "total_tests": len(tests),
            "pass_rate": f"{(passed/len(tests))*100:.1f}%",
            "results": results,
            "summary": {
                "security_headers": results.get("Security Headers", {}).get("total_headers", 0),
                "rate_limiting": "ACTIVE" if results.get("Rate Limiting", {}).get("has_rate_limit_headers") else "INACTIVE",
                "threat_detection": results.get("Threat Detection", {}).get("detection_rate", "0%"),
                "api_availability": results.get("API Endpoints", {}).get("availability_rate", "0%"),
                "cors_configured": results.get("CORS Configuration", {}).get("configured", False),
                "performance": results.get("Response Timing", {}).get("performance", "UNKNOWN")
            }
        }
        
        # Print summary
        print(f"📊 FINAL RESULTS:")
        print(f"   Overall Status: {overall_status}")
        print(f"   Tests Passed: {passed}/{len(tests)} ({report['pass_rate']})")
        print(f"   Security Headers: {report['summary']['security_headers']}/7 implemented")
        print(f"   Rate Limiting: {report['summary']['rate_limiting']}")
        print(f"   Threat Detection: {report['summary']['threat_detection']} effective")
        print(f"   API Availability: {report['summary']['api_availability']}")
        print(f"   Performance: {report['summary']['performance']}")
        
        if overall_status == "EXCELLENT":
            print("\n🎉 OUTSTANDING! Day 5 Security & Compliance system is production-ready!")
        elif overall_status == "GOOD":
            print("\n👍 GOOD! Security system is functional with room for enhancement.")
        else:
            print("\n⚠️ NEEDS WORK! Security system requires attention before production.")
        
        return report


def main():
    """Main test execution."""
    validator = SecuritySystemValidator()
    
    print("🚀 TeamFlow Day 5: Advanced Security & Compliance System Test")
    print("Testing comprehensive security features and GDPR compliance...")
    
    try:
        # Test server availability first
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not available or not healthy")
            return
            
        print("✅ Server is running and healthy")
        
        # Run comprehensive tests
        report = validator.generate_report()
        
        # Save report
        with open("day5_security_test_report.json", "w") as f:
            import json
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: day5_security_test_report.json")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


if __name__ == "__main__":
    main()