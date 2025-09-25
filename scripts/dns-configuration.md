# DNS Configuration Template for TeamFlow

## Domain: teamflow.app

### A Records
```
Type: A
Name: @
Value: [Auto-configured by Vercel - Vercel will provide IP]
TTL: 300 (5 minutes)
```

### CNAME Records
```
# API Subdomain
Type: CNAME
Name: api
Value: teamflow-api-production.up.railway.app
TTL: 300

# WWW Redirect
Type: CNAME
Name: www
Value: teamflow.vercel.app
TTL: 300
```

### TXT Records (Optional - for verification)
```
# Domain verification
Type: TXT
Name: @
Value: [Vercel verification token]
TTL: 300

# SPF Record (if email needed)
Type: TXT
Name: @
Value: "v=spf1 include:_spf.google.com ~all"
TTL: 300
```

## Cloudflare DNS Configuration (Recommended)

### DNS Records
```json
[
  {
    "type": "A",
    "name": "teamflow.app",
    "content": "[Vercel IP - auto-configured]",
    "ttl": 300,
    "proxied": true
  },
  {
    "type": "CNAME",
    "name": "api",
    "content": "teamflow-api-production.up.railway.app",
    "ttl": 300,
    "proxied": false
  },
  {
    "type": "CNAME",
    "name": "www",
    "content": "teamflow.vercel.app",
    "ttl": 300,
    "proxied": true
  }
]
```

### Page Rules (Cloudflare)
```
# HTTPS Redirect
URL: http://teamflow.app/*
Setting: Always Use HTTPS

# WWW Redirect
URL: www.teamflow.app/*
Setting: Forwarding URL (301 - Permanent Redirect)
Destination: https://teamflow.app/$1
```

## Environment Variable Updates

### Frontend (.env.production)
```env
VITE_API_BASE_URL=https://api.teamflow.app
VITE_APP_URL=https://teamflow.app
VITE_ENVIRONMENT=production
```

### Backend (.env.production)
```env
FRONTEND_URL=https://teamflow.app
ALLOWED_ORIGINS=https://teamflow.app,https://www.teamflow.app
CORS_ORIGINS=["https://teamflow.app", "https://www.teamflow.app"]
```

## SSL Certificate Configuration

### Vercel SSL (Automatic)
- Let's Encrypt certificates
- Automatic renewal
- Wildcard support for subdomains
- Edge termination

### Railway SSL (Automatic)
- Let's Encrypt certificates
- Automatic renewal
- Custom domain SSL support

## Security Headers Configuration

### Vercel (vercel.json)
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains; preload"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
        }
      ]
    }
  ]
}
```

## Verification Commands

### DNS Propagation Check
```bash
# Check A record
dig teamflow.app

# Check CNAME records  
dig api.teamflow.app
dig www.teamflow.app

# Check from multiple locations
nslookup teamflow.app 8.8.8.8
nslookup teamflow.app 1.1.1.1
```

### SSL Certificate Check
```bash
# Check SSL certificate
openssl s_client -connect teamflow.app:443 -servername teamflow.app

# Check certificate expiry
echo | openssl s_client -servername teamflow.app -connect teamflow.app:443 2>/dev/null | openssl x509 -noout -dates
```

### HTTP Security Check
```bash
# Check security headers
curl -I https://teamflow.app

# Check HTTPS redirect
curl -I http://teamflow.app
```

## Monitoring Setup

### DNS Monitoring
- Monitor DNS propagation status
- Alert on DNS record changes
- Track DNS resolution performance

### SSL Monitoring  
- Monitor certificate expiry (30 days warning)
- Alert on certificate validation failures
- Track SSL handshake performance

### Domain Health Checks
- Monitor domain accessibility
- Check HTTPS redirect functionality
- Validate security header presence