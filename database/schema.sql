-- ============================================================
-- Server Monitoring System Database Schema
-- ============================================================
-- This script creates all necessary tables for the monitoring system
-- Supports both PostgreSQL and MySQL

-- ============================================================
-- 1. System Metrics Table
-- ============================================================
-- Stores CPU, memory, and disk usage metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    cpu_usage FLOAT NOT NULL,
    cpu_cores INT NOT NULL,
    memory_usage FLOAT NOT NULL,
    memory_total_mb BIGINT NOT NULL,
    memory_used_mb BIGINT NOT NULL,
    memory_available_mb BIGINT NOT NULL,
    swap_usage FLOAT,
    disk_usage FLOAT NOT NULL,
    disk_total_gb FLOAT NOT NULL,
    disk_used_gb FLOAT NOT NULL,
    disk_free_gb FLOAT NOT NULL,
    uptime_seconds BIGINT NOT NULL,
    load_average_1m FLOAT,
    load_average_5m FLOAT,
    load_average_15m FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- ============================================================
-- 2. Alerts Table
-- ============================================================
-- Stores all generated alerts
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,  -- 'CPU', 'MEMORY', 'DISK', 'LOG'
    metric_name VARCHAR(100),
    current_value FLOAT,
    threshold_value FLOAT,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- 'CRITICAL', 'WARNING', 'INFO'
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for alert queries
CREATE INDEX idx_alerts_timestamp ON alerts(created_at DESC);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);

-- ============================================================
-- 3. Logs Table
-- ============================================================
-- Stores parsed system logs
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    log_type VARCHAR(50) NOT NULL,  -- 'SYSLOG', 'AUTH', 'DMESG'
    log_source VARCHAR(255) NOT NULL,  -- File path
    level VARCHAR(20),  -- 'ERROR', 'WARNING', 'INFO'
    message TEXT NOT NULL,
    process_name VARCHAR(255),
    process_id INT,
    user_name VARCHAR(100),
    hostname VARCHAR(255),
    raw_line TEXT,
    is_parsed BOOLEAN DEFAULT TRUE,
    is_important BOOLEAN DEFAULT FALSE,  -- Flagged for review
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for log queries
CREATE INDEX idx_logs_timestamp ON logs(created_at DESC);
CREATE INDEX idx_logs_type ON logs(log_type);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_important ON logs(is_important);

-- ============================================================
-- 4. Alert Thresholds Table
-- ============================================================
-- Stores configurable alert thresholds
CREATE TABLE IF NOT EXISTS alert_thresholds (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL UNIQUE,
    warning_threshold FLOAT NOT NULL,
    critical_threshold FLOAT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. System Information Table
-- ============================================================
-- Stores static system information
CREATE TABLE IF NOT EXISTS system_info (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    os_type VARCHAR(100),
    os_version VARCHAR(100),
    kernel_version VARCHAR(100),
    total_cpu_cores INT,
    boot_time TIMESTAMP,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. Processes Table
-- ============================================================
-- Stores top processes data
CREATE TABLE IF NOT EXISTS top_processes (
    id SERIAL PRIMARY KEY,
    pid INT NOT NULL,
    process_name VARCHAR(255) NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    memory_mb BIGINT,
    status VARCHAR(20),
    user VARCHAR(100),
    create_time TIMESTAMP,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for process queries
CREATE INDEX idx_top_processes_timestamp ON top_processes(recorded_at DESC);

-- ============================================================
-- Insert Default Alert Thresholds
-- ============================================================
INSERT INTO alert_thresholds (metric_name, warning_threshold, critical_threshold, description)
VALUES 
    ('CPU_USAGE', 70.0, 85.0, 'CPU usage percentage'),
    ('MEMORY_USAGE', 80.0, 90.0, 'Memory usage percentage'),
    ('DISK_USAGE', 80.0, 95.0, 'Disk usage percentage'),
    ('SWAP_USAGE', 50.0, 80.0, 'Swap usage percentage')
ON CONFLICT (metric_name) DO NOTHING;

-- ============================================================
-- Create Views for Common Queries
-- ============================================================

-- Latest metrics view
CREATE OR REPLACE VIEW latest_metrics AS
SELECT *
FROM system_metrics
ORDER BY timestamp DESC
LIMIT 1;

-- Recent alerts view
CREATE OR REPLACE VIEW recent_alerts AS
SELECT *
FROM alerts
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 100;

-- Critical alerts view
CREATE OR REPLACE VIEW critical_alerts AS
SELECT *
FROM alerts
WHERE severity = 'CRITICAL' AND is_resolved = FALSE
ORDER BY created_at DESC;

-- Important logs view
CREATE OR REPLACE VIEW important_logs AS
SELECT *
FROM logs
WHERE is_important = TRUE
ORDER BY created_at DESC
LIMIT 100;

-- ============================================================
-- Permissions and Cleanup (Optional)
-- ============================================================
-- For non-root users, you may need to grant permissions:
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO monitoring_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO monitoring_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO monitoring_user;
