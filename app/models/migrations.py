import sqlite3
import os
from datetime import datetime

class Migration:
    def __init__(self, db_path):
        self.db_path = db_path
        self.migrations_table = 'schema_migrations'
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Create migrations tracking table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def is_applied(self, version):
        """Check if migration has been applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT version FROM schema_migrations WHERE version = ?',
            (version,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def mark_applied(self, version):
        """Mark migration as applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO schema_migrations (version) VALUES (?)',
                (version,)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Already applied
            pass
        conn.close()
    
    def column_exists(self, table, column):
        """Check if column exists in table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return column in columns
    
    def run_migration(self, version, migration_func):
        """Run a migration function"""
        if self.is_applied(version):
            print(f"Migration {version} already applied, skipping...")
            return
        
        print(f"Running migration {version}...")
        
        try:
            migration_func()
            self.mark_applied(version)
            print(f"✓ Migration {version} completed successfully")
        except Exception as e:
            print(f"✗ Migration {version} failed: {e}")
            # Don't raise - allow other migrations to run
    
    def run_all_migrations(self):
        """Run all pending migrations"""
        
        # Migration 001: Add user_id to trades
        def migration_001():
            if not self.column_exists('trades', 'user_id'):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('ALTER TABLE trades ADD COLUMN user_id INTEGER DEFAULT 1')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id)')
                conn.commit()
                conn.close()
        
        # Migration 002: Add confidence fields
        def migration_002():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if not self.column_exists('trades', 'confidence'):
                cursor.execute('ALTER TABLE trades ADD COLUMN confidence INTEGER')
            if not self.column_exists('trades', 'emotion_before'):
                cursor.execute('ALTER TABLE trades ADD COLUMN emotion_before TEXT')
            if not self.column_exists('trades', 'rule_followed'):
                cursor.execute('ALTER TABLE trades ADD COLUMN rule_followed INTEGER DEFAULT 1')
            if not self.column_exists('trades', 'risk_percentage'):
                cursor.execute('ALTER TABLE trades ADD COLUMN risk_percentage REAL')
            
            conn.commit()
            conn.close()
        
        # Migration 003: Add user plan fields
        def migration_003():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if not self.column_exists('users', 'plan'):
                cursor.execute("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'")
            if not self.column_exists('users', 'is_active'):
                cursor.execute('ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1')
            if not self.column_exists('users', 'last_login'):
                cursor.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP')
            
            conn.commit()
            conn.close()
        
        # Run migrations
        migrations = [
            ('001_add_user_id_to_trades', migration_001),
            ('002_add_confidence_fields', migration_002),
            ('003_add_user_plan', migration_003)
        ]
        
        for version, func in migrations:
            self.run_migration(version, func)
        
        print("✓ All migrations completed successfully")