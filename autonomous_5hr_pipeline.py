"""
═══════════════════════════════════════════════════════════════
  Yash Arora — 24/7 Autonomous Outreach Pipeline
  Runs on GitHub Actions (cloud, no local machine needed)

  Phase 1  →  Lead Discovery & Research    (90 min)
  Phase 2  →  Cooldown & Quality Check     (30 min)
  Phase 3  →  AI-Powered Email Dispatch    (120 min)
  Phase 4  →  Follow-Up Old Leads          (30 min)

  Total runtime: ~4.5 hours per cycle
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import random
import json
from datetime import datetime, timedelta

from lead_engine import (
    load_leads, save_leads, load_blocklist, add_to_blocklist,
    validate_lead, craft_cold_email, craft_followup,
    send_email, search_leads_online, enrich_lead_with_ai,
    ai_generate, SERVICES, MAX_SENDS_PER_DAY,
    DELAY_BETWEEN_MIN, DELAY_BETWEEN_MAX
)

# ─── Target Tier-2 Regional Hubs ───────────────────────────
# Low inbox clutter, high email open rates for small shop owners
TARGET_REGIONS = [
    {
        "city": "Grand Rapids", "state": "MI",
        "niches": ["bakery", "coffee shop", "boutique", "florist", "brewery taproom"]
    },
    {
        "city": "Columbus", "state": "OH",
        "niches": ["artisan bakery", "specialty coffee", "fashion boutique", "juice bar", "pizza shop"]
    },
    {
        "city": "Salt Lake City", "state": "UT",
        "niches": ["custom cakes", "catering", "specialty food", "yoga studio", "outdoor gear shop"]
    },
    {
        "city": "Charlotte", "state": "NC",
        "niches": ["bakery", "cafe", "florist", "wellness studio", "barbershop"]
    },
    {
        "city": "Manchester", "state": "UK",
        "niches": ["independent coffee roaster", "sandwich shop", "bakery", "vintage shop"]
    },
    {
        "city": "Leeds", "state": "UK",
        "niches": ["cafe", "bakery", "independent bookshop", "craft beer bar"]
    },
    {
        "city": "Eindhoven", "state": "Netherlands",
        "niches": ["cafe", "bakery", "design studio", "bike shop"]
    },
]

# Best service fit for each niche type
NICHE_SERVICE_MAP = {
    "bakery": "social_creatives",
    "artisan bakery": "social_creatives",
    "custom cakes": "social_creatives",
    "coffee shop": "qr_digital_menu",
    "specialty coffee": "qr_digital_menu",
    "independent coffee roaster": "qr_digital_menu",
    "cafe": "qr_digital_menu",
    "sandwich shop": "qr_digital_menu",
    "pizza shop": "qr_digital_menu",
    "juice bar": "qr_digital_menu",
    "boutique": "social_creatives",
    "fashion boutique": "social_creatives",
    "vintage shop": "social_creatives",
    "florist": "social_creatives",
    "wellness studio": "mobile_landing_page",
    "yoga studio": "mobile_landing_page",
    "barbershop": "mobile_landing_page",
    "brewery taproom": "qr_digital_menu",
    "craft beer bar": "qr_digital_menu",
    "catering": "mobile_landing_page",
    "outdoor gear shop": "mobile_landing_page",
    "design studio": "mobile_landing_page",
    "bike shop": "mobile_landing_page",
    "independent bookshop": "social_creatives",
    "specialty food": "social_creatives",
}


def log(msg):
    print(f"[{datetime.utcnow().strftime('%H:%M:%S UTC')}] {msg}")


# ═══════════════════════════════════════════════════════════
#  PHASE 1: LEAD DISCOVERY & RESEARCH
# ═══════════════════════════════════════════════════════════

def phase_1_discover(duration_minutes=90):
    log("=" * 60)
    log("PHASE 1: LEAD DISCOVERY & RESEARCH")
    log(f"Duration: {duration_minutes} min | Targets: {len(TARGET_REGIONS)} regions")
    log("=" * 60)

    db = load_leads()
    existing_emails = set(l.get("email", "").lower() for l in db.get("leads", []))
    blocklist = load_blocklist()
    new_count = 0
    start = time.time()

    # Shuffle regions for variety each run
    regions = list(TARGET_REGIONS)
    random.shuffle(regions)

    for region in regions:
        if (time.time() - start) >= (duration_minutes * 60):
            break

        for niche in region["niches"]:
            if (time.time() - start) >= (duration_minutes * 60):
                break

            city_label = f"{region['city']}, {region['state']}"
            log(f"  Scanning: {niche} in {city_label}...")

            # Search for business emails
            raw_emails = search_leads_online(region["city"], niche, existing_emails)

            for email in raw_emails:
                if email in existing_emails or email in blocklist:
                    continue

                # Use AI to enrich the lead
                enriched = enrich_lead_with_ai(email, region["city"], niche)
                if not enriched:
                    log(f"    Skipped {email} (AI enrichment failed)")
                    continue

                service_key = NICHE_SERVICE_MAP.get(niche, "social_creatives")

                new_lead = {
                    "business": enriched.get("business", "Unknown"),
                    "owner": enriched.get("owner", ""),
                    "email": email,
                    "niche": f"{niche.title()} ({city_label})",
                    "pain_point": enriched.get("pain_point", ""),
                    "service_key": service_key,
                    "status": "pending",
                    "discovered_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                    "source": f"web_search_{region['city'].lower().replace(' ', '_')}"
                }

                # Validate before adding
                valid, reason = validate_lead(new_lead, blocklist)
                if valid:
                    db["leads"].append(new_lead)
                    existing_emails.add(email)
                    new_count += 1
                    log(f"    + NEW LEAD: {new_lead['business']} ({email})")
                else:
                    log(f"    Skipped {email}: {reason}")

            # Pace between searches (avoid rate limits)
            wait = random.randint(45, 90)
            log(f"  Pacing: {wait}s before next search...")
            time.sleep(wait)

    save_leads(db)
    log(f"PHASE 1 COMPLETE: {new_count} new leads discovered")
    log(f"Total leads in database: {len(db['leads'])}")
    return new_count


# ═══════════════════════════════════════════════════════════
#  PHASE 2: COOLDOWN & QUALITY VERIFICATION
# ═══════════════════════════════════════════════════════════

def phase_2_cooldown(duration_minutes=30):
    log("")
    log("=" * 60)
    log("PHASE 2: COOLDOWN & QUALITY CHECK")
    log("=" * 60)

    db = load_leads()
    blocklist = load_blocklist()

    # Remove any leads that are on the DNC list
    cleaned = 0
    for lead in db["leads"]:
        email = lead.get("email", "").lower().strip()
        if email in blocklist and lead.get("status") != "blocked":
            lead["status"] = "blocked"
            cleaned += 1
            log(f"  Blocked: {email} (on do-not-contact list)")

    if cleaned:
        save_leads(db)
        log(f"  Cleaned {cleaned} blocked leads")

    # Deduplicate by email
    seen = set()
    unique_leads = []
    dupes = 0
    for lead in db["leads"]:
        email = lead.get("email", "").lower().strip()
        if email not in seen:
            seen.add(email)
            unique_leads.append(lead)
        else:
            dupes += 1
    if dupes:
        db["leads"] = unique_leads
        save_leads(db)
        log(f"  Removed {dupes} duplicate leads")

    # Count stats
    statuses = {}
    for lead in db["leads"]:
        s = lead.get("status", "unknown")
        statuses[s] = statuses.get(s, 0) + 1
    log(f"  Pipeline status: {json.dumps(statuses)}")

    # Cooldown wait
    log(f"  Resting for {duration_minutes} min before dispatch...")
    for minute in range(1, duration_minutes + 1):
        time.sleep(60)
        if minute % 10 == 0:
            log(f"  Cooldown: {minute}/{duration_minutes} min done")

    log("PHASE 2 COMPLETE")


# ═══════════════════════════════════════════════════════════
#  PHASE 3: AI-POWERED EMAIL DISPATCH
# ═══════════════════════════════════════════════════════════

def phase_3_dispatch(duration_minutes=120):
    log("")
    log("=" * 60)
    log("PHASE 3: AI-POWERED EMAIL DISPATCH")
    log(f"Daily cap: {MAX_SENDS_PER_DAY} | Window: {duration_minutes} min")
    log("=" * 60)

    db = load_leads()
    blocklist = load_blocklist()
    sent_count = 0
    start = time.time()

    for lead in db["leads"]:
        # Check limits
        if sent_count >= MAX_SENDS_PER_DAY:
            log(f"Daily cap reached ({MAX_SENDS_PER_DAY})")
            break
        if (time.time() - start) >= (duration_minutes * 60):
            log("Dispatch window expired")
            break

        # Skip already-sent, blocked, or completed leads
        if lead.get("status") in ("sent", "followed_up_1", "followed_up_2", "completed", "blocked", "skipped"):
            continue

        # Validate
        valid, reason = validate_lead(lead, blocklist)
        if not valid:
            lead["status"] = "skipped"
            lead["skip_reason"] = reason
            log(f"  SKIP: {lead.get('business', '?')} — {reason}")
            continue

        # Generate AI-powered email
        log(f"  [{sent_count+1}/{MAX_SENDS_PER_DAY}] Crafting email for: {lead['business']} ({lead['owner']})")
        subject, body = craft_cold_email(lead)

        log(f"    Subject: \"{subject}\"")
        log(f"    Words: {len(body.split())}")

        # Send
        success, msg_id = send_email(lead["email"], subject, body)

        if success:
            lead["status"] = "sent"
            lead["sent_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            lead["message_id"] = msg_id
            lead["subject_used"] = subject
            sent_count += 1
            save_leads(db)  # Save after each send for safety

            # Anti-spam pacing
            delay = random.randint(DELAY_BETWEEN_MIN, DELAY_BETWEEN_MAX)
            log(f"    Pacing: {delay}s (~{round(delay/60,1)} min)")
            time.sleep(delay)
        else:
            lead["status"] = "failed"
            lead["fail_reason"] = "SMTP error"

    save_leads(db)
    log(f"PHASE 3 COMPLETE: {sent_count} emails delivered")
    return sent_count


# ═══════════════════════════════════════════════════════════
#  PHASE 4: FOLLOW-UP OLD LEADS
# ═══════════════════════════════════════════════════════════

def phase_4_followups(max_followups=10):
    log("")
    log("=" * 60)
    log("PHASE 4: FOLLOW-UP SEQUENCE")
    log("=" * 60)

    db = load_leads()
    blocklist = load_blocklist()
    now = datetime.utcnow()
    followup_count = 0

    for lead in db["leads"]:
        if followup_count >= max_followups:
            break

        email = lead.get("email", "").lower().strip()
        if email in blocklist:
            continue

        status = lead.get("status", "")
        sent_at_str = lead.get("sent_at", "")
        if not sent_at_str:
            continue

        try:
            sent_at = datetime.strptime(sent_at_str, "%Y-%m-%d %H:%M UTC")
        except ValueError:
            try:
                sent_at = datetime.strptime(sent_at_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        days_since = (now - sent_at).days
        original_msg_id = lead.get("message_id")
        original_subject = lead.get("subject_used", f"about {lead.get('business', '')}")

        # Follow-up 1: 4+ days after first email
        if status == "sent" and days_since >= 4:
            log(f"  Follow-up #1 for {lead['business']} ({days_since} days old)")
            body = craft_followup(lead, 1)
            subject = f"Re: {original_subject}"

            success, msg_id = send_email(
                lead["email"], subject, body, reply_to_id=original_msg_id
            )
            if success:
                lead["status"] = "followed_up_1"
                lead["followup_1_at"] = now.strftime("%Y-%m-%d %H:%M UTC")
                followup_count += 1
                time.sleep(random.randint(60, 120))

        # Follow-up 2: 10+ days after first email
        elif status == "followed_up_1" and days_since >= 10:
            log(f"  Follow-up #2 (final) for {lead['business']} ({days_since} days old)")
            body = craft_followup(lead, 2)
            subject = f"Re: {original_subject}"

            success, msg_id = send_email(
                lead["email"], subject, body, reply_to_id=original_msg_id
            )
            if success:
                lead["status"] = "completed"
                lead["followup_2_at"] = now.strftime("%Y-%m-%d %H:%M UTC")
                followup_count += 1
                time.sleep(random.randint(60, 120))

    save_leads(db)
    log(f"PHASE 4 COMPLETE: {followup_count} follow-ups sent")
    return followup_count


# ═══════════════════════════════════════════════════════════
#  MAIN EXECUTION
# ═══════════════════════════════════════════════════════════

def run_full_cycle():
    """Complete daily outreach cycle (~4.5 hours)."""
    log("=" * 60)
    log("  YASH ARORA — AUTONOMOUS OUTREACH ENGINE")
    log(f"  Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    log(f"  Daily cap: {MAX_SENDS_PER_DAY} emails")
    log("=" * 60)

    # Phase 1: Discover new leads (90 min)
    phase_1_discover(duration_minutes=90)

    # Phase 2: Cooldown + quality check (30 min)
    phase_2_cooldown(duration_minutes=30)

    # Phase 3: Send cold emails (120 min)
    phase_3_dispatch(duration_minutes=120)

    # Phase 4: Send follow-ups (up to 10)
    phase_4_followups(max_followups=10)

    log("")
    log("=" * 60)
    log("  DAILY CYCLE COMPLETE")
    log(f"  Finished: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    log("=" * 60)


def run_test():
    """Quick test of all phases (2-3 minutes)."""
    log("TEST MODE — Running mini cycle")
    phase_1_discover(duration_minutes=1)
    phase_2_cooldown(duration_minutes=1)
    phase_3_dispatch(duration_minutes=2)
    phase_4_followups(max_followups=2)
    log("TEST COMPLETE")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_test()
    else:
        run_full_cycle()
