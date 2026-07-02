# EASA Mechanics Research

**Source of truth:** `C:\Users\Steff\a2waspwarfare\Missions\[55-2hc]warfarev2_073v48co.chernarus\`
**Research date:** 2026-07-02

---

## 1. Data Model

### Global variables (set at end of EASA_Init.sqf line 668)

```sqf
missionNamespace setVariable ['WFBE_EASA_Vehicles',  _easaVehi];    // array of typeOf strings
missionNamespace setVariable ['WFBE_EASA_Loadouts',  _easaLoadout]; // array of per-vehicle preset arrays
missionNamespace setVariable ['WFBE_EASA_Default',   _easaDefault]; // array of per-vehicle default loadout
```

All three arrays are **parallel-indexed**: index `_i` in `WFBE_EASA_Vehicles` corresponds to index `_i` in `WFBE_EASA_Loadouts` and `WFBE_EASA_Default`.

### Per-vehicle registration block (EASA_Init.sqf)

```sqf
_easaVehi    = _easaVehi    + ['Su34'];
_easaDefault = _easaDefault + [[['Ch29Launcher_Su34','R73Launcher_2'],['6Rnd_Ch29','2Rnd_R73','2Rnd_R73']]];
_easaLoadout = _easaLoadout + [
[
  [16400,'FAB-250 (6) | GBU-12 (2) | Kh-29 (4) | R-73 (2)',
    [['AirBombLauncher','BombLauncherF35','Ch29Launcher_Su34','R73Launcher_2'],
     ['4Rnd_FAB_250','2Rnd_FAB_250','2Rnd_GBU12','4Rnd_Ch29','2Rnd_R73']]],
  ... more presets ...
]
];
```

Header comment: `/* [[Price], [Description], [Weapon, Ammos], [Weapon, Ammos]...] */`
The actual 4th element `_row select 3` is **not in the raw source** — it is computed at the bottom of EASA_Init.sqf (line 667) via a post-processing loop.

### Preset row structure (4 elements after init)

```
[
  <price: Integer>,                  -- element 0
  <description: String>,             -- element 1
  [                                  -- element 2
    [<weapon1>, <weapon2>, ...],     -- select 0: weapon classnames
    [<mag1>, <mag2>, ...]            -- select 1: magazine classnames (may repeat)
  ],
  <hasAAMissile: Boolean>            -- element 3 (set by post-processing loop)
]
```

The **post-processing loop** (EASA_Init.sqf line 667) iterates every loadout and every magazine, looks up `CfgAmmo >> <ammo> >> airLock == 1` and `inheritsFrom == MissileBase`. If any magazine in the preset's ammo list is an air-to-air missile, `_row select 3` is set to `true`.

### Default loadout structure

Same as element 2 of a preset row: `[[weapon1, weapon2], [mag1, mag2, ...]]`.

There is **no preset ID or name** in the default. It is only used to remove the factory-issued weapons before applying an EASA preset for the first time.

### `EASA_LoadoutCat.sqf`

This file does **not exist** in the mission. The "cat" presumably stood for "categories" in an early design but was never implemented. There is no per-category grouping of presets — all presets for a vehicle are one flat array.

---

## 2. Vehicle registry (all entries in EASA_Init.sqf)

| typeOf classname | Air frame label | Pylon count | Faction |
|---|---|---|---|
| `Su34` | Su-34 [AF5] | 10 | RU/CDF |
| `Su25_Ins` | Su-25A [AF3] | 6 | INS |
| `Su25_TK_EP1` | Su-25T [AF4] | 8 | TK |
| `Su39` | Su-39 [AF5] | 10 | RU |
| `L39_TK_EP1` | L-39 [AF3] | 4 | TK |
| `F35B` | F-35B [AF5] | 6 | US |
| `L159_ACR` | L-159 [AF3] | 6 | CZ/NATO |
| `A10` | A-10A [AF3] | 4 | US |
| `A10_US_EP1` | A-10C [AF4] | 8 | US |
| `AV8B` | AV-8B (LGB) [AF4] | 8 | USMC |
| `AV8B2` | AV-8B [AF5] | 8 | USMC |
| `Mi24_D_CZ_ACR` | Mi-24V CZ [AF3] | 4 | CZ |
| `AH64D` | AH-64D (TOW) [AF3] | 4 | US |
| `AH64D_EP1` | AH-64D (Hellfire) [AF4] | 4 | US |
| `BAF_Apache_AH1_D` | Apache AH1 [AF4] | 4 | BAF |
| `AH1Z` | AH-1Z [AF5] | 4 | US |
| `AW159_Lynx_BAF` | Wildcat AH11 [AF3] | 4 | BAF |
| `Mi24_V` | Mi-24V [AF3] | 4 | RU |
| `Mi24_P` | Mi-24P [AF3] | 4 | RU |
| `Ka52` | Ka-52 [AF4] | 8 | RU |
| `Ka52Black` | Ka-52 (Black) [AF5] | 4 | RU |

**All 21 vehicles are aircraft (Air or helicopter).** No ground vehicles are registered. No `isKindOf` checks are used; matching is by exact `typeOf` string comparison via array `find`.

### Airplanes vs helicopters

No distinction is drawn between planes and helicopters in the EASA code itself. The `AW159_Lynx_BAF` (Wildcat) is the **only exception** — it has a special-case in both `EASA_Equip.sqf` and `EASA_RemoveLoadout.sqf` that uses `addWeaponTurret`/`removeWeaponTurret` with turret path `[-1]` (the coaxial/secondary turret) instead of `addWeapon`/`removeWeapon`. This is because the Wildcat's weapons live on a secondary turret, not on the vehicle root. Every other aircraft uses the root-level weapon/magazine commands.

---

## 3. Equip Flow (`EASA_Equip.sqf`)

**Full file content** (Client\Module\EASA\EASA_Equip.sqf, 37 lines):

```sqf
Private ["_get", "_index", "_loadout", "_loadout_old", "_type", "_vehicle"];
_vehicle = _this select 0;
_index   = _this select 1;
// (_this select 2) is passed as `true` from GUI but never read — no-op

_type = (missionNamespace getVariable 'WFBE_EASA_Vehicles') find (typeOf _vehicle);

if (_type != -1) then {
    _get = _vehicle getVariable 'WFBE_EASA_Setup';

    if (isNil '_get') then {
        // First-ever EASA purchase: strip factory default loadout
        [_vehicle, (missionNamespace getVariable 'WFBE_EASA_Default') select _type] Call EASA_RemoveLoadout;
        _get = -1;
    } else {
        // Swap: strip previously-purchased EASA loadout
        _loadout_old = (((missionNamespace getVariable 'WFBE_EASA_Loadouts') select _type) select _get) select 2;
        [_vehicle, _loadout_old] Call EASA_RemoveLoadout;
    };

    _loadout = (((missionNamespace getVariable 'WFBE_EASA_Loadouts') select _type) select _index) select 2;

    if ((typeOf _vehicle) == "AW159_Lynx_BAF") then {
        {_vehicle addMagazineTurret [_x, [-1]]} forEach (_loadout select 1);
        {_vehicle addWeaponTurret  [_x, [-1]]} forEach (_loadout select 0);
    } else {
        {_vehicle addMagazine _x} forEach (_loadout select 1);
        {_vehicle addWeapon   _x} forEach (_loadout select 0);
    };

    if (_get != _index) then {_vehicle setVariable ["WFBE_EASA_Setup", _index, true]};
};
```

**Order:** magazines are added **before** weapons (for Wildcat turret path). For all others: `addMagazine` first in forEach, then `addWeapon`.

**`setVariable [..., true]`** broadcasts the new index to all machines (the third argument is `true` = global broadcast). This is the **only server round-trip**: no `publicVariable` or `PVF` is used. All weapon manipulation runs on the **client** (script executes locally via `createDialog`).

**No "locked while servicing"** mechanism exists in EASA — the dialog is simply closed (`closeDialog 0`) after purchase. Simultaneous use while the vehicle is in motion is not prevented at the EASA level (only the Service menu's rearm/repair checks `speed > 20`).

**Cost deduction** happens in `GUI_Menu_EASA.sqf` before calling `EASA_Equip`:
```sqf
if (_funds > (_row select 0)) then {
    [vehicle player, _index, true] Call EASA_Equip;
    -(_row select 0) Call ChangePlayerFunds;
```
Note: strict `>` (not `>=`), so a player needs strictly more money than the price.

### `EASA_RemoveLoadout.sqf` (strip sequence)

```sqf
// magazines first, then weapons
{_vehicle removeMagazine _x}     forEach (_loadout select 1);
{_vehicle removeWeapon   _x}     forEach (_loadout select 0);
// Wildcat path uses removeMagazineTurret/removeWeaponTurret [-1]
```

---

## 4. Eligibility for EASA

### Module enable

`WFBE_C_MODULE_WFBE_EASA` lobby parameter (Parameters.hpp line 375–380):
```hpp
class WFBE_C_MODULE_WFBE_EASA {
    title  = "$STR_WF_PARAMETER_EASA";
    values[] = {0,1};
    texts[] = {"$STR_WF_Disabled","$STR_WF_Enabled"};
    default = 1;
};
```
Default is `1` (enabled). Init_CommonConstants.sqf line 235: `if (isNil "WFBE_C_MODULE_WFBE_EASA") then {WFBE_C_MODULE_WFBE_EASA = 1}`.

### Upgrade unlock

`WFBE_UP_EASA = 15` (Init_CommonConstants.sqf line 52). EASA costs **$4,000** to unlock (Upgrades_CO_US.sqf line 46: `[[4000,0]]`). Its prerequisite is `WFBE_UP_AIR` (air factory upgrade). It is available to all factions that have aircraft (US, RU, CDF, TK, etc.). INS and GUE factions also have it in their upgrade files.

### Per-use eligibility (GUI_Menu_Service.sqf lines 150–164)

```sqf
if ((missionNamespace getVariable "WFBE_C_MODULE_WFBE_EASA") > 0) then {
    _enable = false;
    _currentUpgrades = (sideJoined) Call WFBE_CO_FNC_GetSideUpgrades;
    _easaLevel = _currentUpgrades select WFBE_UP_EASA;
    if (!(isNull _csp) && _easaLevel > 0) then {
        if (player distance _csp < (missionNamespace getVariable "WFBE_C_UNITS_SUPPORT_RANGE")) then {
            if (typeOf(vehicle player) in (missionNamespace getVariable 'WFBE_EASA_Vehicles')) then {
                if (driver (vehicle player) == player) then {_enable = true};
            };
        };
    };
    ctrlEnable [20010,_enable];
```

**All conditions for the EASA button to be enabled:**
1. `WFBE_C_MODULE_WFBE_EASA > 0` (module param)
2. EASA upgrade purchased by the team (`_easaLevel > 0`)
3. A service point (`_csp`) exists and is not null
4. Player is within `WFBE_C_UNITS_SUPPORT_RANGE` (70 m) of the service point
5. Player's vehicle `typeOf` is in `WFBE_EASA_Vehicles`
6. Player is the **driver** of the vehicle

`_csp` is the side's **air/vehicle service point building** (`WFBE_%1SERVICEPOINTTYPE`). No town-center path, no repair-truck path for EASA. EASA is **only available at the service point building**.

---

## 5. Service Points

**For EASA specifically** (GUI_Menu_Service.sqf line 144–148, 154–155):

```sqf
_sp = [sideJoined, missionNamespace getVariable Format["WFBE_%1SERVICEPOINTTYPE",sideJoinedText], _buildings] Call GetFactories;
if (count _sp > 0) then {_csp = [vehicle player, _sp] Call WFBE_CO_FNC_GetClosestEntity};
// ...
if (!(isNull _csp) && _easaLevel > 0) then {
    if (player distance _csp < 70) then { ... _enable = true };
```

EASA only works at the **service point building** (the air hangar/service building per faction). Not at depots, not at repair trucks.

**Regular rearm/repair/refuel** in the same dialog checks: service point OR depot (`WFBE_CL_FNC_GetClosestDepot`) OR repair trucks within `WFBE_C_UNITS_REPAIR_TRUCK_RANGE`. But these have nothing to do with EASA.

---

## 6. Export Target for the Web Tool

### What to emit

There is **no "preset" concept separate from the loadout entries** — every entry in `_easaLoadout[i]` IS a preset. A web tool that generates a new preset must emit a new array entry in the correct vehicle's loadout sub-array.

**Paste-ready SQF shape for a single new preset:**

```sqf
// Add to the vehicle's loadout array in EASA_Init.sqf
// File: Client\Module\EASA\EASA_Init.sqf
// Find the vehicle registration block, e.g. for Su-34:
//   _easaLoadout = _easaLoadout + [ [...existing presets...] ];
// Add a new row inside the vehicle's preset array:
[
  <price: Integer>,                        // e.g. 12000
  '<label: String>',                       // e.g. 'GBU-12 (4) | R-73 (2)'
  [
    ['<WeaponClass1>','<WeaponClass2>'],   // weapon classnames (addWeapon order)
    ['<MagClass1>','<MagClass2>']          // magazine classnames (addMagazine order)
  ]
  // The 4th element (AA missile flag) is COMPUTED automatically by the post-processing
  // loop at line 667 of EASA_Init.sqf — do NOT include it in source
]
```

**Where to edit:** `Client\Module\EASA\EASA_Init.sqf` only. The post-processing loop and the three `missionNamespace setVariable` calls at the end re-index everything automatically.

**If adding a new vehicle type** not currently in the list:
```sqf
_easaVehi    = _easaVehi    + ['NewVehicleClassname'];
_easaDefault = _easaDefault + [[['WeaponA'],['MagA','MagA']]];
_easaLoadout = _easaLoadout + [
[
  [5000,'Preset 1 label',[['WeaponA','WeaponB'],['MagA','MagB']]]
]
];
```
All three arrays must stay in sync (same insertion position).

---

## 7. Ground-Vehicle Weapon Mounting

### Current state in the mission

**No ground vehicle has EASA support.** All 21 entries in `WFBE_EASA_Vehicles` are aircraft. There is no `isKindOf "Car"` or `isKindOf "Tank"` path in any EASA script.

`Common_BalanceInit.sqf` does use `addWeapon`/`addWeaponTurret` on ground vehicles (e.g., line 344: BRDM-2, BTR-90, Pandur, T-34 Guerilla), but these are **balance adjustments on spawn**, not EASA.

### Arma 2 mechanics for `addWeapon` on a vehicle

When you call `vehicle addWeapon "SomeWeaponClass"` on a vehicle:
- The weapon is added to the **vehicle's root weapon list** (same slot pool as the vehicle's built-in weapons)
- By default this means the **driver-as-gunner** position for vehicles without a dedicated gunner turret (e.g., a plain Ural truck or an unarmed Land Rover)
- For vehicles WITH a main gunner turret, `addWeapon` adds to the **same root-level list** that includes the driver's weapons; it does NOT automatically route to the main turret gunner — that requires `addWeaponTurret [wpn, [turretIndex]]`

**The weapon cycling/HUD glitch explained:**

In Arma 2 OA, a vehicle's weapons are stored as a flat list. Adding a second weapon to a vehicle that already has one mounted weapon:
- Increases the list length unexpectedly — the HUD's weapon switch cycles through all entries including duplicates
- `reload _vehicle` / rearming via `setVehicleAmmo 1` will try to refill the **config-defined** magazine list for the turret, but the dynamically-added weapon has no matching config entry → the engine may fill it incorrectly or skip it, causing zero-ammo on the added weapon after the first rearm
- The AI gunner (if using a turret) will cycle to the added weapon and get confused if no magazine class is recognized for the turret's `Magazines[]` config array
- Multiple calls to `addWeapon` for the same weapon classname stack duplicate entries (the engine does not de-duplicate)

**The `addWeaponTurret [weapon, [turretIndex]]` path** (as used by `EASA_Equip.sqf` for the Wildcat at `[-1]`) targets a specific turret and avoids the driver-weapon confusion, but still has the rearm issue unless the config defines the magazine in the turret's `Magazines[]`.

`Common_RearmVehicle.sqf` at line ~15 reads `getArray (configFile >> "CfgVehicles" >> typeOf _vehicle >> "Turrets" >> "MainTurret" >> "Magazines")` to determine what to rearm — dynamically added weapons that are not in that config array will lose ammo on rearm.

### How EASA avoids the glitch for aircraft

EASA strips the **entire current loadout** before adding the new one (`EASA_RemoveLoadout` then `EASA_Equip`). This prevents weapon list accumulation. For aircraft pylon weapons, the Arma 2 engine stores them in the `Magazines[]` of the root vehicle config or the main turret's `Magazines[]`; `Common_RearmVehicle.sqf` reads those + the root vehicle magazines to rearm, then at line 65–68 re-applies the EASA preset:

```sqf
if ((missionNamespace getVariable "WFBE_C_MODULE_WFBE_EASA") > 0) then {
    if (_type in (missionNamespace getVariable 'WFBE_EASA_Vehicles')) then {
        _get = _vehicle getVariable 'WFBE_EASA_Setup';
        if !(isNil '_get') then {[_vehicle, _get] Call EASA_Equip};
    };
};
```

So the rearm sequence is: base rearm (config weapons) → re-apply EASA preset on top. This works cleanly for aircraft because the pylon weapons are designed to be swappable.

---

## 8. Constants and Parameters

| Name | Location | Default | Notes |
|---|---|---|---|
| `WFBE_C_MODULE_WFBE_EASA` | Parameters.hpp + Init_CommonConstants.sqf | `1` (enabled) | Lobby param; 0=disable, 1=enable |
| `WFBE_UP_EASA` | Init_CommonConstants.sqf:52 | `15` | Upgrade array index for EASA |
| `WFBE_C_GAMEPLAY_AIR_AA_MISSILES` | Init_CommonConstants.sqf:216 | `1` | 0=no AA ever, 1=AA with upgrade WFBE_UP_AIRAAM, 2=AA always |
| `WFBE_UP_AIRAAM` | Init_CommonConstants.sqf:56 | `19` | Upgrade index for AA missiles unlock |
| `WFBE_C_UNITS_SUPPORT_RANGE` | Init_CommonConstants.sqf:370 | `70` | Meters from service point for EASA access |
| EASA upgrade cost | Upgrades_CO_US.sqf:46 | `$4,000` | Requires `WFBE_UP_AIR` (air factory) prerequisite |

**AA missile filtering in the GUI** (GUI_Menu_EASA.sqf lines 14–26):
```sqf
switch (missionNamespace getVariable "WFBE_C_GAMEPLAY_AIR_AA_MISSILES") do {
    case 0: {if (_row select 3) then {_add = false}};
    case 1: {
        if ((_upgrades select WFBE_UP_AIRAAM) == 0 && (_row select 3)) then {_add = false};
    };
};
```
Presets containing AA missiles are hidden from the list if the module is disabled or the AIRAAM upgrade has not been purchased.

---

## 9. Gotchas and Tool-Designer Notes

### Magazine count and weapon count limits

No explicit cap is enforced in EASA. The de-facto limit is the number of **pylon slots** on the aircraft. The comment in EASA_Init.sqf says "Su-34 [AF5] - 10 pylons", but this is informational only — the engine does not enforce it. Over-adding will cause weapon list corruption (see §7).

Magazine duplication is intentional: `addMagazine` is called once per magazine class occurrence in the list. E.g., `['4Rnd_FAB_250','2Rnd_FAB_250','4Rnd_FAB_250','2Rnd_FAB_250']` calls `addMagazine` four times to simulate loading two pairs of bomb pylons. This is because `addMagazine` in A2OA adds one magazine slot per call, and some launchers (like `AirBombLauncher`) hold multiple launcher slots.

### The `_row select 3` AA missile flag is computed, not authored

Do not include the 4th element when writing new presets to the SQF file. The post-processing loop in EASA_Init.sqf line 667 sets it. If the web tool emits 4-element rows, they will be overwritten correctly by the loop but the code will look inconsistent.

### Strict cost check `>`

The GUI checks `_funds > (_row select 0)` not `>=`. A player must have strictly more than the loadout price. This is probably a bug but any tooling should match it for documentation purposes.

### `WFBE_EASA_Setup` variable persists through death / rearm

`setVariable [..., true]` makes it network-global and persistent for the vehicle object's lifetime. On rearm, `Common_RearmVehicle.sqf` reads this variable and re-applies the EASA preset automatically. It is NOT cleared on vehicle respawn (new vehicle object = nil variable = default loadout).

### No server-side validation

All EASA logic runs client-side. The cost deduction uses `ChangePlayerFunds` which presumably replicates. There is no server PVF call specific to EASA. This means a cheating client could call `EASA_Equip` without paying.

### `GUI_Menu_EASA.sqf` — third parameter to EASA_Equip is ignored

```sqf
[vehicle player, _index, true] Call EASA_Equip;
```
`EASA_Equip.sqf` only reads `_this select 0` and `_this select 1`. The `true` third argument is never used. Legacy artifact.

### The EASA button is on the Service menu, not standalone

The flow is: WF Menu → Service → EASA button (idc 20010) → closes service dialog → opens EASA dialog (`RscMenu_EASA`, idd 23000). The EASA button is only enabled when all eligibility checks pass (see §4).

---

## 10. Summary of Files Modified to Add a New Loadout

| File | What to change |
|---|---|
| `Client\Module\EASA\EASA_Init.sqf` | Only file needed: add a new row to the vehicle's preset array, or add a new vehicle block (3 parallel array entries) |

No changes needed to any other file for adding presets to existing vehicles. For a new vehicle type, additionally verify `Common_BalanceInit.sqf` handles its spawn-time weapon setup.
