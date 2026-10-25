"""Database schema initialization and idempotent DDL migration upgrades."""

import api.db.models as _models  # noqa: F401
import structlog
from api.db.models.base import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

logger = structlog.get_logger("api.db.init")


async def ensure_database_schema(conn: AsyncConnection) -> None:
    """Ensure all 18 tables, columns, constraints, triggers, and vector/GIN indexes exist."""
    dialect_name = conn.dialect.name
    if dialect_name == "postgresql":
        # 1. Enable pgvector extension (fail-fast if extension is missing)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # 2. Create all 18 tables registered on Base.metadata idempotently
        await conn.run_sync(Base.metadata.create_all)

        # 3. Trigger functions for OCC and source detachment
        await conn.execute(
            text("""
                CREATE OR REPLACE FUNCTION handle_occ_and_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    NEW.version = OLD.version + 1;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )

        await conn.execute(
            text("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )

        await conn.execute(
            text("""
                CREATE OR REPLACE FUNCTION handle_note_source_detached()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF OLD.document_id IS NOT NULL AND NEW.document_id IS NULL THEN
                        NEW.is_source_detached = TRUE;
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )

        # 4. Idempotent schema DDL upgrades, triggers, and vector/GIN indexes
        await conn.execute(
            text("""
                DO $$
                BEGIN
                    -- folders table upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'folders'
                    ) THEN
                        ALTER TABLE folders 
                        ADD COLUMN IF NOT EXISTS color VARCHAR(30) DEFAULT '#6366f1' NOT NULL,
                        ADD COLUMN IF NOT EXISTS description TEXT NULL;
                    END IF;

                    -- drafts table upgrades & OCC trigger
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'drafts'
                    ) THEN
                        ALTER TABLE drafts
                        ADD COLUMN IF NOT EXISTS bib_content TEXT DEFAULT '' NOT NULL,
                        ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1 NOT NULL,
                        ADD COLUMN IF NOT EXISTS previous_snapshot JSONB NULL,
                        ADD COLUMN IF NOT EXISTS pdf_preview_storage_path VARCHAR(500) NULL;

                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'drafts' AND column_name = 'template'
                        ) THEN
                            ALTER TABLE drafts ALTER COLUMN template DROP NOT NULL;
                            ALTER TABLE drafts ALTER COLUMN template SET DEFAULT 'standard';
                        END IF;

                        IF NOT EXISTS (
                            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_drafts_occ'
                        ) THEN
                            CREATE TRIGGER trg_drafts_occ
                            BEFORE UPDATE ON drafts
                            FOR EACH ROW EXECUTE FUNCTION handle_occ_and_timestamp();
                        END IF;
                    END IF;

                    -- users table upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'users'
                    ) THEN
                        ALTER TABLE users 
                        ADD COLUMN IF NOT EXISTS role VARCHAR(30) DEFAULT 'researcher' NOT NULL,
                        ADD COLUMN IF NOT EXISTS institution VARCHAR(255) NULL,
                        ADD COLUMN IF NOT EXISTS academic_rank VARCHAR(100) NULL,
                        ADD COLUMN IF NOT EXISTS orcid_id VARCHAR(50) NULL,
                        ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500) NULL,
                        ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL,
                        ADD COLUMN IF NOT EXISTS department VARCHAR(255) NULL,
                        ADD COLUMN IF NOT EXISTS bio VARCHAR(1000) NULL,
                        ADD COLUMN IF NOT EXISTS research_interests VARCHAR(500) NULL,
                        ADD COLUMN IF NOT EXISTS google_scholar_url VARCHAR(500) NULL,
                        ADD COLUMN IF NOT EXISTS theme_preference VARCHAR(20)
                            DEFAULT 'system' NOT NULL,
                        ADD COLUMN IF NOT EXISTS byok_api_key_encrypted TEXT NULL;
                    END IF;

                    -- documents upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'documents'
                    ) THEN
                        ALTER TABLE documents
                        ADD COLUMN IF NOT EXISTS is_starred BOOLEAN DEFAULT FALSE NOT NULL,
                        ADD COLUMN IF NOT EXISTS access_status VARCHAR(30)
                            DEFAULT 'open_access_pdf' NOT NULL;
                    END IF;

                    -- document_chunks upgrades (user_id, content_tsv, embedding vector(1536))
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'document_chunks'
                    ) THEN
                        ALTER TABLE document_chunks
                        ADD COLUMN IF NOT EXISTS user_id UUID
                            REFERENCES users(id) ON DELETE CASCADE,
                        ADD COLUMN IF NOT EXISTS content_tsv TSVECTOR NULL;

                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'document_chunks'
                              AND column_name = 'embedding'
                              AND udt_name != 'vector'
                        ) THEN
                            ALTER TABLE document_chunks DROP COLUMN embedding;
                            ALTER TABLE document_chunks ADD COLUMN embedding vector(1536) NULL;
                        END IF;
                    END IF;

                    -- document_summaries & reference_items multi-tenant user_id upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'document_summaries'
                    ) THEN
                        ALTER TABLE document_summaries
                        ADD COLUMN IF NOT EXISTS user_id UUID
                            REFERENCES users(id) ON DELETE CASCADE;
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'reference_items'
                    ) THEN
                        ALTER TABLE reference_items
                        ADD COLUMN IF NOT EXISTS user_id UUID
                            REFERENCES users(id) ON DELETE CASCADE;
                    END IF;

                    -- research_sessions upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'research_sessions'
                    ) THEN
                        ALTER TABLE research_sessions 
                        ADD COLUMN IF NOT EXISTS active_document_id UUID 
                            REFERENCES documents(id) ON DELETE SET NULL,
                        ADD COLUMN IF NOT EXISTS viewport_state JSONB 
                            DEFAULT '{"page": 1, "zoom_ratio": 1.0, "scroll_top": 0.0}'::jsonb 
                            NOT NULL,
                        ADD COLUMN IF NOT EXISTS active_tab VARCHAR(30) 
                            DEFAULT 'chat' NOT NULL,
                        ADD COLUMN IF NOT EXISTS is_archived BOOLEAN 
                            DEFAULT FALSE NOT NULL,
                        ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE NULL;

                        CREATE INDEX IF NOT EXISTS idx_sessions_user_archived 
                        ON research_sessions (user_id, is_archived, updated_at);
                    END IF;

                    -- session_documents upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'session_documents'
                    ) THEN
                        ALTER TABLE session_documents
                        ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0 NOT NULL;

                        CREATE INDEX IF NOT EXISTS idx_session_docs_document 
                        ON session_documents (document_id);
                    END IF;

                    -- session_turns upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'session_turns'
                    ) THEN
                        ALTER TABLE session_turns
                        ADD COLUMN IF NOT EXISTS trace_id VARCHAR(64) NULL;

                        CREATE INDEX IF NOT EXISTS idx_session_turns_session_created 
                        ON session_turns (session_id, created_at ASC);
                    END IF;

                    -- Triggers for research_notes
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_research_notes_occ'
                    ) THEN
                        CREATE TRIGGER trg_research_notes_occ
                        BEFORE UPDATE ON research_notes
                        FOR EACH ROW EXECUTE FUNCTION handle_occ_and_timestamp();
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_research_notes_detached'
                    ) THEN
                        CREATE TRIGGER trg_research_notes_detached
                        BEFORE UPDATE ON research_notes
                        FOR EACH ROW EXECUTE FUNCTION handle_note_source_detached();
                    END IF;
                END $$;
            """)
        )

        # 5. Create HNSW vector & GIN full-text indexes idempotently
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw "
                "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_graph_nodes_embedding_hnsw "
                "ON graph_nodes USING hnsw (embedding vector_cosine_ops);"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_document_chunks_tsv "
                "ON document_chunks USING gin (content_tsv);"
            )
        )
        logger.info("database_schema_upgrades_ensured", dialect=dialect_name)
    else:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("database_schema_upgrades_ensured", dialect=dialect_name)


async def run_standalone_migrations() -> None:
    """Run idempotent database schema migrations directly from CLI / CD pipeline."""
    from api.db.session import engine

    logger.info("starting_standalone_database_migrations")
    async with engine.begin() as conn:
        await ensure_database_schema(conn)
    await engine.dispose()
    logger.info("standalone_database_migrations_completed_successfully")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_standalone_migrations())
