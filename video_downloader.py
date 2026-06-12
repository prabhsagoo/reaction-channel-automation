import yt_dlp
from pathlib import Path
from typing import Optional, Dict
import logging
import json

logger = logging.getLogger(__name__)

class VideoDownloader:
    """Download videos from YouTube using yt-dlp"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_video(self, youtube_url: str, quality: str = "best") -> Optional[Dict]:
        """
        Download video from YouTube
        
        Args:
            youtube_url: YouTube video URL
            quality: Video quality (best, 720p, 480p, 360p, audio)
        
        Returns:
            Dict with video info or None if failed
        """
        try:
            logger.info(f"Downloading video from {youtube_url}")
            
            # yt-dlp options
            format_string = self._get_format_string(quality)
            
            ydl_opts = {
                'format': format_string,
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
            }
            
            # Add audio extraction for audio quality
            if quality == "audio":
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'format': 'bestaudio/best',
                })
            
            # Download using yt-dlp library
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                
            logger.info(f"Successfully downloaded video: {info.get('title')}")
            return {
                "status": "success",
                "url": youtube_url,
                "title": info.get('title'),
                "output_dir": str(self.output_dir),
                "quality": quality,
                "duration": info.get('duration'),
            }
                
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return None
    
    @staticmethod
    def _get_format_string(quality: str) -> str:
        """Get yt-dlp format string based on quality"""
        formats = {
            "best": "bestvideo+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "480p": "bestvideo[height<=480]+bestaudio/best",
            "360p": "bestvideo[height<=360]+bestaudio/best",
            "audio": "bestaudio/best"
        }
        return formats.get(quality, "best")
    
    def extract_metadata(self, youtube_url: str) -> Optional[Dict]:
        """Extract video metadata without downloading"""
        try:
            logger.info(f"Extracting metadata from {youtube_url}")
            
            ydl_opts = {
                'quiet': False,
                'no_warnings': False,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                metadata = ydl.extract_info(youtube_url, download=False)
            
            return {
                "title": metadata.get("title"),
                "duration": metadata.get("duration"),
                "description": metadata.get("description"),
                "channel": metadata.get("uploader"),
                "upload_date": metadata.get("upload_date"),
                "view_count": metadata.get("view_count"),
                "thumbnail": metadata.get("thumbnail"),
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return None
