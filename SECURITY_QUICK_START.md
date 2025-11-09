# Security Hardening - Quick Start Guide

## Phase 2 Implementation Summary

Phase 2 Security Hardening is **COMPLETE** and adds critical security improvements to ConsultantOS.

---

## What Changed?

### ✅ Security Improvements
1. **Secure Session Management** - CSRF protection, HTTPOnly cookies, session timeouts
2. **Security Headers** - Protection against XSS, clickjacking, MIME confusion
3. **GZip Compression** - 30-70% bandwidth reduction
4. **Database Safety** - Verified Firestore uses parameterized queries (no SQL injection risk)

### ⚠️ Breaking Changes
- **Production requires `SESSION_SECRET`** environment variable
- **HTTPS-only cookies** in production (requires HTTPS deployment)

---

## Quick Setup

### 1. Set Session Secret

**Development** (auto-generated, no action needed):
```bash
# Session secret auto-generated on startup
python main.py
```

**Production** (required):
```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variable
export SESSION_SECRET="your-generated-secret-here"

# Or add to .env file
echo "SESSION_SECRET=your-generated-secret-here" >> .env
```

### 2. Install Dependencies

```bash
# Install new security dependencies
pip install -r requirements.txt
```

**New Dependencies**:
- `starlette>=0.27.0` - Session middleware
- `itsdangerous>=2.1.0` - Secure session signing

### 3. Test Security

```bash
# Start server
python main.py

# Run security tests in another terminal
python test_security_headers.py

# Or test manually
curl -I http://localhost:8080/health
```

---

## Security Features

### Session Security
- ✅ **1-hour session timeout** - Prevents session hijacking
- ✅ **CSRF protection** - `SameSite=strict` cookies
- ✅ **HTTPOnly cookies** - Prevents JavaScript access
- ✅ **HTTPS-only in production** - Enforces secure transmission

### HTTP Security Headers
- ✅ **X-Content-Type-Options: nosniff** - Prevents MIME confusion
- ✅ **X-Frame-Options: DENY** - Prevents clickjacking
- ✅ **X-XSS-Protection** - Browser XSS filter
- ✅ **Content-Security-Policy** - Controls resource loading
- ✅ **Referrer-Policy** - Protects privacy
- ✅ **Permissions-Policy** - Disables unnecessary features
- ✅ **HSTS (production)** - Forces HTTPS for 1 year

### Performance
- ✅ **GZip compression** - Reduces bandwidth 30-70%
- ✅ **Smart compression** - Only for responses >1KB
- ✅ **Optimized compression level** - Balanced speed vs ratio

---

## Testing Security

### Automated Test
```bash
# Run comprehensive security test
python test_security_headers.py

# Test against different endpoint
python test_security_headers.py http://localhost:8080
```

### Manual Verification

**Check Security Headers**:
```bash
curl -I http://localhost:8080/health | grep -E "X-|Content-Security|Referrer|Permissions"
```

**Check GZip Compression**:
```bash
curl -H "Accept-Encoding: gzip" -I http://localhost:8080/reports | grep "Content-Encoding"
```

**Check Session Cookie**:
```bash
curl -v http://localhost:8080/reports 2>&1 | grep -i "set-cookie"
```

---

## Production Deployment

### Environment Setup
```bash
# Required
export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export environment=production

# Recommended
export GEMINI_API_KEY="your-api-key"
export TAVILY_API_KEY="your-api-key"
```

### Google Cloud Run
```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "environment=production,SESSION_SECRET=$SESSION_SECRET"
```

### Google Secret Manager
```bash
# Store session secret securely
gcloud secrets create session-secret --data-file=- <<< "$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# App will auto-load from Secret Manager in production
```

---

## Common Issues

### Issue: Session secret warning on startup

**Symptom**:
```
WARNING: SESSION_SECRET not configured. Generated temporary session secret for development.
```

**Solution**:
- **Development**: Ignore - auto-generated secret is fine
- **Production**: Set `SESSION_SECRET` environment variable

---

### Issue: CSP blocking resources

**Symptom**: Frontend resources not loading, browser console shows CSP violations

**Solution**: Update CSP directives in `consultantos/api/main.py`:
```python
csp_directives = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.example.com",  # Add trusted CDN
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",  # Add trusted sources
    # ... adjust as needed
]
```

---

### Issue: Cookies not working in production

**Symptom**: Sessions not persisting, users logged out frequently

**Checklist**:
- ✅ HTTPS enabled? (required for `https_only=True` in production)
- ✅ `environment=production` set correctly?
- ✅ Load balancer terminates SSL/TLS?
- ✅ `SameSite=strict` compatible with your domain setup?

**Quick Fix**: Temporarily set `https_only=False` for testing (not recommended for production)

---

## Security Checklist

### Pre-Deployment
- [ ] Set `SESSION_SECRET` environment variable
- [ ] Verify `environment=production`
- [ ] Configure HTTPS on load balancer
- [ ] Review CSP directives for frontend
- [ ] Test authentication flows
- [ ] Run security scanner

### Post-Deployment
- [ ] Verify all security headers present: `curl -I https://your-app.com/health`
- [ ] Test HTTPS-only cookies working
- [ ] Monitor session storage usage
- [ ] Review logs for security warnings
- [ ] Schedule regular security audits

---

## Security Monitoring

### Key Metrics to Track
```bash
# Session usage
# Monitor active sessions in database/cache

# Security header compliance
# Use automated scanners weekly

# Compression effectiveness
# Track response sizes and bandwidth savings

# Failed authentication attempts
# Monitor for brute force attacks
```

### Recommended Tools
- [Mozilla Observatory](https://observatory.mozilla.org/) - Security header scanner
- [Security Headers](https://securityheaders.com/) - Header compliance checker
- [OWASP ZAP](https://www.zaproxy.org/) - Comprehensive security testing

---

## Next Steps

### Additional Security Enhancements (Future)
1. **CSRF Tokens** - Explicit tokens for state-changing operations
2. **Rate Limiting by User** - Per-user limits beyond IP-based
3. **Security Audit Logging** - Comprehensive security event logging
4. **Automated Security Testing** - SAST/DAST in CI/CD
5. **Web Application Firewall** - Advanced threat protection

### Maintenance
- **Weekly**: Review security logs
- **Monthly**: Update dependencies
- **Quarterly**: Security audit
- **Annually**: Rotate session secrets

---

## Support

### Documentation
- Full details: [SECURITY_HARDENING_PHASE2.md](SECURITY_HARDENING_PHASE2.md)
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- OWASP Headers: https://owasp.org/www-project-secure-headers/

### Testing
- Test script: `python test_security_headers.py`
- Health check: `curl http://localhost:8080/health`
- API docs: `http://localhost:8080/docs`

---

## Summary

✅ **Phase 2 Complete** - All security improvements implemented
✅ **No Breaking Changes** - Except production `SESSION_SECRET` requirement
✅ **Production Ready** - With proper environment configuration
✅ **Testing Available** - Automated security header verification

**Production Checklist**: Set `SESSION_SECRET`, enable HTTPS, verify headers ✓
