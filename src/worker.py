from scraper import RedditScraper
import time
from logger import logging


class Worker:

    def __init__(self, scrape_interval=1800):
        self.is_scraping = False
        self.scrape_interval = scrape_interval
        self.reddit_scraper = RedditScraper("kopyamakarna", limit=50)
        self.database = self.reddit_scraper.database

    def start(self):
        self.is_scraping = True
        logging.info("[Worker] Starting worker")
        while self.is_scraping:
            work_start_time = time.time()
            try:
                self.reddit_scraper.scrape()
                self.database.update_tables()
            except Exception as e:
                logging.exception(f"[Worker] Exception while scraping : {e}")
                pass
            logging.info(f"[Worker] Work done in {'{0:.3f}'.format(time.time()-work_start_time)}s")
            time.sleep(self.scrape_interval)

    def stop(self):
        self.is_scraping = False
        logging.info("[Worker] Stopping scrape work")


if __name__ == "__main__":
    # scrape every 20 minutes
    worker = Worker(scrape_interval=1200)
    worker.start()
