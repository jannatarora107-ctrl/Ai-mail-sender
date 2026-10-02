"""
═══════════════════════════════════════════════════════════════
  Yash Arora (@yashwebsites) — Daily Morning Brief
  Runs every morning at 8:00 AM IST via GitHub Actions
  Sends a ready-to-use reel script + growth strategy to inbox
═══════════════════════════════════════════════════════════════
"""

import os
import re
import json
import ssl
import random
import smtplib
import urllib.request
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# ─── Config ─────────────────────────────────────────────────
SENDER_NAME   = "Yash Bot"
SENDER_EMAIL  = os.environ.get("GMAIL_ADDRESS", "yasha7080@gmail.com")
APP_PASSWORD  = os.environ.get("GMAIL_APP_PASSWORD", "")
ATRIA_API_KEY = os.environ.get("ATRIA_API_KEY", "atr_crgUcm9y8AlDpRbav_ogZGG0iMLKiIvU")
YOUR_EMAIL    = "yasha7080@gmail.com"

# ─── Topic Pool (rotates daily by day-of-year) ──────────────
TOPICS = [
    ("AI tools", "5 free AI tools that are making designers rich in 2025"),
    ("AI tools", "I replaced my entire design workflow with AI — here's what happened"),
    ("AI tools", "Top AI agents that literally do your work while you sleep"),
    ("AI tools", "ChatGPT vs Claude vs Gemini — honest review for freelancers"),
    ("AI tools", "How I use Cursor AI to build client websites in 1 day"),
    ("freelancing", "My exact process for getting 3 new clients every month"),
    ("freelancing", "Why your portfolio is losing you clients — and how to fix it"),
    ("freelancing", "The cold email system I used to get 5 clients in 2 weeks"),
    ("freelancing", "How to charge 3x more for the same design work"),
    ("freelancing", "Freelancing vs job — my honest 1-year comparison"),
    ("web design", "5 website mistakes that are killing your client's sales"),
    ("web design", "How to build a full website in under 24 hours"),
    ("web design", "Framer vs Webflow vs WordPress — which one in 2025"),
    ("web design", "Why your client's website needs a mobile-first redesign"),
    ("graphic design", "Design trends killing it right now — Oct 2025"),
    ("graphic design", "How I create a full brand kit in 2 hours"),
    ("graphic design", "Typography tricks that make cheap designs look expensive"),
    ("personal brand", "How to grow from 0 to 1000 followers as a design creator"),
    ("personal brand", "My honest monthly income as a 22-year-old freelancer"),
    ("personal brand", "Why I post reels even when nobody watches — and why you should too"),
]

# ─── Pre-Written Viral Scripts (Curated & Tested) ───────────
TOPIC_SCRIPTS = {
    "5 free AI tools that are making designers rich in 2025":
"""HOOK:
5 free AI tools jo designers ko 2025 mein seriously ahead kar rahe hain.

MAIN CONTENT:
Pehla — Cursor AI. Code likhna ab drag-and-drop jaisa hai. Client website 5 ghante mein ready.
Doosra — Adobe Firefly. Stock photos kharidna band. Custom assets seedha generate karo.
Teesra — Notion AI. Client proposals, meeting notes, project plans — sab ek click mein.
Chautha — ElevenLabs. Studio-quality voiceover teri awaaz mein, recording kharcha zero.
Paanchwa — Kling AI. Product video ads automatically generate karta hai.
Ye sab free hain. Ya ek pizza se bhi saste.

OUTRO + CTA:
Inme se kaunsa use karta hai tu? Comment mein bata. Follow karo — har hafte ek naya AI tool.

CAPTION: 5 free AI tools that are replacing expensive design software in 2025
HASHTAGS: #aitools #designerlife #freelancertips #worksmarter #aifordesigners""",

    "I replaced my entire design workflow with AI — here's what happened":
"""HOOK:
Maine apna poora freelance workflow AI se replace kar diya. Honest results sun lo.

MAIN CONTENT:
Logo & Graphics — Firefly se baseline assets, main sirf typography aur arrange karta hoon. Kaam 70% fast.
Client proposals — Claude draft karta hai, main edit karta hoon. 45 minute se 8 minute.
Social posts — AI se captions aur hooks suggest hote hain. Engagement actually double hua.
Meeting notes — Automatic transcription, client ka ek bhi point miss nahi hota.
Jo replace nahi hua — client relationship aur trust. Wo tu khud hi build karega.
Result? Roz 2 ghante bachte hain — wo naye clients outreach karne mein jaate hain.

OUTRO + CTA:
Kaunsa part of your work sabse zyada time leta hai? Comment mein likh — solution bataunga.

CAPTION: I replaced my design workflow with AI for 30 days — honest results
HASHTAGS: #aiworkflow #designerlife #productivityhacks #aiforcreatives #freelancetips""",

    "Top AI agents that literally do your work while you sleep":
"""HOOK:
Raat ko so gaya. Subah uthke dekha — 3 client tasks already done. AI agents ki reality ye hai.

MAIN CONTENT:
Agent 1: Zapier AI — website leads aate hi Google Sheets update aur initial email sent. Automatically.
Agent 2: Relevance AI — company website scan karta hai aur customized pitch point ready karta hai.
Agent 3: Make dot com — invoice generate karke payment link WhatsApp aur email dono pe send karta hai.
Log sochte hain ye complicated hai. Truth ye hai — 30 minute mein setup ho jata hai.
Ye future nahi hai, ye aaj chal raha hai.

OUTRO + CTA:
Ek bhi AI agent set up karna chahta hai? Comment mein "SETUP" likh — step-by-step tutorial share karunga.

CAPTION: AI agents that work while you sleep — real tools, no buzzwords
HASHTAGS: #aiagents #automation #freelancerlife #aitools #worksmarter""",

    "ChatGPT vs Claude vs Gemini — honest review for freelancers":
"""HOOK:
Teen AI models, teen mahine use kiya — freelancers ke liye kaunsa genuinely best hai?

MAIN CONTENT:
ChatGPT — Best for quick brainstorming aur cold email hooks. Fast hai, but kabhi kabhi generic sound karta hai.
Claude — Best for long proposals aur human-like copywriting. Client emails ke liye number one.
Gemini — Best for research aur factual data integration with Google tools.
Mera workflow — Idea ChatGPT se, client email Claude se, and research Gemini se.
Kisi ka bhi paid plan lene ki zarurat nahi — free tier se sab ho jata hai.

OUTRO + CTA:
Tu roz kaunsa AI model use karta hai? Comment mein bata.

CAPTION: ChatGPT vs Claude vs Gemini — honest freelancer review after 90 days
HASHTAGS: #chatgpt #claude #gemini #aitools #freelancertips""",

    "How I use Cursor AI to build client websites in 1 day":
"""HOOK:
Client ne Sunday ko website maangi — Monday subah live kardi. Cursor AI ka exact process.

MAIN CONTENT:
Prompt likha: "Local bakery mobile-first landing page with Instagram feed & booking form."
20 minute mein full clean code structure ready.
Main code scratch se nahi likhta — Cursor code likhta hai, main sirf brand styling polish karta hoon.
Forms test kiye, domain connect kiya, deploy. Total time — 5 ghante.
Client khush, Rs. 8,000 in the bank, aur Monday free.

OUTRO + CTA:
Cursor AI try kiya hai ya dar lagta hai coding se? Comment mein bata — guide dunga.

CAPTION: Built a full client website in 1 day with Cursor AI — here's how
HASHTAGS: #cursorai #webdev #freelancewebdesigner #aitools #webdesign""",

    "My exact process for getting 3 new clients every month":
"""HOOK:
Har mahine 3 naye high-paying clients. No paid ads, no begging in DMs. Ye exact system hai.

MAIN CONTENT:
Step 1: Monday ko 10 Tier-2 city businesses dhundhta hoon jinka website mobile pe broken hai.
Step 2: Unke owner ko ek short 60-word email bhejta hoon. Zero sales pitch, sirf problem point out karta hoon.
Step 3: Free visual mockup offer karta hoon — bina paise maange.
Step 4: 10 mein se 4 reply karte hain, 2 convert ho jaate hain.
Step 5: 4 din baad baki 6 ko ek simple 2-line follow-up. 1 aur convert.
Total: 3 clients per month, consistently.

OUTRO + CTA:
Tu client outreach kaise karta hai? Comment mein likh — template improve karne mein help karunga.

CAPTION: My exact repeatable system for 3 clients every month — no paid ads
HASHTAGS: #getclients #freelancingsystem #coldoutreach #designfreelancer #clientacquisition""",

    "Why your portfolio is losing you clients — and how to fix it":
"""HOOK:
Client ne portfolio dekha aur ghost kar diya. Galti tere design ki nahi — presentation ki hai.

MAIN CONTENT:
Mistake 1: 15 projects upload kiye hain. Client confuse ho gaya. Sirf best 3 dikhao.
Mistake 2: Sirf pictures hain, story nahi. Likho: "Client ka problem kya tha, aur maine kaise solve kiya."
Mistake 3: Mobile pe 6 second lagte hain load hone mein. Tab tak client chala gaya.
Mistake 4: Contact button page ke end mein chupa hai. Har project ke neeche clear CTA rakho.
Ye 4 changes karke dekho — response rate 3x ho jayega.

OUTRO + CTA:
Apna portfolio link comment mein drop kar — honest 1-minute feedback dunga.

CAPTION: Your portfolio is losing you clients — here are 4 instant fixes
HASHTAGS: #portfoliotips #designportfolio #freelancedesigner #getclients #uxdesign""",

    "The cold email system I used to get 5 clients in 2 weeks":
"""HOOK:
60 cold emails, 5 paying clients, 2 hafte mein. Ye cold outreach ka golden rule hai.

MAIN CONTENT:
Rule 1: Subject line mein sirf 4 words. Example: "quick question for bake me happy".
Rule 2: Email body under 70 words. Agar mobile pe scroll karna pade, email delete ho jata hai.
Rule 3: Owner ka naam use karo, aur unki profile se ek specific cheez mention karo.
Rule 4: Zero links, zero PDFs in first mail. Direct primary inbox delivery.
Rule 5: End with an easy question: "Can I send a quick free sample?"
8% conversion rate. Free tools se.

OUTRO + CTA:
Cold email ka dar lagta hai? Comment mein "EMAIL" likh — exact template bhej dunga.

CAPTION: 60 cold emails, 5 clients, 2 weeks — the exact cold email formula
HASHTAGS: #coldemail #freelancingsystem #getclients #emailmarketing #designfreelancer""",

    "How to charge 3x more for the same design work":
"""HOOK:
Same kaam, same hours — lekin ab client 3 guna zyada pay karta hai. Sirf ek word change kiya.

MAIN CONTENT:
Pehle bolta tha: "Main aapka logo design kar dunga Rs. 1000 mein." Client bargain karta tha.
Ab bolta hoon: "Main aapke brand ka identity kit banaunga jo new customers attract kare."
Deliverable same hai — framing alag hai.
Log deliverables ke liye bargain karte hain, results ke liye premium pay karte hain.
Service bechna band karo, business outcome bechna shuru karo.

OUTRO + CTA:
Abhi tu ek project ka kitna charge karta hai? Comment mein bata — package structure banata hoon.

CAPTION: Same design work, 3x higher price — how to value-price your services
HASHTAGS: #pricingstrategy #freelancetips #designbusiness #valuepricing #getpaidmore""",

    "Freelancing vs job — my honest 1-year comparison":
"""HOOK:
Ek saal freelancing vs regular 9-to-5 job. Sabse honest reality check jo tu sunega.

MAIN CONTENT:
Money: Freelancing mein ceiling nahi hai. Best month Rs. 28,000 tha, worst month Rs. 4,000.
Freedom: Wednesday dopehar ko so sakte ho. Lekin deadline Friday ko hai toh raat 3 baje kaam bhi karna padega.
Boss: Job mein ek boss hota hai. Freelancing mein har client tera boss hota hai.
Skill growth: 1 saal freelancing mein 3 saal ki job jitna seekha — design, sales, finance, client management.
Verdict: Agar tu self-discipline maintain kar sakta hai — freelancing wins hands down.

OUTRO + CTA:
Full-time freelancing ka soch raha hai? Tera sabse bada dar kya hai comment mein bata.

CAPTION: 1 year of full-time freelancing vs 9-to-5 job — honest comparison
HASHTAGS: #freelancingvsjob #freelancelife #designcareer #jobvsfreelance #careeradvice""",

    "5 website mistakes that are killing your client's sales":
"""HOOK:
Client bol raha hai website se orders nahi aa rahe. Ye 5 galtiyan check karo unki site pe.

MAIN CONTENT:
1. No clear headline: Visitor 3 second mein nahi samjha kya milta hai yahan.
2. Slow mobile load: 4 second wait = 50% visitors bounce back.
3. Form too long: Name, email, phone ke alawa 10 faltu questions.
4. No trust proof: Reviews ya client photos gayab hain.
5. CTA button chupa hua: Call-to-action har scroll pe visible hona chahiye.
Ye sab fix karne mein sirf 2 ghante lagte hain — client ko pitch karo aur charge karo.

OUTRO + CTA:
Apne client ki site check kar abhi. Kaunsi galti mili comment mein bata.

CAPTION: 5 website mistakes that kill sales — how designers can pitch the fix
HASHTAGS: #websitedesign #conversionoptimization #webdesigntips #freelancewebdesigner #uxdesign""",

    "How to build a full website in under 24 hours":
"""HOOK:
Client ka urgent deadline tha. 24 ghante mein full polished website live kardi. Process ye hai.

MAIN CONTENT:
Hours 1-3: Content aur branding finalize — colors, font, and 5 key sections.
Hours 4-10: Framer template choose karke custom assets and copy replace kiye.
Hours 11-14: Mobile responsiveness perfect ki — 80% visitors phone pe hote hain.
Hours 15-18: Contact forms connect kiye, domain DNS point kiya, SSL verify.
Hours 19-24: Client review and final polish.
Never start from a blank canvas. Smart designers use systems, not ego.

OUTRO + CTA:
Ek website banane mein tujhe kitne din lagte hain? Comment mein likh.

CAPTION: How I deliver complete client websites in under 24 hours
HASHTAGS: #webdesign #framer #webflow #freelancewebdesigner #websitedevelopment""",

    "Framer vs Webflow vs WordPress — which one in 2025":
"""HOOK:
Framer, Webflow ya WordPress? 2025 mein freelance designer ke liye kaunsa best hai.

MAIN CONTENT:
WordPress: Great for large blogs and complex e-commerce. Bad for modern animations and speed.
Webflow: Industry standard for agencies. Powerful, but learning curve steep hai.
Framer: Absolute king for designers in 2025. Figma se direct copy-paste, ultra-fast hosting.
Mera recommendation: Agar client portfolio, agency, ya business showcase site chahiye — Framer choose karo.
Speed 3x fast hai aur client effortlessly manage kar sakta hai.

OUTRO + CTA:
Tu abhi kis platform pe sites banata hai? Comment mein bata.

CAPTION: Framer vs Webflow vs WordPress in 2025 — which one to learn?
HASHTAGS: #framer #webflow #wordpress #webdesign #freelancewebdesigner""",

    "Why your client's website needs a mobile-first redesign":
"""HOOK:
Client ko lagta hai unki website sundar hai. Lekin 80% customers use phone pe dekh rahe hain — aur wahan sab broken hai.

MAIN CONTENT:
Desktop layout mobile pe cramped ho jata hai.
Text itna chota hota hai ki zoom karna padta hai.
Buttons itne pass hote hain ki wrong click ho jata hai.
Google rankings desktop se nahi, mobile version se decide karta hai.
Jab client ko unki site phone pe screen record karke dikhaoge — wo redesign ke liye instantly ready ho jayenge.
Best pitch in 2025.

OUTRO + CTA:
Apna portfolio phone pe kholo abhi — text readable hai? Comment mein honest check bata.

CAPTION: 80% of users are on mobile — why mobile-first design wins clients
HASHTAGS: #mobiledesign #responsivedesign #webdesigntips #mobilefirst #freelancewebdesigner""",

    "Design trends killing it right now — Oct 2025":
"""HOOK:
Oct 2025 ke 4 hottest design trends jo high-paying clients ko instantly attract kar rahe hain.

MAIN CONTENT:
Trend 1: Bento grids — Apple-style clean card layouts. Scannable and modern.
Trend 2: Bold brutalist typography — Huge headlines with high contrast.
Trend 3: Subtle micro-interactions — Hover states jo interface ko interactive feel karwate hain.
Trend 4: Dark glassmorphism — Sleek, dark themes with frosted glass accents.
Ye sab implement karne ke liye expensive plugins nahi chahiye — basic CSS and good taste.

OUTRO + CTA:
Inme se kaunsa trend tere current project mein fit hota hai? Comment mein bata.

CAPTION: 4 visual design trends dominating client projects in late 2025
HASHTAGS: #designtrends #graphicdesign #uidesign #designinspiration #2025trends""",

    "How I create a full brand kit in 2 hours":
"""HOOK:
Client ne brand kit maangi — 2 ghante mein deliver karke Rs. 4,500 banaye. Ye mera step-by-step framework hai.

MAIN CONTENT:
Minute 0-20: Client survey analysis — primary audience, competitor palette, mood.
Minute 20-50: Color palette (6 hex codes) + 2 matching font pairings in Figma.
Minute 50-90: Logo in 3 formats — primary, compact icon, and inverted monochrome.
Minute 90-110: 3 social announcement templates and business card mockup.
Minute 110-120: 1-page Brand Guidelines PDF export.
Client ko structured kit milti hai, mujhe 2 ghante mein payment.

OUTRO + CTA:
Brand kit banane mein sabse zyada time kahan lagta hai? Comment mein bata — shortcut dunga.

CAPTION: Complete client brand kit in 2 hours — exact step-by-step workflow
HASHTAGS: #brandidentity #brandkit #graphicdesigner #logodesign #brandingtips""",

    "Typography tricks that make cheap designs look expensive":
"""HOOK:
Ek simple font change se client ne bina bargain kiye invoice pay kiya. Typography ka magic ye hai.

MAIN CONTENT:
Trick 1: Maximum 2 font families. Ek bold heading font, ek neutral body font.
Trick 2: Uppercase titles mein letter-spacing thoda badhao (+2% to +5%). Instantly luxury feel aata hai.
Trick 3: Body text line-height 150% se 160% rakho. Crowded text amateur lagti hai.
Trick 4: Pure black (#000000) text avoid karo — dark charcoal (#1A1A1A) use karo softer read ke liye.
Free fonts like Inter, Plus Jakarta Sans, and Playfair Display are all you need.

OUTRO + CTA:
Agli design mein ye letter-spacing trick try karna. Comment mein apna favorite font batao.

CAPTION: 4 simple typography tricks that make any design look premium
HASHTAGS: #typography #graphicdesigntips #designtricks #fontsofinstagram #designeducation""",

    "How to grow from 0 to 1000 followers as a design creator":
"""HOOK:
0 se 1,000 Instagram followers — 90 din mein. 3 cheezein jo actually kaam aayi.

MAIN CONTENT:
Rule 1: Problem-solving reels post karo, aesthetic portfolio showcases nahi. Logo ko help chahiye, bragging nahi.
Rule 2: Roz 15 minutes apne niche ke dusre creators ke comments mein genuine value add karo.
Rule 3: Hook pe 50% time spend karo. Agar pehle 3 second weak hain, baaki 40 second koi nahi dekhega.
Numbers mat track karo pehle 30 din — consistency track karo. Reach follow karegi.

OUTRO + CTA:
Abhi tera follower count kitna hai? Comment mein likh — 30 din baad progress check karenge.

CAPTION: 0 to 1,000 design followers in 90 days — 3 rules that actually work
HASHTAGS: #instagramgrowth #growfollowers #designercommunity #contentcreator #personalbranding""",

    "My honest monthly income as a 22-year-old freelancer":
"""HOOK:
22 saal ka freelancer, ye mahine exactly kitna kamaya — raw honest numbers.

MAIN CONTENT:
Client 1: Small business website on Framer — Rs. 14,000.
Client 2: Full brand identity kit & menu design — Rs. 6,500.
Client 3: Monthly social media creative retainer — Rs. 5,000.
Total revenue: Rs. 25,500.
Expenses (Figma, domain, internet): Rs. 2,800.
Net profit: Rs. 22,700.
Koi get-rich-quick nahi hai — hard work hai, cold emails hain, but independence priceless hai.

OUTRO + CTA:
Freelancing mein sabse mushkil part kya lagta hai? Comment mein discuss karte hain.

CAPTION: Honest monthly freelance income breakdown — real numbers, no fake flex
HASHTAGS: #freelanceincome #freelancerlife #designbusiness #honestcreator #incomebreakdown""",

    "Why I post reels even when nobody watches — and why you should too":
"""HOOK:
Meri ek reel pe sirf 38 views aaye the. Phir bhi maine daily post kiya. Reason sun lo.

MAIN CONTENT:
Jab views kam hote hain — algorithm test kar raha hota hai ki tu consistent hai ya quit kar dega.
Har ek reel jo tu banata hai — teri camera confidence aur hook writing improve hoti hai.
Wahi 38 views dekh kar ek local business owner ne mujhe DM kiya aur Rs. 6,000 ka project diya.
Views vanity metrics hain — 100 views mein se 1 genuine client milna is a win.
Keep showing up. Ek reel poora game change kar sakti hai.

OUTRO + CTA:
Low views se demotivate hote ho? Comment mein "YES" likho — consistency group banate hain.

CAPTION: Why I post reels even with low views — the mindset shift every creator needs
HASHTAGS: #reelsstrategy #instagramreels #contentcreator #growthstrategy #designcreator""",
}

# ─── Weekday Growth Strategies ──────────────────────────────
GROWTH_TIPS = {
    0: """1. WHAT TO POST: Carousel or Educational Reel — Monday audience is focused and saves actionable tips.
2. BEST TIME: 7:30 PM - 8:30 PM IST (peak evening scroll time).
3. ENGAGEMENT TRICK: Add "Save this for your next project" on the last frame — saves boost algorithm distribution.
4. GROWTH ACTION: Leave thoughtful insights on 5 creators' posts in #webdesign or #freelancer.
5. TRENDING ANGLE: "AI workflow hacks" content is getting 2.5x more shares this week.""",

    1: """1. WHAT TO POST: Quick Problem-Solution Reel (45s) — Tuesday audience responds best to punchy tips.
2. BEST TIME: 6:30 PM - 7:30 PM IST.
3. ENGAGEMENT TRICK: Reply to every comment within 20 minutes with a question to start a thread.
4. GROWTH ACTION: DM 3 people who liked your recent reels and thank them personally.
5. TRENDING ANGLE: Behind-the-scenes client transformations (before vs after).""",

    2: """1. WHAT TO POST: Interactive Story Polls + 1 Quick Tool Highlight.
2. BEST TIME: 1:00 PM - 2:00 PM IST (lunch break) or 8:00 PM IST.
3. ENGAGEMENT TRICK: Use "This or That" stickers in Stories — gives you 5x more story interactions.
4. GROWTH ACTION: Reach out to 1 local cafe/shop on Instagram offering a free visual suggestion.
5. TRENDING ANGLE: "Framer vs WordPress" debates are driving massive comment sections right now.""",

    3: """1. WHAT TO POST: In-depth Carousel or Step-by-Step Tutorial.
2. BEST TIME: 7:00 PM - 8:30 PM IST.
3. ENGAGEMENT TRICK: Ask for a 1-word answer in the caption to minimize comment friction.
4. GROWTH ACTION: Optimize your Instagram bio — ensure your niche and clear offer are in the top 2 lines.
5. TRENDING ANGLE: "Mistakes I made as a beginner" resonates deeply with young creators.""",

    4: """1. WHAT TO POST: Relatable / Career Reel or Freelance Reality Check.
2. BEST TIME: 5:00 PM - 7:00 PM IST (pre-weekend high energy).
3. ENGAGEMENT TRICK: Use "Share this with a friend who needs to start freelancing" as your CTA.
4. GROWTH ACTION: Post 3 casual Stories showing your desk setup or what you're working on.
5. TRENDING ANGLE: Income breakdowns and honest freelancing numbers convert the highest profile visits.""",

    5: """1. WHAT TO POST: Quick Visual Inspiration or Design Trick Reel.
2. BEST TIME: 11:00 AM - 1:00 PM IST (relaxed weekend morning).
3. ENGAGEMENT TRICK: Start with a slightly contrarian hook ("Why I don't use X tool").
4. GROWTH ACTION: Connect with 2 other design creators for a potential story shoutout exchange.
5. TRENDING ANGLE: Clean UI animations and aesthetic mobile mockups.""",

    6: """1. WHAT TO POST: Reflection Carousel / Weekly Lessons or High-Value Resource List.
2. BEST TIME: 11:30 AM - 1:30 PM IST or 8:00 PM IST.
3. ENGAGEMENT TRICK: Tease next week's content in your story to build anticipation.
4. GROWTH ACTION: Plan 3 reel topics for the upcoming week so you never wake up without a script.
5. TRENDING ANGLE: "Best free resources of the week" roundups get massive bookmark rates.""",
}

# ─── Atria AI Engine ─────────────────────────────────────────
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def ask_atria(system_prompt, user_prompt, max_tokens=1000):
    """
    Call Atria-Dawn-Preview agentic reasoning model with streaming
    and a strict 15-second deadline.
    """
    if not ATRIA_API_KEY:
        return None

    import socket
    import time
    start_t = time.time()

    payload = json.dumps({
        "model": "Atria-Dawn-Preview",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": True,
        "max_tokens": max_tokens
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.atria-asi.ai/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {ATRIA_API_KEY}", "Content-Type": "application/json"}
    )

    content = []
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            for line in resp:
                if time.time() - start_t > 15:
                    break
                line_str = line.decode('utf-8').strip()
                if not line_str or line_str == "data: [DONE]":
                    continue
                if line_str.startswith("data: "):
                    try:
                        chunk = json.loads(line_str[6:])
                        choices = chunk.get("choices", [])
                        if not choices:
                            continue
                        delta = choices[0].get("delta", {})
                        if "content" in delta and delta["content"]:
                            content.append(delta["content"])
                    except Exception:
                        pass
        result = "".join(content).strip()
        if len(result) > 80:
            return result
    except Exception as e:
        print(f"  [AI note: {e}] — using curated script")
    return None


def get_reel_script(topic_title, category):
    """Try Atria for a fresh custom take, fallback to curated script."""
    system = (
        "You are a viral Instagram Reels scriptwriter for Indian creator @yashwebsites (Yash Arora, freelance web designer & graphic designer). "
        "Tone: Frank, conversational Hinglish/English. No corporate jargon. No fluff. "
        "Format: HOOK (first 3s), MAIN CONTENT (4 short punchy lines), OUTRO + CTA, CAPTION, HASHTAGS."
    )
    prompt = f"Write a 45-second reel script on: '{topic_title}'. Target audience: Young Indian creators, freelancers, and designers."

    ai_script = ask_atria(system, prompt, max_tokens=1000)
    if ai_script:
        return ai_script

    # Fallback to high-quality curated script
    return TOPIC_SCRIPTS.get(topic_title, list(TOPIC_SCRIPTS.values())[0])


# ─── Email Builder ──────────────────────────────────────────
def build_email(topic_title, reel_script, growth_tips, today_str, day_name):
    divider = "-" * 55
    return f"""Good morning Yash,

Here is your daily creator brief for {day_name}, {today_str}.

{divider}
TODAY'S REEL TOPIC
{divider}
{topic_title}

{divider}
READY-TO-FILM REEL SCRIPT
{divider}
{reel_script}

{divider}
PAGE GROWTH ACTION PLAN FOR TODAY
{divider}
{growth_tips}

{divider}
DAILY CHECKLIST
{divider}
- Film before 11:00 AM or after 5:00 PM for best lighting
- Keep face in the first 2 seconds for algorithm retention
- Reply to all comments within 30 minutes of posting
- Post 2-3 interactive Stories today
- Cold email outreach automation fires automatically tonight at 8:20 PM IST

{divider}
Tomorrow's brief arrives at 8:00 AM IST.
-- Yash Bot
"""


# ─── SMTP Sender ─────────────────────────────────────────────
def send_email(subject, body):
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("[SMTP] Missing Gmail credentials")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg["To"] = YOUR_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as srv:
            srv.starttls()
            srv.login(SENDER_EMAIL, APP_PASSWORD)
            srv.sendmail(SENDER_EMAIL, YOUR_EMAIL, msg.as_string())
        print(f"[SUCCESS] Brief delivered to {YOUR_EMAIL}")
        return True
    except Exception as e:
        print(f"[FAILED] SMTP Error: {e}")
        return False


# ─── Main ────────────────────────────────────────────────────
def main():
    today = datetime.date.today()
    today_str = today.strftime("%d %B %Y")
    day_name = today.strftime("%A")
    weekday_num = today.weekday()

    print("=" * 60)
    print(f"  YASH MORNING BRIEF — {day_name}, {today_str}")
    print("=" * 60)

    # Pick topic rotating by day of year
    idx = today.timetuple().tm_yday % len(TOPICS)
    category, topic_title = TOPICS[idx]
    print(f"\nToday's Topic: {topic_title} ({category})")

    # Get reel script
    print("Preparing reel script...")
    reel_script = get_reel_script(topic_title, category)

    # Get growth plan
    growth_tips = GROWTH_TIPS.get(weekday_num, GROWTH_TIPS[0])

    # Send
    subject = f"[{day_name}] Reel Script: {topic_title[:45]}"
    body = build_email(topic_title, reel_script, growth_tips, today_str, day_name)

    print(f"Sending brief to {YOUR_EMAIL}...")
    send_email(subject, body)

    print("\n--- PREVIEW OF DELIVERED EMAIL ---")
    print(body[:800])
    print("...")


if __name__ == "__main__":
    main()
