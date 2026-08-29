# DONGLYN — ARCHITECTURE & ENGINEERING GUIDELINES

> Official technical architecture specification for DONGLYN.
>
> This document defines the application's structural principles,
> technology boundaries, data flow, modularity, API organization,
> frontend architecture, backend architecture, state management,
> integration rules, performance expectations, and scalability strategy.
>
> This document is the architectural source of truth.
> Implementation decisions MUST follow these principles unless
> a deliberate exception is documented.

---

# 1. ARCHITECTURE NORTH STAR

DONGLYN should be:

- Modular
- Maintainable
- Scalable
- Secure
- Performant
- Type-safe
- Easy to debug
- Easy to extend
- Production-ready

The architecture must support the current streaming experience while leaving room for future features without requiring a complete rewrite.

---

# 2. ARCHITECTURAL PRINCIPLES

## 2.1 Separation of Concerns

Keep responsibilities separated.

UI should handle:

- presentation
- interaction
- user experience

Application logic should handle:

- business rules
- workflows
- orchestration

API layer should handle:

- HTTP
- authentication
- validation
- serialization

Database layer should handle:

- persistence
- queries
- transactions

External integrations should remain isolated behind service abstractions.

---

## 2.2 Single Responsibility

A module, component, service, or function should have one clear responsibility.

Avoid:

- giant components
- giant API handlers
- giant service files
- duplicated business logic
- mixed database and UI logic

---

## 2.3 Reusability

Prefer reusable modules over duplication.

If the same behavior exists in multiple places, extract a shared abstraction when doing so improves clarity.

Do not over-engineer trivial code.

---

## 2.4 Type Safety

Use TypeScript consistently wherever TypeScript is part of the project.

Avoid:

```ts
any
```

unless there is a documented technical reason.

Prefer:

- explicit types
- interfaces
- schemas
- inferred types where appropriate
- discriminated unions
- strict compiler settings

---

## 2.5 API-First Thinking

The frontend must not directly depend on database implementation details.

Use an API/service boundary.

The UI should consume application data through defined contracts.

---

# 3. RECOMMENDED HIGH-LEVEL STRUCTURE

The application should conceptually follow:

```text
┌─────────────────────────────────────────────┐
│                  DONGLYN UI                 │
│                                             │
│  Pages / Layouts / Components / Player      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              APPLICATION LAYER              │
│                                             │
│ Search / Discovery / Watch / Auth / Profile │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                 API LAYER                   │
│                                             │
│ REST / Server Actions / Route Handlers      │
└──────────────────────┬──────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
┌─────────────────────┐ ┌─────────────────────┐
│    DATA SERVICES    │ │ EXTERNAL SERVICES   │
│                     │ │                     │
│ Database / Cache    │ │ CAPTCHA / Storage   │
│ Search / History    │ │ Streaming Sources   │
└─────────────────────┘ └─────────────────────┘
```

The exact implementation may differ based on the existing repository, but the responsibility boundaries must remain clear.

---

# 4. FRONTEND ARCHITECTURE

DONGLYN should use a modern component-based frontend architecture.

Preferred principles:

- route-based organization
- reusable components
- server-first rendering where supported
- client components only when interaction requires them
- shared UI primitives
- feature-oriented organization

Do not turn the entire application into client-side JavaScript unnecessarily.

---

# 5. FRONTEND LAYERS

Conceptually:

```text
Presentation
    ↓
Feature Components
    ↓
Application Services
    ↓
API Client
    ↓
Backend
```

---

# 6. PAGE / ROUTE RESPONSIBILITIES

Pages and route-level components should primarily:

- compose sections
- load required data
- define page structure
- coordinate feature components

Avoid placing large business logic directly inside page files.

---

# 7. COMPONENT ARCHITECTURE

Components should be divided into:

## Primitive Components

Examples:

- Button
- Input
- Badge
- Dialog
- Dropdown
- Tabs
- Tooltip
- Skeleton

## Shared Components

Examples:

- Navbar
- Footer
- Search
- PosterCard
- SectionHeader
- EpisodeSelector

## Feature Components

Examples:

- TrendingSection
- ContinueWatching
- DonghuaDetail
- WatchHistory
- FavoriteList
- StreamingPlayer

## Page Components

Examples:

- HomePage
- BrowsePage
- SearchPage
- DetailPage
- WatchPage
- ProfilePage

Keep these layers distinguishable.

---

# 8. FEATURE-BASED ORGANIZATION

When the project grows, prefer feature-oriented modules.

Example:

```text
src/
├── app/
├── components/
├── features/
│   ├── auth/
│   ├── browse/
│   ├── search/
│   ├── donghua/
│   ├── watch/
│   ├── history/
│   ├── favorites/
│   └── profile/
├── lib/
├── services/
├── hooks/
├── types/
└── utils/
```

The exact directory names may adapt to the framework already used by the repository.

Do not restructure the entire project unnecessarily if the existing architecture is already healthy.

---

# 9. API CLIENT

Frontend API communication should be centralized.

Avoid scattering raw `fetch()` calls across dozens of components.

Prefer:

```text
Component
   ↓
Feature Hook / Service
   ↓
API Client
   ↓
Endpoint
```

This provides:

- consistent error handling
- consistent headers
- easier authentication
- easier testing
- easier API migration

---

# 10. DATA FETCHING

Choose data fetching based on the type of content.

## Static / Slow-Changing Content

Prefer server-side or cached fetching where possible.

Examples:

- genres
- static metadata
- popular content

## Frequently Changing Content

Use appropriate revalidation or client fetching.

Examples:

- latest episodes
- trending content
- watch progress

## User-Specific Content

Fetch using authenticated context.

Examples:

- history
- favorites
- watchlist
- profile

---

# 11. CACHING

Caching should be intentional.

Good candidates:

- genres
- donghua metadata
- popular content
- static configuration

Avoid caching sensitive user-specific data globally.

Never allow one user's private data to leak through shared caching.

---

# 12. STATE MANAGEMENT

Do not introduce a global state library unless there is a real requirement.

Prefer:

1. Server state
2. URL state
3. Local component state
4. Context for genuinely global state
5. Global state library only when justified

Examples:

URL state:

- search query
- filters
- page
- genre

Local state:

- modal open
- dropdown state
- player controls

User session:

- authentication context / framework session

---

# 13. URL STATE

Search and browse state should be shareable through URLs when appropriate.

Examples:

```text
/search?q=...
/donghua?genre=action
/browse?page=2
```

Do not store navigational state only in local component state when a URL representation is useful.

---

# 14. BACKEND ARCHITECTURE

The backend should follow clear layers.

Recommended:

```text
Route / Controller
        ↓
Validation
        ↓
Application Service
        ↓
Repository / Data Service
        ↓
Database
```

External integrations:

```text
Application Service
        ↓
Integration Adapter
        ↓
External Provider
```

---

# 15. API DESIGN

Use predictable REST conventions where REST is used.

Example:

```text
GET    /api/donghua
GET    /api/donghua/:id
GET    /api/donghua/:id/episodes

GET    /api/search
GET    /api/genres

GET    /api/me
GET    /api/me/history
POST   /api/me/history

GET    /api/me/favorites
POST   /api/me/favorites
DELETE /api/me/favorites/:id

GET    /api/me/watchlist
POST   /api/me/watchlist
DELETE /api/me/watchlist/:id
```

Exact routes must follow the existing project contract if already established.

Do not break existing public APIs without a migration plan.

---

# 16. API RESPONSE FORMAT

Responses should be predictable.

Successful response example:

```json
{
  "data": {},
  "meta": {}
}
```

Error example:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Donghua tidak ditemukan."
  }
}
```

Do not expose internal stack traces to clients.

---

# 17. VALIDATION

Every external input must be validated.

Validate:

- query parameters
- route parameters
- request bodies
- authentication data
- filters
- pagination
- IDs

Use schema-based validation where appropriate.

Never trust client-side validation alone.

---

# 18. DATABASE ARCHITECTURE

Database access should remain isolated from UI and route handlers.

Prefer:

```text
API
 ↓
Service
 ↓
Repository / ORM
 ↓
Database
```

Avoid direct database queries inside UI components.

---

# 19. DATA MODEL CONCEPT

Core entities may include:

```text
User
Donghua
Episode
Genre
DonghuaGenre
WatchHistory
Favorite
Watchlist
StreamingSource
```

Additional entities may be introduced as the product evolves.

Do not create unnecessary tables without a clear domain requirement.

---

# 20. RELATIONSHIPS

Conceptually:

```text
User
 ├── WatchHistory
 ├── Favorite
 └── Watchlist

Donghua
 ├── Episodes
 ├── Genres
 └── StreamingSources

Episode
 └── StreamingSources
```

Keep relational ownership clear.

---

# 21. IDENTIFIERS

Use stable identifiers.

Do not expose sensitive internal database identifiers unnecessarily.

Public IDs should be treated as part of the API contract.

---

# 22. WATCH HISTORY

Watch history should be designed around:

- user
- donghua
- episode
- progress
- last watched timestamp

The system should support efficient retrieval of recent activity.

---

# 23. FAVORITES

Favorites represent explicit user preference.

Operations should be idempotent where appropriate.

Example:

Adding an already-existing favorite should not create duplicate records.

---

# 24. WATCHLIST

Watchlist follows the same principle.

Avoid duplicate records.

---

# 25. STREAMING ARCHITECTURE

The streaming player should not need to understand internal scraping or provider logic.

Use:

```text
Player
  ↓
Episode API
  ↓
Streaming Service
  ↓
Provider Adapter
  ↓
External Source
```

This allows providers to change without rewriting the player.

---

# 26. STREAMING PROVIDER ABSTRACTION

Use an adapter pattern when multiple providers exist.

Conceptually:

```ts
interface StreamingProvider {
  getSources(episodeId: string): Promise<StreamingSource[]>
}
```

Possible adapters:

```text
ProviderA
ProviderB
ProviderC
```

The player consumes normalized data rather than provider-specific responses.

---

# 27. NORMALIZED STREAMING SOURCE

A normalized streaming source may contain:

```ts
type StreamingSource = {
  id: string
  url: string
  quality?: string
  type?: string
  server?: string
  subtitles?: SubtitleTrack[]
}
```

Keep provider-specific fields isolated.

---

# 28. SCRAPING / CONTENT INGESTION

If DONGLYN uses external scraping or content ingestion:

DO NOT place scraping logic directly inside frontend code.

Use a backend service or worker.

Recommended:

```text
Scheduler / Trigger
        ↓
Ingestion Service
        ↓
Provider Adapter
        ↓
Parser / Normalizer
        ↓
Database
```

---

# 29. CONTENT NORMALIZATION

External provider data should be normalized before entering the application domain.

External:

```text
Provider-specific format
```

↓

Normalizer

↓

Internal:

```text
Donghua
Episode
Genre
StreamingSource
```

This prevents provider-specific structures from leaking throughout the codebase.

---

# 30. SEARCH ARCHITECTURE

Search should use a dedicated service boundary.

Conceptually:

```text
Search UI
   ↓
Search API
   ↓
Search Service
   ↓
Database / Search Index
```

Do not couple the UI to database-specific search syntax.

---

# 31. SEARCH FILTERS

Potential filters:

- genre
- status
- year
- type
- rating
- release state

Filters should be represented as validated query parameters.

---

# 32. PAGINATION

Large datasets must not be loaded entirely into the browser.

Use pagination or cursor-based retrieval.

The implementation should prioritize performance and predictable navigation.

---

# 33. AUTHENTICATION ARCHITECTURE

Authentication must remain separate from general content logic.

Conceptually:

```text
Client
 ↓
Auth Layer
 ↓
Session / Token
 ↓
User Context
 ↓
Application Services
```

Do not duplicate authentication checks throughout every component manually.

---

# 34. AUTHORIZATION

Authentication answers:

"Who is this?"

Authorization answers:

"What may this user do?"

Keep these concepts separate.

Protected operations include:

- profile access
- history
- favorites
- watchlist
- account settings

---

# 35. CAPTCHA INTEGRATION

DONGLYN may use:

- Cloudflare challenge on entry/security-sensitive flows
- hCaptcha where configured

Captcha verification must happen server-side.

Never trust a CAPTCHA result supplied only by the browser.

The backend should verify the token with the appropriate provider before accepting the protected operation.

---

# 36. EXTERNAL SERVICE ADAPTERS

External integrations should be isolated.

Examples:

```text
services/
├── captcha/
├── email/
├── storage/
├── streaming/
└── analytics/
```

Do not scatter provider-specific SDK calls throughout application code.

---

# 37. ERROR HANDLING

Errors should be categorized.

Example:

```text
ValidationError
AuthenticationError
AuthorizationError
NotFoundError
ConflictError
RateLimitError
ExternalServiceError
InternalServerError
```

Convert internal errors into safe public responses.

---

# 38. LOGGING

Use structured logging.

Logs should help diagnose:

- API failures
- provider failures
- authentication events
- ingestion failures
- database failures
- unexpected exceptions

Never log:

- passwords
- tokens
- session secrets
- CAPTCHA secrets
- private credentials

---

# 39. OBSERVABILITY

Production architecture should leave room for:

- error monitoring
- performance monitoring
- structured logs
- request tracing
- health checks

Do not expose internal observability data publicly.

---

# 40. HEALTH CHECKS

Backend services should expose an appropriate health mechanism.

Example:

```text
GET /api/health
```

Health checks may verify:

- application status
- database connectivity
- critical dependencies

Do not expose sensitive infrastructure details.

---

# 41. RATE LIMITING

Rate limits should exist around sensitive or expensive operations.

Examples:

- authentication
- search abuse
- scraping triggers
- API-heavy endpoints
- CAPTCHA verification
- account actions

Limits should be appropriate to the endpoint.

---

# 42. ASYNCHRONOUS WORK

Long-running tasks should not block normal user requests.

Examples:

- content ingestion
- scraping
- metadata synchronization
- heavy processing
- notifications

Use background workers or queues where appropriate.

---

# 43. JOB ARCHITECTURE

Conceptually:

```text
Trigger
  ↓
Queue
  ↓
Worker
  ↓
Task
  ↓
Database
```

Jobs should be:

- retryable
- observable
- idempotent when possible

---

# 44. CONFIGURATION

Environment-specific values must use environment variables or secure configuration.

Never hardcode:

- database credentials
- API keys
- CAPTCHA secrets
- signing secrets
- provider credentials

Provide an `.env.example` with safe placeholders.

---

# 45. ENVIRONMENT SEPARATION

Support:

```text
development
test
production
```

Do not use production credentials in local development.

---

# 46. API CONTRACTS

API contracts should be treated as stable interfaces.

Changes should consider:

- backward compatibility
- frontend consumers
- external clients
- migration requirements

Avoid breaking changes without a deliberate migration.

---

# 47. TYPES SHARING

Where practical, shared domain types may be placed in a shared package/module.

Example:

```text
packages/
└── types/
```

Avoid duplicating identical API types across frontend and backend.

---

# 48. DOMAIN TYPES

Domain types should describe business concepts rather than database implementation details.

Prefer:

```ts
Donghua
Episode
WatchHistory
StreamingSource
```

rather than exposing ORM-generated structures everywhere.

---

# 49. FRONTEND / BACKEND BOUNDARY

Frontend should receive only the data it needs.

Do not return:

- internal provider credentials
- internal database fields
- private operational metadata
- secrets
- unnecessary backend implementation details

---

# 50. FILE UPLOADS / MEDIA

If the application later supports user uploads:

- store media outside the application server when appropriate
- validate file type
- validate file size
- generate safe filenames
- prevent arbitrary execution
- isolate public and private assets

---

# 51. STATIC ASSETS

Static assets should be optimized.

Prefer:

- compressed images
- modern image formats
- responsive sizes
- lazy loading
- CDN delivery where appropriate

Large assets should not block initial rendering.

---

# 52. PERFORMANCE ARCHITECTURE

Priorities:

1. Fast initial render
2. Low JavaScript overhead
3. Optimized images
4. Efficient API requests
5. Caching
6. Minimal layout shift
7. Smooth playback

Do not optimize prematurely at the cost of maintainability.

---

# 53. RENDERING STRATEGY

Use the framework's strengths.

Prefer server rendering for:

- content pages
- SEO-sensitive pages
- metadata-heavy pages

Use client rendering for:

- interactive player controls
- dynamic filters
- interactive menus
- user-specific interactions

Do not make every page fully client-rendered by default.

---

# 54. SEO ARCHITECTURE

Public content pages should be indexable where appropriate.

Important pages:

- Home
- Browse
- Genre
- Donghua detail

Potential metadata:

- title
- description
- canonical URL
- Open Graph
- Twitter/X metadata

---

# 55. SEO CONTENT

Each Donghua detail page should have meaningful metadata.

Avoid duplicate generic descriptions across every page.

---

# 56. ROUTING PRINCIPLES

Routes should be:

- predictable
- readable
- stable
- semantic

Examples:

```text
/
 /donghua
 /donghua/[slug]
 /donghua/[slug]/watch/[episode]
 /genre/[slug]
 /search
 /profile
```

Exact route structure must follow the existing application where already established.

---

# 57. SLUGS

Public content pages should prefer readable slugs when appropriate.

Example:

```text
/donghua/renegade-immortal
```

Slugs should be stable.

---

# 58. SECURITY BOUNDARY

Architecture must assume:

```text
Everything from the browser can be manipulated.
```

Never trust:

- client state
- hidden fields
- localStorage
- query parameters
- browser-only authorization
- CAPTCHA claims without server verification

All sensitive decisions happen server-side.

---

# 59. DEPENDENCY MANAGEMENT

Before adding a dependency, ask:

1. Do we really need it?
2. Can existing dependencies solve the problem?
3. Is it maintained?
4. Does it add significant bundle size?
5. Does it introduce security concerns?

Avoid dependency bloat.

---

# 60. CODE ORGANIZATION RULE

Do not create:

- giant utility files
- giant component files
- generic "helpers" dumping grounds
- circular dependencies

Prefer focused modules.

---

# 61. DEPENDENCY DIRECTION

Preferred direction:

```text
UI
 ↓
Features
 ↓
Services
 ↓
Infrastructure
```

Lower-level infrastructure should not import high-level UI modules.

Avoid circular dependency graphs.

---

# 62. TESTING ARCHITECTURE

Test at multiple levels.

## Unit Tests

Test:

- utilities
- parsers
- normalizers
- business rules

## Integration Tests

Test:

- services
- database interactions
- API behavior

## End-to-End Tests

Test critical flows:

- authentication
- search
- browsing
- watching
- favorites
- watchlist

---

# 63. TEST PRIORITY

Highest priority:

1. Authentication
2. Streaming flow
3. Search
4. User data
5. Content ingestion
6. Critical API endpoints

---

# 64. MIGRATIONS

Database schema changes must use migrations.

Never manually modify production schemas without a controlled migration process.

Every migration should be reviewable and reproducible.

---

# 65. BACKUP STRATEGY

Production data should have a backup strategy.

At minimum consider:

- scheduled database backups
- retention
- restore testing
- backup monitoring

A backup is only useful if it can actually be restored.

---

# 66. DEPLOYMENT ARCHITECTURE

A production deployment should conceptually separate:

```text
CDN / Reverse Proxy
        ↓
Frontend / Application
        ↓
Backend Services
        ↓
Database
```

External providers remain behind application service boundaries.

---

# 67. SCALABILITY

Design for horizontal growth where practical.

Potential future architecture:

```text
             ┌──────────────┐
             │     CDN      │
             └──────┬───────┘
                    │
             ┌──────▼───────┐
             │ Load Balancer│
             └──────┬───────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     App #1      App #2      App #3
        │           │           │
        └───────────┼───────────┘
                    ▼
               Cache / DB
```

Do not prematurely deploy complex infrastructure before it is necessary.

---

# 68. CACHE STRATEGY

Potential cache layers:

```text
Browser Cache
      ↓
CDN Cache
      ↓
Application Cache
      ↓
Database
```

Cache only data that is safe and useful to cache.

---

# 69. DATABASE PERFORMANCE

Use:

- appropriate indexes
- pagination
- selective queries
- connection pooling
- efficient joins
- query monitoring

Avoid fetching huge datasets when only a small subset is needed.

---

# 70. N+1 PREVENTION

Be aware of N+1 query patterns.

When loading:

```text
Donghua
 └── Episodes
```

do not accidentally execute one database query per Donghua when a batched query is appropriate.

---

# 71. CONCURRENCY

Operations that can race must be designed safely.

Examples:

- favorite creation
- watch history updates
- ingestion
- synchronization

Use:

- unique constraints
- transactions
- idempotency
- proper locking where necessary

---

# 72. IDEMPOTENCY

Operations such as:

```text
Add Favorite
Add Watchlist
Sync Episode
Update Watch Progress
```

should be designed to tolerate retries where practical.

---

# 73. STREAMING RESILIENCE

External streaming providers may fail.

The architecture should support:

- provider fallback
- retry
- timeout
- graceful errors
- server switching

Do not allow one provider failure to crash the entire application.

---

# 74. TIMEOUTS

External requests must have sensible timeouts.

Never allow an external provider to hold a request indefinitely.

---

# 75. RETRIES

Retry only operations where retrying is safe.

Use:

- bounded retries
- exponential backoff where appropriate
- clear failure states

Do not endlessly retry failing providers.

---

# 76. FRONTEND ERROR BOUNDARIES

Critical UI sections should fail gracefully.

A broken recommendation section should not crash the entire homepage.

Use error boundaries or equivalent mechanisms where supported.

---

# 77. FEATURE FLAGS

Future experimental features may use feature flags.

Examples:

- new player
- new recommendation engine
- new search experience

Do not hardcode experimental behavior throughout the codebase.

---

# 78. LOGICAL MODULES

Recommended domains:

```text
auth
users
donghua
episodes
genres
search
streaming
history
favorites
watchlist
captcha
```

Each domain should own its business logic.

---

# 79. ARCHITECTURAL ANTI-PATTERNS

Never introduce:

- database calls inside UI components
- provider-specific streaming logic inside the player
- duplicated authentication logic
- secrets in frontend code
- giant route handlers
- giant components
- random global state
- unnecessary microservices
- unnecessary dependencies
- uncontrolled client-side fetching
- direct external API calls from random components
- circular dependencies

---

# 80. WHEN TO CREATE A SERVICE

Create a service when logic:

- is reused
- contains business rules
- communicates with an external provider
- coordinates multiple repositories
- needs independent testing

Do not create a service for every two-line function.

---

# 81. WHEN TO CREATE A COMPONENT

Create a component when:

- UI is reused
- UI has meaningful internal behavior
- UI represents a domain concept
- extraction improves readability

Avoid splitting every tiny HTML fragment into a component.

---

# 82. WHEN TO CREATE A HOOK

Create a hook when stateful client behavior is reused.

Examples:

- useSearch
- useWatchProgress
- usePlayer
- useDebounce

Do not create hooks simply to wrap one trivial statement.

---

# 83. ARCHITECTURAL CHANGE PROCESS

Before making a major architectural change:

1. Inspect the current repository.
2. Understand existing conventions.
3. Identify dependencies.
4. Identify affected modules.
5. Define migration impact.
6. Implement incrementally.
7. Run tests.
8. Run type checks.
9. Run lint.
10. Verify production build.

Never rewrite working architecture without a clear reason.

---

# 84. BACKWARD COMPATIBILITY

Existing functionality must be preserved unless the task explicitly requires a breaking change.

Before modifying a shared component or API:

- find all consumers
- understand current behavior
- update dependent tests
- verify critical flows

---

# 85. REFACTORING RULE

Prefer incremental refactoring.

Bad:

```text
Delete everything
Rewrite everything
Hope it works
```

Good:

```text
Understand
↓
Extract
↓
Migrate
↓
Test
↓
Remove old code
```

---

# 86. DEFINITION OF DONE

A feature is not architecturally complete until:

- implementation works
- types pass
- lint passes
- tests pass
- production build passes
- error states exist
- loading states exist
- responsive behavior works
- security boundaries are respected
- existing functionality remains intact

---

# 87. ARCHITECTURE QA CHECKLIST

Before merging major changes:

## Structure

- Are responsibilities separated?
- Are modules focused?
- Are dependencies directional?

## API

- Are inputs validated?
- Are responses consistent?
- Are errors safe?

## Database

- Are queries efficient?
- Are indexes appropriate?
- Are migrations included?

## Security

- Are secrets protected?
- Is server-side authorization enforced?
- Is external input validated?

## Performance

- Is unnecessary client JavaScript avoided?
- Are images optimized?
- Is caching appropriate?

## Reliability

- Are external services protected by timeout?
- Are retries safe?
- Are provider failures handled?

## Testing

- Are critical flows covered?
- Do unit tests pass?
- Do integration tests pass?
- Does the production build pass?

---

# 88. FINAL ARCHITECTURE PRINCIPLE

DONGLYN should remain simple internally even when the product becomes complex externally.

Complexity belongs behind clear boundaries.

The user should experience:

FAST
+
SIMPLE
+
RELIABLE

while the architecture provides:

MODULARITY
+
SECURITY
+
SCALABILITY
+
OBSERVABILITY

---

# 89. DONGLYN ARCHITECTURE NORTH STAR

Build the smallest architecture that can support the product correctly.

Do not build infrastructure for hypothetical problems.

Do not sacrifice maintainability for premature optimization.

Do not sacrifice security for convenience.

Do not sacrifice UX for technical purity.

Do not sacrifice performance for unnecessary abstraction.

The architecture exists to serve DONGLYN.

DONGLYN is a streaming product first.

The codebase should make that obvious.
