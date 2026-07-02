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
2. 🔄 Research fleet (Opus): A=EASA mechanics+data model+export target, B=real-world loadout presets mapped to A2 classnames + unarmed-vehicle list, C=improvement audit of all 7 tools. Reports land in `docs/research/`.
3. Build EASA Loadouts tool (single-file index.html pattern, gen pipeline from config reference, presets from research B, export = EASA-compatible SQF patch).
4. Improvement pass across the 7 existing tools (subagent fleet, serialized, per-repo feat branches → main → Pages).
5. Hub: add tile + thumb on a miksuu feat branch. NO prod deploy without Steff.
6. Final report with suggestions/questions.

## Log
- 2026-07-02: repo init, journal created, research fleet dispatched.

## Discovered Issues
- (none yet)
