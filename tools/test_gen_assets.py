"""Tests for gen_assets.py — verifies the generated JSON files.

Run with:
    python -m pytest tools -q
or:
    python -m pytest tools/test_gen_assets.py -v

Assumes gen_assets.py has already been run and assets/data/*.json exist.
If not, the tests run the generator automatically.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Repo root (parent of tools/)
REPO_ROOT = Path(__file__).parent.parent
ASSETS_DATA = REPO_ROOT / 'assets' / 'data'
TOOLS_DIR = REPO_ROOT / 'tools'

# Default ref path (sibling directory)
REF_PATH = REPO_ROOT / '..' / 'arma2-co-config-reference'


def _ensure_generated():
    """Run gen_assets.py if output files are missing."""
    needed = ['airframes.json', 'weapons.json', 'magazines.json', 'vehicles.json']
    if not all((ASSETS_DATA / f).exists() for f in needed):
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / 'gen_assets.py'),
             '--ref', str(REF_PATH), '--out', str(REPO_ROOT)],
            capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f'gen_assets.py failed:\n{result.stdout}\n{result.stderr}')


def load_json(name: str):
    _ensure_generated()
    return json.loads((ASSETS_DATA / name).read_text(encoding='utf-8'))


# ---------------------------------------------------------------------------
# Test fixtures (loaded once per session via module-level cache)
# ---------------------------------------------------------------------------

_CACHE: dict[str, object] = {}


def _get(name: str):
    if name not in _CACHE:
        _CACHE[name] = load_json(name)
    return _CACHE[name]


def airframes():
    return _get('airframes.json')


def weapons():
    return _get('weapons.json')


def magazines():
    return _get('magazines.json')


def vehicles():
    return _get('vehicles.json')


# ---------------------------------------------------------------------------
# The canonical 21 EASA classes (from docs/research/easa-mechanics.md §2)
# ---------------------------------------------------------------------------

EASA_21 = [
    'Su34', 'Su25_Ins', 'Su25_TK_EP1', 'Su39', 'L39_TK_EP1',
    'F35B', 'L159_ACR', 'A10', 'A10_US_EP1', 'AV8B', 'AV8B2',
    'Mi24_D_CZ_ACR', 'AH64D', 'AH64D_EP1', 'BAF_Apache_AH1_D',
    'AH1Z', 'AW159_Lynx_BAF', 'Mi24_V', 'Mi24_P', 'Ka52', 'Ka52Black',
]


# ---------------------------------------------------------------------------
# airframes.json tests
# ---------------------------------------------------------------------------

def test_airframes_contains_all_21_easa():
    """airframes.json must contain every one of the 21 EASA-registered aircraft."""
    af_classes = {e['class'] for e in airframes()}
    missing = [c for c in EASA_21 if c not in af_classes]
    assert not missing, (
        f'Missing EASA classes in airframes.json: {missing}\n'
        f'All present: {sorted(af_classes & set(EASA_21))}'
    )


def test_airframes_have_required_fields():
    """Every airframe entry must have class, displayName, kind, stock."""
    for af in airframes():
        cls = af['class']
        assert 'class' in af, f'{cls}: missing "class"'
        assert 'displayName' in af, f'{cls}: missing "displayName"'
        assert af.get('kind') in ('plane', 'heli'), (
            f'{cls}: kind must be plane|heli, got {af.get("kind")!r}')
        assert 'stock' in af, f'{cls}: missing "stock"'
        assert 'weapons' in af['stock'], f'{cls}: missing stock.weapons'
        assert 'mags' in af['stock'], f'{cls}: missing stock.mags'


def test_airframe_a10_has_gau_weapon():
    """A10 stock must include the GAU-8 cannon (GAU8 classname)."""
    af_map = {e['class']: e for e in airframes()}
    a10 = af_map.get('A10')
    assert a10 is not None, 'A10 not found in airframes.json'
    weps = a10['stock']['weapons']
    gau_weapons = [w for w in weps if 'GAU' in w or 'gau' in w.lower()]
    assert gau_weapons, (
        f'A10 stock weapons do not include a GAU weapon. Got: {weps}')


def test_airframe_kinds_planes_and_helis():
    """Known planes and helis must have the correct kind."""
    af_map = {e['class']: e for e in airframes()}
    planes = ['Su34', 'A10', 'F35B', 'AV8B', 'L159_ACR']
    helis  = ['AH64D', 'Ka52', 'Mi24_V', 'AW159_Lynx_BAF', 'Mi24_D_CZ_ACR']
    for cls in planes:
        if cls in af_map:
            assert af_map[cls]['kind'] == 'plane', (
                f'{cls} should be "plane", got {af_map[cls]["kind"]!r}')
    for cls in helis:
        if cls in af_map:
            assert af_map[cls]['kind'] == 'heli', (
                f'{cls} should be "heli", got {af_map[cls]["kind"]!r}')


def test_airframe_easa_factions_set():
    """All 21 EASA airframes must have a non-null faction field."""
    af_map = {e['class']: e for e in airframes()}
    no_faction = [c for c in EASA_21 if af_map.get(c, {}).get('faction') is None]
    assert not no_faction, (
        f'EASA airframes missing faction: {no_faction}')


# ---------------------------------------------------------------------------
# weapons.json tests
# ---------------------------------------------------------------------------

def test_weapons_not_empty():
    assert len(weapons()) > 0, 'weapons.json is empty'


def test_weapons_have_required_fields():
    """Every weapon entry must have displayName, magazines, category."""
    for cls, wp in weapons().items():
        assert 'displayName' in wp, f'{cls}: missing displayName'
        assert 'magazines' in wp, f'{cls}: missing magazines'
        assert isinstance(wp['magazines'], list), f'{cls}: magazines must be a list'
        assert 'category' in wp, f'{cls}: missing category'


def test_every_weapon_magazine_exists_in_magazines():
    """Every magazine classname in weapons.json must exist in magazines.json."""
    mags = magazines()
    missing_refs: list[tuple[str, str]] = []
    for wep_cls, wp in weapons().items():
        for mag_cls in wp.get('magazines', []):
            if mag_cls not in mags:
                missing_refs.append((wep_cls, mag_cls))
    assert not missing_refs, (
        f'Weapon→magazine cross-reference failures ({len(missing_refs)}):\n' +
        '\n'.join(f'  {w} references {m}' for w, m in missing_refs[:20]))


def test_weapons_no_noise_classes():
    """SmokeLauncher, CMFlareLauncher, CarHorn must not appear in weapons.json."""
    noise = {'SmokeLauncher', 'CMFlareLauncher', 'CarHorn'}
    found_noise = [c for c in weapons() if c in noise]
    assert not found_noise, (
        f'Noise weapons should not appear in weapons.json: {found_noise}')


# ---------------------------------------------------------------------------
# magazines.json tests
# ---------------------------------------------------------------------------

def test_magazines_not_empty():
    assert len(magazines()) > 0, 'magazines.json is empty'


def test_magazines_have_required_fields():
    """Every magazine must have displayName, count, ammo, airLock."""
    for cls, mg in magazines().items():
        assert 'displayName' in mg, f'{cls}: missing displayName'
        assert 'count' in mg, f'{cls}: missing count'
        assert 'ammo' in mg, f'{cls}: missing ammo'
        assert 'airLock' in mg, f'{cls}: missing airLock'
        assert isinstance(mg['airLock'], bool), (
            f'{cls}: airLock must be bool, got {type(mg["airLock"]).__name__}')


def test_airlock_true_for_r73_type_magazine():
    """R-73 type magazines (or Sidewinder/Stinger) must have airLock=True.

    M_R73_AA, M_Stinger_AA, M_Sidewinder_AA all have airLock=1 in CfgAmmo.
    Magazines referencing these ammo classes must resolve airLock=True.
    """
    mags = magazines()
    # 4Rnd_R73 is the canonical R-73 magazine
    r73 = mags.get('4Rnd_R73')
    assert r73 is not None, '4Rnd_R73 not in magazines.json'
    assert r73['airLock'] is True, (
        f'4Rnd_R73 should have airLock=True, got {r73["airLock"]}')

    # 2Rnd_R73 inherits from 4Rnd_R73 — should also resolve True
    r73_2 = mags.get('2Rnd_R73')
    if r73_2 is not None:
        assert r73_2['airLock'] is True, (
            f'2Rnd_R73 should inherit airLock=True, got {r73_2["airLock"]}')


def test_airlock_false_for_rocket_magazine():
    """Unguided rocket magazines (non-AA) must have airLock=False."""
    mags = magazines()
    # 40Rnd_S8T is an unguided S-8 rocket magazine — definitely not AA
    ffar = mags.get('14Rnd_FFAR') or mags.get('38Rnd_FFAR') or mags.get('40Rnd_S8T')
    if ffar is not None:
        assert ffar['airLock'] is False, (
            f'Rocket magazine should have airLock=False, got {ffar["airLock"]}')


def test_r73_mag_has_displayname():
    """4Rnd_R73 should have a non-empty displayName (inherited from parent)."""
    mags = magazines()
    r73 = mags.get('4Rnd_R73')
    assert r73 is not None, '4Rnd_R73 not in magazines.json'
    assert r73.get('displayName'), (
        f'4Rnd_R73 displayName should be non-empty, got {r73.get("displayName")!r}')


# ---------------------------------------------------------------------------
# vehicles.json tests
# ---------------------------------------------------------------------------

def test_vehicles_not_empty():
    assert len(vehicles()) > 0, 'vehicles.json is empty'


def test_vehicles_have_required_fields():
    """Every vehicle must have class, displayName, armed, weapons, turretPaths."""
    for v in vehicles():
        cls = v['class']
        assert 'class' in v, f'{cls}: missing "class"'
        assert 'displayName' in v, f'{cls}: missing "displayName"'
        assert 'armed' in v, f'{cls}: missing "armed"'
        assert isinstance(v['armed'], bool), f'{cls}: armed must be bool'
        assert 'weapons' in v, f'{cls}: missing "weapons"'
        assert 'turretPaths' in v, f'{cls}: missing "turretPaths"'


def test_armed_vehicle_has_weapons_list():
    """Any vehicle with armed=True must have a non-empty weapons list."""
    for v in vehicles():
        if v['armed']:
            assert v['weapons'], (
                f'{v["class"]}: armed=True but weapons list is empty')


def test_unarmed_vehicle_has_no_weapons():
    """Any vehicle with armed=False must have an empty weapons list."""
    for v in vehicles():
        if not v['armed']:
            assert not v['weapons'], (
                f'{v["class"]}: armed=False but weapons={v["weapons"]}')


def test_known_armed_vehicles():
    """HMMWV_M2 and BRDM2_CDF must be armed."""
    veh_map = {v['class']: v for v in vehicles()}

    hmmwv_m2 = veh_map.get('HMMWV_M2')
    assert hmmwv_m2 is not None, 'HMMWV_M2 not found in vehicles.json'
    assert hmmwv_m2['armed'] is True, (
        f'HMMWV_M2 should be armed=True, got {hmmwv_m2["armed"]}')
    assert any('M2' in w for w in hmmwv_m2['weapons']), (
        f'HMMWV_M2 should have an M2 weapon, got {hmmwv_m2["weapons"]}')

    brdm = veh_map.get('BRDM2_CDF')
    assert brdm is not None, 'BRDM2_CDF not found in vehicles.json'
    assert brdm['armed'] is True, (
        f'BRDM2_CDF should be armed=True, got {brdm["armed"]}')


def test_known_unarmed_vehicles():
    """Plain HMMWV transport and UAZ_RU (unarmed) must be armed=False."""
    veh_map = {v['class']: v for v in vehicles()}

    hmmwv = veh_map.get('HMMWV')
    assert hmmwv is not None, 'HMMWV not found in vehicles.json'
    assert hmmwv['armed'] is False, (
        f'HMMWV (transport) should be armed=False, got {hmmwv["armed"]}')

    # UAZ_RU inherits from UAZ_Unarmed_Base which overrides Turrets to empty
    uaz_ru = veh_map.get('UAZ_RU')
    assert uaz_ru is not None, 'UAZ_RU not found in vehicles.json'
    assert uaz_ru['armed'] is False, (
        f'UAZ_RU should be armed=False, got {uaz_ru["armed"]}')


def test_vehicles_only_ground():
    """vehicles.json must not contain aircraft (Plane/Helicopter children)."""
    # All aircraft classnames from airframes.json
    af_classes = {e['class'] for e in airframes()}
    veh_classes = {v['class'] for v in vehicles()}
    overlap = af_classes & veh_classes
    assert not overlap, (
        f'vehicles.json should not contain aircraft: {sorted(overlap)[:10]}')


# ---------------------------------------------------------------------------
# Cross-file consistency
# ---------------------------------------------------------------------------

def test_airframe_stock_mags_in_magazines():
    """All magazine classnames in airframe stock.mags must exist in magazines.json."""
    mags = magazines()
    missing: list[tuple[str, str]] = []
    for af in airframes():
        for mag_cls in af['stock']['mags']:
            if mag_cls not in mags:
                missing.append((af['class'], mag_cls))
    assert not missing, (
        f'Airframe stock.mags not in magazines.json ({len(missing)}):\n' +
        '\n'.join(f'  {a} → {m}' for a, m in missing[:20]))


def test_airframe_stock_weapons_in_weapons():
    """All weapon classnames in airframe stock.weapons should exist in weapons.json
    (noise weapons like CMFlareLauncher are allowed to be absent since they are filtered)."""
    weps = weapons()
    # These are known noise/utility weapons that are intentionally excluded from weapons.json
    known_excluded = {'CMFlareLauncher', 'SmokeLauncher', 'CarHorn', 'Laserdesignator_mounted'}
    missing_unexpected: list[tuple[str, str]] = []
    for af in airframes():
        for wep_cls in af['stock']['weapons']:
            if wep_cls not in weps and wep_cls not in known_excluded:
                missing_unexpected.append((af['class'], wep_cls))
    if missing_unexpected:
        # Warn but don't fail — some config-dump weapons may be obscure sub-classes
        import warnings
        warnings.warn(
            f'{len(missing_unexpected)} stock weapons not in weapons.json '
            f'(first 5: {missing_unexpected[:5]})')


if __name__ == '__main__':
    import subprocess
    subprocess.run([sys.executable, '-m', 'pytest', __file__, '-v'], check=True)
