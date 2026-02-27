from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.database import Database

class User(UserMixin):
    def __init__(self, id, email, password_hash, full_name, plan='free'):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.plan = plan
    
    @staticmethod
    def get(user_id, db_path):
        """Get user by ID"""
        db = Database(db_path)
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                email=row['email'],
                password_hash=row['password_hash'],
                full_name=row['full_name'],
                plan=row['plan']
            )
        return None
    
    @staticmethod
    def get_by_email(email, db_path):
        """Get user by email"""
        db = Database(db_path)
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                email=row['email'],
                password_hash=row['password_hash'],
                full_name=row['full_name'],
                plan=row['plan']
            )
        return None
    
    @staticmethod
    def create(email, password, full_name, db_path):
        """Create new user"""
        db = Database(db_path)
        conn = db.get_connection()
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(password)
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name)
                VALUES (?, ?, ?)
            ''', (email, password_hash, full_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return User.get(user_id, db_path)
        except Exception as e:
            conn.close()
            return None
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)