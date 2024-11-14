# config.py
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Default key for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')  
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads/')  # Default upload folder
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    UPLOAD_FOLDER = "static/uploads"
