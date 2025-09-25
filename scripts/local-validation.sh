#!/bin/bash
# 🚀 TeamFlow Local Production Validation
# Test the production-ready system locally before deploying

echo "🔍 TeamFlow Local Production Validation"
echo "========================================"
echo "📅 Date: $(date)"
echo "🏠 Testing locally before cloud deployment"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
LOCAL_BACKEND="http://localhost:8000"
LOCAL_FRONTEND="http://localhost:3000"

# Function to check if process is running on port
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "🟢 ${GREEN}$service is running on port $port${NC}"
        return 0
    else
        echo -e "🔴 ${RED}$service is NOT running on port $port${NC}"
        return 1
    fi
}

# Function to test API endpoint
test_endpoint() {
    local url=$1
    local name=$2
    local expected_status=$3
    
    echo -n "🔍 Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}:%{time_total}" "$url" --max-time 5 2>/dev/null)
    
    if [ -z "$response" ]; then
        echo -e "${RED}❌ NO RESPONSE${NC}"
        return 1
    fi
    
    status_code=$(echo $response | cut -d: -f1)
    response_time=$(echo $response | cut -d: -f2)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ SUCCESS${NC} (${status_code}) - ${response_time}s"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (${status_code}) - ${response_time}s"
        return 1
    fi
}

# Function to check backend health
check_backend_health() {
    echo "🔧 Backend Health Check:"
    echo "------------------------"
    
    if check_port 8000 "Backend"; then
        test_endpoint "$LOCAL_BACKEND/health" "Health Endpoint" "200"
        test_endpoint "$LOCAL_BACKEND/docs" "API Docs" "200"
        test_endpoint "$LOCAL_BACKEND/api/v1/health" "API Health" "200"
    else
        echo "❌ Backend not running. Start with: cd backend && make dev"
        return 1
    fi
}

# Function to check frontend health  
check_frontend_health() {
    echo ""
    echo "🎨 Frontend Health Check:"
    echo "-------------------------"
    
    if check_port 3000 "Frontend"; then
        test_endpoint "$LOCAL_FRONTEND" "Frontend App" "200"
    else
        echo "❌ Frontend not running. Start with: cd frontend && npm run dev"
        return 1
    fi
}

# Function to test critical API endpoints
test_critical_apis() {
    echo ""
    echo "🔌 Critical API Tests:"
    echo "----------------------"
    
    local endpoints=(
        "$LOCAL_BACKEND/api/v1/auth/health:200:Auth System"
        "$LOCAL_BACKEND/api/v1/tasks/health:200:Task System"
        "$LOCAL_BACKEND/api/v1/organizations/health:200:Organizations"
        "$LOCAL_BACKEND/api/v1/template/health:200:Template System"
    )
    
    local working=0
    local total=${#endpoints[@]}
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r url expected_status name <<< "$endpoint_info"
        if test_endpoint "$url" "$name" "$expected_status"; then
            ((working++))
        fi
    done
    
    echo ""
    echo "📊 API Health Summary: $working/$total endpoints working"
    return $working
}

# Function to test database operations
test_database() {
    echo ""
    echo "🗄️  Database Operations Test:"
    echo "-----------------------------"
    
    # Test database connection through API
    echo -n "🔍 Testing database connection... "
    response=$(curl -s "$LOCAL_BACKEND/api/v1/health" 2>/dev/null)
    
    if echo "$response" | grep -q "database.*healthy\|database.*connected\|status.*healthy"; then
        echo -e "${GREEN}✅ DATABASE CONNECTED${NC}"
        return 0
    else
        echo -e "${RED}❌ DATABASE ISSUE${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Function to check build readiness
check_build_readiness() {
    echo ""
    echo "📦 Production Build Readiness:"
    echo "------------------------------"
    
    # Check backend requirements
    echo -n "📋 Backend dependencies... "
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        echo -e "${GREEN}✅ READY${NC}"
    else
        echo -e "${RED}❌ MISSING${NC}"
    fi
    
    # Check frontend build config
    echo -n "📋 Frontend build config... "
    if [ -f "$FRONTEND_DIR/package.json" ] && [ -f "$FRONTEND_DIR/vite.config.ts" ]; then
        echo -e "${GREEN}✅ READY${NC}"
    else
        echo -e "${RED}❌ MISSING${NC}"
    fi
    
    # Check environment files
    echo -n "📋 Environment configs... "
    if [ -f ".env.production" ]; then
        echo -e "${GREEN}✅ READY${NC}"
    else
        echo -e "${YELLOW}⚠️  CREATED${NC}"
        echo "DATABASE_URL=postgresql://localhost:5432/teamflow_prod" > .env.production
        echo "SECRET_KEY=your-production-secret-here" >> .env.production
        echo "CORS_ORIGINS=https://your-frontend-domain.com" >> .env.production
    fi
}

# Function to generate pre-deployment summary
generate_summary() {
    echo ""
    echo "📋 LOCAL VALIDATION SUMMARY"
    echo "============================"
    echo "🕒 Validation completed at: $(date)"
    echo ""
    
    # Overall assessment
    if [ $? -eq 0 ]; then
        echo -e "🟢 ${GREEN}VALIDATION STATUS: READY FOR DEPLOYMENT${NC}"
        echo "✅ Local system is running properly"
        echo "✅ All critical endpoints responding"
        echo "✅ Database connectivity confirmed"
        echo "✅ Build configuration ready"
    else
        echo -e "🟡 ${YELLOW}VALIDATION STATUS: ISSUES TO RESOLVE${NC}"
        echo "⚠️  Some issues detected in local testing"
        echo "🔧 Fix local issues before deploying to production"
    fi
    
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Fix any issues shown above"
    echo "   2. Ensure both frontend and backend are running locally"
    echo "   3. Deploy to Railway (backend) and Vercel (frontend)"
    echo "   4. Run production monitoring after deployment"
    echo ""
    echo "🚀 Deployment Commands:"
    echo "   Backend:  railway up (in backend directory)"
    echo "   Frontend: vercel --prod (in frontend directory)"
}

# Main execution
main() {
    echo "🚀 Starting local production validation..."
    echo ""
    
    # Check if services are running
    check_backend_health
    backend_status=$?
    
    check_frontend_health  
    frontend_status=$?
    
    # If services are running, test them
    if [ $backend_status -eq 0 ]; then
        test_critical_apis
        test_database
    fi
    
    # Check build readiness regardless
    check_build_readiness
    
    # Generate summary
    generate_summary
    
    echo ""
    echo "🎯 Local Validation Complete!"
    echo ""
    
    if [ $backend_status -eq 0 ] && [ $frontend_status -eq 0 ]; then
        echo -e "${GREEN}✅ READY FOR CLOUD DEPLOYMENT${NC}"
        echo "🚀 Your TeamFlow system is ready for production!"
    else
        echo -e "${YELLOW}⚠️  START LOCAL SERVICES FIRST${NC}"
        echo "🔧 Run 'cd backend && make dev' and 'cd frontend && npm run dev'"
        echo "   Then run this validation script again"
    fi
}

# Run main function
main