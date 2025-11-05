Operations Manual

Runbooks

Healthcheck fails
- Check container logs: docker logs minimax-api
- Verify .env is loaded and MiniMax_BASE_URL is reachable
- Restart service: docker compose restart api

Pipeline failures
- Inspect build/batch_reports/ for the latest report and error details
- Re-run a specific slug with verbose logging:
  python -m src.pipeline.enhance --slug <dish>

Drive sync issues
- Ensure service account has access to target folders
- Verify GDRIVE_* env vars and credentials path are correct
- Retry a slug:
  python -m src.drive.sync --slug <dish>

QA Reports
- Daily reports saved under build/qa_reports/
- To generate on demand:
  python -m src.qa.reporter --email --webhook

Scheduling
- Use host cron or a scheduler. For host cron, add:
  0 2 * * * cd /opt/minimax && /usr/bin/python3 -m src.scheduler.daily_runner --sync-drive >> /var/log/minimax-nightly.log 2>&1

Backups & Restore
- Back up build/ and menu/items:
  python infra/backup/backup_build.py
- Restore: extract the tarball at project root
  tar -xzf infra/backup/backups/backup_<TS>.tar.gz -C .

Security
- Rotate API keys regularly (MiniMax, SMTP, Drive)
- Keep .env files outside of version control; prefer a secret manager
- Restrict network egress if possible; whitelist API endpoints only

Performance
- Target < 2 minutes per item; see durations in batch reports
- Increase RATE_LIMIT_RPM and batch size thoughtfully; avoid API quotas

