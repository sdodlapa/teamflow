#!/bin/bash
# 🚀 TeamFlow Interactive Cloud Deployment Guide
# Step-by-step deployment with authentication

echo "🚀 TeamFlow Interactive Cloud Deployment Guide"
echo "==============================================="
echo "📅 Date: $(date)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}This guide will walk you through deploying TeamFlow to production.${NC}"
echo ""

echo -e "${YELLOW}STEP 1: Railway Authentication${NC}"
echo "----------------------------------------"
echo "Railway CLI is installed. Now you need to authenticate:"
echo ""
echo -e "${GREEN}1. Run: ${BLUE}railway login${NC}"
echo -e "${GREEN}2. This will open your browser to login to Railway${NC}"
echo -e "${GREEN}3. Create a Railway account if you don't have one${NC}"
echo -e "${GREEN}4. After login, come back to this terminal${NC}"
echo ""

echo -e "${YELLOW}STEP 2: Vercel Authentication${NC}"
echo "----------------------------------------" 
echo "Vercel CLI is installed. You'll need to authenticate:"
echo ""
echo -e "${GREEN}1. Run: ${BLUE}vercel login${NC}"
echo -e "${GREEN}2. This will prompt for your email or GitHub login${NC}"
echo -e "${GREEN}3. Create a Vercel account if you don't have one${NC}"
echo -e "${GREEN}4. Verify your email if required${NC}"
echo ""

echo -e "${YELLOW}STEP 3: Deploy Backend to Railway${NC}"
echo "----------------------------------------"
echo "After Railway authentication:"
echo ""
echo -e "${GREEN}1. cd backend${NC}"
echo -e "${GREEN}2. railway init --name teamflow-api-production${NC}"
echo -e "${GREEN}3. railway add postgresql${NC}"
echo -e "${GREEN}4. railway up${NC}"
echo ""

echo -e "${YELLOW}STEP 4: Deploy Frontend to Vercel${NC}"
echo "----------------------------------------"
echo "After Vercel authentication:"
echo ""
echo -e "${GREEN}1. cd frontend${NC}"
echo -e "${GREEN}2. vercel --prod${NC}"
echo -e "${GREEN}3. Follow prompts to configure project${NC}"
echo ""

echo -e "${YELLOW}STEP 5: Test Production Deployment${NC}"
echo "----------------------------------------"
echo "After deployment:"
echo ""
echo -e "${GREEN}1. Test backend: curl https://your-railway-url.up.railway.app/health${NC}"
echo -e "${GREEN}2. Test frontend: Open Vercel URL in browser${NC}"
echo -e "${GREEN}3. Verify API connection between frontend and backend${NC}"
echo ""

echo -e "${BLUE}📋 Quick Commands Summary:${NC}"
echo "=========================="
echo ""
echo -e "${YELLOW}Authentication:${NC}"
echo "railway login"
echo "vercel login"
echo ""
echo -e "${YELLOW}Backend Deployment:${NC}"
echo "cd backend"
echo "railway init --name teamflow-api-production"
echo "railway add postgresql"
echo "railway up"
echo ""
echo -e "${YELLOW}Frontend Deployment:${NC}"
echo "cd frontend"
echo "vercel --prod"
echo ""

echo -e "${GREEN}🎯 Let's start! Run the authentication commands above.${NC}"
echo ""
echo -e "${BLUE}When you're ready to continue, let me know and I'll help with the next steps!${NC}"