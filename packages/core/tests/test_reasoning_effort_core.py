import pytest
from core.domain.value_objects.reasoning_effort import (
    map_reasoning_effort_to_provider,
)


def test_map_reasoning_effort_to_openai():
    # OpenAI mapping
    assert map_reasoning_effort_to_provider("openai", "off") == {}
    assert map_reasoning_effort_to_provider("openai", "low") == {"reasoning_effort": "low"}
    assert map_reasoning_effort_to_provider("openai", "medium") == {"reasoning_effort": "medium"}
    assert map_reasoning_effort_to_provider("openai", "high") == {"reasoning_effort": "high"}


def test_map_reasoning_effort_to_gemini():
    # Gemini thinking_config mapping
    assert map_reasoning_effort_to_provider("gemini", "off") == {"thinking_budget": 0}
    assert map_reasoning_effort_to_provider("gemini", "low") == {"thinking_budget": 1024}
    assert map_reasoning_effort_to_provider("gemini", "high") == {"thinking_budget": 16384}


def test_map_reasoning_effort_to_anthropic():
    # Anthropic thinking tokens mapping
    assert map_reasoning_effort_to_provider("anthropic", "off") == {
        "thinking": {"type": "disabled"}
    }
    assert map_reasoning_effort_to_provider("anthropic", "high") == {
        "thinking": {"type": "enabled", "budget_tokens": 32768}
    }


def test_invalid_effort_level_rejected():
    with pytest.raises(ValueError):
        map_reasoning_effort_to_provider("openai", "ultra_max")  # type: ignore
