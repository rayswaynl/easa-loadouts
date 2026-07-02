# Miksuu Warfare Tools — Suite Audit
**Date:** 2026-07-02  
**Auditor:** Claude Code (read-only, no changes made)  
**Repos audited:** WDDM · loadout-lab · sector-planner · strategy-economy · garrison-editor · wf-menu-designer · faction-builder

---

## 1. WDDM — Warfare Dynamic Defense Manager

**Health verdict:** Solid single-page canvas app; clean git, no unmerged branches, no uncommitted work. Core export (SQF via textarea + clipboard, PNG screenshot, JSON save/load, URL-hash share) all wired and working. Cross-link to Sector Planner writes `wddm_structure` to localStorage correctly. No undo stack at all — every canvas drag/delete is permanent. No `/tools` back-link in UI. Mobile completely broken (canvas + `overflow:hidden`).

**Backlog:**

| Pri | Item | File / Location | Acceptance |
|-----|------|----------------|------------|
| P1-bug | Missing `?? 0` guard before `+pos[0]` in import parser (line 2067): if `pos` is undefined the import silently adds NaN objects | `index.html:2067` | Import of entries with missing `pos` field shows error toast rather than silently adding broken objects |
| P1-bug | `overflow:hidden` on `body` with no responsive breakpoints — canvas area is completely invisible on viewports < ~900 px wide; the tool also has no no-mobile warning | `index.html:24` | Add a ≥ 900 px viewport guard that shows a "use a wider screen" overlay |
| P2-win | No undo: any accidental `Delete` on a placed structure is permanent | `index.html` JS | Add Ctrl+Z undo stack (push snapshot before every destructive canvas op) |
| P2-win | No `/tools` or `miksuu.com/tools` back-link in the brand bar or anywhere in the UI | `index.html` brand bar | Add `← All Tools` link to `https://miksuu.com/tools` in brand bar |
| P2-win | Portrait JPGs pre-fetched for ALL catalog entries on load (~6.5 MB eager), not lazy | `index.html:820 preloadPortraits()` | Fetch only when a portrait is scrolled into view in picker (intersection observer) |
| P3-feat | `feat/commander-positions` local branch (9 WDDM presets + buildable compositions) never merged; `origin/feature/more-buildings-preview` remote branch not merged either | git | Review and merge or close both branches |
| P3-feat | Large structure thumbnails (`D30_TK_EP1.png` 470 KB, etc.) slow first render on picker open — no lazy-load | `assets/` | Convert to WebP + lazy-load in picker grid |

---

## 2. Loadout Lab — WASP Kit Editor

**Health verdict:** Most complete tool in the suite. Session autosave (`loadoutlab` key), faction handoff (reads `wasp-faction-handoff`, writes `wasp-loadout-handoff`), all export modes (DefaultGear / AI / Buy-menu) working. Two untracked artifacts (`test-results/`, `tools/smoke_screenshot.png`) not `.gitignore`'d. Key functional gap: the Gear Catalog panel state is ephemeral — never saved anywhere, lost on every page reload. No undo on item removal.

**Backlog:**

| Pri | Item | File / Location | Acceptance |
|-----|------|----------------|------------|
| P1-bug | `CATALOG_ITEMS` (gear catalog entries) not persisted — all buy-shop entries lost on tab close | `index.html` — `exportBuyMenu`/`CATALOG_ITEMS` | Persist `CATALOG_ITEMS` to `loadoutlab_catalog` localStorage key; restore on load |
| P1-bug | `clearAll()` race: if called before `loadClassData()` resolves, `DEFAULT_ITEMS` is empty and items are silently blanked | `index.html:1525 clearAll()` | Guard: only run `LO.items = DEFAULT_ITEMS.map(...)` when `DEFAULT_ITEMS.length > 0` |
| P1-bug | Mag deduplication is consecutive-only: non-sequential duplicates produce multiple UI rows for one mag, confusing users | `index.html` — importLoadout step 6 `collapsed` | Deduplicate non-contiguous same-class mags by count, matching SQF runtime behavior |
| P2-win | No undo on slot "Remove" buttons — misclick destroys a weapon selection permanently | `index.html` | One-level undo per slot (`lastRemoved`) with a 5-second "Undo remove" toast |
| P2-win | `test-results/` and `smoke_screenshot.png` untracked but not `.gitignore`'d | `.gitignore` | Add both paths to `.gitignore` |
| P3-feat | Gear catalog faction-relevance filter: with hundreds of items, an "only show items used by this faction" toggle would dramatically improve discoverability | `index.html` picker panel | Faction filter toggle in picker, grays out items not in seed-loadouts for chosen faction |

---

## 3. Sector Planner — WASP Campaign Map

**Health verdict:** Most featured tool — map pan/zoom canvas, multi-map support (5 maps), mission.sqm generator, campaign sim, supply routes. Clean git, only `.claude/` untracked. Key structural gap: painted town ownership (`town._side`) is never persisted — refreshing the page wipes all ownership and the sim produces silent zero output. Supply routes are persisted (`sp-supply-routes-v1`) but ownership isn't. `maps.json` is 162 KB because it includes every raw CfgWorlds entry — 90%+ could be trimmed.

**Backlog:**

| Pri | Item | File / Location | Acceptance |
|-----|------|----------------|------------|
| P1-bug | Town ownership/side paint is session-only — lost on refresh; Campaign Sim silently produces wrong results if ownership is unpainted | `index.html` — `paintSide()` | Write `sp-ownership-v1` localStorage key on every side-change; restore on load before sim |
| P1-bug | Campaign Sim produces a flat chart with no warning when neither ownership nor routes are set up | `index.html` — campaign sim runner | Guard: if `allNeutral && !routeCount` show blocking message before running |
| P2-win | `maps.json` is 162 KB because it includes unnamed FlatArea/StrongpointArea/CityCenter entries — could be trimmed to ~10-20 KB | `assets/data/maps.json` | Strip entries where `name` is missing or matches `^(FlatArea|StrongpointArea|CityCenter)` |
| P2-win | No keyboard shortcuts: no `Delete` to remove selected town, no `Ctrl+Z`, no `G` to fit-to-view | `index.html` `keydown` handler | Wire `Delete`, `Ctrl+Z`, `G` shortcuts |
| P3-feat | GUER is paintable as side owner but cannot be a Generated Mission faction — GUER spawn present but not a mission side | `index.html` — mission generator faction selects | Add GUER option to "Generate Mission" faction dropdowns |

---

## 4. Strategy & Economy — WASP Balance Tuner

**Health verdict:** Sophisticated 3-panel tool (tech-tree, economy, AI commander constants). Clean git; untracked `JOURNAL.md`, `node_modules/`, `server.pid`. Panel sync is correct and race-condition-free. Paste-and-patch export is robust (reverse-order apply, deepEq float tolerance). Key bugs: seed capture race (edits before first generate produce wrong diff baseline) and `parseSqfValueText` silently coerces unknown upgrade constant names to `0`. No undo, no session persistence.

**Backlog:**

| Pri | Item | File / Location | Acceptance |
|-----|------|----------------|------------|
| P1-bug | Seed capture race: if the user edits any field before clicking "Generate" for the first time, `captureSeeds()` snapshots the already-edited model — diffs are then empty | `index.html:3003-3011` | Call `captureSeeds()` synchronously inside `loadData()` immediately after data is assigned to `MODEL`, before any UI render |
| P1-bug | `parseSqfValueText` substitutes `0` for unknown `WFBE_UP_*` constant names instead of erroring — silent prereq corruption on round-trip with unknown constants | `index.html` — `parseSqfValueText` | If a `WFBE_UP_*` token is not in `MODEL.upgrades.ids`, emit a warning and skip that entry |
| P2-win | Stale Artillery Intervals / Respawn Ranges display in AI panel: edited in Economy but the AI panel doesn't re-render live | `index.html:~2298` — `updateSeedPreview()` | Subscribe to `change` on those fields and call `renderAiPanelQueue()` after |
| P2-win | No bulk-enable/disable: toggling all 22 upgrades for a faction requires 22 clicks | `index.html` tech-tree panel | Add "Enable All / Disable All for this faction" buttons |
| P3-feat | No session persistence: all edits lost on page reload | `index.html` | Save model delta to `localStorage['strategy-economy-session']` on each change; restore on load |

---

## 5. Garrison Editor — Group Templates & Town Garrison

**Health verdict:** Clean git, no uncommitted work, no unmerged branches. Dual-mode emitter (patch + change-list) is well-designed and round-trip tested. `coreUnits` from the faction handoff payload is accepted but entirely ignored — the faction is seeded from GUE defaults instead. No undo, no session persistence (ironic for a tool using localStorage for cross-tool handoff). `EXP.groupsRaw` sync bug means manually editing a pasted textarea after paste silently desynchs the diff baseline.

**Backlog:**

| Pri | Item | File / Location | Acceptance |
|-----|------|----------------|------------|
| P1-bug | `coreUnits` from Faction Builder handoff is read but never used — faction seeded from GUE templates regardless | `index.html:2121 fhbAccept()` | When `handoff.coreUnits` is present, populate the faction's templates from `coreUnits` instead of GUE fallback |
| P1-bug | `EXP.groupsRaw` / `EXP.garrisonRaw` not refreshed after user manually edits the source textarea post-paste: diff compares against stale data | `index.html:1556-1563` | On every `input` event on the source textarea, update `EXP.groupsRaw` to current textarea value |
| P1-bug | `addVariantToKey` always appends to the last sub-key for tiered factions — no way to add a variant to intermediate tiers | `index.html:897` | Pass sub-key explicitly to `addVariantToKey`; render per-sub-key "+ Variant" buttons |
| P2-win | No undo: `removeUnit`, `removeVariant`, `addNewKey` all permanent for the session | `index.html` | Add undo stack (push snapshot on destructive ops), `Ctrl+Z` binding |
| P3-feat | No session persistence — all edits lost on reload | `index.html` | Persist model to `localStorage['garrison-editor-session']` on change; restore on load |

---

## 6. WF Menu / HUD Designer

**Health verdict:** Best-tested tool (Playwright round-trip, inspector, smoke suites). Undo/redo with 100-step stack, multi-select, copy/paste, clipboard, group/lock/hide — all present. However two critical code bugs silently break inheritance-based inspector hints and the "reset to inherited" path: `inheritedVal()` always returns `undefined` because it reads `bc.props` instead of `bc` (base classes in `ui.json` are flat objects, not `{props:{...}}`). Drag undo push is post-move — undo steps are off by one. No localStorage at all — page refresh silently destroys all edits with no beforeunload warning.

**Backlog:**

| Pri | Item | File / Location | Acceptance |
|-----|------|----------------|------------|
| P1-bug | `inheritedVal()` and `resolveBaseChain()` always return undefined — inspector "Inherited from X" hints blank, "Reset to inherited" broken | `index.html:1758` and `:3157` — both read `bc.props` | Change `bc.props` → `bc` in both functions; add `&& key !== '_section'` guard |
| P1-bug | No `beforeunload` warning: 0% of edits survive a page refresh; no dirty-state tracking | `index.html` — event setup | Add `let isDirty = false`; set on first edit; `window.addEventListener('beforeunload', e => { if(isDirty) e.preventDefault(); })` |
| P1-bug | Drag undo push is AFTER the move (`mouseup` handler line 2731), so undo always returns to the wrong state | `index.html:2659` `onCtrlMouseDown` | Move `pushUndo()` to `onCtrlMouseDown` (before `dragging.startPositions` capture), remove from `mouseup` |
| P1-bug | `evalSZ()` null check `typeof val == null` is always false — null values throw in the replace chain | `index.html:856` | Change to `val == null` (double-equals catches both null and undefined) |
| P2-win | 3 of 4 resize handles (TL/TR/BL corner CSS divs) are rendered but have no resize logic — they do a move instead | `index.html` `onCtrlMouseDown` resize dispatch | Wire TL/TR/BL handles to constrained resize ops (anchor opposite corner, shrink from grabbed corner) |
| P2-win | `cleanText()` strips too aggressively — `$STR_WF_MAIN_Purchase_Units` → "Units" instead of "Purchase Units" | `index.html:896 cleanText()` | Join all non-prefix segments with space rather than taking last segment only |
| P2-win | Dead code: `parseHpp()` + `parseControlsBlock()` (350 lines, never called); `dialogs.json` never fetched (35 KB dead asset) | `index.html:3454-3765`; `assets/data/dialogs.json` | Delete dead functions; delete `dialogs.json` from repo |
| P3-feat | No "Export all 24 displays" batch: requires 24 manual export actions | `index.html` export panel | Add "Export all displays as Dialogs.hpp" button producing a single combined file |

---

## 7. Faction Builder — WASP Side Composer

**Health verdict:** v1 is complete and functional — all concerns about Task 4 being cut short are unfounded. `runEmit()` produces 4 core files + 7 GUE-template clones + registration patches + README.txt in a ZIP. Cross-tool launcher writes `wasp-faction-handoff` to localStorage and opens each sibling in a new tab. Export works without requiring a prior emit click. Clean git, no unmerged branches. Critical issues: `switchStep()` declared twice (second silently overwrites first — dead code), Structures and Glue panels don't re-render on revisit (frozen at first-visit state), 42 MB of thumbnails in repo (lazy-loaded, acceptable at runtime), no session persistence.

**Backlog:**

| Pri | Item | File / Location | Acceptance |
|-----|------|----------------|------------|
| P1-bug | Structures and Glue step panels don't re-initialize on tab revisit — values freeze at first-visit state | `index.html:1677` `_STEP_INITED` guard | Remove the guard for Structures and Glue panels; call their `initXxxPanel()` on every `switchStep()` call to those steps |
| P1-bug | Duplicate `switchStep()` declaration (line 759 and 1656) — first is dead code, risks confusion | `index.html:759` | Delete the first dead `switchStep()` declaration |
| P2-win | No session persistence: all faction work lost on page reload | `index.html` | Autosave `MODEL.faction` to `localStorage['faction-builder-session']` on every field change; restore on load |
| P2-win | Token collision only warns, doesn't block emit — user can silently overwrite an existing WASP faction (e.g., type `GUE`) | `index.html` `runEmit()` | If token matches a reserved WASP token (`GUE`, `USMC`, `CDF`, `TKA`, `RU`, etc.), show a blocking confirm before emit |
| P3-feat | `cloneGUE()` token substitution replaces `GUE` inside comments and generic SQF strings — could corrupt a template file with `Guerilla` in a comment | `index.html:1936 cloneGUE()` | Replace only in classname/variable positions: scope substitution to `_GUE_`, `"GUE"`, `GUE_`, `_GUE` patterns rather than bare word |

---

## Suite-Wide Issues

### localStorage Handoff Matrix

| Key | Writer | Readers | Status |
|-----|--------|---------|--------|
| `wasp-faction-handoff` | Faction Builder | Loadout Lab, Strategy & Economy, Garrison Editor, Sector Planner | **Working** — all 4 receivers implement the banner and accept the payload |
| `wasp-loadout-handoff` | Loadout Lab | Faction Builder (implied) | **One-way** — Faction Builder has no reader for this key |
| `wasp-garrison-highlight` | Garrison Editor | Sector Planner | **Working** — Sector Planner reads this to pre-highlight town types |
| `wddm_structure` | WDDM | Sector Planner | **Working** — Sector Planner reads this on load to pre-highlight structure type |
| `sp-supply-routes-v1` | Sector Planner | Sector Planner only | Persistence only, not cross-tool |

**Gap:** `wasp-loadout-handoff` is written by Loadout Lab to signal Faction Builder, but Faction Builder has no code that reads it. If the intent was for Faction Builder to receive a "loadout draft" from Loadout Lab, that receiver is missing.

### Shared Suite Gaps (all 7 tools)

| Priority | Issue |
|----------|-------|
| P2 | No `/tools` back-link in any tool — once you open a tool you cannot navigate back to `miksuu.com/tools` without using the browser back button |
| P2 | No mobile layout in any tool — all use `overflow:hidden` fixed-pixel grids; a "use a wider screen" overlay would prevent confusion |
| P2 | No session persistence in 5 of 7 tools (Garrison Editor, WF Menu, Strategy & Economy, Faction Builder, Sector Planner partial) — page refresh silently destroys work |
| P2 | WF Menu Designer, Strategy & Economy, Garrison Editor, Faction Builder have no favicon (`data:` SVG inline is fine but WF Menu uses `No matches` → no favicon at all — confirmed absent in wf-menu-designer) |
| P3 | Hardcoded `rayswaynl.github.io/*` URLs in cross-tool launchers — if any repo is renamed, all cross-links break silently |
| P3 | No CI pipeline in any tool — all deploy via manual push; a typo in `index.html` goes live immediately with no lint gate |

---

## Top 10 Highest-Value Items — Suite-Wide

| Rank | Tool | Item | Why it matters |
|------|------|------|---------------|
| 1 | WF Menu | Fix `inheritedVal()` / `resolveBaseChain()` (`bc.props` → `bc`) | Silent: inspector hints blank, "reset to inherited" does nothing — core inspector feature is broken |
| 2 | WF Menu | Add `beforeunload` dirty-state warning | Users lose all edits silently on accidental refresh — no localStorage fallback |
| 3 | Sector Planner | Persist town ownership to localStorage | Campaign Sim silently produces wrong results without painted ownership, which is lost on every refresh |
| 4 | Garrison Editor | Wire `coreUnits` handoff from Faction Builder | The whole faction handoff pipeline is plumbed, but the receiver ignores the most useful field |
| 5 | Loadout Lab | Persist `CATALOG_ITEMS` (gear catalog) | Biggest usability hole in an otherwise complete tool — all shop entries lost on every reload |
| 6 | WF Menu | Fix drag undo (push before move, not after) | Undo is effectively broken for drag operations — the most common editing action |
| 7 | Strategy & Economy | Fix seed capture race | First-generation diffs empty for users who edit before clicking "Generate" — makes the tool appear broken |
| 8 | WF Menu | Fix `evalSZ()` null check (`typeof val == null` → `val == null`) | Null values silently throw, breaking geometry calculation for affected controls |
| 9 | Faction Builder | Remove `_STEP_INITED` guard on Structures/Glue panels | Panels freeze at first-visit state — a returning user sees stale data |
| 10 | Suite-wide | Add `← All Tools` back-link to brand bar in all 7 tools | Navigation spine missing — suite feels disconnected from the hub |

---

## Git State Summary

| Repo | Uncommitted | Unmerged branches | Notable |
|------|------------|------------------|---------|
| WDDM | None | None | Clean |
| loadout-lab | `test-results/`, `smoke_screenshot.png` (untracked) | None | Add to `.gitignore` |
| sector-planner | `.claude/` (untracked) | None | Clean |
| strategy-economy | `JOURNAL.md`, `node_modules/`, `server.pid`, `test-results/`, `tests/export-panel.png` (untracked) | None | `node_modules/` not in `.gitignore`? Verify |
| garrison-editor | None | None | Clean |
| wf-menu-designer | None | `feat/v1`, `feat/improve`, `feat/v2-overhaul` — local branches only, all merged | Delete stale branches |
| faction-builder | None | None | Clean |
