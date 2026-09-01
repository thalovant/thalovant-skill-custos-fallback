"""Fallback coverage for fr-FR — a maintained locale, so it is exercised.

The skill's entire output is a rendered dialog. A missing or malformed
``fr-FR`` dialog file does not fall back to English: OVOS speaks the raw
dialog name aloud, which in a room is worse than the wrong language. Only
booting the French pipeline catches that.
"""

from unittest import TestCase

from ._helpers import FallbackFiringMixin


class TestFrFallbackFires(FallbackFiringMixin, TestCase):
    LANG = "fr-FR"

    def test_nonsense_is_answered_rather_than_ignored(self):
        self.assert_answers("flibbertigibbet wumpus")

    def test_a_plausible_french_question_outside_the_domain_is_answered(self):
        self.assert_answers("quelle est la pression des pneus de la camionnette")
