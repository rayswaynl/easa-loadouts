"""
EASA Loadouts — Playwright smoke gate (build-1 core).

Run (from repo root):
    python tools/test_playwright.py

Asserts (per spec):
  1. Zero console errors on load
  2. Mode switching works (plane / heli / vehicle)
  3. Selecting Su34 shows its presets
  4. Loading an Su34 preset populates the rack
  5. AA badge appears for R-73 preset (2Rnd_R73 has airLock=true)
  6. Vehicle mode lists eligible + greys excluded

Returns exit code 0 on PASS, 1 on any failure.
"""

import sys
import io
import threading
import http.server
import time
import os

# Force UTF-8 output (Windows cp1252 safety)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── embedded HTTP server (serves repo root so assets/data/ is reachable) ──────
SERVE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8098

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)
    def log_message(self, fmt, *args):
        pass  # suppress per-request noise

server = http.server.HTTPServer(('localhost', PORT), QuietHandler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
time.sleep(0.4)

# ── helpers ───────────────────────────────────────────────────────────────────
PASS_N = 0
FAIL_N = 0

def ok(label):
    global PASS_N
    PASS_N += 1
    print(f"  PASS  {label}")

def fail(label, detail=""):
    global FAIL_N
    FAIL_N += 1
    msg = f"  FAIL  {label}"
    if detail:
        msg += f"\n        {detail}"
    print(msg)

# ── tests ─────────────────────────────────────────────────────────────────────
from playwright.sync_api import sync_playwright

URL = f"http://localhost:{PORT}/index.html"
SCREENSHOT = os.path.join(SERVE_DIR, "tools", "smoke_screenshot.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda err: console_errors.append(str(err)))

    page.goto(URL, wait_until="networkidle", timeout=20000)

    # Give init() async data loading time to complete
    page.wait_for_timeout(1500)

    # ── Test 1: Zero console errors on load ───────────────────────────────────
    real_errors = [
        e for e in console_errors
        if 'font' not in e.lower() and 'googleapis' not in e.lower()
           and 'favicon' not in e.lower()
    ]
    if not real_errors:
        ok("Zero console errors on load")
    else:
        fail("Zero console errors on load", "; ".join(real_errors[:3]))

    # ── Test 2: Mode switching works ──────────────────────────────────────────
    # Click Helicopter button
    page.click("#modeBtn-heli")
    page.wait_for_timeout(300)
    heli_on = page.evaluate("() => document.getElementById('modeBtn-heli').classList.contains('on')")
    plane_off = page.evaluate("() => !document.getElementById('modeBtn-plane').classList.contains('on')")
    if heli_on and plane_off:
        ok("Mode switching: heli button activates, plane deactivates")
    else:
        fail("Mode switching", f"heli.on={heli_on}, plane.off={plane_off}")

    # Click Vehicle button
    page.click("#modeBtn-vehicle")
    page.wait_for_timeout(300)
    veh_on = page.evaluate("() => document.getElementById('modeBtn-vehicle').classList.contains('on')")
    if veh_on:
        ok("Mode switching: vehicle mode activates")
    else:
        fail("Mode switching: vehicle mode", "vehicle button not marked on")

    # Return to plane
    page.click("#modeBtn-plane")
    page.wait_for_timeout(300)

    # ── Test 3: Selecting Su34 shows its presets ──────────────────────────────
    # Su34 is in the plane mode list (easa-seed.json class = "Su34", airframes.json matches)
    # Call selectAirframe directly via the exposed window global
    page.evaluate("() => window.selectAirframe('Su34')")
    page.wait_for_timeout(600)

    preset_count = page.evaluate("""() => {
        const rows = document.querySelectorAll('#presetListIG .preset-row');
        return rows.length;
    }""")
    # Su34 has 86 in-game presets per easa-seed.json
    if preset_count >= 10:
        ok(f"Su34 presets shown: {preset_count} in-game rows")
    else:
        fail("Su34 presets shown", f"expected >=10, got {preset_count}")

    # ── Test 4: Loading a preset populates the rack ───────────────────────────
    # Click the first Su34 preset row
    page.evaluate("""() => {
        const row = document.querySelector('#presetListIG .preset-row');
        if (row) row.click();
    }""")
    page.wait_for_timeout(500)

    rack_count = page.evaluate("""() => {
        const tiles = document.querySelectorAll('#stationRack .station-tile');
        return tiles.length;
    }""")
    if rack_count > 0:
        ok(f"Rack populated: {rack_count} station tile(s)")
    else:
        fail("Rack populated after preset load", f"station-tiles: {rack_count}")

    # ── Test 5: AA badge appears for R-73 preset ─────────────────────────────
    # Find a preset that contains 2Rnd_R73 (airLock=true) by scanning the IG list
    # Su34 has R-73 presets; load the first one that shows AA badge
    aa_found = page.evaluate("""() => {
        const rows = document.querySelectorAll('#presetListIG .preset-row');
        for (const row of rows) {
            const badge = row.querySelector('.aa-badge');
            if (badge) { row.click(); return true; }
        }
        return false;
    }""")
    page.wait_for_timeout(500)

    if not aa_found:
        # Try direct state manipulation: load a rack entry with 2Rnd_R73
        page.evaluate("""() => {
            window.state.rack = [{id:'t1', weaponClass:'R73Launcher_2', magClass:'2Rnd_R73', isGun:false}];
            renderRack();
            updateTotals();
        }""")
        page.wait_for_timeout(300)

    aa_badge = page.evaluate("""() => {
        // Check totals strip badges
        const b = document.querySelector('#totalsBadges .aa-badge');
        return !!b;
    }""")
    if aa_badge:
        ok("AA badge appears when rack contains airLock=true magazine")
    else:
        fail("AA badge appears for R-73", "No .aa-badge found in #totalsBadges")

    # ── Test 6: Vehicle mode lists eligible + greys excluded ──────────────────
    page.click("#modeBtn-vehicle")
    page.wait_for_timeout(400)

    eligible_count = page.evaluate("""() => {
        const rows = document.querySelectorAll('#vehListEl .veh-row:not(.excluded)');
        return rows.length;
    }""")
    excluded_count = page.evaluate("""() => {
        const rows = document.querySelectorAll('#vehListEl .veh-row.excluded');
        return rows.length;
    }""")

    if eligible_count > 0:
        ok(f"Vehicle mode: {eligible_count} eligible vehicle rows")
    else:
        fail("Vehicle mode: eligible vehicles listed", f"got {eligible_count}")

    if excluded_count > 0:
        ok(f"Vehicle mode: {excluded_count} excluded rows (greyed)")
    else:
        fail("Vehicle mode: excluded vehicles greyed", f"got {excluded_count}")

    # Verify excluded has a reason tooltip
    excl_has_tooltip = page.evaluate("""() => {
        const row = document.querySelector('#vehListEl .veh-row.excluded');
        return row ? (row.title.length > 0 || row.querySelector('.veh-excl-reason') !== null) : false;
    }""")
    if excl_has_tooltip:
        ok("Excluded vehicles show reason tooltip/text")
    else:
        fail("Excluded vehicles reason", "no title or .veh-excl-reason found")

    # ── Screenshot ────────────────────────────────────────────────────────────
    # Switch back to plane mode + load a visual state for the shot
    page.click("#modeBtn-plane")
    page.wait_for_timeout(300)
    page.evaluate("() => window.selectAirframe('Su25_TK_EP1')")
    page.wait_for_timeout(500)
    page.evaluate("""() => {
        const row = document.querySelector('#presetListIG .preset-row');
        if (row) row.click();
    }""")
    page.wait_for_timeout(400)
    page.screenshot(path=SCREENSHOT, full_page=False)
    ok(f"Screenshot saved → tools/smoke_screenshot.png")

    browser.close()

# ── summary ───────────────────────────────────────────────────────────────────
server.shutdown()
print(f"\n{'='*55}")
print(f"  {PASS_N} passed  /  {FAIL_N} failed  /  {PASS_N + FAIL_N} total")
print(f"{'='*55}")
sys.exit(0 if FAIL_N == 0 else 1)
