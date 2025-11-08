-- ============================================================================
-- AI Security Lab v4.0 - Performance Optimization Indexes
-- Migration 003
-- ============================================================================

-- ============================================================================
-- Intelligence Results Optimization
-- ============================================================================

-- Composite index for common query patterns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_intelligence_camera_level_time 
    ON intelligence_results(camera_id, threat_level, timestamp DESC)
    WHERE threat_score > 0.3;

-- Index for threat score range queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_intelligence_score_range 
    ON intelligence_results(threat_score DESC, timestamp DESC)
    WHERE threat_score > 0.5;

-- Index for AI model filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_intelligence_ai_models 
    ON intelligence_results USING GIN(ai_models_used);

-- Partial index for high-priority threats
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_intelligence_critical_threats
    ON intelligence_results(timestamp DESC, camera_id)
    WHERE threat_level IN ('critical', 'high');

-- ============================================================================
-- Alerts Optimization
-- ============================================================================

-- Composite index for alert queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_status_priority_time
    ON alerts(status, priority, timestamp DESC)
    WHERE status IN ('active', 'acknowledged');

-- Index for camera-based alert lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_camera_status
    ON alerts(camera_id, status, timestamp DESC);

-- Index for detection-based alert lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_detection_lookup
    ON alerts(detection_id, timestamp DESC)
    WHERE detection_id IS NOT NULL;

-- Partial index for unresolved alerts
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_unresolved
    ON alerts(priority DESC, timestamp DESC)
    WHERE status != 'resolved';

-- Index for user action tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_user_actions
    ON alerts(acknowledged_by, acknowledged_at)
    WHERE acknowledged_by IS NOT NULL;

-- ============================================================================
-- Timeline Events Optimization
-- ============================================================================

-- Composite index for timeline queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_type_level_time
    ON timeline_events(type, threat_level, timestamp DESC)
    WHERE threat_level IS NOT NULL;

-- Index for camera timeline
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_camera_type
    ON timeline_events(camera_id, type, timestamp DESC)
    WHERE camera_id IS NOT NULL;

-- GIN index for metadata searches
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_metadata
    ON timeline_events USING GIN(metadata);

-- ============================================================================
-- Users Table Optimization
-- ============================================================================

-- Index for active user lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active
    ON users(role, is_active)
    WHERE is_active = TRUE;

-- Index for last login tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_last_login
    ON users(last_login DESC NULLS LAST)
    WHERE is_active = TRUE;

-- ============================================================================
-- Camera Statistics Optimization
-- ============================================================================

-- Refresh materialized view more efficiently
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_camera_stats_refresh
    ON camera_stats_24h(camera_id, last_detection DESC NULLS LAST);

-- ============================================================================
-- Query Optimization Functions
-- ============================================================================

-- Function to analyze slow queries
CREATE OR REPLACE FUNCTION analyze_slow_queries(threshold_ms INT DEFAULT 1000)
RETURNS TABLE (
    query_text TEXT,
    calls BIGINT,
    total_time_ms FLOAT,
    mean_time_ms FLOAT,
    max_time_ms FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        LEFT(pg_stat_statements.query, 100) as query_text,
        pg_stat_statements.calls,
        pg_stat_statements.total_exec_time / 1000 as total_time_ms,
        pg_stat_statements.mean_exec_time / 1000 as mean_time_ms,
        pg_stat_statements.max_exec_time / 1000 as max_time_ms
    FROM pg_stat_statements
    WHERE pg_stat_statements.mean_exec_time / 1000 > threshold_ms
    ORDER BY pg_stat_statements.total_exec_time DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Function to get index usage statistics
CREATE OR REPLACE FUNCTION check_index_usage()
RETURNS TABLE (
    table_name TEXT,
    index_name TEXT,
    index_scans BIGINT,
    tuples_read BIGINT,
    tuples_fetched BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname || '.' || tablename as table_name,
        indexrelname as index_name,
        idx_scan as index_scans,
        idx_tup_read as tuples_read,
        idx_tup_fetch as tuples_fetched
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public'
    ORDER BY idx_scan DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Vacuum and Analyze Optimization
-- ============================================================================

-- Auto-vacuum settings for high-write tables
ALTER TABLE intelligence_results SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE alerts SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE timeline_events SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

-- ============================================================================
-- Statistics Updates
-- ============================================================================

-- Update table statistics for query planner
ANALYZE intelligence_results;
ANALYZE alerts;
ANALYZE timeline_events;
ANALYZE cameras;
ANALYZE users;

-- ============================================================================
-- Record Migration
-- ============================================================================

INSERT INTO migrations (version, name, execution_time_ms)
VALUES ('003', 'performance_indexes', 0.0)
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- Verification
-- ============================================================================

-- Show all indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Show index sizes
SELECT 
    schemaname || '.' || tablename AS table,
    indexrelname AS index,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
