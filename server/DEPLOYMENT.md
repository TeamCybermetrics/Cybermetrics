# Deployment Guide

## Environment Variables

### Required

- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase service account key JSON file
- `FIREBASE_WEB_API_KEY` - Firebase Web API key for password verification

### Optional

- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8000`)
- `ENVIRONMENT` - Environment mode: `development`, `staging`, or `production` (default: `development`)
- `TRUST_PROXY` - Enable proxy header trust (default: `false`)

## Proxy Configuration

### TRUST_PROXY Setting

The `TRUST_PROXY` environment variable controls whether the application trusts `X-Forwarded-For` and `X-Real-IP` headers for client IP detection.

**Default: `false` (DISABLED)**

#### When to Enable

✅ **Enable (`TRUST_PROXY=true`)** when:
- Running behind a **trusted reverse proxy** (nginx, Apache, Cloudflare, AWS ALB, etc.)
- The reverse proxy **strips client-supplied forward headers**
- You need accurate client IP logging and rate limiting

❌ **Keep Disabled (`TRUST_PROXY=false`)** when:
- Running directly exposed to the internet
- Not behind a reverse proxy
- Unsure about proxy configuration

#### Security Warning

⚠️ **CRITICAL**: Only enable `TRUST_PROXY` when behind a trusted reverse proxy that strips client-supplied headers.

If enabled without a proper proxy, attackers can spoof their IP address by sending fake `X-Forwarded-For` headers, bypassing rate limiting and security controls.

### Example Configurations

#### Development (No Proxy)
```bash
# .env
TRUST_PROXY=false
```

#### Production (Behind nginx)
```bash
# .env
TRUST_PROXY=true
ENVIRONMENT=production
```

#### nginx Configuration Example
```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        
        # Strip any client-supplied forward headers
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
    }
}
```

## Rate Limiting

The application includes built-in rate limiting for authentication endpoints:

- **Signup**: 5 failed attempts per IP within 15 minutes
- **Login**: 5 failed attempts per IP **and** per email within 15 minutes

### In-Memory Storage

⚠️ **Note**: Rate limiting uses in-memory storage. For production with multiple instances, consider:
- Using Redis for shared rate limit state
- Implementing sticky sessions
- Using a dedicated rate limiting service

### Cleanup Task

The rate limiter automatically runs a background cleanup task every 5 minutes to prune expired entries. This task:
- Starts automatically on application startup
- Stops gracefully on shutdown
- Prevents memory leaks from stale data

## Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `FIREBASE_WEB_API_KEY`
- [ ] Enable HTTPS/TLS
- [ ] Configure reverse proxy (nginx, Cloudflare, etc.)
- [ ] Set `TRUST_PROXY=true` if behind reverse proxy
- [ ] Verify proxy strips client-supplied forward headers
- [ ] Set up monitoring and logging
- [ ] Consider Redis for rate limiting in multi-instance deployments
- [ ] Configure CORS origins appropriately
- [ ] Set up database backups (Firestore)

## Testing Proxy Configuration

To verify proxy configuration is working correctly:

1. **Check startup logs** for proxy trust mode:
   ```
   🔒 Proxy trust mode: ENABLED
   ```

2. **Test IP detection** by checking rate limit logs or making requests

3. **Verify headers** are being set correctly by your reverse proxy

4. **Test rate limiting** works as expected with real client IPs
