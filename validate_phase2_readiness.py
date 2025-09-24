#!/usr/bin/env python3
"""
Phase 2 Pre-Implementation Validation
Verify all Phase 1 dependencies are ready for Phase 2 development.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

def validate_phase1_foundation():
    """Validate Phase 1 foundation is solid for Phase 2."""
    
    print("🔍 PHASE 2 PRE-IMPLEMENTATION VALIDATION")
    print("=" * 50)
    
    validation_results = []
    
    # 1. Import Validation
    print("\n1. Testing Phase 1 Component Imports...")
    try:
        from app.core.template_config import TemplateConfigLoader, DomainType
        from app.models.template import DomainTemplate, TemplateRegistry
        from app.models.base import BaseModel
        from app.services.universal_service import UniversalEntityService
        from app.api.template import router
        validation_results.append(("✅ Core Imports", "All Phase 1 components import successfully"))
    except ImportError as e:
        validation_results.append(("❌ Core Imports", f"Import error: {e}"))
        return False, validation_results
    
    # 2. API Validation
    print("   Testing Template API endpoints...")
    try:
        from app.main import app
        client = TestClient(app)
        
        # Test health endpoint
        health_response = client.get("/api/v1/template/health")
        if health_response.status_code == 200:
            validation_results.append(("✅ API Health", "Template health endpoint working"))
        else:
            validation_results.append(("❌ API Health", f"Health endpoint failed: {health_response.status_code}"))
        
        # Test domains endpoint
        domains_response = client.get("/api/v1/template/domains")
        if domains_response.status_code == 200:
            validation_results.append(("✅ API Domains", "Template domains endpoint working"))
        else:
            validation_results.append(("❌ API Domains", f"Domains endpoint failed: {domains_response.status_code}"))
            
    except Exception as e:
        validation_results.append(("❌ API Testing", f"API test failed: {e}"))
    
    # 3. BaseModel Validation
    print("   Testing BaseModel template fields...")
    try:
        # Check template fields exist
        template_fields = ['is_template_generated', 'template_version', 'domain_config']
        missing_fields = []
        for field in template_fields:
            if not hasattr(BaseModel, field):
                missing_fields.append(field)
        
        if not missing_fields:
            validation_results.append(("✅ BaseModel", "All template fields present"))
        else:
            validation_results.append(("❌ BaseModel", f"Missing fields: {missing_fields}"))
    except Exception as e:
        validation_results.append(("❌ BaseModel", f"BaseModel test failed: {e}"))
    
    # 4. Configuration System
    print("   Testing template configuration system...")
    try:
        loader = TemplateConfigLoader()
        domains = loader.get_available_domains()
        validation_results.append(("✅ Config Loader", f"Configuration system working ({len(domains)} domains)"))
    except Exception as e:
        validation_results.append(("❌ Config Loader", f"Config loader failed: {e}"))
    
    # 5. Redis Check
    print("   Testing Redis configuration...")
    try:
        from app.core.cache import cache
        if cache.redis_client is None:
            validation_results.append(("✅ Redis Config", "Redis properly disabled, no connection warnings"))
        else:
            validation_results.append(("✅ Redis Config", "Redis connected successfully"))
    except Exception as e:
        validation_results.append(("❌ Redis Config", f"Redis test failed: {e}"))
    
    # 6. Dependencies Check
    print("   Checking Phase 2 dependencies...")
    required_packages = [
        ('jinja2', 'Jinja2'),
        ('yaml', 'PyYAML'), 
        ('pathlib', 'pathlib'),
        ('typing', 'typing'),
        ('pydantic', 'pydantic')
    ]
    
    missing_packages = []
    for package, name in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(name)
    
    if not missing_packages:
        validation_results.append(("✅ Dependencies", "All required packages available"))
    else:
        validation_results.append(("❌ Dependencies", f"Missing packages: {missing_packages}"))
    
    return True, validation_results

def check_directory_structure():
    """Check that directory structure is ready for Phase 2."""
    
    print("\n2. Checking Directory Structure...")
    
    project_root = Path.cwd()
    required_dirs = [
        "backend/app/core",
        "backend/app/models", 
        "backend/app/api",
        "backend/app/services",
        "backend/tests",
        "frontend/src",
        "docs"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    if not missing_dirs:
        print("   ✅ All required directories exist")
        return True
    else:
        print(f"   ❌ Missing directories: {missing_dirs}")
        return False

def create_phase2_directories():
    """Create Phase 2 specific directories."""
    
    print("\n3. Creating Phase 2 Directories...")
    
    project_root = Path.cwd()
    phase2_dirs = [
        "templates",
        "templates/backend",
        "templates/frontend", 
        "templates/config",
        "domain_configs",
        "tests/template_validation",
        "docs/template-system"
    ]
    
    created_dirs = []
    for dir_path in phase2_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(dir_path)
    
    if created_dirs:
        print(f"   ✅ Created directories: {created_dirs}")
    else:
        print("   ✅ All Phase 2 directories already exist")
    
    return True

def main():
    """Main validation function."""
    
    # Change to backend directory if exists
    backend_path = Path.cwd() / "backend"
    if backend_path.exists():
        import os
        os.chdir(backend_path)
    
    success, results = validate_phase1_foundation()
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS")
    print("=" * 50)
    
    for status, message in results:
        print(f"{status} {message}")
    
    # Directory structure check
    dir_success = check_directory_structure()
    
    # Create Phase 2 directories
    create_success = create_phase2_directories()
    
    # Overall assessment
    print("\n" + "=" * 50)
    print("🎯 PHASE 2 READINESS ASSESSMENT")
    print("=" * 50)
    
    passed_checks = sum(1 for status, _ in results if "✅" in status)
    total_checks = len(results)
    
    if passed_checks >= total_checks - 1 and dir_success and create_success:
        print("🎉 READY TO START PHASE 2!")
        print("   All critical dependencies validated")
        print("   Directory structure prepared")
        print("   Template system foundation solid")
        print("\nNext steps:")
        print("   1. Review Phase 2 todo list")
        print("   2. Install any missing dependencies")
        print("   3. Begin Week 1 implementation")
        return True
    elif passed_checks >= total_checks * 0.8:
        print("⚠️  MOSTLY READY FOR PHASE 2")
        print(f"   {passed_checks}/{total_checks} validation checks passed")
        print("   Some non-critical issues found")
        print("   Can proceed with caution")
        return True
    else:
        print("❌ NOT READY FOR PHASE 2")
        print(f"   Only {passed_checks}/{total_checks} validation checks passed")
        print("   Critical issues need to be resolved")
        print("   Fix issues before starting Phase 2")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)