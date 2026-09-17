#!/usr/bin/env python3
"""Heavy-model and persistence behaviour of the SolveSpace web build.
Usage: web_heavy.py URL OUTDIR model.slvs...
"""
import json, os, sys, time
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
models = sys.argv[3:]
os.makedirs(out, exist_ok=True)
res = []


def rec(**kw):
    res.append(kw)
    print(json.dumps(kw), flush=True)


with sync_playwright() as p:
    b = p.chromium.launch(args=["--ignore-gpu-blocklist", "--use-gl=angle",
                                "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 1400, "height": 900}, accept_downloads=True)
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append(m.text))
    pg.on("pageerror", lambda e: logs.append("PAGEERROR " + str(e)))
    pg.on("dialog", lambda d: d.accept())
    pg.goto(url)
    pg.wait_for_function("getComputedStyle(document.getElementById('splash')).display=='none'")
    pg.wait_for_timeout(1500)

    def mem():
        return pg.evaluate("(()=>{try{return Math.round(HEAP8.buffer.byteLength/1048576)}catch(e){return null}})()")

    def click_btn(label):
        return pg.evaluate("""(label)=>{const ms=[...document.querySelectorAll('.modal')].filter(e=>getComputedStyle(e).display!='none');
            for(let k=ms.length-1;k>=0;k--){const b=[...ms[k].querySelectorAll('.button')].find(x=>x.innerText.includes(label)); if(b){b.click();return true;}}
            return false;}""", label)

    def open_model(path):
        for _ in range(4):
            if not click_btn("OK"):
                break
            pg.wait_for_timeout(200)
        pg.keyboard.press("Control+o")
        pg.wait_for_timeout(700)
        while True:
            txt = pg.evaluate("[...document.querySelectorAll('.modal')].filter(e=>getComputedStyle(e).display!='none').map(e=>e.innerText).join('|')")
            if "not saved" in txt or "Save" in txt and "File manager" not in txt:
                if not (click_btn("Don't") or click_btn("No")):
                    break
                pg.wait_for_timeout(600)
            else:
                break
        fi = pg.locator(".modal input[type=file]").filter(visible=True)
        if not fi.count():
            rec(step="open", file=os.path.basename(path), ok=False, why="no upload input")
            return
        t = time.time()
        fi.first.set_input_files(path)
        pg.wait_for_timeout(500)
        up = time.time() - t
        base = os.path.basename(path)
        radio = pg.locator(f'label[data-filename$="{base}"] input[type=radio]')
        if not radio.count():
            rec(step="open", file=base, ok=False, why="not listed after upload")
            return
        radio.first.check()
        t = time.time()
        click_btn("OK")
        pg.wait_for_timeout(300)
        pg.evaluate("1")  # round-trip: main thread is free again
        load = time.time() - t
        pg.keyboard.press("f")
        pg.wait_for_timeout(1000)
        pg.screenshot(path=f"{out}/heavy-{base}.png")
        txt = pg.evaluate("[...document.querySelectorAll('.modal')].filter(e=>getComputedStyle(e).display!='none').map(e=>e.innerText).join('|')")
        rec(step="open", file=base, ok=True, upload_s=round(up, 2), load_s=round(load, 2),
            wasm_mem_mb=mem(), modal=txt[:150])
        # interactive drag: rotate the view with the middle... use right-drag (rotate) 40 moves
        box = pg.locator("#canvas0").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        pg.mouse.move(cx, cy)
        t = time.time()
        pg.mouse.down(button="middle")
        for i in range(40):
            pg.mouse.move(cx + 3 * i, cy + 2 * i)
        pg.mouse.up(button="middle")
        pg.evaluate("1")
        rec(step="drag-rotate 40 moves", file=base, seconds=round(time.time() - t, 2),
            wasm_mem_mb=mem())

    for m in models:
        open_model(m)

    # persistence: what survives a reload?
    ls_before = pg.evaluate("Object.fromEntries(Object.entries(localStorage))")
    files_before = pg.evaluate("(()=>{try{return FS.readdir('/data')}catch(e){return 'FS not reachable: '+e}})()")
    pg.reload()
    pg.wait_for_function("getComputedStyle(document.getElementById('splash')).display=='none'")
    pg.wait_for_timeout(3000)
    files_after = pg.evaluate("(()=>{try{return FS.readdir('/data')}catch(e){return 'FS not reachable: '+e}})()")
    ls_after = pg.evaluate("Object.fromEntries(Object.entries(localStorage))")
    rec(step="persistence across reload", files_before=files_before, files_after=files_after,
        localStorage_keys=sorted(ls_after.keys()), recent_files=[v for k, v in ls_after.items() if k.startswith("RecentFile")])
    pg.screenshot(path=f"{out}/after-reload.png")
    json.dump({"results": res, "console_tail": logs[-40:]}, open(f"{out}/heavy.json", "w"), indent=1)
    b.close()
