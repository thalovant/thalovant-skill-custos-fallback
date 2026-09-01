# Changelog

## 0.1.0

First release.

Speaks a refusal when no skill matched, in the 90-100 last-resort fallback
band, so an unmatched utterance ends in a sentence rather than the caller's
timeout. Measured on a live hub, an unmatched utterance produced no terminal
event at all for a full twelve seconds while a matched one answered in 1.6s.

Ships the same twenty locales as the other Custos skills. `en-US` and `fr-FR`
are maintained; the rest are machine-authored and unreviewed (see
`../TRANSLATIONS.md`).
