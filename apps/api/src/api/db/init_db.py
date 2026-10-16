"""Database schema initialization and idempotent DDL migration upgrades."""

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

logger = structlog.get_logger("api.db.init")


async def ensure_database_schema(conn: AsyncConnection) -> None:
    """Ensure all table columns, constraints, triggers, and indexes are up to date."""
    dialect_name = conn.dialect.name
    if dialect_name == "postgresql":
        # 1. Trigger functions
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

        # 2. Schema DDL block
        await conn.execute(
            text("""
                DO $$
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
                        ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL;
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

                    -- session_turns table creation
                    CREATE TABLE IF NOT EXISTS session_turns (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        session_id UUID NOT NULL REFERENCES research_sessions(id) ON DELETE CASCADE,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        citations JSONB NOT NULL DEFAULT '[]'::jsonb,
                        prompt_tokens INT NOT NULL DEFAULT 0,
                        completion_tokens INT NOT NULL DEFAULT 0,
                        latency_ms INT NOT NULL DEFAULT 0,
                        finish_reason VARCHAR(30) NOT NULL DEFAULT 'stop',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_session_turns_session_created 
                    ON session_turns (session_id, created_at ASC);

                    -- research_notes table creation & indexes
                    CREATE TABLE IF NOT EXISTS research_notes (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        document_id UUID NULL REFERENCES documents(id) ON DELETE SET NULL,
                        chunk_id UUID NULL REFERENCES document_chunks(id) ON DELETE SET NULL,
                        selected_text TEXT NOT NULL,
                        bounding_boxes JSONB NOT NULL DEFAULT '[]'::jsonb,
                        page_number INT NOT NULL CHECK (page_number >= 1),
                        user_note TEXT NULL,
                        tags TEXT[] NOT NULL DEFAULT '{}',
                        frozen_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
                        is_source_detached BOOLEAN NOT NULL DEFAULT FALSE,
                        version INT NOT NULL DEFAULT 1,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_research_notes_doc_fk
                        ON research_notes(document_id);
                    CREATE INDEX IF NOT EXISTS idx_research_notes_chunk_fk
                        ON research_notes(chunk_id);
                    CREATE INDEX IF NOT EXISTS idx_research_notes_user_doc
                        ON research_notes(user_id, document_id);
                    CREATE INDEX IF NOT EXISTS idx_research_notes_tags
                        ON research_notes USING gin(tags);
                    CREATE INDEX IF NOT EXISTS idx_research_notes_created
                        ON research_notes(created_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_research_notes_user_created
                        ON research_notes(user_id, created_at DESC);

                    -- note_syntheses table creation & indexes
                    CREATE TABLE IF NOT EXISTS note_syntheses (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(255) NOT NULL,
                        mode VARCHAR(50) NOT NULL CHECK (
                            mode IN ('concept_lesson', 'literature_review',
                                      'research_gap', 'active_recall_quiz')
                        ),
                        language VARCHAR(10) NOT NULL DEFAULT 'vi',
                        markdown_content TEXT NOT NULL,
                        interactive_badges JSONB NOT NULL DEFAULT '[]'::jsonb,
                        source_note_ids TEXT[] NOT NULL DEFAULT '{}',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_note_syntheses_user
                        ON note_syntheses(user_id, created_at DESC);

                    -- Ensure active_recall_quiz constraint upgrade
                    ALTER TABLE note_syntheses
                        DROP CONSTRAINT IF EXISTS note_syntheses_mode_check;
                    ALTER TABLE note_syntheses
                        DROP CONSTRAINT IF EXISTS ck_note_syntheses_valid_mode;
                    ALTER TABLE note_syntheses ADD CONSTRAINT ck_note_syntheses_valid_mode CHECK (
                        mode IN ('concept_lesson', 'literature_review',
                                      'research_gap', 'active_recall_quiz')
                    );

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
                        BEFORE UPDATE OF document_id ON research_notes
                        FOR EACH ROW EXECUTE FUNCTION handle_note_source_detached();
                    END IF;

                    -- Triggers for note_syntheses
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_note_syntheses_updated_at'
                    ) THEN
                        CREATE TRIGGER trg_note_syntheses_updated_at
                        BEFORE UPDATE ON note_syntheses
                        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                    END IF;

                END $$;
            """)
        )
        logger.info("database_schema_upgrades_ensured", dialect=dialect_name)
