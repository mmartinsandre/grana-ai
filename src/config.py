import os
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env file

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DATA_FILE = os.getenv('DATA_FILE', 'user_data.json')

    def __init__(self):
        if not self.TELEGRAM_TOKEN:
            raise ValueError("No TELEGRAM_TOKEN set for application")
