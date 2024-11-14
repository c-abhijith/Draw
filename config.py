# config.py
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Default key for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cloudinary configuration - use explicit values for testing
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

    print(f"Cloud Name: {CLOUDINARY_CLOUD_NAME}")  # Debug print
    print(f"API Key: {CLOUDINARY_API_KEY}")  # Debug print
    print(f"API Secret: {'*' * len(CLOUDINARY_API_SECRET) if CLOUDINARY_API_SECRET else 'None'}")  # Debug print

    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        raise ValueError("Missing Cloudinary configuration. Please check your environment variables.")
