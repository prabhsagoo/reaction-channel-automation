#!/usr/bin/env python3
"""
Simple web dashboard for analytics and management
Run: python dashboard.py
Then visit: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
from database import Database
from pathlib import Path
import json
import logging

app = Flask(__name__)
db = Database()
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        videos = db.get_videos(limit=1000)
        
        stats = {
            'total_videos': len(videos),
            'downloaded': len([v for v in videos if v['status'] == 'downloaded']),
            'uploaded': len([v for v in videos if v['status'] == 'uploaded']),
            'total_duration': sum([v.get('duration', 0) or 0 for v in videos]),
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos')
def get_videos():
    """Get videos list"""
    try:
        status = request.args.get('status')
        videos = db.get_videos(status=status, limit=100)
        
        # Format for display
        formatted = []
        for v in videos:
            formatted.append({
                'id': v['id'],
                'title': v['title'],
                'channel': v['channel'],
                'duration': v['duration'],
                'status': v['status'],
                'created_at': v['created_at'],
                'file_path': v['file_path'],
            })
        
        return jsonify(formatted)
    except Exception as e:
        logger.error(f"Error getting videos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/uploads')
def get_uploads():
    """Get uploads"""
    try:
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, a.views, a.revenue 
            FROM uploads u 
            LEFT JOIN analytics a ON u.youtube_video_id = a.youtube_video_id
            ORDER BY u.uploaded_at DESC 
            LIMIT 50
        ''')
        
        uploads = []
        for row in cursor.fetchall():
            uploads.append({
                'id': row['id'],
                'punjabi_title': row['punjabi_title'],
                'youtube_video_id': row['youtube_video_id'],
                'upload_status': row['upload_status'],
                'views': row['views'] or 0,
                'revenue': row['revenue'] or 0.0,
                'uploaded_at': row['uploaded_at'],
            })
        
        conn.close()
        return jsonify(uploads)
    except Exception as e:
        logger.error(f"Error getting uploads: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/revenue')
def get_revenue():
    """Get revenue statistics"""
    try:
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(revenue) as total_revenue, SUM(views) as total_views FROM analytics')
        result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'total_revenue': result[0] or 0.0,
            'total_views': result[1] or 0,
            'avg_cpm': round((result[0] or 0) / max(1, (result[1] or 1)) * 1000, 2)
        })
    except Exception as e:
        logger.error(f"Error getting revenue: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline/<int:video_id>', methods=['POST'])
def update_pipeline(video_id):
    """Update video pipeline status"""
    try:
        data = request.json
        db.update_pipeline_status(video_id, data['stage'], data.get('notes', ''))
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating pipeline: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting dashboard at http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, port=5000)
