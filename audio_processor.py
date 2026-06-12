import subprocess
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Extract and process audio from videos"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_audio(self, video_file: Path, format: str = "mp3") -> Optional[Path]:
        """
        Extract audio from video file
        
        Args:
            video_file: Path to video file
            format: Audio format (mp3, wav, aac)
        
        Returns:
            Path to extracted audio file or None if failed
        """
        try:
            if not video_file.exists():
                logger.error(f"Video file not found: {video_file}")
                return None
            
            output_file = self.output_dir / f"{video_file.stem}.{format}"
            
            logger.info(f"Extracting audio from {video_file}")
            
            # FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', str(video_file),
                '-q:a', '0',
                '-map', 'a',
                str(output_file),
                '-y'  # Overwrite output file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_file.exists():
                logger.info(f"Audio extracted to {output_file}")
                return output_file
            else:
                logger.error(f"Audio extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return None
    
    def get_duration(self, video_file: Path) -> Optional[float]:
        """Get video duration in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1',
                str(video_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            return None
        except Exception as e:
            logger.error(f"Error getting duration: {str(e)}")
            return None
    
    def convert_audio_format(self, audio_file: Path, output_format: str = "wav") -> Optional[Path]:
        """Convert audio to different format"""
        try:
            output_file = self.output_dir / f"{audio_file.stem}.{output_format}"
            
            cmd = [
                'ffmpeg',
                '-i', str(audio_file),
                str(output_file),
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Audio converted to {output_format}")
                return output_file
            return None
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}")
            return None