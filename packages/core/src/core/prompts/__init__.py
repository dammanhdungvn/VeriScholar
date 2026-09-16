"""Prompt Management Subsystem for VeriScholar."""

from core.prompts.template import (
    PromptMetadata,
    PromptRegistry,
    PromptTemplate,
    default_registry,
)

__all__ = [
    "PromptMetadata",
    "PromptRegistry",
    "PromptTemplate",
    "default_registry",
]
