# Nigerian Job Intelligence System

An automated pipeline that scrapes Nigerian job listings from Jobberman, stores them in PostgreSQL, and delivers a curated daily digest to a Telegram channel. Runs continuously on a 6-hour schedule with full deduplication — only new jobs trigger a notification.

---

## What It Does

- Deploys a headless Chromium browser to scrape live job listings from Jobberman
- Validates every listing through a Pydantic data model before saving
- Stores jobs in PostgreSQL with automatic deduplication (same job never saved twice)
- Sends formatted alerts to a Telegram channel with title, company, location, salary, and direct link
- Handles Telegram rate limiting automatically with retry logic
- Logs all activity to both terminal and `app.log`

---

## Business Value

This system solves a real problem: Nigerian job seekers check multiple sites manually every day. This pipeline does that work automatically and delivers results directly to their phone.

Immediate monetization paths:
- Charge subscribers ₦2,000–5,000/month for niche job alerts (tech only, remote only, etc.)
- Sell the lead data as a market intelligence report to recruiters
- White-label the pipeline for a specific industry or company size

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Playwright (headless Chromium) + BeautifulSoup |
| Data Validation | Pydantic v2 |
| Database | PostgreSQL via psycopg2 |
| Notifications | Telegram Bot API |
| Scheduling | schedule |
| Config | python-dotenv |

---

## Project Structure

```
nigerian-job-intelligence/
├── main.py                  # Entry point — runs the full pipeline on a schedule
├── config.py                # Centralised config and constants
├── requirements.txt
├── .env.example             # Template for required environment variables
├── .gitignore
├── scrapers/
│   └── jobberman.py         # Playwright scraper for Jobberman.com
├── models/
│   └── job.py               # Pydantic Job model — validates all scraped data
├── database/
│   └── vault.py             # PostgreSQL connection, table init, save, fetch
└── notifier/
    └── telegram.py          # Telegram message formatting and delivery
```

---

## Setup

**1. Clone the repo and create a virtual environment**
```bash
git clone https://github.com/exceliyoha53/nigerian-job-intelligence.git
cd nigerian-job-intelligence
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
playwright install chromium
```

**2. Set up PostgreSQL**

Create a database named `nigerian_jobs`:
```sql
CREATE DATABASE nigerian_jobs;
```

**3. Configure environment variables**

Copy `.env.example` to `.env` and fill in your values:
```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHANNEL_ID=your_channel_id
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/nigerian_jobs
```

To get your Telegram channel ID: add your bot as an admin to a channel, then forward any message from that channel to `@username_to_id_bot`.

**4. Run**
```bash
python main.py
```

The system initializes the database, runs an immediate scrape, then schedules itself every 6 hours. Press `Ctrl+C` to stop.

---

## How the Pipeline Works

```
main.py (every 6 hours)
    │
    ├── scrape_jobberman()     →  Jobberman.com (3 pages, ~48 jobs)
    │
    ├── save_jobs()            →  PostgreSQL
    │       └── ON CONFLICT DO NOTHING  (deduplication)
    │
    └── send_daily_digest()    →  Telegram channel
            └── only if new_count > 0
```

On each run, only jobs with URLs not already in the database are inserted. The Telegram digest is capped at 20 jobs per run with 1.2s between messages to respect Telegram's rate limits.

---

## Extending This System

- **Add more sources**: Create a new scraper in `scrapers/` following the same pattern as `jobberman.py`. Add it to the pipeline in `main.py`.
- **Filter by category**: Add a `category` column to the jobs table and filter `fetch_recent_jobs()` by it — e.g. tech jobs only.
- **Deploy**: Containerize with Docker and run on a DigitalOcean droplet or Railway.app for 24/7 uptime without your laptop.

---

## Author

Excel Iyoha — Telecommunications Engineering student, building automation systems and remote-ready software.  
[GitHub](https://github.com/exceliyoha53) · [LinkedIn](https://www.linkedin.com/in/excel-iyoha/)