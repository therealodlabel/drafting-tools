# Provenance and change record

This folder is the written record of what drafting.tools changed relative to
upstream SolveSpace, why each change was made, who asked for it, and who wrote
it. It is kept in the repository rather than alongside it, so it travels with
the source it describes and is published under the same licence.

## The files

| File | What it holds |
|---|---|
| [`CHANGE-LEDGER.md`](CHANGE-LEDGER.md) | Every change, one row each: what it does, why, **who asked for it or where it was requested**, **who wrote it**, and how it was verified |
| [`AUTHORSHIP.md`](AUTHORSHIP.md) | How this fork was written, including the use of an AI assistant, stated plainly |
| [`COMMUNITY-REQUESTS.md`](COMMUNITY-REQUESTS.md) | The upstream questions, bug reports and answers that motivated the work — quoted in substance, with links back to the originals |
| [`LICENSE-COMPLIANCE.md`](LICENSE-COMPLIANCE.md) | What GPLv3 requires of a modified version, and where each obligation is met in this repository |

## How to read a ledger row

Each row answers four separate questions, deliberately kept apart because they
have different answers:

1. **What changed** — the behaviour, not the diff. The diff is in the commit.
2. **Why** — the problem it solves.
3. **Requested by** — who wanted it. This is either the project owner, an
   upstream issue or forum thread (linked), or "none: found here", meaning
   nobody reported it and it was found by testing done for this fork.
4. **Written by** — who produced the change. For this project that is either
   *Claude (Anthropic), under direction* or *upstream, unmodified*. Where an
   upstream patch or branch was consulted, the row says so.

"Requested by" and "written by" are usually different, and that is the point of
recording them separately. A bug found by fuzzing done here and fixed here is
credited here. A fix that follows an upstream patch is credited upstream, even
when it was retyped.

## What this record is for

Three practical reasons:

1. **Licence compliance.** GPLv3 §5 requires a modified version to carry
   prominent notices stating that it is modified and giving the date. The
   ledger is the detailed form of that statement.

2. **Honest attribution.** SolveSpace is somebody else's work, and most of this
   codebase is still theirs. The ledger makes the boundary visible: what is
   ours is a small, specific list, and it is written down rather than implied.

3. **Traceability.** When something in this fork behaves differently from
   upstream — in a year, to someone who was not here — the ledger says when it
   changed and why, without archaeology through the diff.

## What this record is not

It is a factual account of authorship and provenance, not a legal instrument,
and it is not legal advice. Documenting the origin of each change is good
practice and makes the GPL obligations demonstrably met, but it does not by
itself create or limit liability for anything. The software is distributed
under GPLv3, which disclaims warranty (§15) and limits liability (§16) in its
own terms; those sections, not this folder, are what govern.

## Keeping it current

A change that alters behaviour gets a ledger row in the same commit that makes
the change. The ledger is ordered oldest first and never rewritten — a fix to
an earlier change is a new row that references it, not an edit to the old one.
