"""Pydantic schemas for research sessions (Module 1)."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from api.schemas.envelope import PaginatedResponseEnvelope, SingleResponseEnvelope
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ViewportStateSchema(BaseModel):
    """Schema representing the viewport scroll, zoom, and active page."""

    model_config = ConfigDict(from_attributes=True)

    page: int = Field(default=1, ge=1, description="1-indexed active PDF page")
    zoom_ratio: float = Field(default=1.0, gt=0.0, description="Visual zoom scale factor")
    scroll_top: float = Field(
        default=0.0, ge=0.0, description="Vertical scroll offset position in pixels"
    )


class SessionDocumentItem(BaseModel):
    """Embedded document metadata item within a session response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None = None
    filename: str
    status: str
    file_size_bytes: int
    added_at: datetime
    display_order: int


class SessionCreateRequest(BaseModel):
    """Payload for creating a new research session."""

    title: str | None = Field(
        default=None,
        max_length=255,
        description=(
            "Tiêu đề phiên nghiên cứu (tùy chọn). Nếu không truyền, hệ thống tự động "
            "đặt tên theo bài báo đầu tiên hoặc thời gian khởi tạo."
        ),
        examples=["Nghiên cứu Kiến trúc Attention & Transformer"],
    )
    initial_document_ids: list[UUID] = Field(
        default_factory=list,
        description="Danh sách tài liệu ban đầu nạp vào phiên (tối đa 5 bài)",
        examples=[["c7a2e8c5-9231-419b-a0eb-4a1796d8e05c"]],
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Strip and validate title non-empty if provided."""
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title must not be empty or contain only whitespace")
        if len(cleaned) > 255:
            raise ValueError("Title must not exceed 255 characters")
        return cleaned


class SessionResponseData(BaseModel):
    """Schema for research session response payload."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    document_ids: list[UUID]
    active_document_id: UUID | None
    viewport_state: ViewportStateSchema
    active_tab: str
    is_archived: bool
    version: int
    message_count: int = 0
    documents: list[SessionDocumentItem] | None = None
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class SessionSingleEnvelope(SingleResponseEnvelope[SessionResponseData]):
    """Standard API envelope wrapping a single research session."""

    pass


class SessionHistoryItem(BaseModel):
    """Item for Sidebar History list."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    document_count: int
    active_tab: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class SessionHistoryEnvelope(PaginatedResponseEnvelope[SessionHistoryItem]):
    """Paginated collection envelope for session sidebar history."""

    pass


class SessionUpdateMetadataRequest(BaseModel):
    """Payload for updating session metadata (title) with OCC."""

    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề phiên nghiên cứu")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title must not be empty or contain only whitespace")
        if len(cleaned) > 255:
            raise ValueError("Title must not exceed 255 characters")
        return cleaned


class SessionUpdateViewportRequest(BaseModel):
    """Payload for saving active viewport state and active tab with OCC."""

    active_document_id: UUID | None = Field(
        None, description="Tài liệu đang mở trên Canvas PDF Viewer"
    )
    viewport_state: ViewportStateSchema = Field(
        ..., description="Vị trí cuộn trang, trang hiện tại, tỉ lệ zoom"
    )
    active_tab: Literal["chat", "notes", "summary", "graph", "draft"] = Field(
        "chat", description="Tab đang kích hoạt trên thanh công cụ"
    )


class SessionAddDocumentRequest(BaseModel):
    """Payload for adding a document into an existing session."""

    source_type: Literal["document_id", "url"] = Field(
        ..., description="Phương thức nạp tài liệu: document_id (đã có) hoặc url (tải về)"
    )
    document_id: UUID | None = Field(None, description="UUID bài báo trong thư viện cá nhân")
    url: str | None = Field(None, description="Đường dẫn URL bài báo trực tuyến (arXiv, PubMed)")
    title: str | None = Field(None, max_length=255, description="Tiêu đề tùy chọn khi nạp qua URL")

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip()
            if not cleaned.startswith(("http://", "https://")):
                raise ValueError("URL must start with http:// or https://")
            return cleaned
        return None


class CitationItemSchema(BaseModel):
    """Schema for citation reference with bounding box."""

    model_config = ConfigDict(from_attributes=True)

    citation_id: str
    document_id: UUID
    document_title: str
    page_number: int
    bounding_boxes: list[list[float]] = Field(default_factory=list)
    score: float = 1.0


class SessionTurnItem(BaseModel):
    """Schema for a single chat turn in research session."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    question: str
    answer: str
    citations: list[CitationItemSchema] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    finish_reason: str = "stop"
    created_at: datetime


class SessionTurnListEnvelope(PaginatedResponseEnvelope[SessionTurnItem]):
    """Paginated collection envelope for session chat history."""

    pass


class SessionChatMessageRequest(BaseModel):
    """Request payload for sending question and streaming response in session."""

    question: str = Field(..., min_length=1, max_length=4000, description="Nội dung câu hỏi")
    stream: bool = Field(True, description="Kích hoạt truyền dòng Server-Sent Events (SSE)")
    scope: Literal["multi_paper", "single_paper"] = Field(
        "multi_paper",
        description="Phạm vi tra cứu: toàn bộ bài báo trong phiên hoặc đào sâu 1 bài",
    )
    focused_document_id: UUID | None = Field(
        None, description="UUID bài báo trọng tâm khi scope=single_paper"
    )
    enable_thinking: bool = Field(
        False, description="Kích hoạt cơ chế suy luận phản biện chuyên sâu (Thinking Mode)"
    )
    interactive_response: dict[str, Any] | None = Field(
        default=None,
        description="Dữ liệu phản hồi tùy chọn (persona_id, quiz) khi chọn thẻ AT-CoT",
    )
