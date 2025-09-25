# TeamFlow Production Monitoring Setup

## Monitoring Stack Overview

### Free Tier Monitoring Services
- **Uptime Monitoring**: UptimeRobot (FREE - 50 monitors, 5-minute intervals)
- **Error Tracking**: Sentry (FREE - 5,000 errors/month)
- **Performance**: Vercel Analytics (FREE - Web Vitals, page views)
- **Logs**: Railway Logs (FREE tier - structured logging)
- **Database**: Railway PostgreSQL Metrics (FREE - connection pooling, query stats)

### Total Monthly Cost: $0 (All FREE tiers)

## 1. Uptime Monitoring (UptimeRobot)

### Monitors to Configure

#### Frontend Monitoring
```
Monitor Type: HTTPS
URL: https://teamflow.app
Name: TeamFlow Frontend
Interval: 5 minutes
Timeout: 30 seconds
Alert Contacts: [Your email/SMS/Slack]
```

#### Backend API Monitoring
```
Monitor Type: HTTPS  
URL: https://api.teamflow.app/health
Name: TeamFlow API Health
Interval: 5 minutes
Timeout: 30 seconds
Alert Contacts: [Your email/SMS/Slack]

Monitor Type: HTTPS
URL: https://api.teamflow.app/api/v1/auth/health
Name: TeamFlow Auth Service
Interval: 10 minutes
Timeout: 30 seconds
```

#### Database Monitoring
```
Monitor Type: Port
Host: [Railway PostgreSQL host]
Port: 5432
Name: TeamFlow Database
Interval: 10 minutes
```

#### SSL Certificate Monitoring
```
Monitor Type: HTTPS
URL: https://teamflow.app
Name: SSL Certificate teamflow.app
SSL Expiry Alert: 30 days before
```

## 2. Error Tracking (Sentry)

### Frontend Sentry Configuration

#### Install Sentry SDK
```bash
cd frontend
npm install --save @sentry/react @sentry/tracing
```

#### Sentry Configuration (`src/sentry.ts`)
```typescript
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

if (process.env.NODE_ENV === 'production') {
  Sentry.init({
    dsn: process.env.VITE_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    integrations: [
      new BrowserTracing({
        tracePropagationTargets: [
          "https://teamflow.app",
          "https://api.teamflow.app"
        ],
      }),
    ],
    tracesSampleRate: 0.1,
    beforeSend(event, hint) {
      // Filter out non-critical errors
      if (event.level === 'info') return null;
      return event;
    },
  });
}
```

### Backend Sentry Configuration

#### Install Sentry SDK
```bash
cd backend
pip install sentry-sdk[fastapi]
```

#### Sentry Configuration (`app/core/monitoring.py`)
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("ENVIRONMENT", "production"),
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        before_send=filter_errors,
    )

def filter_errors(event, hint):
    # Filter out health check 404s
    if event.get('request', {}).get('url', '').endswith('/health'):
        return None
    return event
```

## 3. Performance Monitoring

### Vercel Analytics (FREE)
- Automatic Web Vitals tracking
- Page view analytics
- Performance insights
- Core metrics: LCP, FID, CLS, FCP, TTFB

### Custom Performance Tracking

#### Frontend Performance Monitoring
```typescript
// src/utils/performance.ts
export class PerformanceMonitor {
  static trackPageLoad(pageName: string) {
    if (typeof window !== 'undefined' && 'performance' in window) {
      const loadTime = window.performance.timing.loadEventEnd - 
                      window.performance.timing.navigationStart;
      
      // Send to analytics
      if (loadTime > 3000) {
        console.warn(`Slow page load: ${pageName} - ${loadTime}ms`);
      }
    }
  }

  static trackAPICall(endpoint: string, duration: number) {
    if (duration > 2000) {
      console.warn(`Slow API call: ${endpoint} - ${duration}ms`);
    }
  }
}
```

#### Backend Performance Monitoring
```python
# app/middleware/performance.py
import time
from fastapi import Request

async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log slow requests
    if process_time > 2.0:
        logger.warning(f"Slow request: {request.url.path} - {process_time:.2f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 4. Health Checks

### Backend Health Check Endpoint
```python
# app/api/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check endpoint"""
    try:
        # Database connectivity check
        await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "healthy",
                "api": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@router.get("/api/v1/auth/health")
async def auth_health():
    """Auth service specific health check"""
    return {"status": "healthy", "service": "auth"}
```

## 5. Logging Configuration

### Backend Logging (Structured Logs)
```python
# app/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

def setup_logging():
    logger = logging.getLogger("teamflow")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger
```

## 6. Alerting Configuration

### Alert Channels
- **Email**: Primary notification method
- **Slack**: Real-time team notifications (webhook)
- **SMS**: Critical alerts only (PagerDuty free tier)

### Alert Rules

#### Critical Alerts (Immediate Response)
- Frontend down > 2 minutes
- API down > 2 minutes
- Database connection failures
- SSL certificate expiry < 7 days

#### Warning Alerts (Within 1 hour)
- High error rate (>5% of requests)
- Slow response times (>5 seconds)
- Memory usage > 80%
- Disk space < 20%

#### Info Alerts (Daily Summary)
- Daily performance summary
- Error rate trends
- User activity summary

## 7. Dashboard Setup

### UptimeRobot Public Status Page
```
URL: https://stats.uptimerobot.com/[your-key]
Custom Domain: status.teamflow.app (optional)
```

### Grafana Dashboard (Optional - FREE tier)
- System metrics visualization
- Custom dashboards for business metrics
- Alert rule management

## 8. Monitoring Checklist

### Pre-Go-Live Setup
- [ ] UptimeRobot monitors configured
- [ ] Sentry projects created (frontend + backend)
- [ ] Health check endpoints implemented
- [ ] Performance tracking added
- [ ] Logging configuration deployed
- [ ] Alert channels configured
- [ ] Status page published

### Post-Go-Live Validation
- [ ] All monitors reporting healthy
- [ ] Error tracking capturing issues
- [ ] Performance metrics collecting
- [ ] Alerts triggering correctly
- [ ] Logs flowing properly
- [ ] Dashboard accessible

## 9. Incident Response Plan

### Severity Levels
1. **Critical**: Service completely down
2. **High**: Major feature broken
3. **Medium**: Minor feature issue
4. **Low**: Cosmetic or minor bug

### Response Times
- Critical: 15 minutes
- High: 1 hour
- Medium: 4 hours
- Low: Next business day

### Escalation Path
1. Email/Slack notification
2. SMS alert (if critical)
3. Manual intervention required

This monitoring setup provides comprehensive visibility into system health while maintaining zero monthly costs through strategic use of free tiers.