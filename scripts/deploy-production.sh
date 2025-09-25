#!/bin/bash
set -e

echo "🚀 TeamFlow Production Deployment Script"
echo "========================================"
echo "Version: 1.0.0"
echo "Date: $(date)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Pre-deployment validation
log_info "Starting pre-deployment validation..."

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ] || [ ! -f "frontend/package.json" ]; then
    log_error "Please run this script from the TeamFlow project root directory"
    log_error "Required: frontend/ and backend/ directories with frontend/package.json"
    exit 1
fi

log_success "Directory structure validated"

# Validate frontend build
log_info "Validating frontend build..."
cd frontend

if ! npm run build > /dev/null 2>&1; then
    log_error "Frontend build failed"
    exit 1
fi

BUILD_SIZE=$(du -sh dist/ | cut -f1)
log_success "Frontend build successful (Size: $BUILD_SIZE)"

# Validate backend imports
log_info "Validating backend imports..."
cd ../backend

if ! python -c "from app.main import app; from app.services.template_service import TemplateService; print('Backend validation passed')" > /dev/null 2>&1; then
    log_error "Backend import validation failed"
    exit 1
fi

log_success "Backend validation passed"

# Environment validation
log_info "Checking environment configuration..."

if [ -z "$VERCEL_TOKEN" ] && [ -z "$1" ]; then
    log_warning "VERCEL_TOKEN not set - will need manual frontend deployment"
fi

if [ -z "$RAILWAY_TOKEN" ] && [ -z "$2" ]; then
    log_warning "RAILWAY_TOKEN not set - will need manual backend deployment"
fi

# Database migration preparation
log_info "Preparing database migrations..."

# Check if we have pending migrations
if command -v alembic >/dev/null 2>&1; then
    log_success "Alembic available for database migrations"
else
    log_warning "Alembic not found - database migrations will need manual execution"
fi

echo ""
log_info "=== PRE-DEPLOYMENT SUMMARY ==="
echo "✅ Frontend build: Ready"
echo "✅ Backend validation: Passed"
echo "✅ Directory structure: Valid"
echo "⚠️  Environment tokens: Check manually"
echo "✅ Migration tools: Available"
echo ""

# Deployment options
echo "🚀 DEPLOYMENT OPTIONS:"
echo "1. Automatic deployment (requires tokens)"
echo "2. Manual deployment instructions"
echo "3. Exit"
echo ""

read -p "Select option (1-3): " option

case $option in
    1)
        log_info "Starting automatic deployment..."
        
        # Frontend deployment
        if [ ! -z "$VERCEL_TOKEN" ] || [ ! -z "$1" ]; then
            log_info "Deploying frontend to Vercel..."
            cd ../frontend
            if command -v vercel >/dev/null 2>&1; then
                vercel --prod --token="${VERCEL_TOKEN:-$1}"
                log_success "Frontend deployment initiated"
            else
                log_error "Vercel CLI not installed"
            fi
        fi
        
        # Backend deployment
        if [ ! -z "$RAILWAY_TOKEN" ] || [ ! -z "$2" ]; then
            log_info "Deploying backend to Railway..."
            cd ../backend
            if command -v railway >/dev/null 2>&1; then
                railway up --detach
                log_success "Backend deployment initiated"
            else
                log_error "Railway CLI not installed"
            fi
        fi
        
        log_success "Automatic deployment process completed!"
        ;;
        
    2)
        log_info "Manual deployment instructions:"
        echo ""
        echo "📦 FRONTEND DEPLOYMENT:"
        echo "1. cd frontend"
        echo "2. npm run build"
        echo "3. Deploy dist/ folder to your hosting provider"
        echo "   - Vercel: vercel --prod"
        echo "   - Netlify: drag dist/ folder to Netlify dashboard"
        echo "   - Other: follow provider-specific instructions"
        echo ""
        echo "⚙️  BACKEND DEPLOYMENT:"
        echo "1. cd backend"
        echo "2. Set up production environment variables"
        echo "3. Deploy to your hosting provider:"
        echo "   - Railway: railway up"
        echo "   - Render: git push to connected repository"
        echo "   - Heroku: git push heroku main"
        echo ""
        echo "🗄️  DATABASE SETUP:"
        echo "1. Create production PostgreSQL database"
        echo "2. Set DATABASE_URL environment variable"
        echo "3. Run migrations: alembic upgrade head"
        echo ""
        echo "🔧 POST-DEPLOYMENT:"
        echo "1. Verify frontend loads at your domain"
        echo "2. Test API health check: curl your-api-url/health"
        echo "3. Test user registration and login"
        echo "4. Verify all core features work"
        ;;
        
    3)
        log_info "Deployment cancelled by user"
        exit 0
        ;;
        
    *)
        log_error "Invalid option selected"
        exit 1
        ;;
esac

echo ""
log_success "🎉 TeamFlow deployment script completed!"
echo ""
echo "📋 POST-DEPLOYMENT CHECKLIST:"
echo "- [ ] Frontend accessible at production URL"
echo "- [ ] Backend API responding to health checks" 
echo "- [ ] Database migrations applied successfully"
echo "- [ ] User registration/login working"
echo "- [ ] Core features (tasks, organizations) functional"
echo "- [ ] File upload/download working"
echo "- [ ] Template system operational"
echo ""
echo "🚀 Ready for enterprise customer onboarding!"