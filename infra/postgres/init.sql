-- VeriScholar Production Database Initialization Script (PostgreSQL 18 + pgvector)
-- Automatically executed on first container startup by /docker-entrypoint-initdb.d/

-- ============================================================================
-- 1. EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- 2. TRIGGER FUNCTIONS
-- ============================================================================

-- OCC (Optimistic Concurrency Control) & Timestamp updater
CREATE OR REPLACE FUNCTION handle_occ_and_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version = OLD.version + 1;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- General timestamp updater
CREATE OR REPLACE FUNCTION handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 3. TABLES (3NF Schema)
-- ============================================================================

-- 3.1. Users & Identities
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'researcher',
    google_id VARCHAR(255) UNIQUE,
    avatar_url VARCHAR(512),
    token_quota INTEGER NOT NULL DEFAULT 200000,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    storage_quota_bytes BIGINT NOT NULL DEFAULT 1073741824,
    storage_used_bytes BIGINT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION handle_updated_at();


-- 3.2. Content-Addressable Storage (CAS) Blobs
CREATE TABLE IF NOT EXISTS document_storage_blobs (
    sha256_hash VARCHAR(64) PRIMARY KEY,
    storage_path VARCHAR(512) NOT NULL,
    byte_size BIGINT NOT NULL,
    content_type VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    ref_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.3. Folders (Hierarchical Research Classification)
CREATE TABLE IF NOT EXISTS folders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES folders(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_folders_user_parent_name
ON folders (user_id, COALESCE(parent_id, '00000000-0000-0000-0000-000000000000'::uuid), name);

CREATE INDEX IF NOT EXISTS ix_folders_user_id ON folders(user_id);
CREATE INDEX IF NOT EXISTS ix_folders_parent_id ON folders(parent_id);

CREATE TRIGGER trg_folders_updated_at
BEFORE UPDATE ON folders
FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

-- 3.4. Documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    folder_id UUID REFERENCES folders(id) ON DELETE SET NULL,
    blob_hash VARCHAR(64) NOT NULL REFERENCES document_storage_blobs(sha256_hash),
    title VARCHAR(512) NOT NULL,
    author VARCHAR(512),
    doi VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    page_count INTEGER NOT NULL DEFAULT 0,
    is_starred BOOLEAN NOT NULL DEFAULT FALSE,
    is_persistent BOOLEAN NOT NULL DEFAULT TRUE,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS ix_documents_folder_id ON documents(folder_id);
CREATE INDEX IF NOT EXISTS ix_documents_blob_hash ON documents(blob_hash);
CREATE INDEX IF NOT EXISTS ix_documents_status ON documents(status);

CREATE TRIGGER trg_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

-- 3.5. Document Chunks & High-Dimensional Vectors
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    bounding_boxes JSONB NOT NULL DEFAULT '[]'::jsonb,
    token_count INTEGER NOT NULL DEFAULT 0,
    embedding vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_chunks_doc_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS ix_chunks_page ON document_chunks(document_id, page_number);

-- Full-Text Sparse Search Index (GIN)
CREATE INDEX IF NOT EXISTS ix_chunks_fts ON document_chunks USING gin(to_tsvector('simple', content));

-- Dense Vector Search Index (HNSW with Cosine Metric)
CREATE INDEX IF NOT EXISTS ix_chunks_embedding_hnsw
ON document_chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 3.6. Document Summaries (3-point Overview, Methodology, Findings)
CREATE TABLE IF NOT EXISTS document_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    overview TEXT NOT NULL,
    methodology TEXT NOT NULL,
    key_findings TEXT NOT NULL,
    contributions JSONB NOT NULL DEFAULT '{}'::jsonb,
    limitations JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3.7. Reference Items & Academic Citations
CREATE TABLE IF NOT EXISTS reference_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ref_id VARCHAR(64) NOT NULL,
    title TEXT NOT NULL,
    authors JSONB NOT NULL DEFAULT '[]'::jsonb,
    year INTEGER,
    venue VARCHAR(255),
    doi VARCHAR(255),
    arxiv_id VARCHAR(100),
    has_open_access_pdf BOOLEAN NOT NULL DEFAULT FALSE,
    pdf_download_url VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_reference_items_doc_id ON reference_items(document_id);
CREATE INDEX IF NOT EXISTS ix_reference_items_doi ON reference_items(doi);

CREATE TABLE IF NOT EXISTS citation_edges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_doc_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    relation VARCHAR(50) NOT NULL DEFAULT 'CITES',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_citation_edges_source ON citation_edges(source_doc_id);
CREATE INDEX IF NOT EXISTS ix_citation_edges_target ON citation_edges(target_doc_id);

-- 3.8. Research Sessions & Chat Turns
CREATE TABLE IF NOT EXISTS research_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_research_sessions_user_id ON research_sessions(user_id);

CREATE TRIGGER trg_research_sessions_occ
BEFORE UPDATE ON research_sessions
FOR EACH ROW EXECUTE FUNCTION handle_occ_and_timestamp();

CREATE TABLE IF NOT EXISTS session_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES research_sessions(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(session_id, document_id)
);

CREATE TABLE IF NOT EXISTS session_turns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES research_sessions(id) ON DELETE CASCADE,
    turn_index INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    grounding_citations JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_session_turns_session_idx ON session_turns(session_id, turn_index);

-- 3.9. Research Notes & Syntheses
CREATE TABLE IF NOT EXISTS research_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    chunk_id UUID REFERENCES document_chunks(id) ON DELETE SET NULL,
    selected_text TEXT NOT NULL,
    bounding_boxes JSONB NOT NULL DEFAULT '[]'::jsonb,
    page_number INTEGER NOT NULL,
    user_note TEXT NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    frozen_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_research_notes_user_id ON research_notes(user_id);
CREATE INDEX IF NOT EXISTS ix_research_notes_doc_id ON research_notes(document_id);

CREATE TRIGGER trg_research_notes_occ
BEFORE UPDATE ON research_notes
FOR EACH ROW EXECUTE FUNCTION handle_occ_and_timestamp();

CREATE TABLE IF NOT EXISTS note_syntheses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_title VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'vi',
    synthesized_markdown TEXT NOT NULL,
    interactive_badges JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_note_syntheses_user_id ON note_syntheses(user_id);

-- 3.10. Academic Drafts, Comments & SAFE Fact-Checking
CREATE TABLE IF NOT EXISTS drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    format VARCHAR(50) NOT NULL DEFAULT 'latex',
    template VARCHAR(50) NOT NULL DEFAULT 'ieee_conference',
    content TEXT NOT NULL DEFAULT '',
    version INTEGER NOT NULL DEFAULT 1,
    last_compiled_at TIMESTAMPTZ,
    last_compile_status VARCHAR(50),
    pdf_preview_storage_path VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_drafts_user_id ON drafts(user_id);

CREATE TRIGGER trg_drafts_occ
BEFORE UPDATE ON drafts
FOR EACH ROW EXECUTE FUNCTION handle_occ_and_timestamp();

CREATE TABLE IF NOT EXISTS draft_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_id UUID NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    author_name VARCHAR(255) NOT NULL,
    line_number INTEGER NOT NULL,
    selected_text TEXT NOT NULL,
    comment TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_draft_comments_draft_id ON draft_comments(draft_id);

CREATE TRIGGER trg_draft_comments_updated_at
BEFORE UPDATE ON draft_comments
FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

CREATE TABLE IF NOT EXISTS draft_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_id UUID NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    selected_text TEXT NOT NULL,
    claims JSONB NOT NULL DEFAULT '[]'::jsonb,
    total_claims INTEGER NOT NULL DEFAULT 0,
    supported_count INTEGER NOT NULL DEFAULT 0,
    contradicted_count INTEGER NOT NULL DEFAULT 0,
    not_enough_info_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_draft_verifications_draft_id ON draft_verifications(draft_id);

-- 3.11. Public Shares & Revocations
CREATE TABLE IF NOT EXISTS shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    allow_export BOOLEAN NOT NULL DEFAULT TRUE,
    view_count INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_shares_token ON shares(token);
CREATE INDEX IF NOT EXISTS ix_shares_user_id ON shares(user_id);
CREATE INDEX IF NOT EXISTS ix_shares_document_id ON shares(document_id);

-- 3.12. Research Organizations / Labs & Members
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    storage_quota_bytes BIGINT NOT NULL DEFAULT 10737418240,
    storage_used_bytes BIGINT NOT NULL DEFAULT 0,
    token_quota INTEGER NOT NULL DEFAULT 1000000,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_organizations_slug ON organizations(slug);

CREATE TRIGGER trg_organizations_updated_at
BEFORE UPDATE ON organizations
FOR EACH ROW EXECUTE FUNCTION handle_updated_at();

CREATE TABLE IF NOT EXISTS organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_organization_members_org_user UNIQUE (organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS ix_organization_members_org ON organization_members(organization_id);
CREATE INDEX IF NOT EXISTS ix_organization_members_user ON organization_members(user_id);

-- 3.13. Usage Records & Token Cost Control Tracking
CREATE TABLE IF NOT EXISTS usage_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL,
    model_name VARCHAR(100),
    tokens_prompt INTEGER NOT NULL DEFAULT 0,
    tokens_completion INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    cost_cents NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    bytes_transferred BIGINT NOT NULL DEFAULT 0,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_usage_records_user_id ON usage_records(user_id);
CREATE INDEX IF NOT EXISTS ix_usage_records_activity ON usage_records(activity_type);
CREATE INDEX IF NOT EXISTS ix_usage_records_created_at ON usage_records(created_at);

-- ============================================================================
-- 4. VERIFICATION LOG
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'VeriScholar PostgreSQL 18 Schema and Extensions Initialized Successfully:';
    RAISE NOTICE '  - Extensions: vector, uuid-ossp, pg_trgm';
    RAISE NOTICE '  - 19 Relational Tables in 3NF with Cascade and OCC Triggers';
    RAISE NOTICE '  - Organizations, Usage Records, and Token Cost Control Configured';
END $$;

