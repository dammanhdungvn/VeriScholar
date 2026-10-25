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

                    -- drafts table upgrades
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'drafts'
                    ) THEN
                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'drafts' AND column_name = 'template'
                        ) THEN
                            ALTER TABLE drafts ALTER COLUMN template DROP NOT NULL;
                            ALTER TABLE drafts ALTER COLUMN template SET DEFAULT 'standard';
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
                        ADD COLUMN IF NOT EXISTS google_scholar_url VARCHAR(500) NULL;
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

                END $$;
            """)
        )
        logger.info("database_schema_upgrades_ensured", dialect=dialect_name)
    elif dialect_name == "sqlite":
        try:
            # folders table upgrades
            folders_check = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='folders'")
            )
            if folders_check.scalar_one_or_none():
                res = await conn.execute(text("PRAGMA table_info(folders)"))
                f_cols = [row[1] for row in res.fetchall()]
                if "color" not in f_cols:
                    await conn.execute(
                        text(
                            "ALTER TABLE folders ADD COLUMN color VARCHAR(30) "
                            "DEFAULT '#6366f1' NOT NULL"
                        )
                    )
                if "description" not in f_cols:
                    await conn.execute(text("ALTER TABLE folders ADD COLUMN description TEXT"))

            # users table upgrades
            users_check = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            )
            if users_check.scalar_one_or_none():
                res = await conn.execute(text("PRAGMA table_info(users)"))
                u_cols = [row[1] for row in res.fetchall()]
                user_column_defs = [
                    (
                        "role",
                        "ALTER TABLE users ADD COLUMN role VARCHAR(30) "
                        "DEFAULT 'researcher' NOT NULL",
                    ),
                    ("institution", "ALTER TABLE users ADD COLUMN institution VARCHAR(255)"),
                    ("academic_rank", "ALTER TABLE users ADD COLUMN academic_rank VARCHAR(100)"),
                    ("orcid_id", "ALTER TABLE users ADD COLUMN orcid_id VARCHAR(50)"),
                    ("avatar_url", "ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)"),
                    (
                        "is_verified",
                        "ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0 NOT NULL",
                    ),
                    ("department", "ALTER TABLE users ADD COLUMN department VARCHAR(255)"),
                    ("bio", "ALTER TABLE users ADD COLUMN bio VARCHAR(1000)"),
                    (
                        "research_interests",
                        "ALTER TABLE users ADD COLUMN research_interests VARCHAR(500)",
                    ),
                    (
                        "google_scholar_url",
                        "ALTER TABLE users ADD COLUMN google_scholar_url VARCHAR(500)",
                    ),
                ]
                for col_name, sql_stmt in user_column_defs:
                    if col_name not in u_cols:
                        await conn.execute(text(sql_stmt))

            table_check = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='drafts'")
            )
            if table_check.scalar_one_or_none():
                res = await conn.execute(text("PRAGMA table_info(drafts)"))
                cols = [row[1] for row in res.fetchall()]
                if "template" not in cols:
                    await conn.execute(
                        text(
                            "ALTER TABLE drafts ADD COLUMN template VARCHAR(50) DEFAULT 'standard'"
                        )
                    )
                if "pdf_preview_storage_path" not in cols:
                    await conn.execute(
                        text("ALTER TABLE drafts ADD COLUMN pdf_preview_storage_path TEXT")
                    )
                if "last_compile_status" not in cols:
                    await conn.execute(
                        text("ALTER TABLE drafts ADD COLUMN last_compile_status VARCHAR(20)")
                    )
                if "last_compiled_at" not in cols:
                    await conn.execute(
                        text("ALTER TABLE drafts ADD COLUMN last_compiled_at TIMESTAMP")
                    )
        except Exception:
            logger.exception("sqlite_schema_upgrade_failed")
            raise
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
