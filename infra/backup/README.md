Backups

Included script: infra/backup/backup_build.py

What it captures:
- build/ (generated assets, manifests, reports)
- menu/items/ (per-item JSON metadata)

Usage:
- Local archive:
  python infra/backup/backup_build.py

- Upload to S3 (optional):
  export BACKUP_S3_BUCKET=your-bucket
  python infra/backup/backup_build.py

Schedule:
- Add to crontab or run as a Kubernetes CronJob.

