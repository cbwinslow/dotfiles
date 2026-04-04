#!/bin/bash
# System Metrics Push Script for Uptime Kuma
# Pushes GPU, CPU, Disk, Temp, and RAM metrics to Kuma push monitors
# Run via cron every 5 minutes: */5 * * * * /usr/local/bin/kuma-push-metrics.sh

KUMA_URL="http://localhost:3001/api/push"

# Function to push metrics to Kuma
push_metric() {
    local monitor_name="$1"
    local status="$2"  # up or down
    local message="$3"
    local ping="${4:-0}"
    
    curl -s -X POST "${KUMA_URL}?status=${status}&msg=${message}&ping=${ping}" \
         -H "Content-Type: application/json" \
         --data-urlencode "monitor_name=${monitor_name}"
}

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# === GPU Monitoring (NVIDIA) ===
if command -v nvidia-smi &> /dev/null; then
    # GPU 0 - Tesla K80
    GPU0_TEMP=$(nvidia-smi -i 0 --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    GPU0_UTIL=$(nvidia-smi -i 0 --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    GPU0_MEM=$(nvidia-smi -i 0 --query-gpu=utilization.memory --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    push_metric "GPU 0 - Tesla K80" "up" "GPU0: ${GPU0_UTIL}% util, ${GPU0_TEMP}°C, ${GPU0_MEM}% mem" "${GPU0_UTIL}"
    
    # GPU 1 - Tesla K80
    GPU1_TEMP=$(nvidia-smi -i 1 --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    GPU1_UTIL=$(nvidia-smi -i 1 --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    GPU1_MEM=$(nvidia-smi -i 1 --query-gpu=utilization.memory --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    push_metric "GPU 1 - Tesla K80" "up" "GPU1: ${GPU1_UTIL}% util, ${GPU1_TEMP}°C, ${GPU1_MEM}% mem" "${GPU1_UTIL}"
    
    # GPU 2 - Tesla K40m
    GPU2_TEMP=$(nvidia-smi -i 2 --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    GPU2_UTIL=$(nvidia-smi -i 2 --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    GPU2_MEM=$(nvidia-smi -i 2 --query-gpu=utilization.memory --format=csv,noheader,nounits 2>/dev/null || echo "N/A")
    push_metric "GPU 2 - Tesla K40m" "up" "GPU2: ${GPU2_UTIL}% util, ${GPU2_TEMP}°C, ${GPU2_MEM}% mem" "${GPU2_UTIL}"
else
    push_metric "GPU 0 - Tesla K80" "down" "nvidia-smi not available"
    push_metric "GPU 1 - Tesla K80" "down" "nvidia-smi not available"
    push_metric "GPU 2 - Tesla K40m" "down" "nvidia-smi not available"
fi

# === CPU Usage ===
CPU_IDLE=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d'%' -f1)
CPU_USAGE=$(echo "100 - ${CPU_IDLE}" | bc 2>/dev/null || echo "N/A")
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
push_metric "CPU Usage" "up" "CPU: ${CPU_USAGE}% util, Load: ${LOAD_AVG}" "${CPU_USAGE%.*}"

# === RAM Usage ===
RAM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
RAM_USED=$(free -m | awk '/^Mem:/{print $3}')
RAM_PERCENT=$(echo "scale=1; ${RAM_USED} * 100 / ${RAM_TOTAL}" | bc 2>/dev/null || echo "N/A")
push_metric "RAM Usage" "up" "RAM: ${RAM_USED}MB/${RAM_TOTAL}MB (${RAM_PERCENT}%)" "${RAM_PERCENT%.*}"

# === Disk IO ===
DISK_ROOT=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
DISK_DATA=$(df -h /home 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%' || echo "N/A")
push_metric "Disk IO" "up" "Disk /: ${DISK_ROOT}% | /home: ${DISK_DATA}%" "${DISK_ROOT}"

# === System Temperatures ===
if command -v sensors &> /dev/null; then
    CPU_TEMP=$(sensors 2>/dev/null | grep -i 'core 0' | awk '{print $3}' | tr -d '+°C' | head -1 || echo "N/A")
    push_metric "System Temps" "up" "CPU: ${CPU_TEMP}°C" "${CPU_TEMP%.*}"
else
    push_metric "System Temps" "up" "sensors not installed" "0"
fi

echo "[${TIMESTAMP}] Metrics pushed to Uptime Kuma"

# === GPU Power Draw ===
if command -v nvidia-smi &> /dev/null; then
    TOTAL_POWER=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | awk '{sum+=$1} END {printf "%.0f", sum}')
    push_metric "GPU Power Draw" "up" "Total GPU Power: ${TOTAL_POWER}W" "${TOTAL_POWER}"
fi

# === Network IO ===
NET_RX=$(cat /sys/class/net/eth0/statistics/rx_bytes 2>/dev/null || echo 0)
NET_TX=$(cat /sys/class/net/eth0/statistics/tx_bytes 2>/dev/null || echo 0)
push_metric "Network IO" "up" "RX: $(($NET_RX/1048576))MB TX: $(($NET_TX/1048576))MB" "0"

# === Load Average ===
LOAD1=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
LOAD5=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $2}' | tr -d ',')
push_metric "Load Average" "up" "Load: ${LOAD1} (1m), ${LOAD5} (5m)" "${LOAD1%.*}"

# === Swap Usage ===
SWAP_TOTAL=$(free -m | awk '/^Swap:/{print $2}')
SWAP_USED=$(free -m | awk '/^Swap:/{print $3}')
SWAP_PERCENT=$(echo "scale=1; ${SWAP_USED} * 100 / ${SWAP_TOTAL}" | bc 2>/dev/null || echo "0")
push_metric "Swap Usage" "up" "Swap: ${SWAP_USED}MB/${SWAP_TOTAL}MB (${SWAP_PERCENT}%)" "${SWAP_PERCENT%.*}"

# === Process Count ===
PROC_COUNT=$(ps aux | wc -l)
push_metric "Process Count" "up" "Running processes: ${PROC_COUNT}" "${PROC_COUNT}"

# === Docker Containers ===
if command -v docker &> /dev/null; then
    CONTAINER_COUNT=$(docker ps -q 2>/dev/null | wc -l)
    push_metric "Docker Containers" "up" "Active containers: ${CONTAINER_COUNT}" "${CONTAINER_COUNT}"
fi

# === System Uptime ===
UPTIME_DAYS=$(awk '{print int($1/86400)}' /proc/uptime)
push_metric "System Uptime" "up" "Uptime: ${UPTIME_DAYS} days" "${UPTIME_DAYS}"

# === ZFS Pool Health (if available) ===
if command -v zpool &> /dev/null; then
    ZFS_HEALTH=$(zpool list -H -o health 2>/dev/null | head -1 || echo "N/A")
    push_metric "ZFS Pool Health" "up" "ZFS: ${ZFS_HEALTH}" "0"
fi

# === Debug Monitors ===

# System Log Errors (last 5 min)
LOG_ERRORS=$(journalctl -p err --since "5 minutes ago" --no-pager 2>/dev/null | wc -l || echo "0")
push_metric "System Logs Errors" "up" "Errors in last 5min: ${LOG_ERRORS}" "${LOG_ERRORS}"

# Kernel Dmesg Errors
DMESG_ERRORS=$(dmesg -T 2>/dev/null | grep -iE "(error|fail|warn|critical)" | tail -10 | wc -l || echo "0")
push_metric "Kernel Dmesg Errors" "up" "Kernel issues: ${DMESG_ERRORS}" "${DMESG_ERRORS}"

# OOM Killer Events
OOM_EVENTS=$(dmesg 2>/dev/null | grep -i "killed process" | wc -l || echo "0")
push_metric "OOM Killer Events" "up" "OOM kills: ${OOM_EVENTS}" "${OOM_EVENTS}"

# Failed Systemd Services
FAILED_SERVICES=$(systemctl --failed --no-legend 2>/dev/null | grep "failed" | wc -l || echo "0")
push_metric "Failed Systemd Services" "up" "Failed services: ${FAILED_SERVICES}" "${FAILED_SERVICES}"

# High Load Events (load > CPU cores)
CPU_CORES=$(nproc)
LOAD_INT=${LOAD1%.*}
if [ "$LOAD_INT" -gt "$CPU_CORES" ] 2>/dev/null; then
    push_metric "High Load Events" "up" "LOAD ALERT: ${LOAD1} > ${CPU_CORES} cores" "${LOAD_INT}"
else
    push_metric "High Load Events" "up" "Load normal: ${LOAD1}" "${LOAD_INT}"
fi

# Inode Usage
INODE_ROOT=$(df -i / 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%' || echo "0")
push_metric "Inode Usage" "up" "Inode usage: ${INODE_ROOT}%" "${INODE_ROOT}"

# Network Connections
NET_CONN=$(ss -tuln 2>/dev/null | wc -l || netstat -tuln 2>/dev/null | wc -l || echo "0")
push_metric "Network Connections" "up" "Active connections: ${NET_CONN}" "${NET_CONN}"

# Context Switches (if available)
if [ -f /proc/stat ]; then
    CTX_SWITCHES=$(grep "ctxt" /proc/stat | awk '{print $2}' || echo "0")
    push_metric "Context Switches" "up" "Context switches: ${CTX_SWITCHES}" "0"
fi

echo "[${TIMESTAMP}] Debug metrics pushed"
