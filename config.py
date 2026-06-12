import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for the toolkit"""
    
    # YouTube API
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./videos.db")
    
    # Video Processing
    VIDEO_DOWNLOAD_DIR = Path(os.getenv("VIDEO_DOWNLOAD_DIR", "./videos"))
    AUDIO_EXTRACT_DIR = Path(os.getenv("AUDIO_EXTRACT_DIR", "./audio"))
    
    # Metadata
    DEFAULT_LANGUAGE = "pa"  # Punjabi
    DEFAULT_CATEGORY = "22"  # People & Blogs
    
    # Upload Settings
    MAX_RETRIES = 3
    BATCH_SIZE = 10
    
    def __init__(self):
        # Create directories if they don't exist
        self.VIDEO_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.AUDIO_EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not os.getenv("YOUTUBE_API_KEY"):
            raise ValueError("YOUTUBE_API_KEY not set in .env file")
        return True