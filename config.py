# config.py
import os
import configparser
import logging
from dotenv import load_dotenv

# --- CONSTANTS ---
BASE_URL = "https://fines.police.gov.rw/"
CHECK_FINES_URL = "https://fines.police.gov.rw/checkFines"
CONFIG_FILE = 'config.ini'
ENV_FILE = '.env'

def load_configuration():
    """Loads and validates configuration from files."""
    try:
        load_dotenv(dotenv_path=ENV_FILE)
        parser = configparser.ConfigParser()
        if not parser.read(CONFIG_FILE):
            raise FileNotFoundError(f"{CONFIG_FILE} not found.")

        # Load and return a dictionary of settings
        settings = {
            'plate_number': parser['VEHICLE']['PLATE_NUMBER'],
            'tin_number': parser['VEHICLE']['TIN_NUMBER'],
            'smtp_server': parser['EMAIL']['SMTP_SERVER'],
            'smtp_port': int(parser['EMAIL']['SMTP_PORT']),
            'sender_email': parser['EMAIL']['SENDER_EMAIL'],
            'receiver_email': parser['EMAIL']['RECEIVER_EMAIL'],
            'email_password': os.getenv('EMAIL_PASSWORD')
        }

        if not all(settings.values()):
            raise ValueError("One or more configuration values are missing in config.ini or .env file.")
        
        logging.info("Configuration loaded successfully.")
        return settings

    except (FileNotFoundError, KeyError, ValueError) as e:
        logging.critical(f"Configuration Error: {e}")
        logging.critical("Please ensure config.ini and .env files are correctly set up. Exiting.")
        exit(1)

# Load settings once when the module is imported
settings = load_configuration()