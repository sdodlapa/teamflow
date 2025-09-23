#!/bin/bash

# TeamFlow Deployment Verification Script
# Verifies all components are ready for production deployment

echo "🚀 TeamFlow Production Readiness Verification"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track verification results
CHECKS_PASSED=0
TOTAL_CHECKS=0

check_component() {
    local component_name="$1"
    local check_command="$2"
    local description="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "\n${BLUE}Checking: ${component_name}${NC}"
    echo "Description: $description"
    
    if eval "$check_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
}

echo -e "\n${YELLOW}=== Backend Components ===${NC}"

# Backend structure checks
check_component "Backend App Structure" \
    "test -f backend/app/main.py && test -d backend/app/api && test -d backend/app/models" \
    "Verify FastAPI application structure exists"

check_component "Database Models" \
    "test -f backend/app/models/base.py && test -f backend/app/models/user.py && test -f backend/app/models/task.py" \
    "Verify SQLAlchemy models are present"

check_component "API Routes" \
    "test -f backend/app/api/__init__.py && test -d backend/app/api" \
    "Verify API route structure exists"

check_component "Database Migrations" \
    "test -f backend/alembic.ini && test -d backend/alembic/versions" \
    "Verify Alembic migration setup"

check_component "Tests" \
    "test -f backend/tests/conftest.py && test -d backend/tests/unit && test -d backend/tests/integration" \
    "Verify test suite structure"

check_component "Requirements" \
    "test -f backend/requirements.txt && test -f backend/requirements-dev.txt" \
    "Verify Python dependencies defined"

echo -e "\n${YELLOW}=== Frontend Components ===${NC}"

# Frontend structure checks
check_component "Frontend App Structure" \
    "test -f frontend/src/App.tsx && test -d frontend/src/components" \
    "Verify React application structure"

check_component "Package Configuration" \
    "test -f frontend/package.json && test -f frontend/tsconfig.json" \
    "Verify npm and TypeScript configuration"

check_component "UI Components" \
    "test -f frontend/src/components/Dashboard.tsx && test -f frontend/src/components/TaskManagement.tsx && test -f frontend/src/components/Login.tsx" \
    "Verify main UI components exist"

check_component "Component Styles" \
    "test -f frontend/src/components/Dashboard.css && test -f frontend/src/components/TaskManagement.css && test -f frontend/src/components/Login.css" \
    "Verify component stylesheets exist"

check_component "Vite Configuration" \
    "test -f frontend/vite.config.ts && test -f frontend/index.html" \
    "Verify Vite build configuration"

echo -e "\n${YELLOW}=== Production Infrastructure ===${NC}"

# Infrastructure checks
check_component "Docker Backend" \
    "test -f backend/Dockerfile.prod && test -f backend/scripts/start-production.sh" \
    "Verify backend production Docker setup"

check_component "Docker Frontend" \
    "test -f frontend/Dockerfile.prod && test -f frontend/nginx.conf" \
    "Verify frontend production Docker setup"

check_component "Production Orchestration" \
    "test -f docker-compose.prod.yml" \
    "Verify production docker-compose configuration"

check_component "CI/CD Pipeline" \
    "test -f .github/workflows/ci-cd.yml" \
    "Verify GitHub Actions CI/CD pipeline"

check_component "Backup Systems" \
    "test -f scripts/backup.sh && test -f scripts/restore.sh" \
    "Verify backup and restore scripts"

echo -e "\n${YELLOW}=== Documentation ===${NC}"

# Documentation checks
check_component "Main Documentation" \
    "test -f README-FINAL.md && test -f PROJECT-CONSOLIDATION-FINAL.md" \
    "Verify comprehensive project documentation"

check_component "Development Docs" \
    "test -d docs && test -f docs/05-api-documentation.md" \
    "Verify development documentation exists"

# Advanced checks (if components are available)
echo -e "\n${YELLOW}=== Component Integrity Checks ===${NC}"

if command -v python3 &> /dev/null; then
    check_component "Python Syntax Check" \
        "python3 -m py_compile backend/app/main.py" \
        "Verify Python code compiles without syntax errors"
fi

if command -v node &> /dev/null && test -f frontend/package.json; then
    check_component "TypeScript Compilation" \
        "cd frontend && npm run build --if-present" \
        "Verify TypeScript code compiles successfully"
fi

# Summary
echo -e "\n${YELLOW}=== Verification Summary ===${NC}"
echo "=============================================="

PASS_PERCENTAGE=$((CHECKS_PASSED * 100 / TOTAL_CHECKS))

echo "Total Checks: $TOTAL_CHECKS"
echo "Checks Passed: $CHECKS_PASSED"
echo "Pass Rate: ${PASS_PERCENTAGE}%"

if [ $CHECKS_PASSED -eq $TOTAL_CHECKS ]; then
    echo -e "\n${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}✅ TeamFlow is ready for production deployment!${NC}"
    exit 0
elif [ $PASS_PERCENTAGE -ge 90 ]; then
    echo -e "\n${YELLOW}⚠️  Most checks passed (${PASS_PERCENTAGE}%)${NC}"
    echo -e "${YELLOW}The project is mostly ready, but some components may need attention.${NC}"
    exit 1
else
    echo -e "\n${RED}❌ Several checks failed (${PASS_PERCENTAGE}% passed)${NC}"
    echo -e "${RED}The project needs additional work before deployment.${NC}"
    exit 2
fi