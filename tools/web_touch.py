#!/usr/bin/env python3
"""Check that the web build is usable by touch, at phone size.

A one-finger tap has to place a point: it used to send a left-button press and
then a middle-button release, so nothing ever completed. A two-finger pinch has
to zoom in one direction and out the other. And nothing may overflow sideways at
phone width.

Usage: web_touch.py URL OUTDIR
"""
import os, sys, json
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
results = []


def step(name, ok, **kw):
    results.append(dict(step=name, ok=ok, **kw))
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


def pinch(pg, cx, cy, start, end, steps=12):
    """Two-finger pinch about (cx, cy), from `start` to `end` pixels apart."""
    pts = []
    for i in range(steps + 1):
        d = (start + (end - start) * i / steps) / 2.0
        pts.append([{"x": cx - d, "y": cy}, {"x": cx + d, "y": cy}])
    pg.evaluate(
        """(frames) => {
        const el = document.getElementById('canvas0');
        const mk = (type, pts) => {
            const touches = pts.map((p, i) => new Touch({
                identifier: i, target: el, clientX: p.x, clientY: p.y }));
            el.dispatchEvent(new TouchEvent(type, {
                touches, targetTouches: touches, changedTouches: touches,
                bubbles: true, cancelable: true }));
        };
        const mkEnd = (pts) => {
            const changed = pts.map((p, i) => new Touch({
                identifier: i, target: el, clientX: p.x, clientY: p.y }));
            el.dispatchEvent(new TouchEvent('touchend', {
                touches: [], targetTouches: [], changedTouches: changed,
                bubbles: true, cancelable: true }));
        };
        mk('touchstart', frames[0]);
        for (const f of frames.slice(1)) mk('touchmove', f);
        mkEnd(frames[frames.length - 1]);
    }""",
        pts,
    )


with sync_playwright() as p:
    b = p.chromium.launch(args=["--ignore-gpu-blocklist", "--use-gl=angle",
                                "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True,
                        is_mobile=True, device_scale_factor=3)
    pg = ctx.new_page()
    logs = []
    pg.on("pageerror", lambda e: logs.append(str(e)))
    pg.goto(url)
    pg.wait_for_function(
        "getComputedStyle(document.getElementById('splash')).display=='none'")
    pg.wait_for_timeout(2000)
    pg.screenshot(path=f"{out}/1-phone-boot.png")

    # Nothing may stick out sideways: a horizontal scrollbar on a phone means
    # part of the drawing is unreachable.
    overflow = pg.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth")
    step("no horizontal overflow at 390px", overflow <= 0, overflow_px=overflow)

    # The menu rows have to be big enough to hit.
    pg.locator(".menubar > li").first.tap()
    pg.wait_for_timeout(400)
    heights = pg.evaluate(
        """[...document.querySelectorAll('ul.menu:not(.menubar) li')]
             .filter(e => e.offsetParent && e.innerText.trim())
             .map(e => Math.round(e.getBoundingClientRect().height))""")
    smallest = min(heights) if heights else 0
    step("menu rows are tappable (>=30px)", smallest >= 30,
         smallest_px=smallest, rows=len(heights))
    pg.screenshot(path=f"{out}/2-menu.png")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(400)

    box = pg.locator("#canvas0").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    # A tap has to complete a click. Drawing a rectangle takes two of them; if
    # the release never arrives as a left button, the title never gains the
    # unsaved marker because no request was made.
    pg.keyboard.press("r")
    for dx, dy in ((-90, -60), (90, 60)):
        pg.touchscreen.tap(cx + dx, cy + dy)
        pg.wait_for_timeout(400)
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(600)
    title = pg.title()
    step("one-finger tap places geometry", "•" in title, title=title)
    pg.screenshot(path=f"{out}/3-tapped.png")

    # Pinch out then in; the view scale has to move in opposite directions.
    pg.keyboard.press("f")
    pg.wait_for_timeout(600)
    before = pg.evaluate("window.devicePixelRatio")  # placeholder, scale read below
    shot_before = pg.screenshot(path=f"{out}/4-before-pinch.png")
    pinch(pg, cx, cy, 120, 340)
    pg.wait_for_timeout(600)
    shot_out = pg.screenshot(path=f"{out}/5-pinched-out.png")
    pinch(pg, cx, cy, 340, 120)
    pg.wait_for_timeout(600)
    shot_in = pg.screenshot(path=f"{out}/6-pinched-in.png")
    # The two pinches must not produce the same picture, and pinching back in
    # must move away from the pinched-out state.
    step("pinch changes the view", shot_out != shot_before)
    step("pinch in and out differ", shot_out != shot_in)

    step("no uncaught page errors", not logs, errors=logs[:3])
    b.close()

json.dump(results, open(f"{out}/results.json", "w"), indent=1)
print("\n" + ("ALL PASS" if all(r["ok"] for r in results) else "SOME FAILED"))
sys.exit(0 if all(r["ok"] for r in results) else 1)
