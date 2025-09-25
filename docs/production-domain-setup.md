# TeamFlow Production Domain Setup

## Domain Configuration
**Primary Domain:** `teamflow.app` (recommended)
**Cost:** ~$12/year

## DNS Configuration

### Required DNS Records

#### A Records
```
@ → [Auto-configured by Vercel]
```

#### CNAME Records
```
api → teamflow-api-production.up.railway.app
www → teamflow.vercel.app
```

## SSL/TLS Configuration

### Automatic SSL Features
- ✅ Let's Encrypt certificates (FREE)
- ✅ Automatic certificate renewal
- ✅ TLS 1.3 support
- ✅ HTTP → HTTPS redirect
- ✅ HSTS headers
- ✅ Perfect Forward Secrecy

### Security Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

## Domain Setup Steps

### 1. Domain Purchase
1. Purchase `teamflow.app` from registrar (Google Domains, Namecheap, etc.)
2. Point nameservers to Vercel or Cloudflare

### 2. Vercel Configuration
```bash
# Add domain in Vercel dashboard
vercel domains add teamflow.app
vercel domains add www.teamflow.app
```

### 3. Railway Configuration
```bash
# Add custom domain for API
railway domain add api.teamflow.app
```

### 4. Environment Variables Update
```env
# Frontend (.env.production)
VITE_API_BASE_URL=https://api.teamflow.app
VITE_APP_URL=https://teamflow.app

# Backend
FRONTEND_URL=https://teamflow.app
ALLOWED_ORIGINS=https://teamflow.app,https://www.teamflow.app
```

## CDN Configuration

### Vercel Edge Network
- ✅ Global CDN (50+ locations)
- ✅ Brotli compression
- ✅ Image optimization
- ✅ Static asset caching

### Performance Optimizations
- Cache-Control headers optimized
- Gzip/Brotli compression enabled
- HTTP/2 and HTTP/3 support
- Edge Side Includes (ESI)

## Cost Summary
- Domain Registration: $12/year
- SSL Certificate: FREE
- CDN: FREE
- DNS Management: FREE
- **Total Annual Cost: $12**

## Monitoring Setup
- SSL certificate expiry monitoring
- Domain DNS propagation checks
- HTTPS redirect validation
- Security header verification

## Go-Live Checklist
- [ ] Domain purchased and configured
- [ ] DNS records propagated (24-48 hours)
- [ ] SSL certificates active
- [ ] HTTPS redirects working
- [ ] API subdomain accessible
- [ ] WWW redirect functional
- [ ] Security headers validated
- [ ] CDN performance verified