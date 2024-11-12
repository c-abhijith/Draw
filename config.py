# config.py
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Default key for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')  # Default to SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads/')  # Default upload folder
    DROPBOX_ACCESS_TOKEN = 'sl.CAmw5H_IxehupCFLuw17wBin5keORpBtHvQUAxjX-FvURu9x6Wiyiw-3UsIcq9ILfv6k-os8PMP9rGELnIf6wxE71MD17zqbXp3G77WRe_75Vkp0eGHyTHTYRJVb2EGsMsCYy3CxtH1MV2WaY8v-T7s'
