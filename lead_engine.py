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
# PROFESSIONAL OUTREACH & MICRO-SERVICE ENGINE (YASH ARORA)
# ==============================================================

SENDER_NAME = "Yash Arora"
SENDER_EMAIL = os.environ.get("GMAIL_ADDRESS", "")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

DATA_DIR = os.path.dirname(__file__)
LEADS_DB = os.path.join(DATA_DIR, "leads_database.json")
SENT_LOG = os.path.join(DATA_DIR, "sent_emails_log.txt")

# PROFESSIONAL MICRO-SERVICES CATALOG (NO "CANVA" JARGON)
SERVICES = {
    "social_creatives": {
        "title": "Custom Brand Creatives & Announcement Cards",
        "price": "$5 - $10",
        "description": "clean, mobile-first brand creatives and visual announcement cards that help products and weekly drops pop.",
        "sample_offer": "Would it be okay if I put together a quick, free sample design tailored to your brand style?"
    },
    "qr_digital_menu": {
        "title": "Instant QR Digital Menu & Price Catalog",
        "price": "$15 - $20",
        "description": "an interactive mobile menu that customers scan directly on their phones to view current items and order via WhatsApp.",
        "sample_offer": "Would it be okay if I set up a free digital preview of your menu for you to see?"
    },
    "mobile_landing_page": {
        "title": "1-Page High-Converting Mobile Showcase",
        "price": "$25 - $35",
        "description": "a fast, 1-page mobile layout displaying your booking availability, packages, and client testimonials.",
        "sample_offer": "Would it be okay if I put together a free mobile preview layout for your business?"
    }
}

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
    owner = lead["owner"].strip()
    business = lead["business"].strip()
    pain_point = lead["pain_point"].strip()
    
    # Map legacy keys if present
    service_key = lead.get("service_key", "social_creatives")
    if service_key == "canva_posts":
        service_key = "social_creatives"
        
    service = SERVICES.get(service_key, SERVICES["social_creatives"])
    
    # Custom punchy subject lines based on service & business
    if service_key == "qr_digital_menu":
        subject = f"idea for {business.lower()}'s counter menu"
    elif service_key == "mobile_landing_page":
        subject = f"quick design thought for {business.lower()}"
    else:
        subject = f"creative idea for {business.lower()}'s posts"
    
    body = f"""Hi {owner},

I was checking out {business} and really loved what you've built—your craft looks fantastic.

One quick observation: {pain_point}

I'm Yash, an independent digital designer. I help local brands with {service['description']} for just {service['price']}.

{service['sample_offer']}

Best,
Yash Arora"""

    return subject, body

def send_outreach_email(lead, live=False):
    subject, body = generate_personalized_email(lead)
    recipient = lead["email"].strip()
    
    if not live:
        print(f"[SIMULATION] To: {recipient} | Subject: '{subject}'")
        print(f"[WORD COUNT] {len(body.split())} words\n---\n{body}\n---")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] SUCCESS -> {recipient} ({lead['business']}) | Subject: {subject}\n"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] DELIVERED -> {recipient} ({lead['business']})")
        with open(SENT_LOG, "a", encoding="utf-8") as lf:
            lf.write(log_entry)
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] FAILED -> {recipient}: {e}")
        return False
