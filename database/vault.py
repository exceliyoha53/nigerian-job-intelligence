import psycopg2
import logging
import os
from dotenv import load_dotenv
from typing import List
from models.job import Job


load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """
    Opens and returns a fresh connection to PostgreSQL.
    """
    return psycopg2.connect(DATABASE_URL)

def init_vault():
    """
    Creates the jobs table if it doesn't exist yet.
    Run this once at startup — safe to call multiple times.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          SERIAL PRIMARY KEY,
            title       TEXT NOT NULL,
            company     TEXT NOT NULL,
            location    TEXT,
            salary      TEXT,
            job_url     TEXT UNIQUE NOT NULL,
            source      TEXT,
            scraped_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("PostgreSQL vault initialized.")


def save_jobs(jobs: List[Job]) -> int:
    """
    Saves a list of Job objects to the database.
    Skips duplicates silently using ON CONFLICT DO NOTHING.
    Returns the count of newly inserted jobs.
    """
    if not jobs:
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    new_count = 0

    for job in jobs:
        try:
            cursor.execute("""
                INSERT INTO jobs (title, company, location, salary, job_url, source)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_url) DO NOTHING
            """,
            (job.title, job.company, job.location, job.salary, job.job_url, job.source)
            )

            if cursor.rowcount == 1:
                new_count += 1

        except Exception as e:
            logger.error(f"Failed to save job '{job.title}': {e}")

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Saved {new_count} new jobs to vault.")
    return new_count

def fetch_recent_jobs(limit: int = 10) -> List[dict]:
    """
    Retrieves the most recently scraped jobs.
    Returns a list of dicts — easy to format for Telegram messages.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, company, location, salary, job_url
        FROM jobs
        ORDER BY scraped_at DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    jobs = []
    for row in rows:
        jobs.append({
            "title": row[0],
            "company": row[1],
            "location": row[2],
            "salary": row[3],
            "job_url": row[4]
        })
    return jobs
