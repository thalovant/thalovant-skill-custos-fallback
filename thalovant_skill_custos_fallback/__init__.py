"""Answer for Custos when no skill could.

An unmatched utterance produces no terminal event on the wire at all. Measured
against this hub on 2026-09-01: subscribing a client to `ovos.intent.unmatched`,
`complete_intent_failure`, `ovos.utterance.handled`, `speak` and four other
names, a matched question returned `ovos.utterance.speak` in 1.60s while an
unmatched one produced nothing for the full twelve seconds. A caller therefore
learns of it only by waiting out its own timeout, which in a room is several
seconds of silence for a question this hub was never going to answer.

The node cannot fix that. Anything it does — a vocabulary gate, a list of known
intents — is a guess about the hub's capabilities held somewhere that cannot
know them, and it goes stale the moment a skill is installed. The hub is the
only place that knows nothing matched.

This is deliberately its own package rather than a handler bolted onto the
shadow or query skills. `FallbackSkill` declares `can_answer` abstract, and an
unimplemented abstract method does not merely disable the fallback: the class
cannot be instantiated, the skill fails to load, and every intent it owns fails
with it. That happened once already, taking status, incidents and check-in down
in both locales. Isolated here, the worst a mistake in this file can do is stop
the apology — the shadow's ingestion and the live query path are untouched.

It refuses rather than improvises on purpose. Handing an unmatched question to
a language model would make this appliance answer infrastructure questions it
has no evidence for, and a confident wrong answer about a pool or a BMC is
worse than an honest "I cannot".
"""

from __future__ import annotations

from ovos_utils.log import LOG

from thalovant_skillkit.skill import ThalovantFallbackSkill


class CustosFallbackSkill(ThalovantFallbackSkill):
    """Say that nothing matched, instead of leaving the room in silence.

    Lower numbers run first. ovos-core consults its fallbacks in three bands --
    high (1-5), medium (6-90) and low (91-100) -- each a separate pipeline
    stage, and the low band this sits in is the last stage of all, after every
    intent matcher and the other two bands. Inside a band exactly one skill
    fires: the lowest number whose can_answer said yes.

    `can_answer` here is unconditionally True, so this skill's number is the
    whole of its politeness. **It was 95, and that was wrong.** Nine sibling
    skills register fallbacks between 96 and 99 -- joke-garden, guide,
    learning-lounge, language-buddy, local-pulse, memory, ops-copilot,
    safety-guide, source-scout -- and every one of them was unreachable while
    this answered first. Asked "what can you help me with today", a hub with
    both installed said "I cannot answer that" while the guide skill sat behind
    it holding the list. Worse, weather and date-time register at 95 too, so
    which of the three spoke came down to sort stability.

    100 is the end of the band and behind every sibling, which is what "every
    more capable skill has already declined" was supposed to mean. A chat or
    language-model fallback registered anywhere below this still pre-empts it,
    which remains the intended way to replace this message.

    Speaking a refusal needs nothing: no network, no node, no internet. This
    must work precisely when the rest of the appliance does not, which is why
    none of the REQUIRES_* attributes is set.
    """

    FALLBACK_PRIORITY = 100

    def can_answer(self, message) -> bool:
        """Always, because saying so is the answer.

        A fallback that reports nothing could handle the request is exactly
        the case where every more capable skill has already declined. There
        is no utterance this cannot respond to, and priority -- not this -- is
        what decides where it stands in the queue.
        """
        return True

    def reply(self, utterance: str, lang: str, context: dict) -> str:
        """The hub answering, rather than the caller timing out."""
        # Unmatched speech may contain personal information or a dictated
        # credential. Record the outcome without retaining the raw question.
        LOG.info("custos fallback: nothing matched (lang=%s)", self.locale_resources.lang(lang))
        return self.dialog("custos.unknown.request", lang)
