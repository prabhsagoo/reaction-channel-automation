from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Dict, List
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class YouTubeUploader:
    """Upload videos to YouTube"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        try:
            creds = None
            
            # Load existing token if available
            token_file = Path("token.json")
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save token for future use
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
            
            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("Successfully authenticated with YouTube API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def upload_video(self, video_file: str, metadata: Dict, 
                    thumbnail_file: Optional[str] = None,
                    privacy_status: str = "private") -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            video_file: Path to video file
            metadata: Dict with title, description, hashtags
            thumbnail_file: Optional thumbnail image path
            privacy_status: Video privacy (private, unlisted, public)
        
        Returns:
            Video ID if successful, None otherwise
        """
        try:
            logger.info(f"Uploading video: {video_file}")
            
            # Prepare request body
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Untitled'),
                    'description': metadata.get('description', ''),
                    'tags': metadata.get('hashtags', []),
                    'categoryId': metadata.get('category_id', '22'),  # People & Blogs
                    'defaultLanguage': metadata.get('language', 'pa'),
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'madeForKids': False,
                },
                'recordingDetails': {
                    'recordingDate': metadata.get('recording_date'),
                } if metadata.get('recording_date') else {}
            }
            
            # Remove empty recordingDetails
            if not body['recordingDetails']:
                del body['recordingDetails']
            
            # Upload video
            request = self.service.videos().insert(
                part='snippet,status',
                body=body,
                media_body=video_file,
                notifySubscribers=False,
                onUploadProgress=self._on_upload_progress
            )
            
            response = request.execute()
            video_id = response.get('id')
            
            logger.info(f"Video uploaded successfully. ID: {video_id}")
            
            # Upload thumbnail if provided
            if thumbnail_file:
                self.upload_thumbnail(video_id, thumbnail_file)
            
            return video_id
            
        except HttpError as e:
            logger.error(f"HTTP error during upload: {e}")
            return None
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return None
    
    def upload_thumbnail(self, video_id: str, thumbnail_file: str) -> bool:
        """Upload custom thumbnail"""
        try:
            request = self.service.thumbnails().set(
                videoId=video_id,
                media_body=thumbnail_file
            )
            request.execute()
            logger.info(f"Thumbnail uploaded for video {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error uploading thumbnail: {str(e)}")
            return False
    
    def batch_upload(self, videos: List[Dict]) -> Dict:
        """
        Upload multiple videos
        
        Args:
            videos: List of dicts with 'file', 'metadata', 'thumbnail' keys
        
        Returns:
            Dict with upload results
        """
        results = {
            "total": len(videos),
            "successful": 0,
            "failed": 0,
            "videos": []
        }
        
        for i, video in enumerate(videos, 1):
            logger.info(f"Uploading video {i}/{len(videos)}")
            
            video_id = self.upload_video(
                video['file'],
                video['metadata'],
                video.get('thumbnail'),
                video.get('privacy_status', 'private')
            )
            
            if video_id:
                results["successful"] += 1
                results["videos"].append({
                    "file": video['file'],
                    "video_id": video_id,
                    "status": "success"
                })
            else:
                results["failed"] += 1
                results["videos"].append({
                    "file": video['file'],
                    "status": "failed"
                })
        
        return results
    
    @staticmethod
    def _on_upload_progress(status):
        """Progress callback for upload"""
        if status.progress() < 1:
            percent = int(status.progress() * 100)
            logger.info(f"Upload progress: {percent}%")
        else:
            logger.info("Upload completed")