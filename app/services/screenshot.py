import os
from werkzeug.utils import secure_filename
from datetime import datetime

class ScreenshotService:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def upload_screenshot(self, file, trade_id, screenshot_type='before'):
        """Upload screenshot file"""
        if not file:
            return None
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"trade_{trade_id}_{screenshot_type}_{timestamp}.png")
        
        # Save file
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        
        return filename
