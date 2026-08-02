import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_KEY = os.getenv("ADMIN_KEY")
BASE_URL = os.getenv("BASE_URL")


class Settings:
    card_canvas_size = (900, 600)
    card_qr_size = (400, 400)
    card_qr_offset_y = 50
    qr_box_size = 10


settings = Settings()
