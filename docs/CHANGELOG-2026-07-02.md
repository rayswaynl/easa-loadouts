# Warfare Tools & miksuu.com — Full Changelog · 2026-07-02

One-day program: new EASA Loadouts tool + functional & visual overhauls of all 7 suite tools + full miksuu.com pass.
**Deployed:** all 8 tool repos live on GitHub Pages. **Staged (awaiting Steff):** miksuu.com branch stack.

---

## 🆕 EASA Loadouts v1.0 — NEW TOOL
**Live:** https://rayswaynl.github.io/easa-loadouts/ · repo `rayswaynl/easa-loadouts`

- **Pylon-rack editor**: airframe silhouette over station tiles; a station = one magazine entry (the real EASA semantic unit, `2Rnd_FAB_250` renders ×2); launchers dedupe on export (duplicate `addWeapon` = the stacking glitch); pylon-capacity gauge (soft warning — engine doesn't enforce).
- **Modes**: Airplane · Helicopter · **Vehicle** — vehicle mode restricted to **unarmed** ground vehicles (55 eligible per faction); armed vehicles shown greyed with the reason (2nd mounted weapon = HUD cycling glitch + ammo loss on rearm). Armed/unarmed derived programmatically from CfgVehicles turret inheritance (202 armed / 142 unarmed indexed).
- **Presets**: all **490 in-game presets** parsed live from the mission's `EASA_Init.sqf` (21 aircraft) + **41 real-world presets** across 15 airframes (A-10 CAS standard, Mi-24 Afghanistan '80s, AH-64 tank-plinking, Ka-52 Vikhr anti-armor…), each with a doctrine rationale and only classnames verified to exist in A2:CO.
- **AA badge** computed from `CfgAmmo airLock` (matching the in-game AIRAAM gating) — never authored into exports, exactly like the mission's post-processing loop expects.
- **SQF I/O**:
  - Single preset row (paste-ready, comment header says exactly where it goes)
  - New-aircraft block (the 3 parallel `_easaVehi/_easaDefault/_easaLoadout` additions)
  - **Full `EASA_Init.sqf` import → edit → re-export** — no-op round-trip is **byte-identical** against the real 81 KB mission file (verified)
  - Vehicle mount snippet (`addWeaponTurret` per the mission's own `Common_BalanceInit.sqf` pattern, with rearm caveat + optional re-apply hook)
- QoL: localStorage autosave + restore, status LED, staggered load, toasts, `?` help overlay, a11y (focus rings, ARIA, reduced-motion).
- Pipeline: `tools/gen_easa_seed.py` (SQF parser/emitter, 26 tests), `tools/gen_assets.py` (config indexer: 79 aircraft / 106 weapons / 156 mags / 344 vehicles / 387 thumbs, 23 tests), 22-test Playwright suite.
- Research corpus in `docs/research/`: EASA mechanics deep-dive, real-world loadout catalog + presets JSON, plus the 7-tool and miksuu site audits.

## 🚨 Critical live fix — Sector Planner
- **The live tool had been dead-on-load since 2026-06-29**: the campaign-sim commit (`3d669ff`) accidentally replaced the trailing `init();` bootstrap. Every unit/round-trip suite stayed green; nothing did a cold load. **Restored + pushed** — live again (verified 40 towns rendering).
- Added `tools/test_coldload.py` — a Playwright cold-load regression gate (map dropdown ≥7 worlds, towns loaded, 0 console errors). Recommended for every tool repo.

## 🔧 Tool-by-tool

### Loadout Lab
- Fix: Gear Catalog now persists (was lost on every tab close) · `clearAll()` pre-load race guarded · non-consecutive duplicate mags merged in display (export semantics untouched) · test artifacts gitignored.
- Visual: quartermaster **requisition form** preview (ruled items, stamped TOTALS block) + full suite vocabulary (LED, ordinals, brackets, toasts, help overlay, footer, stagger).

### Garrison & AI Groups
- Fix: **Faction Builder → Garrison handoff finally works** — `coreUnits` payload now seeds the roster (was read then ignored) · stale `groupsRaw` after hand-editing the paste re-syncs · `+ Variant` respects the tier (was always last) · new 26-assertion smoke suite.
- Visual: **ORBAT cards** with NATO echelon pips, threat-level tint bars on garrison rows.
- Tests: 3 old `test_roundtrip.mjs` failures diagnosed (separate session): stale hardcoded expectations (CRLF checkout + wrong spacing), not code bugs — fixed by deriving expectations from input (pending commit in that session).

### WF Menu / HUD Designer
- Fix: drag undo off-by-one (push before move) · **autosave + restore + beforeunload warning** (refresh used to destroy all edits) · `evalSZ()` null check · dead resize handles removed · `cleanText()` no longer eats label words · renderer honors ST_RIGHT/ST_CENTER (the old HUD overlap) · **new bug found & fixed**: display data mutated without cloning (undo could corrupt parsed source). Audit's top finding (`inheritedVal`) disproved — was correct all along.
- Visual: **CRT console** frame (vignette + phosphor glow on selection handles/guides only — the game-UI canvas stays a faithful preview).

### Sector & Town Planner
- Fix (beyond the live bug): **town ownership persists per world** (campaign sim no longer silently flat after refresh) + reset control · sim flat-output guard · `maps.json` trimmed 162→30 KB · **undo/redo** (Ctrl+Z/Y) · F/G fit-view · shortcut help.
- Visual: **war-room map table** (topo texture, field-radio sim playback deck), ordinals/LED/brackets/toasts/help.

### Strategy & Economy
- Fix: seed-capture race fixed at the root (first generate after an edit produced empty diffs; dead MutationObserver hack removed) · unknown `WFBE_UP_*` names now warn visibly instead of silently becoming 0 · **Enable All / Disable All** · Economy→AI shared-array readouts live-sync · repo hygiene.
- Visual: **command ledger** (requisition cards with level pips + cost stamps, income ticker-tape strip, cross-link flash).

### Faction Builder
- Fix: Structures/Glue panels re-render on revisit (were frozen at first visit) · duplicate `switchStep()` removed · **session persistence** with restore prompt · reserved-token collision guard (US/RU/CDF/INS/GUE/TK…).
- Visual: **personnel dossier** (folder tabs, APPROVED stamps — gated to genuine completion after review caught them firing on fresh load, DEPLOYMENT ORDERS export panel); undefined `var(--abyss)` fixed to palette.

### WDDM
- Fix: **undo/redo** (50-level, byte-identical SQF verified after undo) · **lazy portraits — 189 image requests (~6.5 MB) on load → 0** · import parser crash guard · narrow-viewport notice.
- Visual: **blueprint drafting table** (olive grid + measurement ticks + metre labels, dimension-bracket selection), toolbar overlap fixed after review.
- Housekeeping: both old unmerged branches (`feat/commander-positions`, `feature/more-buildings-preview`) confirmed fully merged — safe to delete.

## 🌐 miksuu.com — STAGED (deploy on your word)
Branch stack: `feat/site-improve-jul2` → `feat/site-visual-jul2` → `feat/site-easa-tile` · build clean (77 pages) · 208 tests green.

**Improve:** home metadata + `revalidate 60` (status chip no longer frozen at build) · root canonical-leak fixed (pages claimed canonical=home) · `ogMeta()` on /tools + per-slug tool pages · sitemap +/tools + 8 slugs, −/changelog redirect · per-route error boundaries (wasp/players/guides/news/servers) · WCAG contrast bumps on info text. Verified-not-bugs: /leaderboard (redirects to /wasp by design), 404 page (already branded), /wasp SSR (already fixed).
**Visual:** ordinal SectionHeader pattern site-wide · hero polish (grain ≤.05, CTA hierarchy) · tools hub "power-on" hover + LED dots · War Room briefing-table rows + mono rank numerals · guides: sticky TOC rail, 70ch prose, blockquote/code styling · nav underline-grow micro-interactions · ops-console footer with server-IP/discord chips · empty-state treatment. All motion behind `motion-safe`.
**Tile:** EASA Loadouts (8th tool) + **all 8 hub thumbnails regenerated** from today's overhaul screenshots.

**Owner actions:** ① say go for the Game PC deploy (I run: pull → build → pm2 restart) · ② PayPal URL in `/admin/settings` (instant, no deploy) · ③ optional `og-tools.jpg` social card.

## 📚 Process artifacts
- `docs/DESIGN-BRIEF.md` — the reusable ops-console design contract (palette/typography/vocabulary/identity-moments/verification bar).
- Lessons institutionalized: cold-load gates everywhere; orchestrator screenshot review (caught 4 defects agents' tests missed); never hardcode fixture excerpts in tests (CRLF) — derive from input; byte-identical no-op round-trip is the oracle.
