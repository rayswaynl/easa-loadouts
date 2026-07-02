# EASA Loadouts — spec (draft v0, research pending)

## What it is
Browser designer for WASP Warfare **EASA** armament: pick an airframe (Airplane / Helicopter) or an **unarmed ground vehicle**, assemble a weapon loadout, and export game-ready SQF. Ships with **real-world preset loadouts** (named after real doctrine/configurations) as one-click starting points.

Suite conventions: single-file `index.html`, offline, WDDM/Loadout-Lab dark theme (gunmetal/steel/olive/orange/bone/chalk, Oswald/Inter/JetBrains Mono), own repo + GitHub Pages, tile on miksuu.com/tools.

## Unique core interaction (program bar)
A **side-profile "hardpoint rack" stage**: the selected airframe shown as a large silhouette with its weapon stations rendered as slots beneath/on it; drag or click weapons from the pool onto stations; the rack updates live with weight/ammo/cost. (Distinct from Loadout Lab's slot-list and WDDM's grid — this is the armament-on-airframe visual.)

## Modes
1. **Airplane** — fixed-wing roster per faction.
2. **Helicopter** — rotary roster per faction.
3. **Vehicle** — ONLY ground vehicles with NO existing mounted weapon (a second mounted weapon glitches weapon cycling in A2). Armed vehicles listed greyed-out with the reason. Mount one weapon (M2/DShKM/Mk19/AGS/…) + magazines.

## Panels (3-column app grid like Loadout Lab)
- Left: mode toggle (segmented), faction filter, airframe/vehicle picker (thumbnails from arma2-co-config-reference), preset list for selection.
- Center: the hardpoint rack stage + live totals (mag count, cost if EASA costs exist, validation badges).
- Right: weapon/magazine pool picker (search + category chips), export panel.

## Data (generated, assets/data/)
- `airframes.json` — per-faction air rosters + stock loadouts + allowed pools (from mission source + CfgVehicles/CfgWeapons/CfgMagazines).
- `vehicles.json` — unarmed ground vehicles (eligible) + armed (excluded w/ reason) + mountable weapon set.
- `presets.json` — real-world presets (name, rationale line, weapon+mag lists) — curated from research.
- Generator: `tools/gen_assets.py` (adapted from loadout-lab; weapon type/magazines inherited via parent chain).

## Export targets (⚠ finalize from research A)
- EASA loadout SQF (whatever `EASA_LoadoutCat`/pool arrays expect) — paste-ready patch.
- Per-preset "apply" snippet (removeWeapon/addWeapon/addMagazine sequence) for testing in the editor.
- Vehicle mode: mount snippet + (if research supports) mission-config registration.

## Gates
- Round-trip: import exported SQF → identical state.
- Playwright: 0 console errors, picker/export smoke, screenshot for the hub thumb.
- Classname validation: every emitted classname exists in the config reference index.

## Open questions (fill from research)
- [ ] Exact EASA pool/data structure + where presets could hook (research A).
- [ ] Do EASA costs exist per weapon? (research A)
- [ ] Final rosters + preset list (research B).
- [ ] Ground-vehicle mounting: turret path semantics + what WASP already does (research A/B).
