#!/usr/bin/env bash
# run_once_08-setup-monitoring.sh
# Configure Prometheus, Grafana, and monitoring exporters
set -euo pipefail

MONITORING_DIR="${HOME}/infra/monitoring"

echo "==> Setting up monitoring stack..."

# Ensure monitoring directories exist
mkdir -p "${MONITORING_DIR}"/{prometheus,grafana/{provisioning/dashboards,provisioning/datasources,provisioning/notifiers},exporters,kuma}

# Generate Prometheus config if not present
PROM_CONFIG="${MONITORING_DIR}/prometheus/prometheus.yml"
if [[ ! -f "$PROM_CONFIG" ]]; then
    cat > "$PROM_CONFIG" <<'PROMEOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']
PROMEOF
    echo "==> Created Prometheus config: ${PROM_CONFIG}"
fi

# Generate Grafana datasource config if not present
GRAFANA_DS="${MONITORING_DIR}/grafana/provisioning/datasources/prometheus.yml"
if [[ ! -f "$GRAFANA_DS" ]]; then
    mkdir -p "$(dirname "$GRAFANA_DS")"
    cat > "$GRAFANA_DS" <<'GSEOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
GSEOF
    echo "==> Created Grafana datasource config."
fi

echo "==> Monitoring setup complete."
