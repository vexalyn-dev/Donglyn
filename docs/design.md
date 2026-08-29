# DONGLYN — DESIGN SYSTEM & UI/UX GUIDELINES

> Official visual and UX specification for DONGLYN.
>
> This document is the single source of truth for the visual identity,
> UI/UX principles, design system, typography, colors, components,
> motion, responsive behavior, accessibility, and interaction patterns.
>
> Every frontend implementation MUST follow this document unless
> a deliberate design decision is explicitly documented.

---

# 1. PRODUCT DESIGN DIRECTION

## Brand

DONGLYN

## Product

DONGLYN is a premium Donghua streaming platform focused on:

- Donghua discovery
- Donghua browsing
- Search
- Genres
- Trending content
- Latest releases
- Donghua details
- Episode streaming
- Continue watching
- Watch history
- Favorites
- Watchlist
- User accounts

# 2. DESIGN NORTH STAR

DONGLYN must feel:

- Premium
- Cinematic
- Modern
- Elegant
- Dark
- Clean
- Sophisticated
- Powerful
- Fast
- Comfortable

The interface should communicate:

> "A premium place to discover and watch Donghua."

DONGLYN must NOT look like:

- A generic anime website
- A generic SaaS dashboard
- An AI-generated template
- An esports website
- A cheap streaming template

The final visual identity must feel unique to DONGLYN.

# 3. CORE DESIGN PHILOSOPHY

## 3.1 Content First

Donghua artwork is the primary visual content.

The interface exists to support discovery, navigation, playback, organization, and interaction.

UI must never compete with the artwork.

## 3.2 Clarity Over Decoration

Every visual element must have a purpose.

Avoid decorative elements that do not improve usability, hierarchy, navigation, branding, or feedback.

## 3.3 Premium Through Restraint

Premium does NOT mean excessive glow, gradients, glassmorphism, rounded cards, animations, or borders.

Premium means:

- excellent spacing
- strong typography
- high-quality imagery
- precise alignment
- consistent components
- subtle interactions
- thoughtful hierarchy

## 3.4 Motion With Purpose

Animation should communicate interaction, state, navigation, feedback, or hierarchy.

Do not animate something simply because it can be animated.

## 3.5 Mobile Is First-Class

Mobile must not feel like a compressed desktop version.

Mobile layouts must be intentionally designed.

# 4. VISUAL IDENTITY

Primary visual formula:

BLACK FOUNDATION
+
WHITE TYPOGRAPHY
+
CRIMSON ACCENTS
+
CINEMATIC DONGHUA ARTWORK
+
SUBTLE RED LIGHT
+
PREMIUM SPACING
+
SMOOTH MICRO-INTERACTIONS

# 5. COLOR SYSTEM

## 5.1 Background Colors

Background Primary: `#050505`
Background Secondary: `#070707`
Background Tertiary: `#090909`

Use these for the application background, secondary sections, grouped content, and subtle visual separation.

## 5.2 Surface Colors

Surface: `#0D0D0D`
Surface Elevated: `#101010`
Surface Higher: `#151515`
Surface Highest: `#181818`

Use for cards, panels, controls, dropdowns, menus, modals, and elevated UI.

## 5.3 Brand Colors

Primary Crimson: `#E50914`
Bright Crimson: `#FF1A24`
Deep Crimson: `#8B0000`
Dark Crimson: `#5C0000`

Primary crimson is the main DONGLYN action color.

Use crimson for primary buttons, active states, progress indicators, important badges, selected controls, and important interaction states.

## 5.4 Text Colors

Primary Text: `#F5F5F5`
Secondary Text: `#A1A1AA`
Muted Text: `#71717A`
Disabled Text: `#52525B`

## 5.5 Borders

Default Border: `rgba(255,255,255,0.06)`
Strong Border: `rgba(255,255,255,0.10)`
Active Border: `rgba(229,9,20,0.35)`

## 5.6 Glow

Crimson Glow: `rgba(229,9,20,0.15)`

Use only for hero lighting, primary CTA emphasis, active interaction, and important focus states.

DO NOT use crimson glow on every card.

# 6. COLOR USAGE RULE

BLACK = foundation

WHITE = hierarchy

GRAY = supporting information

CRIMSON = identity + action

Artwork = visual personality

Do not make every card, border, or text element red. Red is an accent, not the entire interface.

# 7. TYPOGRAPHY

Primary font:

- Inter

Alternatives:

- Geist
- Manrope

Use one primary UI font consistently.

Recommended hierarchy:

Display: large, bold, cinematic
H1: 32–48px / 700
H2: 24–32px / 700
H3: 18–24px / 600
Body: 14–16px / 1.5–1.7
Metadata: 12–14px

Avoid excessive font weights, excessive uppercase, giant text everywhere, and extremely tight line-height.

# 8. SPACING SYSTEM

Use:

- 4px
- 8px
- 12px
- 16px
- 24px
- 32px
- 48px
- 64px
- 80px

Do not introduce random spacing values unless required.

# 9. CONTAINER SYSTEM

Desktop maximum content width:

1280–1600px

Mobile horizontal padding:

16px

Desktop horizontal padding:

24–40px depending on viewport.

# 10. BORDER RADIUS

Small: 8px
Medium: 12px
Large: 16px
XL: 20px

Use restrained modern rounding. Avoid unnecessary pill-shaped interfaces.

# 11. SHADOW SYSTEM

Shadows should be subtle.

Cards: soft, low-intensity shadow.
Modals: medium, soft elevated shadow.
Hero: cinematic, subtle depth.

Avoid harsh, giant, or colored shadows everywhere.

# 12. ICON SYSTEM

## PRIMARY ICON LIBRARY

DONGLYN MUST USE:

**Lucide Animated**

Official website:

https://lucide-animated.com/

Lucide Animated is the primary icon system for the application.

Do not randomly mix icon libraries.

Avoid Font Awesome, Bootstrap Icons, Heroicons, random SVG icon packs, or emoji icons when a suitable Lucide Animated icon exists.

## ICONS

Use Lucide Animated for:

- Search
- Menu
- X
- Play
- Pause
- Volume
- VolumeX
- Fullscreen
- Settings
- Heart
- Bookmark
- History
- User
- LogIn
- LogOut
- Filter
- Plus
- Check
- Info
- Star
- Monitor
- Smartphone
- Download
- Share
- RefreshCw
- Home
- Film
- ChevronDown
- ChevronUp
- ChevronLeft
- ChevronRight
- ArrowRight
- ArrowLeft
- MoreHorizontal
- Eye
- Lock
- Mail
- Bell
- Sliders
- Shield
- ShieldCheck

Always choose icons based on semantic meaning.

## ICON SIZES

Small: 16px
Normal: 18–20px
Large: 20–24px
Hero: 24–32px

Icon-only buttons MUST have accessible labels.

# 13. ICON ANIMATION

Animated icons should primarily react to:

- hover
- click
- focus
- open
- close
- active
- loading
- success

Do not continuously animate icons.

# 14. MOTION SYSTEM

Motion should feel:

- smooth
- subtle
- responsive
- premium

Micro: 150–200ms
Component: 200–300ms
Modal: 250–400ms
Page: 250–500ms

Prefer opacity, transform, scale, translate, and subtle blur.

Avoid expensive animation whenever possible.

## CARD MOTION

Poster hover:

- scale 1.02–1.04
- subtle image zoom
- dark overlay
- play button reveal
- subtle elevation
- minimal crimson ambient glow

## BUTTON MOTION

Button hover may use subtle brightness, elevation, icon movement, or slight transform.

Avoid bouncing or aggressive scaling.

## NAVIGATION MOTION

Drawer: slide + fade
Dropdown: fade + slight translate
Modal: fade + scale
Page: fade + subtle translate

## REDUCED MOTION

Always respect `prefers-reduced-motion`.

# 15. NAVBAR

Desktop:

DONGLYN

Home
Donghua
Genre
Schedule

Search
Login/Profile

Initial state:

- dark transparency
- subtle blur
- minimal border

Scrolled state:

- darker surface
- higher opacity
- subtle backdrop blur
- subtle border
- subtle shadow

Active navigation:

- white text
- subtle crimson indicator

Do not use oversized red navigation elements.

## MOBILE NAVBAR

DONGLYN
Search
Menu

Menu opens a premium navigation drawer containing:

- Home
- Donghua
- Genre
- Schedule
- History
- Favorites
- Profile

Use Lucide Animated Menu and X.

# 16. HERO BANNER

The hero is the most cinematic part of DONGLYN.

Use:

- Donglyn branding
- Donghua artwork
- black
- crimson
- cinematic lighting

Treatment:

- dark gradient
- vignette
- subtle red ambient lighting
- readable text overlay

Do not excessively blur artwork.

Recommended:

TITLE

Description

[ PLAY ] Mulai Streaming
[ ARROW ] Jelajahi Donghua

Primary CTA is crimson with white text.

Secondary CTA is charcoal with subtle border.

# 17. SECTION HEADERS

Recommended:

Trending Now                         View All →

View All remains visually secondary.

Use Lucide Animated ArrowRight. The arrow may subtly move on hover.

# 18. PREMIUM POSTER CARD

Poster cards are one of the most important UI components.

Aspect ratio:

`2:3`

Normal state:

- high-quality poster
- consistent ratio
- subtle border
- soft shadow
- dark background
- minimal metadata

Hover:

1. Poster slightly scales.
2. Image subtly zooms.
3. Dark overlay appears.
4. Play button appears.
5. Lucide Animated Play reacts.
6. Card slightly elevates.
7. Minimal crimson ambient glow appears.

Do not turn the card red.

## INFORMATION HIERARCHY

1. Poster
2. Title
3. Episode
4. Status
5. Rating

Long titles should use line clamping.

## BADGES

Possible:

- NEW
- HD
- 4K
- SUB
- ONGOING
- COMPLETED

Badge design:

- compact
- dark
- translucent
- subtle border
- small typography

Use crimson only when meaningful.

# 19. CONTINUE WATCHING

Cards contain:

- poster
- title
- episode
- progress
- percentage
- play button

Progress:

dark track + DONGLYN crimson progress

# 20. TRENDING

Trending may use ranking numbers:

01
02
03
04
05

Numbers should be large, subtle, and low opacity.

On hover:

- ranking becomes stronger
- poster scales
- play icon appears

# 21. LATEST EPISODES

Display:

- poster
- title
- episode
- status
- release information

Keep the UI compact.

# 22. GENRE UI

Possible genres:

- All
- Action
- Adventure
- Fantasy
- Cultivation
- Martial Arts
- Romance
- Comedy
- Historical

Inactive: dark charcoal

Active: subtle crimson accent

Avoid huge genre pills.

# 23. SEARCH

Search should feel like a premium streaming service.

Use Lucide Animated Search.

Search must be:

- fast
- minimal
- responsive
- visually focused

Results display:

- poster
- title
- episode
- genre
- status

# 24. DONGHUA DETAIL PAGE

Structure:

Cinematic Backdrop

Poster

Title

Rating
Year
Episodes
Status

Genres

Description

[ PLAY ] Watch Now
[ BOOKMARK ] Add to List

## BACKDROP

Use Donghua artwork with:

- dark overlay
- gradient
- subtle blur when appropriate
- subtle crimson ambient lighting

Artwork must remain recognizable.

# 25. WATCH PAGE

The video player is the primary focus.

Recommended:

Video Player

Title
Episode

Episode Selector

Server Selector

Previous / Next

Metadata

Do not surround the player with unnecessary UI.

# 26. EPISODE SELECTOR

Selected episode:

DONGLYN crimson accent

Inactive:

dark charcoal

Hover:

subtle border

For large episode counts use pagination, search, filtering, or grouping when appropriate.

Avoid huge walls of episode buttons.

# 27. SERVER SELECTOR

If multiple streaming servers exist:

Server 1
Server 2
Server 3

Use:

- compact selector
- segmented control
- dropdown

Selected state:

subtle crimson accent

# 28. AUTHENTICATION UI

Authentication pages should feel premium.

Visual formula:

BLACK
+
DONGLYN LOGO
+
DARK SURFACE
+
CRIMSON CTA

Inputs should be dark, clean, and minimal.

Focus uses subtle crimson accent.

# 29. PROFILE

Keep profile simple.

Possible sections:

- Profile
- History
- Favorites
- Watchlist
- Settings

Avoid generic dashboard aesthetics.

# 30. WATCH HISTORY

Show:

- poster
- title
- episode
- progress
- last watched

Use crimson for progress.

# 31. FAVORITES

Primary icon:

Lucide Animated Heart

Use the same premium poster card system.

# 32. WATCHLIST

Primary icon:

Lucide Animated Bookmark

Use the same poster system.

# 33. BUTTON SYSTEM

## Primary

- crimson background
- white text
- strong hierarchy

Hover:

- subtle brightness
- slight elevation
- subtle crimson emphasis

## Secondary

- charcoal background
- white text
- subtle border

## Ghost

- transparent
- muted text

## Icon Button

- dark translucent surface
- subtle border
- animated Lucide icon

Every button supports:

- default
- hover
- active
- focus
- disabled
- loading

# 34. INPUT SYSTEM

Default:

`#101010`

Border:

`rgba(255,255,255,0.08)`

Focus:

subtle crimson border

Placeholder:

`#71717A`

Text:

`#F5F5F5`

Support:

- error
- success
- disabled
- loading

# 35. MODALS

Modal:

- dark surface
- subtle border
- soft shadow
- backdrop

Animation:

fade + scale

Close:

Lucide Animated X

# 36. DROPDOWNS

Use:

- dark surface
- subtle border
- soft shadow

Chevron:

Lucide Animated ChevronDown

Selected option:

subtle crimson accent

# 37. LOADING STATES

Avoid generic spinners everywhere.

Prefer:

- skeleton poster
- skeleton text
- subtle shimmer
- fade-in content

Skeleton dimensions should match real components.

Goal:

minimum layout shift.

# 38. EMPTY STATES

Empty states should be:

- simple
- useful
- friendly

Examples:

"Belum ada donghua di daftar kamu."

"Donghua tidak ditemukan."

Use subtle Lucide Animated icons.

# 39. ERROR STATES

Never expose raw technical errors.

Example:

Terjadi kesalahan.

Silakan coba lagi.

[ Refresh ]

Use Lucide Animated RefreshCw.

# 40. TOASTS

Toast design:

- dark surface
- subtle border
- soft shadow
- Lucide Animated icon

Keep messages short.

# 41. FOOTER

Footer should be visually quiet.

Suggested:

DONGLYN

Tempat terbaik untuk menikmati donghua favoritmu.

Home
Donghua
Genre
Schedule

Privacy
Terms
DMCA

Do not overload the footer.

# 42. BACKGROUND SYSTEM

Main background remains mostly black.

Optional ambient lighting:

- subtle crimson
- very low opacity
- cinematic

Avoid giant gradients.

# 43. RESPONSIVE DESIGN

Support:

320px
375px
390px
430px
768px
1024px
1280px
1440px
1920px+

Never allow horizontal overflow.

# 44. MOBILE DESIGN

Prioritize:

1. Content
2. Navigation
3. Search
4. Playback
5. User actions

Reduce:

- decorative effects
- unnecessary spacing
- oversized typography
- complex interactions

# 45. TOUCH TARGETS

Recommended minimum:

44 × 44px

Avoid tiny mobile controls.

# 46. RESPONSIVE POSTER GRID

Mobile:

2 columns where appropriate

Tablet:

3–4 columns

Desktop:

5–7 columns depending on viewport

Do not force a fixed column count when it harms visual quality.

# 47. MOBILE POSTER BEHAVIOR

Maintain:

2:3 aspect ratio

Reduce desktop hover behavior.

Touch devices must not depend on hover to discover functionality.

# 48. ACCESSIBILITY

DONGLYN must support:

- keyboard navigation
- semantic HTML
- screen readers
- visible focus states
- accessible labels
- alt text
- sufficient contrast
- reduced motion

# 49. FOCUS STATES

Never remove focus indicators without replacement.

Preferred:

subtle crimson outline
clear contrast

# 50. ICON ACCESSIBILITY

Every icon-only control MUST have:

`aria-label`

Example:

`aria-label="Cari Donghua"`

# 51. COLOR ACCESSIBILITY

Never communicate important information through color alone.

Combine color with:

- text
- icons
- labels
- state indicators

# 52. IMAGE SYSTEM

Poster:

`2:3`

Use:

`object-fit: cover`

Never distort artwork.

Use responsive image loading and lazy loading where appropriate.

# 53. IMAGE FALLBACK

Every image must have a graceful fallback.

Fallback must preserve:

- aspect ratio
- layout
- dark visual language

Broken image UI should never dominate the interface.

# 54. PERFORMANCE DESIGN

Avoid excessive:

- blur
- backdrop-filter
- box-shadow
- continuous animations
- DOM-heavy effects
- JavaScript animations

Prefer:

- CSS transforms
- opacity
- optimized images
- efficient rendering

# 55. UX WRITING

Use concise Indonesian.

Preferred:

- Mulai Streaming
- Lanjut Menonton
- Jelajahi Donghua
- Episode Terbaru
- Sedang Trending
- Tambahkan ke Daftar
- Coba Lagi
- Memverifikasi koneksi...
- Verifikasi berhasil
- Verifikasi keamanan gagal.

Avoid robotic copy, excessive technical terminology, and long explanations inside UI.

# 56. SECURITY UI

Security should feel:

- invisible
- fast
- trustworthy
- professional

Security should NOT feel:

- scary
- annoying
- repetitive
- intrusive

# 57. CAPTCHA VISUAL LANGUAGE

Captcha screens must visually match DONGLYN.

Use:

- black background
- dark surface
- subtle crimson accent
- Lucide Animated Shield
- Lucide Animated ShieldCheck

# 58. CAPTCHA STATES

Loading:

"Memverifikasi..."

Success:

"Verifikasi berhasil"

Error:

"Verifikasi keamanan gagal."

"Silakan coba lagi."

Retry uses Lucide Animated RefreshCw.

# 59. DESIGN ANTI-PATTERNS

Never introduce:

- excessive glassmorphism
- rainbow gradients
- excessive pills
- glowing borders everywhere
- giant decorative blobs
- generic dashboards
- excessive rounded cards
- excessive red
- excessive animation
- random icon styles
- emoji interface icons
- inconsistent spacing
- inconsistent typography

# 60. PREMIUM QUALITY DEFINITION

Premium means:

- better spacing
- better typography
- better imagery
- better hierarchy
- better interaction
- better consistency

Premium does NOT mean:

- more glow
- more gradients
- more animation
- more borders

# 61. VISUAL INTENSITY

Recommended hierarchy:

Hero: 100%
Poster Cards: 60%
Navigation: 30%
Content Sections: 25–40%
Footer: 15%
Security Screens: 25–35%

The strongest visual element should remain the content.

# 62. COMPONENT CONSISTENCY

Every component must share:

- typography
- spacing
- radius
- colors
- border language
- icon system
- motion language

Avoid one-off styling unless necessary.

# 63. REUSABLE COMPONENTS

Preferred reusable components:

- Navbar
- Button
- IconButton
- PosterCard
- PosterGrid
- SectionHeader
- Badge
- GenrePill
- SearchInput
- Modal
- Dropdown
- Tabs
- EpisodeSelector
- ServerSelector
- Skeleton
- Toast
- EmptyState
- ErrorState

Do not duplicate visually identical components.

# 64. DESIGN DECISION PRIORITY

When design decisions conflict, prioritize:

1. Accessibility
2. Usability
3. Content hierarchy
4. Performance
5. Consistency
6. Branding
7. Decoration

# 65. DESIGN QA

Before considering a UI complete, verify:

## Visual

- Does it feel premium?
- Does it feel cinematic?
- Is crimson balanced?
- Is typography clean?
- Is spacing intentional?
- Are posters high quality?

## UX

- Is navigation obvious?
- Can users discover content quickly?
- Are CTAs clear?
- Are states understandable?
- Are interactions predictable?

## Motion

- Does animation have a purpose?
- Is motion subtle?
- Does it feel responsive?
- Does reduced-motion work?

## Responsive

- Does mobile feel intentionally designed?
- Are touch targets large enough?
- Is there horizontal overflow?
- Does the poster grid remain clean?

## Accessibility

- Can everything be keyboard navigated?
- Are icon buttons labeled?
- Are focus states visible?
- Is contrast sufficient?

# 66. FINAL DESIGN FORMULA

DONGLYN

BLACK
+
WHITE
+
CRIMSON
+
CINEMATIC DONGHUA ARTWORK
+
PREMIUM POSTER CARDS
+
MODERN TYPOGRAPHY
+
SUBTLE MOTION
+
LUCIDE ANIMATED
+
CLEAN UX
+
MOBILE-FIRST
+
ACCESSIBILITY
+
PERFORMANCE

# 67. DONGLYN DESIGN NORTH STAR

The final experience should make users think:

> "This isn't just another Donghua website."

It should feel like:

> "This is DONGLYN."

Every screen should feel like it belongs to the same product.

Every interaction should feel intentional.

Every animation should have a reason.

Every color should have a purpose.

Every component should have a role.

Every piece of content should remain visually important.

# 68. FINAL STANDARD

The final design must feel:

PREMIUM
CINEMATIC
MODERN
ELEGANT
DARK
CLEAN
FAST
INTENTIONAL

It must NOT feel:

GENERIC
NOISY
OVERDESIGNED
AI-GENERATED
TEMPLATE-BASED

DONGLYN IS THE PRODUCT.

THE DESIGN SYSTEM EXISTS TO MAKE THAT IDENTITY CONSISTENT.
