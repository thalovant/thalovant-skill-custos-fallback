# Changelog

## 0.1.5 (2026-09-26)

Dependency floor only; no behaviour change.

- Require thalovant-skillkit 0.22.0, the release that sends speech markup (SSML)
  beside a reply's plain words. The reply here needs no markup: two plain
  sentences, spoken through the kit's fallback `reply`, so the kit's guard
  against SSML in plain text covers it.

## 0.1.4 (2026-09-19)

- Complete 15 common regional resource sets using shared translations and explicit
  regional wording; keep existing regional translations.
- Use SkillKit 0.15 regional generation and freshness checks, with complete files
  for native OVOS and direct resource readers.
- Update resource and regional behavior tests and document translation provenance.


## 0.1.3 - 2026-09-19

- Use SkillKit 0.14 regional fallback for compatible language variants without duplicating translations. Preserve the requesting session language.
- Exercise regional requests through the native OVOS test harness.

## 0.1.2 — 2026-09-13

Stop recording raw unmatched speech in logs. Verify refusal routing through native OVOS for all 24 bundled locales, use shared OVOS test helpers, and validate wheel/sdist resources in CI.

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
