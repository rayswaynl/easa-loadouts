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
- EASA CORE BUILD dispatched (Opus): 3-panel app, ordnance-rack stage, stations=mag entries, presets (in-game + RW), AA badge via airLock, vehicle mode w/ eligibility. Export/import = build-2 after core lands.
- Visual overhauls in flight: loadout, garrison, wfmenu, sector, wddm, strategy, site.

## Discovered Issues
- (none yet)
