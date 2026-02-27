import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                plan TEXT DEFAULT 'free'
            )
        ''')

        # Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL
            )
        ''')

        # Trades table (with user_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                pair TEXT NOT NULL,
                session TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                setup_type TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                position_size REAL NOT NULL,
                risk_amount REAL NOT NULL,
                reward_amount REAL NOT NULL,
                risk_reward_ratio REAL NOT NULL,
                risk_percentage REAL,
                confidence INTEGER,
                emotion_before TEXT,
                rule_followed INTEGER DEFAULT 1,
                entry_time TIMESTAMP NOT NULL,
                exit_time TIMESTAMP,
                exit_price REAL,
                profit_loss REAL,
                status TEXT DEFAULT 'open',
                notes TEXT,
                screenshot_before TEXT,
                screenshot_after TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Trade tags junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_tags (
                trade_id INTEGER,
                tag_id   INTEGER,
                FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id)   REFERENCES tags(id)   ON DELETE CASCADE,
                PRIMARY KEY (trade_id, tag_id)
            )
        ''')

        # Default mistake tags
        default_tags = [
            ('Early Entry',    '#ef4444'),
            ('Overtrade',      '#f97316'),
            ('News Trade',     '#eab308'),
            ('FOMO',           '#dc2626'),
            ('Revenge Trade',  '#b91c1c'),
            ('No Stop Loss',   '#991b1b'),
            ('Moved Stop Loss', '#7f1d1d')
        ]

        for name, color in default_tags:
            cursor.execute(
                'INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)',
                (name, color)
            )

        conn.commit()
        conn.close()