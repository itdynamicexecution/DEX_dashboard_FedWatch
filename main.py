import time
import os
import logging
from dotenv import load_dotenv
from cme_scraper import run_scraper_job, send_telegram_log

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", "10"))

def main():
    logging.info("🚀 Starting DEX Dashboard FedWatch Autonomous Daemon...")
    send_telegram_log("🟢 <b>DEX FedWatch Daemon Started</b>\nVPS: <code>dashboard-VVIP-Fed (174.138.25.163)</code>\nStatus: Running 24/7 autonomous scraper.")

    while True:
        try:
            logging.info("Executing periodic FedWatch sync job...")
            run_scraper_job()
        except Exception as e:
            logging.error(f"Error in main runner loop: {e}")
            send_telegram_log(f"⚠️ <b>FedWatch Daemon Error</b>: {e}")

        logging.info(f"Sleeping for {INTERVAL_MINUTES} minutes...")
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
