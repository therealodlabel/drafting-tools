# GPLv3 compliance

SolveSpace is licensed under the GNU General Public License, version 3 or later
(`COPYING.txt` at the repository root). drafting.tools is a modified version of
it and is distributed under the same licence.

This file lists what the licence asks of a modified version and where each
obligation is met, so that the claim can be checked rather than taken on trust.
It is a factual index, not legal advice.

## Obligations and where they are met

| Obligation | Section | Where it is met |
|---|---|---|
| Keep intact all notices stating that the GPL applies, and all copyright notices | §4, §5(a) | Unchanged. No copyright header in the upstream sources was edited. `COPYING.txt` and `THIRD_PARTIES.txt` are untouched |
| Carry prominent notices stating that the work is modified, and the date | §5(a) | `NOTICE-drafting-tools.md`; the banner at the top of `README.md`; the About dialog in the running program, which states it is a modified build, not the official release, and gives the year. [`CHANGE-LEDGER.md`](CHANGE-LEDGER.md) is the detailed form |
| License the whole modified work under GPLv3 | §5(c) | `NOTICE-drafting-tools.md`. Every change in the ledger is published in the same public repository under the same licence |
| Provide the corresponding source for any object code conveyed | §6 | Serving the WebAssembly build to a browser conveys object code. The source offer is `https://drafting.tools/source`, stated in `NOTICE-drafting-tools.md`, in the README banner, and in the About dialog |
| Do not impose further restrictions | §10 | None imposed. No additional terms, no CLA, no field-of-use restriction |
| Warranty disclaimer and limitation of liability | §15, §16 | Unmodified, as in `COPYING.txt` |

## Bundled third-party components

The WebAssembly build statically links several libraries, each under its own
licence, reproduced in the corresponding `extlib/` subdirectory and tabulated in
`NOTICE-drafting-tools.md`: cairo (LGPL-2.1 or MPL-1.1), pixman (MIT), libpng
(PNG Reference Library License v2), zlib (zlib), FreeType (FTL or GPLv2),
libdxfrw (GPLv2+), Eigen (MPL-2.0), mimalloc (MIT). The bundled Bitstream Vera
font is covered by `THIRD_PARTIES.txt`.

The Eigen submodule URL was changed to a mirror (ledger row 1.2) because
`gitlab.com` is unreachable from the build environments used here. It pins the
same commit; no Eigen code differs.

## Things that have to be true before the site is public

1. **`https://drafting.tools/source` must resolve.** It is the written source
   offer under §6. Pointing it at the public fork is sufficient. A dead link
   there is the one compliance failure this project could plausibly commit, and
   it is the failure the forum's licence thread was actually about.

2. **The served build and the published source must match.** Whatever
   commit is deployed should be identifiable from the site — the About dialog
   already carries a version string, and the deploy step should publish the
   commit it built from.

3. **No third-party hosts.** Verified as a CI check ("no external origin"), for
   privacy reasons rather than licensing ones, but it also keeps the set of
   conveyed components equal to the set documented above.

## On the boundary between the two projects

Most of this repository is upstream SolveSpace, under its authors' copyright.
The modifications are enumerated in [`CHANGE-LEDGER.md`](CHANGE-LEDGER.md) —
roughly forty behavioural changes across six commits — and their authorship is
described in [`AUTHORSHIP.md`](AUTHORSHIP.md). Nothing in this fork is copied
from an upstream pull request; where upstream has an open patch for the same
problem, the ledger row names it and states the relationship.

The forum thread on licence infringement makes the community's position clear:
forks are unobjectionable, hidden source and unacknowledged origin are not.
This fork is public, says what it changed, says who it came from, and keeps the
original notices.
