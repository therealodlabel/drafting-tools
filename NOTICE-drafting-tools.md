# drafting.tools — modified version notice

This repository is a **modified version of SolveSpace**, the parametric 2D/3D CAD program
by Jonathan Westhues and other authors. It is not an official SolveSpace release, and the
SolveSpace project is not responsible for it.

- Upstream project: https://solvespace.com/ — https://github.com/solvespace/solvespace
- This modified version: https://drafting.tools/
- Complete source for whatever build is served at drafting.tools: https://drafting.tools/source

## Licence

SolveSpace is licensed under the GNU General Public License, version 3 or later
(`COPYING.txt`). This modified version is distributed under the same licence. There is no
warranty, to the extent permitted by law.

Serving the WebAssembly build to a browser conveys object code under GPLv3 §6, so the
corresponding source for the exact build being served is offered from the link above, at no
charge, for as long as that build is served.

## Bundled third-party code

`THIRD_PARTIES.txt` covers the bundled Bitstream Vera font. The WebAssembly build also
statically links these, each under its own licence, reproduced in the corresponding
`extlib/` subdirectory:

| Component | Licence |
|---|---|
| cairo | LGPL-2.1 or MPL-1.1 |
| pixman | MIT |
| libpng | PNG Reference Library License |
| zlib | zlib License |
| FreeType | FTL or GPLv2 |
| mimalloc | MIT |
| Eigen | MPL-2.0 |
| libdxfrw (SolveSpace fork) | GPLv2 or later |

## Changes made in this fork

Changed in 2026 by the drafting.tools maintainer. What follows is a summary.

The full record — every change with its reason, who requested it, where it was requested,
who wrote it and how it was verified — is in [`docs/provenance/`](docs/provenance/):

- [`CHANGE-LEDGER.md`](docs/provenance/CHANGE-LEDGER.md) — the per-change record
- [`AUTHORSHIP.md`](docs/provenance/AUTHORSHIP.md) — how this fork was written, including
  the use of an AI assistant
- [`COMMUNITY-REQUESTS.md`](docs/provenance/COMMUNITY-REQUESTS.md) — the upstream reports
  and answers that motivated the work
- [`LICENSE-COMPLIANCE.md`](docs/provenance/LICENSE-COMPLIANCE.md) — GPLv3 obligations and
  where each is met

**Build and packaging**

- Eigen is fetched from the `eigen-mirror/eigen` GitHub mirror instead of gitlab.com, which
  is blocked on many corporate and sandboxed networks. Same commits, same content.
- The Emscripten toolchain version is pinned instead of tracking "latest".
- The web build defaults to single-threaded, so it runs on ordinary static hosting without
  `Cross-Origin-Opener-Policy` / `Cross-Origin-Embedder-Policy` headers.
- Added a CI workflow that runs the upstream test suite, a sanitizer build, loader fuzzing,
  and the deployable web build.
- Added `tools/`: model generators, solver and boolean benchmarks, an export matrix test, a
  `.slvs` loader fuzzer with its corpus, and browser test drivers.

**Robustness**

- `GenerateAll()` recursion is bounded and reported instead of overflowing the stack on a
  damaged file (in the browser that killed the whole session).
- Fixed a null dereference in `Group::GenerateShellAndMesh()` when the group chain is broken.
- Fixed a null dereference in `LocateImportedFile()` in builds without dialogs (CLI, tests),
  which crashed whenever a linked part file was missing.

**Web front end**

- Removed the Font Awesome CDN stylesheet; menu indicators are inline SVG, so the page makes
  no third-party requests.
- WebGL falls back to a software context and, failing that, explains itself instead of
  leaving a black canvas.
- The browser tab shows the model name and a marker for unsaved changes.
- Saved and exported files get the right extension, and downloads are named after the file
  rather than its pseudo-filesystem path.
- Rebranded as drafting.tools, with an About dialog that states this is a modified version
  and where its source lives.
