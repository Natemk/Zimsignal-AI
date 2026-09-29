-- Migration: 001_source_registry.sql
-- Description: Establishes data provenance and ingestion policies for all external sources

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS source_registry (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    base_url VARCHAR(512) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'api', 'scrape', 'feed', 'upload', 'mcp'
    publisher VARCHAR(255) NOT NULL,
    source_tier SMALLINT NOT NULL CHECK (source_tier IN (1, 2, 3)), -- 1=Official, 2=Verified, 3=Unverified
    access_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    refresh_cron VARCHAR(100),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_success_at TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookup by source type and tier
CREATE INDEX idx_source_registry_tier_type ON source_registry (source_tier, source_type);