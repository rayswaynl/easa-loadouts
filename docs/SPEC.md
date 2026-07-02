# EASA Loadouts — spec v1 (mechanics research resolved; rosters/presets pending research B)

## What it is
Browser designer for WASP Warfare **EASA** armament — a full editor for the mission's EASA table plus a ground-vehicle weapon-mount designer, shipping **real-world preset loadouts**. Single-file `index.html`, offline, suite dark theme, own repo (`rayswaynl/easa-loadouts`) + GitHub Pages, tile on miksuu.com/tools.

## Ground truth (from docs/research/easa-mechanics.md)
- EASA data lives ONLY in `Client\Module\EASA\EASA_Init.sqf`: three parallel arrays `_easaVehi` / `_easaDefault` / `_easaLoadout`.
- Preset row (authored) = `[price:int, 'label', [[weapons...],[mags...]]]` — the 4th AA-flag element is COMPUTED by the init post-processing loop; never emit it.
- 21 registered aircraft (planes + helos, exact `typeOf` match). Wildcat `AW159_Lynx_BAF` is special (turret path `[-1]`).
- Mags repeat per pylon slot (`addMagazine` once per occurrence) — the editor must model mag COUNTS as repeated entries.
- AA presets are hidden in-game unless AIRAAM upgrade (idx 19) purchased / module 2 — the tool computes and badges `hasAA` per preset (from CfgAmmo airLock via generated data).
- Ground vehicles: NOT in EASA. The mission's own pattern for arming ground vehicles is `addWeaponTurret` in `Common_BalanceInit.sqf` (BRDM-2 Igla :344, Pandur :362). Dynamically added weapons LOSE AMMO on rearm (rearm reads config `Magazines[]`) unless re-applied EASA-style. Mounting a 2nd weapon on an already-armed vehicle → HUD cycling glitch + rearm corruption ⇒ Vehicle mode restricts to UNARMED vehicles only.

## Modes
1. **Airplane** / 2. **Helicopter** — same engine, filtered rosters:
   - Seed = parsed live `EASA_Init.sqf` (all 21 aircraft, defaults + every existing preset with prices/labels).
   - Edit existing presets, reorder, reprice, relabel; add new presets (from scratch, from stock default, or from a **real-world preset** one-click).
   - Add a NEW aircraft to the EASA table (any air vehicle in the config reference): define default-strip loadout + preset list → emits the 3-parallel-array block.
   - Live badges per preset: computed AA flag (⚠ gated behind AIRAAM in-game), pylon-count sanity hint (informational — engine doesn't enforce), price, classname validation.
3. **Vehicle** — unarmed ground vehicles only (armed ones visible but greyed out with reason "already has a mounted weapon — 2nd weapon glitches cycling/rearm").
   - Mount 1 weapon + magazines; export a `Common_BalanceInit.sqf`-style `addWeaponTurret` snippet (+ documented rearm caveat and optional re-apply hook note).

## Unique core interaction (program bar)
**Hardpoint rack stage**: selected airframe as a large side-profile silhouette; its loadout rendered as station tiles under the wing/fuselage line; click/drag weapons from the pool onto the rack; live totals (mags, price, AA badge). Presets animate onto the rack.

## Pylon/station model (per Steff 2026-07-02: "Can the EASA be pylon based somehow?" → YES, as the editing model)
- ENGINE TRUTH: A2:OA has no per-pylon API (that's A3 setPylonLoadout). EASA = flat [[weapons],[mags]]; pylon counts in EASA_Init comments are informational. Visuals follow model weapon proxies via magazines.
- TOOL MODEL: each airframe gets a curated `stations[]` layout (id, group: wingtip|outer|inner|centerline|gun, allowed categories, IRL label), sized from the documented pylon count + real station charts (research B).
- A station tile holds ONE munition package = one MAGAZINE entry (the real EASA semantic unit; `2Rnd_FAB_250` renders as ×2). Gun stations hold the gun + its mag.
- EXPORT FLATTEN: weapons[] = deduped launchers (same launcher twice = the stacking glitch), mags[] = one entry per filled station, stable order (station order).
- IMPORT UNFLATTEN: assign a preset's mags to stations heuristically (category→group match, fill outer→in); leftover mags go to an "overflow" strip (still valid, just unplaced).
- PYLON-CAPACITY METER: sum of munitions vs documented pylons → soft warning only (engine doesn't enforce; over-adding corrupts weapon cycling).

## Panels (3-column, Loadout-Lab grid)
- Left: mode segmented control, faction chips, airframe/vehicle thumbnail picker; per-airframe preset list (existing = editable, real-world = suggested, "+ new").
- Center: hardpoint rack stage + validation strip.
- Right: weapon/mag pool (search + category chips: Gun pods, Rockets, AGM, Bombs, AAM, CM) with per-airframe plausible-pool highlighting; export panel.

## Exports (all copy-to-clipboard + download)
1. **Single preset row** — paste into a vehicle's existing preset array (3-element row, comment header telling exactly where).
2. **New vehicle block** — the 3 parallel `_easaVehi/_easaDefault/_easaLoadout` additions.
3. **Full EASA_Init.sqf** — regenerated whole file (paste-over). ROUND-TRIP GATE: parse the real file → re-emit → semantically identical (arrays equal), byte-level where feasible.
4. **Vehicle mount snippet** — BalanceInit-style SQF.
5. Import: paste an `EASA_Init.sqf` (or a block) → parse into the editor.

## Data (assets/data/, generated by tools/gen_assets.py)
- `easa-seed.json` — parsed from the mission's EASA_Init.sqf (the 21 aircraft + presets + defaults).
- `airframes.json` — air vehicles per faction (classname, display name, faction, plane|heli, pylons-info, thumbnail, stock weapons/mags) from config reference + research B rosters.
- `weapons.json` / `magazines.json` — air weapons + vehicle-mount weapons w/ display names, thumbs, compatible mags, ammo airLock (for AA computation), inherited via parent chain (loadout-lab gotcha).
- `vehicles.json` — ground vehicles per faction: eligible (unarmed) / excluded (armed + reason); mountable weapon set.
- `presets-realworld.json` — curated real-world presets (research B): name, rationale, weapons+mags, per airframe.

## Gates
- Round-trip: EASA_Init.sqf parse→emit identical (CI-able Python test + in-browser check).
- Playwright: 0 console errors; picker/preset/export smoke; screenshot → hub thumb.
- Classname validation: every emitted classname exists in the config-reference index; every preset's mags compatible with its weapons.

## In-game truths to surface in UI copy (from research)
- EASA usable only at the side's service-point building (70 m), driver seat, EASA upgrade ($4k, needs air factory), module param on (default on).
- Cost check is strict `>` (need MORE than price) — quirk, surface in tooltip.
- Rearm re-applies the EASA preset automatically (WFBE_EASA_Setup).
