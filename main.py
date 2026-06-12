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
    
    # This would query analytics from YouTube API
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