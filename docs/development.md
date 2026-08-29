# DONGLYN — DEVELOPMENT GUIDELINES

> Development source of truth for the DONGLYN streaming platform.
>
> This document defines how the project should be developed, modified,
> tested, reviewed, debugged, and prepared for production.
>
> Primary goals:
> - Keep development predictable.
> - Preserve existing functionality.
> - Maintain the premium DONGLYN UX.
> - Avoid unnecessary rewrites.
> - Keep the codebase clean and scalable.

---

# 1. CORE DEVELOPMENT PRINCIPLES

Every implementation should prioritize:

1. Correctness
2. Security
3. Maintainability
4. Performance
5. UX
6. Simplicity

Do not optimize for code volume.

Prefer the smallest clean implementation that completely solves the requirement.

---

# 2. BEFORE CHANGING CODE

Before modifying an existing feature:

1. Inspect the repository.
2. Identify the relevant files.
3. Understand existing architecture.
4. Find consumers of shared components.
5. Check existing API contracts.
6. Check related tests.
7. Identify possible regressions.
8. Implement incrementally.

Never blindly overwrite working code.

---

# 3. EXISTING FUNCTIONALITY IS SACRED

If the task is a redesign or UI improvement:

DO NOT unnecessarily change:

- API behavior
- database schema
- authentication logic
- scraping logic
- streaming logic
- routes
- existing business rules

unless explicitly required.

A redesign should improve the interface without destroying functionality.

---

# 4. DEVELOPMENT WORKFLOW

Use:

```text
Understand
   ↓
Plan
   ↓
Implement
   ↓
Run Type Check
   ↓
Run Lint
   ↓
Run Tests
   ↓
Build
   ↓
Review
```

For small changes, the process can be lighter, but critical checks must still be performed.

---

# 5. REPOSITORY INSPECTION

Before implementation, inspect:

- package.json
- lockfile
- framework configuration
- TypeScript configuration
- Tailwind configuration
- environment examples
- source structure
- API routes
- database configuration
- existing components
- test configuration

Do not assume the project uses a technology simply because it is common.

Follow the actual repository.

---

# 6. TECHNOLOGY RESPECT

Use the existing project stack unless there is a strong reason to change it.

Do not introduce:

- unnecessary frameworks
- duplicate UI libraries
- competing state managers
- unnecessary ORMs
- unnecessary backend frameworks

Avoid technology churn.

---

# 7. PACKAGE MANAGEMENT

Use the package manager already established by the repository.

Do not switch package managers casually.

Always update the lockfile when dependencies change.

---

# 8. DEPENDENCY POLICY

Before adding a dependency:

- confirm it is necessary
- check whether an existing package already solves the problem
- evaluate bundle size
- evaluate maintenance
- evaluate security
- evaluate licensing where relevant

Avoid dependency bloat.

---

# 9. TYPESCRIPT

Use strict TypeScript where the project supports it.

Prefer:

```ts
type
interface
unknown
generics
discriminated unions
```

Avoid:

```ts
any
```

unless there is a documented reason.

When handling unknown external data, validate it before trusting its shape.

---

# 10. NAMING

Use descriptive names.

Good:

```text
DonghuaCard
EpisodeSelector
WatchHistoryService
StreamingProvider
```

Avoid:

```text
Thing
Data
Helper
Manager2
Temp
NewComponent
```

Names should explain intent.

---

# 11. COMPONENT DEVELOPMENT

Components should have one clear responsibility.

Avoid giant components containing:

- API calls
- database logic
- authentication
- complex business rules
- dozens of unrelated UI sections

Extract meaningful logic into services/hooks/utilities.

---

# 12. COMPONENT SIZE

Large files are not automatically bad.

Do not split files merely to reduce line count.

Extract code when separation improves:

- readability
- reusability
- testing
- ownership
- maintainability

---

# 13. UI COMPONENT HIERARCHY

Prefer:

```text
Primitive
   ↓
Shared
   ↓
Feature
   ↓
Page
```

Example:

```text
Button
  ↓
PosterCard
  ↓
DonghuaCard
  ↓
TrendingSection
  ↓
HomePage
```

---

# 14. DESIGN SYSTEM

DONGLYN must maintain a consistent design language.

Primary qualities:

- modern
- elegant
- premium
- clean
- cinematic
- user-friendly

Do not introduce random visual styles for individual pages.

---

# 15. COLORS

Follow the established DONGLYN palette and existing design specification.

Do not invent unrelated colors casually.

Accent colors should be used intentionally for:

- focus
- active states
- primary actions
- selected states
- important highlights

Avoid excessive accent usage.

---

# 16. TYPOGRAPHY

Use the typography defined by the project design system.

Maintain:

- clear hierarchy
- readable body text
- consistent heading scale
- appropriate line height
- predictable spacing

Do not use random fonts on individual components.

---

# 17. ICONS

DONGLYN should use the configured Lucide / Lucide Animated icon system.

Preferred source:

```text
lucide-animated.com
```

Use animated icons where animation adds meaningful feedback.

Avoid mixing unrelated icon libraries unless explicitly required.

---

# 18. ICON ANIMATION

Animations should be:

- subtle
- smooth
- purposeful
- premium

Avoid:

- excessive bouncing
- constant spinning
- distracting motion
- animation on every element

---

# 19. POSTER CARDS

Donghua poster cards are a major part of the product identity.

Cards should feel:

- premium
- cinematic
- modern
- consistent
- responsive

Consider:

- aspect ratio consistency
- image quality
- rounded corners
- subtle hover interaction
- title truncation
- episode/status metadata
- loading skeleton
- fallback image

---

# 20. IMAGE HANDLING

Optimize images.

Use:

- responsive sizing
- lazy loading when appropriate
- modern formats
- appropriate compression
- meaningful alt text

Do not load unnecessarily huge images.

---

# 21. LOADING STATES

Every asynchronous user-facing feature should have an appropriate loading state.

Examples:

- skeleton
- spinner
- progress indicator
- subtle animated placeholder

Avoid blank screens during normal loading.

---

# 22. ERROR STATES

Every important asynchronous feature should handle failure.

Example:

```text
Loading
   ↓
Success
   OR
Error
   ↓
Retry
```

Errors should be understandable to users.

---

# 23. EMPTY STATES

Empty data is not necessarily an error.

Examples:

- no favorites
- no watch history
- no search results
- empty watchlist

Provide a useful empty state with an appropriate action.

---

# 24. RESPONSIVE DEVELOPMENT

Design for:

- mobile
- tablet
- desktop
- large desktop

Do not treat desktop as the only target.

Important content should remain usable at narrow widths.

---

# 25. MOBILE-FIRST THINKING

When appropriate, establish the core layout for smaller screens first, then enhance it for larger screens.

Avoid desktop layouts that simply collapse badly on mobile.

---

# 26. ACCESSIBILITY

Interactive elements must be usable with:

- keyboard
- screen readers where applicable
- sufficient contrast
- visible focus states

Use semantic HTML.

Buttons should be buttons.

Links should be links.

Do not use clickable `<div>` elements when a semantic element exists.

---

# 27. KEYBOARD ACCESS

Important interactions should support keyboard navigation.

Examples:

- search
- menus
- dialogs
- player controls
- filters
- authentication forms

---

# 28. REDUCED MOTION

Respect user preferences for reduced motion where practical.

Do not make essential information dependent on animation.

---

# 29. FRONTEND DATA FETCHING

Centralize API communication where practical.

Prefer:

```text
Component
   ↓
Feature Hook / Service
   ↓
API Client
   ↓
API
```

Avoid scattering raw API calls throughout UI components.

---

# 30. API ERROR HANDLING

The frontend should gracefully handle:

- 400
- 401
- 403
- 404
- 409
- 429
- 500
- network errors
- timeout errors

Provide useful UI feedback without exposing internal details.

---

# 31. FORM DEVELOPMENT

Forms should include:

- validation
- loading state
- disabled state during submission
- success state
- error state

Do not allow repeated accidental submissions.

---

# 32. SEARCH DEVELOPMENT

Search should support:

- debouncing where appropriate
- loading state
- empty results
- error state
- pagination when necessary
- URL synchronization where useful

Do not send a request on every keystroke without a reason.

---

# 33. WATCH PAGE DEVELOPMENT

The watch page is a critical flow.

Prioritize:

1. Fast player availability
2. Reliable episode loading
3. Clear episode navigation
4. Source fallback
5. Watch progress
6. Error recovery

Do not allow secondary UI to block playback unnecessarily.

---

# 34. STREAMING PLAYER

The player should be isolated from provider-specific implementation.

Player input should be normalized.

Example:

```text
Episode
 ↓
Streaming Service
 ↓
Normalized Sources
 ↓
Player
```

---

# 35. WATCH PROGRESS

Watch progress should update safely.

Avoid sending excessive requests.

Use debouncing, throttling, or milestone-based updates where appropriate.

Never trust client-provided user identity.

---

# 36. AUTH DEVELOPMENT

Protected features must verify authentication server-side.

Examples:

- profile
- history
- favorites
- watchlist

Do not hide UI and assume that is sufficient protection.

---

# 37. CAPTCHA DEVELOPMENT

If Cloudflare and hCaptcha are configured:

```text
Browser
 ↓
Challenge / CAPTCHA
 ↓
Token
 ↓
Backend Verification
 ↓
Protected Operation
```

Never implement:

```text
captchaPassed === true
```

as the only security check.

---

# 38. DATABASE DEVELOPMENT

Use migrations for schema changes.

Never manually modify production schema as an undocumented one-off action.

Keep schema changes reproducible.

---

# 39. DATABASE QUERIES

Queries should be:

- parameterized
- efficient
- scoped
- predictable

Avoid fetching data that the UI does not need.

---

# 40. DATABASE PERFORMANCE

Watch for:

- N+1 queries
- missing indexes
- unnecessary joins
- huge result sets
- repeated identical queries

Use pagination for large datasets.

---

# 41. API DEVELOPMENT

Endpoints should have:

- clear purpose
- validation
- predictable response
- predictable errors
- appropriate authentication
- appropriate rate limiting

Avoid endpoints that mix unrelated responsibilities.

---

# 42. BACKEND SERVICES

Business logic belongs in services rather than giant controllers/routes.

Example:

```text
Route
 ↓
Validation
 ↓
Service
 ↓
Repository
 ↓
Database
```

---

# 43. EXTERNAL PROVIDERS

External APIs, streaming providers, CAPTCHA services, and similar integrations should be isolated.

Use adapters/services.

Do not scatter provider-specific SDK calls across the application.

---

# 44. EXTERNAL REQUESTS

All external requests should consider:

- timeout
- retries
- response validation
- error handling
- rate limits

Never assume an external service is always available.

---

# 45. SCRAPING / INGESTION

If content ingestion exists:

- keep it outside frontend code
- normalize provider data
- validate external responses
- prevent duplicate records
- use retries carefully
- use queues for heavy jobs where appropriate

---

# 46. CACHE DEVELOPMENT

Cache only appropriate data.

Good candidates:

- popular content
- genres
- static metadata
- slow-changing content

Do not accidentally cache private user data globally.

---

# 47. PERFORMANCE DEVELOPMENT

Optimize the critical path first.

Priorities:

```text
Initial Render
 ↓
Images
 ↓
API Latency
 ↓
JavaScript
 ↓
Interaction
 ↓
Secondary Features
```

Measure before performing major optimization.

---

# 48. JAVASCRIPT BUDGET

Avoid unnecessary client-side JavaScript.

Prefer server-side rendering or server components where supported and appropriate.

Use client components only when interaction requires them.

---

# 49. BUNDLE SIZE

Before adding a large dependency, consider:

- dynamic import
- tree shaking
- native browser APIs
- existing dependencies

Do not import an entire library when a small module is sufficient.

---

# 50. ANIMATION PERFORMANCE

Prefer GPU-friendly animation properties where appropriate.

Avoid expensive animations on large numbers of elements.

Do not animate layout continuously when transform/opacity can achieve the same result.

---

# 51. DEBUGGING PROCESS

When an error appears:

1. Read the complete error.
2. Identify the first meaningful failure.
3. Find the responsible file.
4. Inspect surrounding code.
5. Reproduce the issue.
6. Make the smallest correct fix.
7. Re-run relevant checks.

Do not blindly patch symptoms.

---

# 52. DEBUGGING RULE

Fix root causes.

Bad:

```text
Suppress error
Disable lint rule
Add random timeout
Ignore exception
```

Good:

```text
Understand why it fails
Fix the underlying problem
Add regression coverage
```

---

# 53. LINT

Lint warnings should not be ignored casually.

If a rule is genuinely incorrect for a specific case:

- use the narrowest suppression
- document why
- avoid disabling the rule globally

---

# 54. TYPE CHECK

Run type checks after meaningful changes.

Type errors should be fixed rather than hidden through unsafe casts.

Avoid:

```ts
as any
```

as a shortcut.

---

# 55. TESTING

Use appropriate tests for the feature.

## Unit

Use for:

- utilities
- parsers
- normalizers
- business rules

## Integration

Use for:

- API services
- database behavior
- provider adapters

## E2E

Use for:

- login
- search
- browsing
- watching
- favorites
- watchlist

---

# 56. REGRESSION TESTING

Every bug fix should consider whether a regression test is appropriate.

Especially for:

- authentication
- streaming
- database logic
- search
- user data

---

# 57. TEST NAMING

Tests should explain behavior.

Good:

```text
should reject unauthorized history access
should return normalized streaming sources
should prevent duplicate favorites
```

Avoid vague names such as:

```text
works
test1
basic test
```

---

# 58. GIT WORKFLOW

Use focused commits.

A commit should represent one logical change when practical.

Examples:

```text
feat: add donghua search filters
fix: prevent duplicate watch history
refactor: extract streaming provider adapter
style: refine poster card spacing
```

---

# 59. COMMIT HYGIENE

Do not commit:

- `.env`
- secrets
- build artifacts unless required
- debug logs
- temporary files
- personal machine configuration

---

# 60. BRANCHING

Use branches appropriate to the project's workflow.

Typical structure:

```text
main
develop
feature/*
fix/*
refactor/*
```

Follow the repository's existing convention if one already exists.

---

# 61. CODE REVIEW

Before considering a change complete, review:

- correctness
- readability
- security
- performance
- accessibility
- responsive behavior
- regression risk

---

# 62. REDESIGN DEVELOPMENT RULES

For a redesign task:

DO:

- preserve functionality
- preserve routes
- preserve data flow
- reuse working APIs
- improve hierarchy
- improve spacing
- improve typography
- improve interaction
- improve responsive behavior

DO NOT:

- rewrite backend unnecessarily
- change database unnecessarily
- remove working features
- replace working authentication without reason
- change APIs without need

---

# 63. DESIGN IMPLEMENTATION

When implementing the DONGLYN design:

- follow `design.md`
- follow `architecture.md`
- follow `security.md`
- preserve existing behavior

If documents conflict with the current repository's working contract, inspect the repository and choose the safest compatible implementation.

---

# 64. ACCESSIBILITY QA

Before completion verify:

- keyboard navigation
- focus states
- labels
- alt text
- semantic controls
- contrast
- reduced motion

---

# 65. RESPONSIVE QA

Test at minimum:

```text
Mobile
Tablet
Desktop
Large Desktop
```

Check:

- navbar
- hero/banner
- poster grids
- cards
- search
- player
- dialogs
- forms
- footer

---

# 66. BROWSER QA

Test critical flows in supported modern browsers.

At minimum consider:

- Chromium-based browsers
- Firefox
- Safari where applicable

Do not assume browser behavior is identical.

---

# 67. PRODUCTION BUILD

Before declaring a major change complete:

```text
lint
typecheck
test
build
```

All relevant checks should pass.

---

# 68. ENVIRONMENT QA

Verify development and production configurations separately.

Do not accidentally depend on:

- local-only files
- localhost URLs
- development secrets
- debug flags
- local databases

---

# 69. DEPLOYMENT CHECK

Before production deployment verify:

- environment variables
- database connection
- API URLs
- CAPTCHA configuration
- security headers
- CORS
- authentication
- streaming providers
- error monitoring

---

# 70. DOCUMENTATION

Document non-obvious decisions.

Useful documentation includes:

- architecture
- security
- setup
- environment variables
- deployment
- provider integration
- migration instructions

Avoid documenting obvious code line-by-line.

---

# 71. COMMENTS

Comments should explain WHY, not WHAT.

Bad:

```ts
// Set loading to true
setLoading(true)
```

Good:

```ts
// Prevent duplicate submissions while the provider request is running.
setLoading(true)
```

---

# 72. TODO POLICY

TODOs should be meaningful.

Bad:

```text
// TODO fix this
```

Good:

```text
// TODO: Replace temporary provider fallback after Provider B migration.
```

Avoid leaving vague TODOs indefinitely.

---

# 73. TEMPORARY CODE

Temporary solutions must be obvious.

If a workaround is necessary:

- isolate it
- document it
- define the intended replacement
- avoid spreading it across the codebase

---

# 74. FEATURE DEVELOPMENT

For larger features:

```text
Requirement
 ↓
Architecture
 ↓
Data model
 ↓
API
 ↓
Service
 ↓
UI
 ↓
Tests
 ↓
QA
```

Do not build UI first and discover data requirements afterward unless the task specifically calls for a visual prototype.

---

# 75. MIGRATION STRATEGY

For major refactors:

```text
Existing
   ↓
Introduce new abstraction
   ↓
Migrate consumers
   ↓
Test
   ↓
Remove old implementation
```

Avoid big-bang rewrites when incremental migration is possible.

---

# 76. FEATURE FLAGS

Use feature flags for risky or experimental changes when appropriate.

Examples:

- new player
- new recommendation system
- redesigned search
- new authentication flow

---

# 77. SECURITY DEVELOPMENT

Follow `security.md`.

Never weaken security simply to make development easier.

Local development may use test credentials and test providers, but production security behavior must remain explicit.

---

# 78. PERFORMANCE REGRESSION

Major UI changes should not introduce obvious:

- bundle growth
- image bloat
- unnecessary API calls
- layout shift
- animation lag

Measure when a change is performance-sensitive.

---

# 79. ERROR BOUNDARIES

A failure in one secondary feature should not necessarily crash the entire application.

Where supported, isolate critical feature failures.

Example:

```text
Home
 ├── Hero
 ├── Trending
 ├── Latest
 └── Recommendations
```

If Recommendations fail, the rest should remain usable.

---

# 80. QUALITY BAR

DONGLYN should feel like a finished product.

Avoid shipping:

- placeholder UI
- broken animations
- inconsistent spacing
- random icons
- missing loading states
- unexplained errors
- obvious console errors
- inaccessible controls

---

# 81. DEVELOPMENT ANTI-PATTERNS

Never:

- rewrite everything without need
- ignore existing architecture
- bypass validation
- disable security controls casually
- suppress errors blindly
- use `any` everywhere
- duplicate API logic
- duplicate UI unnecessarily
- add dependencies for trivial problems
- ship broken builds
- leave debug code in production
- hardcode secrets
- break existing routes accidentally

---

# 82. DEFINITION OF DONE

A feature is done when:

- functionality works
- UI matches the design system
- responsive behavior works
- accessibility is considered
- loading state exists
- error state exists
- empty state exists where relevant
- security requirements are satisfied
- type checks pass
- lint passes
- tests pass
- production build passes
- existing functionality remains intact

---

# 83. FINAL DEVELOPMENT CHECKLIST

Before finalizing:

## Code

- [ ] Clean implementation
- [ ] No unnecessary duplication
- [ ] Types are safe
- [ ] No debug code

## UI

- [ ] DONGLYN design language
- [ ] Responsive
- [ ] Accessible
- [ ] Loading states
- [ ] Error states
- [ ] Empty states
- [ ] Lucide Animated used appropriately

## Backend

- [ ] Validation
- [ ] Authentication
- [ ] Authorization
- [ ] Rate limiting where appropriate
- [ ] Safe errors

## Data

- [ ] Efficient queries
- [ ] Correct migrations
- [ ] No unnecessary data exposure

## Security

- [ ] No secrets exposed
- [ ] CAPTCHA verified server-side
- [ ] Secure sessions
- [ ] Input validation
- [ ] Ownership checks

## Quality

- [ ] Lint passes
- [ ] Typecheck passes
- [ ] Tests pass
- [ ] Build passes

---

# 84. FINAL PRINCIPLE

Build DONGLYN like a product that will still be maintained years from now.

Prefer:

```text
Simple
+
Clean
+
Secure
+
Tested
+
Consistent
```

over:

```text
Fast hack
+
Random abstraction
+
Dependency bloat
+
Technical debt
```

Every implementation should make the next implementation easier.

---

# 85. DONGLYN DEVELOPMENT NORTH STAR

The code should be:

CLEAN

The UI should be:

PREMIUM

The architecture should be:

SCALABLE

The security should be:

STRONG

The experience should be:

FAST

And the result should feel:

POLISHED.
