from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional

from src.menu.utils import BUILD_DIR, PROCESSED_DIR
from src.notifications.email import send_email
from src.notifications.webhooks import notify_team
from .validator import QAResult, validate_many


def _collect_slugs() -> List[str]:
    slugs = {p.stem for p in PROCESSED_DIR.glob("*.done")}
    # Also look at platform bundles
    bundles = BUILD_DIR / "platform_assets"
    if bundles.exists():
        for platform_dir in bundles.iterdir():
            if platform_dir.is_dir():
                for slug_dir in platform_dir.iterdir():
                    if slug_dir.is_dir():
                        slugs.add(slug_dir.name)
    return sorted(slugs)


def _collect_durations_for_today(today: Optional[datetime] = None) -> Dict[str, float]:
    today = today or datetime.now(timezone.utc)
    day = today.strftime("%Y%m%d")
    out: Dict[str, float] = {}
    rpt_dir = BUILD_DIR / "batch_reports"
    if not rpt_dir.exists():
        return out
    for rpt in rpt_dir.glob("batch_*.json"):
        if day not in rpt.name:
            continue
        try:
            data = json.loads(rpt.read_text(encoding="utf-8"))
            for slug, dur in (data.get("durations_sec") or {}).items():
                out[slug] = float(dur)
        except Exception:
            continue
    return out


def _report_dir() -> Path:
    d = BUILD_DIR / "qa_reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def generate_daily_report(*, email: bool = False, webhook: bool = False) -> Dict[str, any]:
    slugs = _collect_slugs()
    results = validate_many(slugs)
    durations = _collect_durations_for_today()

    ok = [r for r in results.values() if not r.issues]
    with_issues = [r for r in results.values() if r.issues]
    avg_duration = round(mean(durations.values()), 2) if durations else 0.0

    summary = {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "counts": {
            "slugs": len(slugs),
            "ok": len(ok),
            "with_issues": len(with_issues),
        },
        "avg_duration_sec": avg_duration,
        "issues_top": _summarize_issues(with_issues),
        "scores": {
            "avg": round(mean([r.score for r in results.values()]) if results else 0, 1),
            "min": min([r.score for r in results.values()], default=0),
            "max": max([r.score for r in results.values()], default=0),
        },
    }

    payload = {
        "summary": summary,
        "items": {slug: results[slug].__dict__ for slug in slugs},
    }

    # Write JSON and a compact text file
    out_json = _report_dir() / f"qa_{summary['date']}.json"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_txt = _report_dir() / f"qa_{summary['date']}.txt"
    out_txt.write_text(_format_text_summary(summary, with_issues), encoding="utf-8")

    # Send notifications
    subject = f"QA Daily: {summary['counts']['ok']} ok / {summary['counts']['with_issues']} issues"
    body = out_txt.read_text(encoding="utf-8")
    if email:
        try:
            send_email(subject, body)
        except Exception:
            pass
    if webhook:
        try:
            notify_team(subject, {"summary": summary})
        except Exception:
            pass

    return payload


def _summarize_issues(items: List[QAResult]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for r in items:
        for issue in r.issues:
            counts[issue] += 1
    # Return top 5
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5])


def _format_text_summary(summary: Dict[str, any], items_with_issues: List[QAResult]) -> str:
    lines = []
    lines.append(f"Date: {summary['date']}")
    lines.append(
        f"Processed: {summary['counts']['slugs']} | OK: {summary['counts']['ok']} | Issues: {summary['counts']['with_issues']}"
    )
    lines.append(
        f"Avg duration: {summary['avg_duration_sec']}s | Score avg/min/max: {summary['scores']['avg']}/{summary['scores']['min']}/{summary['scores']['max']}"
    )
    if summary["issues_top"]:
        lines.append("Top issues:")
        for name, cnt in summary["issues_top"].items():
            lines.append(f" - {name}: {cnt}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate daily QA report and optionally notify team")
    parser.add_argument("--email", action="store_true")
    parser.add_argument("--webhook", action="store_true")
    args = parser.parse_args()

    payload = generate_daily_report(email=args.email, webhook=args.webhook)
    print(json.dumps({"ok": True, "summary": payload.get("summary")}, indent=2))


if __name__ == "__main__":
    main()

