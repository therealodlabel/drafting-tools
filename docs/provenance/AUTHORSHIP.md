# Authorship

## The short version

Upstream SolveSpace is the work of Jonathan Westhues and its contributors, and
remains the great majority of this codebase. The modifications listed in
[`CHANGE-LEDGER.md`](CHANGE-LEDGER.md) were made for drafting.tools in
September 2026 by Shavarsh (`therealodlabel`), working with Claude, an AI
assistant made by Anthropic. Claude wrote the code, the tests and this
documentation; the direction, the requirements, the review and the decision to
publish were the owner's.

That division is stated here rather than left to be inferred, because the
alternative — a fork that presents machine-written changes as though a person
typed them — is the kind of thing that is better said plainly at the start than
discovered later.

## What "written by Claude" means in practice

For each change in the ledger, the process was:

1. The owner set a requirement, or a problem surfaced from testing.
2. Claude read the relevant upstream code, proposed an approach, and wrote the
   change.
3. Claude wrote or extended a test that fails without the change.
4. The full upstream test suite (263 cases, 933 checks) was run, plus the
   fork's own fuzzing, sanitizer and browser harnesses.
5. The owner reviewed and pushed.

No change was committed without the upstream test suite passing. The
measurements quoted in the ledger — crash rates, test counts, pixel sizes — are
outputs of scripts in `tools/`, and can be reproduced by running them.

## Why this is recorded

**Attribution.** SolveSpace's authors deserve to have the boundary between
their work and this fork's drawn clearly, in writing. The ledger draws it.

**Honesty about how it was made.** Anyone deciding whether to trust, run,
contribute to or fork this code is entitled to know that its modifications were
machine-written and human-directed, and to weigh that however they like.

**Contributing back.** Several fixes here are not specific to drafting.tools
and are worth offering upstream. Upstream projects increasingly ask
contributors to disclose AI assistance; having it written down in advance means
a contribution can be offered honestly rather than retrofitted with a
disclosure.

## What it does not mean

It does not mean the changes are unreviewed, untested, or disclaimed. They were
written deliberately, tested against the project's own suite, and are the
owner's responsibility as the distributor — exactly as they would be if he had
typed them. Recording that an assistant wrote them is a statement about
process, not a disclaimer of the result.

It also does not change the licence. Every line added here is published under
GPLv3 along with the rest of the work, and the copyright notices of upstream
SolveSpace are intact and untouched.

## Contact

Source, issues and the full history: the public fork linked from
`NOTICE-drafting-tools.md`, and `https://drafting.tools/source`.
