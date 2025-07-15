# scraper.py
import requests
import logging
from bs4 import BeautifulSoup
from config import BASE_URL, CHECK_FINES_URL

class Scraper:
    def __init__(self, plate_number, tin_number):
        self.plate_number = plate_number
        self.tin_number = tin_number
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_fines(self):
        """
        Scrapes the website to check for fines.
        Returns a tuple: (total_fine_amount, fines_table_html) or (0, None) if no fines.
        """
        logging.info(f"Starting check for Plate: {self.plate_number}")
        try:
            token = self._get_security_token()
            
            payload = {'_token': token, 'plate': self.plate_number, 'tin': self.tin_number}
            logging.info("Submitting form to check for fines...")
            response = self.session.post(CHECK_FINES_URL, data=payload, headers={'Referer': BASE_URL})
            response.raise_for_status()

            return self._parse_result(response.text)

        except requests.exceptions.RequestException as e:
            logging.error(f"A network error occurred: {e}")
        except (AttributeError, TypeError, KeyError, ValueError) as e:
            logging.error(f"Could not parse the webpage. The website structure may have changed. Details: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred during scraping: {e}")
        
        return 0, None # Return a default value on failure

    def _get_security_token(self):
        """Fetches the CSRF token from the main page."""
        logging.info("Fetching security token from main page...")
        response = self.session.get(BASE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': '_token'})
        if not token:
            raise ValueError("Security token (_token) not found on the page.")
        logging.info("Security token found.")
        return token['value']

    def _parse_result(self, html_content):
        """Parses the HTML of the result page to find fine details."""
        soup = BeautifulSoup(html_content, 'html.parser')
        total_row = soup.find('tr', class_='fw-bold')
        if not total_row:
            raise ValueError("Could not find the total row in the results page.")

        total_amount_cell = total_row.find_all('td')[-1]
        total_amount_text = total_amount_cell.text.strip()
        
        total_fine = int(''.join(filter(str.isdigit, total_amount_text)))
        fines_table_html = str(soup.find('div', class_='table-responsive'))
        
        return total_fine, fines_table_html