# main.py
import schedule
import time
import logging
import argparse

from config import settings
from scraper import Scraper
from notifier import Notifier

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_check(scraper, notifier):
    """The main workflow: scrape for fines and notify if any are found."""
    total_fine, fines_table_html = scraper.get_fines()

    if total_fine and total_fine > 0:
        logging.warning(f"!!! FINE FOUND !!! Total Amount: {total_fine} FRW")
        notifier.send_notification(
            plate_number=scraper.plate_number,
            tin_number=scraper.tin_number,
            fine_amount=total_fine,
            fine_details_html=fines_table_html
        )
    elif total_fine is not None:
        logging.info("Success: No fines found.")
    else:
        logging.error("Check failed. See previous logs for details.")

def test_email_sending(notifier, plate_number, tin_number):
    """Sends a sample email notification for testing purposes."""
    logging.info("--- Running Email Sending Test ---")
    dummy_fine_amount = 25000
    dummy_fine_details_html = """
    <div class="table-responsive">
        <table style="width: 100%; border-collapse: collapse;">
            <thead><tr><th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">Ticket number</th><th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">Offense</th><th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">Amount</th></tr></thead>
            <tbody><tr><td style="border: 1px solid #ddd; padding: 8px;">T0123456789</td><td style="border: 1px solid #ddd; padding: 8px;">Exceeding speed limit</td><td style="border: 1px solid #ddd; padding: 8px;">25000 FRW</td></tr>
            <tr><td colspan="2" style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Total</td><td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">25000 FRW</td></tr></tbody>
        </table>
    </div>
    """
    notifier.send_notification(plate_number, tin_number, dummy_fine_amount, dummy_fine_details_html)
    logging.info("--- Email Test Complete ---")


def main():
    """Main function to parse command-line arguments and run the checker."""
    parser = argparse.ArgumentParser(description="Automated RNP Traffic Fine Checker.")
    parser.add_argument(
        '--run-once', action='store_true', help="Run the fine check a single time and exit."
    )
    parser.add_argument(
        '--test-email', action='store_true', help="Send a test email to the configured receiver and exit."
    )
    args = parser.parse_args()

    # --- Initialize Components ---
    logging.info("Initializing application components...")
    scraper = Scraper(
        plate_number=settings['plate_number'], 
        tin_number=settings['tin_number']
    )
    notifier = Notifier(
        smtp_server=settings['smtp_server'],
        smtp_port=settings['smtp_port'],
        sender_email=settings['sender_email'],
        email_password=settings['email_password'],
        receiver_email=settings['receiver_email']
    )
    
    # --- Execute based on arguments ---
    if args.test_email:
        test_email_sending(notifier, settings['plate_number'], settings['tin_number'])
    elif args.run_once:
        run_check(scraper, notifier)
    else:
        # Default behavior: run the scheduler
        logging.info("Performing initial check on startup...")
        run_check(scraper, notifier)
        
        schedule.every().day.at("09:00").do(run_check, scraper=scraper, notifier=notifier)
        
        logging.info("Scheduler started. Will check for fines every day at 09:00.")
        logging.info("The script will now run in the background. Press Ctrl+C to exit.")

        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()