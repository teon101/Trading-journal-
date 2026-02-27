#!/usr/bin/env python
"""
Management CLI for TradeJournal
Usage:
    python manage.py migrate        # Run database migrations
    python manage.py backup         # Create database backup
    python manage.py restore <file> # Restore from backup
    python manage.py list-backups   # List all backups
    python manage.py create-user    # Create a new user
    python manage.py clean-sample-data  # Remove sample/test trades (user_id=1)
"""

import sys
import os
import getpass
import sqlite3
from app.models.migrations import Migration
from app.models.backup import DatabaseBackup
from app.models.user import User

DATABASE_PATH = 'database/trading_journal.db'

def migrate():
    """Run database migrations"""
    print("Running migrations...")
    migration = Migration(DATABASE_PATH)
    migration.run_all_migrations()
    print("✓ Migrations complete")

def backup():
    """Create database backup"""
    print("Creating backup...")
    backup_system = DatabaseBackup(DATABASE_PATH)
    backup_file = backup_system.create_backup()
    if backup_file:
        print(f"✓ Backup created: {backup_file}")
    else:
        print("✗ Backup failed")

def restore(backup_file):
    """Restore database from backup"""
    if not os.path.exists(backup_file):
        print(f"✗ Backup file not found: {backup_file}")
        return
    
    confirm = input(f"⚠️  This will replace the current database. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Restore cancelled")
        return
    
    print(f"Restoring from {backup_file}...")
    backup_system = DatabaseBackup(DATABASE_PATH)
    if backup_system.restore_backup(backup_file):
        print("✓ Restore complete")
    else:
        print("✗ Restore failed")

def list_backups():
    """List all available backups"""
    backup_system = DatabaseBackup(DATABASE_PATH)
    backups = backup_system.list_backups()
    
    if not backups:
        print("No backups found")
        return
    
    print("\n📦 Available Backups:")
    print("-" * 70)
    for backup in backups:
        print(f"{backup['filename']}")
        print(f"  Size: {backup['size_kb']} KB")
        print(f"  Created: {backup['created']}")
        print()

def create_user():
    """Create a new user"""
    print("\n👤 Create New User")
    print("-" * 40)
    
    email = input("Email: ")
    full_name = input("Full Name: ")
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("✗ Passwords don't match")
        return
    
    user = User.create(email, password, full_name, DATABASE_PATH)
    
    if user:
        print(f"✓ User created: {email}")
    else:
        print("✗ User creation failed (email may already exist)")

def cleanup_backups():
    """Clean up old backups"""
    backup_system = DatabaseBackup(DATABASE_PATH)
    keep = int(input("How many recent backups to keep? (default 10): ") or 10)
    backup_system.cleanup_old_backups(keep_count=keep)
    print("✓ Cleanup complete")

def clean_sample_data():
    """Remove all sample/test trades"""
    confirm = input("⚠️  This will delete all trades for user_id=1. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trades WHERE user_id = 1')
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✓ Deleted {deleted} sample trades")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    commands = {
        'migrate': migrate,
        'backup': backup,
        'restore': lambda: restore(sys.argv[2] if len(sys.argv) > 2 else None),
        'list-backups': list_backups,
        'create-user': create_user,
        'cleanup-backups': cleanup_backups,
        'clean-sample-data': clean_sample_data
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == '__main__':
    main()