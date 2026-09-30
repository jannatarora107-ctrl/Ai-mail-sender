import json
import os
import time
import random
from datetime import datetime
from lead_engine import filter_lead, send_outreach_email, SERVICES

DATA_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(DATA_DIR, "leads_database.json")
SENT_LOG = os.path.join(DATA_DIR, "sent_emails_log.txt")

# DAILY SAFETY LIMIT (To protect your personal Gmail from getting banned/spam flagged)
# Researches up to 100 leads, sends max 15-25 emails/day safely.
MAX_DAILY_SENDS = 15
MIN_DELAY_SECONDS = 90
MAX_DELAY_SECONDS = 180

def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"leads": [], "stats": {"total_researched": 0, "qualified": 0, "sent": 0}}

def save_database(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_daily_pipeline(live=False):
    db = load_database()
    leads = db.get("leads", [])
    
    print("=" * 65)
    print("DAILY AUTONOMOUS OUTREACH PIPELINE — YASH ARORA")
    print(f"Mode: {'LIVE SENDING' if live else 'SIMULATION / DRY RUN'}")
    print(f"Total Leads in Pipeline: {len(leads)}")
    print("=" * 65)
    
    sent_count = 0
    
    for i, lead in enumerate(leads):
        if sent_count >= MAX_DAILY_SENDS:
            print(f"\n[LIMIT REACHED] Daily safety limit of {MAX_DAILY_SENDS} emails reached to protect Gmail health.")
            break
            
        if lead.get("status") == "sent":
            continue
            
        valid, reason = filter_lead(lead)
        if not valid:
            print(f"[SKIPPED] {lead.get('business', 'Unknown')}: {reason}")
            lead["status"] = "skipped"
            lead["skip_reason"] = reason
            continue
            
        print(f"\n[{sent_count + 1}/{MAX_DAILY_SENDS}] Qualifying: {lead['business']} ({lead['owner']})")
        print(f"  Niche: {lead['niche']} | Target Service: {SERVICES[lead['service_key']]['title']} ({SERVICES[lead['service_key']]['price']})")
        
        success = send_outreach_email(lead, live=live)
        if success:
            if live:
                lead["status"] = "sent"
                lead["sent_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sent_count += 1
            
            # Anti-spam delay
            delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
            print(f"  Waiting {delay}s (~{round(delay/60, 1)} min) before next email...")
            if live:
                time.sleep(delay)
            else:
                time.sleep(1)

    if live:
        save_database(db)
        
    print("\n" + "=" * 65)
    print(f"PIPELINE BATCH COMPLETE: {sent_count} emails processed.")
    print("=" * 65)

if __name__ == "__main__":
    import sys
    is_live = "--send" in sys.argv
    run_daily_pipeline(live=is_live)
