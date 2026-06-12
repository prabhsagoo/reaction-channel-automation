#!/usr/bin/env python3
"""
Main CLI tool for Punjabi Reaction Channel Automation
"""

import click
import logging
from pathlib import Path
from config import Config
from video_downloader import VideoDownloader
from audio_processor import AudioProcessor
from metadata_generator import PunjabiMetadataGenerator
from youtube_uploader import YouTubeUploader
from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
config = Config()
db = Database()
downloader = VideoDownloader(config.VIDEO_DOWNLOAD_DIR)
audio_processor = AudioProcessor(config.AUDIO_EXTRACT_DIR)
metadata_gen = PunjabiMetadataGenerator()
uploader = YouTubeUploader()

@click.group()
def cli():
    """Punjabi Reaction Channel Automation Toolkit"""
    pass

@cli.command()
@click.option('--url', prompt='YouTube URL', help='YouTube video URL to download')
@click.option('--quality', default='best', help='Video quality (best, 720p, 480p, 360p)')
def download(url, quality):
    """Download video from YouTube"""
    click.echo(f"🎬 Downloading video from {url}")
    
    # Download video
    result = downloader.download_video(url, quality)
    if result:
        click.echo("✅ Video downloaded successfully")
        
        # Extract metadata
        metadata = downloader.extract_metadata(url)
        if metadata:
            click.echo(f"📝 Video: {metadata['title']}")
            click.echo(f"👤 Channel: {metadata['channel']}")
            click.echo(f"⏱️  Duration: {metadata['duration']}s")
            
            # Add to database
            file_path = config.VIDEO_DOWNLOAD_DIR / f"{metadata['title']}.webm"
            db.add_video(url, metadata['title'], metadata['description'] or '', 
                        metadata['channel'], metadata['duration'] or 0, str(file_path))
    else:
        click.echo("❌ Failed to download video")

@cli.command()
@click.option('--url', prompt='YouTube URL', help='YouTube video URL')
@click.option('--title', prompt='Content title', help='Video title')
@click.option('--channel', prompt='Channel name', help='Original channel name')
@click.option('--type', default='reaction', help='Content type')
def generate_metadata(url, title, channel, type):
    """Generate Punjabi metadata"""
    click.echo("📝 Generating Punjabi metadata...")
    
    # Extract metadata from YouTube
    original_metadata = downloader.extract_metadata(url)
    if not original_metadata:
        click.echo("❌ Could not extract metadata from video")
        return
    
    # Generate Punjabi metadata
    metadata = metadata_gen.generate_metadata(
        title,
        original_metadata.get('description', ''),
        channel,
        type
    )
    
    click.echo(f"\n✅ Punjabi Title: {metadata['title']}")
    click.echo(f"\n📄 Description:\n{metadata['description']}")
    click.echo(f"\n🏷️  Hashtags: {' '.join(metadata['hashtags'])}")

@cli.command()
@click.option('--video-file', prompt='Video file path', help='Path to video file')
@click.option('--format', default='mp3', help='Audio format (mp3, wav, aac)')
def extract_audio(video_file, format):
    """Extract audio from video"""
    click.echo(f"🔊 Extracting audio from {video_file}")
    
    audio_file = audio_processor.extract_audio(Path(video_file), format)
    if audio_file:
        click.echo(f"✅ Audio extracted to {audio_file}")
    else:
        click.echo("❌ Failed to extract audio")

@cli.command()
@click.option('--file', prompt='Video file', help='Path to video file to upload')
@click.option('--title', prompt='Video title', help='Title in Punjabi')
@click.option('--description', prompt='Description', help='Video description')
@click.option('--tags', default='ਪੰਜਾਬੀ,ਯੂਟਿਊਬ,ਵਾਇਰਲ', help='Comma-separated tags')
@click.option('--privacy', default='private', help='private, unlisted, or public')
def upload(file, title, description, tags, privacy):
    """Upload video to YouTube"""
    click.echo(f"📤 Uploading video: {file}")
    
    metadata = {
        'title': title,
        'description': description,
        'hashtags': [tag.strip() for tag in tags.split(',')],
        'language': 'pa',
        'category_id': '22',
    }
    
    video_id = uploader.upload_video(file, metadata, privacy)
    if video_id:
        click.echo(f"✅ Video uploaded successfully!")
        click.echo(f"🎬 Video ID: {video_id}")
        click.echo(f"📺 Watch: https://www.youtube.com/watch?v={video_id}")
        
        # Add to database
        db.add_upload(1, video_id, title, description, metadata['hashtags'])
    else:
        click.echo("❌ Failed to upload video")

@cli.command()
def list_videos():
    """List downloaded videos"""
    click.echo("📋 Downloaded Videos:")
    
    videos = db.get_videos(status='downloaded')
    if not videos:
        click.echo("No videos found")
        return
    
    for video in videos[:10]:
        click.echo(f"\n📹 {video['title']}")
        click.echo(f"   Channel: {video['channel']}")
        click.echo(f"   Duration: {video['duration']}s")
        click.echo(f"   File: {video['file_path']}")

@cli.command()
def list_uploads():
    """List uploaded videos"""
    click.echo("🎥 Uploaded Videos:")
    
    import sqlite3
    db_path = "videos.db"
    db_conn = sqlite3.connect(db_path)
    db_conn.row_factory = sqlite3.Row
    cursor = db_conn.cursor()
    
    cursor.execute('SELECT * FROM uploads ORDER BY uploaded_at DESC LIMIT 10')
    uploads = cursor.fetchall()
    db_conn.close()
    
    if not uploads:
        click.echo("No uploads found")
        return
    
    for upload in uploads:
        click.echo(f"\n📹 {upload['punjabi_title']}")
        click.echo(f"   YouTube ID: {upload['youtube_video_id']}")
        click.echo(f"   Status: {upload['upload_status']}")

@cli.command()
def channel_info():
    """Get your YouTube channel information"""
    click.echo("📺 Your Channel Information:")
    
    info = uploader.get_channel_info()
    if info:
        click.echo(f"\n✅ Channel: {info['title']}")
        click.echo(f"📊 Subscribers: {info['subscribers']}")
        click.echo(f"👁️  Total Views: {info['views']}")
        click.echo(f"🎬 Total Videos: {info['videos']}")
    else:
        click.echo("❌ Could not fetch channel information")

@cli.command()
def dashboard():
    """Start web dashboard"""
    click.echo("🚀 Starting dashboard...")
    click.echo("📺 Open: http://localhost:5000")
    
    try:
        from dashboard import app
        app.run(debug=True, port=5000)
    except ImportError:
        click.echo("❌ Flask not installed. Run: pip install flask")

@cli.command()
def setup():
    """Setup YouTube API credentials"""
    click.echo("🔧 YouTube API Setup")
    click.echo("\n1. Go to: https://console.cloud.google.com/")
    click.echo("2. Create a new project")
    click.echo("3. Enable YouTube Data API v3")
    click.echo("4. Create OAuth 2.0 credentials (Desktop app)")
    click.echo("5. Download JSON and save as 'credentials.json'")
    click.echo("\nPlace credentials.json in the current directory")

@cli.command()
def version():
    """Show version"""
    click.echo("Punjabi Reaction Channel Automation Toolkit v1.0.0")

if __name__ == '__main__':
    cli()
