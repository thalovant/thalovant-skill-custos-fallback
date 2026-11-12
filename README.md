Last Edit: Claude Code (Claude Sonnet 5.5) - 2026-11-10 - Motive: Standard README (say it, install, settings, languages, develop).

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thalovant/.github/main/profile/assets/thalovant-logo-dark.png">
    <img src="https://raw.githubusercontent.com/thalovant/.github/main/profile/assets/thalovant-logo-light.png" alt="Thalovant" width="240">
  </picture>
</p>

# Custos Fallback

[![Test](https://github.com/thalovant/thalovant-skill-custos-fallback/actions/workflows/test.yml/badge.svg)](https://github.com/thalovant/thalovant-skill-custos-fallback/actions/workflows/test.yml)

Gives a request nobody answers a helpful reply instead of silence.

## Say it

- “Anything no other skill understands” → A short explanation, and a suggestion to ask about incidents or the appliance's status.

It speaks only after the other skills decline, and works offline.

## Install

Open the Thalovant marketplace on your hub and add **Thalovant Custos Fallback**. Or install it yourself:

```sh
pip install thalovant-skill-custos-fallback
```

## Languages

40 languages and regional variants, including English, French, Spanish, German ([full list](thalovant_skill_custos_fallback/locale/supported.json)).

## Develop

```sh
pip install -e ".[test]"
python -m pytest test --ignore=test/end2end
```

Pull requests are tested on every change ([workflow](https://github.com/thalovant/thalovant-skill-custos-fallback/actions/workflows/test.yml)).

## Licence

Apache-2.0.
