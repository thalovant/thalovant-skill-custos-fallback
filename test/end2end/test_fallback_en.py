"""Fallback coverage for en-US. Drift-immune: it loaded, and it spoke."""

from unittest import TestCase

from ._helpers import FallbackFiringMixin


class TestEnFallbackFires(FallbackFiringMixin, TestCase):
    LANG = "en-US"

    def test_nonsense_is_answered_rather_than_ignored(self):
        self.assert_answers("flibbertigibbet wumpus")

    def test_a_plausible_english_question_outside_the_domain_is_answered(self):
        # Nonsense words could conceivably be filtered before intent matching.
        # A real question this hub simply cannot answer is the honest case.
        self.assert_answers("what is the tire pressure on the van")
