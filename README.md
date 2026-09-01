# Custos Fallback — an OVOS fallback skill that answers when nothing matched

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![OVOS skill](https://img.shields.io/badge/OVOS-skill-brightgreen)](https://openvoiceos.org)
[![Languages](https://img.shields.io/badge/languages-24-informational)](#languages)

A last-resort [OpenVoiceOS](https://openvoiceos.org) fallback skill. When no
intent matches, it says so — in the user's language, immediately — instead of
leaving the caller to discover the failure by timing out.

Built for the [Thalovant](https://thalovant.com) Custos appliance, but it
depends on nothing from it. It is about eighty lines and will slot into any
ovos-core or HiveMind hub.

## The problem, measured

An utterance that matches no intent produces **no terminal event on the wire at
all**. Not a renamed one. Nothing.

Here is a client subscribed to every terminal event worth naming —
`ovos.intent.unmatched`, `complete_intent_failure`, `ovos.utterance.handled`,
`speak`, `ovos.utterance.speak`, `ovos.intent.matched`,
`ovos.utterance.cancelled` — sending one utterance of each kind down the same
connection to a live HiveMind hub:

```
--- unmatched: 'flibbertigibbet wumpus' ---
    NOTHING arrived in 12s

--- matched control: 'what is the weather' ---
    + 1.60s  ovos.utterance.speak     ctx={'request_id': 'request-e43b32b3...'}
    + 1.61s  ovos.utterance.handled   ctx={'request_id': 'request-e43b32b3...'}
```

The correlation plumbing is healthy: the matched reply comes back in 1.6s with
the right `request_id`. The unmatched one simply never resolves. A voice client
therefore waits out its full timeout — several seconds of silence in a room —
for a question the hub was never going to answer.

`ovos-core` does raise `ovos.intent.unmatched` internally. It does not reach
HiveMind satellite clients the way `speak` and `ovos.utterance.handled` do, so
a satellite cannot tell "nothing matched" from "still thinking".

A fallback skill is the fix, because **the hub is the only place that knows
nothing matched.** Anything the client does — a vocabulary gate, a list of
known intents — is a guess about the hub's capabilities held somewhere that
cannot know them, and it goes stale the moment a skill is installed.

## What it does

Speaks a short refusal that names what the assistant *can* answer, then returns
`True` so the interaction ends.

> I cannot answer that. Ask me about incidents, or how this appliance is doing.

Priority **95**, in the 90–100 last-resort band: it runs after every intent
match and every other fallback, so a persona, an LLM fallback, or
`ovos-skill-fallback-unknown` at 100 all get their turn first.

## Why it refuses instead of asking a language model

Routing unmatched questions to an LLM is tempting and, for an infrastructure
assistant, wrong. It would answer questions it has no evidence for, and a
confident wrong answer about a storage pool or a BMC is worse than an honest
"I cannot". This refuses in about the time a real answer takes.

Anything cleverer belongs behind an explicit intent, where the wait is asked
for rather than sprung.

## Install

```bash
pip install git+https://github.com/thalovant/thalovant-skill-custos-fallback
```

Or from a checkout:

```bash
pip install -e .
```

Nothing to configure. It has no settings, no network access, and no intent
files — it is reached precisely when nothing else matched.

## Languages

Twenty-four locales, every language OVOS itself supports:

```
ca-ES  cs-CZ  da-DK  de-DE  en-US  es-ES  eu-ES  fa-IR  fr-FR  gl-ES
hu-HU  it-IT  kab    kab-DZ nl-BE  nl-NL  pl-PL  pt-BR  pt-PT  ru-RU
sv-FI  sv-SE  tr-TR  uk-UA
```

That set is deliberate. A skill booted in a language it has no locale directory
for **does not fall back to English** — it speaks the dialog's identifier, and
the room hears the literal string `custos.unknown.request`. So for a
dialog-only skill an imperfect translation always beats an omitted one.

`en-US` and `fr-FR` are maintained. **The other 22 are machine-authored and
have not been reviewed by a native speaker** — Kabyle least of all. Corrections
are the most useful contribution this repository can receive; a pull request
touching one language's `locale/<lang>/` directory needs no coordination with
any other.

## Tests

```bash
pip install -e '.[test]' && pytest test/                 # unit
pip install --pre -e '.[test,e2e]' && pytest test/       # + real ovos-core
```

The end-to-end suite boots an actual ovos-core through
[ovoscope](https://github.com/OpenVoiceOS/ovoscope) and asserts two things the
unit tests structurally cannot: that the skill *loads*, and that an unmatchable
utterance produces speech rather than silence — in both maintained locales.

That distinction is not academic. `FallbackSkill` declares `can_answer`
abstract, and an unimplemented abstract method does not merely disable the
fallback: the class cannot be instantiated, the skill fails to load, and **every
intent in its package fails with it**. That is why this is its own package
rather than a handler bolted onto a skill that does real work. It passed unit
tests once while doing exactly that.

The locale assertion checks the *rendered text*, not just that something was
spoken — a missing dialog file still emits a perfectly ordinary `speak`
message, so "did it speak" passes on the exact failure locale coverage exists
to catch.

## License

Apache-2.0.
