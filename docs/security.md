# DONGLYN — SECURITY GUIDELINES

> Official security specification for DONGLYN.
>
> This document defines the security principles, authentication,
> authorization, CAPTCHA protection, input validation, secrets handling,
> API security, database security, streaming protection, abuse prevention,
> logging, privacy, and security QA requirements.
>
> Security is a first-class architectural requirement.
> Security controls MUST be enforced server-side where applicable.

---

# 1. SECURITY NORTH STAR

DONGLYN should be:

- Secure
- Private
- Resilient
- Predictable
- Abuse-resistant
- Production-ready
- User-friendly

Security should protect the platform without making normal users feel like they are fighting the security system.

The ideal experience is:

> Strong security behind a simple interface.

---

# 2. SECURITY PRINCIPLES

## 2.1 NEVER TRUST THE CLIENT

Everything sent from the browser must be considered untrusted.

Never trust:

- localStorage
- cookies without validation
- hidden form fields
- query parameters
- request bodies
- client-side permissions
- client-side CAPTCHA state
- client-side roles
- client-side watch progress

Sensitive decisions must be validated server-side.

---

# 3. DEFENSE IN DEPTH

DONGLYN should not rely on a single security mechanism.

Use multiple layers:

```text
Browser
   ↓
Security Headers
   ↓
Rate Limiting
   ↓
Authentication
   ↓
Authorization
   ↓
Input Validation
   ↓
Application Logic
   ↓
Database Constraints
   ↓
External Service Protection
```

A failure in one layer should not automatically compromise the entire application.

---

# 4. THREAT MODEL

Consider threats including:

- credential attacks
- account enumeration
- brute force
- bot abuse
- scraping abuse
- API abuse
- malicious input
- XSS
- CSRF
- SQL injection
- SSRF
- session theft
- token leakage
- insecure direct object references
- malicious file uploads
- external provider compromise
- database exposure
- secret leakage
- denial-of-service behavior

Security implementation should prioritize realistic threats to the application.

---

# 5. AUTHENTICATION

Authentication must be handled through a trusted authentication mechanism.

Do not build insecure custom authentication when a proven framework or provider is already available.

Authentication must support:

- secure password handling
- session management
- logout
- expiration
- invalidation
- account recovery
- appropriate abuse protection

---

# 6. PASSWORD SECURITY

Passwords must NEVER be stored as plaintext.

Use a modern password hashing algorithm supported by the authentication system.

Never:

- log passwords
- return passwords in API responses
- store passwords in localStorage
- include passwords in analytics events

Password reset tokens must be:

- random
- short-lived
- single-use
- invalidated after successful reset

---

# 7. SESSION SECURITY

Sessions must be protected against theft.

Where cookies are used, prefer:

- `HttpOnly`
- `Secure`
- appropriate `SameSite`

Do not expose sensitive session tokens to client-side JavaScript unnecessarily.

Sessions should expire according to the application's security requirements.

Logout should invalidate the session appropriately.

---

# 8. TOKEN SECURITY

Never expose:

- private API keys
- database credentials
- CAPTCHA secret keys
- signing secrets
- provider credentials
- administrative tokens

to browser code.

Public client configuration is not the same as a secret.

Treat every environment variable as sensitive until proven otherwise.

---

# 9. AUTHORIZATION

Authorization must happen server-side.

Example:

```text
User A
  ↓
GET /api/me/history
  ↓
Server identifies User A
  ↓
Only User A's history is returned
```

Never trust:

```text
userId=123
```

provided by the browser as proof of identity.

---

# 10. OBJECT-LEVEL AUTHORIZATION

Every protected resource must verify ownership where appropriate.

Example:

```text
GET /api/history/:id
```

The server must verify:

```text
resource.userId === authenticatedUser.id
```

before returning private data.

This protects against IDOR-style vulnerabilities.

---

# 11. INPUT VALIDATION

Every external input must be validated.

Validate:

- request body
- query parameters
- route parameters
- headers where relevant
- uploaded files
- external provider responses

Use allowlists and schemas where possible.

---

# 12. INPUT SANITIZATION

Do not blindly trust user-provided HTML.

For user-generated content:

- sanitize HTML if HTML is allowed
- otherwise render as text
- encode output appropriately

Never insert untrusted content directly into the DOM.

---

# 13. XSS PROTECTION

Prevent:

- reflected XSS
- stored XSS
- DOM-based XSS

Avoid unsafe APIs such as unrestricted HTML injection.

If raw HTML rendering is required, sanitize it with a trusted sanitizer.

---

# 14. SQL INJECTION

Never construct SQL queries using unsafe string concatenation.

Prefer:

- ORM parameterization
- prepared statements
- parameterized queries

Example concept:

```text
BAD:
SELECT * FROM users WHERE email = '${email}'

GOOD:
Parameterized query
```

Database access must treat user input as data, never executable SQL.

---

# 15. CSRF

If authentication relies on cookies, protect state-changing operations against CSRF.

Consider:

- SameSite cookies
- CSRF tokens where appropriate
- Origin validation
- strict request validation

GET requests should not perform destructive state changes.

---

# 16. CORS

CORS must be explicit.

Do not use:

```text
Access-Control-Allow-Origin: *
```

for authenticated APIs unless there is a deliberate and safe reason.

Prefer an allowlist of trusted origins.

---

# 17. SECURITY HEADERS

Production should use appropriate security headers.

Consider:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
```

Avoid headers that conflict with required application behavior.

CSP should be introduced carefully and tested against the actual application.

---

# 18. HTTPS

Production traffic must use HTTPS.

Redirect HTTP to HTTPS where appropriate.

Do not send credentials or session information over plaintext HTTP.

---

# 19. CAPTCHA SECURITY

DONGLYN may use:

- Cloudflare protection/challenge
- hCaptcha

depending on the configured flow.

CAPTCHA is an anti-abuse control, not an authentication mechanism.

---

# 20. CAPTCHA SERVER VERIFICATION

The browser must never be trusted to declare:

```text
captchaPassed = true
```

Instead:

```text
Browser
  ↓
CAPTCHA token
  ↓
DONGLYN backend
  ↓
CAPTCHA provider verification
  ↓
Verified
  ↓
Continue protected operation
```

The secret verification key must remain server-side.

---

# 21. CAPTCHA PLACEMENT

CAPTCHA should be used where it meaningfully reduces abuse.

Potential areas:

- initial security challenge
- registration
- login after suspicious activity
- password recovery
- high-risk actions
- automated abuse protection

Do not unnecessarily challenge every normal interaction.

---

# 22. CAPTCHA FAILURE HANDLING

Never expose provider secrets or raw provider internals.

User-facing response:

```text
Verifikasi keamanan gagal.
Silakan coba lagi.
```

Log useful diagnostic information server-side without logging secrets.

---

# 23. RATE LIMITING

Rate limit security-sensitive endpoints.

Examples:

```text
/api/auth/login
/api/auth/register
/api/auth/forgot-password
/api/search
/api/captcha/verify
```

Also consider expensive operations such as:

- scraping triggers
- synchronization
- streaming-source resolution

---

# 24. BRUTE-FORCE PROTECTION

Protect authentication against repeated attempts.

Possible controls:

- rate limiting
- progressive delays
- CAPTCHA escalation
- temporary lockout
- IP reputation
- device/session signals

Avoid permanent account lockouts that can be abused for denial-of-service against users.

---

# 25. ACCOUNT ENUMERATION

Do not reveal whether an account exists through overly specific public responses.

For example, password recovery should avoid clearly revealing:

```text
This email does not exist.
```

Prefer neutral messaging where appropriate.

---

# 26. API SECURITY

Every API endpoint should have an explicit security classification.

Examples:

```text
PUBLIC
AUTHENTICATED
ADMIN
INTERNAL
```

Do not accidentally expose internal endpoints publicly.

---

# 27. PUBLIC API ENDPOINTS

Even public endpoints require:

- validation
- rate limiting where appropriate
- safe error handling
- output filtering
- abuse protection

Public does not mean unrestricted.

---

# 28. ADMIN / INTERNAL ENDPOINTS

Administrative functionality must have stronger authorization.

Never rely on:

```text
/admin
```

being hidden as a security mechanism.

Require explicit authorization.

---

# 29. ERROR HANDLING

Never expose:

- stack traces
- SQL queries
- filesystem paths
- environment variables
- provider credentials
- internal service URLs
- internal architecture details

to users.

Production errors should be safe and concise.

---

# 30. ERROR CODES

Use stable internal/public error codes where useful.

Example:

```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Silakan login terlebih dahulu."
  }
}
```

Do not expose sensitive implementation details.

---

# 31. SECRETS MANAGEMENT

Secrets belong in:

- environment variables
- deployment secret managers
- secure server configuration

Never commit secrets to Git.

Never place secrets in:

- frontend source
- public configuration
- documentation
- screenshots
- logs
- issue reports

---

# 32. ENVIRONMENT FILES

Use:

```text
.env
.env.local
.env.production
.env.example
```

as appropriate to the framework.

`.env.example` must contain placeholders only.

Example:

```text
DATABASE_URL=
HCAPTCHA_SECRET=
CLOUDFLARE_SECRET=
```

Never put real values in `.env.example`.

---

# 33. SECRET ROTATION

Secrets should be rotatable.

If a secret is exposed:

1. Revoke it.
2. Generate a replacement.
3. Update deployment configuration.
4. Verify affected services.
5. Remove the leaked value from source/history where practical.
6. Review logs and access.

Do not assume deleting the visible line makes an exposed secret safe.

---

# 34. GIT SECURITY

Before committing:

- inspect `.gitignore`
- verify environment files
- scan for secrets
- inspect staged changes

Never commit:

```text
.env
private keys
service credentials
database dumps containing secrets
session tokens
```

---

# 35. DATABASE SECURITY

Database credentials must remain server-side.

Production database access should be restricted.

Prefer:

- private networking
- firewall restrictions
- least-privilege accounts
- encrypted connections
- strong credentials

---

# 36. DATABASE LEAST PRIVILEGE

Application database users should have only the permissions they require.

Do not use unrestricted administrative database accounts for normal application traffic.

---

# 37. DATABASE CONSTRAINTS

Security should not depend only on application logic.

Use database constraints where appropriate:

- unique constraints
- foreign keys
- not-null constraints
- check constraints

Example:

```text
User + Favorite + Donghua
```

should prevent duplicate favorites through an appropriate unique constraint.

---

# 38. TRANSACTIONS

Use transactions for security-sensitive multi-step operations where partial completion could create inconsistent state.

Examples:

- account changes
- ownership changes
- critical data synchronization

---

# 39. PRIVACY

Collect only data that DONGLYN actually needs.

Avoid collecting unnecessary:

- personal information
- device information
- tracking data
- behavioral data

If data is not required, prefer not storing it.

---

# 40. USER DATA

User-specific data includes:

- profile information
- watch history
- favorites
- watchlist
- preferences
- authentication data

Only return user data to authorized users.

---

# 41. DATA MINIMIZATION

API responses should return only required fields.

Do not return the entire user record when the UI only needs:

```text
id
name
avatar
```

---

# 42. LOG PRIVACY

Logs must not contain:

- passwords
- session tokens
- access tokens
- refresh tokens
- CAPTCHA secrets
- database passwords
- private API keys

Sensitive values should be redacted.

---

# 43. AUDIT EVENTS

For security-sensitive actions, consider recording:

- login
- logout
- password change
- password reset
- suspicious activity
- account changes
- administrative actions

Keep audit records minimal and useful.

---

# 44. STREAMING SECURITY

Streaming sources are external and unreliable.

Never assume an external URL is safe simply because it came from a known provider.

Validate and normalize provider responses.

---

# 45. STREAMING URL VALIDATION

Before using a provider-generated URL, validate:

- scheme
- hostname where appropriate
- expected format
- protocol
- expiration where relevant

Avoid blindly requesting arbitrary URLs from user-controlled input.

---

# 46. SSRF PROTECTION

Any backend feature that fetches remote URLs must defend against SSRF.

Never allow unrestricted server-side fetching of arbitrary user-supplied URLs.

Block or restrict access to:

- localhost
- loopback addresses
- private network ranges
- internal metadata endpoints
- internal infrastructure

Use strict allowlists where practical.

---

# 47. EXTERNAL PROVIDERS

Provider integrations must be isolated behind adapters.

Example:

```text
Streaming Service
       ↓
Provider Adapter
       ↓
Validated Provider Response
       ↓
Internal Domain Model
```

Do not allow provider-specific untrusted structures to spread through the application.

---

# 48. TIMEOUTS

External network requests must have timeouts.

Never allow an external provider to keep an application request open indefinitely.

---

# 49. RETRIES

Retries must be bounded.

Use retries only when:

- the operation is safe
- failure is transient
- retry count is limited

Avoid retry storms.

---

# 50. USER-GENERATED CONTENT

If users can submit:

- comments
- names
- descriptions
- profile information

treat all such values as untrusted.

Validate length, format, encoding, and allowed content.

---

# 51. FILE UPLOAD SECURITY

If file uploads are introduced:

Validate:

- extension
- MIME type
- actual file signature
- file size

Use generated safe filenames.

Never execute uploaded files.

Store uploads outside sensitive executable paths where appropriate.

---

# 52. IMAGE SECURITY

Remote images should be handled through controlled image loading mechanisms.

Do not allow arbitrary remote image sources if the framework configuration can enforce a safe allowlist.

---

# 53. CONTENT SECURITY

Third-party scripts should be minimized.

Before adding a third-party script, determine:

- why it is needed
- what data it receives
- whether it can be replaced
- whether it affects CSP
- whether it increases attack surface

---

# 54. DEPENDENCY SECURITY

Dependencies are part of the attack surface.

Regularly check for:

- known vulnerabilities
- abandoned packages
- suspicious dependencies
- unnecessary packages

Prefer established, maintained packages.

---

# 55. SUPPLY CHAIN SECURITY

Avoid installing packages simply because they are popular in snippets.

Before adding a package:

1. Verify package identity.
2. Check maintenance.
3. Review permissions/capabilities.
4. Check dependency footprint.
5. Check known vulnerabilities.

---

# 56. CLIENT STORAGE

Do not store sensitive credentials in:

```text
localStorage
sessionStorage
```

unless there is a deliberate, well-understood security reason.

Prefer secure session mechanisms.

---

# 57. BROWSER SECURITY

Frontend should avoid:

- dangerous HTML injection
- unsafe URL handling
- exposing secrets
- insecure redirects
- unnecessary third-party scripts

---

# 58. OPEN REDIRECT PROTECTION

Do not blindly redirect users to arbitrary URLs supplied through query parameters.

If redirect parameters are supported, validate against an allowlist or restrict them to internal paths.

---

# 59. SECURITY REDIRECTS

Examples of dangerous patterns:

```text
/redirect?url=https://attacker.example
```

unless explicitly validated.

Prefer:

```text
/redirect?destination=/watch
```

with strict internal destination validation.

---

# 60. CLICKJACKING PROTECTION

Protect sensitive pages against unauthorized framing where appropriate.

Use suitable headers/policies such as CSP `frame-ancestors`.

Streaming/player pages may require special consideration if legitimate embedding is supported.

---

# 61. SECURITY FOR THE PLAYER

The video player must not expose:

- provider credentials
- internal API secrets
- private administrative endpoints

Player controls should only receive data necessary for playback.

---

# 62. WATCH PROGRESS SECURITY

Watch progress is user-owned data.

The backend should:

- authenticate the user
- validate episode ownership/reference
- validate progress values
- reject impossible values
- avoid accepting arbitrary user IDs

Example validation:

```text
progress >= 0
progress <= duration
```

where duration is known and applicable.

---

# 63. FAVORITE SECURITY

Favorite operations must:

- require authentication
- validate Donghua ID
- verify resource existence where appropriate
- prevent duplicates
- enforce ownership on deletion

---

# 64. WATCHLIST SECURITY

Watchlist operations follow the same rules:

- authentication
- validation
- duplicate protection
- ownership checks

---

# 65. SEARCH ABUSE

Search endpoints should defend against:

- extremely long queries
- excessive requests
- expensive wildcard patterns
- pathological filters

Use:

- query length limits
- rate limiting
- pagination
- safe database queries

---

# 66. SCRAPING ABUSE

If DONGLYN has scraping or ingestion functionality, protect it from uncontrolled public triggering.

Scraping jobs should be:

- authenticated
- authorized
- rate-limited
- queued
- observable

Never expose unrestricted scraping controls to anonymous users.

---

# 67. RESOURCE EXHAUSTION

Protect expensive operations from consuming unlimited resources.

Set appropriate limits for:

- request body size
- query length
- pagination size
- upload size
- external response size
- job concurrency

---

# 68. DENIAL-OF-SERVICE RESILIENCE

Application-level controls should include:

- rate limiting
- caching
- pagination
- request timeouts
- bounded retries
- resource limits

Infrastructure-level protection may additionally use CDN/WAF capabilities.

---

# 69. CLOUDFLARE SECURITY

If Cloudflare is used, it may provide:

- WAF
- bot protection
- challenge
- rate limiting
- DDoS protection
- CDN

Cloudflare should complement application security rather than replace it.

---

# 70. HCAPTCHA SECURITY

hCaptcha should be treated as a verification signal.

The backend must validate:

- token validity
- expected site configuration
- response status

Do not treat the browser's visual result as proof by itself.

---

# 71. SECURITY UX

Security errors should be understandable.

Bad:

```text
403 Forbidden
ERR_CAPTCHA_17
```

Better:

```text
Verifikasi keamanan gagal.
Silakan coba lagi.
```

Technical details belong in logs, not user-facing messages.

---

# 72. SECURITY STATES

Important security UI states:

```text
Checking
Verified
Failed
Expired
Retrying
Blocked
```

Each state should have clear feedback.

---

# 73. SECURITY ANIMATIONS

Security screens may use:

- Lucide Animated Shield
- Lucide Animated ShieldCheck
- Lucide Animated RefreshCw
- subtle loading motion

Do not use frightening red flashing animations.

---

# 74. AUTHENTICATION UX

Avoid making legitimate users repeat verification unnecessarily.

Use risk-based escalation where supported.

Example:

```text
Normal login
    ↓
No challenge

Suspicious activity
    ↓
CAPTCHA

Repeated suspicious activity
    ↓
Stronger protection
```

---

# 75. SECURITY BY DEFAULT

Default configuration should be the safer configuration.

Examples:

- secure cookies
- HTTPS
- strict validation
- limited CORS
- rate limits
- safe error messages
- secret-free frontend

Developers should have to deliberately weaken a security control.

---

# 76. SECURITY CONFIGURATION

Security-sensitive configuration must be centralized where practical.

Examples:

```text
CORS origins
Rate limits
Cookie settings
CAPTCHA configuration
Allowed providers
Upload limits
Security headers
```

Avoid duplicating security constants throughout the codebase.

---

# 77. SECURITY TESTING

Security testing should cover:

- authentication
- authorization
- input validation
- CAPTCHA verification
- rate limiting
- ownership checks
- XSS
- CSRF
- SSRF
- injection
- secret exposure

---

# 78. AUTHORIZATION TESTS

Explicitly test:

```text
User A cannot access User B's history.
User A cannot delete User B's favorite.
User A cannot modify User B's watchlist.
Anonymous users cannot access private endpoints.
```

---

# 79. INPUT SECURITY TESTS

Test malicious values including:

```text
<script>
' OR 1=1
../../
javascript:
http://localhost
```

and other malformed or oversized inputs.

Expected behavior:

- validation failure
- safe handling
- no execution
- no sensitive error leakage

---

# 80. CAPTCHA TESTS

Test:

- missing token
- invalid token
- expired token
- provider failure
- valid token
- repeated requests

Never bypass CAPTCHA only because the frontend claims success.

---

# 81. RATE LIMIT TESTS

Verify that repeated requests eventually receive appropriate throttling.

Ensure rate limiting does not permanently lock legitimate users unnecessarily.

---

# 82. SECRET SCANNING

CI/CD should ideally scan for accidental secrets.

Potential targets:

- API keys
- tokens
- private keys
- database credentials
- cloud credentials

A secret detected in source should be treated as compromised until proven otherwise.

---

# 83. SECURITY CI/CD

Recommended pipeline:

```text
Install
  ↓
Lint
  ↓
Type Check
  ↓
Unit Tests
  ↓
Integration Tests
  ↓
Build
  ↓
Dependency Audit
  ↓
Secret Scan
  ↓
Deploy
```

Do not deploy known critical security issues without an explicit risk decision.

---

# 84. SECURITY MONITORING

Monitor for:

- authentication spikes
- repeated failures
- unusual API traffic
- provider failures
- suspicious scraping
- unexpected admin activity
- rate-limit events

---

# 85. INCIDENT RESPONSE

If a security incident occurs:

1. Identify the affected system.
2. Contain the issue.
3. Revoke compromised credentials.
4. Rotate secrets.
5. Preserve relevant logs.
6. Patch the vulnerability.
7. Verify the fix.
8. Review the root cause.
9. Document the incident.

Do not simply patch symptoms without understanding the cause.

---

# 86. COMPROMISED SECRET RESPONSE

If a secret appears in Git, logs, screenshots, or chat:

```text
Assume compromised.
```

Then:

```text
Revoke
↓
Rotate
↓
Deploy replacement
↓
Audit usage
↓
Clean exposure
```

---

# 87. BACKUP SECURITY

Backups may contain sensitive information.

Protect backups with:

- access control
- encryption where appropriate
- restricted storage
- retention policies

Do not expose database backups through public web directories.

---

# 88. PRODUCTION ACCESS

Production access should follow least privilege.

Developers should not automatically receive unrestricted production credentials.

Administrative access should be limited and auditable where possible.

---

# 89. DEBUG MODE

Production must not run with development/debug settings that expose:

- stack traces
- internal paths
- environment configuration
- verbose diagnostics

---

# 90. SECURITY HEADERS QA

Verify production responses for appropriate security headers.

Do not blindly copy a header configuration without testing application behavior.

---

# 91. SECURITY ARCHITECTURE ANTI-PATTERNS

Never:

- store passwords in plaintext
- expose secrets to frontend
- trust client authorization
- trust client CAPTCHA state
- build raw SQL from user input
- allow arbitrary server-side URL fetching
- use unrestricted CORS for private APIs
- expose stack traces
- commit `.env`
- log access tokens
- rely on hidden admin routes
- use localStorage for sensitive tokens without a deliberate security design
- allow unlimited expensive requests
- trust external provider responses blindly

---

# 92. SECURITY REVIEW CHECKLIST

Before production:

## Authentication

- Passwords hashed securely
- Sessions protected
- Logout works
- Reset tokens are safe
- Brute-force protection exists

## Authorization

- Protected routes verified server-side
- Resource ownership checked
- Admin permissions enforced

## Input

- Body validation
- Query validation
- Route validation
- Output encoding
- XSS protection
- Injection protection

## Network

- HTTPS
- CORS configured
- Security headers
- SSRF protection
- External request timeouts

## CAPTCHA

- Server-side verification
- Secrets protected
- Invalid tokens rejected
- Expired tokens handled

## Data

- Database credentials protected
- Least privilege
- Constraints
- Backups protected

## Secrets

- No secrets in source
- No secrets in logs
- Secret scanning enabled
- Rotation process understood

## Abuse

- Rate limits
- Resource limits
- Search protection
- Scraping protection
- DoS mitigation

## Monitoring

- Security events logged
- Sensitive values redacted
- Errors monitored

---

# 93. DEFINITION OF SECURITY DONE

A security-sensitive feature is not complete until:

- inputs are validated
- authentication is enforced where required
- authorization is enforced where required
- ownership is checked
- secrets are protected
- errors are sanitized
- abuse controls exist where appropriate
- tests cover critical security paths
- production configuration is reviewed

---

# 94. FINAL SECURITY PRINCIPLE

DONGLYN security should be:

STRONG
+
SILENT
+
LAYERED
+
SERVER-SIDE
+
USER-FRIENDLY

The user should feel:

> "DONGLYN is safe."

without constantly feeling:

> "DONGLYN is blocking me."

---

# 95. DONGLYN SECURITY NORTH STAR

Protect:

THE USER
+
THE ACCOUNT
+
THE CONTENT
+
THE API
+
THE DATABASE
+
THE INFRASTRUCTURE

while maintaining:

SPEED
+
SIMPLICITY
+
RELIABILITY
+
GOOD UX

Security is not an extra feature.

Security is part of DONGLYN's architecture.
