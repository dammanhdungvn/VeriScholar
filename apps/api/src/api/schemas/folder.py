"""Pydantic schemas for Hierarchical Folders, Hierarchical RAG, and Literature Matrix (Module 4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from api.schemas.envelope import SingleResponseEnvelope
from pydantic import BaseModel, ConfigDict, Field, field_validator


class FolderCreateRequest(BaseModel):
    """Payload for creating a new research project folder."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Tên thư mục đề tài nghiên cứu"
    )
    parent_id: UUID | None = Field(None, description="UUID thư mục cha nếu tạo thư mục con")
    color: str = Field("#6366f1", max_length=30, description="Mã màu nhận diện thư mục (HEX)")
    description: str | None = Field(
        None, max_length=1000, description="Mô tả tóm tắt định hướng nghiên cứu"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Tên thư mục không được để trống")
        return cleaned


class FolderUpdateRequest(BaseModel):
    """Payload for updating folder metadata or moving in hierarchy."""

    name: str | None = Field(None, min_length=1, max_length=255)
    parent_id: UUID | None = Field(None, description="Di chuyển thư mục sang thư mục cha mới")
    color: str | None = Field(None, max_length=30)
    description: str | None = Field(None, max_length=1000)


class FolderDocumentAssignRequest(BaseModel):
    """Payload for associating or moving documents to a folder."""

    document_ids: list[UUID] = Field(
        ..., min_length=1, max_length=100, description="Danh sách UUID bài báo"
    )


class FolderResponseData(BaseModel):
    """Response payload for a research folder."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    parent_id: UUID | None = None
    color: str = "#6366f1"
    description: str | None = None
    document_count: int = 0
    subfolder_count: int = 0
    created_at: datetime
    updated_at: datetime


class FolderTreeItem(BaseModel):
    """Recursive tree item for hierarchical folder navigation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    parent_id: UUID | None = None
    color: str = "#6366f1"
    description: str | None = None
    document_count: int = 0
    subfolders: list[FolderTreeItem] = Field(default_factory=list)


class FolderSingleEnvelope(SingleResponseEnvelope[FolderResponseData]):
    """Envelope wrapping a single folder."""

    pass


class FolderTreeEnvelope(BaseModel):
    """Envelope wrapping a tree of folders."""

    success: bool = True
    data: list[FolderTreeItem]
    meta: dict[str, Any] = Field(default_factory=dict)


class SufficiencyGateSchema(BaseModel):
    """Evaluation result of evidence sufficiency."""

    is_sufficient: bool
    sufficiency_score: float
    analyzed_aspects: list[str] = Field(default_factory=list)
    missing_aspects: list[str] = Field(default_factory=list)
    recommended_search_queries: list[str] = Field(default_factory=list)
    reasoning: str


# ==============================================================================
# 2-Tier Hierarchical RAG Schemas
# ==============================================================================


class HierarchicalRagQueryRequest(BaseModel):
    """Request payload for 2-tier Hierarchical RAG search in Library."""

    query: str = Field(
        ..., min_length=3, max_length=2000, description="Nội dung câu hỏi nghiên cứu"
    )
    folder_id: UUID | None = Field(
        None, description="UUID thư mục cần tìm kiếm (None = toàn bộ thư viện)"
    )
    enable_thinking: bool = Field(True, description="Kích hoạt luồng suy luận 5.6-luna")
    stream: bool = Field(False, description="Yêu cầu truyền dòng SSE")


class HierarchicalRagQueryResponseData(BaseModel):
    """Response payload for 2-tier Hierarchical RAG."""

    answer: str
    thought: str | None = None
    tier_used: Literal["tier1_notes", "tier2_chunks", "hybrid"]
    notes_retrieved_count: int
    chunks_retrieved_count: int
    sufficiency: SufficiencyGateSchema
    citations: list[dict[str, Any]] = Field(default_factory=list)
