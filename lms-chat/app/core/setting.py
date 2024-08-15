import os
import dotenv

class Settings:
    def __init__(self):
        dotenv.load_dotenv()
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.DEBUG = os.getenv("DEBUG")
        self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")
        self.CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS").split(",")
        self.CORS_ALLOWED_METHODS = os.getenv("CORS_ALLOWED_METHODS").split(",")
        self.CORS_ALLOWED_HEADERS = os.getenv("CORS_ALLOWED_HEADERS").split(",")
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.RABBITMQ_URL = os.getenv("RMQ_URL")

env = Settings()