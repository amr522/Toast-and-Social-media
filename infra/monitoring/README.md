Monitoring Overview

- Health checks: the API exposes GET /health at src/main.py: returns {"status":"ok"}.
- Container health: docker-compose.yml defines a curl-based healthcheck.
- Logs: Uvicorn access and app logs are emitted to stdout/stderr for aggregation.

Options

- Prometheus/Blackbox: Use blackbox_exporter to probe /health. Example scrape config:

  - job_name: minimax-api-health
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets: ['http://minimax-api:8080/health']
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

- Loki/Promtail: Ship container logs for centralized search. Point promtail to Docker engine and filter by container name minimax-api.

Dashboards & Alerts

- Alerts: trigger on failed healthchecks or long downtime.
- Dashboards: track request rate, latency (if you add middleware), batch durations from build/batch_reports, and QA scores from build/qa_reports.

