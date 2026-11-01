CREATE TABLE IF NOT EXISTS app_users (
    user_id TEXT PRIMARY KEY,
    email TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organisations (
    organisation_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organisation_memberships (
    user_id TEXT NOT NULL REFERENCES app_users(user_id) ON DELETE CASCADE,
    organisation_id TEXT NOT NULL REFERENCES organisations(organisation_id)
        ON DELETE CASCADE,
    role TEXT NOT NULL,
    subscription TEXT NOT NULL DEFAULT 'free',
    connected_services TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, organisation_id),
    CHECK (role IN ('user', 'farmer', 'business', 'analyst', 'admin'))
);

CREATE INDEX IF NOT EXISTS idx_memberships_organisation
    ON organisation_memberships (organisation_id, user_id);