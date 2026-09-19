# Change ledger

Every behavioural change in drafting.tools relative to upstream SolveSpace,
oldest first. Base commit: `cbff7a91` on `solvespace/solvespace` master.

**Abbreviations used in the "Requested by" column**

| Value | Meaning |
|---|---|
| **Owner** | Shavarsh (`therealodlabel`), the project owner, as a requirement of this fork |
| **GH #n** | An open issue or pull request on `github.com/solvespace/solvespace` |
| **Forum** | A thread on `solvespace.com/forum.pl` — see [`COMMUNITY-REQUESTS.md`](COMMUNITY-REQUESTS.md) |
| **Found here** | Nobody reported it. It was found by testing, fuzzing or stress work done for this fork |
| **GPLv3** | Required by the licence, not by a person |

**"Written by"** is *Claude (Anthropic)* for every row below, working under the
project owner's direction and review. Where an upstream patch, branch or report
described the same problem, the row names it; where the upstream approach was
read and deliberately not followed, the row says that too. See
[`AUTHORSHIP.md`](AUTHORSHIP.md).

---

## Commit `4d942804` — Fork setup, hardening pass 1, web front-end fixes (2026-09-17)

| # | Change | Why | Requested by | Notes on origin | Verified by |
|---|---|---|---|---|---|
| 1.1 | `NOTICE-drafting-tools.md`, README banner, rewritten About dialog | A modified version has to say that it is modified, when, and where its source is | **GPLv3 §5**, **Owner** | Wording is ours. The obligation is the licence's; the forum's licence thread confirms the community reads it the same way | Read by the owner; About dialog checked in the running build |
| 1.2 | Eigen submodule switched to `eigen-mirror/eigen` | `gitlab.com` is unreachable from both build environments used here | **Found here** | Same commit hash as upstream's submodule pin; a mirror change only | Submodule checks out; builds succeed |
| 1.3 | Single-threaded WebAssembly build is the default | A threaded build needs COOP/COEP headers, which a plain static host cannot always set. The site must run from a folder of files | **Owner** (hosting constraint) | Ours | Web build boots and runs without cross-origin isolation |
| 1.4 | Font Awesome CDN removed; check marks, radio dots and submenu arrows drawn as inline SVG | The page must contact no third party. A webfont CDN is a request to someone else's server on every visit | **Owner** (no tracking) | Ours | Network capture in the browser: **zero external hosts** |
| 1.5 | `GenerateAll()` recursion is bounded, and reports a damaged file instead of recursing forever | A crafted or corrupt `.slvs` could drive unbounded recursion and overflow the stack | **Found here** (fuzzing) | Upstream **GH #1688** proposes making `GenerateAll` non-recursive — a rewrite. We read it and chose a bound instead, as the smaller change | Fuzz corpus no longer overflows; 263 upstream tests pass |
| 1.6 | Null dereference fixed in `GenerateShellAndMesh()` when the group chain is broken | A file referencing a missing predecessor group crashed | **Found here** (fuzzing) | Appears unreported upstream | Fuzz corpus; test suite |
| 1.7 | Null dereference fixed in `LocateImportedFile()` in builds without dialogs | The headless CLI crashed on a missing linked file instead of declining | **Found here** (fuzzing) | Upstream **GH #1768** is an open PR fixing the same crash. Found independently here before that PR was read; the fix is equivalent in effect | CLI now declines cleanly |
| 1.8 | WebGL context falls back to software, and only then shows an explanation | On a machine with no usable GPU the canvas was black with no message | **Found here** (stress testing); matches **Forum** reports of black or white screens on startup | Ours | Software-only run renders instead of a black screen |
| 1.9 | Downloaded files are named properly (`box.slvs`, not `_data__box`); a name typed without an extension gets the right one | Saving and exporting produced unusable filenames, and an extensionless export wrote a 0-byte file *and* raised an error | **Found here** (testing); related **Forum** threads on failed STL export | Ours | Browser workflow test |
| 1.10 | Tab title shows the model name and a bullet when there are unsaved changes | The tab said "SolveSpace Web Edition (EXPERIMENTAL)" regardless of state | **Owner** (branding), **Found here** (no unsaved indicator) | Ours | Browser workflow test |
| 1.11 | Autosave writes a recovery file when the sketch has never been saved | Autosave did nothing at all for an unsaved sketch — exactly the case a browser tab loses | **Found here** | Ours | Recovery test |
| 1.12 | CI pipeline (`drafting-tools.yml`): native build, test suite, sanitizers, fuzzing gate, web build, "no external origin" check | Nothing enforced any of the above. Upstream's own workflows fail in this fork for unrelated reasons and were set to manual | **Owner** (must stay green), **Found here** | Ours | Green on GitHub runners |
| 1.13 | Test and benchmark tooling: `fuzz_slvs.py` and a 16-file crash corpus, `bench_*.py`, `gen_*.py`, `serve.py` | The work above needed measurement, and the measurements need to be repeatable by anyone | **Found here** | Ours. Upstream **GH #1020** asks for an automated performance benchmark; ours is offerable against it | Used throughout |

## Commit `cf57ab42` — Build correctness and base-path joining (2026-09-17)

| # | Change | Why | Requested by | Notes on origin | Verified by |
|---|---|---|---|---|---|
| 2.1 | Web UI files (`solvespaceui.js`, `solvespaceui.css`, `filemanagerui.js`) are real build outputs with declared dependencies | Editing only the JS or CSS left a stale copy in the output directory, because the copy step ran as POST_BUILD on an already-up-to-date target. Silent, and it wasted hours | **Found here** | Ours | Touching a JS file now rebuilds its copy |
| 2.2 | `joinPath()` in the file manager UI | Setting the virtual filesystem base path to `/data` produced `/datafile.slvs` on upload — a regression from change 1.9's companion edit | **Found here** (our own regression) | Ours | Upload path in the browser test |

## Commit `ba4b3c2e` — Reject damaged sketches at load time (2026-09-19)

| # | Change | Why | Requested by | Notes on origin | Verified by |
|---|---|---|---|---|---|
| 3.1 | Load-time validation of a `.slvs` before it reaches the kernel: duplicate and null handles rejected, per-constraint required-handle table, `ValidateLoadedSketch()` refuses a file with nothing usable left | The file loader trusted its input. A corrupt or hostile file reached the geometry kernel and tripped internal assertions, which abort the program. On a public site the input is untrusted by definition | **Owner** (public hosting), **Found here** (fuzzing) | Ours | Fuzz crash rate over 1500 mutated files fell from **36% to 0.7%**; sanitizer findings **0**; 263 upstream tests pass; 0 false positives across all 62 upstream example models |
| 3.2 | `PruneBrokenEntities()` and tightened pruning of requests and constraints | Pruning accepted forward references and missing entities, leaving dangling handles behind | **Found here** | Ours | As above |
| 3.3 | `Remap()` allocates past the highest existing id instead of `size() + 1` | Deleting from a remap table let the next allocation collide with a live id | **Found here** | Ours | Test suite |
| 3.4 | `PT_ON_FACE` and `PT_FACE_DISTANCE` check that the entity really is a face | A constraint naming a non-face entity reached code that assumed otherwise | **Found here** (fuzzing) | Ours | Fuzz corpus |
| 3.5 | `EnsureValidActives()` no longer re-enters `GenerateAll` while generating | Re-entrancy during regeneration; the other half of change 1.5 | **Found here** | Ours | Fuzz corpus |
| 3.6 | Upstream `test.yml` and `cd.yml` set to manual dispatch | They fail in this fork for reasons unrelated to it (macOS dependency install), and a permanently red CI teaches people to ignore CI | **Found here** | Ours | CI is green |

## Commit `211f78bc` — Lathe, revolve and helix subtype (2026-09-19)

| # | Change | Why | Requested by | Notes on origin | Verified by |
|---|---|---|---|---|---|
| 4.1 | Validation no longer requires a known subtype on `LATHE`, `REVOLVE` and `HELIX` groups | **A regression introduced by change 3.1 in this fork.** Those group types never read the subtype field, so requiring it flagged perfectly valid models as damaged | **Found here** (our own regression, caught by testing against all upstream example models) | Ours | 0 false positives across all 62 example models |

## Commit `d7b34f69` — Files and unsaved work survive a reload (2026-09-19)

| # | Change | Why | Requested by | Notes on origin | Verified by |
|---|---|---|---|---|---|
| 5.1 | IndexedDB-backed filesystem mounted at `/data`, synced on load and debounced on write | Everything lived in memory. Closing the tab lost the work — on a tool whose premise is "sit down at someone else's computer", that is the whole product failing | **Owner**, and **Forum**: the upstream web-edition thread is largely people reporting that file I/O does not work | Ours. Upstream has not implemented this | Files survive a reload in the browser test |
| 5.2 | Recovery offer on startup when an autosave is found | An unsaved sketch is the common case here; a closed tab should be recoverable | **Owner** | Ours | Recovery test: draw, wait for autosave, reload, restore |
| 5.3 | `RemoveAutosave()` also removes the recovery file | Otherwise a saved sketch still offered to recover itself | **Found here** | Ours | Recovery test |
| 5.4 | Web autosave interval defaults to one minute | A browser tab dies without warning far more often than a desktop program does | **Owner** | Ours | Recovery test |

## Commit `48ff4eb7` — One-click STL, printability warning, touch pass (2026-09-19)

| # | Change | Why | Requested by | Notes on origin | Verified by |
|---|---|---|---|---|---|
| 6.1 | **File → Export STL for Printing** (Ctrl+Shift+E): writes `<sketch>.stl` at 1:1 millimetres with no format prompt | The target use is a part going to a 3D printer. STL carries no units and every slicer reads it as millimetres, which is what the sketch is in, so the 2D export scale is bypassed rather than applied | **Owner** (3D-printing audience) | Ours | Browser workflow test |
| 6.2 | Export dialog suggests an extension the dialog accepts | It suggested the sketch's own name *including* `.slvs`, so accepting the prefilled name on a mesh export asked the exporter to write a `.slvs` mesh | **Found here** (testing) | Ours. Introduced by change 1.9, which preserved the extension to fix a different problem | Prefill is now `box.stl`, was `box.slvs` |
| 6.3 | Watertightness reported **before** the file is written, in printing terms | Upstream reports it after the write, in the language of the mesh ("naked edges"). A non-watertight STL loads in a slicer and then prints as something other than the part | **Owner** (printability check), **Forum**: a dozen-plus threads of people asking what the red lines mean | Reuses upstream's existing `MakeCertainEdgesInto` check; the timing and the wording are ours | Browser workflow test |
| 6.4 | `ExportMeshTo()` returns whether it wrote anything; no longer leaks the open file handle when the `.mtl` companion cannot be created; no longer reports success for an unrecognised extension | Two latent resource and correctness bugs in the same function | **Found here** (reading the function while making 6.3) | Ours | Test suite |
| 6.5 | Touch release reports the correct button | The handler read the finger count back from a field it had already cleared, so **every** touch release arrived as a middle-button one — a one-finger drag never let go of what it was dragging | **Found here** (writing the touch test); requested in substance by the **Forum** web-edition thread, where touchscreen support is asked for repeatedly | Ours | `tools/web_touch.py`: one-finger tap places geometry |
| 6.6 | Pinch keeps its direction past the clamp | The sign was read back from an already-clamped value, so a fast pinch closed zoomed **in** | **Found here** | Ours | `tools/web_touch.py`: pinch in and out differ |
| 6.7 | `touchend` with no remaining touches no longer divides by zero | It put a NaN into the pointer position, which selects nothing and moves the view nowhere | **Found here** | Ours | `tools/web_touch.py`: no uncaught page errors |
| 6.8 | Coarse-pointer and small-screen layout: 34px menu rows, larger buttons, 16px editor font, text window stacks under the drawing at phone width, canvas claims its own gestures | 19px menu rows are below every platform's minimum tap target, and a 410px minimum on the text window leaves a sliver of drawing on a phone | **Owner** (mobile pass), **Forum**: repeated requests for tablet and touchscreen use | Ours | Phone viewport: 0px horizontal overflow, smallest menu row 40px |
| 6.9 | `localStorage` settings keys namespaced under `draftingtools.`, migrated from the old flat names on first read, read through helpers that tolerate storage being disabled or full; a corrupt entry falls back to its default | Unprefixed keys collide with anything else served from the same origin. Worse, `localStorage` throws outright when site data is blocked — enough to stop the program starting — and a corrupt entry put a NaN into a preference | **Found here** | Ours | Web build boots; settings persist across reloads |
| 6.10 | `tools/web_touch.py` | 6.5 through 6.8 needed a repeatable check at phone size | **Found here** | Ours | Six of six checks pass |
| 6.11 | New menu string added to `res/locales/en_US.po` | Otherwise the new menu item logs a missing-translation warning on every start | **Found here** | Ours | Warning gone |

---

## Summary of origins

| Origin | Rows |
|---|---|
| Requested by the project owner | 12 |
| Found by testing, fuzzing or stress work done for this fork | 21 |
| Required by GPLv3 | 1 |
| Corresponds to an open upstream report (GH #1688, GH #1768) | 2 |
| Motivated by upstream forum reports | 5 (overlapping with the above) |
| Regressions introduced by this fork and then fixed by it | 2 |

Nothing in this fork is copied from an upstream pull request. Where upstream had
an open patch for the same problem (GH #1688, GH #1768), it is named in the row
and the relationship is stated. Everything else in the repository is upstream
SolveSpace, unmodified, under its own copyright.
