import logging
import requests
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text: str) -> bool:
    """
    Sends a single text message to the channel.
    Returns True if successful, False if it failed.
    """
    url = f"{TELEGRAM_API}/sendMessage"

    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False
    
def format_job_message(job: dict) -> str:
    """
    Takes a job dict and returns a formatted Telegram message string.
    """

    salary_line = f"💰 <b>Salary:</b> {job['salary']}" if job['salary'] else "💰 <b>Salary:</b> Not listed"

    return (
        f"🆕 <b>{job['title']}</b>\n"
        f"🏢 {job['company']}\n"
        f"📍 {job['location']}\n"
        f"{salary_line}\n"
        f"🔗 <a href='{job['job_url']}'>View Job</a>"
    )

def send_daily_digest(jobs: List[dict]) -> None:
    """
    Sends a header message then one message per job.
    This is what gets called by main.py on each scheduled run.
    """
    if not jobs:
        logger.info("No new jobs to send.")
        return
    
    send_message(f"📢 <b>Nigerian Jobs Digest</b>\n{len(jobs)} new jobs found\n{'─'*20}")

    sent = 0
    for job in jobs:
        message = format_job_message(job)
        success = send_message(message)
        if success:
            sent += 1

    logger.info(f"Digest sent: {sent}/{len(jobs)} messages delivered.")
