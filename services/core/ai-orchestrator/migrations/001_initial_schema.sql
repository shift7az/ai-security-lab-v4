-- ============================================================================
-- AI Security Lab v4.0 - Initial Database Schema
-- TimescaleDB Migration 001
-- ============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- Cameras Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS cameras (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'offline',
    stream_url TEXT,
    snapshot_url TEXT,
    uptime_percentage FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT cameras_status_check CHECK (status IN ('online', 'offline', 'error', 'maintenance'))
);

-- Index for camera lookups
CREATE INDEX IF NOT EXISTS idx_cameras_status ON cameras(status);
CREATE INDEX IF NOT EXISTS idx_cameras_name ON cameras(name);

-- ============================================================================
-- Intelligence Results Table (Hypertable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS intelligence_results (
    detection_id TEXT NOT NULL,
    camera_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    threat_score FLOAT NOT NULL DEFAULT 0.0,
    threat_level TEXT NOT NULL,
    ai_models_used TEXT[] DEFAULT '{}',
    insights JSONB DEFAULT '{}',
    processing_time_ms FLOAT DEFAULT 0.0,
    
    PRIMARY KEY (detection_id, timestamp),
    
    CONSTRAINT intelligence_threat_level_check CHECK (
        threat_level IN ('none', 'low', 'medium', 'high', 'critical')
    ),
    CONSTRAINT intelligence_threat_score_check CHECK (
        threat_score >= 0.0 AND threat_score <= 1.0
    )
);

-- Create hypertable for time-series data
SELECT create_hypertable(
    'intelligence_results',
    'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_intelligence_camera_time 
    ON intelligence_results(camera_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_intelligence_threat_score 
    ON intelligence_results(threat_score DESC, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_intelligence_threat_level 
    ON intelligence_results(threat_level, timestamp DESC);

-- ============================================================================
-- Alerts Table (Hypertable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT NOT NULL,
    camera_id TEXT NOT NULL,
    detection_id TEXT,
    threat_level TEXT NOT NULL,
    priority TEXT NOT NULL,
    message TEXT NOT NULL,
    description TEXT DEFAULT '',
    timestamp TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMPTZ,
    resolved_by TEXT,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    
    PRIMARY KEY (id, timestamp),
    
    CONSTRAINT alerts_threat_level_check CHECK (
        threat_level IN ('none', 'low', 'medium', 'high', 'critical')
    ),
    CONSTRAINT alerts_priority_check CHECK (
        priority IN ('low', 'medium', 'high', 'critical')
    ),
    CONSTRAINT alerts_status_check CHECK (
        status IN ('active', 'acknowledged', 'resolved')
    )
);

-- Create hypertable
SELECT create_hypertable(
    'alerts',
    'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_alerts_status_priority 
    ON alerts(status, priority DESC, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_camera_time 
    ON alerts(camera_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_detection 
    ON alerts(detection_id);

-- ============================================================================
-- Timeline Events Table (Hypertable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_events (
    id TEXT NOT NULL,
    type TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    camera_id TEXT,
    threat_level TEXT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    metadata JSONB DEFAULT '{}',
    
    PRIMARY KEY (id, timestamp),
    
    CONSTRAINT timeline_type_check CHECK (
        type IN ('threat', 'alert', 'system', 'camera')
    )
);

-- Create hypertable
SELECT create_hypertable(
    'timeline_events',
    'timestamp',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_timeline_type_time 
    ON timeline_events(type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_timeline_camera 
    ON timeline_events(camera_id, timestamp DESC);

-- ============================================================================
-- Users Table (For future authentication)
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'operator',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    
    CONSTRAINT users_role_check CHECK (
        role IN ('admin', 'operator', 'viewer')
    )
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================================================
-- Migrations Table (Track applied migrations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    version TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    execution_time_ms FLOAT
);

-- ============================================================================
-- Camera Statistics Materialized View (For Performance)
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS camera_stats_24h AS
SELECT 
    c.id as camera_id,
    c.name as camera_name,
    COUNT(ir.detection_id) as total_detections,
    COUNT(ir.detection_id) FILTER (WHERE ir.threat_score > 0.3) as threats_detected,
    AVG(ir.threat_score) FILTER (WHERE ir.threat_score > 0.3) as avg_threat_score,
    MAX(ir.timestamp) as last_detection
FROM cameras c
LEFT JOIN intelligence_results ir ON c.id = ir.camera_id 
    AND ir.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY c.id, c.name;

-- Index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_camera_stats_24h_id 
    ON camera_stats_24h(camera_id);

-- ============================================================================
-- Continuous Aggregates (TimescaleDB Feature)
-- ============================================================================

-- Hourly threat summary
CREATE MATERIALIZED VIEW IF NOT EXISTS threats_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) as hour,
    camera_id,
    COUNT(*) as detection_count,
    AVG(threat_score) as avg_threat_score,
    MAX(threat_score) as max_threat_score,
    COUNT(*) FILTER (WHERE threat_level = 'critical') as critical_count,
    COUNT(*) FILTER (WHERE threat_level = 'high') as high_count
FROM intelligence_results
WHERE threat_score > 0.3
GROUP BY hour, camera_id;

-- Refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('threats_hourly',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- ============================================================================
-- Data Retention Policies
-- ============================================================================

-- Keep intelligence results for 30 days
SELECT add_retention_policy('intelligence_results', 
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- Keep alerts for 90 days
SELECT add_retention_policy('alerts', 
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Keep timeline events for 60 days
SELECT add_retention_policy('timeline_events', 
    INTERVAL '60 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for cameras table
DROP TRIGGER IF EXISTS update_cameras_updated_at ON cameras;
CREATE TRIGGER update_cameras_updated_at
    BEFORE UPDATE ON cameras
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to create timeline event when alert is created
CREATE OR REPLACE FUNCTION create_alert_timeline_event()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO timeline_events (
        id,
        type,
        timestamp,
        camera_id,
        threat_level,
        title,
        description,
        metadata
    ) VALUES (
        'timeline_' || NEW.id,
        'alert',
        NEW.timestamp,
        NEW.camera_id,
        NEW.threat_level,
        NEW.message,
        NEW.description,
        jsonb_build_object(
            'alert_id', NEW.id,
            'priority', NEW.priority,
            'detection_id', NEW.detection_id
        )
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for new alerts
DROP TRIGGER IF EXISTS alert_timeline_trigger ON alerts;
CREATE TRIGGER alert_timeline_trigger
    AFTER INSERT ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION create_alert_timeline_event();

-- ============================================================================
-- Initial Grants (if needed for restricted users)
-- ============================================================================

-- Grant permissions to security user (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO security;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO security;

-- ============================================================================
-- Record Migration
-- ============================================================================

INSERT INTO migrations (version, name, execution_time_ms)
VALUES ('001', 'initial_schema', 0.0)
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify hypertables created
SELECT * FROM timescaledb_information.hypertables;

-- Verify continuous aggregates
SELECT * FROM timescaledb_information.continuous_aggregates;

-- Verify retention policies
SELECT * FROM timescaledb_information.jobs WHERE job_type = 'retention';

-- Show table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
