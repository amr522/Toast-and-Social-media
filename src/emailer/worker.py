"""Email worker: generates personalized emails and sends via AWS SES.

This is a minimal scaffold. Implementations should be placed in functions:
- fetch_subscribers()
- generate_email_content(customer)
- render_template(html_body, reservation_link, order_link)
- send_email_via_ses(to_address, subject, html_content)
"""

import os


def fetch_subscribers():
    # placeholder: query Cloud SQL for opted-in subscribers
    return []


def run_email_campaign(dry_run=True):
    subscribers = fetch_subscribers()
    for s in subscribers:
        # call LLM to generate body, render template and either store or send
        pass


if __name__ == "__main__":
    run_email_campaign(dry_run=True)
