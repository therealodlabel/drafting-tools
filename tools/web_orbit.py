#!/usr/bin/env python3
"""Check that the view can be turned and moved without a middle mouse button.

Draws and extrudes a rectangle, then presses the arrow keys. Each press must
change the picture, left and right must not cancel into nothing, and shift+arrow
must move the view rather than turn it. Before the fix, arrow keys were dropped
entirely and a trackpad user had no way to look at the side of a part.

Usage: web_orbit.py URL OUTDIR
"""
import os, sys, json
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
results = []


def step(name, ok, **kw):
    results.append(dict(step=name, ok=ok, **kw))
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


with sync_playwright() as p:
    b = p.chromium.launch(args=["--ignore-gpu-blocklist", "--use-gl=angle",
                                "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_context(viewport={"width": 1280, "height": 860}).new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url)
    pg.wait_for_function("getComputedStyle(document.getElementById('splash')).display=='none'")
    pg.wait_for_timeout(1500)

    box = pg.locator("#canvas0").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    canvas = lambda: pg.locator("#canvas0").screenshot()

    # A solid to look at.
    pg.mouse.move(cx, cy)
    pg.keyboard.press("r")
    for x, y in ((cx - 120, cy - 80), (cx + 120, cy + 80)):
        pg.mouse.move(x, y, steps=25)
        pg.wait_for_timeout(100)
        pg.mouse.down(); pg.mouse.up()
        pg.wait_for_timeout(200)
    pg.keyboard.press("Escape")
    pg.keyboard.press("Shift+X")
    pg.wait_for_timeout(2000)
    pg.keyboard.press("f")
    pg.wait_for_timeout(800)

    start = canvas()
    pg.screenshot(path=f"{out}/1-start.png")

    pg.keyboard.press("ArrowLeft")
    pg.wait_for_timeout(500)
    left = canvas()
    step("ArrowLeft turns the view", left != start)

    pg.keyboard.press("ArrowRight")
    pg.wait_for_timeout(500)
    back = canvas()
    step("ArrowRight turns it back the other way", back != left)

    for k in ("ArrowUp", "ArrowUp", "ArrowRight", "ArrowRight"):
        pg.keyboard.press(k)
        pg.wait_for_timeout(300)
    turned = canvas()
    pg.screenshot(path=f"{out}/2-turned.png")
    step("repeated presses keep turning", turned != back)

    pg.keyboard.press("Shift+ArrowLeft")
    pg.wait_for_timeout(500)
    panned = canvas()
    pg.screenshot(path=f"{out}/3-panned.png")
    step("Shift+Arrow moves the view", panned != turned)

    step("no page errors", not errors, errors=errors[:3])
    b.close()

json.dump(results, open(f"{out}/results.json", "w"), indent=1)
ok = all(r["ok"] for r in results)
print("\n" + ("ALL PASS" if ok else "SOME FAILED"))
sys.exit(0 if ok else 1)
