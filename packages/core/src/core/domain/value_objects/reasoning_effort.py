"""Vendor-agnostic Reasoning Effort Value Object & Provider Parameter Mapping."""

from typing import Any, Literal

ReasoningEffortLevel = Literal["off", "low", "medium", "high", "light", "extra_high"]

VALID_REASONING_EFFORT_LEVELS: frozenset[str] = frozenset(
    {"off", "low", "medium", "high", "light", "extra_high"}
)


def map_reasoning_effort_to_provider(provider: str, level: str) -> dict[str, Any]:
    """Map a vendor-agnostic ReasoningEffortLevel to the target LLM provider SDK parameters.

    Supported providers:
    - openai (e.g. 5.6-luna, o1, o3-mini)
    - gemini (thinking_budget)
    - anthropic (thinking budget_tokens)
    - dmr / local (thinking intensity)
    """
    if level not in VALID_REASONING_EFFORT_LEVELS:
        valid_opts = sorted(VALID_REASONING_EFFORT_LEVELS)
        raise ValueError(f"Invalid reasoning effort level '{level}'. Must be one of: {valid_opts}")

    # Canonical normalization
    norm_level = level
    if level == "light":
        norm_level = "off"
    elif level == "extra_high":
        norm_level = "high"

    norm_provider = (provider or "").strip().lower()

    if norm_provider in ("openai", "azure_openai"):
        if norm_level == "off":
            return {}
        return {"reasoning_effort": norm_level}

    if norm_provider in ("gemini", "google"):
        budgets = {
            "off": 0,
            "low": 1024,
            "medium": 4096,
            "high": 16384,
        }
        return {"thinking_budget": budgets[norm_level]}

    if norm_provider in ("anthropic", "claude"):
        if norm_level == "off":
            return {"thinking": {"type": "disabled"}}
        token_budgets = {
            "low": 2048,
            "medium": 8192,
            "high": 32768,
        }
        return {"thinking": {"type": "enabled", "budget_tokens": token_budgets[norm_level]}}

    # Default / Local / Docker Model Runner fallback
    if norm_level == "off":
        return {"thinking": False}
    return {"thinking": True, "thinking_intensity": norm_level}
