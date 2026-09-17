#!/usr/bin/env python3
"""Generate 3D models that stress the NURBS boolean kernel.

Usage: gen_solid.py M MODE OUT.slvs
  M       number of circles in the sketch (=> M cylinders after the extrude)
  grid    circles laid out on a grid, well separated  (unions of disjoint solids)
  touch   circles spaced exactly 2r apart             (tangent solids: hard booleans)
  overlap circles spaced 1.5r apart                   (overlapping solids)
The model is: reference group -> sketch on XY with M circles -> one-sided extrude (union).
"""
import math, sys

HEADER_SRC = os.environ.get("SOLVESPACE_SRC", ".") + "/test/request/circle/normal.slvs"
WP, G = "80020000", "00000002"


def f(v):
    return f"{v:.20f}"


def main():
    m, mode, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    txt = open(HEADER_SRC, "rb").read().decode("latin-1")
    head = txt[:txt.index("Param.h.v.=00040010")]
    r = 5.0
    pitch = {"grid": 4 * r, "touch": 2 * r, "overlap": 1.5 * r}[mode]
    cols = max(1, int(math.ceil(math.sqrt(m))))

    params, reqs = [], []
    for i in range(m):
        h = 4 + i
        x, y = (i % cols) * pitch, (i // cols) * pitch
        params += [f"Param.h.v.={(h << 16) | 0x10:08x}\nParam.val={f(x)}\nAddParam\n\n",
                   f"Param.h.v.={(h << 16) | 0x11:08x}\nParam.val={f(y)}\nAddParam\n\n",
                   f"Param.h.v.={(h << 16) | 0x40:08x}\nParam.val={f(r)}\nAddParam\n\n"]
        reqs.append(f"Request.h.v={h:08x}\nRequest.type=400\nRequest.workplane.v={WP}\n"
                    f"Request.group.v={G}\nRequest.construction=0\nAddRequest\n\n")
    refreqs = "".join(f"Request.h.v={i:08x}\nRequest.type=100\nRequest.group.v=00000001\n"
                      "Request.construction=0\nAddRequest\n\n" for i in (1, 2, 3))
    # extrude group 3, vector (0,0,10)
    gparams = "".join(f"Param.h.v.=8003{i:04x}\nParam.val={f(v)}\nAddParam\n\n"
                      for i, v in ((0, 0.0), (1, 0.0), (2, 10.0)))
    extrude = ("Group.h.v=00000003\nGroup.type=5100\nGroup.order=2\nGroup.name=extrude\n"
               "Group.opA.v=00000002\nGroup.color=00646464\nGroup.subtype=7000\n"
               "Group.skipFirst=0\nGroup.predef.entityB.v=80020000\nGroup.predef.swapUV=0\n"
               "Group.predef.negateU=0\nGroup.predef.negateV=0\nGroup.visible=1\n"
               "Group.suppress=0\nGroup.relaxConstraints=0\nGroup.allowRedundant=0\n"
               "Group.allDimsReference=0\nGroup.scale=1.00000000000000000000\n"
               "Group.remap={\n}\nAddGroup\n\n")
    with open(out, "wb") as fh:
        fh.write((head + extrude + "".join(params) + gparams + refreqs + "".join(reqs)).encode("latin-1"))


if __name__ == "__main__":
    main()
