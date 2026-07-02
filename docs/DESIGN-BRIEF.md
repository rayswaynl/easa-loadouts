# Warfare Tools — Visual/UX Overhaul Brief (2026-07-02)

Applies to: all 7 suite tools + the new EASA Loadouts tool + miksuu.com. Every overhaul agent reads this FIRST and executes against it. The goal: each tool feels like a station in the same Cold-War operations room — committed, atmospheric, and meticulous — without changing what anything DOES.

## The direction (commit fully)
**"Cold-War operations console."** Not a dark theme with orange buttons — an ops room. Push the existing identity to full commitment: tactical textures, stencil-cut headers, targeting-bracket framing, phosphor status lights, document-stamp moments. Restraint in color, drama in atmosphere and detail.

## HARD CONSTRAINTS (violating these = rejected work)
- **Palette is LOCKED** (CSS vars): gunmetal `#14171B`, steel `#2A2F36`/`#343b44`, olive `#5C6536`, bone `#E7E3D6`, orange `#D9763C`/`#B85F2A`, chalk `#F2EFE8`, line `#39414b`, danger `#c0392b`. You may add *derived* tints/alphas of these; no new hues.
- **Fonts are LOCKED**: Oswald (display), Inter (body), JetBrains Mono (data/classnames). Push character via weight/case/tracking, not new fonts.
- Single-file tools stay single-file, offline-capable, no build step, no new runtime libraries. CSS-only motion.
- **Functionality is sacred**: do not restructure state logic or export functions. Visual layer + interaction affordances only. All existing tests/round-trip gates must stay green.
- **A11y preserved or improved**: visible focus rings (orange), AA contrast (bone-on-gunmetal is fine; avoid low-alpha text below ~55% on gunmetal), `prefers-reduced-motion` disables all non-essential animation, keyboard paths intact, ARIA attributes preserved.
- Performance: no heavy background effects on the main interaction canvas; texture overlays are static CSS (no animated filters on large areas); target zero added network requests.

## Suite-wide vocabulary (implement consistently in every tool)
1. **Brandbar**: existing anatomy (mark, wordmark, tool name, chips, ← All Tools). Elevate: 1px olive top rule; tool name in Oswald caps w/ +2px tracking; a small round status LED (phosphor green = data loaded, orange pulse = dirty/unsaved, steady red = validation errors) with title tooltip.
2. **Stage framing**: the tool's central canvas gets **corner brackets** (targeting-reticle style, 2px, line color, ~18px arms) and a **very subtle grain + scanline overlay** (CSS gradient/repeating-linear, opacity ≤ .04, `pointer-events:none`).
3. **Panel headers**: Oswald, uppercase, letter-spacing 1.5px, with a thin left accent bar (3px olive) and a faint index number ("01 / ARSENAL" style ordinals).
4. **Buttons**: keep hierarchy (primary orange / default steel / danger). Add: 120ms ease transform on press (scale .98), consistent 5px radius, disabled = 40% + `cursor:not-allowed` + title reason.
5. **Chips/badges**: unify to the JetBrains Mono 10px pill style; status colors only from palette.
6. **Empty states**: military-flavor copy in JetBrains Mono caps (e.g. "— NO ORDNANCE SELECTED —", "AWAITING ORDERS", "SECTOR CLEAR") + one-line hint of the next action + (where sensible) a ghosted diagram/silhouette.
7. **Load orchestration**: ONE staggered reveal on app load (brandbar → panels left-to-right → stage), 250–400ms total, `animation-delay` steps, disabled under reduced-motion. No scattered random animations.
8. **Micro-interactions**: hover lift on picker tiles (1px translate + border-orange), drag ghosting w/ drop-target highlight, copy-to-clipboard flash ("COPIED ✓" chip), toast pattern bottom-right (steel bg, olive left rule, auto-dismiss).
9. **Help overlay**: `?` key opens a keyboard-shortcut/cheat-sheet modal (existing modal styles). Add a small `?` button in the brandbar.
10. **Scrollbars/inputs/modals**: keep existing styles; ensure consistent across tools (10px thumb steel2, focus border orange).
11. **Footer strip** (if a tool has one): version/source chip + "Part of the Warfare Tools suite → miksuu.com/tools".

## Per-tool identity moment (ONE memorable thing each — execute precisely)
- **WDDM**: blueprint drafting-table — faint blue-less *olive* grid + measurement ticks on the composition canvas; placed structures get thin dimension-line callouts on select.
- **Loadout Lab**: quartermaster's bench — the loadout preview panel styled as a requisition form (ruled lines, stamped total weight/cost box).
- **Sector Planner**: war-room map table — subtle topographic contour texture behind the map, towns as pinned markers w/ string-line connection emphasis in campaign mode; sim playback controls styled as a field radio deck.
- **Strategy & Economy**: command ledger — tech-tree nodes as stamped requisition cards; the economy panel gets a ticker-tape income preview strip.
- **Garrison Editor**: order-of-battle chart — group templates rendered as unit ORBAT cards with NATO-style echelon pips; garrison table rows get threat-level tint bars.
- **WF Menu Designer**: console-in-console — the editing viewport framed as a period CRT (soft vignette, slight phosphor glow on selection handles); alignment guides in orange.
- **Faction Builder**: personnel dossier — step tabs as folder tabs; completing a step stamps it ("APPROVED" olive stamp, slight rotation); final export panel = "DEPLOYMENT ORDERS" document.
- **EASA Loadouts**: flightline ordnance rack — airframe silhouette with station diagram, munition tiles as stenciled crates/pylons; the pylon-capacity meter as a loadmaster's balance gauge.
- **miksuu.com**: the public face — same ops-room atmosphere at editorial quality: hero with subtle grain, section headers with the ordinal+accent-bar pattern, leaderboard as a briefing table (row hover = file-highlight), guide pages get a reading TOC rail, tools hub tiles get hover "power-on" (thumb brightens + LED dot). Tailwind: extend theme with the derived tints; keep all changes inside the existing palette. NO layout-shift regressions (CLS), keep static rendering where it is static.

## Verification (every overhaul)
- All repo tests + round-trip gates green.
- Playwright: zero console errors; screenshot at 1440×900 saved to the repo (`docs/screenshots/overhaul-<date>.png`) — this becomes the new hub thumbnail source.
- Reduced-motion check: `prefers-reduced-motion` renders instantly.
- Diff discipline: no changes to export/emit functions; state logic untouched unless a UX item requires a handler (then minimal).
