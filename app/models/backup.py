import shutil
import os
from datetime import datetime
import gzip

class DatabaseBackup:
    def __init__(self, db_path, backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Create a compressed backup of the database"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"trading_journal_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Copy database
            shutil.copy2(self.db_path, backup_path)
            
            # Compress
            compressed_path = f"{backup_path}.gz"
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed
            os.remove(backup_path)
            
            print(f"✓ Backup created: {compressed_path}")
            return compressed_path
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            return None
    
    def restore_backup(self, backup_file):
        """Restore database from backup"""
        try:
            # Extract compressed backup
            extracted_path = backup_file.replace('.gz', '')
            with gzip.open(backup_file, 'rb') as f_in:
                with open(extracted_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Backup current database
            current_backup = f"{self.db_path}.before_restore"
            shutil.copy2(self.db_path, current_backup)
            
            # Restore
            shutil.copy2(extracted_path, self.db_path)
            os.remove(extracted_path)
            
            print(f"✓ Database restored from: {backup_file}")
            print(f"  Previous database backed up to: {current_backup}")
            return True
        except Exception as e:
            print(f"✗ Restore failed: {e}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.db.gz'):
                filepath = os.path.join(self.backup_dir, file)
                size = os.path.getsize(filepath) / 1024  # KB
                backups.append({
                    'filename': file,
                    'path': filepath,
                    'size_kb': round(size, 2),
                    'created': datetime.fromtimestamp(os.path.getctime(filepath))
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self, keep_count=10):
        """Keep only the most recent N backups"""
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                os.remove(backup['path'])
                print(f"Removed old backup: {backup['filename']}")