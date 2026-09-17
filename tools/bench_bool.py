#!/usr/bin/env python3
"""Time N-stage boolean chains and look for kernel failures.
Usage: bench_bool.py DEBUGTOOL CLI "modes" "counts" [timeout_s]
Checks the STL for watertightness (every edge shared by exactly 2 triangles).
"""
import os, resource, struct, subprocess, sys, time
from collections import Counter

debug, cli = sys.argv[1], sys.argv[2]
modes, counts = sys.argv[3].split(), [int(c) for c in sys.argv[4].split()]
tmo = float(sys.argv[5]) if len(sys.argv) > 5 else 900
env = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8")


def check_stl(path):
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    edges = Counter()
    deg = 0
    for i in range(n):
        off = 84 + i * 50
        v = struct.unpack("<9f", d[off + 12:off + 48])
        p = [tuple(round(c, 5) for c in v[0:3]), tuple(round(c, 5) for c in v[3:6]),
             tuple(round(c, 5) for c in v[6:9])]
        if len({*p}) < 3:
            deg += 1
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edges[tuple(sorted((p[a], p[b])))] += 1
    naked = sum(1 for e, c in edges.items() if c != 2)
    return n, naked, deg


print(f"{'mode':8} {'stages':>6} {'rebuild_s':>10} {'stl_s':>7} {'rss_MB':>7} {'tris':>7} "
      f"{'naked':>6} {'degen':>6}  notes", flush=True)
for mode in modes:
    for n in counts:
        subprocess.run([sys.executable, "/home/claude/stress/gen_bool.py", str(n), mode,
                        "/tmp/bool.slvs"], check=True)
        notes, el = [], 0.0
        t = time.time()
        try:
            p = subprocess.run([debug, "solve", "/tmp/bool.slvs"], capture_output=True,
                               timeout=tmo, env=env)
            el = time.time() - t
            err = p.stderr.decode()
            if "FAILED" in err:
                notes.append("solve FAILED")
            for pat in ("Assertion", "assert", "oolean", "naked", "can't find a ray",
                        "WithMagnitude(1) of zero", "Too many"):
                c = err.count(pat)
                if c:
                    notes.append(f"'{pat}'x{c}")
            if p.returncode not in (0, 1):
                notes.append(f"rc={p.returncode}")
        except subprocess.TimeoutExpired:
            el = tmo; notes.append("TIMEOUT")
        tris = naked = deg = ""
        stl_s = 0.0
        if "TIMEOUT" not in notes:
            t = time.time()
            try:
                subprocess.run([cli, "export-mesh", "--output", "/tmp/bool.stl", "/tmp/bool.slvs"],
                               capture_output=True, timeout=tmo, env=env)
                stl_s = time.time() - t
                if os.path.exists("/tmp/bool.stl"):
                    tris, naked, deg = check_stl("/tmp/bool.stl")
                    os.remove("/tmp/bool.stl")
                else:
                    notes.append("NO STL")
            except subprocess.TimeoutExpired:
                stl_s = tmo; notes.append("STL TIMEOUT")
        rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
        print(f"{mode:8} {n:>6} {el:10.2f} {stl_s:7.2f} {rss:7.0f} {str(tris):>7} {str(naked):>6} "
              f"{str(deg):>6}  {'; '.join(notes)}", flush=True)
