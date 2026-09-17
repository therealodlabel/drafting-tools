#!/usr/bin/env python3
"""Generate models with N successive boolean operations between overlapping solids.

Usage: gen_bool.py N MODE OUT.slvs
Each stage i is: a sketch group on XY holding one circle, plus an extrude group that
UNIONs (even i) or DIFFERENCEs (odd i) a cylinder into the running shell.
  chain   : stages march along X by 0.6*r, so every stage overlaps the previous one
  tangent : stages are exactly 2r apart -> tangent surfaces (the hard case)
  coaxial : every stage shares the axis, alternating radius -> coincident/coaxial faces
"""
import sys

HEADER_SRC = os.environ.get("SOLVESPACE_SRC", ".") + "/test/request/circle/normal.slvs"


def f(v):
    return f"{v:.20f}"


def main():
    n, mode, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    txt = open(HEADER_SRC, "rb").read().decode("latin-1")
    head = txt[:txt.index("Group.h.v=00000002")]   # keep only the reference group
    r = 5.0
    groups, params, reqs = [], [], []
    order = 1
    for i in range(n):
        gs, ge = 2 + 2 * i, 3 + 2 * i          # sketch group, extrude group
        req = 4 + i
        if mode == "chain":
            x, rad, h = i * 0.6 * r, r, 10.0
        elif mode == "tangent":
            x, rad, h = i * 2 * r, r, 10.0
        else:  # coaxial
            x, rad, h = 0.0, r * (1.0 if i % 2 == 0 else 0.6), 10.0 + i
        groups.append(
            f"Group.h.v={gs:08x}\nGroup.type=5001\nGroup.order={order}\nGroup.name=sketch{i}\n"
            f"Group.activeWorkplane.v=80{gs:02x}0000\nGroup.color=ff000000\nGroup.subtype=6000\n"
            "Group.skipFirst=0\nGroup.predef.q.w=1.00000000000000000000\n"
            "Group.predef.origin.v=00010001\nGroup.predef.swapUV=0\nGroup.predef.negateU=0\n"
            "Group.predef.negateV=0\nGroup.visible=1\nGroup.suppress=0\n"
            "Group.relaxConstraints=0\nGroup.allowRedundant=0\nGroup.allDimsReference=0\n"
            "Group.scale=1.00000000000000000000\nGroup.remap={\n}\nAddGroup\n\n")
        order += 1
        combine = 0 if i % 2 == 0 else 1       # 0 = union, 1 = difference
        groups.append(
            f"Group.h.v={ge:08x}\nGroup.type=5100\nGroup.order={order}\nGroup.name=extrude{i}\n"
            f"Group.opA.v={gs:08x}\nGroup.color=00646464\nGroup.subtype=7000\n"
            f"Group.meshCombine={combine}\nGroup.skipFirst=0\n"
            f"Group.predef.entityB.v=80{gs:02x}0000\nGroup.predef.swapUV=0\n"
            "Group.predef.negateU=0\nGroup.predef.negateV=0\nGroup.visible=1\nGroup.suppress=0\n"
            "Group.relaxConstraints=0\nGroup.allowRedundant=0\nGroup.allDimsReference=0\n"
            "Group.scale=1.00000000000000000000\nGroup.remap={\n}\nAddGroup\n\n")
        order += 1
        params += [f"Param.h.v.={(req << 16) | 0x10:08x}\nParam.val={f(x)}\nAddParam\n\n",
                   f"Param.h.v.={(req << 16) | 0x11:08x}\nParam.val={f(0.0)}\nAddParam\n\n",
                   f"Param.h.v.={(req << 16) | 0x40:08x}\nParam.val={f(rad)}\nAddParam\n\n"]
        params += [f"Param.h.v.=80{ge:02x}{k:04x}\nParam.val={f(v)}\nAddParam\n\n"
                   for k, v in ((0, 0.0), (1, 0.0), (2, h))]
        reqs.append(f"Request.h.v={req:08x}\nRequest.type=400\nRequest.workplane.v=80{gs:02x}0000\n"
                    f"Request.group.v={gs:08x}\nRequest.construction=0\nAddRequest\n\n")
    refreqs = "".join(f"Request.h.v={i:08x}\nRequest.type=100\nRequest.group.v=00000001\n"
                      "Request.construction=0\nAddRequest\n\n" for i in (1, 2, 3))
    # request handles for the circles start at 4, so shift them past the reference requests
    with open(out, "wb") as fh:
        fh.write((head + "".join(groups) + "".join(params) + refreqs
                  + "".join(reqs)).encode("latin-1"))


if __name__ == "__main__":
    main()
