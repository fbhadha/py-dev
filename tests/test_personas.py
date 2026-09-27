"""The pack's fixed personas are ADK UserPersona objects, and every one ends the conversation."""

import json
from pathlib import Path

import pytest

PERSONAS = "skills/pack-adk/references/personas.json"
FIXED_LIST = ["PLAIN", "VAGUE", "HURRIED", "SCEPTICAL", "WANDERER", "CHANGER"]
BEHAVIOUR_KEYS = {"name", "description", "behavior_instructions", "violation_rubrics"}


@pytest.fixture
def personas(root: Path) -> list[dict]:
    return json.loads((root / PERSONAS).read_text(encoding="utf-8"))["personas"]


def test_six_in_the_fixed_order(personas: list[dict]) -> None:
    assert [p["id"] for p in personas] == FIXED_LIST


@pytest.mark.parametrize("persona_id", FIXED_LIST)
def test_ends_the_conversation(personas: list[dict], persona_id: str) -> None:
    persona = next(p for p in personas if p["id"] == persona_id)
    assert any(
        "{{ stop_signal }}" in line
        for behaviour in persona["behaviors"]
        for line in behaviour["behavior_instructions"]
    )


@pytest.mark.parametrize("persona_id", FIXED_LIST)
def test_in_adk_shape(personas: list[dict], persona_id: str) -> None:
    persona = next(p for p in personas if p["id"] == persona_id)
    assert {"id", "description", "behaviors"} <= set(persona)
    assert all(set(b) >= BEHAVIOUR_KEYS for b in persona["behaviors"])
