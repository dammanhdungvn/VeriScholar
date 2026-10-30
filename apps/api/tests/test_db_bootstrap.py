import pytest
from api.db.init_db import ensure_database_schema
from api.db.session import engine
from sqlalchemy import text


@pytest.mark.asyncio
async def test_ensure_database_schema_runs_idempotently():
    """Verify that ensure_database_schema runs consecutively without raising exceptions."""
    if engine.dialect.name != "postgresql":
        pytest.skip("Bootstrap test requires PostgreSQL with pgvector")

    async with engine.begin() as conn:
        await ensure_database_schema(conn)
        await ensure_database_schema(conn)  # 2nd run to verify idempotency

        # Verify 19 tables exist
        res = await conn.execute(
            text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        )
        tables = {row[0] for row in res.fetchall()}
        required_tables = {
            "users",
            "scholar_profiles",
            "user_api_keys",
            "document_storage_blobs",
            "documents",
            "document_chunks",
            "document_summaries",
            "reference_items",
            "research_sessions",
            "session_documents",
            "session_turns",
            "research_notes",
            "folders",
            "graph_nodes",
            "graph_edges",
            "folder_community_summaries",
            "drafts",
            "draft_assets",
            "draft_messages",
            "wiki_pages",
        }
        missing = required_tables - tables
        assert not missing, f"Missing required tables in schema: {missing}"
    await engine.dispose()
