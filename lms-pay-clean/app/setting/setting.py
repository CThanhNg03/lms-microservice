import logging
import dotenv
import os

class Setting():
    def __init__(self):
        dotenv.load_dotenv()
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.RMQ_URL = os.getenv('RMQ_URL')

    def get_db_url(self):
        return self.DATABASE_URL

settings = Setting()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
