-- ============================================================================
-- UPTIME KUMA ANALYSIS & REPORTING QUERIES
-- For troubleshooting, research, and benchmarking
-- Run: mysql -u cbwinslow -p123qweasd kuma < kuma_analysis_queries.sql
-- ============================================================================

-- ============================================================================
-- SECTION 1: AVAILABILITY & UPTIME REPORTS
-- ============================================================================

-- 1.1 Overall Service Availability (Last 24 Hours)
SELECT 
    m.name,
    m.type,
    COUNT(h.id) as total_checks,
    SUM(CASE WHEN h.status = 1 THEN 1 ELSE 0 END) as up_count,
    SUM(CASE WHEN h.status = 0 THEN 1 ELSE 0 END) as down_count,
    ROUND(SUM(CASE WHEN h.status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(h.id), 2) as uptime_percent,
    ROUND(AVG(h.ping), 2) as avg_response_ms,
    MAX(h.ping) as max_response_ms,
    MIN(h.ping) as min_response_ms
FROM monitor m
LEFT JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY m.id, m.name, m.type
ORDER BY uptime_percent ASC, avg_response_ms DESC;

-- 1.2 Service Downtime Summary (Last 7 Days)
SELECT 
    m.name,
    COUNT(DISTINCT DATE(h.time)) as days_with_incidents,
    SUM(CASE WHEN h.status = 0 THEN 1 ELSE 0 END) as total_down_checks,
    SEC_TO_TIME(SUM(CASE WHEN h.status = 0 THEN m.interval ELSE 0 END)) as estimated_downtime
FROM monitor m
LEFT JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND h.status = 0
GROUP BY m.id, m.name
HAVING total_down_checks > 0
ORDER BY total_down_checks DESC;

-- 1.3 Critical Services Health Dashboard
SELECT 
    m.name,
    m.type,
    CASE 
        WHEN ROUND(SUM(CASE WHEN h.status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(h.id), 2) >= 99.9 THEN 'HEALTHY'
        WHEN ROUND(SUM(CASE WHEN h.status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(h.id), 2) >= 99.0 THEN 'WARNING'
        ELSE 'CRITICAL'
    END as health_status,
    ROUND(SUM(CASE WHEN h.status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(h.id), 2) as uptime_24h,
    ROUND(AVG(h.ping), 2) as avg_response_ms,
    MAX(h.time) as last_check
FROM monitor m
LEFT JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY m.id, m.name, m.type
ORDER BY FIELD(health_status, 'CRITICAL', 'WARNING', 'HEALTHY'), avg_response_ms DESC;

-- ============================================================================
-- SECTION 2: PERFORMANCE & BENCHMARKING
-- ============================================================================

-- 2.1 Response Time Trends (Hourly Average - Last 7 Days)
SELECT 
    m.name,
    DATE_FORMAT(h.time, '%Y-%m-%d %H:00') as hour,
    ROUND(AVG(h.ping), 2) as avg_response_ms,
    ROUND(MIN(h.ping), 2) as min_response_ms,
    ROUND(MAX(h.ping), 2) as max_response_ms,
    COUNT(*) as check_count
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND h.status = 1
    AND m.type IN ('http', 'port', 'ping')
GROUP BY m.id, m.name, DATE_FORMAT(h.time, '%Y-%m-%d %H:00')
ORDER BY m.name, hour;

-- 2.2 Peak Response Times (Identify Performance Degradation)
SELECT 
    m.name,
    DATE_FORMAT(h.time, '%Y-%m-%d %H:%i') as timestamp,
    h.ping as response_ms,
    h.msg
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
    AND h.ping > (
        SELECT AVG(ping) * 2 
        FROM heartbeat 
        WHERE monitor_id = m.id 
        AND time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
        AND status = 1
    )
    AND h.status = 1
ORDER BY h.ping DESC
LIMIT 50;

-- 2.3 Performance Percentiles (p50, p95, p99)
SELECT 
    m.name,
    COUNT(*) as total_samples,
    ROUND(AVG(h.ping), 2) as avg_ms,
    ROUND(
        (SELECT ping FROM heartbeat 
         WHERE monitor_id = m.id AND status = 1 
         AND time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
         ORDER BY ping LIMIT 1 OFFSET (COUNT(*)/2)
        ), 2
    ) as p50_ms,
    MAX(h.ping) as p100_ms
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
    AND h.status = 1
GROUP BY m.id, m.name
HAVING total_samples > 100
ORDER BY avg_ms DESC;

-- 2.4 GPU Performance Benchmarking (If GPU monitors active)
SELECT 
    m.name,
    DATE_FORMAT(h.time, '%Y-%m-%d %H:%i') as timestamp,
    h.ping as utilization_percent,
    h.msg as details
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE m.name LIKE 'GPU%'
    AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY h.time DESC
LIMIT 100;

-- ============================================================================
-- SECTION 3: ERROR ANALYSIS & TROUBLESHOOTING
-- ============================================================================

-- 3.1 Recent Failures with Details
SELECT 
    m.name,
    m.type,
    h.time as failure_time,
    h.msg as error_message,
    TIMESTAMPDIFF(SECOND, LAG(h.time) OVER (PARTITION BY m.id ORDER BY h.time), h.time) as seconds_since_last_check
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.status = 0
    AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY h.time DESC
LIMIT 100;

-- 3.2 Error Patterns (Group by Error Message)
SELECT 
    m.name,
    h.msg as error_pattern,
    COUNT(*) as occurrence_count,
    MIN(h.time) as first_seen,
    MAX(h.time) as last_seen
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.status = 0
    AND h.time > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY m.id, m.name, h.msg
ORDER BY occurrence_count DESC;

-- 3.3 Flapping Services (Services that go up/down frequently)
SELECT 
    m.name,
    COUNT(*) as status_changes,
    SUM(CASE WHEN h.status = 0 THEN 1 ELSE 0 END) as down_events,
    ROUND(SUM(CASE WHEN h.status = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as instability_percent
FROM monitor m
JOIN (
    SELECT monitor_id, status, time,
           LAG(status) OVER (PARTITION BY monitor_id ORDER BY time) as prev_status
    FROM heartbeat
    WHERE time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
) h ON m.id = h.monitor_id
WHERE h.status != h.prev_status
GROUP BY m.id, m.name
HAVING status_changes > 5
ORDER BY status_changes DESC;

-- 3.4 Recovery Time Analysis (MTTR)
SELECT 
    m.name,
    AVG(TIMESTAMPDIFF(SECOND, down.time, up.time)) as avg_recovery_seconds,
    COUNT(*) as recovery_count
FROM monitor m
JOIN (
    SELECT monitor_id, time, status,
           LEAD(time) OVER (PARTITION BY monitor_id ORDER BY time) as recovery_time,
           LEAD(status) OVER (PARTITION BY monitor_id ORDER BY time) as next_status
    FROM heartbeat
    WHERE time > DATE_SUB(NOW(), INTERVAL 7 DAY)
) down ON m.id = down.monitor_id
JOIN heartbeat up ON down.monitor_id = up.monitor_id AND up.time = down.recovery_time
WHERE down.status = 0 AND down.next_status = 1
GROUP BY m.id, m.name
ORDER BY avg_recovery_seconds DESC;

-- ============================================================================
-- SECTION 4: RESOURCE UTILIZATION REPORTS
-- ============================================================================

-- 4.1 System Resource Trends (For push monitors)
SELECT 
    m.name,
    DATE_FORMAT(h.time, '%Y-%m-%d %H:00') as hour,
    ROUND(AVG(h.ping), 2) as avg_value,
    ROUND(MAX(h.ping), 2) as peak_value,
    SUBSTRING_INDEX(h.msg, ' ', 1) as metric_unit
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE m.type = 'push'
    AND m.name IN ('CPU Usage', 'RAM Usage', 'Disk IO', 'GPU 0 - Tesla K80', 'GPU 1 - Tesla K80', 'GPU 2 - Tesla K40m')
    AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY m.id, m.name, DATE_FORMAT(h.time, '%Y-%m-%d %H:00')
ORDER BY m.name, hour;

-- 4.2 Resource Correlation (High CPU + High RAM events)
SELECT 
    DATE_FORMAT(cpu.time, '%Y-%m-%d %H:%i') as timestamp,
    cpu.ping as cpu_percent,
    ram.ping as ram_percent,
    CASE 
        WHEN cpu.ping > 80 AND ram.ping > 80 THEN 'CRITICAL'
        WHEN cpu.ping > 80 OR ram.ping > 80 THEN 'WARNING'
        ELSE 'NORMAL'
    END as status
FROM (
    SELECT h.time, h.ping
    FROM heartbeat h
    JOIN monitor m ON h.monitor_id = m.id
    WHERE m.name = 'CPU Usage'
        AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
) cpu
JOIN (
    SELECT h.time, h.ping
    FROM heartbeat h
    JOIN monitor m ON h.monitor_id = m.id
    WHERE m.name = 'RAM Usage'
        AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
) ram ON DATE_FORMAT(cpu.time, '%Y-%m-%d %H:%i') = DATE_FORMAT(ram.time, '%Y-%m-%d %H:%i')
WHERE cpu.ping > 70 OR ram.ping > 70
ORDER BY timestamp DESC;

-- 4.3 GPU Cluster Utilization Summary
SELECT 
    CASE 
        WHEN m.name LIKE 'GPU 0%' THEN 'GPU 0 - Tesla K80'
        WHEN m.name LIKE 'GPU 1%' THEN 'GPU 1 - Tesla K80'
        WHEN m.name LIKE 'GPU 2%' THEN 'GPU 2 - Tesla K40m'
    END as gpu_name,
    ROUND(AVG(h.ping), 2) as avg_utilization,
    ROUND(MAX(h.ping), 2) as peak_utilization,
    COUNT(*) as samples,
    SEC_TO_TIME(TIMESTAMPDIFF(SECOND, MIN(h.time), MAX(h.time))) as monitoring_duration
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE m.name LIKE 'GPU%'
    AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY gpu_name
ORDER BY avg_utilization DESC;

-- ============================================================================
-- SECTION 5: CAPACITY PLANNING & TRENDS
-- ============================================================================

-- 5.1 Weekly Availability Trend
SELECT 
    m.name,
    CONCAT(YEAR(h.time), '-Week', WEEK(h.time)) as week,
    ROUND(SUM(CASE WHEN h.status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) as availability_percent,
    ROUND(AVG(h.ping), 2) as avg_response_ms,
    COUNT(*) as total_checks
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY m.id, m.name, YEAR(h.time), WEEK(h.time)
ORDER BY m.name, week;

-- 5.2 Database Connection Pool Saturation (if applicable)
SELECT 
    m.name,
    h.time,
    h.msg,
    h.ping as connection_time_ms
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE m.name IN ('MySQL Database', 'PostgreSQL Database', 'Redis Cache')
    AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
    AND h.ping > 100  -- Slow connections
ORDER BY h.ping DESC
LIMIT 50;

-- 5.3 Service Dependency Analysis (Grouped by infrastructure layer)
SELECT 
    CASE 
        WHEN m.name IN ('MySQL Database', 'PostgreSQL Database', 'Redis Cache') THEN 'Data Layer'
        WHEN m.name LIKE 'GPU%' OR m.name IN ('CPU Usage', 'RAM Usage') THEN 'Compute Layer'
        WHEN m.name IN ('Docker Daemon', 'Docker Containers') THEN 'Container Layer'
        WHEN m.name IN ('Server Ping', 'Network IO') THEN 'Network Layer'
        ELSE 'Application Layer'
    END as layer,
    COUNT(DISTINCT m.id) as service_count,
    ROUND(AVG(CASE WHEN h.status = 1 THEN 1 ELSE 0 END) * 100, 2) as layer_health_percent,
    ROUND(AVG(h.ping), 2) as avg_response_ms
FROM monitor m
LEFT JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY layer
ORDER BY layer_health_percent ASC;

-- ============================================================================
-- SECTION 6: EXPORT REPORTS
-- ============================================================================

-- 6.1 Export Daily Summary (for external reporting)
SELECT 
    DATE(h.time) as date,
    m.name,
    m.type,
    MIN(h.ping) as min_response,
    MAX(h.ping) as max_response,
    AVG(h.ping) as avg_response,
    COUNT(CASE WHEN h.status = 1 THEN 1 END) as up_count,
    COUNT(CASE WHEN h.status = 0 THEN 1 END) as down_count,
    ROUND(COUNT(CASE WHEN h.status = 1 THEN 1 END) * 100.0 / COUNT(*), 4) as availability
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.time > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(h.time), m.id, m.name, m.type
ORDER BY date DESC, m.name;

-- 6.2 Alert Summary (Last 24h incidents)
SELECT 
    m.name,
    m.type,
    DATE_FORMAT(h.time, '%Y-%m-%d %H:%i:%s') as incident_start,
    h.msg as incident_details,
    'INVESTIGATE' as recommended_action
FROM monitor m
JOIN heartbeat h ON m.id = h.monitor_id
WHERE h.status = 0
    AND h.time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
    AND NOT EXISTS (
        SELECT 1 FROM heartbeat h2 
        WHERE h2.monitor_id = h.monitor_id 
        AND h2.time < h.time 
        AND h2.time > DATE_SUB(h.time, INTERVAL 5 MINUTE)
        AND h2.status = 0
    )
ORDER BY h.time DESC;

-- ============================================================================
-- USAGE INSTRUCTIONS:
-- ============================================================================
-- 1. Individual query: Copy section and run in MySQL
-- 2. Full report: mysql -u cbwinslow -p123qweasd kuma < kuma_analysis_queries.sql
-- 3. Automated report: Create cron job to run daily/weekly and email results
-- 4. Integration: Pipe output to script for Grafana/Prometheus ingestion
-- ============================================================================
