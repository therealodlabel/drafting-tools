#!/usr/bin/env python3
"""Scale the number of extruded cylinders and time the NURBS boolean rebuild.
Usage: bench_solid.py DEBUGTOOL CLI "modes" "counts" [timeout_s]
"""
import os, re, resource, subprocess, sys, time

debug, cli = sys.argv[1], sys.argv[2]
modes, counts = sys.argv[3].split(), [int(c) for c in sys.argv[4].split()]
tmo = float(sys.argv[5]) if len(sys.argv) > 5 else 900
env = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8")
print(f"{'mode':8} {'solids':>6} {'rebuild_s':>10} {'stl_s':>7} {'rss_MB':>7} {'tris':>8}  notes", flush=True)
for mode in modes:
    for n in counts:
        subprocess.run([sys.executable, "/home/claude/stress/gen_solid.py", str(n), mode,
                        "/tmp/solid.slvs"], check=True)
        t = time.time()
        notes = []
        try:
            p = subprocess.run([debug, "solve", "/tmp/solid.slvs"], capture_output=True,
                               timeout=tmo, env=env)
            el = time.time() - t
            err = p.stderr.decode()
            if "FAILED" in err:
                notes.append("solve FAILED")
            for pat in ("Assertion", "boolean", "Boolean", "naked", "can't find a ray",
                        "WithMagnitude(1) of zero"):
                c = err.count(pat)
                if c:
                    notes.append(f"'{pat}' x{c}")
            if p.returncode not in (0, 1):
                notes.append(f"rc={p.returncode}")
        except subprocess.TimeoutExpired:
            el = tmo; notes.append(f"TIMEOUT>{tmo}s")
        tris, stl_s = "", 0.0
        if not notes or "TIMEOUT" not in notes[-1]:
            t = time.time()
            try:
                q = subprocess.run([cli, "export-mesh", "--output", "/tmp/solid.stl",
                                    "/tmp/solid.slvs"], capture_output=True, timeout=tmo, env=env)
                stl_s = time.time() - t
                if os.path.exists("/tmp/solid.stl"):
                    tris = str(int.from_bytes(open("/tmp/solid.stl", "rb").read(84)[80:84], "little"))
                    os.remove("/tmp/solid.stl")
                else:
                    notes.append("no STL written")
            except subprocess.TimeoutExpired:
                stl_s = tmo; notes.append("STL TIMEOUT")
        rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
        print(f"{mode:8} {n:>6} {el:10.2f} {stl_s:7.2f} {rss:7.0f} {tris:>8}  {'; '.join(notes)}",
              flush=True)
