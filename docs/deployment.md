Production Deployment Guide

Overview

This project runs a small FastAPI app for healthchecks and orchestration hooks, plus a set of CLI tools for the MiniMax media pipeline. Containerization and docker-compose are provided; run scheduling via your platform of choice (host cron, Kubernetes CronJobs, or a scheduler).

Artifacts

- Dockerfile: builds the app image, default command runs uvicorn serving src.main:app on 8080.
- docker-compose.yml: defines api service and a helper one-shot batch service.
- .env.staging / .env.prod: sample environment files with production-safe defaults.
- infra/monitoring/: notes on health/monitoring and example Prometheus blackbox config.
- infra/backup/: backup scripts for build/ and menu/items.

Build and Run

1) Copy environment file
   cp .env.staging .env   # or source from your secret manager

2) Build and start
   docker compose build
   docker compose up -d api

3) Health check
   curl http://localhost:8080/health  # -> {"status":"ok"}

Batch Processing

- One-shot batch (inside Compose):
  docker compose run --rm batch

- Nightly (host cron example):
  0 2 * * * cd /opt/minimax && /usr/bin/docker compose run --rm batch >> /var/log/minimax-batch.log 2>&1

Google Drive Sync

- Provide service account credentials via:
  - GDRIVE_SERVICE_ACCOUNT_FILE mounted into container (e.g., /secrets/gcp/service-account.json)
  - or GDRIVE_SERVICE_ACCOUNT_JSON env var.

Backups

- Local tarball:
  python infra/backup/backup_build.py
- S3 upload (optional):
  BACKUP_S3_BUCKET=your-bucket python infra/backup/backup_build.py

Security & Secrets

- Do not commit real API keys.
- Use .env.prod as a template; load secrets via a secrets manager (KMS/Secret Manager/Parameter Store) and inject at deploy time.
- Rotate keys regularly; scope service account permissions minimally.

Monitoring

- Health endpoint: GET /health
- Container healthcheck in Compose uses curl.
- For metrics, consider adding Prometheus client middleware or exporting batch/QA metrics to a time-series DB.

Rollback

- Tag images per release (e.g., minimax-pipeline:2025-11-04) and keep N-2 images available.
- Roll back by `docker compose pull` desired tag and `docker compose up -d`.

