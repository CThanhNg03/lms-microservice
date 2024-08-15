import os
import dotenv


class Setting:
    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.RMQ_URL = os.getenv('RMQ_URL')

env = Setting()
        