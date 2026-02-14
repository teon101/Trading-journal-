from playwright.sync_api import sync_playwright
import os
from datetime import datetime

class ScreenshotService:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
    
    def capture_url(self, url, trade_id, screenshot_type='before'):
        """
        Capture screenshot from a URL (TradingView)
        screenshot_type: 'before' or 'after'
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': 1920, 'height': 1080})
                
                # Navigate to URL
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait a bit for charts to render
                page.wait_for_timeout(3000)
                
                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"trade_{trade_id}_{screenshot_type}_{timestamp}.png"
                filepath = os.path.join(self.upload_folder, filename)
                
                # Take screenshot
                page.screenshot(path=filepath, full_page=False)
                
                browser.close()
                
                return filename
                
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    
    def capture_mt5_window(self, trade_id, screenshot_type='before'):
        """
        Capture screenshot of active window (for MT5)
        This will capture whatever is currently visible on screen
        """
        try:
            from PIL import ImageGrab
            
            # Capture the screen
            screenshot = ImageGrab.grab()
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trade_{trade_id}_{screenshot_type}_{timestamp}.png"
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save screenshot
            screenshot.save(filepath, 'PNG')
            
            return filename
            
        except Exception as e:
            print(f"MT5 Screenshot error: {e}")
            return None
    
    def upload_screenshot(self, file, trade_id, screenshot_type='before'):
        """
        Handle manual screenshot upload
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trade_{trade_id}_{screenshot_type}_{timestamp}.png"
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save file
            file.save(filepath)
            
            return filename
            
        except Exception as e:
            print(f"Upload error: {e}")
            return None