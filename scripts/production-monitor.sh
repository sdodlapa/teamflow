#!/bin/bash
# 🚀 TeamFlow Production Monitoring Script
# Automated health checks and status monitoring for production environment

echo "🔍 TeamFlow Production Health Monitor"
echo "========================================"
echo "📅 Date: $(date)"
echo "🌐 Production Environment Status Check"
echo ""

# Configuration
FRONTEND_URL="https://teamflow.vercel.app"
BACKEND_URL="https://teamflow-api-production.up.railway.app"
HEALTH_ENDPOINT="$BACKEND_URL/health"
API_HEALTH_ENDPOINT="$BACKEND_URL/api/v1/health"
LOG_FILE="production-monitoring.log"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check HTTP status
check_http_status() {
    local url=$1
    local name=$2
    local expected_status=$3
    
    echo -n "🌐 Checking $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}:%{time_total}" "$url" --max-time 10)
    status_code=$(echo $response | cut -d: -f1)
    response_time=$(echo $response | cut -d: -f2)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ UP${NC} (${status_code}) - ${response_time}s"
        echo "$(date): $name - UP ($status_code) - ${response_time}s" >> $LOG_FILE
        return 0
    else
        echo -e "${RED}❌ DOWN${NC} (${status_code}) - ${response_time}s"
        echo "$(date): $name - DOWN ($status_code) - ${response_time}s" >> $LOG_FILE
        return 1
    fi
}

# Function to check specific endpoint with content validation
check_endpoint_content() {
    local url=$1
    local name=$2
    local expected_content=$3
    
    echo -n "🔍 Checking $name content... "
    
    start_time=$(date +%s.%N)
    response=$(curl -s "$url" --max-time 10)
    end_time=$(date +%s.%N)
    response_time=$(echo "$end_time - $start_time" | bc)
    
    if echo "$response" | grep -q "$expected_content"; then
        echo -e "${GREEN}✅ HEALTHY${NC} - ${response_time}s"
        echo "$(date): $name Content - HEALTHY - ${response_time}s" >> $LOG_FILE
        return 0
    else
        echo -e "${RED}❌ UNHEALTHY${NC} - ${response_time}s"
        echo "$(date): $name Content - UNHEALTHY - ${response_time}s" >> $LOG_FILE
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    echo -n "🗄️  Checking database connectivity... "
    
    # Use the API health endpoint to check database
    response=$(curl -s "$API_HEALTH_ENDPOINT" --max-time 10)
    
    if echo "$response" | grep -q "database.*healthy\|database.*connected\|status.*healthy"; then
        echo -e "${GREEN}✅ CONNECTED${NC}"
        echo "$(date): Database - CONNECTED" >> $LOG_FILE
        return 0
    else
        echo -e "${RED}❌ CONNECTION ISSUE${NC}"
        echo "$(date): Database - CONNECTION ISSUE" >> $LOG_FILE
        return 1
    fi
}

# Function to check API endpoints
check_critical_apis() {
    echo "🔌 Critical API Endpoint Checks:"
    echo "--------------------------------"
    
    local endpoints=(
        "$BACKEND_URL/api/v1/auth/health"
        "$BACKEND_URL/api/v1/tasks/health" 
        "$BACKEND_URL/api/v1/organizations/health"
        "$BACKEND_URL/api/v1/template/health"
    )
    
    local working=0
    local total=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        local name=$(echo $endpoint | sed 's/.*\/api\/v1\///' | sed 's/\/health//')
        if check_http_status "$endpoint" "$name API" "200"; then
            ((working++))
        fi
    done
    
    echo ""
    echo "📊 API Health Summary: $working/$total endpoints healthy"
    echo "$(date): API Summary - $working/$total endpoints healthy" >> $LOG_FILE
}

# Function to check performance metrics
check_performance() {
    echo "⚡ Performance Metrics:"
    echo "----------------------"
    
    # Test frontend load time
    echo -n "🌐 Frontend load time... "
    frontend_time=$(curl -s -o /dev/null -w "%{time_total}" "$FRONTEND_URL" --max-time 15)
    if (( $(echo "$frontend_time < 5.0" | bc -l) )); then
        echo -e "${GREEN}✅ ${frontend_time}s${NC} (Good)"
    else
        echo -e "${YELLOW}⚠️  ${frontend_time}s${NC} (Slow)"
    fi
    
    # Test API response time
    echo -n "🔌 API response time... "
    api_time=$(curl -s -o /dev/null -w "%{time_total}" "$HEALTH_ENDPOINT" --max-time 10)
    if (( $(echo "$api_time < 1.0" | bc -l) )); then
        echo -e "${GREEN}✅ ${api_time}s${NC} (Fast)"
    else
        echo -e "${YELLOW}⚠️  ${api_time}s${NC} (Acceptable)"
    fi
    
    echo "$(date): Performance - Frontend: ${frontend_time}s, API: ${api_time}s" >> $LOG_FILE
}

# Function to generate summary report
generate_summary() {
    echo ""
    echo "📋 PRODUCTION MONITORING SUMMARY"
    echo "================================="
    echo "🕒 Check completed at: $(date)"
    echo ""
    
    # Count recent successes and failures
    local recent_logs=$(tail -20 $LOG_FILE | grep "$(date +%Y-%m-%d)")
    local successes=$(echo "$recent_logs" | grep -c "UP\|HEALTHY\|CONNECTED")
    local failures=$(echo "$recent_logs" | grep -c "DOWN\|UNHEALTHY\|ISSUE")
    
    if [ $failures -eq 0 ]; then
        echo -e "🟢 ${GREEN}SYSTEM STATUS: ALL HEALTHY${NC}"
        echo "✅ All systems operational"
        echo "✅ No issues detected"
    elif [ $failures -lt 3 ]; then
        echo -e "🟡 ${YELLOW}SYSTEM STATUS: MOSTLY HEALTHY${NC}"
        echo "⚠️  Minor issues detected ($failures)"
        echo "✅ Core systems operational"
    else
        echo -e "🔴 ${RED}SYSTEM STATUS: ISSUES DETECTED${NC}"
        echo "❌ Multiple issues detected ($failures)"
        echo "🚨 Requires immediate attention"
    fi
    
    echo ""
    echo "📊 Today's Health Score: $(( successes * 100 / (successes + failures) ))%"
    echo ""
    echo "🔗 Production URLs:"
    echo "   • Frontend: $FRONTEND_URL"
    echo "   • Backend:  $BACKEND_URL"
    echo "   • Health:   $HEALTH_ENDPOINT"
    echo ""
    echo "📝 Full logs: $LOG_FILE"
    echo "🔄 Next check: Run this script again or set up cron job"
}

# Main execution
main() {
    echo "🚀 Starting comprehensive health check..."
    echo ""
    
    # Initialize log entry
    echo "$(date): === PRODUCTION HEALTH CHECK STARTED ===" >> $LOG_FILE
    
    # Core system checks
    echo "🏗️  Core System Health:"
    echo "----------------------"
    check_http_status "$FRONTEND_URL" "Frontend" "200"
    check_http_status "$BACKEND_URL" "Backend API" "200"
    check_http_status "$HEALTH_ENDPOINT" "Health Endpoint" "200"
    echo ""
    
    # Database check
    check_database
    echo ""
    
    # API endpoints check
    check_critical_apis
    echo ""
    
    # Performance check
    check_performance
    echo ""
    
    # Generate summary
    generate_summary
    
    # Close log entry
    echo "$(date): === PRODUCTION HEALTH CHECK COMPLETED ===" >> $LOG_FILE
    echo ""
}

# Create log file if it doesn't exist
touch $LOG_FILE

# Run main function
main

echo ""
echo "🎯 TeamFlow Production Monitoring Complete!"
echo "   📊 View detailed logs: cat $LOG_FILE"
echo "   🔄 Run again: ./scripts/production-monitor.sh"
echo "   ⏰ Set up automated monitoring: */15 * * * * /path/to/this/script"
echo ""
echo "🚀 TeamFlow is ready for enterprise customers!"