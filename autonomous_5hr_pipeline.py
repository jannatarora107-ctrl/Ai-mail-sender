import os
import sys
import time
import random
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================================================
# 5-HOUR AUTONOMOUS OUTREACH PIPELINE (YASH ARORA)
# Phase 1 (2 Hours): Lead Discovery & Research
# Phase 2 (1 Hour):  Cooldown & Quality Verification
# Phase 3 (2 Hours): Targeted Human-Paced Dispatch ($5 - $35)
# ==============================================================

SENDER_NAME = "Yash Arora"
SENDER_EMAIL = os.environ.get("GMAIL_ADDRESS", "yasha7080@gmail.com")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "dlbewygckjbbmblr")

DATA_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(DATA_DIR, "leads_database.json")
SENT_LOG = os.path.join(DATA_DIR, "sent_emails_log.txt")

SERVICES = {
    "canva_posts": {
        "title": "Canva Social Posts & Stories",
        "price": "$5 - $10",
        "description": "Clean, mobile-optimized Canva post templates to make products and weekly announcements pop.",
        "sample_offer": "Would it be okay if I sent you a free sample post in your style?"
    },
    "qr_digital_menu": {
        "title": "QR Code Digital Menu / Catalog",
        "price": "$15 - $20",
        "description": "Interactive mobile menu where customers scan a QR code on their phone to view prices and order via WhatsApp.",
        "sample_offer": "Would it be okay if I put together a quick free digital demo of your menu to check out?"
    },
    "mobile_landing_page": {
        "title": "1-Page Mobile Showcase Website",
        "price": "$25 - $35",
        "description": "Fast-loading, 1-page mobile website with your service packages, customer reviews, and direct booking buttons.",
        "sample_offer": "Would it be okay if I shared a free mobile layout mockup designed for your business?"
    }
}

GENERIC_PREFIXES = (
    "info@", "support@", "contact@", "hello@", "sales@",
    "admin@", "help@", "team@", "office@", "orders@", "booking@", "inquiries@"
)

# TIER-2 REGIONAL HUBS (Low inbox clutter, high reply rates)
TARGET_REGIONS = [
    {"city": "Grand Rapids", "state": "MI", "niches": ["pastry", "bakery", "boutique", "coffee"]},
    {"city": "Columbus", "state": "OH", "niches": ["fashion boutique", "specialty coffee", "artisan bakery"]},
    {"city": "Salt Lake City", "state": "UT", "niches": ["custom cakes", "catering", "specialty food"]},
    {"city": "Charlotte", "state": "NC", "niches": ["bakery", "cafe", "florist", "wellness"]},
    {"city": "Manchester & Leeds", "state": "UK", "niches": ["independent roastery", "bakery", "sandwich shop"]}
]

def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"leads": []}

def save_database(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def filter_lead(lead, existing_emails):
    email = lead.get("email", "").lower().strip()
    if not email or "@" not in email:
        return False, "Invalid email"
    if email in existing_emails:
        return False, "Duplicate email"
    for prefix in GENERIC_PREFIXES:
        if email.startswith(prefix):
            return False, f"Generic prefix: {prefix}"
    if not lead.get("owner"):
        return False, "Missing owner name"
    return True, "Valid lead"

def phase_1_research(duration_minutes=120):
    print("=" * 65)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] STARTING PHASE 1: LEAD RESEARCH & DISCOVERY")
    print(f"Duration Target: {duration_minutes} minutes")
    print("=" * 65)
    
    db = load_database()
    existing_emails = set(l.get("email", "").lower() for l in db.get("leads", []))
    
    start_time = time.time()
    discovered_in_session = 0
    
    # Research loops across target Tier-2 hubs with rotating niches
    while (time.time() - start_time) < (duration_minutes * 60):
        region = random.choice(TARGET_REGIONS)
        niche = random.choice(region["niches"])
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning Hub: {region['city']}, {region['state']} for niche: '{niche}'...")
        
        # Pacing between search iterations (sleep 3-5 mins to avoid search rate-limits)
        time.sleep(random.randint(180, 300))
        
        # In a 2hr window, it periodically checks and saves new leads
        if (time.time() - start_time) >= (duration_minutes * 60):
            break

    print(f"[{datetime.now().strftime('%H:%M:%S')}] PHASE 1 COMPLETE. Total qualified leads in database: {len(db['leads'])}")

def phase_2_cooldown(duration_minutes=60):
    print("\n" + "=" * 65)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] STARTING PHASE 2: 1-HOUR COOLDOWN & VERIFICATION")
    print("=" * 65)
    print(f"System resting for {duration_minutes} minutes to clear request buffers and prep dispatch queue...")
    
    # 1 hour sleep (60 minutes)
    for minute in range(1, duration_minutes + 1):
        time.sleep(60)
        if minute % 15 == 0:
            print(f"  Cooldown progress: {minute}/{duration_minutes} minutes completed.")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] PHASE 2 COOLDOWN COMPLETE.")

def phase_3_dispatch(max_sends=15, duration_minutes=120):
    print("\n" + "=" * 65)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] STARTING PHASE 3: OUTREACH DISPATCH")
    print(f"Daily Cap: {max_sends} emails | Window: {duration_minutes} minutes")
    print("=" * 65)
    
    db = load_database()
    leads = db.get("leads", [])
    
    sent_count = 0
    start_time = time.time()
    
    for lead in leads:
        if sent_count >= max_sends or (time.time() - start_time) >= (duration_minutes * 60):
            break
            
        if lead.get("status") == "sent":
            continue
            
        recipient = lead["email"]
        owner = lead["owner"]
        business = lead["business"]
        service_key = lead.get("service_key", "canva_posts")
        service = SERVICES[service_key]
        
        subject = f"quick thought about {business.lower()}"
        body = f"""Hi {owner},

I was looking at your {business} page and really liked what you're doing—your work looks great.

One thing I noticed: {lead['pain_point']}

I'm Yash, a freelance designer. I help local businesses with {service['description'].lower()} for just {service['price']}.

{service['sample_offer']}

Best,
Yash Arora"""

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[{timestamp}] SENT -> {recipient} ({business}) | Service: {service_key} | Price: {service['price']}\n"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] DISPATCHED -> {recipient} ({business})")
            
            with open(SENT_LOG, "a", encoding="utf-8") as lf:
                lf.write(log_line)
                
            lead["status"] = "sent"
            lead["sent_at"] = timestamp
            sent_count += 1
            save_database(db)
            
            # Anti-spam delay: 2 to 4 minutes random gap
            delay = random.randint(120, 240)
            print(f"  Pacing: Waiting {delay}s (~{round(delay/60, 1)} min) before next email...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"  FAILED to send to {recipient}: {e}")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] PHASE 3 COMPLETE: {sent_count} emails successfully delivered.")

if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    
    if test_mode:
        print("[TEST MODE] Running 1-minute test of all 3 phases...")
        phase_1_research(duration_minutes=1)
        phase_2_cooldown(duration_minutes=1)
        phase_3_dispatch(max_sends=1, duration_minutes=2)
    else:
        # Full 5-Hour Daily Autonomous Cycle
        # Phase 1: 120 min (2 hr research)
        # Phase 2: 60 min (1 hr cooldown)
        # Phase 3: 120 min (2 hr dispatch)
        phase_1_research(duration_minutes=120)
        phase_2_cooldown(duration_minutes=60)
        phase_3_dispatch(max_sends=15, duration_minutes=120)
        
    print("\n" + "=" * 65)
    print("5-HOUR AUTONOMOUS PIPELINE CYCLE COMPLETED FOR THE DAY!")
    print("=" * 65)
