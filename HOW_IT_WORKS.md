# How it works

## The problem

An utterance that matches no intent produces **no terminal event on the bus at
all**. A voice client cannot tell "nothing matched" from "still thinking", so
it waits out its own timeout — several seconds of silence in a room.

A client subscribed to every ending you would expect
(`ovos.intent.unmatched`, `complete_intent_failure`,
`ovos.utterance.handled`, `speak`, `ovos.utterance.speak`,
`ovos.intent.matched`, `ovos.utterance.cancelled`), sending two utterances
down the same connection to a live HiveMind hub:

```
unmatched  "flibbertigibbet wumpus"    nothing arrived in 12 seconds
matched    "what is the weather"       replied in 1.6 seconds
```

`ovos-core` does raise `ovos.intent.unmatched` internally, but it does not
reach HiveMind satellite clients the way `speak` does.

The fix has to live on the hub, because the hub is the only place that *knows*
nothing matched. A client guessing from a list of known intents is holding a
copy of the hub's capabilities that goes stale the moment a skill is installed.

## Priority

Registered at **95**, inside the 90–100 last-resort band, so intent matches,
personas, LLM fallbacks and `ovos-skill-fallback-unknown` (priority 100) all
get their turn first.

## Why it refuses instead of asking a language model

This began on an appliance that watches servers and storage, where a
confidently wrong answer about a failing disk is worse than no answer. A
refusal costs about a second; a model guessing costs longer and may mislead.

Deliberate thinking belongs behind an explicit intent, where the wait was asked
for rather than sprung on someone.

## Why 24 languages

A skill booted in a language it has no locale directory for does **not** fall
back to English. It renders the dialog's identifier, and the room hears the
literal string `custos.unknown.request`. So for a dialog-only skill, an
imperfect translation always beats an omitted one.

The 24 are every language OVOS itself supports:

Català · Čeština · Dansk · Deutsch · English · Español · Euskara · فارسی ·
Français · Galego · Italiano · Magyar · Nederlands · Polski · Português ·
Русский · Svenska · Taqbaylit · Türkçe · Українська

`en-US` and `fr-FR` are maintained. The other 22 are machine-authored and
unreviewed — Kabyle least vouched-for of all. Corrections are the most useful
contribution this repository can receive, and a pull request touching one
language's `locale/<lang>/` directory needs no coordination with any other.

## Why it is its own package

`FallbackSkill` declares `can_answer` abstract. An unimplemented abstract
method does not merely disable the fallback: the class cannot be instantiated,
the skill fails to load, and **every intent in its package fails with it**.
That happened once, taking status, incidents and check-in down in two
languages.

Isolated here, the worst a bug in this file can do is stop the apology.

## Tests

```bash
pip install -e '.[test]' && pytest test/                 # fast
pip install --pre -e '.[test,e2e]' && pytest test/       # + a real ovos-core
```

The end-to-end suite boots an actual ovos-core through
[ovoscope](https://github.com/OpenVoiceOS/ovoscope) and asserts two things the
unit tests structurally cannot: that the skill loads, and that an unmatchable
utterance produces speech rather than silence, in both maintained locales.

The locale assertion checks the *rendered text*, not merely that something was
spoken — a missing dialog file still emits a perfectly ordinary `speak`
message, so "did it speak" passes on the exact failure locale coverage exists
to catch.
