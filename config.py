# config.py
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Default key for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')  
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads/')  # Default upload folder
    PARENT_FOLDER_ID = os.getenv('PARENT_FOLDER_ID')
    CSRF_ENABLED = True
