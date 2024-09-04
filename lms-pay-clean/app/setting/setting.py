import logging
import dotenv
import os
from uvicorn.config import LOGGING_CONFIG

class Setting():
    def __init__(self):
        dotenv.load_dotenv()
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.RMQ_URL = os.getenv('RMQ_URL')
        self.mail = {
            "username": os.getenv('MAIL_USERNAME'),
            "password": os.getenv('MAIL_PASSWORD'),
            "from": os.getenv('MAIL_FROM'),
            "server": os.getenv('MAIL_SERVER'),
            "from_name": os.getenv('MAIL_FROM_NAME')
        }
        self.secret = {
            "token_expire": int(os.getenv('TOKEN_EXPIRE')),
            "refresh_token_expire": int(os.getenv('REFRESH_TOKEN_EXPIRE')),
            "secret_key": os.getenv('SECRET_KEY'),
            "algorithm": os.getenv('ALGORITHM'),
            "hash": os.getenv('HASH').split(","),
        }
        self.admin = {
            "username": os.getenv('SUPERADMIN_USERNAME'),
            "password": os.getenv('SUPERADMIN_PASSWORD'),
            "email": os.getenv('SUPERADMIN_EMAIL'),
        }

    def get_db_url(self):
        return self.DATABASE_URL
    
    def get_secret(self):
        return self.secret

settings = Setting()

logger = logging.getLogger("uvicorn")
# formatter = logging.Formatter(LOGGING_CONFIG["formatters"]["default"]["fmt"])
# logger.setLevel(logging.INFO)
# handler = logging.StreamHandler()
# handler.setLevel(logging.INFO)
# handler.setFormatter(formatter)
# logger.addHandler(handler)
