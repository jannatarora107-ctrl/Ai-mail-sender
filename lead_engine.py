import os
import sys
import time
import random
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ==============================================================
# AUTONOMOUS LEAD & OUTREACH ENGINE (YASH ARORA)
# Micro-Services ($5 - $35): Canva Posts, QR Menu, Mobile Landing
# ==============================================================

SENDER_NAME = "Yash Arora"
SENDER_EMAIL = os.environ.get("GMAIL_ADDRESS", "")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

DATA_DIR = os.path.dirname(__file__)
LEADS_DB = os.path.join(DATA_DIR, "leads_database.json")
SENT_LOG = os.path.join(DATA_DIR, "sent_emails_log.txt")

# MICRO-SERVICES CATALOG
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

# FILTER CRITERIA
GENERIC_PREFIXES = (
    "info@", "support@", "contact@", "hello@", "sales@",
    "admin@", "help@", "team@", "office@", "orders@", "booking@", "inquiries@"
)

def filter_lead(lead):
    email = lead.get("email", "").lower().strip()
    if not email or "@" not in email:
        return False, "Missing or invalid email"
    for prefix in GENERIC_PREFIXES:
        if email.startswith(prefix):
            return False, f"Generic prefix: {prefix}"
    if not lead.get("owner"):
        return False, "Missing owner name"
    if not lead.get("pain_point"):
        return False, "Missing diagnosed pain point"
    return True, "Valid qualified lead"

def generate_personalized_email(lead):
    owner = lead["owner"]
    business = lead["business"]
    pain_point = lead["pain_point"]
    service_key = lead.get("service_key", "canva_posts")
    service = SERVICES[service_key]
    
    subject = f"quick thought about {business.lower()}"
    
    body = f"""Hi {owner},

I was looking at your {business} page and really liked what you're doing—your work looks great.

One thing I noticed: {pain_point}

I'm Yash, a freelance designer. I help local businesses with {service['description'].lower()} for just {service['price']}.

{service['sample_offer']}

Best,
Yash Arora"""

    return subject, body

def send_outreach_email(lead, live=False):
    subject, body = generate_personalized_email(lead)
    recipient = lead["email"]
    
    if not live:
        print(f"[SIMULATION] To: {recipient} | Subject: {subject} | Service: {lead['service_key']}")
        print(f"[PREVIEW] Words: {len(body.split())}\n{body}\n")
        return True

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
        log_entry = f"[{timestamp}] SENT -> {recipient} ({lead['business']}) | Service: {lead['service_key']} | Price: {SERVICES[lead['service_key']]['price']}\n"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS: Sent to {recipient}")
        with open(SENT_LOG, "a", encoding="utf-8") as lf:
            lf.write(log_entry)
        return True
    except Exception as e:
        print(f"FAILED to send to {recipient}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 65)
    print("YASH ARORA — AUTONOMOUS LEAD QUALIFICATION & DISPATCH ENGINE")
    print("=" * 65)
    print("Catalog loaded: 3 Micro-Services ($5 - $35)")
    print(f"Sender: {SENDER_NAME} <{SENDER_EMAIL}>")
    print("Ready to qualify leads and auto-dispatch.")
