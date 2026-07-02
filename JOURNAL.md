# JOURNAL — EASA Loadouts tool + Warfare Tools suite improvement pass

## Working State (2026-07-02)
- **Assignment (Steff):** (1) heavily improve the 7 live tools on https://miksuu.com/tools, (2) build a NEW tool — **EASA Loadouts** — with a Vehicle option and an Airplane/Helicopter option, shipping **real-world preset loadouts**; ground vehicles must EXCLUDE anything that already has a mounted weapon (second weapon glitches), (3) report suggestions/questions back. Research on Opus 4.8 subagents per Steff.
- **This repo:** `C:\Users\Steff\easa-loadouts` → will become `rayswaynl/easa-loadouts` + GitHub Pages, tiled on miksuu.com /tools.
- **Phase:** 1 — research (3 Opus agents in flight: EASA mechanics / real-world loadouts / 7-tool audit).

## Program bars (from warfare-tools-program memory)
- Each tool = unique core interaction, own repo + Pages, Playwright-verified (0 console errors), export round-trip gates.
- Hub tile on miksuu via feat branch — **user-approved prod deploy ONLY** (never push miksuu main / deploy unprompted).
- Serialize fleets, ≤~14 concurrent agents. `parallel()` takes thunks.
- Mission source of truth: `C:\Users\Steff\a2waspwarfare\Missions\[55-2hc]warfarev2_073v48co.chernarus\`
- EASA module: `Client\Module\EASA\{EASA_Init,EASA_LoadoutCat,EASA_Equip}.sqf`, `Client\GUI\GUI_Menu_EASA.sqf`, eligibility fns `Client_CanUse{TownCenter,RepairPoint}EASA.sqf`.
- Items/thumbnail pipeline to reuse: `loadout-lab/tools/gen_assets.py` + `arma2-co-config-reference` repo.
- Miksuu hub: `miksuus-warfare/web/src/app/tools/tools.ts` (+ thumb PNG in `web/public/tools-thumbs/`); repo currently on `main`, clean except stray untracked notes. Old `-main` worktree GONE — work in the main checkout, branch first.

## Plan
1. ✅ Recon (repos present, EASA files located, miksuu on main).
2. 🔄 Research fleet (Opus): A=EASA mechanics+data model+export target, B=real-world loadout presets mapped to A2 classnames + unarmed-vehicle list, C=improvement audit of all 7 tools, D=full miksuu.com site audit (Steff expanded scope mid-session: "do a pass on all aspects of miksuu.com in general"). Reports land in `docs/research/`.
3. Build EASA Loadouts tool (single-file index.html pattern, gen pipeline from config reference, presets from research B, export = EASA-compatible SQF patch).
4. Improvement pass across the 7 existing tools (subagent fleet, serialized, per-repo feat branches → main → Pages).
5. Hub: add tile + thumb on a miksuu feat branch. NO prod deploy without Steff.
6. Final report with suggestions/questions.

## Log
- 2026-07-02: repo init, journal created, research fleet dispatched (+ site audit D after Steff expanded scope).
- Research A (EASA mechanics) ✅ → docs/research/easa-mechanics.md. Data model: 3 parallel arrays in EASA_Init.sqf; preset=[price,label,[[wpns],[mags]]]; 4th AA element COMPUTED (never author); 21 aircraft exact-typeOf; Wildcat turret [-1] special case; ground vehicles unsupported → BalanceInit addWeaponTurret pattern (BRDM-2 Igla :344); 2nd-weapon glitch = HUD cycling + rearm ammo-loss (rearm reads config Magazines[]); EASA avoids via strip-before-apply + rearm re-apply (WFBE_EASA_Setup). SPEC.md updated to v1.
- Research C (7-tool audit) ✅ → docs/research/tools-audit.md. Faction Builder v1 actually COMPLETE. Top bugs: wf-menu inheritedVal reads bc.props not bc (inspector dead), no beforeunload; sector-planner ownership not persisted (campaign sim silently flat-zero after refresh); loadout-lab gear catalog not persisted + clearAll race; garrison-editor ignores coreUnits handoff; strategy-economy seed-capture race → empty diffs. Suite-wide: add "← All Tools" back-link.
- Builders dispatched: gen_easa_seed.py (parser+round-trip) + gen_assets.py (config indexer) — unblocked by research A.
- IMPROVEMENT WAVE 1 dispatched (Sonnet, own repos, branch feat/improve-jul2, no push): wf-menu-designer, sector-planner, loadout-lab, garrison-editor. Wave 2 (strategy-economy, faction-builder, WDDM) after wave 1 slots free.
- Research D (miksuu site audit) ✅ → docs/research/miksuu-site-audit.md + deep-dive corrections (root error/404 EXIST; real items = per-route boundaries, ogMeta canonical fix, sitemap /tools; /armory intentionally hidden). improve-site dispatched on feat/site-improve-jul2 (deploy user-gated).
- NEW LANE (Steff): "Do Visual / UX / UI overhauls as well" → docs/DESIGN-BRIEF.md written (ops-console commitment, locked palette/fonts, 11 suite vocabulary items, per-tool identity moments, verification bar). Overhauls sequenced AFTER each repo's functional merge (branch feat/visual-jul2).
- MERGED+DEPLOYED to Pages: loadout-lab (catalog persist, clearAll guard, mag dedup — verified 13 pytest), garrison-editor (coreUnits handoff WIRED, groupsRaw sync, per-tier variants — 35 pytest + RT + 26 smoke green), wf-menu-designer (undo timing, autosave+beforeunload, evalSZ, ST_RIGHT/CENTER align, deep-clone corruption fix — 3 suites green ON MAIN; note: its tests live at REPO ROOT not tools/). AUDIT FALSE POSITIVE confirmed: inheritedVal bc.props was CORRECT (improver disproved with passing inspector tests).
- Visual overhauls dispatched: loadout-lab (quartermaster), garrison-editor (ORBAT), wf-menu-designer (CRT console — chrome only, canvas stays faithful preview).
- STEFF Q&A: "Can EASA be pylon based?" → answered YES as editing model (engine has no pylon API; stations=magazine entries, flatten on export, capacity meter soft-warn) — in SPEC.md.
- ALL 7 FUNCTIONAL PASSES MERGED+DEPLOYED to Pages ✅: loadout-lab, garrison-editor, wf-menu-designer, sector-planner (72 tests, maps.json 162→30KB), faction-builder (53 tests; re-render fix verified safe — panels use idempotent on*= handlers), WDDM (lazy portraits 189 reqs→0; both old unmerged branches confirmed EMPTY of unique commits — safe to delete), strategy-economy (10 Playwright; dead MutationObserver hack removed with the seed race).
- Research B ✅ (41 RW presets / 15 airframes / 55+57 vehicle eligibility / 14 mountable CfgWeapons pairs) + builder-index ✅ (airframes 79 / weapons 106 / mags 156 / vehicles 344, 202 armed / 142 unarmed, 387 thumbs, 49 tests). DECISION: vehicles.json armed flag is AUTHORITATIVE for eligibility (scanner tables conflicted on UAZ_RU/GAZ_Vodnik; generated data verified correct). KNOWN GAP: boats (RHIB/PBX/Zodiac) not in vehicles.json — curated list covers them.
- miksuu.com: improve-site ✅ on feat/site-improve-jul2 (build clean 77 pages, 208 vitest; /leaderboard was NEVER broken — it redirects to /wasp; canonical leak fixed; 5 per-route error boundaries; sitemap +tools). visual-site STACKS on it as feat/site-visual-jul2. DEPLOY = user-gated, owner items: PayPal URL in /admin/settings, og-tools.jpg optional.
- EASA CORE BUILD ✅ (commit 363260a): index.html 85 KB, 10/10 Playwright green. 3-panel ops-console app — airframe picker (21 EASA aircraft), preset list (in-game virtualised + RW), ordnance-rack stage (silhouette, station tiles, pylon meter), vehicle mode (54 eligible / 57 excluded, armed-flag authoritative). window.exportSinglePresetRow/exportFullEasaInit/exportVehicleSnippet/importEasaBlock stubs ready for build-2.
- Visual overhauls in flight: loadout, garrison, wfmenu, sector, wddm, strategy, site.

## Log (continued)
- 🚨 LIVE BUG FOUND+FIXED: sector-planner was DEAD-ON-LOAD in production since 2026-06-29 — commit 3d669ff (campaign sim) accidentally REPLACED the trailing `init();` bootstrap with its section header. All parser tests stayed green; browser "verifications" only probed function existence. Fix: restored init() as last statement (main 3a016dd) + NEW tools/test_coldload.py regression gate (asserts map dropdown ≥7 worlds + towns + 0 errors on cold load). Verified live-fix rendering (40 towns Chernarus). LESSON: every tool needs a COLD-LOAD gate, not just unit/round-trip tests.
- ALL 7 VISUAL OVERHAULS MERGED+DEPLOYED ✅ (loadout quartermaster / garrison ORBAT / wf-menu CRT / sector war-room / WDDM blueprint (+toolbar overlap fix after my screenshot review) / strategy command-ledger / faction-builder pending? NO — faction-builder visual not dispatched yet!). Site visual (feat/site-visual-jul2) verified by me via dev server + Playwright (home/tools/guide) — awaiting Steff deploy approval.
- Shared-browser gotcha: the Playwright MCP browser is ONE instance shared with subagents — my sector screenshot got swapped mid-check by the WDDM agent. Use own python-playwright probes for verification.
- EASA build-2 (SQF import/export + byte-identical gate) dispatched.

## Discovered Issues
- garrison-editor tools/test_roundtrip.mjs: 3 PRE-EXISTING failures → RESOLVED by the spawned task session (task_dea4e8c0): stale HARDCODED expectations, not code bugs — (a) literals assumed LF but a2waspwarfare checks out CRLF (core.autocrlf), (b) SmallTown2 expected `], [` spacing that never existed in the source. Exporter proven correct by the byte-identical no-op oracle. Fix (in that session, uncommitted pending Steff's word): derive expected blocks from the pasted input + source-EOL, + fixture-sanity assertions. LESSON for suite tests: never hardcode fixture excerpts — derive from input (EOL-portable); the no-op round-trip is the oracle.
- faction-builder visual overhaul NOT YET dispatched (only tool missing it) — do after current wave.
- vehicles.json lacks boats (RHIB/PBX/Zodiac) — curated list covers eligibility; extend gen_assets.py later if boat mounting wanted.
