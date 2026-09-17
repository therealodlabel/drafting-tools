#!/usr/bin/env python3
"""Generate large, fully-constrained 2D sketches to stress the SolveSpace solver.

Usage: gen_chain.py N MODE OUT.slvs [JITTER]
  easy : staircase of N unit segments; each has H or V + a distance.
         (H/V equations are removed by substitution, so Newton sees ~N equations)
  hard : same staircase, but only segment 0 is horizontal + length 1; every later
         segment is PERPENDICULAR and EQUAL-LENGTH to the previous one
         (~2N equations go through Newton).
  over : 'hard' plus one extra conflicting distance (tests failure reporting).
All models are 0 DOF when consistent. JITTER perturbs the initial guess (default 0.15).
"""
import os
import random, sys

HEADER_SRC = os.environ.get("SOLVESPACE_SRC", ".") + "/test/request/line_segment/normal.slvs"
WP = "80020000"
G = "00000002"


def f(v):
    return f"{v:.20f}"


def main():
    n = int(sys.argv[1]); mode = sys.argv[2]; out = sys.argv[3]
    jit = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
    rnd = random.Random(1234)

    txt = open(HEADER_SRC, "rb").read().decode("latin-1")
    head = txt[:txt.index("Param.h.v.=00040010")]
    refreqs = "".join(
        f"Request.h.v={r:08x}\nRequest.type=100\nRequest.group.v=00000001\n"
        "Request.construction=0\nAddRequest\n\n" for r in (1, 2, 3))

    pts = [(0.0, 0.0)]
    for i in range(n):
        x, y = pts[-1]
        pts.append((x + 1, y) if i % 2 == 0 else (x, y + 1))

    params, reqs, cons = [], [], []
    ch = [1]

    def con(ctype, **kw):
        body = f"Constraint.h.v={ch[0]:08x}\nConstraint.type={ctype}\n" \
               f"Constraint.group.v={G}\nConstraint.workplane.v={WP}\n"
        for k, v in kw.items():
            body += f"Constraint.{k}={v}\n"
        body += "Constraint.other=0\nConstraint.other2=0\nConstraint.reference=0\nAddConstraint\n\n"
        cons.append(body)
        ch[0] += 1

    for i in range(n):
        r = 4 + i
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        j = lambda: rnd.uniform(-jit, jit)
        for pid, val in ((0x10, x0 + j()), (0x11, y0 + j()), (0x13, x1 + j()), (0x14, y1 + j())):
            params.append(f"Param.h.v.={(r << 16) | pid:08x}\nParam.val={f(val)}\nAddParam\n\n")
        reqs.append(f"Request.h.v={r:08x}\nRequest.type=200\nRequest.workplane.v={WP}\n"
                    f"Request.group.v={G}\nRequest.construction=0\nAddRequest\n\n")
        a, b, line = f"{(r << 16) | 1:08x}", f"{(r << 16) | 2:08x}", f"{r << 16:08x}"
        prev_end = "00010001" if i == 0 else f"{((r - 1) << 16) | 2:08x}"
        con(20, **{"ptA.v": prev_end, "ptB.v": a})
        if mode == "easy" or i == 0:
            con(80 if i % 2 == 0 else 81, **{"entityA.v": line})
            con(30, **{"valA": f(1.0), "ptA.v": a, "ptB.v": b})
        else:
            prev = f"{(r - 1) << 16:08x}"
            con(122, **{"entityA.v": prev, "entityB.v": line})
            con(50, **{"entityA.v": prev, "entityB.v": line})
    if mode == "over":
        last = f"{((4 + n - 1) << 16) | 2:08x}"
        con(30, **{"valA": f(1.0), "ptA.v": "00010001", "ptB.v": last})

    with open(out, "wb") as fh:
        fh.write((head + "".join(params) + refreqs + "".join(reqs) + "".join(cons)).encode("latin-1"))


if __name__ == "__main__":
    main()
