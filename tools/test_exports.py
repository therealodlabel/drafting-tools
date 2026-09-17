#!/usr/bin/env python3
"""Exercise every CLI export format on a set of models; report size, time and errors.
Usage: test_exports.py CLI OUTDIR file.slvs...
"""
import os, subprocess, sys, time

cli, outdir = sys.argv[1], sys.argv[2]
files = sys.argv[3:]
os.makedirs(outdir, exist_ok=True)
env = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8")
CASES = [("export-view", e) for e in ("pdf", "eps", "ps", "svg", "dxf", "plt", "hpgl", "step", "txt")] + \
        [("export-wireframe", e) for e in ("step", "dxf")] + \
        [("export-mesh", e) for e in ("stl", "obj", "js", "html", "wrl")] + \
        [("export-surfaces", "step"), ("thumbnail", "png")]
print(f"{'model':22} {'command':17} {'ext':5} {'sec':>6} {'bytes':>9}  status", flush=True)
for f in files:
    base = os.path.splitext(os.path.basename(f))[0]
    for cmd, ext in CASES:
        out = os.path.join(outdir, f"{base}.{cmd}.{ext}")
        args = [cli, cmd, "--output", out]
        if cmd == "thumbnail":
            args += ["--size", "500x500", "--view", "isometric", "--chord-tol", "1"]
        elif cmd == "export-view":
            args += ["--view", "isometric", "--chord-tol", "1"]
        elif cmd != "export-surfaces":
            args += ["--chord-tol", "1"]
        t = time.time()
        try:
            p = subprocess.run(args + [f], capture_output=True, timeout=300, env=env)
            el = time.time() - t
            err = "\n".join(l for l in p.stderr.decode().splitlines()
                            if "Missing (absent) translation" not in l)
            size = os.path.getsize(out) if os.path.exists(out) else -1
            status = "ok"
            if size <= 0:
                status = "NO OUTPUT"
            if "Error" in err or "error" in err:
                status = "error: " + err.replace("\n", " ")[:90]
            if p.returncode != 0:
                status += f" rc={p.returncode}"
            if size > 0 and "Written" not in err:
                status += " (no 'Written' message)"
        except subprocess.TimeoutExpired:
            el, size, status = 300, -1, "TIMEOUT"
        print(f"{base[:22]:22} {cmd:17} {ext:5} {el:6.2f} {size:9d}  {status}", flush=True)
