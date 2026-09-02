# Changelog

## Unreleased

No change to what the skill does; the words around it were wrong in places.

The priority was described backwards. OVOS runs the lowest fallback number
first, so at 95 this skill speaks ahead of `ovos-skill-fallback-unknown`
(100), not after it, and a chat or language-model fallback registered below
95 would win instead. The docstrings, `HOW_IT_WORKS.md` and the unit test now
say so; the test also pins the band `ovos-core` actually routes to (91-100 —
90 belongs to the medium band).

The `fr-FR` dialog addressed the operator as *vous* while the other Custos
skills, and every other locale here with the distinction, use the informal
form. It now says *Demande-moi*.

The 0.1.0 notes below said twenty locales where the release shipped
twenty-four, and pointed at a file that only exists in the monorepo; both are
corrected in place. The documented fast test command skipped nothing and so
failed at collection without the `e2e` extra; it now ignores `test/end2end`.
`.coveragerc` measured the query skill's package instead of this one. The Python 3.14
classifier, which no CI job tests, is gone.

## 0.1.0

First release, on PyPI as `thalovant-skill-custos-fallback`.

Speaks a refusal when no skill matched, at priority 95 in the last-resort
fallback band, so an unmatched utterance ends in a sentence rather than the caller's
timeout. Measured on a live hub, an unmatched utterance produced no terminal
event at all for a full twelve seconds while a matched one answered in 1.6s.

Ships the same twenty-four locales as the other Custos skills. `en-US` and
`fr-FR` are maintained; the rest are machine-authored and unreviewed (see
`HOW_IT_WORKS.md`).
