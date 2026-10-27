"""Academic Knowledge Graph Extractor and Folder Hierarchy Services.

Provides strict 4-entity and 4-edge schema validation, canonical entity name
normalization, and hierarchical folder cycle detection for VeriScholar.
Pure domain logic: Python Standard Library + Pydantic only.
"""

from __future__ import annotations

import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

VALID_NODE_TYPES = ("Paper", "Method", "Dataset", "MetricResult")
VALID_EDGE_TYPES = ("PROPOSES", "EVALUATED_ON", "ACHIEVES", "CITES")

NodeType = Literal["Paper", "Method", "Dataset", "MetricResult"]
EdgeType = Literal["PROPOSES", "EVALUATED_ON", "ACHIEVES", "CITES"]


def normalize_canonical_name(raw_name: str) -> str:
    """Normalize entity or concept name by stripping, collapsing whitespace, and lowercasing."""
    if not raw_name:
        return ""
    return re.sub(r"\s+", " ", raw_name).strip().lower()


class MetricContextTuple(BaseModel):
    """Contextual binding tuple for MetricResult entities across papers."""

    dataset: str | None = None
    task: str | None = None
    split: str | None = None
    metric_name: str | None = None
    value: float | None = None
    unit: str | None = None


class ExtractedEntity(BaseModel):
    """An academic entity extracted from scholarly literature."""

    type: NodeType
    name: str
    description: str | None = None
    page_number: int
    context_tuple: MetricContextTuple | None = None


class ExtractedRelation(BaseModel):
    """A directed semantic relation between two academic entities."""

    source_name: str
    target_name: str
    type: EdgeType
    page_number: int


class ExtractedGraphPayload(BaseModel):
    """Container payload validating structured outputs of extracted graph elements."""

    entities: list[ExtractedEntity] = Field(default_factory=list)
    relations: list[ExtractedRelation] = Field(default_factory=list)


def detect_folder_cycle(
    folder_id: UUID,
    new_parent_id: UUID | None,
    parent_map: dict[UUID, UUID | None],
) -> bool:
    """Detect whether assigning new_parent_id to folder_id introduces a cyclic hierarchy.

    Traverses upwards from new_parent_id to root. If folder_id is encountered along
    the ancestor path, or if new_parent_id == folder_id, returns True.
    Returns False otherwise.
    """
    if new_parent_id is None:
        return False
    if new_parent_id == folder_id:
        return True

    curr: UUID | None = new_parent_id
    visited: set[UUID] = set()

    while curr is not None:
        if curr == folder_id:
            return True
        if curr in visited:
            break
        visited.add(curr)
        curr = parent_map.get(curr)

    return False
