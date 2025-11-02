"""Scheduler handlers invoked by Cloud Scheduler (Cloud Run endpoints).

Each function should call into the corresponding module (toast.sync, emailer.worker, etc.).
"""
from fastapi import HTTPException


def handle_run_sync():
    # call toast.sync.fetch_toast_customers()
    return {"status": "sync_started"}


def handle_run_newsletter():
    # call emailer.worker.run_email_campaign(dry_run=False)
    return {"status": "newsletter_started"}


def handle_run_birthday():
    # call emailer.worker.send_birthday_emails()
    return {"status": "birthday_started"}
