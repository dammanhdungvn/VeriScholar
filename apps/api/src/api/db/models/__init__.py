"""Database models re-export (19 PostgreSQL 16 + pgvector models)."""

from api.db.models.base import Base, IdentifiableTimestampedModel
from api.db.models.blob import DocumentStorageBlobModel
from api.db.models.chunk import DocumentChunkModel
from api.db.models.document import DocumentModel
from api.db.models.draft import DraftModel
from api.db.models.draft_asset import DraftAssetModel
from api.db.models.draft_message import DraftMessageModel
from api.db.models.folder import FolderModel
from api.db.models.graph import (
    FolderCommunitySummaryModel,
    GraphEdgeModel,
    GraphNodeModel,
)
from api.db.models.note import ResearchNoteModel
from api.db.models.reference import ReferenceItemModel
from api.db.models.scholar_profile import ScholarProfileModel
from api.db.models.session import (
    ResearchSessionModel,
    SessionDocumentModel,
    SessionTurnModel,
)
from api.db.models.summary import DocumentSummaryModel
from api.db.models.user import UserModel
from api.db.models.user_api_key import UserApiKeyModel

__all__ = [
    "Base",
    "IdentifiableTimestampedModel",
    "UserModel",
    "ScholarProfileModel",
    "UserApiKeyModel",
    "DocumentStorageBlobModel",
    "DocumentModel",
    "DocumentChunkModel",
    "DocumentSummaryModel",
    "ReferenceItemModel",
    "ResearchSessionModel",
    "SessionDocumentModel",
    "SessionTurnModel",
    "ResearchNoteModel",
    "FolderModel",
    "GraphNodeModel",
    "GraphEdgeModel",
    "FolderCommunitySummaryModel",
    "DraftModel",
    "DraftAssetModel",
    "DraftMessageModel",
]
