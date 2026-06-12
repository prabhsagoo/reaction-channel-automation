import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database management for videos, uploads, and analytics"""
    
    def __init__(self, db_path: str = "videos.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Videos table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    channel TEXT,
                    duration INTEGER,
                    file_path TEXT,
                    thumbnail_url TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Uploads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER,
                    youtube_video_id TEXT UNIQUE,
                    punjabi_title TEXT,
                    punjabi_description TEXT,
                    hashtags TEXT,
                    privacy_status TEXT,
                    upload_status TEXT,
                    uploaded_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos(id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youtube_video_id TEXT,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    subscribers_gained INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0.0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (youtube_video_id) REFERENCES uploads(youtube_video_id)
                )
            ''')
            
            # Content pipeline table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER,
                    stage TEXT,
                    notes TEXT,
                    scheduled_upload TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            return False
    
    def add_video(self, source_url: str, title: str, description: str, 
                 channel: str, duration: int, file_path: str) -> Optional[int]:
        """Add video to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO videos (source_url, title, description, channel, duration, file_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (source_url, title, description, channel, duration, file_path, "downloaded"))
            
            conn.commit()
            video_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Video added to database with ID: {video_id}")
            return video_id
        except Exception as e:
            logger.error(f"Error adding video: {str(e)}")
            return None
    
    def add_upload(self, video_id: int, youtube_video_id: str, punjabi_title: str,
                  punjabi_description: str, hashtags: List[str]) -> Optional[int]:
        """Record uploaded video"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO uploads (video_id, youtube_video_id, punjabi_title, punjabi_description, hashtags, upload_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (video_id, youtube_video_id, punjabi_title, punjabi_description, ','.join(hashtags), "uploaded"))
            
            conn.commit()
            upload_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Upload recorded with ID: {upload_id}")
            return upload_id
        except Exception as e:
            logger.error(f"Error recording upload: {str(e)}")
            return None
    
    def get_videos(self, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get videos from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute('SELECT * FROM videos WHERE status = ? ORDER BY created_at DESC LIMIT ?',
                             (status, limit))
            else:
                cursor.execute('SELECT * FROM videos ORDER BY created_at DESC LIMIT ?', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching videos: {str(e)}")
            return []
    
    def get_analytics(self, youtube_video_id: str) -> Optional[Dict]:
        """Get analytics for a video"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM analytics WHERE youtube_video_id = ?', (youtube_video_id,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching analytics: {str(e)}")
            return None
    
    def update_pipeline_status(self, video_id: int, stage: str, notes: str = "") -> bool:
        """Update video pipeline status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO pipeline (video_id, stage, notes)
                VALUES (?, ?, ?)
            ''', (video_id, stage, notes))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Pipeline updated for video {video_id}: {stage}")
            return True
        except Exception as e:
            logger.error(f"Error updating pipeline: {str(e)}")
            return False