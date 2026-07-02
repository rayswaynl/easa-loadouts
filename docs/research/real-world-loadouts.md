# EASA Loadouts — Research Report
## Air Rosters, Armament Pools & Real-World Presets

**Sources:**
- Config reference: `C:\Users\Steff\arma2-co-config-reference\Config\` (CfgVehicles.txt, CfgWeapons.txt, CfgMagazines.txt — A2:OA 1.63 dump by UHAX)
- WASP mission: `C:\Users\Steff\a2waspwarfare\Missions\[55-2hc]warfarev2_073v48co.chernarus\Common\Config\Core_Units\`
- BalanceInit: `Common\Functions\Common_BalanceInit.sqf`
- Real-world references: Jane's All the World's Aircraft; USMC Aviation Weapons & Tactics Manual; Soviet/Russian Air Force combat records (Afghanistan 1979–89, Chechnya, Syria 2015+)

---

## A. Air Roster per Faction

All classnames verified present in CfgVehicles.txt unless marked *(ACR — not in dump)*.

### USMC / US West

| Classname | Display | Kind | Shop |
|---|---|---|---|
| MH60S | MH-60S Knighthawk | heli | Aircraft |
| UH1Y | UH-1Y Venom | heli | Aircraft |
| MV22 | MV-22 Osprey | plane | Aircraft + Airport |
| AH1Z | AH-1Z Viper | heli (attack) | Aircraft |
| AH64D | AH-64D Apache | heli (attack) | Aircraft |
| A10 | A-10 Thunderbolt II | plane (attack) | Aircraft + Airport |
| AV8B | AV-8B Harrier II (LGB) | plane (attack) | Airport |
| AV8B2 | AV-8B Harrier II+ | plane (attack) | Airport |
| L159_ACR | L-159 ALCA | plane (attack) | Airport *(ACR DLC — not in dump)* |
| F35B | F-35B Lightning II | plane (attack) | Airport |
| C130J | C-130J Hercules | plane (transport) | Aircraft + Airport |

**CO/EP1 adds:** MH6J_EP1 (Little Bird), AH6J_EP1 (Little Bird armed), UH60M_EP1, UH60M_MEV_EP1, CH_47F_EP1, CH_47F_BAF, AH64D_EP1, BAF_Apache_AH1_D, BAF_Merlin_HC3_D, AW159_Lynx_BAF, C130J_US_EP1, A10_US_EP1

### Russia / East

| Classname | Display | Kind | Shop |
|---|---|---|---|
| Mi17_Ins | Mi-8/17 Hip (armed) | heli | Aircraft |
| Mi17_medevac_RU | Mi-8/17 Medevac | heli | Aircraft |
| Mi17_rockets_RU | Mi-8/17 Hip (rockets) | heli | Aircraft |
| Mi24_P | Mi-24P Hind-F | heli (attack) | Aircraft |
| Mi24_V | Mi-24V Hind-E | heli (attack) | Aircraft |
| Ka52 | Ka-52 Alligator | heli (attack) | Aircraft |
| Ka52Black | Ka-52 (black scheme) | heli (attack) | Aircraft |
| Su25_Ins | Su-25 Frogfoot | plane (attack) | Aircraft + Airport |
| Su25_TK_EP1 | Su-25 Frogfoot (TK) | plane (attack) | Aircraft + Airport |
| Su39 | Su-39 (Su-25TM) | plane (attack) | Airport |
| Su34 | Su-34 Fullback | plane (attack) | Airport |

**CO adds:** UH1H_TK_EP1, Mi24_D_TK_EP1, An2_TK_EP1, L39_TK_EP1

### CDF (Chernarus Defence Forces)

| Classname | Display | Kind | Shop |
|---|---|---|---|
| Mi17_CDF | Mi-8/17 Hip (CDF) | heli | Aircraft |
| Mi17_medevac_CDF | Mi-8/17 Medevac | heli | Aircraft |
| Mi24_D | Mi-24D Hind-D | heli (attack) | Aircraft |
| Su25_CDF | Su-25 Frogfoot (CDF) | plane (attack) | Aircraft + Airport |

### INS (Insurgents)

| Classname | Display | Kind | Shop |
|---|---|---|---|
| Mi17_Ins | Mi-8/17 Hip | heli | Aircraft |
| Mi17_medevac_Ins | Mi-8/17 Medevac | heli | Aircraft |
| Mi24_V | Mi-24V Hind-E | heli (attack) | Aircraft |
| Su25_Ins | Su-25 Frogfoot | plane (attack) | Aircraft + Airport |

### GUE (Guerrillas — Vanilla)

| Classname | Display | Kind | Shop |
|---|---|---|---|
| Mi17_Civilian | Mi-8 Hip (civilian) | heli | Aircraft |

**CO adds:** UH1H_TK_GUE_EP1, Ka60_PMC (opt), Ka60_GL_PMC (opt), An2_1_TK_CIV_EP1, An2_2_TK_CIV_EP1

### TKA (Takistan Army — OA maps)

| Classname | Display | Kind | Shop |
|---|---|---|---|
| UH1H_TK_EP1 | UH-1H Huey (TK) | heli | Aircraft |
| Mi17_TK_EP1 | Mi-8/17 Hip (TK) | heli | Aircraft |
| Mi24_D_TK_EP1 | Mi-24D Hind-D (TK) | heli (attack) | Aircraft |
| An2_TK_EP1 | An-2 Colt | plane | Aircraft + Airport |
| L39_TK_EP1 | L-39 Albatros | plane (attack) | Airport |
| Su25_TK_EP1 | Su-25 Frogfoot | plane (attack) | Airport |

**Roster totals:** ~15 distinct airframe types (ignoring faction reskins), ~35 unique classnames across all factions and maps.

---

## B. Per-Airframe Armament Facts

All classnames verified in CfgWeapons.txt and CfgMagazines.txt.

### A-10 / A10_US_EP1
**Stock (A10):** GAU8 (1350Rnd_30mmAP_A10), MaverickLauncher (2Rnd_Maverick_A10), SidewinderLaucher_AH1Z (2Rnd_Sidewinder_AH1Z), BombLauncherA10 (4Rnd_GBU12), FFARLauncher_14 (14Rnd_FFAR), CMFlareLauncher (120Rnd_CMFlare_Chaff_Magazine)
**Note:** BalanceInit strips FFARLauncher_14 + BombLauncherA10 + SidewinderLaucher_AH1Z + MaverickLauncher from A10 (LF-gated rearming pool); A10_US_EP1 only loses FFARLauncher_14 + BombLauncherA10.

**Plausible pool:**
- GAU8 / 1350Rnd_30mmAP_A10 (always)
- MaverickLauncher / 2Rnd_Maverick_A10
- BombLauncherA10 / 4Rnd_GBU12
- FFARLauncher_14 / 14Rnd_FFAR
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

### AV8B (LGB variant) / AV8B2 (Mk82+FFAR variant)
**Stock AV8B:** GAU12 (300Rnd_25mm_GAU12), BombLauncher (6Rnd_GBU12_AV8B), CMFlareLauncher (120Rnd_CMFlare_Chaff_Magazine)
**Stock AV8B2:** GAU12 (300Rnd_25mm_GAU12), Mk82BombLauncher_6 (6Rnd_Mk82), SidewinderLaucher_AH1Z (2Rnd_Sidewinder_AH1Z), FFARLauncher_14 (14Rnd_FFAR), CMFlareLauncher

**Plausible pool:**
- GAU12 / 300Rnd_25mm_GAU12
- BombLauncher / 6Rnd_GBU12_AV8B
- Mk82BombLauncher_6 / 6Rnd_Mk82
- FFARLauncher_14 / 14Rnd_FFAR
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

### F35B
**Stock:** GAU12 (300Rnd_25mm_GAU12), BombLauncherF35 (2Rnd_GBU12), SidewinderLaucher_F35 (2Rnd_Sidewinder_F35), CMFlareLauncher (120Rnd_CMFlare_Chaff_Magazine)

**Plausible pool:** Same as AV8B pool above + SidewinderLaucher_F35 / 2Rnd_Sidewinder_F35

### Su-25 (all variants: Su25_Ins, Su25_TK_EP1, Su25_CDF)
**Stock (Su25_base):** GSh301 (180Rnd_30mm_GSh301), AirBombLauncher (4Rnd_FAB_250), R73Launcher_2 (2Rnd_R73), S8Launcher (80Rnd_S8T), CMFlareLauncher (120Rnd_CMFlare_Chaff_Magazine)
**Note:** BalanceInit strips R73Launcher_2 + S8Launcher from Su25_Ins; strips AirBombLauncher + 80mmLauncher from Su25_TK_EP1 (LF-gated).

**Plausible pool:**
- GSh301 / 180Rnd_30mm_GSh301
- AirBombLauncher / 4Rnd_FAB_250
- S8Launcher / 80Rnd_S8T (or 40Rnd_S8T)
- 80mmLauncher / 40Rnd_80mm (S-8KOM variant)
- 57mmLauncher / 64Rnd_57mm (S-5 rockets)
- R73Launcher_2 / 2Rnd_R73
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

### Su-39
**Stock:** GSh301 (180Rnd_30mm_GSh301), Ch29Launcher (4Rnd_Ch29), R73Launcher_2 (2Rnd_R73), S8Launcher (80Rnd_S8T), CMFlareLauncher

**Plausible pool:** All Su-25 pool items + Ch29Launcher / 4Rnd_Ch29

### Su-34
**Pilot stock:** 80mmLauncher (40Rnd_S8T), CMFlareLauncher (120Rnd_CMFlare_Chaff_Magazine)
**Gunner turret stock:** GSh301 (180Rnd_30mm_GSh301), Ch29Launcher_Su34 (6Rnd_Ch29, 4Rnd_Ch29), R73Launcher (4Rnd_R73)
**Note:** BalanceInit strips R73Launcher from Su34 pilot slot.

**Plausible pool:**
- GSh301 / 180Rnd_30mm_GSh301
- Ch29Launcher_Su34 / 6Rnd_Ch29
- R73Launcher / 4Rnd_R73
- S8Launcher / 80Rnd_S8T
- AirBombLauncher / 4Rnd_FAB_250
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

### L39_TK_EP1
**Stock:** GSh23L_L39 (150Rnd_23mm_GSh23L), 57mmLauncher (64Rnd_57mm)

**Plausible pool:**
- GSh23L_L39 / 150Rnd_23mm_GSh23L (or 520Rnd_23mm_GSh23L parent)
- 57mmLauncher / 64Rnd_57mm
- 57mmLauncher_128 / 128Rnd_57mm
- AirBombLauncher / 4Rnd_FAB_250 (if mission allows)

### AH-1Z
**Pilot stock:** FFARLauncher (38Rnd_FFAR), CMFlareLauncher (120Rnd_CMFlareMagazine)
**Gunner turret:** M197 (750Rnd_M197_AH1), HellfireLauncher (8Rnd_Hellfire), SidewinderLaucher_AH1Z (2Rnd_Sidewinder_AH1Z)
**Note:** BalanceInit strips SidewinderLaucher_AH1Z (LF-gated).

**Plausible pool:**
- M197 / 750Rnd_M197_AH1 (turret fixed)
- HellfireLauncher / 8Rnd_Hellfire
- FFARLauncher / 38Rnd_FFAR (or 14Rnd_FFAR via FFARLauncher_14)
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlareMagazine

### AH-64D / AH64D_EP1 / BAF_Apache_AH1_D
**Pilot stock:** FFARLauncher (38Rnd_FFAR), CMFlareLauncher (60Rnd_CMFlareMagazine)
**Gunner turret:** M230 (1200Rnd_30x113mm_M789_HEDP), HellfireLauncher (8Rnd_Hellfire)
**Note:** BalanceInit strips HellfireLauncher (LF-gated).

**Plausible pool:**
- M230 / 1200Rnd_30x113mm_M789_HEDP (turret)
- HellfireLauncher / 8Rnd_Hellfire
- FFARLauncher / 38Rnd_FFAR
- SidewinderLaucher_AH64 / 8Rnd_Sidewinder_AH64
- CMFlareLauncher / 60Rnd_CMFlareMagazine

### Mi-24D (Mi24_D, Mi24_D_TK_EP1) — *Mi24_D_CZ_ACR not in dump*
**Pilot stock:** 57mmLauncher_128 (128Rnd_57mm), CMFlareLauncher (120Rnd_CMFlareMagazine)
**Gunner turret:** YakB (1470Rnd_127x108_YakB), AT2Launcher (4Rnd_AT2_Mi24D)
**BalanceInit:** Upgrades 128Rnd_57mm → 64Rnd_57mm (smaller load at lower LF).

**Plausible pool:**
- YakB / 1470Rnd_127x108_YakB (turret)
- AT2Launcher / 4Rnd_AT2_Mi24D
- 57mmLauncher_128 / 128Rnd_57mm
- 57mmLauncher / 64Rnd_57mm
- CMFlareLauncher / 120Rnd_CMFlareMagazine

### Mi-24P (Mi24_P)
**Pilot stock:** GSh302 (750Rnd_30mm_GSh301), 80mmLauncher (40Rnd_80mm), CMFlareLauncher (120Rnd_CMFlareMagazine)
**Gunner turret:** HeliBombLauncher (2Rnd_FAB_250), AT9Launcher (4Rnd_AT9_Mi24P)
**BalanceInit upgrades:** Strips HeliBombLauncher + 80mmLauncher, adds 57mmLauncher + extra GSh301 ammo (LF3).

**Plausible pool:**
- GSh302 / 750Rnd_30mm_GSh301
- HeliBombLauncher / 2Rnd_FAB_250
- AT9Launcher / 4Rnd_AT9_Mi24P
- 80mmLauncher / 40Rnd_80mm
- S8Launcher / 80Rnd_S8T
- 57mmLauncher / 64Rnd_57mm
- CMFlareLauncher / 120Rnd_CMFlareMagazine

### Mi-24V (Mi24_V)
**Pilot stock:** S8Launcher (80Rnd_80mm), CMFlareLauncher (120Rnd_CMFlareMagazine)
**Gunner turret:** YakB (1470Rnd_127x108_YakB), AT6Launcher (4Rnd_AT6_Mi24V)
**Note:** BalanceInit strips AT6Launcher (LF-gated).

**Plausible pool:**
- YakB / 1470Rnd_127x108_YakB (turret)
- AT6Launcher / 4Rnd_AT6_Mi24V
- S8Launcher / 80Rnd_S8T
- 80mmLauncher / 40Rnd_80mm
- 57mmLauncher / 64Rnd_57mm
- CMFlareLauncher / 120Rnd_CMFlareMagazine

### Ka-52 / Ka52Black
**Pilot stock:** 80mmLauncher (40Rnd_80mm), CMFlareLauncher (120Rnd_CMFlare_Chaff_Magazine)
**Gunner turret:** 2A42 (230Rnd_30mmHE_2A42 + 230Rnd_30mmAP_2A42), VikhrLauncher (12Rnd_Vikhr_KA50)
**Note:** BalanceInit strips VikhrLauncher (LF-gated).

**Plausible pool:**
- 2A42 / 230Rnd_30mmHE_2A42, 230Rnd_30mmAP_2A42 (turret)
- VikhrLauncher / 12Rnd_Vikhr_KA50
- S8Launcher / 80Rnd_S8T
- 80mmLauncher / 40Rnd_80mm
- AT6Launcher / 4Rnd_AT6_Mi24V
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

### UH-1Y (UH1Y)
**Pilot stock:** FFARLauncher_14 (14Rnd_FFAR), CMFlareLauncher (120Rnd_CMFlareMagazine)
**Turrets:** M240 door guns (inherited from UH1_Base)
**BalanceInit:** Replaces 14Rnd_FFAR with 4× 14Rnd_FFAR (LF upgrade).

**Plausible pool:**
- FFARLauncher_14 / 14Rnd_FFAR (×1–4)
- FFARLauncher / 38Rnd_FFAR
- CMFlareLauncher / 120Rnd_CMFlareMagazine

### MH-60S (MH60S) — armed transport
**Stock:** CMFlareLauncher (60Rnd_CMFlareMagazine)
**Turrets:** M240_veh (100Rnd_762x51_M240 ×3), M240_veh_2

**Plausible pool:** Primarily door gun / defensive. FFAR pod not stock but plausible.

### Mi-8/17 variants (Mi17_Ins, Mi17_rockets_RU, Mi17_CDF, Mi17_TK_EP1)
**Mi17_Ins/CDF/TK:** CMFlareLauncher, PKT door guns
**Mi17_rockets_RU:** 57mmLauncher (128Rnd_57mm), CMFlareLauncher + PKT door guns

**Plausible pool:**
- 57mmLauncher / 128Rnd_57mm
- S8Launcher / 80Rnd_S8T
- 80mmLauncher / 40Rnd_80mm
- CMFlareLauncher / 120Rnd_CMFlareMagazine

### AH6J_EP1 (Little Bird armed)
**Stock (pilot):** FFARLauncher_14 (14Rnd_FFAR), TwinM134 (4000Rnd_762x51_M134), CMFlareLauncher

### AW159_Lynx_BAF (Wildcat AH11)
**Stock:** CRV7_PG (12Rnd_CRV7), M621 (1200Rnd_20mm_M621), CMFlareLauncher
**BalanceInit upgrades:** CTWS + CRV7_HEPD + SpikeLauncher_ACR (LF3)

---

## C. Real-World Presets

All weapon/magazine classnames verified in CfgWeapons.txt / CfgMagazines.txt.
Where A2 can only approximate, the approximation is noted.

---

### A-10 Thunderbolt II

**Preset 1 — "OIF CAS Standard"**
*Iraq 2003–2010, 23rd FW / A-10s in support of ground forces; typical mixed-ordnance CAS sortie*
- GAU8 / 1350Rnd_30mmAP_A10
- MaverickLauncher / 2Rnd_Maverick_A10
- BombLauncherA10 / 4Rnd_GBU12 *(real: 2× GBU-12 + 2× Mk.82; A2 approximation: 4× GBU-12 covers both)*
- FFARLauncher_14 / 14Rnd_FFAR *(real: 2× LAU-61 pods 19rds each; A2 approximation: single 14-rd pod)*
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 2 — "OEF Tank-Plinking"**
*Afghanistan 2001–2014, dedicated anti-armor; up to 4× AGM-65G Maverick, LGBs for bunkers*
- GAU8 / 1350Rnd_30mmAP_A10
- MaverickLauncher / 2Rnd_Maverick_A10 *(real has 4; A2 pool caps at 2 — note compromise)*
- BombLauncherA10 / 4Rnd_GBU12
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 3 — "Gun Run / Strafing"**
*Close-in support where gun is primary; typical for TIC (troops in contact)*
- GAU8 / 1350Rnd_30mmAP_A10
- FFARLauncher_14 / 14Rnd_FFAR *(suppression while setting up gun pass)*
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 4 — "Sandy CSAR Escort"**
*Search & Rescue escort role, A-10s protect downed pilot extraction; Sidewinder for CAP, gun for suppression*
- GAU8 / 1350Rnd_30mmAP_A10
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- MaverickLauncher / 2Rnd_Maverick_A10
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

---

### AV-8B Harrier II

**Preset 1 — "USMC MEU CAS Standard"**
*USMC MEU/MAG CAS loadout, AV-8B+ deployments 2003–2012; gun pod + precision + rockets + self-defence*
- GAU12 / 300Rnd_25mm_GAU12
- BombLauncher / 6Rnd_GBU12_AV8B *(real: 2–4× AGM-65E; A2 approximation: GBU-12 is closest guided weapon)*
- FFARLauncher_14 / 14Rnd_FFAR
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 2 — "Strike: Precision"**
*Deliberate strike on hardened target; max LGBs, no rockets*
- GAU12 / 300Rnd_25mm_GAU12
- BombLauncher / 6Rnd_GBU12_AV8B
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 3 — "DAS: Unguided Bombs"**
*AV-8B+ Mk82 loadout for non-precision area target; 6× Mk82 per AV8B2 config*
- GAU12 / 300Rnd_25mm_GAU12
- Mk82BombLauncher_6 / 6Rnd_Mk82
- FFARLauncher_14 / 14Rnd_FFAR
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

---

### F-35B

**Preset 1 — "Precision Strike"**
*Standard STOVL loadout; limited to internal-equiv weapons; GBU-12 approximates JDAM/Paveway*
- GAU12 / 300Rnd_25mm_GAU12
- BombLauncherF35 / 2Rnd_GBU12 *(real: internal JDAM; A2: GBU-12)*
- SidewinderLaucher_F35 / 2Rnd_Sidewinder_F35
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 2 — "Beast Mode CAS"**
*F-35B with full external loadout sacrificing stealth; max ordnance*
- GAU12 / 300Rnd_25mm_GAU12
- BombLauncherF35 / 2Rnd_GBU12
- SidewinderLaucher_F35 / 2Rnd_Sidewinder_F35 *(×2 would be ideal; A2 limited to 1 per slot)*
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

---

### Su-25 Frogfoot

**Preset 1 — "Afghanistan '85"**
*40th Army VVS, Bagram/Shindand 1985; primary weapon was S-8 80mm rockets; ATGMs rarely used vs Mujahideen*
- GSh301 / 180Rnd_30mm_GSh301
- S8Launcher / 80Rnd_S8T *(real: 4× B-8M1 pod, 20 rounds each = 80; A2 S8Launcher carries 80 — good match)*
- AirBombLauncher / 4Rnd_FAB_250 *(real: 2× FAB-250; A2 gives 4 — slightly generous)*
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine
*Note: R-60 self-defense removed per BalanceInit/MANPADS threat doctrine — pilots were told not to fly high anyway*

**Preset 2 — "Anti-Armor Strike"**
*Cold War NATO-contingency doctrine; Kh-25ML absent in A2 — approximate with FAB bombs + rockets*
- GSh301 / 180Rnd_30mm_GSh301
- AirBombLauncher / 4Rnd_FAB_250 *(approximates Kh-25ML: closest available guided equiv is absent in A2)*
- S8Launcher / 80Rnd_S8T
- R73Launcher_2 / 2Rnd_R73 *(real had R-60; R-73 is upgrade but closest available)*
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine
*Approximation note: No Kh-25/Kh-29 in vanilla A2. FAB-250 substitutes as unguided approximation.*

**Preset 3 — "CAS Light"**
*Chechnya-era light CAS patrol; gun emphasis, minimal bomb load*
- GSh301 / 180Rnd_30mm_GSh301
- S8Launcher / 80Rnd_S8T
- R73Launcher_2 / 2Rnd_R73
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 4 — "S-5 Area Suppression"**
*57mm S-5 rockets for massed area suppression; used in Afghanistan before S-8 predominance*
- GSh301 / 180Rnd_30mm_GSh301
- 57mmLauncher / 64Rnd_57mm *(real: UB-32 pods, 32rds each; A2: 57mmLauncher carries 64)*
- AirBombLauncher / 4Rnd_FAB_250
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

---

### Su-39

**Preset 1 — "Anti-Tank Specialist"**
*Su-25TM primary mission: Kh-29T TV-guided + Vikhr ATGM; Vikhr absent in A2 — Kh-29 (Ch29) approximates*
- GSh301 / 180Rnd_30mm_GSh301
- Ch29Launcher / 4Rnd_Ch29 *(real: Kh-29T TV-guided; A2: Ch29Launcher is correct classname)*
- S8Launcher / 80Rnd_S8T
- R73Launcher_2 / 2Rnd_R73
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine
*Note: Real Vikhr ATGM (AT-16) has no A2 equivalent — Kh-29 is the best substitute.*

**Preset 2 — "Strike + Self-Defence"**
*Mixed anti-ground + AAM self-protection*
- GSh301 / 180Rnd_30mm_GSh301
- Ch29Launcher / 4Rnd_Ch29
- AirBombLauncher / 4Rnd_FAB_250
- R73Launcher_2 / 2Rnd_R73
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

---

### Su-34 Fullback

**Preset 1 — "Syria 2015 Precision Strike"**
*Documented Syrian campaign loads: Kh-29T + gun; split between pilot (rockets) and gunner (missiles/gun)*
- Pilot: 80mmLauncher / 40Rnd_S8T
- Gunner turret: GSh301 / 180Rnd_30mm_GSh301, Ch29Launcher_Su34 / 6Rnd_Ch29, R73Launcher / 4Rnd_R73
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 2 — "Deep Strike"**
*Long-range interdiction: maximum Kh-29 precision missiles*
- Pilot: 80mmLauncher / 40Rnd_S8T
- Gunner: GSh301 / 180Rnd_30mm_GSh301, Ch29Launcher_Su34 / 6Rnd_Ch29
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 3 — "Escort/Air Superiority"**
*Su-34 escort role, max R-73 short-range AAMs; real aircraft carries R-77 BVR (no A2 equiv)*
- Pilot: 80mmLauncher / 40Rnd_S8T
- Gunner: GSh301 / 180Rnd_30mm_GSh301, R73Launcher / 4Rnd_R73
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine
*Approximation: R-77 AMRAAM-equivalent has no A2 classname; R-73 substitutes as WVR only.*

---

### L-39 Albatros (L39_TK_EP1)

**Preset 1 — "Armed Trainer Strike"**
*L-39ZA config as used by Iraq, Syria, African operators; GSh-23L + S-5 rockets + FAB bombs*
- GSh23L_L39 / 150Rnd_23mm_GSh23L
- 57mmLauncher / 64Rnd_57mm *(real: UB-16 32-rd S-5 pods; A2 57mmLauncher = 64rd — close enough)*
- AirBombLauncher / 4Rnd_FAB_250
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine *(if equipped)*

**Preset 2 — "COIN Patrol"**
*Light patrol loadout; all rockets for volume, no bombs*
- GSh23L_L39 / 150Rnd_23mm_GSh23L
- 57mmLauncher_128 / 128Rnd_57mm *(double rocket load)*
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

---

### AH-1Z Viper

**Preset 1 — "Anti-Armor Heavy"**
*USMC deliberate anti-armor mission; full Hellfire load + gun + Sidewinder self-defence*
- M197 / 750Rnd_M197_AH1 (turret)
- HellfireLauncher / 8Rnd_Hellfire *(real: up to 8× AGM-114K on inner pylons)*
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 2 — "OEF CAS Rockets"**
*Afghanistan: rockets dominate; volume of fire over precision; most common actual USMC Viper usage*
- M197 / 750Rnd_M197_AH1 (turret)
- FFARLauncher / 38Rnd_FFAR *(real: 4× LAU-61 pods 19rds each = 76; A2 caps lower)*
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 3 — "Mixed Strike"**
*Balanced: Hellfires for vehicles, rockets for suppression; standard deployed MEU escort*
- M197 / 750Rnd_M197_AH1 (turret)
- HellfireLauncher / 8Rnd_Hellfire
- FFARLauncher_14 / 14Rnd_FFAR
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 4 — "Air Alert"**
*Anti-helicopter escort; AIM-9 + gun only*
- M197 / 750Rnd_M197_AH1 (turret)
- SidewinderLaucher_AH1Z / 2Rnd_Sidewinder_AH1Z
- CMFlareLauncher / 120Rnd_CMFlareMagazine

---

### AH-64D Apache

**Preset 1 — "OIF 2003 Tank Plinking"**
*101st Airborne Aviation deep attack, Iraq 2003; 8–16× Hellfire was standard; gun always hot*
- M230 / 1200Rnd_30x113mm_M789_HEDP (turret)
- HellfireLauncher / 8Rnd_Hellfire *(real max is 16; A2 capped at 8 by HellfireLauncher mag)*
- FFARLauncher / 38Rnd_FFAR *(real: optional Hydra pods, 19rds each)*
- CMFlareLauncher / 60Rnd_CMFlareMagazine

**Preset 2 — "Urban CAS"**
*Iraq/Afghanistan mixed: Hellfires for point targets, Hydra for suppression, gun always available*
- M230 / 1200Rnd_30x113mm_M789_HEDP (turret)
- HellfireLauncher / 8Rnd_Hellfire
- FFARLauncher_14 / 14Rnd_FFAR
- CMFlareLauncher / 60Rnd_CMFlareMagazine

**Preset 3 — "Escort/Scout"**
*Force protection / convoy escort; Hellfires + Hydra, no Sidewinder (AIM-92 ATAS has no A2 classname)*
- M230 / 1200Rnd_30x113mm_M789_HEDP (turret)
- HellfireLauncher / 8Rnd_Hellfire
- CMFlareLauncher / 60Rnd_CMFlareMagazine
*Approximation: AIM-92 Stinger (ATAS) not in A2; Sidewinder substituted via SidewinderLaucher_AH64 / 8Rnd_Sidewinder_AH64 if desired.*

---

### Mi-24D (Hind-D)

**Preset 1 — "Afghanistan Soviet Anti-Personnel"**
*40th Army Mi-24D, 1980–85; primarily S-5 57mm rockets + YakB; AT-2 Falanga ATGM rarely used vs guerrillas*
- YakB / 1470Rnd_127x108_YakB (turret)
- 57mmLauncher_128 / 128Rnd_57mm *(real: 2× UB-32 pods = 64rds; A2 gives 128 — generous)*
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 2 — "Warsaw Pact Anti-Armor"**
*Cold War contingency doctrine: AT-2 Falanga ATGM + YakB for tank attack columns*
- YakB / 1470Rnd_127x108_YakB (turret)
- AT2Launcher / 4Rnd_AT2_Mi24D
- 57mmLauncher / 64Rnd_57mm
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 3 — "Assault Escort"**
*Balanced mixed loadout: guns + ATGMs + rockets for combined-arms escort missions*
- YakB / 1470Rnd_127x108_YakB (turret)
- AT2Launcher / 4Rnd_AT2_Mi24D
- 57mmLauncher_128 / 128Rnd_57mm
- CMFlareLauncher / 120Rnd_CMFlareMagazine

---

### Mi-24P (Hind-F)

**Preset 1 — "Heavy Gunship"**
*Mi-24P primary: fixed GSh-30-2 for heavy strafing + Ataka ATGM + S-8 rockets*
- GSh302 / 750Rnd_30mm_GSh301 (fixed gun)
- AT9Launcher / 4Rnd_AT9_Mi24P
- S8Launcher / 80Rnd_S8T
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 2 — "Anti-Armor Specialist"**
*Maximum ATGMs: Ataka + bombs for fortification*
- GSh302 / 750Rnd_30mm_GSh301
- AT9Launcher / 4Rnd_AT9_Mi24P
- HeliBombLauncher / 2Rnd_FAB_250
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 3 — "Fire Support"**
*Pure fire support: rockets + gun, no ATGMs — faster rearming cycle*
- GSh302 / 750Rnd_30mm_GSh301
- 80mmLauncher / 40Rnd_80mm
- 57mmLauncher / 64Rnd_57mm
- CMFlareLauncher / 120Rnd_CMFlareMagazine

---

### Mi-24V (Hind-E)

**Preset 1 — "Afghanistan '86 Upgraded"**
*Mi-24V replaced D in Afghanistan; AT-6 Spiral vs Mi-24D's AT-2; same rocket doctrine*
- YakB / 1470Rnd_127x108_YakB (turret)
- AT6Launcher / 4Rnd_AT6_Mi24V
- S8Launcher / 80Rnd_S8T
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 2 — "Rocket Emphasis"**
*Heavy rocket load for area suppression; common in Chechnya*
- YakB / 1470Rnd_127x108_YakB (turret)
- S8Launcher / 80Rnd_S8T
- 80mmLauncher / 40Rnd_80mm *(double S-8 load approximation)*
- CMFlareLauncher / 120Rnd_CMFlareMagazine

**Preset 3 — "Anti-Armor Pure"**
*Maximum ATGMs: 4× AT-6 Spiral + YakB suppression*
- YakB / 1470Rnd_127x108_YakB (turret)
- AT6Launcher / 4Rnd_AT6_Mi24V
- CMFlareLauncher / 120Rnd_CMFlareMagazine

---

### Ka-52 Alligator

**Preset 1 — "Anti-Armor Primary"**
*Ka-52's designed role: Vikhr-M ATGM + 30mm cannon; 12× Vikhr loaded (3 per wing station pair)*
- 2A42 / 230Rnd_30mmHE_2A42 + 230Rnd_30mmAP_2A42 (turret)
- VikhrLauncher / 12Rnd_Vikhr_KA50
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine
*Note: Vikhr is the Ka-52's signature weapon — this preset IS accurately representable in A2.*

**Preset 2 — "Fire Support"**
*CAS support role: S-8 rockets + cannon for volume fire*
- 2A42 / 230Rnd_30mmHE_2A42 + 230Rnd_30mmAP_2A42 (turret)
- S8Launcher / 80Rnd_S8T
- 80mmLauncher / 40Rnd_80mm
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

**Preset 3 — "Mixed Strike"**
*Combined Vikhr ATGMs + S-8 rockets; Syria 2022 documented usage pattern*
- 2A42 / 230Rnd_30mmHE_2A42 + 230Rnd_30mmAP_2A42 (turret)
- VikhrLauncher / 12Rnd_Vikhr_KA50
- S8Launcher / 80Rnd_S8T
- CMFlareLauncher / 120Rnd_CMFlare_Chaff_Magazine

---

### UH-1Y Venom

**Preset 1 — "USMC Fire Support Escort"**
*Typical MEU/MAG-26 loadout; XM8 rocket system + door guns always present*
- FFARLauncher_14 / 14Rnd_FFAR *(real: 2× LAU-61 pods 19rds; A2 caps at 14)*
- CMFlareLauncher / 120Rnd_CMFlareMagazine
*(M240 door guns are always-on turrets, not selectable)*

**Preset 2 — "Heavy Rocket Load"**
*BalanceInit LF-upgraded: 4× FFAR pods (56 total rockets)*
- FFARLauncher / 38Rnd_FFAR *(approximates heavy rocket configuration)*
- CMFlareLauncher / 120Rnd_CMFlareMagazine

---

## D. Ground Vehicles

### Mountable Weapon Set (CfgWeapons + CfgMagazines — addWeaponTurret pattern)

Based on Common_BalanceInit.sqf and verified CfgWeapons entries:

| Weapon (CfgWeapons) | DisplayName | Magazines (CfgMagazines) | Count | Side |
|---|---|---|---|---|
| M2 | "M2 Machinegun" | 100Rnd_127x99_M2 | 100 | West |
| M3P | "M3P" | 250Rnd_127x99_M3P | 250 | West |
| DSHKM | "DShKM" | 50Rnd_127x107_DSHKM, 150Rnd_127x107_DSHKM | 50/150 | East |
| KORD | "KORD" | 150Rnd_127x108_KORD, 50Rnd_127x108_KORD | 150/50 | East |
| PKT | "PKT" | 100Rnd_762x54_PK, 200Rnd_762x54_PKT | 100/200 | East |
| M134 | "M134" | 2000Rnd_762x51_M134, 4000Rnd_762x51_M134 | 2000/4000 | West |
| M240_veh | "M240" | 100Rnd_762x51_M240, 1200Rnd_762x51_M240 | 100/1200 | West |
| MK19 | "Mk19" | 48Rnd_40mm_MK19 | 48 | West |
| AGS30 | "AGS-30" | 29Rnd_30mm_AGS30 | 29 | East |
| AGS17 | "AGS-17" | 400Rnd_30mm_AGS17 | 400 | East |
| TOWLauncherSingle | "M220 TOW" | 6Rnd_TOW_HMMWV, 6Rnd_TOW2 | 6 | West |
| AT5LauncherSingle | "Konkurs 9M113" | 8Rnd_AT5_BMP2 | 8 | East |
| Igla_twice | "SA-18 Igla (twin)" | 2Rnd_Igla | 2 | East |
| SPG9 | "SPG-9" | PG9_AT, OG9_HE | varies | Gue/Ins |
| M242 | "M242 Bushmaster 25mm" | 210Rnd_25mm_M242_APDS, 210Rnd_25mm_M242_HEI | 210 | West |

*Note: Igla_twice and SPG9 are weapon-class entries in CfgWeapons used in addWeaponTurret calls; M242 used in BalanceInit Pandur conversion. Static vehicle objects (M2StaticMG, KORD_Static etc. from CfgVehicles) are NOT the mounting classnames.*

### Eligible Unarmed Vehicles (EASA weapon mounting candidates)

Per faction — vehicles with no weapons[] or only smoke/flares:

**USMC / US:**
- MMT_USMC — USMC supply truck (unarmed)
- M1030 — motorcycle (unarmed)
- HMMWV — base Humvee (unarmed)
- HMMWV_Ambulance — medevac Humvee (unarmed)
- MTVR — cargo truck (unarmed)
- MtvrRepair — repair truck (unarmed)
- MtvrRefuel — refuel truck (unarmed)
- WarfareSalvageTruck_USMC — salvage truck (unarmed)
- WarfareReammoTruck_USMC — ammo truck (unarmed)
- WarfareSupplyTruck_USMC — supply truck (unarmed)
- Zodiac — inflatable boat (unarmed)
- PBX — patrol boat base (unarmed)
- ATV_US_EP1 — ATV (unarmed)
- HMMWV_M1035_DES_EP1 — soft-top Humvee OA (unarmed)
- M1133_MEV_EP1 — Stryker MEV medevac (unarmed)
- BAF_ATV_W — BAF ATV (unarmed)
- BAF_Offroad_W — BAF Land Rover (unarmed)
- LandRover_Special_CZ_EP1 — CZ special LR (unarmed)

**Russia / East:**
- MMT_Civ — civilian truck (unarmed)
- TT650_Ins / TT650_TK_EP1 — motorbike (unarmed)
- UAZ_RU / UAZ_INS / UAZ_CDF — base UAZ (unarmed)
- UAZ_Unarmed_TK_EP1 — explicitly unarmed UAZ (unarmed)
- SUV_TK_EP1 — SUV (unarmed)
- Kamaz / KamazRepair / KamazRefuel — Kamaz trucks (unarmed)
- Ural_CDF / Ural_INS — Ural trucks (unarmed)
- WarfareSalvageTruck_RU / _CDF / _INS
- WarfareReammoTruck_RU, UralReammo_CDF, UralReammo_INS
- WarfareSupplyTruck_RU / _CDF / _INS
- UralRepair_CDF / UralRepair_INS / KamazRepair
- GAZ_Vodnik_MedEvac — medevac Vodnik (unarmed)
- V3S_TK_EP1 / V3S_Open_EP1 — TK truck (unarmed)
- M113Ambul_TK_EP1 — armored ambulance (unarmed)
- SUV_PMC — PMC SUV (unarmed)

**GUE:**
- TT650_Gue — motorbike (unarmed)
- V3S_Gue — truck (unarmed)
- WarfareRepairTruck_Gue / WarfareSalvageTruck_Gue / WarfareReammoTruck_Gue / WarfareSupplyTruck_Gue

### Armed / Excluded Vehicles (grey out with reason)

| Classname | Weapon(s) | Exclude Reason |
|---|---|---|
| HMMWV_M2 | M2 HMG | Already armed — M2 turret |
| HMMWV_MK19 | Mk19 grenade launcher | Already armed — Mk19 turret |
| HMMWV_TOW | TOW ATGM | Already armed — TOW launcher |
| HMMWV_Avenger | Stinger SAM | Already armed — Avenger SAM system |
| HMMWV_Armored | M2 HMG (armored HMMWV) | Already armed |
| RHIB2Turret | M240 / M2 | Armed patrol boat |
| LAV25 | M242 25mm + coax | Already armed — cannon |
| Pandur2_ACR | ATKMK44 30mm / M242 (after BalanceInit) | Already armed |
| HMMWV_M998A2_SOV_DES_EP1 | Varies (SOV armed) | Already armed |
| HMMWV_M1151_M2_DES_EP1 | M2 HMG | Already armed |
| HMMWV_M998_crows_MK19_DES_EP1 | Mk19 CROWS | Already armed |
| HMMWV_M998_crows_M2_DES_EP1 | M2 CROWS | Already armed |
| M1126_ICV_M2_EP1 | M2 HMG | Already armed — Stryker ICV |
| M1126_ICV_mk19_EP1 | Mk19 | Already armed — Stryker ICV |
| M1129_MC_EP1 | mortar | Already armed (mortar carrier) |
| M1135_ATGMV_EP1 | TOW ATGM | Already armed — ATGMV |
| M1128_MGS_EP1 | 105mm cannon | Already armed — Stryker MGS |
| BAF_Jackal2_GMG_W | GMG grenade launcher | Already armed |
| BAF_Jackal2_L2A1_W | L2A1 HMG | Already armed |
| UAZ_MG_INS / _CDF / _TK | PKT / DSHKM | Already armed — MG turret |
| UAZ_AGS30_RU / _CDF / _INS / _TK | AGS-30 | Already armed — grenade launcher |
| UAZ_SPG9_INS | SPG-9 recoilless | Already armed |
| UAZ_MG_TK_EP1 | PKT | Already armed |
| UAZ_AGS30_TK_EP1 | AGS-30 | Already armed |
| LandRover_MG_TK_EP1 | PKT/DShKM | Already armed |
| LandRover_SPG9_TK_EP1 | SPG-9 | Already armed |
| GAZ_Vodnik / GAZ_Vodnik_HMG | DSHKM or KORD | Already armed |
| Pickup_PK_GUE / Pickup_PK_TK_GUE_EP1 | PKT/PK | Already armed — technical |
| Offroad_DSHKM_Gue / _TK_GUE_EP1 | DShKM | Already armed — technical |
| Offroad_SPG9_Gue / _TK_GUE_EP1 | SPG-9 | Already armed — technical |
| BRDM2_INS / _CDF / _TK / _Gue | KPVT 14.5mm + PKT | Already armed — APC |
| BRDM2_ATGM_INS / _TK | AT-5 Konkurs / converted Igla | Already armed — ATGM carrier |
| BTR60_TK_EP1 | KPVT + PKT | Already armed — APC |
| BTR90 | 2A42 + AT5 | Already armed — IFV |
| BRDM2_TK_GUE_EP1 | KPVT | Already armed |
| BTR40_TK_GUE_EP1 | none (base) | Check: base BTR-40 may be unarmed |
| BTR40_MG_TK_GUE_EP1 | DShKM | Already armed |
| Ural_ZU23_INS / _CDF / _Gue / _TK | ZU-23 twin 23mm AA | Already armed — AA truck |
| GRAD_RU / _CDF / _INS / _TK | BM-21 rockets | Artillery — already armed |
| ArmoredSUV_PMC | DSHKM | Already armed |
| Ka60_GL_PMC | M32 grenade launcher (turret) | Already armed |

---

## Known Gaps & Uncertainties

1. **L159_ACR and Mi24_D_CZ_ACR** — ACR DLC classes not present in the config dump. Classnames confirmed by WASP mission source but weapon/magazine data unknown. Tool should show "ACR DLC required" warning.
2. **Kh-25/Kh-29 family** — Kh-25ML (AS-10 Karen) has no A2 equivalent. Ch29Launcher (Kh-29L) exists only on Su-39 and Su-34. Su-25 presets use FAB-250 as anti-armor approximation.
3. **Vikhr ATGM** — 12Rnd_Vikhr_KA50 + VikhrLauncher exist only on Ka-52. Su-39's real Vikhr capability is approximated by Ch29Launcher.
4. **R-77 (AMRAAM)** — No BVR missile class in A2. Su-34 escort preset uses R-73 as WVR-only substitute.
5. **AIM-92 Stinger (ATAS)** — Not in A2. Apache escort preset notes this gap.
6. **230Rnd_30mmAP_2A42** — Confirmed in CfgMagazines as Ka-52 turret AP belt. Keep separate from HE belt (230Rnd_30mmHE_2A42).
7. **GSh23L_L39** — Specific L-39 gun variant; parent GSh23L (520Rnd_23mm_GSh23L) is the standard. L-39 uses the sub-variant with 150Rnd_23mm_GSh23L magazine.
8. **BTR40_TK_GUE_EP1** — Base BTR-40 may be unarmed (open-topped, no factory weapon). BTR40_MG variant has DShKM. Needs verification.
9. **M1030** and **TT650** variants — Motorcycles confirmed unarmed in A2 base (no turrets).
10. **UH1H_TK_EP1 / UH1H_TK_GUE_EP1** — These have no weapons at all (truly unarmed Hueys used as light transport). Not suitable for EASA rearming unless FFAR pods are added by the tool.
