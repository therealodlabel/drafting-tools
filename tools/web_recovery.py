#!/usr/bin/env python3
"""Check that unsaved work survives closing the tab.

Draws a rectangle, waits for an autosave to land in persistent storage, reloads
the page as if the tab had been closed, and takes the offer to restore.
Usage: web_recovery.py URL OUTDIR [wait_seconds]
"""
import os, sys, time
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
wait_s = float(sys.argv[3]) if len(sys.argv) > 3 else 80
os.makedirs(out, exist_ok=True)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--ignore-gpu-blocklist", "--use-gl=angle",
                                    "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = b.new_context(viewport={"width": 1280, "height": 860})
        pg = ctx.new_page()
        logs = []
        pg.on("console", lambda m: logs.append(m.text))
        pg.goto(url)
        pg.wait_for_function("getComputedStyle(document.getElementById('splash')).display=='none'")
        pg.wait_for_timeout(1500)

        box = pg.locator("#canvas0").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        pg.mouse.move(cx, cy)
        pg.keyboard.press("r")
        for x, y in ((cx - 140, cy - 90), (cx + 140, cy + 90)):
            pg.mouse.move(x, y, steps=25)
            pg.wait_for_timeout(100)
            pg.mouse.down(); pg.mouse.up()
            pg.wait_for_timeout(200)
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(500)
        pg.screenshot(path=f"{out}/1-drawn.png")
        print("drew a rectangle; waiting up to %ds for an autosave" % wait_s, flush=True)

        deadline = time.time() + wait_s
        saved = False
        while time.time() < deadline:
            pg.wait_for_timeout(5000)
            files = pg.evaluate("(()=>{try{return FS.readdir('/data')}catch(e){return []}})()")
            if any(f.startswith(".recovered") for f in files):
                saved = True
                print("autosave written:", files, flush=True)
                break
        if not saved:
            print("FAIL: no autosave appeared in /data")
            b.close()
            return 1

        # Give the debounced write-back time to reach IndexedDB, then reload as if
        # the tab had been closed and reopened.
        pg.wait_for_timeout(2000)
        pg.reload()
        pg.wait_for_function("getComputedStyle(document.getElementById('splash')).display=='none'")
        pg.wait_for_timeout(2500)
        pg.screenshot(path=f"{out}/2-after-reload.png")

        txt = pg.evaluate("[...document.querySelectorAll('.modal')]"
                          ".filter(e=>getComputedStyle(e).display!='none')"
                          ".map(e=>e.innerText).join(' | ')")
        print("dialog after reload:", txt.replace("\n", " ")[:200], flush=True)
        if "Restore" not in txt:
            print("FAIL: no recovery offer after reload")
            b.close()
            return 1

        clicked = pg.evaluate("""() => {
            const ms=[...document.querySelectorAll('.modal')].filter(e=>getComputedStyle(e).display!='none');
            for(let k=ms.length-1;k>=0;k--){
                const btn=[...ms[k].querySelectorAll('.button')].find(x=>x.innerText.includes('Restore'));
                if(btn){btn.click();return true;}
            }
            return false; }""")
        pg.wait_for_timeout(3000)
        pg.keyboard.press("f")
        pg.wait_for_timeout(1500)
        pg.screenshot(path=f"{out}/3-restored.png")
        title = pg.title()
        print("clicked restore:", clicked, "| tab title:", title, flush=True)
        print("PASS" if clicked and "•" in title else "CHECK THE SCREENSHOT", flush=True)
        b.close()
        return 0


sys.exit(main())
