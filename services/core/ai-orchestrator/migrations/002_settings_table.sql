-- ============================================================================
-- AI Security Lab v4.0 - Settings Management
-- TimescaleDB Migration 002
-- ============================================================================

-- System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    value_type TEXT NOT NULL,
    default_value JSONB,
    is_secret BOOLEAN DEFAULT FALSE,
    is_readonly BOOLEAN DEFAULT FALSE,
    validation_rules JSONB DEFAULT '{}',
    modified_by TEXT,
    modified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT settings_value_type_check CHECK (
        value_type IN ('string', 'number', 'boolean', 'array', 'object')
    ),
    CONSTRAINT settings_category_check CHECK (
        category IN ('database', 'cache', 'services', 'performance', 'features', 'monitoring', 'security')
    )
);

-- Index for category lookups
CREATE INDEX IF NOT EXISTS idx_settings_category ON system_settings(category);

-- Index for modified settings
CREATE INDEX IF NOT EXISTS idx_settings_modified ON system_settings(modified_at DESC) WHERE modified_at IS NOT NULL;

-- Settings Change History Table
CREATE TABLE IF NOT EXISTS settings_history (
    id SERIAL PRIMARY KEY,
    setting_key TEXT NOT NULL,
    old_value JSONB,
    new_value JSONB,
    modified_by TEXT NOT NULL,
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    reason TEXT
);

-- Index for history lookups
CREATE INDEX IF NOT EXISTS idx_settings_history_key ON settings_history(setting_key, modified_at DESC);

-- Record migration
INSERT INTO migrations (version, name, execution_time_ms)
VALUES ('002', 'settings_table', 0.0)
ON CONFLICT (version) DO NOTHING;
