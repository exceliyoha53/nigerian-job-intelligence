from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import logging
from models.job import Job
from typing import List

logger = logging.getLogger(__name__)


def scrape_jobberman(max_pages: int = 3) -> List[Job]:
    all_jobs: List[Job] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"https://www.jobberman.com/jobs?page={page_num}"
            logger.info(f"Scraping page {page_num}: {url}")
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_selector('[data-cy="listing-cards-components"]', timeout=15000)
            except PlaywrightTimeout:
                logger.warning(f"Page {page_num} timed out. Skipping.")

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            job_cards = soup.find_all("div", attrs={"data-cy": "listing-cards-components"})
            logger.info(f"Found {len(job_cards)} job cards on page {page_num}")

            if not job_cards:
                logger.info("No job cards found. Stopping pagination.")
                break
            
            for card in job_cards:
                job = _parse_card(card)
                if job:
                    all_jobs.append(job)

        browser.close()

    logger.info(f"Scrape complete. Total validated jobs: {len(all_jobs)}")
    return all_jobs


def _parse_card(card) -> Job | None:
    try:
        title_tag = card.find("a", attrs={"data-cy": "listing-title-link"})
        title = title_tag.find("p").get_text(strip=True) if title_tag else None

        job_url = title_tag["href"] if title_tag and title_tag.get("href") else None
        if not job_url:
            return None

        company_tag = card.find("p", class_="text-sm text-blue-700 text-loading-animate inline-block mt-3")
        company = company_tag.get_text(strip=True) if company_tag else "Unknown"

        tag_spans = card.find_all("span", class_="mb-3 px-3 py-1 rounded bg-brand-secondary-100 mr-2 text-loading-hide text-gray-700")

        location = tag_spans[0].get_text(strip=True) if len(tag_spans) > 0 else "Nigeria"
        job_type = tag_spans[1].get_text(strip=True) if len(tag_spans) > 1 else None

        if len(tag_spans) > 2:
            salary = " ".join(tag_spans[2].get_text(strip=True).split())
        else:
            salary = None

        job = Job(
            title=title or "",
            company=company,
            location=location,
            salary=salary,
            job_url=job_url,
            source="jobberman"
        )
        return job

    except Exception as e:
        logger.warning(f"Failed to parse card: {e}")
        return None