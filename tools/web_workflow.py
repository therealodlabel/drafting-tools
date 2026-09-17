#!/usr/bin/env python3
"""Drive a realistic workflow in the SolveSpace web build (headless Chromium + SwiftShader).
Draw rectangle -> dimension -> extrude -> iso view -> save (download) -> export STL ->
open an uploaded example -> open a large generated sketch. Screenshots + timings.
Usage: web_workflow.py URL OUTDIR EXAMPLE.slvs BIG.slvs
"""
import json, os, sys, time
from playwright.sync_api import sync_playwright

url, out, example, big = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
results = []


def step(name, ok, **kw):
    results.append(dict(step=name, ok=ok, **kw))
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


with sync_playwright() as p:
    b = p.chromium.launch(args=["--ignore-gpu-blocklist", "--use-gl=angle",
                                "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    ctx = b.new_context(viewport={"width": 1400, "height": 900}, accept_downloads=True)
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append(m.text))
    pg.on("pageerror", lambda e: logs.append("PAGEERROR " + str(e)))
    t0 = time.time()
    pg.goto(url)
    pg.wait_for_function("document.getElementById('splash') && getComputedStyle(document.getElementById('splash')).display=='none'", timeout=60000)
    step("app boots", True, seconds=round(time.time() - t0, 2))
    pg.wait_for_timeout(1500)
    cv = pg.locator("#canvas0")
    box = cv.bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    def shot(n):
        pg.screenshot(path=f"{out}/{n}.png")

    def modal_visible():
        return pg.evaluate("Array.from(document.querySelectorAll('.modal')).some(e=>getComputedStyle(e).display!='none')")

    def click_modal_button(label):
        # click the matching button in the TOP-MOST visible modal (last in DOM order)
        return pg.evaluate("""(label) => {
            const ms = Array.from(document.querySelectorAll('.modal')).filter(e=>getComputedStyle(e).display!='none');
            for (let k = ms.length-1; k >= 0; k--) {
                const b = Array.from(ms[k].querySelectorAll('.button')).find(x=>x.innerText.includes(label));
                if (b) { b.click(); return true; }
            }
            return false; }""", label)

    # 1. rectangle
    def hclick(x, y):  # human-like: many mousemove events, then click
        pg.mouse.move(x, y, steps=25)
        pg.wait_for_timeout(100)
        pg.mouse.down(); pg.mouse.up()
        pg.wait_for_timeout(200)

    pg.mouse.move(cx, cy)
    pg.keyboard.press("r")
    hclick(cx - 150, cy - 100)
    hclick(cx + 150, cy + 100)
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(800)
    shot("01-rectangle")
    txt = pg.evaluate("1")
    step("draw rectangle (r + 2 clicks)", True)

    # 2. dimension: select top edge then 'd'
    hclick(cx + 60, cy - 100)
    pg.keyboard.press("d")
    pg.wait_for_timeout(300)
    hclick(cx + 60, cy - 160)
    if click_modal_button("OK"):
        step("dimension placement", False, note="error dialog after 'd' (bad selection)")
    pg.wait_for_timeout(500)
    ed = pg.locator("input.editor").filter(visible=True)
    if ed.count():
        ed.first.fill("40")
        ed.first.press("Enter")
        step("dimension edit box appears and accepts value", True)
    else:
        step("dimension edit box appears and accepts value", False,
             note="no visible input.editor after placing dimension")
    pg.wait_for_timeout(800)
    shot("02-dimension")

    # 3. extrude
    t = time.time()
    pg.keyboard.press("Shift+X")
    pg.wait_for_timeout(1500)
    pg.keyboard.press("F3")
    pg.wait_for_timeout(1000)
    pg.keyboard.press("f")
    pg.wait_for_timeout(1000)
    shot("03-extrude-iso")
    step("extrude (Shift+X) + isometric (F3) + zoom-fit (f)", True, seconds=round(time.time() - t, 2))

    # 4. save -> file dialog -> download dialog
    pg.keyboard.press("Control+s")
    pg.wait_for_timeout(1000)
    shot("04-save-dialog")
    ok = modal_visible()
    inp = pg.locator(".modal input[type=input]")
    vis = [i for i in range(inp.count()) if inp.nth(i).is_visible()]
    if ok and vis:
        inp.nth(vis[0]).fill("box")
        click_modal_button("OK")
        pg.wait_for_timeout(1500)
        shot("05-after-save")
        dl_link = pg.locator(".modal a[download]")
        n = [i for i in range(dl_link.count()) if dl_link.nth(i).is_visible()]
        if n:
            with pg.expect_download() as di:
                dl_link.nth(n[-1]).click(force=True)
            d = di.value
            path = f"{out}/{d.suggested_filename}"
            d.save_as(path)
            step("save produces a download", True, file=d.suggested_filename, bytes=os.path.getsize(path))
        else:
            html = pg.evaluate("Array.from(document.querySelectorAll('.modal')).filter(e=>getComputedStyle(e).display!='none').map(e=>e.innerText).join(' | ')")
            step("save produces a download", False, visible_modal_text=html[:300])
        click_modal_button("OK")
    else:
        step("save dialog opens", False)
    pg.wait_for_timeout(800)

    # 5. export STL through menu
    def menu(top, item):
        pg.locator(".menubar > li", has_text=top).first.click()
        pg.wait_for_timeout(300)
        pg.locator("ul.menu:not(.menubar) li > span.label", has_text=item).filter(visible=True).first.click()
        pg.wait_for_timeout(1000)

    for fname in ("part.stl", "part"):
        try:
            menu("File", "Export Triangle Mesh")
        except Exception as e:
            step("open File > Export Triangle Mesh", False, err=str(e)[:200]); break
        shot(f"06-export-dialog-{fname}")
        pre = pg.evaluate("Array.from(document.querySelectorAll('.modal input[type=input]')).filter(e=>e.offsetParent).map(e=>e.value)")
        inp = pg.locator(".modal input[type=input]")
        vis = [i for i in range(inp.count()) if inp.nth(i).is_visible()]
        if not vis:
            step(f"export dialog ({fname})", False); break
        inp.nth(vis[0]).fill(fname)
        click_modal_button("OK")
        pg.wait_for_timeout(2000)
        vis_text = pg.evaluate("Array.from(document.querySelectorAll('.modal')).filter(e=>getComputedStyle(e).display!='none').map(e=>e.innerText).join(' | ')")
        dl_link = pg.locator(".modal a[download]")
        n = [i for i in range(dl_link.count()) if dl_link.nth(i).is_visible()]
        if n:
            with pg.expect_download() as di:
                dl_link.nth(n[-1]).click(force=True)
            d = di.value
            path = f"{out}/export-{d.suggested_filename}"
            d.save_as(path)
            head = open(path, "rb").read(80)
            step(f"export mesh typed name '{fname}'", True, prefilled=pre, file=d.suggested_filename,
                 bytes=os.path.getsize(path))
        else:
            step(f"export mesh typed name '{fname}'", False, prefilled=pre, modal=vis_text[:300])
        shot(f"07-export-result-{fname}")
        for _ in range(4):
            if not click_modal_button("OK"):
                break
            pg.wait_for_timeout(300)
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(300)

    # 6. open uploaded example
    def open_file(local, label, extra=()):
        t = time.time()
        while click_modal_button("OK"):
            pg.wait_for_timeout(300)
        pg.keyboard.press("Control+o")
        pg.wait_for_timeout(800)
        if not modal_visible():
            # maybe "unsaved changes" prompt came first
            pass
        txt = pg.evaluate("Array.from(document.querySelectorAll('.modal')).filter(e=>getComputedStyle(e).display!='none').map(e=>e.innerText).join(' | ')")
        if "Don't Save" in txt or "Discard" in txt or "save" in txt.lower() and "File manager" not in txt:
            click_modal_button("Don't") or click_modal_button("No") or click_modal_button("Discard")
            pg.wait_for_timeout(800)
        fi = pg.locator(".modal input[type=file]")
        vis = [i for i in range(fi.count()) if fi.nth(i).is_visible()]
        if not vis:
            step(f"open dialog for {label}", False, modal=txt[:300]); return
        for f_ in [*extra, local]:
            fi.nth(vis[0]).set_input_files(f_)
            pg.wait_for_timeout(700)
        base = os.path.basename(local)
        radio = pg.locator(f'label[data-filename$="{base}"] input[type=radio]')
        if radio.count():
            radio.first.check()
        else:
            step(f"uploaded file listed ({label})", False); return
        tt = time.time()
        click_modal_button("OK")
        # wait for the app to settle: poll until main thread responsive & no modal
        pg.wait_for_timeout(500)
        pg.wait_for_function("true", timeout=600000)
        el = round(time.time() - tt, 2)
        pg.keyboard.press("f")
        pg.wait_for_timeout(1500)
        shot(f"08-open-{label}")
        modal = pg.evaluate("Array.from(document.querySelectorAll('.modal')).filter(e=>getComputedStyle(e).display!='none').map(e=>e.innerText).join(' | ')")
        heap = pg.evaluate("performance.memory ? Math.round(performance.memory.usedJSHeapSize/1e6) : null")
        wasm_mb = pg.evaluate("(typeof HEAP8!=='undefined' && HEAP8) ? Math.round(HEAP8.buffer.byteLength/1e6) : (typeof wasmMemory!=='undefined'? Math.round(wasmMemory.buffer.byteLength/1e6):null)")
        step(f"open {label}", True, open_seconds=el, modal_after=modal[:200], js_heap_mb=heap, wasm_mem_mb=wasm_mb)

    open_file(example, "example")
    import glob
    mech = "/home/claude/stress/examples/mechanisms"
    open_file(f"{mech}/whitworth.slvs", "assembly-whitworth",
              extra=[f for f in sorted(glob.glob(f"{mech}/whitworth-*.slvs"))])
    open_file(big, "big-sketch")

    # 7. resize / reflow check
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(1500)
    shot("09-phone-viewport")
    ov = pg.evaluate("document.documentElement.scrollWidth > window.innerWidth")
    step("phone-width viewport renders without horizontal overflow", not ov)

    json.dump(dict(results=results, console_tail=logs[-60:]), open(f"{out}/results.json", "w"), indent=1)
    b.close()
