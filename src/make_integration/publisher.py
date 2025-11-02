"""Publisher adapter that posts content packages to Make.com webhooks."""
import requests


class PlatformPublisher:
    def __init__(self, webhooks: dict):
        self.webhooks = webhooks

    def post(self, platform: str, payload: dict):
        url = self.webhooks.get(platform)
        if not url:
            raise ValueError(f"No webhook configured for {platform}")
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
