"""
Quick local pipeline — run on your machine for manual batch sends.
Usage:
  python daily_pipeline.py          # Dry run (simulation)
  python daily_pipeline.py --send   # Live send
"""
import json
import os
import sys
import time
import random
from datetime import datetime

from lead_engine import (
    load_leads, save_leads, load_blocklist,
    validate_lead, craft_cold_email, send_email,
    SERVICES, MAX_SENDS_PER_DAY, DELAY_BETWEEN_MIN, DELAY_BETWEEN_MAX
)

def run_pipeline(live=False):
    db = load_leads()
    leads = db.get("leads", [])
    blocklist = load_blocklist()

    print("=" * 60)
    print("  YASH ARORA — LOCAL OUTREACH PIPELINE")
    print(f"  Mode: {'LIVE SENDING' if live else 'DRY RUN (simulation)'}")
    print(f"  Leads in database: {len(leads)}")
    print(f"  Daily cap: {MAX_SENDS_PER_DAY}")
    print("=" * 60)

    sent = 0
    for lead in leads:
        if sent >= MAX_SENDS_PER_DAY:
            print(f"\n[CAP] {MAX_SENDS_PER_DAY} emails reached — stopping.")
            break

        if lead.get("status") in ("sent", "followed_up_1", "followed_up_2", "completed", "blocked", "skipped"):
            continue

        valid, reason = validate_lead(lead, blocklist)
        if not valid:
            print(f"[SKIP] {lead.get('business', '?')}: {reason}")
            lead["status"] = "skipped"
            lead["skip_reason"] = reason
            continue

        svc = SERVICES.get(lead.get("service_key", "social_creatives"), SERVICES["social_creatives"])
        print(f"\n[{sent+1}/{MAX_SENDS_PER_DAY}] {lead['business']} ({lead['owner']})")
        print(f"  Niche: {lead.get('niche', '?')} | Service: {svc['label']} ({svc['price']})")

        subject, body = craft_cold_email(lead)
        print(f"  Subject: \"{subject}\"")
        print(f"  Words: {len(body.split())}")

        if live:
            success, msg_id = send_email(lead["email"], subject, body)
            if success:
                lead["status"] = "sent"
                lead["sent_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                lead["message_id"] = msg_id
                lead["subject_used"] = subject
                sent += 1

                delay = random.randint(DELAY_BETWEEN_MIN, DELAY_BETWEEN_MAX)
                print(f"  Pacing: {delay}s")
                time.sleep(delay)
        else:
            print(f"  [SIM] Would send to: {lead['email']}")
            print(f"  ---\n{body}\n  ---")
            sent += 1
            time.sleep(0.5)

    if live:
        save_leads(db)

    print(f"\n{'=' * 60}")
    print(f"  DONE: {sent} emails {'sent' if live else 'simulated'}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    run_pipeline(live="--send" in sys.argv)
