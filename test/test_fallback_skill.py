"""The fallback has one job, and one way to fail catastrophically."""

from pathlib import Path

from ovos_bus_client.message import Message

from thalovant_skill_custos_fallback import CustosFallbackSkill

LOCALE = Path(__file__).parent.parent / "thalovant_skill_custos_fallback" / "locale"


class HarnessSkill(CustosFallbackSkill):
    def __del__(self):
        pass

    @property
    def lang(self):
        return "en-US"

    @property
    def settings(self):
        return {}


def make_skill():
    skill = HarnessSkill.__new__(HarnessSkill)
    skill.said = []
    skill.speak = lambda text, *a, **k: skill.said.append(text)
    return skill


def _dialog_lines():
    path = LOCALE / "en-US" / "dialog" / "custos.unknown.request.dialog"
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_the_skill_instantiates_as_a_fallback_skill():
    # FallbackSkill declares can_answer abstract, and omitting it does not
    # merely disable the fallback: the class cannot be instantiated, the skill
    # fails to load, and every intent it owns goes with it. That took status,
    # incidents and check-in down in both locales once already. Cheap version
    # of the check that cost a CI round to learn.
    assert not getattr(CustosFallbackSkill, "__abstractmethods__", frozenset()), (
        "an unimplemented abstract method stops the whole skill loading"
    )
    assert make_skill() is not None


def test_it_answers_rather_than_leaving_the_room_silent():
    skill = make_skill()
    handled = skill.handle_fallback(
        Message("recognizer_loop:utterance", {"utterances": ["flibbertigibbet wumpus"]})
    )
    assert handled is True, "returning False lets the caller time out anyway"
    assert skill.said[-1] in _dialog_lines()


def test_an_utterance_the_message_does_not_carry_is_not_a_crash():
    # A fallback that raises is worse than one that says nothing: it leaves the
    # caller waiting out its timeout, which is the failure this exists to end.
    skill = make_skill()
    for payload in ({}, {"utterances": []}, {"utterances": None}, None):
        skill.said.clear()
        assert skill.handle_fallback(Message("x", payload)) is True
        assert skill.said[-1] in _dialog_lines()


def test_the_showroom_gets_the_same_answer_without_anything_spoken():
    # The preview bridge beside the hub calls this over the skill API. It comes
    # from the same reply() the fallback speaks, so the two cannot drift.
    skill = make_skill()
    assert skill.preview_reply("flibbertigibbet wumpus", "en-US") in _dialog_lines()
    assert skill.said == []


def test_it_sits_at_the_very_end_of_the_last_resort_band():
    # ovos-core's low band is FallbackRange(90, 101), matched as start < p <=
    # stop, so 90 itself belongs to the medium band and runs a whole pipeline
    # stage earlier than last resort. Lower numbers run first within a band,
    # and only the lowest one whose can_answer said yes fires.
    assert 90 < CustosFallbackSkill.FALLBACK_PRIORITY <= 100
    # And at the very end of it. `can_answer` here is unconditionally True, so
    # this number is the whole of the skill's politeness: anything it runs
    # ahead of is a skill that never speaks.
    #
    # This used to assert `< 100`, to beat the stock unknown-request skill at
    # 100. That trade was measured and reversed: the stock skill is installed
    # nowhere in this estate, while nine siblings register fallbacks at 96-99
    # -- joke-garden, guide, learning-lounge, language-buddy, local-pulse,
    # memory, ops-copilot, safety-guide, source-scout -- and at 95 this
    # silenced all of them. "What can you help me with today" answered "I
    # cannot answer that" with the guide skill sat behind it holding the list.
    # If the stock skill ever does turn up, the fix is not to install a second
    # skill whose whole job is saying it does not know.
    assert CustosFallbackSkill.FALLBACK_PRIORITY == 100, (
        "anything below 100 runs ahead of sibling fallbacks at 96-99, which then never speak"
    )
    # An operator override in settings is honoured only inside the band; the
    # skill must still resolve to 100 when there is none.
    assert make_skill().fallback_priority() == 100


def test_can_answer_is_unconditional():
    assert make_skill().can_answer(Message("x", {"utterances": ["anything at all"]})) is True


def test_every_locale_carries_the_dialog_english_has():
    # A missing dialog file does not fall back to English; it speaks the raw
    # dialog name, which in a room is worse than the wrong language.
    expected = {p.name for p in (LOCALE / "en-US" / "dialog").glob("*.dialog")}
    assert expected, "en-US carries no dialog at all"
    missing = {
        locale.name: sorted(expected - {p.name for p in (locale / "dialog").glob("*.dialog")})
        for locale in sorted(LOCALE.iterdir())
        if locale.is_dir()
    }
    assert not any(missing.values()), f"locales missing dialog files: {missing}"


def test_no_dialog_file_is_empty_or_untranslated_english():
    english = (LOCALE / "en-US" / "dialog" / "custos.unknown.request.dialog").read_text()
    for locale in sorted(LOCALE.iterdir()):
        if not locale.is_dir():
            continue
        text = (locale / "dialog" / "custos.unknown.request.dialog").read_text()
        assert text.strip(), f"{locale.name} dialog is empty"
        assert len(text.strip().splitlines()) >= 2, f"{locale.name} lost a variant"
        if locale.name not in {"en-US"}:
            assert text != english, f"{locale.name} is still English"


# Every language OVOS itself supports. `ovos-skill-date-time` carries the
# widest set of the core skills (including both Kabyle spellings); ovos-core
# adds nl-BE and uk-UA that no core skill ships.
OVOS_LANGUAGES = {
    "ca-ES", "cs-CZ", "da-DK", "de-DE", "en-US", "es-ES", "eu-ES", "fa-IR",
    "fr-FR", "gl-ES", "hu-HU", "it-IT", "kab", "kab-DZ", "nl-BE", "nl-NL",
    "pl-PL", "pt-BR", "pt-PT", "ru-RU", "sv-FI", "sv-SE", "tr-TR", "uk-UA",
}


def test_every_language_ovos_supports_is_carried():
    """An absent locale is not a silent no-op — it speaks its own identifier.

    Verified against a real ovos-core: booting this skill in a language with
    no locale directory makes it say the literal string
    "custos.unknown.request" out loud. So for a dialog-only skill, a shipped
    translation is strictly better than an omitted one however imperfect it
    is, and the only defensible set is every language OVOS supports.

    (This is the opposite calculus to intent files, where a phrasing nobody
    can vouch for silently matches nothing and advertises support that fails.
    This skill has no intent files.)
    """
    present = {p.name for p in LOCALE.iterdir() if p.is_dir()}
    missing = OVOS_LANGUAGES - present
    assert not missing, f"languages OVOS supports that would speak a raw identifier: {sorted(missing)}"


def test_unmatched_private_speech_is_not_written_to_logs(monkeypatch):
    from thalovant_skill_custos_fallback import LOG
    entries = []
    monkeypatch.setattr(LOG, "info", lambda *args: entries.append(args))
    skill = make_skill()
    secret = "my door code is 983472"
    assert skill.preview_reply(secret, "en-US") in _dialog_lines()
    assert entries
    assert secret not in repr(entries)
    assert "983472" not in repr(entries)
