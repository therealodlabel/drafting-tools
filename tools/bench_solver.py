#!/usr/bin/env python3
"""Time SolveSpace loading+solving generated sketches of increasing size.
Usage: bench_solver.py TOOL "modes" "sizes" [timeout_s]
"""
import re, resource, subprocess, sys, time, os

tool = sys.argv[1]
modes = sys.argv[2].split()
sizes = [int(x) for x in sys.argv[3].split()]
tmo = float(sys.argv[4]) if len(sys.argv) > 4 else 600
env = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8")
print(f"{'mode':6} {'N':>6} {'gen_s':>7} {'solve_s':>9} {'rss_MB':>7}  result")
for m in modes:
    for n in sizes:
        t = time.time()
        subprocess.run([sys.executable, "/home/claude/stress/gen_chain.py", str(n), m, "/tmp/c.slvs"],
                       check=True)
        gen = time.time() - t
        before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        t = time.time()
        try:
            p = subprocess.run([tool, "solve", "/tmp/c.slvs"], capture_output=True,
                               timeout=tmo, env=env)
            out = p.stderr.decode()
            el = time.time() - t
            mm = re.search(r"sketch-in-plane\s+(\S+)\s+dof=(-?\d+)(\s+FAILED)?", out)
            res = f"{mm.group(1)} dof={mm.group(2)}{' FAILED' if mm.group(3) else ''}" if mm else out.strip()[-90:]
            bad = len(re.findall(r"bad constraint", out))
            if bad:
                res += f" ({bad} constraints blamed)"
        except subprocess.TimeoutExpired:
            el, res = tmo, f"TIMEOUT >{tmo}s"
        rss = (resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss) / 1024
        print(f"{m:6} {n:>6} {gen:7.2f} {el:9.2f} {rss:7.0f}  {res}", flush=True)
