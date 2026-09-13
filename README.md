# Custos Fallback

[![PyPI](https://img.shields.io/pypi/v/thalovant-skill-custos-fallback)](https://pypi.org/project/thalovant-skill-custos-fallback/)
[![License](https://img.shields.io/pypi/l/thalovant-skill-custos-fallback)](LICENSE)

**Your voice assistant should never just go quiet on you.**

Ask it something it doesn't know, and normally nothing happens at all. No
answer, no "sorry" — just silence, and you standing there wondering if it even
heard you.

This adds the missing reply:

> *"I cannot answer that. Ask me about incidents, or how this appliance is
> doing."*

That's the whole skill.

## Install

```bash
pip install thalovant-skill-custos-fallback
```

Nothing to set up. It only speaks when no other skill could help, so it never
gets in the way.

Works with any [OpenVoiceOS](https://openvoiceos.org) assistant.

## Anything else

- [How it works](HOW_IT_WORKS.md) — for the curious, and for anyone hacking on it
- Apache-2.0 licensed. Use it, fork it, ship it.

## Privacy and verification

Unmatched requests produce a localized refusal. Logs record the outcome and
resolved language without retaining the raw question, which may contain personal
information. The skill uses no network service.

Native OVOScope tests load every shipped locale and check that its refusal reaches
the originating session. Separate behavior tests cover fallback priority, missing
input, packaged resources, and the absence of raw speech in logs.

```sh
python -m pip install --pre -e '.[test,e2e]' build
python -m pytest -q test --ignore=test/end2end
python -m pytest -q test/end2end
python -m build
thalovant-skillkit check-artifacts . --wheel dist/*.whl --sdist dist/*.tar.gz
```

Passing resource and dispatch checks does not establish native-speaker review
of every translation.

For the current OVOS stack, use `--pre` as shown above. If deliberately testing
legacy Workshop 8.0.0, also install `"setuptools<81"`: its older plugin manager
imports `pkg_resources`, which newer setuptools releases removed. This is a
legacy environment constraint, not a runtime-wide setuptools restriction.
