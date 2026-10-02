"""
═══════════════════════════════════════════════════════════════
  Yash Arora (@yashwebsites) — Daily Morning Brief
  Runs every morning at 8:00 AM IST via GitHub Actions
  Sends a ready-to-use reel script + growth strategy to your inbox
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

try:
    import requests as http
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─── Config ─────────────────────────────────────────────────
SENDER_NAME   = "Yash Arora Bot"
SENDER_EMAIL  = os.environ.get("GMAIL_ADDRESS", "")
APP_PASSWORD  = os.environ.get("GMAIL_APP_PASSWORD", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

YOUR_EMAIL    = "yasha7080@gmail.com"       # Where brief gets sent
YOUR_HANDLE   = "@yashwebsites"
YOUR_NICHE    = "web design, graphic design, AI tools, freelancing"
AI_MODEL      = "google/gemini-flash-1.5"

# ─── Trending Topics Pool ────────────────────────────────────
# These are evergreen + trending topic buckets for your niche
TOPIC_BUCKETS = [
    # AI Tools (always trending for creator audience)
    "AI tools that replace expensive software (Photoshop, After Effects)",
    "Free AI tools for freelancers in 2025",
    "How to use ChatGPT / Claude to 10x your freelance output",
    "AI design tools vs Figma — honest comparison",
    "Cursor AI / Bolt / Lovable for building websites without coding",
    "Top 5 AI agents that do your work while you sleep",
    "How I use AI to write cold emails and get clients",
    "AI video editors vs manual — which one wins?",

    # Web Design / Dev
    "5 website mistakes that cost you clients",
    "Why your portfolio is losing you clients",
    "How to build a client's website in 24 hours",
    "Framer vs Webflow vs WordPress — which one should you use in 2025",
    "How to charge more as a freelance designer",
    "The exact process I use to build a $500 website in 1 week",

    # Freelancing Growth
    "How I find clients without Instagram DMs",
    "Cold email vs Instagram DMs — which gets more clients",
    "My exact system for getting 3-5 leads per week",
    "How to price your services so clients don't ghost you",
    "The one thing freelancers never tell you about getting clients",

    # Graphic Design
    "Design trends that will dominate 2025",
    "How I make brand kits in under 2 hours",
    "Logo design process from brief to final file",
    "Typography tricks that make designs look expensive",

    # Personal Brand / Creator
    "How to grow from 0 to 1000 followers as a design creator",
    "Why I post reels even when no one watches",
    "My honest income breakdown as a freelance designer",
    "Day in my life as a 22-year-old freelance designer",
]

# ─── AI Call ────────────────────────────────────────────────
def ai_call(system_prompt, user_prompt, max_tokens=1200):
    if not HAS_REQUESTS or not OPENROUTER_KEY:
        return None
    try:
        r = http.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/jannatarora107-ctrl/Ai-mail-sender",
                "X-Title": "Yash Morning Brief"
            },
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.85,
                "max_tokens": max_tokens
            },
            timeout=45
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  [AI] Failed: {e}")
        return None


# ─── Generate Reel Script ────────────────────────────────────
def generate_reel_script(topic):
    system = """You are a viral Instagram Reels scriptwriter for Indian creator @yashwebsites 
(web designer, graphic designer, AI tools, freelancing content).

STYLE RULES:
- Hook in first 1-2 seconds — must stop the scroll
- Conversational Hindi-English (Hinglish) or pure English — whatever feels natural for the topic
- 45-60 seconds reading time (about 120-160 words total)
- Frank, direct tone — like talking to a friend. NO "magical", NO corporate energy
- Each section label should be on its own line
- NO emojis in the script itself
- End with a CLEAR call to action (follow, comment, or save)

FORMAT (exactly this):
HOOK (first 3 seconds):
[hook line — one punchy sentence]

MAIN CONTENT:
[body of the reel — 4-6 short punchy lines. Each line is one thought.]

OUTRO + CTA:
[closing line + call to action]

CAPTION IDEA:
[one line caption for the post — under 15 words, no hashtags]

3 HASHTAG SETS:
#[tag1] #[tag2] #[tag3] #[tag4] #[tag5]"""

    user = f"""Write a reel script for this topic: "{topic}"

Creator context:
- Handle: @yashwebsites
- Niche: {YOUR_NICHE}
- Audience: Young Indians interested in design, freelancing, AI tools
- Tone: Frank, like "Aladdin ka chirag" — not magical, not clickbait. Real talk.

Make the hook STOP someone mid-scroll. No filler words."""

    return ai_call(system, user, max_tokens=700)


# ─── Generate Growth Strategy ────────────────────────────────
def generate_growth_strategy(today, day_of_week):
    system = """You are a no-BS Instagram growth advisor for Indian creators.
Give direct, actionable advice. No generic tips. No corporate speak.
Keep it under 200 words total."""

    user = f"""Today is {day_of_week}, {today}.

Creator: @yashwebsites (web design, graphic design, AI tools, freelance)
Current stage: Growing, building audience in design/tech niche

Give me:
1. WHAT TO POST TODAY (content format — Reel? Carousel? Story?)
2. BEST TIME TO POST (in IST, with reason)
3. ONE ENGAGEMENT TRICK for today
4. ONE PAGE GROWTH ACTION for this week (not generic — specific)
5. TRENDING ANGLE to use right now in design/AI/freelance niche

Be specific. Talk like you're texting me directly."""

    return ai_call(system, user, max_tokens=400)


# ─── Pick Today's Topic ──────────────────────────────────────
def pick_todays_topic():
    """Pick topic based on day of week — rotates through buckets."""
    today = datetime.date.today()
    # Use day of year mod topic count for consistent rotation
    index = today.timetuple().tm_yday % len(TOPIC_BUCKETS)
    return TOPIC_BUCKETS[index]


# ─── Build the Email ────────────────────────────────────────
def build_email(topic, reel_script, growth_tips, today_str, day_name):
    divider = "-" * 55

    email_body = f"""Good morning Yash,

Here's your daily brief for {day_name}, {today_str}.

{divider}
TODAY'S REEL TOPIC
{divider}
{topic}

{divider}
READY-TO-FILM SCRIPT
{divider}
{reel_script if reel_script else "[AI unavailable — try again later]"}

{divider}
PAGE GROWTH STRATEGY FOR TODAY
{divider}
{growth_tips if growth_tips else "[AI unavailable — try again later]"}

{divider}
QUICK REMINDERS
{divider}
- Film in natural light before 11 AM or after 5 PM
- Keep your face in first 2 seconds — algorithm loves it
- Reply to every comment in first 30 min of posting
- Post Stories today even if no Reel (keeps you visible)
- Cold email outreach runs automatically tonight at 8:20 PM IST

{divider}
Tomorrow's brief arrives tomorrow morning at 8:00 AM IST.

-- Yash Arora Bot"""

    return email_body


# ─── Send via Gmail SMTP ─────────────────────────────────────
def send_morning_brief(subject, body):
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("[SMTP] Missing credentials")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"]    = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg["To"]      = YOUR_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as srv:
            srv.starttls()
            srv.login(SENDER_EMAIL, APP_PASSWORD)
            srv.sendmail(SENDER_EMAIL, YOUR_EMAIL, msg.as_string())
        print(f"[SENT] Morning brief delivered to {YOUR_EMAIL}")
        return True
    except Exception as e:
        print(f"[FAILED] {e}")
        return False


# ─── Main ────────────────────────────────────────────────────
def main():
    today = datetime.date.today()
    today_str = today.strftime("%d %B %Y")
    day_name = today.strftime("%A")

    print("=" * 55)
    print(f"YASH MORNING BRIEF — {day_name}, {today_str}")
    print("=" * 55)

    # 1. Pick topic
    topic = pick_todays_topic()
    print(f"\nToday's topic: {topic}")

    # 2. Generate reel script
    print("Generating reel script...")
    reel_script = generate_reel_script(topic)

    # 3. Generate growth strategy
    print("Generating growth strategy...")
    growth_tips = generate_growth_strategy(today_str, day_name)

    # 4. Build email
    subject = f"[{day_name}] Your Reel Script + Growth Brief — {today_str}"
    body = build_email(topic, reel_script, growth_tips, today_str, day_name)

    # 5. Send
    print(f"\nSending brief to {YOUR_EMAIL}...")
    send_morning_brief(subject, body)

    print("\n--- PREVIEW ---")
    print(body[:800])
    print("...")


if __name__ == "__main__":
    main()
