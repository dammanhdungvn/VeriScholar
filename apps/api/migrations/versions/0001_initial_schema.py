"""Initial schema migration: 3NF database layout for VeriScholar.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-04 10:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    uuid_def = sa.text("uuid_generate_v4()")
    now_def = sa.func.now()

    # 2. Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="researcher"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )

    # 3. Storage Blobs
    op.create_table(
        "document_storage_blobs",
        sa.Column("sha256_hash", sa.String(64), primary_key=True),
        sa.Column("storage_path", sa.String(512), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column(
            "content_type",
            sa.String(100),
            nullable=False,
            server_default="application/pdf",
        ),
        sa.Column("ref_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )

    # 4. Folders
    op.create_table(
        "folders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("folders.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_folders_user_id", "folders", ["user_id"])
    op.create_index("ix_folders_parent_id", "folders", ["parent_id"])

    # 5. Documents
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "folder_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("folders.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "blob_hash",
            sa.String(64),
            sa.ForeignKey("document_storage_blobs.sha256_hash"),
            nullable=False,
        ),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("author", sa.String(512), nullable=True),
        sa.Column("doi", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("page_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_starred", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_persistent", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_folder_id", "documents", ["folder_id"])
    op.create_index("ix_documents_blob_hash", "documents", ["blob_hash"])
    op.create_index("ix_documents_status", "documents", ["status"])

    # 6. Document Chunks
    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("bounding_boxes", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_chunks_doc_id", "document_chunks", ["document_id"])
    op.create_index("ix_chunks_page", "document_chunks", ["document_id", "page_number"])

    # 7. Document Summaries
    op.create_table(
        "document_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("overview", sa.Text(), nullable=False),
        sa.Column("methodology", sa.Text(), nullable=False),
        sa.Column("key_findings", sa.Text(), nullable=False),
        sa.Column("contributions", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("limitations", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )

    # 8. Reference Items & Citation Edges
    op.create_table(
        "reference_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ref_id", sa.String(64), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authors", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(255), nullable=True),
        sa.Column("doi", sa.String(255), nullable=True),
        sa.Column("arxiv_id", sa.String(100), nullable=True),
        sa.Column(
            "has_open_access_pdf",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("pdf_download_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_reference_items_doc_id", "reference_items", ["document_id"])
    op.create_index("ix_reference_items_doi", "reference_items", ["doi"])

    op.create_table(
        "citation_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "source_doc_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_doc_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("relation", sa.String(50), nullable=False, server_default="CITES"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_citation_edges_source", "citation_edges", ["source_doc_id"])
    op.create_index("ix_citation_edges_target", "citation_edges", ["target_doc_id"])

    # 9. Research Sessions & Chat Turns
    op.create_table(
        "research_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_research_sessions_user_id", "research_sessions", ["user_id"])

    op.create_table(
        "session_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("research_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.UniqueConstraint("session_id", "document_id", name="uq_session_document"),
    )

    op.create_table(
        "session_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("research_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "grounding_citations",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_session_turns_session_idx", "session_turns", ["session_id", "turn_index"])

    # 10. Research Notes & Syntheses
    op.create_table(
        "research_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "chunk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_chunks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("selected_text", sa.Text(), nullable=False),
        sa.Column("bounding_boxes", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("user_note", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("frozen_snapshot", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_research_notes_user_id", "research_notes", ["user_id"])
    op.create_index("ix_research_notes_doc_id", "research_notes", ["document_id"])

    op.create_table(
        "note_syntheses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_title", sa.String(255), nullable=False),
        sa.Column("mode", sa.String(50), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="vi"),
        sa.Column("synthesized_markdown", sa.Text(), nullable=False),
        sa.Column(
            "interactive_badges",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_note_syntheses_user_id", "note_syntheses", ["user_id"])

    # 11. Drafts, Comments & SAFE Verifications
    op.create_table(
        "drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("format", sa.String(50), nullable=False, server_default="latex"),
        sa.Column("template", sa.String(50), nullable=False, server_default="ieee_conference"),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_compiled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_compile_status", sa.String(50), nullable=True),
        sa.Column("pdf_preview_storage_path", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_drafts_user_id", "drafts", ["user_id"])

    op.create_table(
        "draft_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "draft_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("drafts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("author_name", sa.String(255), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("selected_text", sa.Text(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_draft_comments_draft_id", "draft_comments", ["draft_id"])

    op.create_table(
        "draft_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column(
            "draft_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("drafts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("selected_text", sa.Text(), nullable=False),
        sa.Column("claims", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("total_claims", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("supported_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("contradicted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("not_enough_info_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_draft_verifications_draft_id", "draft_verifications", ["draft_id"])

    # 12. Shares
    op.create_table(
        "shares",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=uuid_def),
        sa.Column("token", sa.String(64), unique=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("allow_export", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now_def),
    )
    op.create_index("ix_shares_token", "shares", ["token"])
    op.create_index("ix_shares_user_id", "shares", ["user_id"])
    op.create_index("ix_shares_document_id", "shares", ["document_id"])


def downgrade() -> None:
    op.drop_table("shares")
    op.drop_table("draft_verifications")
    op.drop_table("draft_comments")
    op.drop_table("drafts")
    op.drop_table("note_syntheses")
    op.drop_table("research_notes")
    op.drop_table("session_turns")
    op.drop_table("session_documents")
    op.drop_table("research_sessions")
    op.drop_table("citation_edges")
    op.drop_table("reference_items")
    op.drop_table("document_summaries")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("folders")
    op.drop_table("document_storage_blobs")
    op.drop_table("users")
