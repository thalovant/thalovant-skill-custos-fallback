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

from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import fallback_handler
from ovos_workshop.skills import FallbackSkill


class CustosFallbackSkill(FallbackSkill):
    """Say that nothing matched, instead of leaving the room in silence."""

    @classproperty
    def runtime_requirements(self):
        # Speaking a refusal needs nothing: no network, no node, no internet.
        # This must work precisely when the rest of the appliance does not.
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            requires_internet=False,
            requires_network=False,
            no_internet_fallback=True,
            no_network_fallback=True,
        )

    def can_answer(self, message) -> bool:
        """Always, because saying so is the answer.

        A fallback that reports nothing could handle the request is exactly
        the case where every more capable skill has already declined. There
        is no utterance this cannot respond to, and priority — not this — is
        what decides where it stands in the queue.
        """
        return True

    @fallback_handler(priority=95)
    def handle_unknown_request(self, message):
        """The hub answering, rather than the caller timing out.

        Lower numbers run first. ovos-core consults its fallbacks in three
        bands — high (1-5), medium (6-90) and low (91-100) — each a separate
        pipeline stage, and the low band this sits in is normally the last
        stage of all, after every intent matcher and the other two bands.
        Inside a band exactly one skill fires: the lowest number whose
        can_answer said yes. So at 95 this speaks ahead of the stock
        unknown-request skill at 100, on purpose — with both installed it is
        this message the room hears. The flip side is that a chat or
        language-model fallback registered below 95 would win every
        unmatched utterance, which is the intended way to pre-empt this.
        """
        utterance = ""
        try:
            utterances = (message.data or {}).get("utterances") or []
            utterance = str(utterances[0]) if utterances else ""
        except (AttributeError, IndexError, TypeError):
            utterance = ""
        # What people ask and this hub cannot answer is the list of skills
        # worth writing next, and nothing else records it.
        LOG.info("custos fallback: nothing matched %r", utterance)
        self.speak_dialog("custos.unknown.request")
        return True
