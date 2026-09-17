-- Enable UUID extension for unique primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Target Findings Schema
-- ============================================================================
CREATE TABLE IF NOT EXISTS target_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT UNIQUE NOT NULL,
    waf VARCHAR(100) DEFAULT 'None Detected',
    anomaly_score REAL DEFAULT 0.0,
    ai_insight TEXT DEFAULT '',
    status VARCHAR(50) DEFAULT 'investigating',
    headers TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- Indexes for Performance & Dashboard Filtering
-- ============================================================================
-- Optimizes queries filtering or sorting by highest anomaly score
CREATE INDEX IF NOT EXISTS idx_target_findings_anomaly ON target_findings(anomaly_score DESC);

-- Optimizes filtering by operational status (e.g., investigating, requires_hunter)
CREATE INDEX IF NOT EXISTS idx_target_findings_status ON target_findings(status);

-- ============================================================================
-- Automated Timestamp Trigger
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_target_findings_modtime
    BEFORE UPDATE ON target_findings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
