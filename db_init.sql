CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    user_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email              VARCHAR(255) UNIQUE NOT NULL,
    password_hash      VARCHAR(255) NOT NULL,
    session_token      VARCHAR(255),
    session_expires_at TIMESTAMP,
    created_at         TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projects (
    project_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    engagement_type VARCHAR(100),
    scale_tier      VARCHAR(50),
    status          VARCHAR(50) DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS project_dimensions (
    dimension_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    dimension_name  VARCHAR(100) NOT NULL,
    dimension_value TEXT,
    captured_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS modules (
    module_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    knowledge_area  VARCHAR(100) NOT NULL,
    description     TEXT,
    typical_inputs  TEXT,
    typical_outputs TEXT
);

CREATE TABLE IF NOT EXISTS roadmap_templates (
    template_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_type VARCHAR(100) NOT NULL,
    scale_tier      VARCHAR(50) NOT NULL,
    module_sequence JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS project_roadmap_items (
    roadmap_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    module_id       UUID NOT NULL REFERENCES modules(module_id),
    sequence_order  INTEGER NOT NULL,
    status          VARCHAR(50) DEFAULT 'not_started',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    module_id       UUID NOT NULL REFERENCES modules(module_id),
    artifact_type   VARCHAR(100),
    content         JSONB,
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversation_history (
    message_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    module_id   UUID NOT NULL REFERENCES modules(module_id),
    role        VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_project_module
    ON conversation_history(project_id, module_id, created_at);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_roadmap_items_updated_at
    BEFORE UPDATE ON project_roadmap_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER trg_artifacts_updated_at
    BEFORE UPDATE ON artifacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Add last_active_project_id column if it does not already exist (safe for re-runs)
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS last_active_project_id UUID REFERENCES projects(project_id);
