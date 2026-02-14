from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app.services.screenshot import ScreenshotService
from app.models.database import Database
import os

bp = Blueprint('screenshots', __name__, url_prefix='/api/screenshots')

def get_db():
    return Database(current_app.config['DATABASE'])

def get_screenshot_service():
    return ScreenshotService(current_app.config['UPLOAD_FOLDER'])

@bp.route('/capture-url', methods=['POST'])
def capture_url_screenshot():
    """Capture screenshot from TradingView URL"""
    data = request.json
    trade_id = data.get('trade_id')
    url = data.get('url')
    screenshot_type = data.get('type', 'before')  # 'before' or 'after'
    
    if not url or not trade_id:
        return jsonify({'error': 'Missing trade_id or url'}), 400
    
    service = get_screenshot_service()
    filename = service.capture_url(url, trade_id, screenshot_type)
    
    if not filename:
        return jsonify({'error': 'Screenshot capture failed'}), 500
    
    # Update database
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    column = 'screenshot_before' if screenshot_type == 'before' else 'screenshot_after'
    cursor.execute(f'UPDATE trades SET {column} = ? WHERE id = ?', (filename, trade_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/api/screenshots/view/{filename}'
    })

@bp.route('/capture-screen', methods=['POST'])
def capture_screen_screenshot():
    """Capture screenshot of current screen (for MT5)"""
    data = request.json
    trade_id = data.get('trade_id')
    screenshot_type = data.get('type', 'before')
    
    if not trade_id:
        return jsonify({'error': 'Missing trade_id'}), 400
    
    service = get_screenshot_service()
    filename = service.capture_mt5_window(trade_id, screenshot_type)
    
    if not filename:
        return jsonify({'error': 'Screenshot capture failed'}), 500
    
    # Update database
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    column = 'screenshot_before' if screenshot_type == 'before' else 'screenshot_after'
    cursor.execute(f'UPDATE trades SET {column} = ? WHERE id = ?', (filename, trade_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/api/screenshots/view/{filename}'
    })

@bp.route('/upload', methods=['POST'])
def upload_screenshot():
    """Upload screenshot file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    trade_id = request.form.get('trade_id')
    screenshot_type = request.form.get('type', 'before')
    
    if not trade_id:
        return jsonify({'error': 'Missing trade_id'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    service = get_screenshot_service()
    filename = service.upload_screenshot(file, trade_id, screenshot_type)
    
    if not filename:
        return jsonify({'error': 'Upload failed'}), 500
    
    # Update database
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    column = 'screenshot_before' if screenshot_type == 'before' else 'screenshot_after'
    cursor.execute(f'UPDATE trades SET {column} = ? WHERE id = ?', (filename, trade_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/api/screenshots/view/{filename}'
    })

@bp.route('/view/<filename>')
def view_screenshot(filename):
    """Serve screenshot file"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)