"""Shared infrastructure for the fallback's end-to-end coverage.

This layer exists because the unit suite structurally cannot reach it: those
tests build the skill with ``__new__`` and stub ``speak_dialog``, proving the
logic and nothing about loading. A ``FallbackSkill`` missing its abstract
``can_answer`` passes unit tests and still cannot be instantiated by ovos-core,
which takes every intent in its package down with it. That happened once.

Assertions are deliberately drift-immune, matching the sibling skills: rather
than pinning an ordered message sequence (which breaks on bus-vocabulary
changes like the ``speak`` -> ``ovos.utterance.speak`` rename), each test
asserts only that the skill spoke.
"""

from pathlib import Path

from ovos_utils.log import LOG
from ovoscope import CaptureSession, get_minicroft, make_session, make_utterance_message

SKILL_ID = "thalovant-skill-custos-fallback.thalovant"
DIALOG_NAME = "custos.unknown.request"
LOCALE_ROOT = (
    Path(__file__).resolve().parents[2] / "thalovant_skill_custos_fallback" / "locale"
)

# Both spellings of the "the skill spoke" side effect across ovos-core versions.
_SPOKE = {"speak", "ovos.utterance.speak"}


class FallbackFiringMixin:
    """Mixin for per-locale TestCases. Subclasses set ``LANG``."""

    LANG: str = "en-US"

    @classmethod
    def setUpClass(cls):
        LOG.set_level("DEBUG")
        # One language per class: a single-locale MiniCroft keeps each module
        # fast, the same reason the sibling skills split en and fr.
        cls.minicroft = get_minicroft([SKILL_ID], lang=cls.LANG)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "minicroft", None):
            cls.minicroft.stop()
        LOG.set_level("CRITICAL")

    def _capture(self, utterance: str):
        session = make_session(
            session_id=f"custos-fallback-{self.LANG}-{abs(hash(utterance))}",
            blacklisted_intents=[],
            blacklisted_skills=[],
            lang=self.LANG,
        )
        message = make_utterance_message(utterance, lang=self.LANG, session=session)
        capture = CaptureSession(minicroft=self.minicroft)
        capture.capture(message, timeout=15)
        return list(capture.finish())

    def test_the_skill_loads_at_all(self):
        # Asserted separately from behaviour: this is the failure that also
        # silently removes every other intent in whichever package it lives in.
        self.assertTrue(self.minicroft.is_all_loaded(), f"{SKILL_ID} did not finish loading")

    def assert_answers(self, utterance: str):
        messages = self._capture(utterance)
        types = [m.msg_type for m in messages]
        self.assertTrue(
            _SPOKE.intersection(types),
            f"{utterance!r} in {self.LANG} produced no speech at all "
            f"(captured: {types}) — which is the silence this skill exists to end",
        )
        spoken = [
            str((m.data or {}).get("utterance") or "")
            for m in messages
            if m.msg_type in _SPOKE
        ]
        # A missing dialog file does not fall back to English: OVOS renders the
        # dialog *name*, speaks "custos unknown request" at the room, and still
        # emits a perfectly ordinary speak message. Asserting only that it spoke
        # would pass on exactly the failure this locale coverage is here to find.
        for line in spoken:
            self.assertNotIn(
                DIALOG_NAME,
                line.replace(" ", ".").lower(),
                f"{self.LANG} spoke the raw dialog name, so its dialog file is missing: {line!r}",
            )
        expected = self.dialog_lines()
        self.assertTrue(
            any(line.strip() in expected for line in spoken),
            f"{self.LANG} spoke {spoken!r}, none of which is a line of its own "
            f"dialog file ({sorted(expected)!r})",
        )

    def dialog_lines(self) -> set:
        path = (
            LOCALE_ROOT / self.LANG / "dialog" / f"{DIALOG_NAME}.dialog"
        )
        return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
