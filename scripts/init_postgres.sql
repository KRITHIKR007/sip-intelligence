-- =============================================================================
-- SIP Intelligence Platform — PostgreSQL Initialization
-- =============================================================================
-- This runs automatically when the PostgreSQL container starts for the first time.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";    -- pgvector
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- trigram similarity for fuzzy search

-- Create schemas
CREATE SCHEMA IF NOT EXISTS sip;

-- Grant permissions
GRANT ALL ON SCHEMA sip TO sip_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA sip GRANT ALL ON TABLES TO sip_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA sip GRANT ALL ON SEQUENCES TO sip_user;

