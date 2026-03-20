import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jobs.db")

SCRAPE_INTERVAL_HOURS = 6

JOBBERMAN_URL = "https://www.jobberman.com/jobs"