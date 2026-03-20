import schedule
import time
import logging
import sys
from database.vault import init_vault, save_jobs, fetch_recent_jobs
from scrapers.jobberman import scrape_jobberman
from notifier.telegram import send_daily_digest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout) 
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    """
    The full pipeline — scrape, save, notify.
    This is the function schedule calls every 6 hours.
    """
    logger.info("=" * 50)
    logger.info("PIPELINE STARTED")
    logger.info("=" * 50)

    logger.info("Step 1: Scraping Jobberman...")
    jobs = scrape_jobberman(max_pages=3)

    if not jobs:
        logger.warning("No jobs scraped. Aborting pipeline.")
        return

    logger.info("Step 2: Saving to PostgreSQL vault...")
    new_count = save_jobs(jobs)
    logger.info(f"Result: {new_count} new jobs added out of {len(jobs)} scraped.")

    if new_count == 0:
        logger.info("Step 3: No new jobs — skipping Telegram notification.")
        return

    logger.info(f"Step 3: Sending {new_count} new jobs to Telegram...")

    recent_jobs = fetch_recent_jobs(limit=new_count)
    send_daily_digest(recent_jobs)

    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 50)


if __name__ == "__main__":
    logger.info("Initializing Nigerian Job Intelligence System...")

    init_vault()

    logger.info("Running initial pipeline on startup...")
    run_pipeline()

    schedule.every(6).hours.do(run_pipeline)
    logger.info("Scheduler armed. Pipeline will run every 6 hours.")
    logger.info("Press Ctrl+C to shut down.\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received. System offline.")