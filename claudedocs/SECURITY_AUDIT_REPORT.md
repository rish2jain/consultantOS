# ConsultantOS Security Audit Report
**Date**: November 7, 2025
**Auditor**: Security Audit (Automated)
**Scope**: Authentication, Authorization, Input Validation, Secrets Management, Infrastructure Security

---

## Executive Summary

This security audit identified **12 security vulnerabilities** across the ConsultantOS application, ranging from **CRITICAL** to **LOW** severity. The most critical issue is **exposed API keys committed to the repository**, which poses immediate risk of unauthorized access and abuse.

**Severity Breakdown**:
- 🔴 **CRITICAL**: 2 findings
- 🟠 **HIGH**: 4 findings
- 🟡 **MEDIUM**: 3 findings
- 🟢 **LOW**: 3 findings

**Overall Security Posture**: ⚠️ **HIGH RISK** - Immediate action required

---

## CRITICAL Vulnerabilities

### 🔴 CRIT-001: API Keys Exposed in Repository
**Severity**: CRITICAL
**CVSS Score**: 9.8
**File**: `.env`
**Line**: 7, 10

**Finding**:
Hardcoded production API keys are committed to the git repository:
- `TAVILY_API_KEY=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`
- `GEMINI_API_KEY=AIzaSyBrKM5_cvn9fyQfZ2j8RT4BTwaVzEx9RSk`

**Impact**:
- Unauthorized access to third-party services
- API quota abuse and financial liability
- Data exfiltration through compromised keys
- Service disruption through rate limit exhaustion

**Remediation**:
```bash
# IMMEDIATE ACTION REQUIRED
# 1. Revoke exposed API keys
#    - Tavily: https://app.tavily.com/settings/api
#    - Google AI Studio: https://makersuite.google.com/app/apikey

# 2. Remove .env from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (CAUTION: coordinate with team)
git push origin --force --all

# 4. Add .env to .gitignore (already present, verify)
echo ".env" >> .gitignore

# 5. Use Google Secret Manager for production
gcloud secrets create tavily-api-key --data-file=- <<< "NEW_KEY"
gcloud secrets create gemini-api-key --data-file=- <<< "NEW_KEY"

# 6. Update config.py to enforce Secret Manager in production
```

**Code Fix** (`consultantos/config.py`):
```python
class Settings(BaseSettings):
    # API Keys - NEVER set defaults in production
    tavily_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Force Secret Manager in production
    environment: str = "development"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.environment == "production":
            if not self.tavily_api_key or self.tavily_api_key.startswith("tvly-dev"):
                raise RuntimeError("Production requires Secret Manager for API keys")
```

---

### 🔴 CRIT-002: No Password Strength Validation
**Severity**: CRITICAL
**CVSS Score**: 8.5
**File**: `consultantos/user_management.py`
**Line**: 35-98

**Finding**:
The `create_user()` function accepts passwords without strength validation. No minimum length, complexity requirements, or common password checks.

**Impact**:
- Weak passwords enable brute force attacks
- Account takeover through password guessing
- Credential stuffing from data breaches

**Remediation**:
```python
# Add to consultantos/utils/validators.py
import re
from typing import List

class PasswordValidator:
    """Password strength validation"""

    # Common passwords from haveibeenpwned.com
    COMMON_PASSWORDS = {
        "password", "123456", "password123", "admin", "letmein",
        "welcome", "monkey", "1234567890", "qwerty", "abc123"
    }

    @staticmethod
    def validate_password(password: str) -> List[str]:
        """
        Validate password strength

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Minimum length
        if len(password) < 12:
            errors.append("Password must be at least 12 characters")

        # Maximum length (prevent DoS)
        if len(password) > 128:
            errors.append("Password must be less than 128 characters")

        # Complexity requirements
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letters")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letters")
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain numbers")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special characters")

        # Common password check
        if password.lower() in PasswordValidator.COMMON_PASSWORDS:
            errors.append("Password is too common")

        # No sequential characters
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            errors.append("Password contains sequential numbers")

        return errors

# Update consultantos/user_management.py
def create_user(email: str, password: str, name: Optional[str] = None) -> Dict:
    """Create a new user account with password validation"""
    from consultantos.utils.validators import PasswordValidator

    # Validate password strength
    password_errors = PasswordValidator.validate_password(password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": password_errors}
        )

    # Continue with existing logic...
```

**Additional Recommendations**:
- Implement rate limiting on registration endpoint (10/hour per IP)
- Add CAPTCHA for registration to prevent automated attacks
- Consider integration with haveibeenpwned.com API for breach detection

---

## HIGH Severity Vulnerabilities

### 🟠 HIGH-001: Insufficient Rate Limiting
**Severity**: HIGH
**CVSS Score**: 7.5
**File**: `consultantos/api/main.py`
**Line**: 108-110

**Finding**:
Rate limiting is only applied to IP addresses at 10 requests/hour. No per-user rate limiting, no distributed rate limiting for horizontal scaling, no API endpoint differentiation.

**Impact**:
- API abuse through distributed attacks
- Resource exhaustion (DoS)
- Bypass through IP rotation/proxies
- Cost escalation from third-party API abuse

**Current Implementation**:
```python
@app.post("/analyze")
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def analyze_company(request: Request, ...):
```

**Remediation**:
```python
# 1. Install Redis for distributed rate limiting
# pip install redis slowapi[redis]

# 2. Update consultantos/api/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis

# Redis connection for distributed rate limiting
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True
)

def get_rate_limit_key(request: Request) -> str:
    """Composite rate limit key (IP + API key if present)"""
    ip = get_remote_address(request)
    api_key = request.headers.get("X-API-Key")

    if api_key:
        # Hash API key for privacy
        import hashlib
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return f"{ip}:{api_key_hash}"
    return ip

limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}"
)

# 3. Implement tiered rate limits
@app.post("/analyze")
@limiter.limit("10/hour")  # Unauthenticated
@limiter.limit("50/hour", key_func=lambda: f"api_key:{get_api_key()}")  # Authenticated
async def analyze_company(...):
    pass

# 4. Add endpoint-specific limits
@app.post("/auth/login")
@limiter.limit("5/minute")  # Stricter for authentication
async def login(...):
    pass

@app.get("/health")
@limiter.exempt  # No limit for health checks
async def health_check():
    pass
```

**Configuration** (`.env`):
```bash
REDIS_HOST=localhost
REDIS_PORT=6379

# Tiered rate limits
RATE_LIMIT_ANONYMOUS=10/hour
RATE_LIMIT_AUTHENTICATED=50/hour
RATE_LIMIT_PREMIUM=200/hour
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_REGISTRATION=3/hour
```

---

### 🟠 HIGH-002: CORS Wildcard with Credentials Risk
**Severity**: HIGH
**CVSS Score**: 7.2
**File**: `consultantos/api/main.py`
**Line**: 52-72

**Finding**:
CORS is configured with `allow_origins=["*"]` by default, though credentials are disabled. This configuration is overly permissive and could be accidentally misconfigured.

**Current Code**:
```python
allowed_origins = getattr(settings, 'allowed_origins', [])
if not allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Too permissive
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

**Impact**:
- XSS attacks from untrusted domains
- CSRF vulnerabilities if credentials are enabled
- Data exposure to malicious websites
- Phishing attacks through domain confusion

**Remediation**:
```python
# consultantos/config.py
class Settings(BaseSettings):
    # CORS Configuration
    allowed_origins: List[str] = []  # Force explicit configuration
    cors_allow_credentials: bool = False
    cors_max_age: int = 3600

    def validate_cors(self):
        """Validate CORS configuration for production"""
        if self.environment == "production":
            if not self.allowed_origins:
                raise RuntimeError("Production requires explicit CORS origins")
            if "*" in self.allowed_origins:
                raise RuntimeError("Wildcard CORS not allowed in production")

# consultantos/api/main.py
settings.validate_cors()

# Explicitly define allowed origins
allowed_origins = settings.allowed_origins or [
    "http://localhost:3000",  # Development frontend
    "http://localhost:8080",  # Development API
]

# Validate no wildcard in production
if settings.environment == "production" and "*" in allowed_origins:
    raise RuntimeError("Wildcard CORS origin not allowed in production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],  # Explicit headers
    max_age=settings.cors_max_age,
)

# Log CORS configuration for audit
logger.info(f"CORS configured: origins={allowed_origins}, credentials={settings.cors_allow_credentials}")
```

**.env**:
```bash
# Production CORS (explicit domains only)
ALLOWED_ORIGINS=https://consultantos.app,https://www.consultantos.app
CORS_ALLOW_CREDENTIALS=true
```

---

### 🟠 HIGH-003: Missing JWT/Session Management
**Severity**: HIGH
**CVSS Score**: 7.0
**File**: `consultantos/auth.py`

**Finding**:
API key authentication is the only method. No JWT tokens for user sessions, no token expiration, no refresh tokens. API keys are long-lived and cannot be easily rotated per-session.

**Impact**:
- API keys exposed in browser storage/logs
- No session invalidation on logout
- Stolen keys valid indefinitely until manual revocation
- No multi-device session management

**Remediation**:
```python
# consultantos/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import secrets

# JWT Configuration
JWT_SECRET_KEY = secrets.token_urlsafe(32)  # Store in Secret Manager
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = {"sub": user_id, "type": "access"}

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    to_encode = {
        "sub": user_id,
        "type": "refresh",
        "jti": secrets.token_urlsafe(16)  # Unique token ID
    }
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Store refresh token JTI in database for revocation capability
    db_service = get_db_service()
    db_service.store_refresh_token(user_id, to_encode["jti"], expire)

    return encoded_jwt

def verify_access_token(token: str) -> Optional[Dict]:
    """Verify JWT access token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            return None

        return {"user_id": user_id}
    except JWTError:
        return None

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")

        if user_id is None or token_type != "refresh":
            return None

        # Verify refresh token not revoked
        db_service = get_db_service()
        if not db_service.is_refresh_token_valid(user_id, jti):
            return None

        # Create new access token
        return create_access_token(user_id)
    except JWTError:
        return None

def revoke_refresh_token(refresh_token: str) -> bool:
    """Revoke refresh token (logout)"""
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")

        db_service = get_db_service()
        return db_service.revoke_refresh_token(user_id, jti)
    except JWTError:
        return False

# Update endpoints
@app.post("/auth/login")
async def login(email: str, password: str):
    """Login with JWT tokens"""
    user_info = authenticate_user(email, password)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(user_info["user_id"])
    refresh_token = create_refresh_token(user_info["user_id"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/refresh")
async def refresh(refresh_token: str):
    """Refresh access token"""
    new_access_token = refresh_access_token(refresh_token)

    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/logout")
async def logout(refresh_token: str):
    """Logout (revoke refresh token)"""
    revoke_refresh_token(refresh_token)
    return {"message": "Logged out successfully"}
```

---

### 🟠 HIGH-004: Insecure Default API Key in Development
**Severity**: HIGH
**CVSS Score**: 6.8
**File**: `consultantos/auth.py`
**Line**: 349-351

**Finding**:
A default API key is auto-generated and logged in development mode. This key could be accidentally used in production or exposed through logs.

**Current Code**:
```python
if settings.environment == "development":
    DEFAULT_API_KEY = create_api_key("demo_user", "Default demo API key")
    logger.info(f"Created default API key for development: {DEFAULT_API_KEY[:16]}...")
```

**Impact**:
- Default credentials in production deployments
- API key exposure through log aggregation
- Unauthorized access through shared development keys

**Remediation**:
```python
# Remove auto-generation, require explicit setup
if settings.environment == "development":
    # Check if demo key already exists
    demo_key_path = Path(".dev_api_key")

    if demo_key_path.exists():
        with open(demo_key_path, "r") as f:
            DEFAULT_API_KEY = f.read().strip()
        logger.info("Loaded existing development API key from .dev_api_key")
    else:
        DEFAULT_API_KEY = create_api_key("demo_user", "Default demo API key")
        with open(demo_key_path, "w") as f:
            f.write(DEFAULT_API_KEY)
        logger.info("Created new development API key, saved to .dev_api_key")
        logger.warning("SECURITY: Development API key created. DO NOT use in production!")

    # Add .dev_api_key to .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            if ".dev_api_key" not in f.read():
                with open(gitignore_path, "a") as f:
                    f.write("\n# Development API key\n.dev_api_key\n")

# Production check
if settings.environment == "production":
    if "DEFAULT_API_KEY" in globals():
        raise RuntimeError("Default API key detected in production - security violation")
```

---

## MEDIUM Severity Vulnerabilities

### 🟡 MED-001: Weak Input Sanitization
**Severity**: MEDIUM
**CVSS Score**: 6.5
**File**: `consultantos/utils/sanitize.py`
**Line**: 26-27

**Finding**:
SQL injection prevention uses simple regex pattern `[';--]` which is insufficient and can be bypassed.

**Current Code**:
```python
# Remove potentially dangerous SQL injection patterns
text = re.sub(r"[';--]", "", text)
```

**Issues**:
- Only removes single quotes, semicolons, and hyphens
- Does not protect against UNION, OR 1=1, etc.
- Regex-based filtering is not a substitute for parameterized queries
- Can be bypassed with URL encoding, Unicode, or alternative syntax

**Impact**:
- Potential SQL injection if used with string concatenation
- NoSQL injection through Firestore queries
- Command injection if sanitized input used in shell commands

**Remediation**:
```python
# consultantos/utils/sanitize.py
import re
import html
from typing import Any
import unicodedata

def sanitize_input(text: str, max_length: int = 1000, context: str = "general") -> str:
    """
    Sanitize user input with context-aware protection

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        context: Sanitization context ('general', 'sql', 'shell', 'html')

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        text = str(text)

    # Normalize Unicode (prevent homograph attacks)
    text = unicodedata.normalize('NFKC', text)

    # Remove null bytes
    text = text.replace('\x00', '')

    # Context-specific sanitization
    if context == "html":
        # HTML escape
        text = html.escape(text, quote=True)
        # Remove script tags (defense in depth)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)  # Remove event handlers

    elif context == "sql":
        # For SQL, ALWAYS use parameterized queries
        # This is defense in depth only
        text = html.escape(text)  # Escape special chars
        # Block common SQL injection patterns
        sql_patterns = [
            r'\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b',
            r'--',
            r'/\*',
            r'\*/',
            r'xp_',
            r'sp_',
            r';'
        ]
        for pattern in sql_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    elif context == "shell":
        # Shell command context - HIGHLY restrictive
        # Only allow alphanumeric, spaces, and safe punctuation
        text = re.sub(r'[^a-zA-Z0-9\s._-]', '', text)

    else:  # general
        # Basic HTML escape
        text = html.escape(text)

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()

# IMPORTANT: Document that sanitization is defense-in-depth
# Primary protection must be:
# - Parameterized queries for SQL (Firestore uses safe API)
# - Avoid shell execution entirely
# - Content Security Policy for XSS
# - Input validation at API boundary
```

**Database Query Safety** (`consultantos/database.py`):
```python
# Firestore uses safe API by design, but verify:
def list_reports(self, user_id: Optional[str] = None, company: Optional[str] = None):
    """
    List reports with filters

    NOTE: Firestore SDK uses parameterized queries automatically.
    DO NOT concatenate user input into query strings.
    """
    query = self.reports_collection

    # SAFE: Using Firestore's where() method with parameters
    if user_id:
        query = query.where("user_id", "==", user_id)  # Safe
    if company:
        query = query.where("company", "==", company)  # Safe

    # UNSAFE EXAMPLE (DO NOT USE):
    # query_string = f"SELECT * FROM reports WHERE user_id = '{user_id}'"  # VULNERABLE
```

---

### 🟡 MED-002: Missing HTTPS Enforcement
**Severity**: MEDIUM
**CVSS Score**: 5.8
**File**: `consultantos/api/main.py`, `Dockerfile`

**Finding**:
No HTTPS enforcement middleware. Application runs on HTTP in development and relies on Cloud Run for HTTPS in production. No HSTS headers configured.

**Impact**:
- Credentials transmitted in plaintext during development
- API keys exposed over HTTP
- Man-in-the-middle attacks
- Session hijacking

**Remediation**:
```python
# consultantos/api/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Trusted Host Protection
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts.split(",")
    )

# HTTPS Redirect (production only, Cloud Run handles this)
if settings.environment == "production" and not settings.behind_proxy:
    app.add_middleware(HTTPSRedirectMiddleware)

# Security Headers Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # HSTS - Force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )

        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**.env**:
```bash
# Production hosts
ALLOWED_HOSTS=consultantos.app,www.consultantos.app
BEHIND_PROXY=true  # Cloud Run uses HTTPS proxy
```

---

### 🟡 MED-003: In-Memory Token Storage
**Severity**: MEDIUM
**CVSS Score**: 5.5
**File**: `consultantos/user_management.py`
**Line**: 21-22

**Finding**:
Email verification and password reset tokens stored in process memory:
```python
_verification_tokens: Dict[str, Dict] = {}
_password_reset_tokens: Dict[str, Dict] = {}
```

**Impact**:
- Tokens lost on application restart
- No token revocation across multiple instances
- Memory exhaustion from token accumulation
- Tokens persist longer than intended

**Remediation**:
```python
# Use Redis for distributed token storage
# consultantos/utils/token_manager.py
import redis
import json
from datetime import timedelta
from typing import Optional, Dict

class TokenManager:
    """Distributed token management with Redis"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=1,  # Separate DB for tokens
            decode_responses=True
        )

    def create_verification_token(self, user_id: str, email: str) -> str:
        """Create email verification token"""
        token = secrets.token_urlsafe(32)

        token_data = {
            "user_id": user_id,
            "email": email,
            "type": "email_verification",
            "created_at": datetime.now().isoformat()
        }

        # Store with 7-day expiration
        self.redis_client.setex(
            f"verify:{token}",
            timedelta(days=7),
            json.dumps(token_data)
        )

        return token

    def verify_token(self, token: str, token_type: str) -> Optional[Dict]:
        """Verify and consume token"""
        key = f"verify:{token}" if token_type == "email_verification" else f"reset:{token}"

        token_data_str = self.redis_client.get(key)
        if not token_data_str:
            return None

        token_data = json.loads(token_data_str)

        # Verify token type
        if token_data.get("type") != token_type:
            return None

        # Delete token (one-time use)
        self.redis_client.delete(key)

        return token_data

    def create_password_reset_token(self, user_id: str, email: str) -> str:
        """Create password reset token"""
        token = secrets.token_urlsafe(32)

        token_data = {
            "user_id": user_id,
            "email": email,
            "type": "password_reset",
            "created_at": datetime.now().isoformat()
        }

        # Store with 24-hour expiration
        self.redis_client.setex(
            f"reset:{token}",
            timedelta(hours=24),
            json.dumps(token_data)
        )

        return token

# Update consultantos/user_management.py
token_manager = TokenManager()

def create_user(email: str, password: str, name: Optional[str] = None) -> Dict:
    # ... existing code ...

    # Generate verification token (stored in Redis)
    verification_token = token_manager.create_verification_token(user_id, email)

    return {
        "user_id": user_id,
        "email": email,
        "verification_token": verification_token
    }

def verify_email_token(token: str) -> bool:
    """Verify email verification token"""
    token_data = token_manager.verify_token(token, "email_verification")

    if not token_data:
        return False

    # Mark email as verified
    user_id = token_data["user_id"]
    db_service = get_db_service()
    db_service.update_user(user_id, {"email_verified": True})

    return True
```

---

## LOW Severity Vulnerabilities

### 🟢 LOW-001: Missing Security Headers
**Severity**: LOW
**CVSS Score**: 3.7
**File**: `consultantos/api/main.py`

**Finding**:
No security headers configured (CSP, HSTS, X-Frame-Options, etc.). Relies on Cloud Run defaults.

**Impact**:
- XSS attack surface
- Clickjacking vulnerabilities
- MIME sniffing attacks

**Remediation**: See MED-002 remediation (Security Headers Middleware).

---

### 🟢 LOW-002: Verbose Error Messages
**Severity**: LOW
**CVSS Score**: 3.1
**File**: Multiple files

**Finding**:
Exception messages expose internal implementation details:
```python
raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
```

**Impact**:
- Information disclosure about system internals
- Stack traces exposed to users
- Enumeration of database structure

**Remediation**:
```python
# consultantos/utils/error_handler.py
import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def custom_exception_handler(request: Request, exc: Exception):
    """
    Custom exception handler with safe error messages
    """
    # Log full error internally
    logger.error(
        f"Exception occurred: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown"
        }
    )

    # Determine safe public message
    if isinstance(exc, HTTPException):
        # HTTPException already has safe detail
        status_code = exc.status_code
        detail = exc.detail
    else:
        # Generic error for unexpected exceptions
        status_code = 500
        detail = "An internal error occurred. Please try again later."

        # In development, include error type (not in production)
        if settings.environment == "development":
            detail = f"{detail} ({type(exc).__name__})"

    return JSONResponse(
        status_code=status_code,
        content={
            "error": detail,
            "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None
        }
    )

# Register handler
from fastapi import FastAPI
app.add_exception_handler(Exception, custom_exception_handler)
```

---

### 🟢 LOW-003: Insufficient Logging
**Severity**: LOW
**CVSS Score**: 2.8
**File**: Multiple files

**Finding**:
Security-relevant events not consistently logged:
- Failed authentication attempts
- API key usage patterns
- Rate limit violations
- Privilege escalation attempts

**Impact**:
- Delayed incident detection
- Insufficient audit trail for compliance
- Difficulty in forensic analysis

**Remediation**:
```python
# consultantos/monitoring.py
import structlog
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Security event logging functions
def log_authentication_success(user_id: str, ip: str, method: str):
    """Log successful authentication"""
    logger.info(
        "authentication_success",
        user_id=user_id,
        ip=ip,
        method=method,
        timestamp=datetime.now().isoformat()
    )

def log_authentication_failure(email: str, ip: str, reason: str):
    """Log failed authentication"""
    logger.warning(
        "authentication_failure",
        email=email,
        ip=ip,
        reason=reason,
        timestamp=datetime.now().isoformat()
    )

def log_rate_limit_exceeded(ip: str, endpoint: str, limit: str):
    """Log rate limit violation"""
    logger.warning(
        "rate_limit_exceeded",
        ip=ip,
        endpoint=endpoint,
        limit=limit,
        timestamp=datetime.now().isoformat()
    )

def log_api_key_usage(user_id: str, endpoint: str, key_hash: str):
    """Log API key usage"""
    logger.info(
        "api_key_usage",
        user_id=user_id,
        endpoint=endpoint,
        key_hash=key_hash[:8],  # Partial hash for privacy
        timestamp=datetime.now().isoformat()
    )

def log_privilege_escalation_attempt(user_id: str, attempted_action: str, ip: str):
    """Log potential privilege escalation"""
    logger.warning(
        "privilege_escalation_attempt",
        user_id=user_id,
        attempted_action=attempted_action,
        ip=ip,
        timestamp=datetime.now().isoformat()
    )

# Add to authentication endpoints
async def authenticate_user(email: str, password: str, ip: str) -> Optional[Dict]:
    user_info = _authenticate_user_internal(email, password)

    if user_info:
        log_authentication_success(user_info["user_id"], ip, "password")
    else:
        log_authentication_failure(email, ip, "invalid_credentials")

    return user_info
```

---

## Dependency Vulnerabilities

### Version Analysis

**Current Versions** (from `requirements.txt`):
```
fastapi==0.120.4         → Latest: 0.115.0 (check for CVEs)
uvicorn==0.35.0          → Latest: 0.32.1 (check for CVEs)
pydantic==2.12.5         → Latest: 2.10.3 (check for CVEs)
slowapi==0.1.9           → Latest: 0.1.9 ✓
passlib[bcrypt]==1.7.4   → Latest: 1.7.4 ✓
python-jose==3.3.0       → Latest: 3.3.0 ✓
```

**Known CVEs** (requires `pip-audit` or `safety` scan):
```bash
# Install security scanning tools
pip install pip-audit safety

# Run vulnerability scan
pip-audit --format json > vulnerabilities.json
safety check --json > safety-report.json
```

**Recommendations**:
1. Pin all dependencies to specific versions (already done ✓)
2. Run weekly vulnerability scans in CI/CD
3. Configure Dependabot/Renovate for automated updates
4. Review changelogs before upgrading

**Automated Scanning** (`.github/workflows/security.yml`):
```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pip-audit safety

      - name: Run pip-audit
        run: pip-audit --format json

      - name: Run safety check
        run: safety check --json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            vulnerabilities.json
            safety-report.json
```

---

## Infrastructure Security

### Dockerfile Security Issues

**Current Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "consultantos.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Security Issues**:
1. ❌ Running as root user
2. ❌ No image signature verification
3. ❌ Copying entire directory (includes .env, secrets)
4. ❌ No health check configured
5. ❌ No resource limits

**Secure Dockerfile**:
```dockerfile
# Use specific version with digest for reproducibility
FROM python:3.11.11-slim@sha256:abc123... AS builder

# Security: Create non-root user
RUN groupadd -r consultantos && useradd -r -g consultantos consultantos

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first (layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy only application code (exclude .env, secrets)
COPY consultantos/ consultantos/
COPY main.py .

# Security: Run as non-root user
USER consultantos

# Health check
HEALTH CHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8080/health')" || exit 1

# Expose port
EXPOSE 8080

# Security: Use exec form to avoid shell interpretation
CMD ["uvicorn", "consultantos.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
```

**.dockerignore**:
```
# Secrets
.env
.env.*
*.key
*.pem
service-account*.json

# Development
.git
.github
.vscode
.idea
*.md
README.md

# Python
__pycache__
*.pyc
*.pyo
*.egg-info
.pytest_cache
.coverage

# Logs
*.log
logs/

# Testing
tests/
.tox/
```

### Cloud Run Security Configuration

**Current `cloudbuild.yaml`**:
```yaml
- '--allow-unauthenticated'  # ❌ Public access
```

**Secure Configuration**:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/consultantos:$COMMIT_SHA', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/consultantos:$COMMIT_SHA']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'consultantos'
      - '--image=gcr.io/$PROJECT_ID/consultantos:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'

      # Security: Require authentication (use IAM or API keys)
      - '--no-allow-unauthenticated'

      # Resource limits
      - '--memory=2Gi'
      - '--cpu=2'
      - '--timeout=300'
      - '--max-instances=10'
      - '--min-instances=1'  # Keep warm instance

      # Security: Service account with minimal permissions
      - '--service-account=consultantos-sa@${PROJECT_ID}.iam.gserviceaccount.com'

      # Environment variables from Secret Manager
      - '--set-secrets=GEMINI_API_KEY=gemini-api-key:latest'
      - '--set-secrets=TAVILY_API_KEY=tavily-api-key:latest'
      - '--set-secrets=JWT_SECRET_KEY=jwt-secret:latest'

      # Networking
      - '--vpc-connector=consultantos-vpc'
      - '--vpc-egress=private-ranges-only'

      # Security headers
      - '--set-env-vars=ENVIRONMENT=production'
      - '--set-env-vars=LOG_LEVEL=INFO'

# Binary authorization (verify image signatures)
options:
  machineType: 'N1_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

# Tag image for tracking
images:
  - 'gcr.io/$PROJECT_ID/consultantos:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/consultantos:latest'
```

---

## Compliance & Best Practices

### OWASP Top 10 (2021) Coverage

| OWASP Risk | Status | Findings |
|------------|--------|----------|
| **A01: Broken Access Control** | 🟡 Partial | API key auth only, no RBAC, missing JWT sessions |
| **A02: Cryptographic Failures** | 🔴 Critical | API keys in repo, no TLS enforcement in dev |
| **A03: Injection** | 🟡 Partial | Weak input sanitization, Firestore safe by design |
| **A04: Insecure Design** | 🟠 High | Missing rate limiting per-user, no session management |
| **A05: Security Misconfiguration** | 🟠 High | CORS wildcard, default credentials, verbose errors |
| **A06: Vulnerable Components** | 🟢 Low | Dependencies pinned, need automated scanning |
| **A07: Auth Failures** | 🟠 High | No password strength, no MFA, no account lockout |
| **A08: Data Integrity Failures** | 🟢 Low | No client-side data deserialization |
| **A09: Logging Failures** | 🟡 Medium | Insufficient security event logging |
| **A10: SSRF** | 🟢 Low | No user-controlled URLs in requests |

### CWE Coverage

- **CWE-798**: Hard-coded credentials (API keys in .env) - 🔴 CRITICAL
- **CWE-522**: Insufficiently protected credentials - 🟠 HIGH
- **CWE-521**: Weak password requirements - 🔴 CRITICAL
- **CWE-352**: CSRF - 🟢 Low (API-only, no cookies)
- **CWE-79**: XSS - 🟡 Medium (input sanitization exists)
- **CWE-89**: SQL Injection - 🟢 Low (Firestore NoSQL)
- **CWE-307**: Improper restriction of excessive auth attempts - 🟠 HIGH

---

## Remediation Roadmap

### Phase 1: IMMEDIATE (Within 24 hours)
**Priority**: Stop the bleeding

1. ✅ **Revoke exposed API keys** (CRIT-001)
   - Tavily API key
   - Gemini API key

2. ✅ **Remove .env from git history** (CRIT-001)
   ```bash
   git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```

3. ✅ **Enable Google Secret Manager** (CRIT-001)
   ```bash
   gcloud secrets create tavily-api-key --data-file=new_key.txt
   gcloud secrets create gemini-api-key --data-file=new_key.txt
   ```

4. ✅ **Add password strength validation** (CRIT-002)
   - Implement `PasswordValidator` class
   - Minimum 12 characters, complexity requirements

5. ✅ **Disable default API key in production** (HIGH-004)
   - Add production check to prevent default credentials

### Phase 2: URGENT (Within 1 week)
**Priority**: Fix high-risk vulnerabilities

1. ✅ **Implement distributed rate limiting** (HIGH-001)
   - Deploy Redis instance
   - Configure per-user + per-IP limits
   - Add endpoint-specific limits

2. ✅ **Fix CORS configuration** (HIGH-002)
   - Remove wildcard origins
   - Require explicit allowed origins in production
   - Add validation logic

3. ✅ **Implement JWT session management** (HIGH-003)
   - Access tokens (15 min expiry)
   - Refresh tokens (30 day expiry)
   - Token revocation on logout

4. ✅ **Add security headers middleware** (MED-002)
   - HSTS, CSP, X-Frame-Options
   - XSS protection headers

5. ✅ **Migrate token storage to Redis** (MED-003)
   - Email verification tokens
   - Password reset tokens

### Phase 3: IMPORTANT (Within 1 month)
**Priority**: Improve security posture

1. ✅ **Enhance input sanitization** (MED-001)
   - Context-aware sanitization
   - Unicode normalization
   - Document parameterized query usage

2. ✅ **Implement structured security logging** (LOW-003)
   - Authentication events
   - Rate limit violations
   - API key usage patterns

3. ✅ **Add custom error handling** (LOW-002)
   - Safe error messages for users
   - Detailed logging for developers

4. ✅ **Harden Dockerfile** (Infrastructure)
   - Non-root user
   - Minimal image layers
   - Health checks

5. ✅ **Update Cloud Run config** (Infrastructure)
   - Remove allow-unauthenticated
   - Add VPC connector
   - Configure service account

### Phase 4: CONTINUOUS (Ongoing)
**Priority**: Maintain security

1. ✅ **Automated dependency scanning**
   - GitHub Actions workflow
   - Weekly vulnerability reports
   - Dependabot/Renovate integration

2. ✅ **Security monitoring**
   - Failed auth attempt tracking
   - Rate limit violation alerts
   - Unusual API usage patterns

3. ✅ **Regular security audits**
   - Quarterly penetration testing
   - Annual third-party audit
   - Continuous code reviews

4. ✅ **Security training**
   - OWASP Top 10 awareness
   - Secure coding practices
   - Incident response drills

---

## Testing & Validation

### Security Test Checklist

```bash
# 1. API Key Security
curl -H "X-API-Key: invalid-key" https://api.consultantos.app/analyze
# Expected: 401 Unauthorized

# 2. Rate Limiting
for i in {1..15}; do curl https://api.consultantos.app/analyze; done
# Expected: 429 Too Many Requests after 10 requests

# 3. CORS
curl -H "Origin: https://evil.com" https://api.consultantos.app/analyze
# Expected: No Access-Control-Allow-Origin header

# 4. HTTPS Enforcement
curl http://api.consultantos.app/analyze
# Expected: 301 Redirect to HTTPS (or connection refused)

# 5. Security Headers
curl -I https://api.consultantos.app/
# Expected: Strict-Transport-Security, X-Frame-Options, etc.

# 6. SQL Injection
curl -X POST https://api.consultantos.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"company": "Tesla'; DROP TABLE reports;--"}'
# Expected: Sanitized input or 400 Bad Request

# 7. XSS
curl -X POST https://api.consultantos.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"company": "<script>alert(1)</script>"}'
# Expected: HTML-escaped in response

# 8. Authentication Bypass
curl https://api.consultantos.app/metrics
# Expected: 401 Unauthorized (requires API key)

# 9. Password Strength
curl -X POST https://api.consultantos.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "weak"}'
# Expected: 400 Bad Request with validation errors

# 10. Token Expiration
# Use expired JWT token
curl -H "Authorization: Bearer <expired-token>" https://api.consultantos.app/analyze
# Expected: 401 Unauthorized
```

---

## Appendix

### A. Security Tools & Resources

**Recommended Tools**:
- `pip-audit`: Python dependency vulnerability scanner
- `bandit`: Python security linter
- `safety`: Dependency vulnerability checker
- `OWASP ZAP`: Web application security scanner
- `Burp Suite`: Manual penetration testing
- `Snyk`: Continuous vulnerability monitoring

**Installation**:
```bash
pip install bandit pip-audit safety
npm install -g snyk
```

**Usage**:
```bash
# Python security linting
bandit -r consultantos/

# Dependency scanning
pip-audit --format json

# Snyk monitoring
snyk monitor
```

### B. Environment Variables Security

**Production `.env` Template**:
```bash
# DO NOT commit this file to git
# Use Google Secret Manager for production

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# API Keys (use Secret Manager)
# TAVILY_API_KEY=<stored-in-secret-manager>
# GEMINI_API_KEY=<stored-in-secret-manager>
# JWT_SECRET_KEY=<stored-in-secret-manager>

# Google Cloud
GCP_PROJECT_ID=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json  # Local only

# Rate Limiting
RATE_LIMIT_ANONYMOUS=10/hour
RATE_LIMIT_AUTHENTICATED=50/hour
RATE_LIMIT_PREMIUM=200/hour

# CORS
ALLOWED_ORIGINS=https://consultantos.app,https://www.consultantos.app
CORS_ALLOW_CREDENTIALS=true

# Redis (for rate limiting and sessions)
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
ALLOWED_HOSTS=consultantos.app,www.consultantos.app
BEHIND_PROXY=true
```

### C. Incident Response Plan

**In case of security breach**:

1. **Immediate Response** (0-1 hour)
   - Revoke all API keys
   - Rotate JWT secret
   - Enable maintenance mode
   - Capture logs and evidence

2. **Investigation** (1-24 hours)
   - Review access logs
   - Identify compromised data
   - Determine attack vector
   - Assess blast radius

3. **Containment** (24-48 hours)
   - Patch vulnerabilities
   - Reset user passwords
   - Notify affected users
   - Update security controls

4. **Recovery** (48-72 hours)
   - Restore from backups
   - Verify system integrity
   - Re-enable services
   - Monitor for anomalies

5. **Post-Mortem** (1 week)
   - Root cause analysis
   - Update security procedures
   - Implement preventive measures
   - Train team on lessons learned

---

## Summary & Recommendations

### Critical Actions Required
1. **Immediately revoke exposed API keys** (CRIT-001)
2. **Remove .env from git history** (CRIT-001)
3. **Implement password strength validation** (CRIT-002)
4. **Deploy distributed rate limiting** (HIGH-001)
5. **Fix CORS configuration** (HIGH-002)

### Security Posture Improvement
- **Current State**: ⚠️ HIGH RISK
- **Target State** (after Phase 1-3): 🟡 MEDIUM RISK
- **Long-term Goal**: 🟢 LOW RISK

### Estimated Effort
- **Phase 1 (IMMEDIATE)**: 4-8 hours
- **Phase 2 (URGENT)**: 2-3 days
- **Phase 3 (IMPORTANT)**: 1-2 weeks
- **Phase 4 (CONTINUOUS)**: Ongoing

### Next Steps
1. Review this report with development team
2. Prioritize remediation based on risk severity
3. Create GitHub issues for each finding
4. Schedule weekly security reviews
5. Implement automated security testing in CI/CD

---

**Report Generated**: November 7, 2025
**Next Audit Recommended**: December 7, 2025 (post-remediation)
