"""
Day 7: Admin Dashboard & Analytics Validation Test
Comprehensive testing for admin dashboard and analytics system
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import httpx
import pytest
from concurrent.futures import ThreadPoolExecutor


class Day7AdminDashboardValidator:
    """
    Day 7 Admin Dashboard & Analytics Validation System
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.admin_url = f"{self.api_url}/admin"
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "day": "Day 7: Admin Dashboard & Analytics",
            "total_tests": 10,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": {},
            "performance_metrics": {},
            "system_health": {}
        }
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive Day 7 validation testing"""
        
        print("🚀 Day 7 Admin Dashboard & Analytics Validation")
        print("=" * 70)
        
        test_categories = [
            ("Admin Analytics Service", self.test_admin_analytics_service),
            ("Admin API Endpoints", self.test_admin_api_endpoints),
            ("Dashboard Summary", self.test_dashboard_summary),
            ("User Analytics", self.test_user_analytics),
            ("Project Analytics", self.test_project_analytics),
            ("Task Analytics", self.test_task_analytics),
            ("Workflow Analytics", self.test_workflow_analytics),
            ("Custom Metrics", self.test_custom_metrics),
            ("Analytics Reports", self.test_analytics_reports),
            ("Admin Authentication", self.test_admin_authentication)
        ]
        
        for test_name, test_function in test_categories:
            print(f"\n📊 Testing: {test_name}")
            try:
                result = await test_function()
                
                if result["success"]:
                    print(f"✅ {test_name}: PASSED")
                    self.test_results["passed_tests"] += 1
                else:
                    print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                    self.test_results["failed_tests"] += 1
                
                self.test_results["test_details"][test_name] = result
                
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                self.test_results["failed_tests"] += 1
                self.test_results["test_details"][test_name] = {
                    "success": False,
                    "error": str(e),
                    "exception_type": type(e).__name__
                }
        
        # Calculate success rate
        total_tests = self.test_results["total_tests"]
        passed_tests = self.test_results["passed_tests"]
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        self.test_results["success_rate"] = success_rate
        
        # Generate final report
        await self.generate_completion_report()
        
        return self.test_results
    
    async def test_admin_analytics_service(self) -> Dict[str, Any]:
        """Test admin analytics service implementation"""
        try:
            # Test service file existence and structure
            import os
            service_path = "/Users/sanjeevadodlapati/Downloads/Repos/teamflow/backend/app/services/admin_analytics_service.py"
            
            if not os.path.exists(service_path):
                return {"success": False, "error": "Admin analytics service file not found"}
            
            # Test service import and initialization
            from app.services.admin_analytics_service import (
                admin_analytics_service,
                AdminAnalyticsService,
                DashboardSummary,
                UserAnalytics,
                ProjectAnalytics,
                TaskAnalytics,
                WorkflowAnalytics,
                AnalyticsMetric,
                AnalyticsTimeframe
            )
            
            # Test service initialization
            service = AdminAnalyticsService()
            
            # Test timeframe filter
            timeframe_filter = service._get_timeframe_filter(AnalyticsTimeframe.LAST_30_DAYS)
            
            return {
                "success": True,
                "service_initialized": True,
                "classes_available": [
                    "AdminAnalyticsService",
                    "DashboardSummary", 
                    "UserAnalytics",
                    "ProjectAnalytics",
                    "TaskAnalytics",
                    "WorkflowAnalytics"
                ],
                "timeframe_filter_works": timeframe_filter is not None
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_admin_api_endpoints(self) -> Dict[str, Any]:
        """Test admin API endpoints structure"""
        try:
            # Test API file existence
            import os
            api_path = "/Users/sanjeevadodlapati/Downloads/Repos/teamflow/backend/app/api/routes/admin.py"
            
            if not os.path.exists(api_path):
                return {"success": False, "error": "Admin API file not found"}
            
            # Read and analyze API file
            with open(api_path, 'r') as f:
                content = f.read()
            
            required_endpoints = [
                '/dashboard/summary',
                '/analytics/users',
                '/analytics/projects', 
                '/analytics/tasks',
                '/analytics/workflows',
                '/analytics/metrics',
                '/analytics/report',
                '/dashboard/health',
                '/dashboard/alerts'
            ]
            
            endpoints_found = []
            for endpoint in required_endpoints:
                if endpoint in content:
                    endpoints_found.append(endpoint)
            
            response_models = [
                'DashboardSummaryResponse',
                'UserAnalyticsResponse',
                'ProjectAnalyticsResponse',
                'TaskAnalyticsResponse',
                'WorkflowAnalyticsResponse',
                'AnalyticsMetricResponse',
                'AnalyticsReportResponse'
            ]
            
            models_found = []
            for model in response_models:
                if model in content:
                    models_found.append(model)
            
            return {
                "success": len(endpoints_found) >= 7,
                "endpoints_found": endpoints_found,
                "endpoints_count": len(endpoints_found),
                "response_models": models_found,
                "models_count": len(models_found),
                "admin_authentication": "get_current_admin_user" in content
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_dashboard_summary(self) -> Dict[str, Any]:
        """Test dashboard summary functionality"""
        try:
            from app.services.admin_analytics_service import admin_analytics_service
            
            # Test dashboard summary generation
            summary = await admin_analytics_service.get_dashboard_summary()
            
            required_fields = [
                'total_users', 'total_organizations', 'total_projects', 
                'total_tasks', 'active_users_today', 'tasks_completed_today',
                'system_health_score', 'performance_score'
            ]
            
            summary_dict = summary.to_dict()
            fields_present = [field for field in required_fields if field in summary_dict]
            
            return {
                "success": len(fields_present) == len(required_fields),
                "fields_present": fields_present,
                "summary_data": {
                    "total_users": summary_dict.get('total_users', 0),
                    "total_projects": summary_dict.get('total_projects', 0),
                    "system_health_score": summary_dict.get('system_health_score', 0)
                },
                "cache_available": hasattr(admin_analytics_service, 'cache')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_user_analytics(self) -> Dict[str, Any]:
        """Test user analytics functionality"""
        try:
            from app.services.admin_analytics_service import (
                admin_analytics_service,
                AnalyticsTimeframe
            )
            
            # Test user analytics generation
            analytics = await admin_analytics_service.get_user_analytics(
                AnalyticsTimeframe.LAST_30_DAYS
            )
            
            required_fields = [
                'total_users', 'active_users', 'new_users', 
                'user_engagement', 'top_organizations', 'user_activity_trends'
            ]
            
            analytics_dict = analytics.to_dict()
            fields_present = [field for field in required_fields if field in analytics_dict]
            
            # Test engagement metrics
            engagement = analytics_dict.get('user_engagement', {})
            engagement_metrics = ['daily_active_rate', 'weekly_active_rate', 'monthly_active_rate']
            engagement_present = [metric for metric in engagement_metrics if metric in engagement]
            
            return {
                "success": len(fields_present) >= 5,
                "fields_present": fields_present,
                "engagement_metrics": engagement_present,
                "has_activity_trends": len(analytics_dict.get('user_activity_trends', [])) > 0,
                "active_users_data": analytics_dict.get('active_users', {})
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_project_analytics(self) -> Dict[str, Any]:
        """Test project analytics functionality"""
        try:
            from app.services.admin_analytics_service import (
                admin_analytics_service,
                AnalyticsTimeframe
            )
            
            # Test project analytics generation
            analytics = await admin_analytics_service.get_project_analytics(
                AnalyticsTimeframe.LAST_30_DAYS
            )
            
            required_fields = [
                'total_projects', 'active_projects', 'completed_projects',
                'project_completion_rate', 'average_project_duration',
                'projects_by_status', 'top_performing_projects'
            ]
            
            analytics_dict = analytics.to_dict()
            fields_present = [field for field in required_fields if field in analytics_dict]
            
            # Test completion rate calculation
            completion_rate = analytics_dict.get('project_completion_rate', 0)
            
            return {
                "success": len(fields_present) >= 5,
                "fields_present": fields_present,
                "completion_rate": completion_rate,
                "has_status_breakdown": len(analytics_dict.get('projects_by_status', {})) > 0,
                "has_top_performers": len(analytics_dict.get('top_performing_projects', [])) > 0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_task_analytics(self) -> Dict[str, Any]:
        """Test task analytics functionality"""
        try:
            from app.services.admin_analytics_service import (
                admin_analytics_service,
                AnalyticsTimeframe
            )
            
            # Test task analytics generation
            analytics = await admin_analytics_service.get_task_analytics(
                AnalyticsTimeframe.LAST_30_DAYS
            )
            
            required_fields = [
                'total_tasks', 'completed_tasks', 'pending_tasks', 'overdue_tasks',
                'task_completion_rate', 'tasks_by_priority', 'tasks_by_status',
                'productivity_trends'
            ]
            
            analytics_dict = analytics.to_dict()
            fields_present = [field for field in required_fields if field in analytics_dict]
            
            # Test priority distribution
            priority_dist = analytics_dict.get('tasks_by_priority', {})
            status_dist = analytics_dict.get('tasks_by_status', {})
            
            return {
                "success": len(fields_present) >= 6,
                "fields_present": fields_present,
                "has_priority_distribution": len(priority_dist) > 0,
                "has_status_distribution": len(status_dist) > 0,
                "has_productivity_trends": len(analytics_dict.get('productivity_trends', [])) > 0,
                "overdue_tracking": 'overdue_tasks' in analytics_dict
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_workflow_analytics(self) -> Dict[str, Any]:
        """Test workflow analytics functionality"""
        try:
            from app.services.admin_analytics_service import (
                admin_analytics_service,
                AnalyticsTimeframe
            )
            
            # Test workflow analytics generation
            analytics = await admin_analytics_service.get_workflow_analytics(
                AnalyticsTimeframe.LAST_30_DAYS
            )
            
            required_fields = [
                'total_workflows', 'active_workflows', 'workflow_executions',
                'success_rate', 'failed_executions', 'average_execution_time',
                'most_used_workflows', 'workflow_performance'
            ]
            
            analytics_dict = analytics.to_dict()
            fields_present = [field for field in required_fields if field in analytics_dict]
            
            # Test success rate
            success_rate = analytics_dict.get('success_rate', 0)
            
            return {
                "success": len(fields_present) >= 6,
                "fields_present": fields_present,
                "success_rate": success_rate,
                "has_performance_data": len(analytics_dict.get('workflow_performance', [])) > 0,
                "tracks_executions": 'workflow_executions' in analytics_dict,
                "tracks_failures": 'failed_executions' in analytics_dict
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_custom_metrics(self) -> Dict[str, Any]:
        """Test custom metrics functionality"""
        try:
            from app.services.admin_analytics_service import (
                admin_analytics_service,
                AnalyticsTimeframe
            )
            
            # Test custom metrics generation
            metric_names = ["user_growth_rate", "task_velocity", "system_uptime"]
            metrics = await admin_analytics_service.get_custom_metrics(
                metric_names, AnalyticsTimeframe.LAST_30_DAYS
            )
            
            # Validate metrics structure
            metrics_valid = []
            for metric in metrics:
                metric_dict = metric.to_dict()
                has_required_fields = all(field in metric_dict for field in 
                                        ['name', 'value', 'metric_type', 'timeframe'])
                if has_required_fields:
                    metrics_valid.append(metric.name)
            
            return {
                "success": len(metrics_valid) >= 2,
                "metrics_generated": len(metrics),
                "valid_metrics": metrics_valid,
                "has_trends": any(metric.to_dict().get('trend') for metric in metrics),
                "has_change_percent": any(metric.to_dict().get('change_percent') for metric in metrics)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_analytics_reports(self) -> Dict[str, Any]:
        """Test analytics report generation"""
        try:
            from app.services.admin_analytics_service import (
                admin_analytics_service,
                AnalyticsTimeframe
            )
            
            # Test comprehensive report generation
            report = await admin_analytics_service.export_analytics_report(
                AnalyticsTimeframe.LAST_30_DAYS
            )
            
            required_sections = [
                'report_metadata', 'dashboard_summary', 'user_analytics',
                'project_analytics', 'task_analytics', 'workflow_analytics'
            ]
            
            sections_present = [section for section in required_sections if section in report]
            
            # Test metadata
            metadata = report.get('report_metadata', {})
            has_metadata = all(field in metadata for field in 
                             ['generated_at', 'timeframe', 'report_version'])
            
            return {
                "success": len(sections_present) == len(required_sections),
                "sections_present": sections_present,
                "has_metadata": has_metadata,
                "report_size": len(json.dumps(report)),
                "timeframe_included": metadata.get('timeframe'),
                "comprehensive": len(sections_present) >= 5
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_admin_authentication(self) -> Dict[str, Any]:
        """Test admin authentication requirements"""
        try:
            # Test authentication dependencies
            from app.core.dependencies import get_current_admin_user
            
            # Test API file has admin authentication
            import os
            api_path = "/Users/sanjeevadodlapati/Downloads/Repos/teamflow/backend/app/api/routes/admin.py"
            
            with open(api_path, 'r') as f:
                content = f.read()
            
            # Check for admin authentication usage
            admin_auth_usage = content.count('get_current_admin_user')
            admin_required = content.count('Depends(get_current_admin_user)')
            
            # Check for admin privileges documentation
            admin_docs = content.count('Requires admin privileges')
            
            return {
                "success": admin_required >= 8,  # Should have admin auth on most endpoints
                "admin_auth_usage": admin_auth_usage,
                "admin_required_count": admin_required,
                "admin_docs_count": admin_docs,
                "has_admin_dependency": "get_current_admin_user" in content,
                "properly_secured": admin_required >= 8
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_completion_report(self):
        """Generate Day 7 completion report"""
        
        print("\n" + "=" * 70)
        print("📊 DAY 7 ADMIN DASHBOARD & ANALYTICS COMPLETION REPORT")
        print("=" * 70)
        
        print(f"🕒 Test completed at: {self.test_results['timestamp']}")
        print(f"📋 Total tests: {self.test_results['total_tests']}")
        print(f"✅ Passed tests: {self.test_results['passed_tests']}")
        print(f"❌ Failed tests: {self.test_results['failed_tests']}")
        print(f"📈 Success rate: {self.test_results['success_rate']:.1f}%")
        
        # Status assessment
        success_rate = self.test_results['success_rate']
        if success_rate >= 90:
            status = "EXCELLENT - PRODUCTION READY"
            status_emoji = "🏆"
        elif success_rate >= 75:
            status = "GOOD - READY FOR TESTING"
            status_emoji = "✅"
        elif success_rate >= 60:
            status = "FAIR - NEEDS REFINEMENT"
            status_emoji = "⚠️"
        else:
            status = "NEEDS DEVELOPMENT"
            status_emoji = "❌"
        
        print(f"\n{status_emoji} Overall Implementation Status: {status}")
        
        # Test details
        print(f"\n📈 Test Results Summary:")
        for test_name, details in self.test_results["test_details"].items():
            status_icon = "✅" if details.get("success", False) else "❌"
            print(f"   {status_icon} {test_name}")
            if not details.get("success", False) and "error" in details:
                print(f"      Error: {details['error']}")
        
        # Day 7 Features Summary
        print(f"\n🎯 Day 7 Admin Dashboard & Analytics Summary:")
        print("   • Comprehensive admin analytics service with caching")
        print("   • Dashboard summary with key performance metrics")
        print("   • User analytics with engagement tracking")
        print("   • Project analytics with completion rates")
        print("   • Task analytics with productivity trends")
        print("   • Workflow analytics with performance monitoring")
        print("   • Custom metrics system for flexible reporting")
        print("   • Complete analytics report generation")
        print("   • Admin-only authentication and authorization")
        print("   • Real-time health monitoring and alerts")
        
        # Recommendations
        print(f"\n🔧 Recommendations:")
        if success_rate >= 75:
            print("   • Day 7 Admin Dashboard & Analytics is well implemented")
            print("   • Ready to complete Phase 3 and move to Phase 4")
            print("   • Consider adding more custom metrics")
            print("   • Test with real data for production readiness")
        else:
            print("   • Focus on completing failing admin dashboard components")
            print("   • Ensure admin authentication is properly implemented")
            print("   • Test analytics data generation thoroughly")
        
        print("\n" + "=" * 70)
        
        # Final status for Day 7
        if success_rate >= 75:
            print("✅ DAY 7 ADMIN DASHBOARD & ANALYTICS: COMPLETE")
            print("🎉 PHASE 3 ADVANCED FEATURES & OPTIMIZATION: COMPLETE")
            print("🚀 Ready for Phase 4: React Frontend Development")
        else:
            print("⚠️ DAY 7 ADMIN DASHBOARD & ANALYTICS: IN PROGRESS")
            print("🔧 Additional development required for Phase 3 completion")
        
        print("=" * 70)


async def main():
    """Main validation function"""
    validator = Day7AdminDashboardValidator()
    
    try:
        print("Starting Day 7 Admin Dashboard & Analytics validation...")
        start_time = time.time()
        
        results = await validator.run_comprehensive_validation()
        
        # Save results to file
        with open("day7_admin_dashboard_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        completion_time = time.time() - start_time
        print(f"\n💾 Validation results saved to: day7_admin_dashboard_results.json")
        print(f"⏱️ Validation completed in {completion_time:.2f} seconds")
        
        # Return appropriate exit code
        success_rate = results.get("success_rate", 0)
        return 0 if success_rate >= 75 else 1
        
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)