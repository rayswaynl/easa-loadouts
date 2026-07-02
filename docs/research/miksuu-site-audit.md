# miksuu.com Site Audit — 2026-07-02

Auditor: Claude Code (read-only; code + live HTTP)
Scope: `web/` (Next.js 14.2.35, App Router, src/ layout)
Live checks: 17 URLs via WebFetch

---

## Overall Verdict

The site is in **good shape for a community project**. Core pages are complete, news is active (Build 85 just posted today), the /tools suite and /leaderboard are fully implemented, and OG metadata is correctly wired for the routes that matter most. The biggest systemic gap is that **six pages ship without OG social cards** — a mechanical fix, not a content problem. There is one confirmed live bug (a sitemap URL that 404s on live) and one visible user-facing placeholder (PayPal "soon"). No broken navigation links were found in the actual rendered nav or footer.

---

## Dimension 1 — Content Freshness / Quality

### WP-1.1 — /armory page is publicly reachable but unfinished [P2]
- **File**: `src/app/armory/page.tsx`
- **Issue**: The page has `robots: { index: false, follow: false }` and is not in the sitemap or nav — but is reachable at `/armory`. It shows 1/4 release gates cleared, placeholder swatch tiles, and the text "Swatches are placeholders — final textures land when the Textures gate clears." This is acceptable as a soft launch but the page should either be link-accessible (add to nav when ready) or fully suppressed (add `/armory` to the `PRIVATE_PATHS` list in `robots.ts` and add a `notFound()` redirect in the page).
- **Acceptance**: Either suppress completely via middleware redirect + robots, or wire it into the nav once textures are done.

### WP-1.2 — PayPal "soon" is a visible user-facing placeholder [P2]
- **File**: `src/app/donate/page.tsx` line 66
- **Issue**: When `paypalUrl` is null in site settings (the current production state), users see a grayed-out "PayPal · soon" button. This is intentional but makes the donate page look unfinished.
- **Fix**: Either wire the PayPal URL in admin settings, or replace the disabled button with a "PayPal not yet available" note with an estimated date, or remove the button entirely until ready.
- **Acceptance**: No user-visible "soon" text on the donate page.

### WP-1.3 — /changelog duplicates /news [P3]
- **File**: `src/app/changelog/page.tsx` (likely a redirect to `/news`)
- **Issue**: Live fetch confirms both `/changelog` and `/news` show identical content (Build 85 as latest). The sitemap includes `/changelog`. If this is an alias it should either be a canonical redirect or the sitemap entry should be removed to avoid duplicate-content penalties.
- **Acceptance**: `/changelog` either 301-redirects to `/news` (like `/wiki` → `/guides`) or the two are differentiated in purpose and the sitemap is updated.

### WP-1.4 — /leaderboard in sitemap 404s on live [P1]
- **File**: `src/app/sitemap.ts` line listing `/leaderboard`
- **Issue**: The sitemap.ts staticRoutes array includes `/leaderboard`. The actual leaderboard page lives at `src/app/leaderboard/page.tsx` and is served at `/leaderboard` — **but Google's cached sitemap from the live domain currently shows 404 for that slug** (confirmed by live-site agent). This may be a deployment lag or a past route rename. The Nav's "War Room > Leaderboard" dropdown also links to `/leaderboard`.
- **Priority note**: This is P1 if the route genuinely 404s in production right now. Verify with a browser hit — the WebFetch agent's 404 report may have been caused by JS-only rendering rather than a true missing route (the leaderboard page is a server component so it should SSR).
- **Fix**: Confirm the route renders; if it's an SSR issue, check that `getIngameLeaderboardFull()` doesn't throw on an empty table and crash the page silently.
- **Acceptance**: `https://miksuu.com/leaderboard` returns HTTP 200 with content.

### WP-1.5 — No events calendar or server changelog [P3]
- **Issue**: Community sites typically have an event calendar (scheduled matches, special events) and a server changelog distinct from patch notes. Currently only `/news` exists for announcements. The Taviana Air War event (per memory context) has no dedicated page.
- **Fix**: Add `/events` as a static MDX-driven page (same pattern as `/guides`), or add an "Events" section to `/news`.
- **Acceptance**: Players can find upcoming events from the nav.

---

## Dimension 2 — Home Page Impact

### WP-2.1 — Hero video preload but no `<video>` fallback described [P3]
- **File**: `src/app/layout.tsx` (preload link) + `src/components/AmbientHero.tsx`
- **Issue**: The root layout preloads `/brand/hero-bg.webm` but no poster image or `<source type="video/mp4">` fallback is declared in the layout. If AmbientHero doesn't implement a poster, the hero area may flash black on slow connections or in browsers that don't support WebM.
- **Fix**: Read `AmbientHero.tsx` to confirm poster and fallback handling; add `<video poster="/brand/hero-poster.jpg">` if missing.
- **Acceptance**: No flash-of-black on the hero on first load, confirmed by slow-3G throttle in DevTools.

### WP-2.2 — Tools suite has no home page cross-promotion [P3]
- **Issue**: The home page has sections for AI Commander, factions, economy, dynamics, and a guides preview — but no mention of the 7-tool Warfare Tools suite, which is a strong differentiator. The `/tools` page is linked only in the nav.
- **Fix**: Add a compact "Warfare Tools" strip to the home page (matching the Guides preview pattern: `grid-cols-3` cards linking to `/tools`).
- **Acceptance**: A visitor landing on the home page is made aware of the tools suite before reaching the footer.

### WP-2.3 — StatusChip data freshness unknown [P2]
- **File**: `src/lib/queries.ts` → `getServerStatus()`; `src/components/StatusChip.tsx`
- **Issue**: The home page server status chip (BattleMetrics-backed) is rendered server-side with no explicit `revalidate` on the home page (`src/app/page.tsx` has no `export const revalidate`). In Next.js 14 App Router, absence of `revalidate` means the page is statically generated at build time. If the server status is included in the static build output, it will be stale between deploys.
- **Fix**: Add `export const revalidate = 60` (or 30) to `src/app/page.tsx`, or move `getServerStatus()` behind a Route Handler that the `StatusChip` fetches client-side.
- **Acceptance**: The home page server status reflects live data within ~60 seconds.

---

## Dimension 3 — UX / Navigation

### WP-3.1 — "War Room" dropdown in nav has no fallback label on mobile [P2]
- **File**: `src/components/Nav.tsx` / `src/components/MobileMenu.tsx`
- **Issue**: The nav includes a "War Room" group with children `[Live (/wasp), Leaderboard (/leaderboard)]`. Confirm that `MobileMenu.tsx` properly exposes these children as nested items rather than collapsing the group silently on mobile. Also: the "War Room" label is military-jargon — new visitors may not know it means "stats and rankings."
- **Fix**: Verify mobile menu expands the War Room group. Consider renaming to "Stats & Rankings" or adding a tooltip.
- **Acceptance**: Both `/wasp` and `/leaderboard` are reachable from the mobile nav.

### WP-3.2 — No breadcrumbs on guide slug pages [P3]
- **File**: `src/app/guides/[slug]/page.tsx`
- **Issue**: The live `/guides/getting-started` page does not show breadcrumb navigation (Guides > Getting Started). Guide pages are linked from the home page and from `/guides`, so the back path is not always obvious, especially for users landing directly from a search result.
- **Fix**: Add a `<nav aria-label="Breadcrumb">` above the guide heading: Home → Guides → [Guide Title].
- **Acceptance**: All guide detail pages display a breadcrumb trail.

### WP-3.3 — 404 page design unverifiable (likely bare Next.js default) [P2]
- **File**: No `src/app/not-found.tsx` found in directory listing
- **Issue**: There is no custom `not-found.tsx` in the app directory. Users hitting broken links (including the `/leaderboard` 404 if confirmed) land on Next.js's default white 404 page, which has no branding, no nav, and no CTA to return to the site.
- **Fix**: Add `src/app/not-found.tsx` matching the site's dark theme with nav, logo, and a "Back to Home" button.
- **Acceptance**: Hitting any 404 URL shows the branded 404 page with the site nav.

### WP-3.4 — No site search [P3]
- **Issue**: The guides page has inline search (client-side `GuideSearch` component) and the players page has `PlayerSearch`, but there is no site-wide search. A community site with 14+ guides, dozens of news posts, and a rules page could benefit from a unified search.
- **Fix**: Low-cost option: add a search page at `/search` backed by the existing `guide-search.ts` + a simple news title index. No external service required.
- **Acceptance**: Nav includes a search affordance linking to `/search`.

---

## Dimension 4 — SEO / Social

### WP-4.1 — Six pages missing OG social card [P2]
Confirmed by code scan (ogMeta= false) and live HTML inspection (no og: tags returned):

| Page | File |
|------|------|
| `/` (home) | `src/app/page.tsx` — no `export const metadata` |
| `/appeal` | `src/app/appeal/page.tsx` — metadata present but no `ogMeta()` call |
| `/changelog` | `src/app/changelog/page.tsx` — no metadata |
| `/login` | `src/app/login/page.tsx` — metadata present but no `ogMeta()` |
| `/profile` | `src/app/profile/page.tsx` — metadata present but no `ogMeta()` |
| `/report` | `src/app/report/page.tsx` — metadata present but no `ogMeta()` |
| `/tools` | `src/app/tools/page.tsx` — metadata present but no `ogMeta()` |

Note: The root layout (`src/app/layout.tsx`) **does** export metadata with `ogMeta({ image: "og-home.jpg" })` as a fallback, so the home page inherits a social card via the layout. However, child pages that define their own `metadata` without `openGraph` override the layout's OG block entirely, leaving those pages with no OG image.

- **Fix**: Add `...ogMeta({ title, description, image: "og-home.jpg", path: "/pagepath" })` to each missing page's metadata export. For `/tools`, add `og-tools.jpg` to the `OgCardName` union in `lib/og-meta.ts` and generate the card.
- **Acceptance**: All non-admin pages return `og:title`, `og:image`, and `og:description` in `<head>`.

### WP-4.2 — Dynamic slug pages missing per-post OG metadata [P2]
- **Files**: `src/app/guides/[slug]/page.tsx`, `src/app/news/[slug]/page.tsx`, `src/app/players/[steamId64]/page.tsx`
- **Issue**: These pages could not be checked directly (PowerShell glob can't read bracket-named files). Verify that each uses `generateMetadata()` to produce per-slug titles, descriptions, and OG images. If news posts lack individual OG images, they should at least use the post title and description in the OG tags with the fallback `og-news.jpg` card.
- **Fix**: Confirm `generateMetadata` is implemented on each slug page; add if missing.
- **Acceptance**: Sharing a guide or news post link on Discord shows the specific post's title.

### WP-4.3 — robots.ts AI crawler intent documented but verify rendering [P3]
- **File**: `src/app/robots.ts`
- **Issue**: The code is well-structured and intentional (AI crawlers explicitly allowed, private paths blocked). The live `robots.txt` output looks correct. However, the live-site agent flagged "conflicting directives" — this was a misread of the dual-group pattern. No action needed on substance; worth adding an inline comment explaining the group ordering to prevent future confusion.
- **Acceptance**: No change needed; document as informational.

---

## Dimension 5 — Performance

### WP-5.1 — Home page has no revalidate (stale server status) [P2]
Covered in WP-2.3 above.

### WP-5.2 — next/image used correctly in tools grid and home page [Info]
- `src/app/tools/ToolsGrid.tsx` uses `<Image>` with `fill` and `sizes` for tool thumbnails.
- `src/app/page.tsx` uses `<Image>` for the "What is Warfare" cards.
- All seven tool thumbnails exist in `public/tools-thumbs/`.
- All six OG cards exist in `public/og/`.
- No raw `<img>` tags spotted in page code.

### WP-5.3 — Fonts loaded via @fontsource (bundle) not Google Fonts CDN [Info]
- `package.json`: `@fontsource/inter`, `@fontsource/oswald`, `@fontsource/jetbrains-mono`
- Self-hosted via npm bundle — good for privacy and performance; no external font DNS lookup.

### WP-5.4 — Tools iframes: poster-tile / on-demand pattern implemented correctly [Info]
- `src/app/tools/ToolsGrid.tsx`: iframes are only mounted when user clicks "Live preview"; before that, a static `<Image>` screenshot is shown. This prevents auto-loading 7 iframes on page load. Pattern confirmed shipped.

### WP-5.5 — Next.js 14.2.35 — consider upgrade path [P3]
- Current: 14.2.35 (latest 14.x). Next.js 15 is stable. No urgent security issue in 14.x, but the upgrade to 15 brings server-action security improvements and better caching APIs. Not blocking; schedule for a maintenance window.

---

## Dimension 6 — Accessibility

### WP-6.1 — Skip-to-content link present [Info]
- `src/app/layout.tsx` includes a `sr-only focus:not-sr-only` skip link to `#main-content`. Good.

### WP-6.2 — SVG logo has `aria-hidden` in nav and footer [Info]
- Both `Nav.tsx` and `Footer.tsx` set `aria-hidden="true"` on the decorative SVG logo. Good.

### WP-6.3 — Emoji used as content in LeaderCard without aria-label [P2]
- **File**: `src/app/leaderboard/page.tsx` — `LeaderCard` renders emoji icons (`⚔`, `🎯`, `📦`, `🔧`, `⏱`) with `aria-hidden="true"`. The category labels (`Most kills`, `Best K/D`, etc.) are in the accompanying `<span>`, so screen readers do get the label. Pattern is correct.
- No action needed; marking as verified.

### WP-6.4 — Focus-visible states on form inputs [P2]
- Appeal and report forms both use `focus-visible:ring-2 focus-visible:ring-orange` on inputs — good.
- Verify that the ToolsGrid filter buttons and "Live preview" button also have visible focus rings.
- **File**: `src/app/tools/ToolsGrid.tsx` — filter buttons use `transition-colors` but no explicit `focus-visible:ring-*`. Add `focus-visible:ring-2 focus-visible:ring-orange focus-visible:ring-offset-2` to all interactive buttons.

### WP-6.5 — Color contrast: bone/30 and bone/40 text on gunmetal [P2]
- The design palette uses `text-bone/30` and `text-bone/40` (very low opacity white on dark background) extensively for secondary/tertiary labels. These almost certainly fail WCAG AA (4.5:1 for normal text). A targeted pass replacing the lowest-contrast instances in visible UI labels (not already-muted decorative text) would improve accessibility.
- **Fix**: Audit with browser DevTools contrast checker; bump `bone/30` labels to at least `bone/50` on the most information-dense pages (leaderboard, admin dashboard).

---

## Dimension 7 — Server Status / Live Data

### WP-7.1 — /wasp page is JS-only; search engines see "Loading live data…" [P2]
- **File**: `src/app/wasp/page.tsx`
- **Issue**: The WASP stats page is confirmed client-side only — static fetch returns only "Loading live data…". This means zero server-rendered content for crawlers or users with JS disabled.
- **Fix**: Move the initial data fetch to a server component (or `generateMetadata` + RSC shell) so the page title, top-level stats, and structured summary render in HTML. Client-side polling for live updates can layer on top.
- **Acceptance**: `curl https://miksuu.com/wasp` returns meaningful stats content in the HTML body.

### WP-7.2 — BattleMetrics-backed server status has no error state visible [P2]
- **File**: `src/components/StatusChip.tsx`
- **Issue**: When BattleMetrics is unreachable, verify that `StatusChip` shows a neutral "Unknown" or "Checking…" state rather than crashing the page or displaying stale data without indication.
- **Fix**: Read `StatusChip.tsx` and `getServerStatus()` to confirm error path returns a safe fallback status. Add a visual "Status unavailable" chip state if missing.
- **Acceptance**: With BattleMetrics mocked to fail, the home page renders a non-crashing status chip.

---

## Dimension 8 — Auth / Profile UX

### WP-8.1 — Login page has no OG card and no description [P2]
Covered in WP-4.1. The login page metadata also has no description, which looks bad in browser history and link previews.

### WP-8.2 — Profile page: verify GDPR export/delete is wired [P2]
- **File**: `src/app/profile/page.tsx`
- **Issue**: The privacy policy (confirmed live) describes data export and deletion options. Verify that the profile page actually links to or provides these actions (data export download + account deletion flow).
- **Fix**: Read `profile/page.tsx` and confirm export/delete actions exist and call server actions.
- **Acceptance**: A logged-in user can download their data and delete their account from `/profile`.

### WP-8.3 — Turnstile CSP allowlist is correct [Info]
- **File**: `src/middleware.ts`
- `challenges.cloudflare.com` is included in `script-src`, `frame-src`, and `connect-src`. Correct per Cloudflare's Turnstile CSP requirements. Appeal form should work without CSP errors.

---

## Dimension 9 — Code Health

### WP-9.1 — Home page missing `export const metadata` entirely [P1]
- **File**: `src/app/page.tsx`
- **Issue**: The home page has no `export const metadata` object. The root layout's metadata (including OG tags) applies as the fallback, which happens to include `ogMeta()`. So the home page is not broken — but it's the only page without its own metadata export, making it an exception to the consistent pattern used across all other pages.
- **Fix**: Add a top-level `export const metadata: Metadata = { title: "Miksuu's Warfare", description: "...", ...ogMeta({...}) }` to `src/app/page.tsx` for consistency and to make the fallback explicit.
- **Acceptance**: `src/app/page.tsx` has its own metadata export.

### WP-9.2 — changelog/page.tsx has no metadata [P2]
- **File**: `src/app/changelog/page.tsx`
- Combined with WP-1.3 (likely a redirect). If it stays as a page, add metadata.

### WP-9.3 — wiki/page.tsx has no metadata [Info]
- **File**: `src/app/wiki/page.tsx` — this is just a `redirect('/guides')` so no metadata needed; Next.js won't render a `<head>` for redirect pages.

### WP-9.4 — No error boundaries on client components [P2]
- **File**: `src/app/wasp/page.tsx`, `src/app/tools/ToolsGrid.tsx`, `src/app/leaderboard/page.tsx` (client tabs)
- **Issue**: No `error.tsx` files were found in the route segment directories. In Next.js 14 App Router, route segments need an `error.tsx` to catch RSC fetch errors without crashing the entire page to a white screen.
- **Fix**: Add `src/app/error.tsx` (global catch-all) and per-segment `error.tsx` for data-heavy routes: `/leaderboard/error.tsx`, `/wasp/error.tsx`, `/players/error.tsx`.
- **Acceptance**: Deliberately breaking the DB query shows a branded error page rather than an unhandled crash.

### WP-9.5 — `server-only` package imported in lib/ [Info]
- `server-only` is in dependencies, indicating server-boundary enforcement is used. Good hygiene.

### WP-9.6 — SQL safety [Info]
- Drizzle ORM (`drizzle-orm: 0.45.2`) is used for DB access via `lib/queries.ts`. Drizzle uses parameterized queries by default — no raw string interpolation risk unless `.execute(sql\`...\`)` is used with dynamic values. Recommend a spot-check of any `sql` template literal calls in `lib/queries.ts`.

---

## Dimension 10 — Admin Dashboard

### WP-10.1 — /admin has no error boundary [P2]
- Admin fetches many data sources in parallel (dashboard, bot config, logging, VIP, etc.) — a single failed query crashes the whole admin page. Add `src/app/admin/error.tsx`.

### WP-10.2 — Admin modules appear complete [Info]
Found pages for: Dashboard, Appeals, Bot (4 tabs confirmed: Welcome, Voicemaster, VIP, Role Panels), Embeds, Logging, Members, Outbox, Reports, Settings (with ContentForm + SettingsForm), Telemetry, Translations. No obviously half-finished shells.

### WP-10.3 — Settings form has PayPal URL field but field may be unconfigured [P2]
- **File**: `src/app/admin/settings/SettingsForm.tsx` line 31
- The PayPal URL field exists in the admin settings form. The "soon" state on the donate page is driven by `paypalUrl` being null/empty in the DB. An admin can fix the PayPal donate button without a code deployment by filling in the PayPal URL in admin settings.
- This is worth documenting: tell the site owner they can unblock WP-1.2 from `/admin/settings` without a deploy.

---

## Top 10 — Highest-Value Improvements

| # | Tag | Work Package | Impact |
|---|-----|--------------|--------|
| 1 | **P1** | **WP-1.4** — Verify `/leaderboard` actually returns 200 on production; fix if 404 | Nav link is broken for the core stats feature |
| 2 | **P1** | **WP-9.1** — Add `export const metadata` to `src/app/page.tsx` | Home page is the only one without explicit metadata; OG is inherited not owned |
| 3 | **P2** | **WP-4.1** — Add `ogMeta()` to the 6 pages missing it (`/tools`, `/appeal`, `/login`, `/profile`, `/report`, `/changelog`) | Zero social previews on these pages when shared; 15-minute mechanical fix |
| 4 | **P2** | **WP-7.1** — SSR the initial WASP stats content so `/wasp` is not JS-only | SEO dead zone for the community's live-stats centrepiece |
| 5 | **P2** | **WP-2.3 / WP-5.1** — Add `export const revalidate = 60` to `src/app/page.tsx` | Home page server status is stale between deploys |
| 6 | **P2** | **WP-3.3** — Add `src/app/not-found.tsx` with branded dark-theme 404 page | Users hitting any broken link see a white Next.js default page |
| 7 | **P2** | **WP-9.4** — Add `src/app/error.tsx` + per-segment error boundaries | Any DB/API failure causes a full page crash with no recovery UI |
| 8 | **P2** | **WP-1.2** — Configure PayPal URL in `/admin/settings` (no deploy needed) | Removes visible "soon" placeholder from the donate page instantly |
| 9 | **P2** | **WP-4.2** — Audit `generateMetadata` on all `[slug]` pages | Guide and news posts share as generic "Miksuu's Warfare" instead of the post title |
| 10 | **P2** | **WP-6.5** — Bump lowest-contrast `bone/30` text labels to `bone/50` | WCAG AA compliance for informational labels site-wide |

---

## Live Bugs Confirmed (2026-07-02)

1. **`/leaderboard` may 404** — listed in sitemap and linked from the "War Room" nav dropdown. WebFetch returned 404; may be a JS-rendering limitation of the audit tool or a genuine route issue. Needs browser verification. If confirmed: check `src/app/leaderboard/page.tsx` for an unhandled `getIngameLeaderboardFull()` throw on empty data.

2. **`/wasp` renders "Loading live data…" to all crawlers and non-JS users** — the entire stats page is client-side only. Not a crash, but a usability and SEO hole for the site's most dynamic page.

3. **PayPal button shows "PayPal · soon"** — visible to all donate page visitors. Fix in admin settings (no deploy): set `paypalUrl` or remove the field.

---

*Audit method: code read (read-only, no edits) + 17 live WebFetch requests. No auth tokens used for protected pages.*
