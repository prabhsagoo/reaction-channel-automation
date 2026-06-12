#!/usr/bin/env python3
"""
YouTube upload functionality with proper error handling
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from typing import Optional, Dict, List
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class YouTubeUploader:
    """Upload videos to YouTube with proper OAuth2 authentication"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API using OAuth2"""
        try:
            creds = None
            token_file = Path("token.json")
            
            # Load existing token
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
                logger.info("Loaded existing token")
            
            # If no valid credentials, refresh or get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing token...")
                    creds.refresh(Request())
                else:
                    logger.info("Getting new credentials...")
                    if not Path(self.credentials_file).exists():
                        logger.error(f"credentials.json not found. Please download it from Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save token
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
                logger.info("Token saved")
            
            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("✅ Successfully authenticated with YouTube API")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            return False
    
    def upload_video(self, video_file: str, metadata: Dict, 
                    privacy_status: str = "private") -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            video_file: Path to video file
            metadata: Dict with title, description, hashtags, language
            privacy_status: private, unlisted, or public
        
        Returns:
            Video ID if successful, None otherwise
        """
        try:
            if not self.service:
                logger.error("Not authenticated with YouTube API")
                return None
            
            video_path = Path(video_file)
            if not video_path.exists():
                logger.error(f"Video file not found: {video_file}")
                return None
            
            logger.info(f"📤 Uploading: {video_path.name}")
            
            # Prepare request body
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Untitled')[:100],
                    'description': metadata.get('description', '')[:5000],
                    'tags': metadata.get('hashtags', [])[:500],
                    'categoryId': metadata.get('category_id', '22'),  # People & Blogs
                    'defaultLanguage': metadata.get('language', 'pa'),
                    'defaultAudioLanguage': 'pa',
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False,
                }
            }
            
            # Upload with resumable media
            media = MediaFileUpload(
                video_file,
                chunksize=1024*1024,  # 1MB chunks
                resumable=True
            )
            
            request = self.service.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media,
                notifySubscribers=False,
            )
            
            # Execute with progress tracking
            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        percent = int(status.progress() * 100)
                        logger.info(f"⬆️  Upload progress: {percent}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        logger.warning(f"Retrying due to server error: {e.resp.status}")
                        time.sleep(5)
                        continue
                    else:
                        raise
            
            video_id = response['id']
            logger.info(f"✅ Video uploaded successfully!")
            logger.info(f"🎬 Video ID: {video_id}")
            logger.info(f"📺 Watch: https://www.youtube.com/watch?v={video_id}")
            
            return video_id
            
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Upload error: {str(e)}")
            return None
    
    def batch_upload(self, videos: List[Dict]) -> Dict:
        """
        Upload multiple videos
        
        Args:
            videos: List of dicts with 'file' and 'metadata' keys
        
        Returns:
            Results dictionary
        """
        results = {
            "total": len(videos),
            "successful": 0,
            "failed": 0,
            "videos": []
        }
        
        for i, video in enumerate(videos, 1):
            logger.info(f"\n📹 Uploading video {i}/{len(videos)}")
            
            video_id = self.upload_video(
                video['file'],
                video['metadata'],
                video.get('privacy_status', 'private')
            )
            
            if video_id:
                results["successful"] += 1
                results["videos"].append({
                    "file": video['file'],
                    "video_id": video_id,
                    "status": "success",
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
            else:
                results["failed"] += 1
                results["videos"].append({
                    "file": video['file'],
                    "status": "failed"
                })
        
        logger.info(f"\n📊 Batch upload complete: {results['successful']}/{results['total']} successful")
        return results
    
    def get_channel_info(self) -> Optional[Dict]:
        """Get authenticated user's channel info"""
        try:
            request = self.service.channels().list(
                part='snippet,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'title': channel['snippet']['title'],
                    'subscribers': channel['statistics'].get('subscriberCount', 'private'),
                    'views': channel['statistics'].get('viewCount', 0),
                    'videos': channel['statistics'].get('videoCount', 0),
                    'thumbnail': channel['snippet']['thumbnails']['default']['url'],
                }
            return None
        except Exception as e:
            logger.error(f"Error getting channel info: {str(e)}")
            return None
