# Yash Arora — AI-Powered Cold Outreach Engine

Fully autonomous cold email system that runs 24/7 on GitHub Actions.

## What It Does

- **Discovers leads** by searching Tier-2 cities where small shop owners actually read their email
- **Writes unique emails** using AI (OpenRouter) — no two emails look the same
- **Sends at human pace** with 2-4 minute gaps between emails
- **Follows up automatically** — gentle bump at 4 days, final note at 10 days
- **Respects "stop" replies** — permanent do-not-contact blocklist
- **Commits results** back to this repo after every run

## Architecture

```
autonomous_5hr_pipeline.py    ← Main runner (4 phases)
    └── lead_engine.py        ← Core: AI emails, SMTP, filtering
        ├── leads_database.json
        ├── do_not_contact.json
        └── sent_emails_log.txt
```

## Phases

| Phase | Duration | What Happens |
|-------|----------|-------------|
| 1 — Discovery | 90 min | Searches for business owner emails in target cities |
| 2 — Cooldown | 30 min | Deduplicates, cleans blocklist, quality check |
| 3 — Dispatch | 120 min | AI-crafts and sends cold emails (max 35/day) |
| 4 — Follow-ups | 30 min | Sends follow-up #1 (4d) and #2 (10d) to old leads |

## Services Offered

| Service | Price |
|---------|-------|
| Custom Brand Creatives & Announcement Cards | $5–$10 |
| QR Digital Menu & Catalog | $15–$20 |
| 1-Page Mobile Showcase | $25–$35 |

## Target Cities (Tier-2 Hubs)

Grand Rapids MI · Columbus OH · Salt Lake City UT · Charlotte NC · Manchester UK · Leeds UK · Eindhoven NL

## Schedule

Runs daily at **8:20 PM IST** (14:50 UTC) via GitHub Actions cron.

## Secrets Required

| Secret | Description |
|--------|-------------|
| `GMAIL_ADDRESS` | Your Gmail (e.g. yasha7080@gmail.com) |
| `GMAIL_APP_PASSWORD` | Gmail App Password (16 chars) |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI email generation |

## Local Usage

```bash
# Dry run (simulation)
python daily_pipeline.py

# Live send
python daily_pipeline.py --send

# Test all phases quickly
python autonomous_5hr_pipeline.py --test
```

---
*Built by Yash Arora · Independent Digital Designer*
