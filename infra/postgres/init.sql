-- VeriScholar Database Initialization Script
-- Automatically executed on first container startup by /docker-entrypoint-initdb.d/

-- 1. Enable pgvector extension for high-dimensional vector embeddings (BGE-M3 / OpenAI)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Enable uuid-ossp extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 3. Verify installed extensions
DO $$
BEGIN
    RAISE NOTICE 'VeriScholar PostgreSQL Extensions Initialized:';
    RAISE NOTICE '  - vector (pgvector)';
    RAISE NOTICE '  - uuid-ossp';
END $$;
