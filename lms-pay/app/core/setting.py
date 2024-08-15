import dotenv
import os

class Setting():
    def __init__(self):
        dotenv.load_dotenv()
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.RMQ_URL = os.getenv('RMQ_URL')

env = Setting()
