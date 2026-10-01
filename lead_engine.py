"""
═══════════════════════════════════════════════════════════════
  Yash Arora — Professional Cold Outreach Engine
  AI-powered email generation via OpenRouter
  Gmail SMTP with threading, follow-ups & unsubscribe
═══════════════════════════════════════════════════════════════
"""

import os
import re
import json
import random
import smtplib
import hashlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formataddr

try:
    import requests as http
except ImportError:
    http = None

# ─── Configuration ──────────────────────────────────────────
SENDER_NAME  = "Yash Arora"
SENDER_EMAIL = os.environ.get("GMAIL_ADDRESS", "")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
AI_MODEL = "google/gemini-flash-1.5"

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(DATA_DIR, "leads_database.json")
DNC_FILE = os.path.join(DATA_DIR, "do_not_contact.json")
SENT_LOG = os.path.join(DATA_DIR, "sent_emails_log.txt")

MAX_SENDS_PER_DAY = 35        # Under 40 — safe for personal Gmail
DELAY_BETWEEN_MIN = 100       # seconds
DELAY_BETWEEN_MAX = 220       # seconds

# ─── Micro-Services Catalog ────────────────────────────────
SERVICES = {
    "social_creatives": {
        "label": "Custom Brand Creatives & Announcement Cards",
        "price": "$5\u2013$10",
        "what": "clean, mobile-first brand creatives and visual announcement cards that make your products and weekly specials stand out",
        "free_offer": "Would it be okay if I put together a quick, free sample design in your brand style?"
    },
    "qr_digital_menu": {
        "label": "QR Digital Menu & Catalog",
        "price": "$15\u2013$20",
        "what": "an interactive mobile menu customers scan on their phones to browse items and order via WhatsApp",
        "free_offer": "Would it be okay if I set up a free digital preview of your menu to check out?"
    },
    "mobile_landing_page": {
        "label": "1-Page Mobile Showcase",
        "price": "$25\u2013$35",
        "what": "a fast, 1-page mobile layout showing your packages, customer reviews, and a direct booking button",
        "free_offer": "Would it be okay if I put together a free mobile preview layout for your business?"
    }
}

SKIP_PREFIXES = (
    "info@", "support@", "contact@", "hello@", "sales@",
    "admin@", "help@", "team@", "office@", "orders@",
    "booking@", "inquiries@", "noreply@", "no-reply@"
)

# ─── AI System Prompts ─────────────────────────────────────
COLD_EMAIL_PROMPT = """You are Yash Arora, a 22-year-old independent digital designer helping small local businesses.

Write a cold outreach email following these STRICT rules:

FORMAT:
- 60-90 words MAXIMUM (count carefully)
- Plain text only — NO bold, NO italics, NO bullet points, NO links, NO images
- Start with "Hi {first_name}," on its own line
- End with "Best,\\nYash Arora" on its own line

CONTENT FLOW:
1. Open with something specific you noticed about THEIR business (not a generic compliment)
2. One honest, gentle observation about what could be better — NEVER insult their work
3. Mention what you do and the price naturally in one sentence
4. End with exactly ONE easy yes/no question offering a free sample

STYLE:
- Sound like you're texting a friend's friend — warm, casual, zero corporate energy
- Every single email MUST have a different opening, different flow, different phrasing
- NEVER start two emails the same way
- Read it out loud — if it sounds like marketing, rewrite it

ABSOLUTELY BANNED:
"amazing opportunity", "limited time", "guarantee", "boost your sales", "100%",
"act now", "don't miss", "exclusive", "Canva", "template", "leverage", "synergy",
"optimize", "maximize", "game-changer", "take your business to the next level",
"I couldn't help but notice", "I came across your", "I hope this email finds you",
"I'd love to", "exciting", "powerful", "revolutionary", "transform"

Return ONLY the email body text. No subject line. No labels. No quotes around it."""

SUBJECT_PROMPT = """Write a cold email subject line for a small business owner.

Rules:
- 3-7 words only
- All lowercase except proper nouns
- Must sound like a casual personal note, NOT marketing
- Spark genuine curiosity without being clickbait
- Must feel specific to THIS business
- NO emojis, NO ALL CAPS, NO exclamation marks, NO question marks
- NEVER use: "quick question", "just reaching out", "opportunity", "offer", "free", "help"

Return ONLY the subject line text. Nothing else. No quotes."""

FOLLOWUP_1_PROMPT = """You are Yash Arora. Write follow-up #1 (sent 4 days after your first cold email).

Rules:
- 2-3 short sentences MAXIMUM (30-45 words)
- Reference your previous note casually ("just bumping this up" or "circling back")
- Do NOT repeat your full pitch — they already read it
- Add ONE tiny new detail or thought
- End with a simple question
- Sign off with just "Yash"
- Plain text only, zero formatting

Return ONLY the follow-up body. No subject. No quotes."""

FOLLOWUP_2_PROMPT = """You are Yash Arora. Write your FINAL follow-up (sent 10 days after first email).

Rules:
- Exactly 2 sentences (20-30 words max)
- Acknowledge this is your last note
- Leave the door open without being pushy
- Sign off with just "Yash"
- Must feel genuinely respectful, not guilt-trippy

Return ONLY the text. No subject. No quotes."""

# ─── OpenRouter AI ─────────────────────────────────────────
def ai_generate(system_prompt, user_prompt, temperature=0.93):
    """Call OpenRouter for AI-generated content. Returns None on failure."""
    if not OPENROUTER_KEY or not http:
        return None
    try:
        r = http.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/jannatarora107-ctrl/Ai-mail-sender",
                "X-Title": "Yash Arora Outreach"
            },
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 350
            },
            timeout=45
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        # Strip any accidental wrapping quotes
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        return text
    except Exception as e:
        print(f"  [AI] Request failed: {e}")
        return None


# ─── Database I/O ──────────────────────────────────────────
def load_leads():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"leads": [], "stats": {"total_sent": 0, "last_run": None}}

def save_leads(data):
    data["stats"]["last_run"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_blocklist():
    if os.path.exists(DNC_FILE):
        with open(DNC_FILE, "r", encoding="utf-8") as f:
            return set(e.lower().strip() for e in json.load(f))
    return set()

def add_to_blocklist(email):
    bl = load_blocklist()
    bl.add(email.lower().strip())
    with open(DNC_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(bl)), f, indent=2)
    print(f"  [DNC] Added {email} to do-not-contact list")


# ─── Lead Validation ──────────────────────────────────────
def validate_lead(lead, blocklist=None):
    """Check if a lead is valid and eligible for outreach."""
    email = lead.get("email", "").lower().strip()
    if not email or "@" not in email:
        return False, "Invalid email"
    for pfx in SKIP_PREFIXES:
        if email.startswith(pfx):
            return False, f"Generic prefix ({pfx})"
    if not lead.get("owner", "").strip():
        return False, "Missing owner name"
    if not lead.get("pain_point", "").strip():
        return False, "Missing pain point"
    if blocklist and email in blocklist:
        return False, "Blocked (do-not-contact)"
    return True, "OK"


# ─── AI Email Generation ──────────────────────────────────
def craft_cold_email(lead):
    """Generate a unique, AI-written cold email + subject for this lead."""
    svc_key = lead.get("service_key", "social_creatives")
    if svc_key == "canva_posts":   # Legacy key migration
        svc_key = "social_creatives"
    svc = SERVICES.get(svc_key, SERVICES["social_creatives"])

    # --- Generate body ---
    body_prompt = (
        f"Write a cold email to:\n"
        f"- Owner: {lead['owner']}\n"
        f"- Business: {lead['business']}\n"
        f"- Type: {lead.get('niche', 'local shop')}\n"
        f"- What I noticed: {lead['pain_point']}\n"
        f"- My service: {svc['what']} for {svc['price']}\n"
        f"- Free sample line: {svc['free_offer']}\n\n"
        f"This person runs a busy small shop and checks email between customer orders. "
        f"Make every word count. 60-90 words."
    )
    body = ai_generate(COLD_EMAIL_PROMPT, body_prompt)

    # --- Generate subject ---
    subj_prompt = (
        f"Business: {lead['business']} ({lead.get('niche', '')}). "
        f"Service: {svc['what']}. City context: {lead.get('niche', '')}."
    )
    subject = ai_generate(SUBJECT_PROMPT, subj_prompt, temperature=0.88)

    if body and subject:
        return subject.strip(), body.strip()

    # Fallback to hand-written template if AI is down
    return _fallback_email(lead, svc)


def craft_followup(lead, followup_num):
    """Generate AI-written follow-up for an existing thread."""
    svc = SERVICES.get(lead.get("service_key", "social_creatives"), SERVICES["social_creatives"])
    prompt_template = FOLLOWUP_1_PROMPT if followup_num == 1 else FOLLOWUP_2_PROMPT

    context = (
        f"Follow-up #{followup_num} to {lead['owner']} at {lead['business']}.\n"
        f"Original topic: {lead['pain_point']}\n"
        f"Service: {svc['what']} for {svc['price']}"
    )
    text = ai_generate(prompt_template, context)

    if text:
        return text.strip()

    # Fallback
    if followup_num == 1:
        return (
            f"Hi {lead['owner']},\n\n"
            f"Just bumping up my last note about {lead['business']}. "
            f"Happy to share a free sample if you're curious — no strings.\n\n"
            f"Yash"
        )
    return (
        f"Hi {lead['owner']},\n\n"
        f"Last note from me. If the timing's off, totally get it. "
        f"Free sample offer stands whenever you're ready.\n\n"
        f"Yash"
    )


def _fallback_email(lead, svc):
    """Template fallback when AI is unavailable."""
    owner = lead["owner"].strip()
    biz = lead["business"].strip()
    openers = [
        f"Hi {owner},\n\nI was checking out {biz} and your work really caught my eye.",
        f"Hi {owner},\n\nCame across {biz} the other day — really solid stuff you're putting out.",
        f"Hi {owner},\n\nHey, just saw {biz} online and liked what you've got going.",
        f"Hi {owner},\n\nYour work at {biz} looks great — especially the attention to detail.",
    ]
    body = (
        f"{random.choice(openers)}\n\n"
        f"One thought: {lead['pain_point']}\n\n"
        f"I'm Yash, an independent designer. I help local brands with "
        f"{svc['what']} for {svc['price']}.\n\n"
        f"{svc['free_offer']}\n\n"
        f"Best,\nYash Arora"
    )
    subjects = [
        f"idea for {biz.lower()}",
        f"thought about {biz.lower()}",
        f"something for {biz.lower()}",
        f"re {biz.lower()}'s feed",
    ]
    return random.choice(subjects), body


# ─── SMTP Dispatch ─────────────────────────────────────────
UNSUB_FOOTER = "\n\n\u2014\nNot relevant? Just reply 'stop' and I won\u2019t email again."

def send_email(recipient, subject, body, reply_to_id=None):
    """
    Send one email via Gmail SMTP.
    Returns (success: bool, message_id: str or None).
    Uses In-Reply-To for follow-up threading.
    """
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("  [SMTP] Error: Gmail credentials missing")
        return False, None

    full_body = body + UNSUB_FOOTER

    msg = MIMEMultipart("alternative")
    msg["From"]    = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg["To"]      = recipient
    msg["Subject"] = subject

    msg_id = make_msgid(domain="gmail.com")
    msg["Message-ID"] = msg_id

    if reply_to_id:
        msg["In-Reply-To"] = reply_to_id
        msg["References"]  = reply_to_id

    msg.attach(MIMEText(full_body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as srv:
            srv.starttls()
            srv.login(SENDER_EMAIL, APP_PASSWORD)
            srv.sendmail(SENDER_EMAIL, recipient, msg.as_string())

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(SENT_LOG, "a", encoding="utf-8") as lf:
            lf.write(f"[{ts}] SENT -> {recipient} | Subject: {subject}\n")

        print(f"  [{datetime.now().strftime('%H:%M:%S')}] DELIVERED -> {recipient}")
        return True, msg_id

    except Exception as e:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] FAILED -> {recipient}: {e}")
        return False, None


# ─── Lead Discovery (Web Search) ──────────────────────────
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@gmail\.com", re.IGNORECASE)

def search_leads_online(city, niche, existing_emails):
    """
    Search DuckDuckGo for business owner emails in a target city/niche.
    Returns list of raw lead dicts (may need AI enrichment).
    """
    if not http:
        return []

    queries = [
        f'"{niche}" "{city}" owner email @gmail.com',
        f'"{niche}" near "{city}" founder @gmail.com',
        f'{niche} shop {city} contact gmail',
    ]
    query = random.choice(queries)
    found = []

    try:
        r = http.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=20
        )
        r.raise_for_status()
        page = r.text

        # Extract emails from search results
        emails_found = set(EMAIL_REGEX.findall(page))
        for em in emails_found:
            em_lower = em.lower()
            if em_lower in existing_emails:
                continue
            skip = False
            for pfx in SKIP_PREFIXES:
                if em_lower.startswith(pfx):
                    skip = True
                    break
            if not skip:
                found.append(em_lower)

    except Exception as e:
        print(f"  [SEARCH] DuckDuckGo failed: {e}")

    return found[:5]  # Cap at 5 per search to avoid flooding


def enrich_lead_with_ai(email, city, niche):
    """Use AI to generate plausible business info for a discovered email."""
    prompt = (
        f"I found this email while researching {niche} businesses in {city}: {email}\n\n"
        f"Based on the email address, guess:\n"
        f"1. The likely business name\n"
        f"2. The owner's first name\n"
        f"3. A specific, honest observation about what a typical {niche} in {city} "
        f"could improve with better visual branding or a mobile menu\n\n"
        f"Reply in this EXACT JSON format (no markdown, no explanation):\n"
        f'{{"business": "...", "owner": "...", "pain_point": "..."}}'
    )
    result = ai_generate(
        "You are a lead research assistant. Output valid JSON only. No markdown fences.",
        prompt,
        temperature=0.7
    )
    if result:
        try:
            # Clean potential markdown fences
            clean = result.strip()
            if clean.startswith("```"):
                clean = re.sub(r"^```\w*\n?", "", clean)
                clean = re.sub(r"\n?```$", "", clean)
            data = json.loads(clean)
            return data
        except (json.JSONDecodeError, KeyError):
            pass
    return None
