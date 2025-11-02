Infra notes and quick commands

- Use Terraform or gcloud to create:
  - Cloud SQL (Postgres)
  - Service accounts with minimal permissions
  - Secret Manager secrets
  - Cloud Run service and Cloud Scheduler jobs
  - Artifact Registry repository

- Example gcloud create scheduler job (replace URL):

  gcloud scheduler jobs create http run-newsletter \
    --schedule="0 9 1,15 * *" \
    --uri="https://<cloud-run-url>/run-newsletter" \
    --http-method=POST \
    --oauth-service-account-email=<service-account>
