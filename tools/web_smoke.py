#!/usr/bin/env python3
"""Load the SolveSpace web build in headless Chromium and report what happens.
Usage: web_smoke.py URL SHOT.png [--gpu-flags=swiftshader|none] [--wait=S]
"""
import sys, time, json
from playwright.sync_api import sync_playwright

url, shot = sys.argv[1], sys.argv[2]
opts = dict(a.split("=", 1) for a in sys.argv[3:] if a.startswith("--"))
gpu = opts.get("--gpu-flags", "swiftshader")
wait = float(opts.get("--wait", "15"))

args = ["--ignore-gpu-blocklist"]
if gpu == "swiftshader":
    args += ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]

with sync_playwright() as p:
    b = p.chromium.launch(args=args)
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    logs = []
    pg.on("console", lambda m: logs.append(f"[{m.type}] {m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"[pageerror] {e}"))
    reqs = []
    pg.on("request", lambda r: reqs.append(r.url))
    t0 = time.time()
    pg.goto(url)
    pg.wait_for_timeout(wait * 1000)
    info = pg.evaluate("""() => ({
        crossOriginIsolated: self.crossOriginIsolated,
        sab: typeof SharedArrayBuffer,
        status: (document.getElementById('status')||{}).innerText,
        splashVisible: !!document.querySelector('#splash') && getComputedStyle(document.querySelector('#splash')).display,
        canvas0: (()=>{const c=document.getElementById('canvas0'); return c? [c.width,c.height]:null})(),
        webgl: (()=>{const c=document.createElement('canvas'); const g=c.getContext('webgl',{failIfMajorPerformanceCaveat:true}); const g2=document.createElement('canvas').getContext('webgl'); return {strict: !!g, lenient: !!g2, renderer: g2 ? g2.getParameter(g2.RENDERER):null}})(),
        heapMB: (performance.memory? Math.round(performance.memory.usedJSHeapSize/1e6):null),
        menubar: Array.from(document.querySelectorAll('.menubar > li > .label, .menubar > li')).slice(0,12).map(e=>e.innerText.split('\\n')[0]),
    })""")
    pg.screenshot(path=shot)
    print(json.dumps(info, indent=1))
    print("load+wait seconds:", round(time.time() - t0, 1))
    ext = sorted({r.split('/')[2] for r in reqs if not r.startswith("http://127.0.0.1")})
    print("third-party hosts contacted:", ext)
    print("--- console (last 40) ---")
    for l in logs[-40:]:
        print(l[:300])
    b.close()
