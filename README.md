# Custos Fallback

**When your voice assistant doesn't know the answer, it should say so.**

Ask an OVOS assistant something no skill can handle, and what happens is…
nothing. No "sorry, I don't know" — just silence, while you stand there
wondering whether it heard you at all. Eventually whatever asked the question
gives up and times out.

This little skill fixes that. It waits until every other skill has had its
turn, and if nobody could answer, it says so out loud, straight away, in your
language.

> *"I cannot answer that. Ask me about incidents, or how this appliance is
> doing."*

That's the whole idea. About eighty lines of Python.

## Install

```bash
pip install git+https://github.com/thalovant/thalovant-skill-custos-fallback
```

There's nothing to configure. No settings, no network access, no API keys. It
runs last by design, so it never gets in the way of a skill that *can* help.

Built for the [Thalovant](https://thalovant.com) Custos appliance, but it
doesn't need any of it — drop it into any [OpenVoiceOS](https://openvoiceos.org)
assistant or HiveMind hub and it works.

## Speaks 24 languages

```
Català · Čeština · Dansk · Deutsch · English · Español · Euskara · فارسی
Français · Galego · Magyar · Italiano · Taqbaylit · Nederlands · Polski
Português · Русский · Svenska · Türkçe · Українська
```

Every language OVOS itself supports. There's a good reason for going all the
way: if a skill has no translation for the language it's running in, OVOS
*doesn't* quietly fall back to English — it reads the internal message name out
loud. Your assistant literally says "custos dot unknown dot request" at you. A
rough translation is always kinder than that.

Which brings us to an honest note: **English and French are the two we
maintain. The other 22 were machine-translated and no native speaker has
checked them.** Kabyle especially. If one of them sounds wrong or just odd,
[open an issue](https://github.com/thalovant/thalovant-skill-custos-fallback/issues)
or send a pull request — fixing one language means touching one folder and
nothing else. It's the most useful thing anyone can contribute here.

## Why not just let an AI answer?

It's tempting. We decided against it.

This started life on an appliance that watches servers and storage, where a
made-up answer about a failing disk is genuinely worse than no answer at all.
An honest "I don't know" takes about a second. A language model guessing takes
longer *and* might be confidently wrong.

If you want your assistant to think hard about something, that should be
something you asked for on purpose — not a surprise that happens whenever it
gets confused.

## For the curious: what's actually going on

An utterance that matches no intent produces **no terminal event on the bus at
all** — so a voice client can't tell "nothing matched" from "still thinking",
and simply waits out its timeout. Here's a client listening for every ending
you'd expect (`ovos.intent.unmatched`, `complete_intent_failure`,
`ovos.utterance.handled`, `speak`, and friends), sending two utterances down
the same connection to a live hub:

```
unmatched  "flibbertigibbet wumpus"    nothing arrived in 12 seconds
matched    "what is the weather"       replied in 1.6 seconds
```

`ovos-core` does raise `ovos.intent.unmatched` internally, but it doesn't reach
HiveMind satellite clients the way `speak` does. And the hub is the only place
that *knows* nothing matched — a client guessing from a list of known intents
goes stale the moment you install a skill. So: a fallback skill.

It registers at priority **95**, inside the 90–100 last-resort band, so
personas, LLM fallbacks and `ovos-skill-fallback-unknown` all get asked first.

## Tests

```bash
pip install -e '.[test]' && pytest test/                 # fast
pip install --pre -e '.[test,e2e]' && pytest test/       # + a real ovos-core
```

The end-to-end tests boot an actual assistant via
[ovoscope](https://github.com/OpenVoiceOS/ovoscope) and check two things the
unit tests can't: that the skill *loads*, and that an unanswerable question
produces real speech — in both maintained languages.

That first one matters more than it sounds. `FallbackSkill` has an abstract
`can_answer` method, and forgetting it doesn't just disable your fallback: the
class can't be created, the skill never loads, and **every other intent in the
same package disappears with it**. That happened to us. It's why this lives in
its own package instead of being bolted onto a skill that does real work.

## License

Apache-2.0 — use it, fork it, ship it.
