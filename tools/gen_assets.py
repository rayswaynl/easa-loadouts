#!/usr/bin/env python3
"""Generate EASA Loadouts editor data from the arma2-co-config-reference repo.

Produces four JSON files in assets/data/:
  airframes.json   — aircraft (Plane/Helicopter) with scope=2, stock weapons/mags
                     gathered through vehicle root + Turrets tree + inheritance
  weapons.json     — vehicle-usable weapons (aircraft pylons + ground-vehicle mounts)
  magazines.json   — every magazine referenced by weapons.json, with airLock flag
  vehicles.json    — scope=2 ground vehicles: unarmed (eligible) and armed (excluded)

Mirrors the parsing approach of loadout-lab/tools/gen_assets.py:
  - Same stack-based _parse() for class hierarchy
  - Same _resolve_types() / _resolve_mags() memoized DFS
  - Same index_images() / copy_images() for thumbnails

Dependency-free (stdlib only).  Idempotent.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex patterns (same set as loadout-lab, extended with weapons[], count, ammo)
# ---------------------------------------------------------------------------

_FWD    = re.compile(r'^class\s+([A-Za-z0-9_]+)\s*(?::\s*[A-Za-z0-9_]+)?\s*;\s*$')
_HEAD   = re.compile(r'^class\s+([A-Za-z0-9_]+)\s*(?::\s*([A-Za-z0-9_]+))?\s*(\{)?\s*$')
_INLINE = re.compile(r'^class\s+([A-Za-z0-9_]+)\s*(?::\s*([A-Za-z0-9_]+))?\s*\{([^}]*)\}\s*;?\s*$')
_INLINE_NESTED = re.compile(r'^class\s+([A-Za-z0-9_]+)\s*(?::\s*([A-Za-z0-9_]+))?\s*\{.*\}\s*;?\s*$')

_DN          = re.compile(r'\bdisplayName\s*=\s*"((?:[^"\\]|\\.)*)"', re.IGNORECASE)
_TYPE        = re.compile(r'(?:^|;)\s*type\s*=\s*(.+?)\s*(?:;|$)')
_SCOPE       = re.compile(r'\bscope\s*=\s*(\d+)')
_FACTION     = re.compile(r'\bfaction\s*=\s*"([^"]*)"')
_SIDE        = re.compile(r'\bside\s*=\s*(\d+)')
_AIRLOCK     = re.compile(r'\bairLock\s*=\s*(\d+)')
_COUNT       = re.compile(r'\bcount\s*=\s*(\d+)')
_AMMO_FIELD  = re.compile(r'\bammo\s*=\s*"([^"]*)"')
_PICTURE     = re.compile(r'\bpicture\s*=\s*"([^"]*)"', re.IGNORECASE)

# magazines[] inline and multi-line (same as loadout-lab)
_MAGS_INLINE = re.compile(r'\bmagazines\[\]\s*(\+)?=\s*\{([^}]*)\}')
_MAGS_OPEN   = re.compile(r'\bmagazines\[\]\s*(\+)?=\s*\{')
# weapons[] inline and multi-line
_WEPS_INLINE = re.compile(r'\bweapons\[\]\s*(\+)?=\s*\{([^}]*)\}')
_WEPS_OPEN   = re.compile(r'\bweapons\[\]\s*(\+)?=\s*\{')

_QUOTED = re.compile(r'"([^"]+)"')


# ---------------------------------------------------------------------------
# Type evaluator (from loadout-lab)
# ---------------------------------------------------------------------------

def _eval_type(raw: str) -> int:
    raw = raw.strip().strip('"').strip("'")
    # Allow digits, whitespace, +
    if re.match(r'^[\d\s+]+$', raw):
        try:
            return int(eval(raw))  # safe: only digits + whitespace + +
        except Exception:
            pass
    try:
        return int(raw)
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Core parser — extended to also capture scope, faction, side, airLock, count,
# ammo, and a weapons[] array (parallel to magazines[]).
# ---------------------------------------------------------------------------

def _parse(text: str, *,
           want_type: bool = False,
           want_mags: bool = False,
           want_weps: bool = False,
           want_scope: bool = False,
           want_faction: bool = False,
           want_airlock: bool = False,
           want_count: bool = False,
           want_ammo: bool = False,
           ) -> dict:
    """Walk class blocks and return {classname: record}.

    Record keys (all may be absent depending on want_* flags):
      dn, parent, _type_raw, _mags_own, _mags_additive,
      _weps_own, _weps_additive,
      _scope, _faction, _side,
      _airlock_raw, _count_raw, _ammo_own
    """
    classes: dict[str, dict] = {}
    stack: list[dict] = []
    pending_name = None
    pending_parent = None

    # Collection state for multi-line arrays
    mags_collecting: bool = False
    mags_for_cls: str | None = None
    mags_additive: bool = False
    weps_collecting: bool = False
    weps_for_cls: str | None = None
    weps_additive: bool = False

    def _new_rec(parent=None):
        return {
            'dn': '', 'parent': parent,
            '_type_raw': None,
            '_mags_own': None, '_mags_additive': False,
            '_weps_own': None, '_weps_additive': False,
            '_scope': None, '_faction': None, '_side': None,
            '_airlock_raw': None, '_count_raw': None, '_ammo_own': None,
        }

    def _capture_fields(line: str, cls_name: str) -> None:
        rec = classes[cls_name]
        dn_m = _DN.search(line)
        if dn_m and not rec['dn']:
            rec['dn'] = dn_m.group(1)
        if want_type and rec['_type_raw'] is None:
            ty_m = _TYPE.search(line)
            if ty_m:
                rec['_type_raw'] = _eval_type(ty_m.group(1))
        if want_scope and rec['_scope'] is None:
            sc_m = _SCOPE.search(line)
            if sc_m:
                rec['_scope'] = int(sc_m.group(1))
        if want_faction:
            fa_m = _FACTION.search(line)
            if fa_m and rec['_faction'] is None:
                rec['_faction'] = fa_m.group(1)
            si_m = _SIDE.search(line)
            if si_m and rec['_side'] is None:
                rec['_side'] = int(si_m.group(1))
        if want_airlock and rec['_airlock_raw'] is None:
            al_m = _AIRLOCK.search(line)
            if al_m:
                rec['_airlock_raw'] = int(al_m.group(1))
        if want_count and rec['_count_raw'] is None:
            co_m = _COUNT.search(line)
            if co_m:
                rec['_count_raw'] = int(co_m.group(1))
        if want_ammo and rec['_ammo_own'] is None:
            am_m = _AMMO_FIELD.search(line)
            if am_m and am_m.group(1):
                rec['_ammo_own'] = am_m.group(1)
        if want_mags and rec['_mags_own'] is None:
            mag_m = _MAGS_INLINE.search(line)
            if mag_m:
                rec['_mags_own'] = _QUOTED.findall(mag_m.group(2))
                rec['_mags_additive'] = mag_m.group(1) == '+'
        if want_weps and rec['_weps_own'] is None:
            wep_m = _WEPS_INLINE.search(line)
            if wep_m:
                rec['_weps_own'] = _QUOTED.findall(wep_m.group(2))
                rec['_weps_additive'] = wep_m.group(1) == '+'

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # --- multi-line collection modes ---
        if mags_collecting:
            if line.startswith('}'):
                if stack:
                    stack.pop()
                mags_collecting = False
                mags_for_cls = None
            else:
                if mags_for_cls and want_mags:
                    for qm in _QUOTED.findall(line):
                        classes[mags_for_cls]['_mags_own'].append(qm)
            continue

        if weps_collecting:
            if line.startswith('}'):
                if stack:
                    stack.pop()
                weps_collecting = False
                weps_for_cls = None
            else:
                if weps_for_cls and want_weps:
                    for qw in _QUOTED.findall(line):
                        classes[weps_for_cls]['_weps_own'].append(qw)
            continue

        # Forward declaration
        m = _FWD.match(line)
        if m:
            classes.setdefault(m.group(1), _new_rec())
            continue

        # Single-line class body (no nested braces in body)
        m = _INLINE.match(line)
        if m:
            cls_name, parent, body = m.group(1), m.group(2), m.group(3)
            if cls_name not in classes:
                classes[cls_name] = _new_rec(parent)
            else:
                if parent is not None:
                    classes[cls_name]['parent'] = parent
            _capture_fields(body, cls_name)
            continue

        # Single-line class body with nested braces
        m = _INLINE_NESTED.match(line)
        if m:
            cls_name, parent = m.group(1), m.group(2)
            if cls_name not in classes:
                classes[cls_name] = _new_rec(parent)
            else:
                if parent is not None:
                    classes[cls_name]['parent'] = parent
            _capture_fields(line, cls_name)
            continue

        # Class header (possible inline '{')
        m = _HEAD.match(line)
        if m:
            cls_name = m.group(1)
            parent = m.group(2)
            has_brace = m.group(3) == '{'
            pending_name = cls_name
            pending_parent = parent
            classes.setdefault(cls_name, _new_rec(parent))
            if parent is not None:
                classes[cls_name]['parent'] = parent
            if has_brace:
                stack.append({'name': cls_name})
                pending_name = pending_parent = None
            continue

        # Bare open brace
        if line == '{':
            stack.append({'name': pending_name})
            pending_name = pending_parent = None
            continue

        # Line ending with '{' (array / sub-object opener)
        if line.endswith('{'):
            if stack and stack[-1]['name']:
                frame_cls = stack[-1]['name']
                # magazines[]
                if want_mags:
                    mag_m = _MAGS_OPEN.match(line)
                    if mag_m:
                        rec = classes[frame_cls]
                        if rec['_mags_own'] is None:
                            rec['_mags_own'] = []
                            rec['_mags_additive'] = mag_m.group(1) == '+'
                        mags_collecting = True
                        mags_for_cls = frame_cls
                        stack.append({'name': None})
                        pending_name = pending_parent = None
                        continue
                # weapons[]
                if want_weps:
                    wep_m = _WEPS_OPEN.match(line)
                    if wep_m:
                        rec = classes[frame_cls]
                        if rec['_weps_own'] is None:
                            rec['_weps_own'] = []
                            rec['_weps_additive'] = wep_m.group(1) == '+'
                        weps_collecting = True
                        weps_for_cls = frame_cls
                        stack.append({'name': None})
                        pending_name = pending_parent = None
                        continue
            stack.append({'name': None})
            pending_name = pending_parent = None
            continue

        # Close brace
        if line.startswith('}'):
            if stack:
                stack.pop()
            pending_name = pending_parent = None
            continue

        # Field line inside innermost named frame
        if stack and stack[-1]['name']:
            _capture_fields(line, stack[-1]['name'])

    return classes


# ---------------------------------------------------------------------------
# Inheritance resolvers (same logic as loadout-lab)
# ---------------------------------------------------------------------------

def _resolve_scalar(classes: dict, field_raw: str, field_resolved: str) -> None:
    """Generic memoized DFS resolver for a scalar field (int or string)."""
    resolved: dict = {}

    def resolve(name: str, seen: set):
        if name in resolved:
            return resolved[name]
        if name in seen:
            return None
        rec = classes.get(name)
        if rec is None:
            return None
        val = rec.get(field_raw)
        if val is not None:
            resolved[name] = val
            return val
        parent = rec.get('parent')
        if parent is None:
            resolved[name] = None
            return None
        val = resolve(parent, seen | {name})
        resolved[name] = val
        return val

    for name in classes:
        classes[name][field_resolved] = resolve(name, set())


def _resolve_types(classes: dict) -> None:
    resolved: dict[str, int] = {}

    def resolve(name: str, seen: set) -> int:
        if name in resolved:
            return resolved[name]
        if name in seen:
            return 0
        rec = classes.get(name)
        if rec is None:
            return 0
        if rec['_type_raw'] is not None:
            val = rec['_type_raw']
            resolved[name] = val
            return val
        parent = rec.get('parent')
        if parent is None:
            resolved[name] = 0
            return 0
        val = resolve(parent, seen | {name})
        resolved[name] = val
        return val

    for name in classes:
        classes[name]['_type_resolved'] = resolve(name, set())


def _resolve_mags(classes: dict) -> None:
    """Resolve magazines[] through inheritance chain (with += additive support)."""
    resolved: dict[str, list] = {}

    def resolve(name: str, seen: set) -> list:
        if name in resolved:
            return resolved[name]
        if name in seen:
            return []
        rec = classes.get(name)
        if rec is None:
            return []
        own = rec.get('_mags_own')
        additive = rec.get('_mags_additive', False)
        parent = rec.get('parent')

        if own is not None and not additive:
            resolved[name] = own
            return own

        parent_mags: list = []
        if parent is not None:
            parent_mags = resolve(parent, seen | {name})

        if own is None:
            val = parent_mags
        else:
            val = parent_mags + own

        resolved[name] = val
        return val

    for name in classes:
        classes[name]['_mags_resolved'] = resolve(name, set())


def _resolve_weps(classes: dict) -> None:
    """Resolve weapons[] through inheritance chain."""
    resolved: dict[str, list] = {}

    def resolve(name: str, seen: set) -> list:
        if name in resolved:
            return resolved[name]
        if name in seen:
            return []
        rec = classes.get(name)
        if rec is None:
            return []
        own = rec.get('_weps_own')
        additive = rec.get('_weps_additive', False)
        parent = rec.get('parent')

        if own is not None and not additive:
            resolved[name] = own
            return own

        parent_weps: list = []
        if parent is not None:
            parent_weps = resolve(parent, seen | {name})

        if own is None:
            val = parent_weps
        else:
            val = parent_weps + own

        resolved[name] = val
        return val

    for name in classes:
        classes[name]['_weps_resolved'] = resolve(name, set())


# ---------------------------------------------------------------------------
# Image helpers (identical to loadout-lab)
# ---------------------------------------------------------------------------

def index_images(images_root: Path) -> dict:
    """Map {classname: source_path} for every <classname>.jpg under Images/."""
    idx: dict[str, Path] = {}
    for p in images_root.rglob('*.jpg'):
        idx.setdefault(p.stem, p)
    return idx


def copy_images(classnames, idx: dict, dest: Path) -> tuple[list, list]:
    """Copy <cls>.jpg for each classname that has art. Returns (copied, missing)."""
    dest.mkdir(parents=True, exist_ok=True)
    copied, missing = [], []
    for cls in sorted(classnames):
        src = idx.get(cls)
        if src:
            shutil.copyfile(src, dest / f'{cls}.jpg')
            copied.append(cls)
        else:
            missing.append(cls)
    return copied, sorted(missing)


# ---------------------------------------------------------------------------
# Ancestry helpers
# ---------------------------------------------------------------------------

def _ancestors(name: str, classes: dict) -> list[str]:
    """Return the ancestor chain [parent, grandparent, ...] for a class."""
    chain = []
    seen = set()
    cur = classes.get(name, {}).get('parent')
    while cur and cur not in seen:
        chain.append(cur)
        seen.add(cur)
        cur = classes.get(cur, {}).get('parent')
    return chain


def _is_descendant_of(name: str, targets: set, classes: dict,
                       _cache: dict | None = None) -> bool:
    """Return True if name is in targets or any ancestor is in targets."""
    if _cache is None:
        _cache = {}
    if name in _cache:
        return _cache[name]
    if name in targets:
        _cache[name] = True
        return True
    seen: set = set()
    cur = name
    while cur:
        if cur in seen:
            break
        seen.add(cur)
        if cur in targets:
            _cache[name] = True
            return True
        cur = classes.get(cur, {}).get('parent')
    _cache[name] = False
    return False


def _resolve_field(name: str, field: str, classes: dict):
    """Walk ancestry to find the first non-None value for a simple field."""
    seen: set = set()
    cur = name
    while cur:
        if cur in seen:
            break
        seen.add(cur)
        rec = classes.get(cur)
        if rec is None:
            break
        val = rec.get(field)
        if val is not None:
            return val
        cur = rec.get('parent')
    return None


# ---------------------------------------------------------------------------
# Weapon / magazine / ammo parsers
# ---------------------------------------------------------------------------

def parse_weapons_full(text: str) -> dict:
    """Parse CfgWeapons → {cls: {dn, type, mags}}."""
    raw = _parse(text, want_type=True, want_mags=True)
    _resolve_types(raw)
    _resolve_mags(raw)
    result: dict[str, dict] = {}
    for cls, rec in raw.items():
        result[cls] = {
            'dn': rec['dn'],
            'type': rec.get('_type_resolved') or 0,
            'mags': rec.get('_mags_resolved') or [],
        }
    return result


def parse_magazines_full(text: str) -> dict:
    """Parse CfgMagazines → {cls: {dn, count, ammo}} with resolved inheritance."""
    raw = _parse(text, want_mags=False, want_count=True, want_ammo=True)
    # resolve count, ammo, and dn through inheritance
    _resolve_scalar(raw, '_count_raw', '_count_resolved')
    _resolve_scalar(raw, '_ammo_own', '_ammo_resolved')
    # Resolve dn: use own dn if non-empty, else walk ancestry
    dn_resolved: dict[str, str] = {}

    def resolve_dn(name: str, seen: set) -> str:
        if name in dn_resolved:
            return dn_resolved[name]
        if name in seen:
            return ''
        rec = raw.get(name)
        if rec is None:
            return ''
        if rec.get('dn'):
            dn_resolved[name] = rec['dn']
            return rec['dn']
        parent = rec.get('parent')
        if parent is None:
            dn_resolved[name] = ''
            return ''
        val = resolve_dn(parent, seen | {name})
        dn_resolved[name] = val
        return val

    result: dict[str, dict] = {}
    for cls, rec in raw.items():
        result[cls] = {
            'dn': resolve_dn(cls, set()),
            'count': rec.get('_count_resolved') or 0,
            'ammo': rec.get('_ammo_resolved') or '',
        }
    return result


def parse_ammo_full(text: str) -> dict:
    """Parse CfgAmmo → {cls: {airLock}} resolving through inheritance."""
    raw = _parse(text, want_airlock=True)
    _resolve_scalar(raw, '_airlock_raw', '_airlock_resolved')
    result: dict[str, dict] = {}
    for cls, rec in raw.items():
        result[cls] = {
            'airLock': bool(rec.get('_airlock_resolved')),
        }
    return result


# ---------------------------------------------------------------------------
# Faction / side helpers
# ---------------------------------------------------------------------------

_SIDE_NAMES = {0: 'RU', 1: 'WEST', 2: 'IND', 3: 'CIV', 4: 'LOGIC'}

_FACTION_SIDE_MAP: dict[str, str] = {
    'RU': 'RU', 'CDF': 'CDF', 'INS': 'INS', 'GUE': 'GUE',
    'US': 'US', 'USMC': 'USMC', 'BIS_BAF': 'BAF',
    'TK': 'TK', 'TK_INS': 'TK_INS', 'TK_CIV': 'TK_CIV',
    'ACR': 'CZ', 'BIS_CZ': 'CZ', 'CZ': 'CZ',
    'UN': 'UN', 'BIS_UN': 'UN',
}


def _get_faction(rec: dict, classes: dict) -> str | None:
    """Walk ancestry to find faction/side, return a normalised faction string."""
    # Direct faction first
    fac = _resolve_field(rec.get('_cls', ''), '_faction', classes)
    if fac:
        return _FACTION_SIDE_MAP.get(fac, fac)
    side_val = _resolve_field(rec.get('_cls', ''), '_side', classes)
    if side_val is not None:
        return _SIDE_NAMES.get(side_val)
    return None


# ---------------------------------------------------------------------------
# Vehicles parser — parses vehicle root + all nested Turrets
# ---------------------------------------------------------------------------

# Weapon classes to exclude from "meaningful" weapons (smoke, horns, CM for ground)
_EXCLUDE_WEAPON_ROOTS = {'SmokeLauncher', 'CarHorn', 'CMFlareLauncher'}

# Aircraft base classes
_AIR_BASES = {'Plane', 'Helicopter', 'Air'}

# Ground base classes we care about
_GROUND_BASES = {'Car', 'Tank', 'Truck', 'Wheeled_APC', 'Tracked_APC',
                 'LandVehicle', 'Motorcycle'}


def _parse_vehicles_deep(text: str) -> dict:
    """Parse CfgVehicles, capturing scope, faction, side, root weapons/mags,
    and per-Turret weapons/mags.

    This is the most complex parser here because we need both the flat class
    hierarchy AND the per-vehicle Turrets sub-tree.  We do a two-level parse:

    Pass 1: standard _parse() to get class hierarchy, scope, faction, side,
            root-level weapons[], magazines[].
    Pass 2: for each vehicle with scope=2 and a relevant base class, extract
            Turrets weapons/magazines by scanning its raw text block.
    """
    # Pass 1 — full class hierarchy with root-level fields
    raw = _parse(text,
                 want_mags=True, want_weps=True,
                 want_scope=True, want_faction=True)
    _resolve_mags(raw)
    _resolve_weps(raw)
    _resolve_scalar(raw, '_scope', '_scope_resolved')
    _resolve_scalar(raw, '_faction', '_faction_resolved')
    _resolve_scalar(raw, '_side', '_side_resolved')

    return raw


def _extract_turret_weapons(text: str, cls_name: str) -> tuple[list[str], list[str], bool]:
    """Extract ALL weapons[] and magazines[] from the Turrets sub-tree of a vehicle.

    Returns (weapons_flat, mags_flat, has_turrets_block).
    has_turrets_block=True means the class itself declared a Turrets { } block
    (even if it is empty) — used by the chain-walker to stop inheritance early.
    """
    # Find start of this class body
    pattern = re.compile(
        r'\bclass\s+' + re.escape(cls_name) + r'\b[^{]*\{', re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return [], [], False

    # Find the full extent of this class body (brace-balanced)
    start = m.end() - 1  # position of the opening '{'
    depth = 0
    end = start
    for i in range(start, len(text)):
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    body = text[start:end + 1]

    # Find Turrets block within body (must be at class depth, i.e. not a nested Turrets
    # inside a sub-class like Sounds.  We look only in the top-level scope of the body.)
    ti = body.find('Turrets')
    if ti < 0:
        return [], [], False

    # Scan from start of Turrets for the opening '{'
    ti2 = body.find('{', ti)
    if ti2 < 0:
        return [], [], False

    # Brace-balance to find the Turrets block extent
    t_depth = 0
    t_end = ti2
    for i in range(ti2, len(body)):
        c = body[i]
        if c == '{':
            t_depth += 1
        elif c == '}':
            t_depth -= 1
            if t_depth == 0:
                t_end = i
                break
    turrets_block = body[ti2:t_end + 1]

    # Extract all weapons[] and magazines[] entries within the Turrets block
    wep_set: list[str] = []
    mag_set: list[str] = []
    seen_weps: set[str] = set()
    seen_mags: set[str] = set()

    for match in re.finditer(r'\bweapons\[\]\s*(?:\+)?=\s*\{([^}]*)\}', turrets_block):
        for q in _QUOTED.findall(match.group(1)):
            if q not in seen_weps:
                seen_weps.add(q)
                wep_set.append(q)

    for match in re.finditer(r'\bmagazines\[\]\s*(?:\+)?=\s*\{([^}]*)\}', turrets_block):
        for q in _QUOTED.findall(match.group(1)):
            if q not in seen_mags:
                seen_mags.add(q)
                mag_set.append(q)

    return wep_set, mag_set, True  # has_turrets_block=True


def _extract_turret_weapons_chain(text: str, cls_name: str,
                                   classes: dict) -> tuple[list[str], list[str]]:
    """Walk the inheritance chain to find Turrets weapons/mags.

    In A2 configs, a subclass (e.g. BRDM2_CDF : BRDM2_Base) often does NOT
    re-declare its own Turrets block and instead relies on the parent's Turrets
    being used at runtime.  We walk the chain and return the first non-empty
    turret weapon set found.

    STOP early if we encounter a class that HAS a Turrets block (even empty) —
    that is an explicit override (like UAZ_Unarmed_Base's empty Turrets {}).
    """
    seen: set[str] = set()
    cur: str | None = cls_name
    while cur and cur not in seen:
        seen.add(cur)
        tw, tm, has_block = _extract_turret_weapons(text, cur)
        if tw:
            return tw, tm
        if has_block:
            # Explicit empty Turrets block — this class overrides turrets to nothing.
            # Do NOT walk further up the chain.
            return [], []
        # No Turrets block in this class body — inherit from parent
        cur = classes.get(cur, {}).get('parent')
    return [], []


# ---------------------------------------------------------------------------
# Weapon category heuristic
# ---------------------------------------------------------------------------

_CATEGORY_RULES = [
    # (pattern, category)
    (re.compile(r'CM|Flare|Chaff', re.I),           'cm'),
    (re.compile(r'Horn', re.I),                      'horn'),
    (re.compile(r'Smoke', re.I),                     'smoke'),
    (re.compile(r'R73|R-73|Sidewinder|Stinger|AA_|9M311|Strela|_AA|AIM_|AIM9|AIM-9|AA\b', re.I), 'aam'),
    (re.compile(r'Bomb|FAB|GBU|Mk8[24]|BLG|OFAB', re.I), 'bomb'),
    (re.compile(r'Maverick|Ch29|Kh|AGM|ATGM|TOW|Hellfire|Vikhr|Kary|AT_', re.I), 'agm'),
    (re.compile(r'Rocket|FFAR|S8|S13|CRV7|Hydra|HEAT_R|B8|FAR|80mm|20Rnd_Rocket|Zuny', re.I), 'rockets'),
    (re.compile(r'GSh|GSH|GShG|M230|M197|30x|20x|23x|cannon|Vulcan|Phalanx', re.I), 'gun'),
    (re.compile(r'GAU|M61|M168|CIWS', re.I),         'gun'),
    (re.compile(r'M2|DShK|KPVT|NSV|PKT|KORD|PKM|M240|M60|MAG|GPMG|M134|Minigun|HMG|MG_', re.I), 'mg'),
    (re.compile(r'Mk19|AGS|GL_|M203|GMG|grenade', re.I), 'gl'),
    (re.compile(r'SPG|9M14|9M17|Milan|Kornet|_AT\b', re.I), 'at'),
    (re.compile(r'Launcher', re.I),                   'rockets'),
]


def _categorize_weapon(cls: str, mags: list[str], weapons_map: dict, ammo_map: dict) -> str:
    """Best-effort category from classname, magazine classnames, and ammo type."""
    # Check ammo airLock for any magazine
    for mag in mags:
        ammo_cls = weapons_map.get(mag, {}).get('ammo', '')
        if ammo_cls and ammo_map.get(ammo_cls, {}).get('airLock'):
            return 'aam'

    for pattern, cat in _CATEGORY_RULES:
        if pattern.search(cls):
            return cat
        for mag in mags[:3]:  # only check first few mags
            if pattern.search(mag):
                return cat

    return 'other'


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

# Weapons that are noise/utility only — excluded from "real" vehicle weapon lists
_EXCLUDE_WEP_CLASSES = {
    'SmokeLauncher', 'CMFlareLauncher', 'CarHorn',
    # Some vehicles have an empty-string or base Default weapon slot
    'Default',
}

# Any class whose name starts with these are excluded
_EXCLUDE_WEP_PREFIXES = ('Horn', 'Smoke', 'CMFlare', 'Flare')


def _is_noise_weapon(cls: str, weapon_types: dict) -> bool:
    """Return True if this weapon is a smoke/horn/CM/utility (not a combat weapon)."""
    if cls in _EXCLUDE_WEP_CLASSES:
        return True
    for p in _EXCLUDE_WEP_PREFIXES:
        if cls.startswith(p):
            return True
    # Check inherited type — horns/smoke have type=0 or very specific type
    # CMFlareLauncher inherits from SmokeLauncher which is type 1+4=5
    # This heuristic: weapons that are NOT in weapons_map at all are unknown
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description='Generate EASA Loadouts asset data.')
    ap.add_argument('--ref', default='../arma2-co-config-reference',
                    help='path to arma2-co-config-reference repo root')
    ap.add_argument('--out', default='.',
                    help='path to easa-loadouts repo root')
    ap.add_argument('--verbose', '-v', action='store_true')
    args = ap.parse_args(argv)

    ref = Path(args.ref)
    out = Path(args.out)

    cfg_dir = ref / 'Config'
    img_root = ref / 'Images'
    data_dir = out / 'assets' / 'data'
    img_dest = out / 'assets' / 'img'
    data_dir.mkdir(parents=True, exist_ok=True)

    print('Reading config files...')
    vehicles_txt  = (cfg_dir / 'CfgVehicles.txt').read_text(encoding='utf-8', errors='replace')
    weapons_txt   = (cfg_dir / 'CfgWeapons.txt').read_text(encoding='utf-8', errors='replace')
    magazines_txt = (cfg_dir / 'CfgMagazines.txt').read_text(encoding='utf-8', errors='replace')
    ammo_txt      = (cfg_dir / 'CfgAmmo.txt').read_text(encoding='utf-8', errors='replace')

    print('Parsing CfgWeapons...')
    weapons_full = parse_weapons_full(weapons_txt)
    print(f'  weapons: {len(weapons_full)}')

    print('Parsing CfgMagazines...')
    mags_full = parse_magazines_full(magazines_txt)
    print(f'  magazines: {len(mags_full)}')

    print('Parsing CfgAmmo...')
    ammo_full = parse_ammo_full(ammo_txt)
    print(f'  ammo classes: {len(ammo_full)}')

    print('Parsing CfgVehicles (pass 1: hierarchy)...')
    veh_raw = _parse_vehicles_deep(vehicles_txt)
    print(f'  vehicle classes: {len(veh_raw)}')

    # Index images
    img_idx = index_images(img_root)
    print(f'  thumbnails found: {len(img_idx)}')

    # -----------------------------------------------------------------------
    # Build ancestry caches
    # -----------------------------------------------------------------------

    # Air ancestry check cache
    _air_cache: dict[str, bool] = {}
    # Ground ancestry check cache
    _ground_cache: dict[str, bool] = {}

    def is_aircraft(name: str) -> bool:
        return _is_descendant_of(name, _AIR_BASES, veh_raw, _air_cache)

    def is_ground_vehicle(name: str) -> bool:
        return _is_descendant_of(name, _GROUND_BASES, veh_raw, _ground_cache)

    # Weapon ancestry cache for noise detection
    _wep_ancestor_cache: dict[str, list] = {}
    _wep_raw = _parse(weapons_txt)  # for ancestry only

    def is_noise_weapon_inherited(wep_cls: str) -> bool:
        if _is_noise_weapon(wep_cls, {}):
            return True
        # Check if the weapon inherits from SmokeLauncher or CarHorn
        return _is_descendant_of(wep_cls, {'SmokeLauncher', 'CarHorn', 'CMFlareLauncher'},
                                  _wep_raw)

    # -----------------------------------------------------------------------
    # The 21 EASA aircraft — the canonical list from easa-mechanics.md §2
    # -----------------------------------------------------------------------
    EASA_CLASSES = [
        'Su34', 'Su25_Ins', 'Su25_TK_EP1', 'Su39', 'L39_TK_EP1',
        'F35B', 'L159_ACR', 'A10', 'A10_US_EP1', 'AV8B', 'AV8B2',
        'Mi24_D_CZ_ACR', 'AH64D', 'AH64D_EP1', 'BAF_Apache_AH1_D',
        'AH1Z', 'AW159_Lynx_BAF', 'Mi24_V', 'Mi24_P', 'Ka52', 'Ka52Black',
    ]

    # Faction from easa-mechanics.md §2 (supplement config where absent)
    _EASA_FACTION_OVERRIDE = {
        'Su34': 'RU', 'Su25_Ins': 'INS', 'Su25_TK_EP1': 'TK', 'Su39': 'RU',
        'L39_TK_EP1': 'TK', 'F35B': 'US', 'L159_ACR': 'CZ', 'A10': 'US',
        'A10_US_EP1': 'US', 'AV8B': 'USMC', 'AV8B2': 'USMC',
        'Mi24_D_CZ_ACR': 'CZ', 'AH64D': 'US', 'AH64D_EP1': 'US',
        'BAF_Apache_AH1_D': 'BAF', 'AH1Z': 'US', 'AW159_Lynx_BAF': 'BAF',
        'Mi24_V': 'RU', 'Mi24_P': 'RU', 'Ka52': 'RU', 'Ka52Black': 'RU',
    }

    # Plane vs heli from easa-mechanics.md §2 (Su- / L39 / F35B / A10 / AV8B = plane)
    _EASA_PLANE = {
        'Su34', 'Su25_Ins', 'Su25_TK_EP1', 'Su39', 'L39_TK_EP1',
        'F35B', 'L159_ACR', 'A10', 'A10_US_EP1', 'AV8B', 'AV8B2',
    }

    # Mission display names from a2waspwarfare LoadoutManager (inGameDisplayName)
    # — the mission overrides/curates these, so they win over config displayName.
    _MISSION_DISPLAY_NAME = {
        # Aircraft (Tools/LoadoutManager/Data/Vehicles/Aircrafts)
        'Su34': 'Su-34', 'Su25_Ins': 'Su-25A', 'Su25_TK_EP1': 'Su-25T',
        'Su39': 'Su-39', 'L39_TK_EP1': 'L-39', 'F35B': 'F-35B',
        'L159_ACR': 'L-159', 'A10': 'A-10A', 'A10_US_EP1': 'A-10C',
        'AV8B': 'AV8B (LGB)', 'AV8B2': 'AV8B', 'Mi24_D_CZ_ACR': 'Mi-24V (CZ)',
        'AH64D': 'AH-64D (TOW)', 'AH64D_EP1': 'AH-64D (Hellfire)',
        'BAF_Apache_AH1_D': 'Apache AH1', 'AH1Z': 'AH-1Z',
        'AW159_Lynx_BAF': 'Wildcat AH11', 'Mi24_V': 'Mi-24V', 'Mi24_P': 'Mi-24P',
        'Ka52': 'Ka-52', 'Ka52Black': 'Ka-52 (Black)',
        'AH6J_EP1': 'AH-6J', 'UH1Y': 'UH1Y', 'An2_TK_EP1': 'An-2',
        'Mi24_D_TK_EP1': 'Mi-24D',
        # Ground vehicles (Tools/LoadoutManager/Data/Vehicles/GroundVehicles)
        'M2A2_EP1': 'M2A2 Bradley', 'M6_EP1': 'M6 Linebacker', 'MLRS': 'MLRS',
        'MLRS_DES_EP1': 'MLRS (Desert)', 'M1128_MGS_EP1': 'Stryker MGS',
        'Pandur2_ACR': 'Pandur', 'BMP2_INS': 'BMP-2', 'BMP2_TK_EP1': 'BMP-2',
        'T34_TK_EP1': 'T-34', 'T34_TK_GUE_EP1': 'T-34 (Guerilla)',
        'BRDM2_ATGM_INS': 'BRDM (Igla)', 'BTR90': 'BTR-90',
    }

    # Aircraft-factory (AF) level per airframe, from a2waspwarfare
    # LoadoutManager inGameFactoryLevel (mirrors mission Core_*.sqf upgrade req).
    _EASA_AF_LEVEL = {
        'Su34': 5, 'Su25_Ins': 3, 'Su25_TK_EP1': 4, 'Su39': 5, 'L39_TK_EP1': 3,
        'F35B': 5, 'L159_ACR': 3, 'A10': 3, 'A10_US_EP1': 4, 'AV8B': 4,
        'AV8B2': 5, 'Mi24_D_CZ_ACR': 3, 'AH64D': 3, 'AH64D_EP1': 4,
        'BAF_Apache_AH1_D': 4, 'AH1Z': 5, 'AW159_Lynx_BAF': 3, 'Mi24_V': 3,
        'Mi24_P': 3, 'Ka52': 4, 'Ka52Black': 5,
        'AH6J_EP1': 2, 'UH1Y': 2, 'An2_TK_EP1': 1, 'Mi24_D_TK_EP1': 3,
    }

    # -----------------------------------------------------------------------
    # Helpers to determine airframe kind from ancestry
    # -----------------------------------------------------------------------

    def _is_plane(name: str) -> bool:
        return _is_descendant_of(name, {'Plane'}, veh_raw)

    def _is_heli(name: str) -> bool:
        return _is_descendant_of(name, {'Helicopter'}, veh_raw)

    def kind_of(cls: str) -> str:
        if cls in _EASA_PLANE or _is_plane(cls):
            return 'plane'
        return 'heli'

    # -----------------------------------------------------------------------
    # Collect ALL airframes (scope=2 aircraft for the broader list)
    # -----------------------------------------------------------------------

    airframes_list = []
    all_airframe_classes: set[str] = set()

    # First pass: all scope=2 aircraft from config
    for cls, rec in veh_raw.items():
        scope = rec.get('_scope') or _resolve_field(cls, '_scope', veh_raw)
        if scope != 2:
            continue
        if not is_aircraft(cls):
            continue
        all_airframe_classes.add(cls)

    print(f'  scope=2 aircraft found: {len(all_airframe_classes)}')

    # Ensure all 21 EASA classes are in the set — even if not scope=2 in the dump
    # (L159_ACR and Mi24_D_CZ_ACR are ACR DLC classes absent from this config reference).
    # For missing EASA classes, we synthesise an entry using their nearest known base class
    # (Mi24_D_CZ_ACR → Mi24_D_Base_CZ_ACR, L159_ACR → unknown, use stubs).
    _EASA_BASE_FALLBACK: dict[str, str] = {
        'Mi24_D_CZ_ACR': 'Mi24_D_Base_CZ_ACR',
        'L159_ACR': 'L159_ACR',  # no base in dump — emit stub
    }
    for cls in EASA_CLASSES:
        if cls not in all_airframe_classes:
            fallback = _EASA_BASE_FALLBACK.get(cls, cls)
            print(f'  NOTE: {cls} not in config dump — synthesising from {fallback}')
            all_airframe_classes.add(cls)
            # Register a synthetic record in veh_raw so the rest of the pipeline works
            if cls not in veh_raw:
                fallback_rec = veh_raw.get(fallback, {})
                veh_raw[cls] = {
                    'dn': fallback_rec.get('dn', ''),
                    'parent': fallback,
                    '_type_raw': None,
                    '_mags_own': None, '_mags_additive': False,
                    '_mags_resolved': fallback_rec.get('_mags_resolved', []),
                    '_weps_own': None, '_weps_additive': False,
                    '_weps_resolved': fallback_rec.get('_weps_resolved', []),
                    '_scope': 2, '_faction': None, '_side': None,
                    '_airlock_raw': None, '_count_raw': None, '_ammo_own': None,
                }

    # Build airframes entries
    # We need turret weapons/mags extracted from the raw text (pass 2)
    for cls in sorted(all_airframe_classes):
        rec = veh_raw[cls]
        dn = (_MISSION_DISPLAY_NAME.get(cls)
              or rec.get('dn') or _resolve_field(cls, 'dn', veh_raw) or cls)
        k = kind_of(cls)

        # Faction
        faction = _EASA_FACTION_OVERRIDE.get(cls)
        if not faction:
            f_raw = _resolve_field(cls, '_faction', veh_raw)
            if f_raw:
                faction = _FACTION_SIDE_MAP.get(f_raw, f_raw)
        if not faction:
            s_raw = _resolve_field(cls, '_side', veh_raw)
            if s_raw is not None:
                faction = _SIDE_NAMES.get(s_raw)

        # Root-level weapons/mags
        root_weps = list(rec.get('_weps_resolved') or [])
        root_mags = list(rec.get('_mags_resolved') or [])

        # Turret weapons/mags (extracted from raw text block)
        # For synthetic EASA stubs, fall back to the base class's raw text block
        _extract_cls = _EASA_BASE_FALLBACK.get(cls, cls) if cls in _EASA_BASE_FALLBACK else cls
        t_weps, t_mags = _extract_turret_weapons_chain(vehicles_txt, _extract_cls, veh_raw)

        # Merge root + turret (dedup, preserve order)
        all_weps: list[str] = []
        seen_w: set[str] = set()
        for w in root_weps + t_weps:
            if w and w not in seen_w:
                seen_w.add(w)
                all_weps.append(w)

        all_mags: list[str] = []
        seen_m: set[str] = set()
        for m in root_mags + t_mags:
            if m and m not in seen_m:
                seen_m.add(m)
                all_mags.append(m)

        # Thumbnail
        thumb = f'{cls}.jpg' if cls in img_idx else None

        entry = {
            'class': cls,
            'displayName': dn,
            'kind': k,
            'faction': faction,
            'afLevel': _EASA_AF_LEVEL.get(cls),
            'thumb': thumb,
            'stock': {
                'weapons': all_weps,
                'mags': all_mags,
            },
        }
        airframes_list.append(entry)

    airframes_list.sort(key=lambda x: x['class'])
    print(f'  airframes emitted: {len(airframes_list)}')

    # -----------------------------------------------------------------------
    # Collect weapons used by vehicles (aircraft pylons + ground-vehicle mounts)
    # Weapons must be "vehicle-usable" — not infantry rifles/pistols.
    # In A2: vehicle weapons have type bits 1+4=5 (MGun) or 4 (Launcher)
    # or are referenced in vehicle Turrets[] weapons arrays.
    # We collect all weapons referenced in any scope=2 vehicle's weapon arrays
    # and filter out noise (smoke/horn/CM) weapons.
    # -----------------------------------------------------------------------

    referenced_weps: set[str] = set()

    # Collect from airframes
    for af in airframes_list:
        for w in af['stock']['weapons']:
            referenced_weps.add(w)

    # Also collect from all scope=2 ground vehicles' turret weapons
    scope2_ground: set[str] = set()
    for cls, rec in veh_raw.items():
        scope = rec.get('_scope') or _resolve_field(cls, '_scope', veh_raw)
        if scope != 2:
            continue
        if is_ground_vehicle(cls):
            scope2_ground.add(cls)
            # Root weapons
            for w in (rec.get('_weps_resolved') or []):
                if w:
                    referenced_weps.add(w)
            # Turret weapons (chain-walk so inherited turrets are found)
            tw, _ = _extract_turret_weapons_chain(vehicles_txt, cls, veh_raw)
            for w in tw:
                if w:
                    referenced_weps.add(w)

    # Filter out noise weapons
    veh_weapons: dict[str, dict] = {}
    for wep_cls in sorted(referenced_weps):
        if is_noise_weapon_inherited(wep_cls):
            continue
        wp = weapons_full.get(wep_cls, {'dn': '', 'type': 0, 'mags': []})
        mags = wp.get('mags') or []
        # Resolve mag displayNames (for category heuristic)
        mag_ammos = {mg: mags_full.get(mg, {}).get('ammo', '') for mg in mags}
        cat = _categorize_weapon(wep_cls, list(mag_ammos.keys()), mags_full, ammo_full)
        # Thumb
        thumb = f'{wep_cls}.jpg' if wep_cls in img_idx else None
        veh_weapons[wep_cls] = {
            'displayName': wp.get('dn') or wep_cls,
            'magazines': mags,
            'category': cat,
            'thumb': thumb,
        }

    print(f'  weapons (vehicle-usable, non-noise): {len(veh_weapons)}')

    # -----------------------------------------------------------------------
    # Collect all magazines referenced by weapons.json
    # -----------------------------------------------------------------------

    referenced_mags: set[str] = set()
    for wp in veh_weapons.values():
        for mg in wp['magazines']:
            referenced_mags.add(mg)
    # Also add mags referenced in airframe stock mags
    for af in airframes_list:
        for mg in af['stock']['mags']:
            referenced_mags.add(mg)

    # Build magazines.json
    # mags_full already resolves ammo through parent chain (parse_magazines_full uses
    # _resolve_scalar which walks ancestry), so ammo_cls is already inherited correctly.
    veh_mags: dict[str, dict] = {}
    for mag_cls in sorted(referenced_mags):
        mg = mags_full.get(mag_cls, {'dn': '', 'count': 0, 'ammo': ''})
        ammo_cls = mg.get('ammo', '')
        # Resolve airLock: ammo_cls already resolved from parent chain
        air_lock = bool(ammo_full.get(ammo_cls, {}).get('airLock', False)) if ammo_cls else False
        thumb = f'{mag_cls}.jpg' if mag_cls in img_idx else None
        veh_mags[mag_cls] = {
            'displayName': mg.get('dn') or mag_cls,
            'count': mg.get('count') or 0,
            'ammo': ammo_cls,
            'airLock': air_lock,
            'thumb': thumb,
        }

    print(f'  magazines collected: {len(veh_mags)}')

    # -----------------------------------------------------------------------
    # Build vehicles.json — ground vehicles scope=2
    # -----------------------------------------------------------------------

    vehicles_list = []

    # In-game display names from the a2waspwarfare wiki visual catalogs
    # (Base-Game-*-Visual-Catalog.md) for classes whose displayName is not
    # resolvable from this config reference dump (would fall back to the
    # classname otherwise).
    _WIKI_DN_FILL = {
        'ATV_CZ_EP1': 'ATV',
        'ATV_US_EP1': 'ATV',
        'BMP2_Ambul_CDF': 'BMP-2 Ambulance',
        'BMP2_Ambul_INS': 'BMP-2 Ambulance',
        'BMP2_CDF': 'BMP-2',
        'BMP2_Gue': 'BMP-2',
        'BMP2_HQ_CDF': 'BMP-2 (HQ)',
        'BMP2_HQ_INS': 'BMP-2 (HQ)',
        'BMP2_HQ_TK_EP1': 'BMP-2 (HQ)',
        'BMP2_UN_EP1': 'BMP-2',
        'BRDM2_ATGM_CDF': 'BRDM-2 (ATGM)',
        'BRDM2_ATGM_TK_EP1': 'BRDM-2 (ATGM)',
        'BRDM2_CDF': 'BRDM-2',
        'BRDM2_Gue': 'BRDM-2',
        'BRDM2_HQ_Gue': 'BRDM-2 (HQ)',
        'BRDM2_HQ_TK_GUE_EP1': 'BRDM-2 (HQ)',
        'BRDM2_INS': 'BRDM-2',
        'BRDM2_TK_EP1': 'BRDM-2',
        'BRDM2_TK_GUE_EP1': 'BRDM-2',
        'BTR40_MG_TK_GUE_EP1': 'BTR-40 (DshKM)',
        'BTR40_MG_TK_INS_EP1': 'BTR-40 (DshKM)',
        'BTR40_TK_GUE_EP1': 'BTR-40',
        'BTR40_TK_INS_EP1': 'BTR-40',
        'CDF_WarfareBMGNest_PK': 'MG Nest (PK)',
        'GRAD_CDF': 'Ural',
        'GRAD_INS': 'Ural',
        'GRAD_RU': 'Ural',
        'GRAD_TK_EP1': 'Ural',
        'GUE_WarfareBMGNest_PK': 'MG Nest (PK)',
        'HMMWV_Ambulance_CZ_DES_EP1': 'HMMWV',
        'HMMWV_Ambulance_DES_EP1': 'HMMWV',
        'HMMWV_Avenger_DES_EP1': 'HMMWV',
        'HMMWV_DES_EP1': 'HMMWV',
        'HMMWV_M1151_M2_CZ_DES_EP1': 'HMMWV',
        'HMMWV_M1151_M2_DES_EP1': 'HMMWV',
        'HMMWV_MK19_DES_EP1': 'HMMWV (Mk19)',
        'HMMWV_TOW_DES_EP1': 'HMMWV (TOW)',
        'Ikarus_TK_CIV_EP1': 'Bus',
        'Ins_WarfareBMGNest_PK': 'MG Nest (PK)',
        'Kamaz': 'Utility Truck',
        'LAV25': 'LAV-25',
        'LandRover_CZ_EP1': 'Car',
        'LandRover_MG_TK_EP1': 'Car',
        'LandRover_MG_TK_INS_EP1': 'Car',
        'LandRover_SPG9_TK_EP1': 'Car',
        'LandRover_SPG9_TK_INS_EP1': 'Car',
        'LandRover_TK_CIV_EP1': 'Car',
        'M1030_US_DES_EP1': 'Motorcycle',
        'M113Ambul_TK_EP1': 'M113 Ambulance',
        'M113Ambul_UN_EP1': 'M113 Ambulance',
        'M113_TK_EP1': 'M113',
        'M113_UN_EP1': 'M113',
        'M1A1_US_DES_EP1': 'M1A1',
        'M1A2_US_TUSK_MG_EP1': 'M1A2 TUSK',
        'MAZ_543_SCUD_TK_EP1': 'Truck',
        'MMT_Civ': 'Mountain bike',
        'MMT_USMC': 'Mountain bike',
        'MTVR': 'Truck',
        'Offroad_SPG9_TK_GUE_EP1': 'Off-road (SPG-9)',
        'Old_bike_TK_CIV_EP1': 'Old bike',
        'Old_bike_TK_INS_EP1': 'Old bike',
        'Old_moto_TK_Civ_EP1': 'Old moto',
        'Pickup_PK_GUE': 'Pickup (PK)',
        'Pickup_PK_INS': 'Pickup (PK)',
        'Pickup_PK_TK_GUE_EP1': 'Pickup (PK)',
        'RU_WarfareBMGNest_PK': 'MG Nest (PK)',
        'SUV_TK_CIV_EP1': 'SUV',
        'SUV_TK_EP1': 'SUV',
        'SUV_UN_EP1': 'SUV',
        'T55_TK_EP1': 'T-55',
        'T55_TK_GUE_EP1': 'T-55',
        'T72_CDF': 'T-72',
        'T72_Gue': 'T-72',
        'T72_INS': 'T-72',
        'T72_RU': 'T-72',
        'T72_TK_EP1': 'T-72',
        'TT650_Civ': 'Motorcycle',
        'TT650_Gue': 'Motorcycle',
        'TT650_Ins': 'Motorcycle',
        'TT650_TK_CIV_EP1': 'Motorcycle',
        'TT650_TK_EP1': 'Motorcycle',
        'UAZ_AGS30_CDF': 'UAZ (AGS-30)',
        'UAZ_AGS30_INS': 'UAZ (AGS-30)',
        'UAZ_AGS30_RU': 'UAZ (AGS-30)',
        'UAZ_AGS30_TK_EP1': 'UAZ (AGS-30)',
        'UAZ_CDF': 'UAZ',
        'UAZ_INS': 'UAZ',
        'UAZ_MG_CDF': 'UAZ (DShKM)',
        'UAZ_MG_INS': 'UAZ (DShKM)',
        'UAZ_MG_TK_EP1': 'UAZ (DShKM)',
        'UAZ_RU': 'UAZ',
        'UAZ_SPG9_INS': 'UAZ (SPG-9)',
        'UAZ_Unarmed_TK_CIV_EP1': 'UAZ',
        'UAZ_Unarmed_TK_EP1': 'UAZ',
        'UAZ_Unarmed_UN_EP1': 'UAZ',
        'UralOpen_CDF': 'Ural (Open)',
        'UralOpen_INS': 'Ural (Open)',
        'UralReammo_CDF': 'Ural (Ammunition)',
        'UralReammo_INS': 'Ural (Ammunition)',
        'UralReammo_TK_EP1': 'Ural (Ammunition)',
        'UralRefuel_CDF': 'Ural (Fuel)',
        'UralRefuel_INS': 'Ural (Fuel)',
        'UralRefuel_TK_EP1': 'Ural (Fuel)',
        'UralRepair_CDF': 'Ural (Repair)',
        'UralRepair_INS': 'Ural (Repair)',
        'UralRepair_TK_EP1': 'Ural (Repair)',
        'Ural_CDF': 'Ural',
        'Ural_INS': 'Ural',
        'Ural_TK_CIV_EP1': 'Ural',
        'Ural_UN_EP1': 'Ural',
        'Ural_ZU23_CDF': 'Ural (ZU-23)',
        'Ural_ZU23_Gue': 'Ural (ZU-23)',
        'Ural_ZU23_INS': 'Ural (ZU-23)',
        'Ural_ZU23_TK_EP1': 'Ural (ZU-23)',
        'Ural_ZU23_TK_GUE_EP1': 'Ural (ZU-23)',
        'V3S_Civ': 'Truck',
        'V3S_Gue': 'Truck',
        'WarfareBMGNest_M240_US_EP1': 'MG Nest',
        'WarfareBMGNest_PK_TK_EP1': 'MG Nest (PK)',
        'WarfareBMGNest_PK_TK_GUE_EP1': 'MG Nest (PK)',
        'WarfareReammoTruck_CDF': 'Ural (Ammunition)',
        'WarfareReammoTruck_Gue': 'Ural (Ammunition)',
        'WarfareReammoTruck_INS': 'Ural (Ammunition)',
        'WarfareReammoTruck_RU': 'Utility Truck (Ammunition)',
        'WarfareReammoTruck_USMC': 'MTVR (Ammunition)',
        'WarfareSalvageTruck_Gue': 'Salvage Truck',
        'WarfareSupplyTruck_Gue': 'Supply Truck',
        'ZSU_CDF': 'ZSU-23 Shilka',
        'ZSU_INS': 'ZSU-23 Shilka',
        'ZSU_TK_EP1': 'ZSU-23 Shilka',
    }

    # Weapons that are "real" combat weapons for armed detection
    def _is_real_combat_weapon(wep_cls: str) -> bool:
        if is_noise_weapon_inherited(wep_cls):
            return False
        if not wep_cls:
            return False
        return True

    for cls in sorted(scope2_ground):
        rec = veh_raw[cls]
        dn = (_MISSION_DISPLAY_NAME.get(cls)
              or rec.get('dn') or _resolve_field(cls, 'dn', veh_raw)
              or _WIKI_DN_FILL.get(cls) or cls)

        # Faction
        f_raw = _resolve_field(cls, '_faction', veh_raw)
        faction = _FACTION_SIDE_MAP.get(f_raw or '', f_raw) if f_raw else None
        if not faction:
            s_raw = _resolve_field(cls, '_side', veh_raw)
            if s_raw is not None:
                faction = _SIDE_NAMES.get(s_raw)

        # Root weapons (resolved through inheritance)
        root_weps = list(rec.get('_weps_resolved') or [])
        # Turret weapons — chain-walk so inherited Turrets blocks are found
        t_weps, t_mags = _extract_turret_weapons_chain(vehicles_txt, cls, veh_raw)

        # All combat weapons
        all_weps: list[str] = []
        seen_w: set[str] = set()
        for w in root_weps + t_weps:
            if w and w not in seen_w and _is_real_combat_weapon(w):
                seen_w.add(w)
                all_weps.append(w)

        armed = len(all_weps) > 0

        # Thumb
        thumb = f'{cls}.jpg' if cls in img_idx else None

        # Turret paths (simple: 'root' for root weps, 'MainTurret' for turret weps)
        turret_paths = []
        if any(w in root_weps for w in all_weps if w in root_weps):
            turret_paths.append('root')
        if t_weps:
            turret_paths.append('Turrets')

        entry = {
            'class': cls,
            'displayName': dn,
            'faction': faction,
            'thumb': thumb,
            'armed': armed,
            'weapons': all_weps,
            'turretPaths': turret_paths,
        }
        vehicles_list.append(entry)

    vehicles_list.sort(key=lambda x: x['class'])
    armed_count = sum(1 for v in vehicles_list if v['armed'])
    unarmed_count = len(vehicles_list) - armed_count
    print(f'  ground vehicles (scope=2): {len(vehicles_list)} '
          f'(armed={armed_count}, unarmed={unarmed_count})')

    # -----------------------------------------------------------------------
    # Write JSON files
    # -----------------------------------------------------------------------

    def write_json(path: Path, data, name: str):
        j = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        path.write_text(j, encoding='utf-8')
        size_kb = len(j.encode('utf-8')) / 1024
        print(f'  {name}: {path.name} — {size_kb:.1f} KB')

    write_json(data_dir / 'airframes.json',  airframes_list,           'airframes')
    write_json(data_dir / 'weapons.json',    veh_weapons,              'weapons')
    write_json(data_dir / 'magazines.json',  veh_mags,                 'magazines')
    write_json(data_dir / 'vehicles.json',   vehicles_list,            'vehicles')

    # -----------------------------------------------------------------------
    # Copy thumbnails for all classes we emitted
    # -----------------------------------------------------------------------

    all_classes_used = (
        {e['class'] for e in airframes_list} |
        set(veh_weapons.keys()) |
        set(veh_mags.keys()) |
        {e['class'] for e in vehicles_list}
    )
    copied, missing_thumbs = copy_images(all_classes_used, img_idx, img_dest)
    print(f'  thumbnails copied: {len(copied)}  (missing: {len(missing_thumbs)})')

    # -----------------------------------------------------------------------
    # EASA class verification
    # -----------------------------------------------------------------------

    emitted_airframe_cls = {e['class'] for e in airframes_list}
    missing_easa = [c for c in EASA_CLASSES if c not in emitted_airframe_cls]
    found_easa   = [c for c in EASA_CLASSES if c in emitted_airframe_cls]

    print(f'\n=== EASA class check ===')
    print(f'  21 required: {len(EASA_CLASSES)}')
    print(f'  found in output: {len(found_easa)}')
    if missing_easa:
        print(f'  *** MISSING EASA CLASSES: {missing_easa} ***')
    else:
        print('  All 21 EASA classes present in airframes.json')

    print(f'\nDone.')
    return {
        'airframes': len(airframes_list),
        'weapons': len(veh_weapons),
        'magazines': len(veh_mags),
        'vehicles': len(vehicles_list),
        'armed': armed_count,
        'unarmed': unarmed_count,
        'easa_found': found_easa,
        'easa_missing': missing_easa,
    }


if __name__ == '__main__':
    main()
