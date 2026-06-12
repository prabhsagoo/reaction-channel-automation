import subprocess
import json
from pathlib import Path
from typing import Optional, Dict
import logging

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
            ydl_opts = {
                'format': self._get_format_string(quality),
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'extract_audio': quality == "audio",
                'audio_format': 'mp3' if quality == "audio" else None,
            }
            
            # Run yt-dlp
            cmd = ['yt-dlp', youtube_url]
            for key, value in ydl_opts.items():
                if value is True:
                    cmd.append(f'--{key.replace("_", "-")}')
                elif value and value is not False and value != "False":
                    cmd.extend([f'--{key.replace("_", "-")}', str(value)])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded video")
                return {
                    "status": "success",
                    "url": youtube_url,
                    "output_dir": str(self.output_dir),
                    "quality": quality
                }
            else:
                logger.error(f"Download failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return None
    
    @staticmethod
    def _get_format_string(quality: str) -> str:
        """Get yt-dlp format string based on quality"""
        formats = {
            "best": "bestvideo+bestaudio/best",
            "720p": "best[height<=720]",
            "480p": "best[height<=480]",
            "360p": "best[height<=360]",
            "audio": "bestaudio/best"
        }
        return formats.get(quality, "best")
    
    def extract_metadata(self, youtube_url: str) -> Optional[Dict]:
        """Extract video metadata without downloading"""
        try:
            logger.info(f"Extracting metadata from {youtube_url}")
            
            cmd = ['yt-dlp', '--dump-json', '--no-warnings', youtube_url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                return {
                    "title": metadata.get("title"),
                    "duration": metadata.get("duration"),
                    "description": metadata.get("description"),
                    "channel": metadata.get("uploader"),
                    "upload_date": metadata.get("upload_date"),
                    "view_count": metadata.get("view_count"),
                    "thumbnail": metadata.get("thumbnail"),
                }
            return None
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return None