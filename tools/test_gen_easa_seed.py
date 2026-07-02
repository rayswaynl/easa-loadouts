"""
test_gen_easa_seed.py
pytest tests for gen_easa_seed.py

Run from repo root:
    python -m pytest tools -q
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Imports from the tool itself
# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen_easa_seed import (
    build_seed,
    emit_all_blocks,
    emit_vehicle_block,
    parse_easa_sqf,
    _parse_sqf_array,
    _tokenise,
    DEFAULT_SQF,
    SOURCE_FILE_REL,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SQF_PATH = DEFAULT_SQF


@pytest.fixture(scope="module")
def seed() -> dict:
    """Parse the real SQF file once; shared across all tests in this module."""
    assert SQF_PATH.exists(), f"SQF file not found at {SQF_PATH}"
    return build_seed(SQF_PATH)


@pytest.fixture(scope="module")
def vehicles(seed) -> list[dict]:
    return seed["vehicles"]


# ---------------------------------------------------------------------------
# Test 1: Parse real file → exactly 21 vehicles + spot-checks
# ---------------------------------------------------------------------------


def test_vehicle_count(vehicles):
    assert len(vehicles) == 22, (
        f"Expected 22 vehicles, got {len(vehicles)}: "
        f"{[v['class'] for v in vehicles]}"
    )


def test_source_file_field(seed):
    assert seed["sourceFile"] == SOURCE_FILE_REL


def test_su34_is_first(vehicles):
    assert vehicles[0]["class"] == "Su34"


def test_su34_comment(vehicles):
    v = vehicles[0]
    assert v["comment"] == "Su-34 [AF5] - 10 pylons", (
        f"Unexpected Su34 comment: {v['comment']!r}"
    )


def test_su34_pylons(vehicles):
    assert vehicles[0]["pylons"] == 10


def test_su34_first_preset_price(vehicles):
    # From the file: line 15 → price 16400
    first = vehicles[0]["presets"][0]
    assert first["price"] == 16400, f"Got price {first['price']}"


def test_su34_first_preset_label(vehicles):
    first = vehicles[0]["presets"][0]
    assert first["label"] == "FAB-250 (6) | GBU-12 (2) | Kh-29 (4) | R-73 (2)", (
        f"Got label {first['label']!r}"
    )


def test_su34_first_preset_weapons(vehicles):
    # From file line 15:
    # [['AirBombLauncher','BombLauncherF35','Ch29Launcher_Su34','R73Launcher_2'],...]
    first = vehicles[0]["presets"][0]
    assert first["weapons"] == [
        "AirBombLauncher",
        "BombLauncherF35",
        "Ch29Launcher_Su34",
        "R73Launcher_2",
    ], f"Got weapons {first['weapons']}"


def test_su34_first_preset_mags(vehicles):
    # From file: ['4Rnd_FAB_250','2Rnd_FAB_250','2Rnd_GBU12','4Rnd_Ch29','2Rnd_R73']
    first = vehicles[0]["presets"][0]
    assert first["mags"] == [
        "4Rnd_FAB_250",
        "2Rnd_FAB_250",
        "2Rnd_GBU12",
        "4Rnd_Ch29",
        "2Rnd_R73",
    ], f"Got mags {first['mags']}"


def test_su34_weapon_count_first_preset(vehicles):
    # 4 weapons per the file
    first = vehicles[0]["presets"][0]
    assert len(first["weapons"]) == 4


# ---------------------------------------------------------------------------
# Test 2: Round-trip (parse → emit blocks → re-parse → identical data)
# ---------------------------------------------------------------------------


def _reparse_emitted(vehicles: list[dict]) -> list[dict]:
    """Emit all vehicle blocks as a synthetic SQF fragment and re-parse it."""
    # Build a minimal SQF that the parser can handle: init lines + blocks
    seed_copy = {"sourceFile": SOURCE_FILE_REL, "vehicles": vehicles}
    blocks = emit_all_blocks(seed_copy)

    # Wrap with the required init preamble the parser expects
    synthetic_sqf = (
        "_easaDefault = [];\n"
        "_easaLoadout = [];\n"
        "_easaVehi = [];\n\n"
        + blocks
        + "\n"
    )

    # Write to a temp path and re-parse
    import tempfile, os
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sqf", delete=False, encoding="utf-8"
    ) as f:
        f.write(synthetic_sqf)
        tmp = Path(f.name)
    try:
        result = parse_easa_sqf(tmp)
    finally:
        os.unlink(tmp)
    return result


def test_roundtrip_vehicle_count(vehicles):
    reparsed = _reparse_emitted(vehicles)
    assert len(reparsed) == len(vehicles)


def test_roundtrip_classnames(vehicles):
    reparsed = _reparse_emitted(vehicles)
    orig_classes = [v["class"] for v in vehicles]
    new_classes = [v["class"] for v in reparsed]
    assert orig_classes == new_classes


def test_roundtrip_presets_equal(vehicles):
    """For every vehicle, the presets list after round-trip must be identical."""
    reparsed = _reparse_emitted(vehicles)
    for orig, new in zip(vehicles, reparsed):
        assert orig["presets"] == new["presets"], (
            f"Preset mismatch for {orig['class']}:\n"
            f"  orig[0]: {orig['presets'][0]}\n"
            f"  new[0]:  {new['presets'][0]}"
        )


def test_roundtrip_defaults_equal(vehicles):
    """Default loadouts must survive round-trip unchanged."""
    reparsed = _reparse_emitted(vehicles)
    for orig, new in zip(vehicles, reparsed):
        assert orig["default"] == new["default"], (
            f"Default mismatch for {orig['class']}: "
            f"{orig['default']} vs {new['default']}"
        )


# ---------------------------------------------------------------------------
# Test 3: Structural validity
# ---------------------------------------------------------------------------


def test_every_vehicle_has_at_least_one_preset(vehicles):
    for v in vehicles:
        assert len(v["presets"]) >= 1, (
            f"{v['class']} has no presets"
        )


def test_every_preset_has_at_least_one_weapon(vehicles):
    for v in vehicles:
        for i, p in enumerate(v["presets"]):
            assert len(p["weapons"]) >= 1, (
                f"{v['class']} preset {i} ({p['label']!r}) has no weapons"
            )


def test_every_preset_has_at_least_one_mag(vehicles):
    for v in vehicles:
        for i, p in enumerate(v["presets"]):
            assert len(p["mags"]) >= 1, (
                f"{v['class']} preset {i} ({p['label']!r}) has no mags"
            )


def test_every_preset_price_is_nonnegative_int(vehicles):
    # Ka137_MG_PMC's Recon preset is free — the loadout manager allows $0 rows.
    for v in vehicles:
        for i, p in enumerate(v["presets"]):
            assert isinstance(p["price"], int) and p["price"] >= 0, (
                f"{v['class']} preset {i}: price {p['price']!r} is not a non-negative int"
            )


def test_every_preset_label_is_nonempty_str(vehicles):
    for v in vehicles:
        for i, p in enumerate(v["presets"]):
            assert isinstance(p["label"], str) and p["label"].strip(), (
                f"{v['class']} preset {i}: label is empty or not a string"
            )


def test_weapons_are_strings(vehicles):
    for v in vehicles:
        for i, p in enumerate(v["presets"]):
            for w in p["weapons"]:
                assert isinstance(w, str), (
                    f"{v['class']} preset {i}: weapon {w!r} is not a string"
                )


def test_mags_are_strings(vehicles):
    for v in vehicles:
        for i, p in enumerate(v["presets"]):
            for m in p["mags"]:
                assert isinstance(m, str), (
                    f"{v['class']} preset {i}: mag {m!r} is not a string"
                )


def test_defaults_have_weapons_and_mags(vehicles):
    for v in vehicles:
        assert isinstance(v["default"]["weapons"], list), (
            f"{v['class']} default weapons not a list"
        )
        assert isinstance(v["default"]["mags"], list), (
            f"{v['class']} default mags not a list"
        )
        # Su25_Ins ships with an empty EASA default (factory weapons untouched),
        # so empty lists are valid; both lists must agree on emptiness though.
        assert (len(v["default"]["weapons"]) >= 1) == (len(v["default"]["mags"]) >= 1), (
            f"{v['class']} default has weapons/mags mismatch"
        )


# ---------------------------------------------------------------------------
# Low-level tokeniser / parser unit tests
# ---------------------------------------------------------------------------


def test_tokenise_simple():
    from gen_easa_seed import _tokenise, _TOK_LBRAK, _TOK_RBRAK, _TOK_STR, _TOK_INT, _TOK_COMMA
    toks = _tokenise("['Su34',16400]")
    types = [t[0] for t in toks]
    assert types == [_TOK_LBRAK, _TOK_STR, _TOK_COMMA, _TOK_INT, _TOK_RBRAK]
    assert toks[1][1] == "Su34"
    assert toks[3][1] == 16400


def test_parse_nested_array():
    result = _parse_sqf_array("[['a','b'],['c']]")
    assert result == [["a", "b"], ["c"]]


def test_parse_empty_array():
    assert _parse_sqf_array("[]") == []


def test_parse_single_quoted_escape():
    # '' inside a string = literal single quote
    result = _parse_sqf_array("['it''s']")
    assert result == ["it's"]
