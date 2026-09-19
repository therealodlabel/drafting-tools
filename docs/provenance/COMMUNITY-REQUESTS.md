# Community requests and answers

The upstream questions, reports and answers that motivated work in this fork.
Summarised in substance and linked to the originals — the posts belong to the
people who wrote them, so nothing here is reproduced at length. Follow the link
for the real thing.

Two sources: the issue tracker at `github.com/solvespace/solvespace/issues` and
the forum at `solvespace.com/forum.pl`. They have different populations. The
tracker is mostly people who can read the source; the forum is mostly people
whose model failed and who have no idea whether it is a bug. The forum is
therefore the better guide to what a first-time visitor will hit.

Read alongside [`CHANGE-LEDGER.md`](CHANGE-LEDGER.md), which cites these by
number.

---

## A. Directly answered by changes in this fork

### A.1 — The web version cannot save, open or export

**Where:** forum, ["Experimental SolveSpace Web Edition"](https://solvespace.com/forum.pl?action=viewthread&parent=2369) (33 replies, still active).

**Question asked, repeatedly:** drawing works, but nothing can be saved, opened,
imported or exported — is that expected?

**Answer given upstream:** yes. File I/O was never implemented in the
experimental web build. The developer who wrote it left the project in 2021 and
nobody is dedicated to it; the build is hosted and auto-updated from master but
not developed.

**What we did:** ledger rows 1.9, 1.11, 5.1–5.4. Files persist in IndexedDB,
downloads are named correctly, and unsaved work survives a closed tab with a
recovery offer.

### A.2 — Touchscreen and tablet support

**Where:** same thread, plus forum ["Android Port"](https://solvespace.com/forum.pl?action=viewthread&parent=3966).

**Request:** make it usable by finger. One poster proposed a specific gesture
set — pinch to zoom, two fingers to pan, three to rotate. Several asked for an
Android build instead of a web one.

**Answer given upstream:** no maintainer capacity.

**What we did:** ledger rows 6.5–6.8, 6.10. Three genuine touch bugs fixed (a
release reporting the wrong button, an inverted pinch past a clamp, a
divide-by-zero on `touchend`), plus tap-target and small-screen layout, with a
phone-sized test harness. The full three-finger gesture set is planned, not
done.

### A.3 — Black or white screen at startup

**Where:** forum, several: ["Blank black canvas on Windows 10"](https://solvespace.com/forum.pl?action=viewall), "White Screen on open", "message: Unable to create a GL context".

**Question:** the program starts and shows nothing. What now?

**Answer given upstream:** varies by thread — driver advice, mostly.

**What we did:** ledger row 1.8. The web build retries without requiring
hardware acceleration, falls back to software rendering, and only if that also
fails shows a panel saying so. A black canvas with no message is no longer a
possible outcome.

### A.4 — STL export fails, or crashes

**Where:** forum, several, including ["can't export STL"](https://solvespace.com/forum.pl?action=viewall), "exporting to stl crashes the program", "SolveSpace V3.1 crashes when exporting triangle mesh", "STL Export Failing with error: 'Active group mesh is empty'".

**Question:** export produces nothing, an error, or a crash.

**What we did:** ledger rows 1.9, 6.1–6.4. An extensionless name no longer
writes a 0-byte file, the export dialog no longer suggests a format it cannot
write, the mesh function no longer leaks its file handle or reports success for
an unrecognised extension, and there is a one-click STL path that removes the
format decision entirely.

### A.5 — "Not closed contour, or not all same style"

**Where:** forum, at least six separate threads under near-identical titles.

**Question:** the sketch looks closed. Which edge is open?

**Answer given upstream:** zoom in and look for the gap.

**What we did:** nothing yet. It is planned as item 6.4 in the roadmap. It is
recorded here because it is the single most-repeated error message on the
forum, and the information needed to answer it is already inside the program.

### A.6 — Red geometry with no explanation

**Where:** forum, a dozen-plus threads: "What do the red lines mean", "Mystery
red lines, circles", "understanding an error in red", "problems with naked
edges", "Incomprehensible open edges", among others.

**Question:** parts of the model turned red. Why?

**What we did, partially:** ledger row 6.3. At export time, a non-watertight
mesh is now reported before the file is written and in terms of what it means
for a print, rather than afterwards in the language of the mesh. Explaining red
geometry *in general*, by clicking it, is planned and not done.

### A.7 — Licence obligations for a modified version

**Where:** forum, ["License infringement?"](https://solvespace.com/forum.pl?action=viewthread&parent=2660) (14 replies).

**Question:** a commercial product appears to be a SolveSpace derivative,
shipping no source. Is that allowed?

**Answer given upstream:** Jonathan Westhues (the author) — models made with
SolveSpace are the user's, commercially or not; the GPL applies to the
software, and distributing a derived binary means publishing the derived code
under the same licence. Selling compiled tools or support is fine. Ruevs (a
maintainer) — shipping the *original* upstream source does not discharge the
obligation; it must be the complete source of the derivative.

Notably, nobody in the thread objected to the existence of a fork. The
objection was to hidden source and unacknowledged origin.

**What we did:** ledger row 1.1, and [`LICENSE-COMPLIANCE.md`](LICENSE-COMPLIANCE.md).

---

## B. Open upstream reports this fork touches

| Where | Subject | Relationship |
|---|---|---|
| [GH #1768](https://github.com/solvespace/solvespace/pull/1768) | Crash in the headless CLI when a linked file is missing | Open upstream PR. The same crash was found here by fuzzing and fixed independently (ledger 1.7) |
| [GH #1688](https://github.com/solvespace/solvespace/pull/1688) | Make `GenerateAll` non-recursive, optimise pruning | Open upstream PR. Same failure mode; upstream proposes a rewrite, we bounded the recursion instead (ledger 1.5). Read and deliberately not followed |
| [GH #1020](https://github.com/solvespace/solvespace/issues/1020) | Asks for an automated performance benchmark | We built one for our own purposes (`tools/bench_*.py`) and it is offerable against this issue |
| [GH #320](https://github.com/solvespace/solvespace/issues/320) | Unbounded recursion in `bsp.cpp`, patch available | Same class as ledger 1.5, likely one of the crash sites still open here |
| [GH #297](https://github.com/solvespace/solvespace/issues/297) | Suggest lowering chord tolerance when Booleans fail | Planned, not done |

## C. Most-wanted upstream features, for the record

Not implemented here, but recorded because they shape the roadmap and because
"who asked for this" is a question the ledger should be able to answer for
future work too.

| Where | Subject | Signal |
|---|---|---|
| [GH #77](https://github.com/solvespace/solvespace/issues/77) + [forum thread](https://solvespace.com/forum.pl?action=viewthread&parent=211) | Named parameters and expressions in dimensions | 36 👍 and 89 comments on the issue; **64 replies** on the forum. The largest single feature discussion in the project |
| [GH #423](https://github.com/solvespace/solvespace/issues/423) | Start a sketch on a selected face | 27 comments; upstream has disabled code for half of it |
| [GH #149](https://github.com/solvespace/solvespace/issues/149), [GH #577](https://github.com/solvespace/solvespace/issues/577) + 11 forum threads | Chamfers and fillets as first-class tools | Asked for continuously since 2022; several people export to FreeCAD solely to fillet |
| [GH #439](https://github.com/solvespace/solvespace/issues/439) | Sweep along a path, and loft | Real kernel work |
| [GH #72](https://github.com/solvespace/solvespace/issues/72) | Mirror groups | 15-reply forum thread as well |
| Forum, six threads | View control without a middle mouse button | Mac trackpads and laptops. Directly relevant to a tool meant to be used on a borrowed machine |

---

## How this file is maintained

A thread earns a place here when it motivates work — done, planned or
deliberately declined. Entries are not removed when the work lands; the ledger
row is added and the entry stays, so the record of *why* survives. Links are to
the original posts so that the people who wrote them keep the credit.
