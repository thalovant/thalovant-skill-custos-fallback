"""Each shipped language can speak its own refusal through the native pipeline."""
from pathlib import Path

import pytest
from ovoscope import FALLBACK_PIPELINE, make_session, make_utterance_message
from thalovant_skillkit.testing_ovos import capture_turn, managed_minicroft

ROOT = Path(__file__).resolve().parents[2] / "thalovant_skill_custos_fallback" / "locale"
SKILL_ID = "thalovant-skill-custos-fallback.thalovant"
LANGS = sorted(p.name for p in ROOT.iterdir() if p.is_dir())


@pytest.mark.parametrize("lang", LANGS)
def test_localized_refusal_reaches_its_originating_session(lang):
    with managed_minicroft([SKILL_ID], lang=lang) as croft:
        session = make_session(session_id=f"fallback-{lang}", lang=lang,
                               pipeline=list(FALLBACK_PIPELINE), blacklisted_skills=[])
        turn = capture_turn(croft, make_utterance_message("unmatched testing words", lang=lang, session=session), timeout=15)
        speech = turn.of_type("ovos.utterance.speak") or turn.of_type("speak")
        expected = set((ROOT / lang / "dialog/custos.unknown.request.dialog").read_text().splitlines())
        assert speech and all(m.data["utterance"] in expected for m in speech)
        assert all(m.context["session"]["session_id"] == session.session_id for m in speech)
