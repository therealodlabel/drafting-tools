#!/usr/bin/env python3
"""Mutation fuzzer for .slvs loading + regeneration.

Usage: fuzz_slvs.py TOOL SEED_DIR OUT_DIR ITERATIONS [TIMEOUT_S]
TOOL is a solvespace-debugtool binary (ideally ASan/UBSan build); each mutant is run
as `TOOL solve mutant.slvs`. Exit codes 0/1 are normal (solved / failed to solve).
Anything else (signal, sanitizer report, timeout) is saved to OUT_DIR as a finding.
"""
import hashlib, os, random, re, subprocess, sys, time

EXTREMES = ["nan", "inf", "-inf", "1e308", "-1e308", "1e-320", "0", "-0", "4294967295",
            "99999999999999999999999", "-1", "ffffffff", "80000000", "7fffffff", ""]


def mutate(lines, rnd):
    lines = list(lines)
    for _ in range(rnd.randint(1, 6)):
        if not lines:
            break
        op = rnd.randrange(9)
        i = rnd.randrange(len(lines))
        if op == 0:  # replace a value with an extreme
            if b"=" in lines[i]:
                k, _, _ = lines[i].partition(b"=")
                lines[i] = k + b"=" + rnd.choice(EXTREMES).encode()
        elif op == 1:  # delete a line
            del lines[i]
        elif op == 2:  # duplicate a line
            lines.insert(i, lines[i])
        elif op == 3:  # swap two lines
            j = rnd.randrange(len(lines))
            lines[i], lines[j] = lines[j], lines[i]
        elif op == 4:  # bit flip
            if lines[i]:
                b = bytearray(lines[i]); p = rnd.randrange(len(b)); b[p] ^= 1 << rnd.randrange(8)
                lines[i] = bytes(b)
        elif op == 5:  # retarget a handle to another handle found in the file
            m = re.match(rb"(.*\.v=)([0-9a-fA-F]{8})$", lines[i])
            if m:
                pool = [l.split(b"=")[-1] for l in lines if re.match(rb".*\.v=[0-9a-fA-F]{8}$", l)]
                lines[i] = m.group(1) + rnd.choice(pool)
        elif op == 6:  # change a type code to another plausible one
            if b".type=" in lines[i]:
                k, _, _ = lines[i].partition(b"=")
                lines[i] = k + b"=" + str(rnd.choice([0, 1, 100, 101, 200, 300, 400, 500, 600, 700,
                                                     900, 1000, 2000, 2001, 3000, 5000, 5001,
                                                     5100, 5101, 5102, 5103, 5200, 5201, 5300,
                                                     10000, 11000, 12000, 13000, 14000, 20, 30,
                                                     122, 123, 125, 200, 210, 99999, -5])).encode()
        elif op == 7:  # truncate file
            lines = lines[:i]
        elif op == 8:  # numeric nudge
            m = re.match(rb"(.*=)(-?[0-9.]+)$", lines[i])
            if m:
                try:
                    v = float(m.group(2)) * rnd.choice([-1, 0, 1e-9, 1e9, 1.0000001])
                    lines[i] = m.group(1) + repr(v).encode()
                except ValueError:
                    pass
    return lines


def main():
    tool, seed_dir, out_dir, iters = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    timeout = float(sys.argv[5]) if len(sys.argv) > 5 else 20
    os.makedirs(out_dir, exist_ok=True)
    seeds = []
    for root, _, files in os.walk(seed_dir):
        for fn in files:
            if fn.endswith(".slvs"):
                p = os.path.join(root, fn)
                if os.path.getsize(p) < 400_000:
                    seeds.append(p)
    rnd = random.Random(int(os.environ.get("FUZZ_SEED", "1")))
    work = os.path.join(out_dir, "_work.slvs")
    seen = set()
    stats = {"runs": 0, "ok": 0, "fail_solve": 0, "crash": 0, "timeout": 0}
    t0 = time.time()
    env = dict(os.environ, ASAN_OPTIONS="detect_leaks=0:abort_on_error=0",
               UBSAN_OPTIONS="print_stacktrace=1", LANG="C.UTF-8", LC_ALL="C.UTF-8")
    for it in range(iters):
        seed = rnd.choice(seeds)
        data = open(seed, "rb").read().split(b"\n")
        mut = mutate(data, rnd)
        blob = b"\n".join(mut)
        open(work, "wb").write(blob)
        stats["runs"] += 1
        try:
            p = subprocess.run([tool, "solve", work], capture_output=True, timeout=timeout, env=env)
            err = p.stderr.decode("latin-1")
            rc = p.returncode
            san = ("ERROR: AddressSanitizer" in err or "runtime error:" in err
                   or "ERROR: LeakSanitizer" in err)
            if rc in (0, 1) and not san:
                stats["ok" if rc == 0 else "fail_solve"] += 1
                continue
            kind = "crash"
            m = re.search(r"(AddressSanitizer: [\w-]+|runtime error: [^\n]{0,80}|"
                          r"Assertion failed[^\n]{0,120}|File [^\n]{0,160})", err)
            sig = m.group(1) if m else f"rc={rc}"
            # first frame in solvespace sources makes a better bucket
            fr = re.search(r"#\d+ 0x[0-9a-f]+ in (\S+) (/home/claude/ss/solvespace/\S+)", err)
            bucket = sig + (" @ " + fr.group(1) + " " + fr.group(2).split("/solvespace/")[-1] if fr else "")
        except subprocess.TimeoutExpired:
            kind, bucket, err, rc = "timeout", "timeout", "", None
        stats[kind] += 1
        key = hashlib.md5(bucket.encode()).hexdigest()[:10]
        if key not in seen:
            seen.add(key)
            base = os.path.join(out_dir, f"{kind}-{key}")
            open(base + ".slvs", "wb").write(blob)
            open(base + ".txt", "w").write(f"seed={seed}\nrc={rc}\nbucket={bucket}\n\n{err[-6000:]}")
            print(f"[{it}] NEW {kind}: {bucket}  (seed {os.path.basename(seed)})", flush=True)
    stats["seconds"] = round(time.time() - t0)
    stats["unique_findings"] = len(seen)
    print(stats)


if __name__ == "__main__":
    main()
