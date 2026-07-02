"""
gen_easa_seed.py
Parse WASP mission EASA_Init.sqf into easa-seed.json.

Usage:
    python tools/gen_easa_seed.py [--sqf PATH] [--out PATH]
    python tools/gen_easa_seed.py --emit [--json PATH] [--out PATH]

The --emit mode regenerates per-vehicle SQF registration blocks from the
JSON (house style matching the original file).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQF = (
    Path(r"C:\Users\Miksuu\Documents\projects\a2waspwarfare\Missions")
    / r"[55-2hc]warfarev2_073v48co.chernarus"
    / r"Client\Module\EASA\EASA_Init.sqf"
)
DEFAULT_JSON = REPO_ROOT / "assets" / "data" / "easa-seed.json"
SOURCE_FILE_REL = "Client/Module/EASA/EASA_Init.sqf"

# ---------------------------------------------------------------------------
# SQF tokeniser / array parser
# ---------------------------------------------------------------------------

# Token types
_TOK_LBRAK = "["
_TOK_RBRAK = "]"
_TOK_COMMA = ","
_TOK_INT = "INT"
_TOK_STR = "STR"


def _tokenise(text: str) -> list[tuple[str, Any]]:
    """Tokenise SQF array literal text into (type, value) pairs.

    Handles:
    - Single-quoted strings (SQF style): 'foo'
    - Integers (positive only in this dataset)
    - '[' ']' ',' structural characters
    - '//' and '/* */' comments stripped beforehand
    """
    tokens: list[tuple[str, Any]] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in " \t\r\n":
            i += 1
        elif ch == "[":
            tokens.append((_TOK_LBRAK, "["))
            i += 1
        elif ch == "]":
            tokens.append((_TOK_RBRAK, "]"))
            i += 1
        elif ch == ",":
            tokens.append((_TOK_COMMA, ","))
            i += 1
        elif ch == "'":
            # single-quoted string; '' is an escaped single quote
            i += 1
            buf: list[str] = []
            while i < n:
                c = text[i]
                if c == "'":
                    if i + 1 < n and text[i + 1] == "'":
                        buf.append("'")
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    buf.append(c)
                    i += 1
            tokens.append((_TOK_STR, "".join(buf)))
        elif ch.isdigit() or (ch == "-" and i + 1 < n and text[i + 1].isdigit()):
            j = i + 1
            while j < n and text[j].isdigit():
                j += 1
            tokens.append((_TOK_INT, int(text[i:j])))
            i = j
        else:
            # skip unexpected characters (shouldn't happen in well-formed SQF)
            i += 1
    return tokens


class _Parser:
    """Recursive-descent parser over a token list.

    Parses SQF array literals: [ val, val, ... ]
    where val is an int, a string, or a nested array.
    """

    def __init__(self, tokens: list[tuple[str, Any]]) -> None:
        self._tok = tokens
        self._pos = 0

    def _peek(self) -> tuple[str, Any] | None:
        if self._pos < len(self._tok):
            return self._tok[self._pos]
        return None

    def _consume(self, expected_type: str | None = None) -> tuple[str, Any]:
        tok = self._tok[self._pos]
        if expected_type and tok[0] != expected_type:
            raise ValueError(
                f"Expected {expected_type} at pos {self._pos}, got {tok}"
            )
        self._pos += 1
        return tok

    def parse_value(self) -> Any:
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of tokens")
        if tok[0] == _TOK_LBRAK:
            return self.parse_array()
        elif tok[0] == _TOK_INT:
            self._consume()
            return tok[1]
        elif tok[0] == _TOK_STR:
            self._consume()
            return tok[1]
        else:
            raise ValueError(f"Unexpected token {tok} at pos {self._pos}")

    def parse_array(self) -> list:
        self._consume(_TOK_LBRAK)
        items: list = []
        tok = self._peek()
        if tok and tok[0] == _TOK_RBRAK:
            self._consume(_TOK_RBRAK)
            return items
        items.append(self.parse_value())
        while True:
            tok = self._peek()
            if tok is None or tok[0] == _TOK_RBRAK:
                break
            if tok[0] == _TOK_COMMA:
                self._consume(_TOK_COMMA)
                # trailing comma: if next is ], stop
                tok2 = self._peek()
                if tok2 and tok2[0] == _TOK_RBRAK:
                    break
                items.append(self.parse_value())
            else:
                raise ValueError(f"Expected , or ] at pos {self._pos}, got {tok}")
        self._consume(_TOK_RBRAK)
        return items


def _strip_comments(text: str) -> str:
    """Remove // and /* */ style comments, but preserve block-comment text as
    a special marker so we can reconstruct the vehicle header comment.

    Strategy: replace /* ... */ with a placeholder containing the comment text,
    and strip // to end-of-line. Return a tuple (cleaned_text, comment_map).

    Actually we need the /* */ comments for vehicle headers, so we handle them
    separately in the main parser by scanning for them BEFORE stripping.
    This function is used only for tokenising array bodies (after we've already
    extracted the per-vehicle blocks).
    """
    # Strip /* */ comments
    result = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # Strip // comments
    result = re.sub(r"//[^\n]*", "", result)
    return result


# ---------------------------------------------------------------------------
# High-level SQF block extractor
# ---------------------------------------------------------------------------

_COMMENT_RE = re.compile(
    r"//\s*(?P<label>[^\n]+?)\s*-\s*(?P<pylons>\d+)\s+pylons"
)
# Matches: // Su-34 [AF5] - 10 pylons
_BLOCK_COMMENT_RE = re.compile(
    r"/\*\s*(?P<label>[^\n*]+?)\s*-\s*(?P<pylons>\d+)\s+pylons\s*\*/"
)

# Match "_easaVehi = _easaVehi + ['ClassName'];"
_VEHI_RE = re.compile(r"_easaVehi\s*=\s*_easaVehi\s*\+\s*\[(?P<body>[^\]]*)\]\s*;")
# Match "_easaDefault = _easaDefault + [<value>];"  – value can be nested
# We grab everything from the first '[' after '+' up to the matching ']';
_DEFAULT_PREFIX = "_easaDefault = _easaDefault +"
_LOADOUT_PREFIX = "_easaLoadout = _easaLoadout +"


def _find_matching_bracket(text: str, start: int) -> int:
    """Return the index of the ']' that closes the '[' at text[start]."""
    assert text[start] == "["
    depth = 0
    i = start
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return i
        elif ch == "'":
            # skip string
            i += 1
            while i < n:
                c = text[i]
                if c == "'":
                    if i + 1 < n and text[i + 1] == "'":
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    i += 1
            continue
        i += 1
    raise ValueError(f"No matching ']' found starting at pos {start}")


def _parse_sqf_array(text: str) -> Any:
    """Parse a SQF array literal string (must start with '[')."""
    clean = _strip_comments(text)
    tokens = _tokenise(clean)
    parser = _Parser(tokens)
    return parser.parse_array()


def _extract_array_after(text: str, pos: int) -> tuple[Any, int]:
    """Find the first '[' at or after pos, parse the nested array, return
    (parsed_value, end_pos_exclusive)."""
    start = text.index("[", pos)
    end = _find_matching_bracket(text, start)
    chunk = text[start : end + 1]
    return _parse_sqf_array(chunk), end + 1


# ---------------------------------------------------------------------------
# Per-vehicle header comment finder
# ---------------------------------------------------------------------------

def _find_vehicle_comment(text: str, pos: int) -> tuple[str | None, int | None]:
    """Look backwards from pos for the most recent // or /* */ comment that
    contains a pylon count (e.g. '// Su-34 [AF5] - 10 pylons').

    Returns (comment_text, pylons_int) or (None, None) if not found.
    We search within 300 characters before pos.
    """
    window = text[max(0, pos - 400) : pos]
    # Try // style first (most common in this file)
    matches = list(_COMMENT_RE.finditer(window))
    if matches:
        m = matches[-1]
        pylons = int(m.group("pylons"))
        label = m.group("label").strip()
        full_comment = f"{label} - {pylons} pylons"
        return full_comment, pylons
    # Try /* */ style
    matches2 = list(_BLOCK_COMMENT_RE.finditer(window))
    if matches2:
        m2 = matches2[-1]
        pylons = int(m2.group("pylons"))
        label = m2.group("label").strip()
        full_comment = f"{label} - {pylons} pylons"
        return full_comment, pylons
    return None, None


# ---------------------------------------------------------------------------
# Main parse function
# ---------------------------------------------------------------------------

def parse_easa_sqf(path: Path) -> list[dict]:
    """Parse EASA_Init.sqf and return list of vehicle dicts."""
    text = path.read_text(encoding="utf-8")

    vehicles: list[dict] = []

    # Find all occurrences of the three parallel-array additions in order.
    # We look for "_easaVehi = _easaVehi +" and record its position, then
    # find the matching "_easaDefault" and "_easaLoadout" additions nearby.

    # Strategy: scan sequentially for _easaVehi additions, then for each one
    # find the immediately following _easaDefault and _easaLoadout additions.

    vehi_positions = [m.start() for m in re.finditer(r"_easaVehi\s*=\s*_easaVehi\s*\+", text)]

    for vp in vehi_positions:
        # Parse classname from _easaVehi + ['ClassName']
        # Find '[' after '+'
        try:
            vehi_arr, after_vehi = _extract_array_after(text, vp)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse _easaVehi at pos {vp}: {e}") from e

        if not vehi_arr or not isinstance(vehi_arr[0], str):
            continue
        classname = vehi_arr[0]

        # Find comment (look backwards from vp for up to 400 chars)
        comment, pylons = _find_vehicle_comment(text, vp)

        # Find _easaDefault = _easaDefault + after vp
        dp = text.find("_easaDefault = _easaDefault +", after_vehi)
        if dp == -1 or dp - after_vehi > 5000:
            raise ValueError(
                f"Cannot find _easaDefault addition for {classname} near pos {after_vehi}"
            )
        try:
            default_arr, after_default = _extract_array_after(text, dp)
        except (ValueError, IndexError) as e:
            raise ValueError(
                f"Failed to parse _easaDefault for {classname} at pos {dp}: {e}"
            ) from e

        # default_arr is [ [[weapons], [mags]] ] — the outer wrapping
        # The structure is _easaDefault + [ DEFAULT_LOADOUT ]
        # where DEFAULT_LOADOUT = [[weapon1,...],[mag1,...]]
        # so default_arr = [[weapons_list],[mags_list]]
        if not default_arr or not isinstance(default_arr[0], list):
            raise ValueError(
                f"Unexpected _easaDefault structure for {classname}: {default_arr!r}"
            )
        default_loadout = default_arr[0]  # [[weapons],[mags]]
        if len(default_loadout) < 2:
            raise ValueError(
                f"_easaDefault for {classname} has < 2 elements: {default_loadout!r}"
            )
        default_weapons = default_loadout[0]
        default_mags = default_loadout[1]

        # Find _easaLoadout = _easaLoadout + after default
        lp = text.find("_easaLoadout = _easaLoadout +", after_default)
        if lp == -1 or lp - after_default > 5000:
            raise ValueError(
                f"Cannot find _easaLoadout addition for {classname} near pos {after_default}"
            )
        try:
            loadout_arr, _ = _extract_array_after(text, lp)
        except (ValueError, IndexError) as e:
            raise ValueError(
                f"Failed to parse _easaLoadout for {classname} at pos {lp}: {e}"
            ) from e

        # loadout_arr = [ [ preset, preset, ... ] ]
        # i.e. the outer list wrapping means loadout_arr[0] is the preset list
        if not loadout_arr or not isinstance(loadout_arr[0], list):
            raise ValueError(
                f"Unexpected _easaLoadout structure for {classname}: {loadout_arr!r}"
            )
        raw_presets = loadout_arr[0]

        presets = []
        for i, row in enumerate(raw_presets):
            # row = [price, 'label', [[weapons], [mags]]]
            # (4th element if present is computed AA flag — ignore)
            if not isinstance(row, list) or len(row) < 3:
                raise ValueError(
                    f"Preset {i} for {classname} has unexpected structure: {row!r}"
                )
            price = row[0]
            label = row[1]
            loadout = row[2]
            if not isinstance(price, int):
                raise ValueError(
                    f"Preset {i} for {classname}: price is not int: {price!r}"
                )
            if not isinstance(label, str):
                raise ValueError(
                    f"Preset {i} for {classname}: label is not str: {label!r}"
                )
            if not isinstance(loadout, list) or len(loadout) < 2:
                raise ValueError(
                    f"Preset {i} for {classname}: loadout structure invalid: {loadout!r}"
                )
            preset_weapons = loadout[0]
            preset_mags = loadout[1]
            presets.append(
                {
                    "price": price,
                    "label": label,
                    "weapons": preset_weapons,
                    "mags": preset_mags,
                }
            )

        vehicles.append(
            {
                "class": classname,
                "comment": comment,
                "pylons": pylons,
                "default": {
                    "weapons": default_weapons,
                    "mags": default_mags,
                },
                "presets": presets,
            }
        )

    return vehicles


def build_seed(sqf_path: Path) -> dict:
    vehicles = parse_easa_sqf(sqf_path)
    return {
        "sourceFile": SOURCE_FILE_REL,
        "vehicles": vehicles,
    }


# ---------------------------------------------------------------------------
# Emit mode — regenerate per-vehicle SQF blocks from JSON
# ---------------------------------------------------------------------------

def _sqf_str(s: str) -> str:
    """Encode a Python string as a SQF single-quoted string."""
    return "'" + s.replace("'", "''") + "'"


def _sqf_str_list(items: list[str]) -> str:
    """Encode a list of strings as a SQF array: ['a','b',...]."""
    return "[" + ",".join(_sqf_str(x) for x in items) + "]"


def emit_vehicle_block(v: dict) -> str:
    """Emit the SQF registration block for one vehicle, matching house style."""
    classname = v["class"]
    comment = v.get("comment")
    pylons = v.get("pylons")

    lines: list[str] = []

    # Header comment: "// Su-34 [AF5] - 10 pylons"
    # comment already contains the full string (e.g. "Su-34 [AF5] - 10 pylons")
    if comment:
        lines.append(f"// {comment}")

    # _easaVehi line
    lines.append(f"_easaVehi = _easaVehi + [{_sqf_str(classname)}];")

    # _easaDefault line
    dw = _sqf_str_list(v["default"]["weapons"])
    dm = _sqf_str_list(v["default"]["mags"])
    lines.append(f"_easaDefault = _easaDefault + [[{dw},{dm}]];")

    # _easaLoadout block
    lines.append("_easaLoadout = _easaLoadout + [")
    lines.append("[")
    preset_strs = []
    for p in v["presets"]:
        pw = _sqf_str_list(p["weapons"])
        pm = _sqf_str_list(p["mags"])
        label = _sqf_str(p["label"])
        preset_strs.append(f"[{p['price']},{label},[{pw},{pm}]]")
    lines.append(",\n".join(preset_strs))
    lines.append("]")
    lines.append("];")

    return "\n".join(lines)


def emit_all_blocks(seed: dict) -> str:
    """Emit all vehicle blocks, joined by blank lines."""
    return "\n\n".join(emit_vehicle_block(v) for v in seed["vehicles"])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    ap = argparse.ArgumentParser(description="Parse or emit EASA_Init.sqf data")
    ap.add_argument(
        "--emit",
        action="store_true",
        help="Regenerate SQF blocks from JSON instead of parsing SQF",
    )
    ap.add_argument(
        "--sqf",
        type=Path,
        default=DEFAULT_SQF,
        help="Path to EASA_Init.sqf (parse mode, default: mission file)",
    )
    ap.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        default=DEFAULT_JSON,
        help="Path to easa-seed.json (emit mode input / parse mode output)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output file (default: stdout for --emit, easa-seed.json for parse)",
    )
    args = ap.parse_args()

    if args.emit:
        # Read JSON → emit SQF blocks
        src = args.json_path
        if not src.exists():
            print(f"ERROR: JSON not found: {src}", file=sys.stderr)
            sys.exit(1)
        seed = json.loads(src.read_text(encoding="utf-8"))
        output = emit_all_blocks(seed)
        if args.out:
            args.out.write_text(output, encoding="utf-8")
            print(f"Written to {args.out}")
        else:
            print(output)
    else:
        # Parse SQF → JSON
        sqf = args.sqf
        if not sqf.exists():
            print(f"ERROR: SQF not found: {sqf}", file=sys.stderr)
            sys.exit(1)
        seed = build_seed(sqf)
        out = args.out or DEFAULT_JSON
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(seed, indent=2, ensure_ascii=False), encoding="utf-8")
        n_vehicles = len(seed["vehicles"])
        n_presets = sum(len(v["presets"]) for v in seed["vehicles"])
        print(f"Parsed {n_vehicles} vehicles, {n_presets} total presets -> {out}")


if __name__ == "__main__":
    _cli()
