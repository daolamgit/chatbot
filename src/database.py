import sqlite3
import os
from datetime import datetime
import threading

class ChatDatabase:
    def __init__(self, db_path="chat_history.db"):
        """Initialize the database connection."""
        self.db_path = db_path
        # Use thread-local storage for connections
        self.local = threading.local()
        self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database, creating a connection per thread."""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn
    
    def close(self):
        """Close all database connections."""
        if hasattr(self.local, 'conn'):
            self.local.conn.close()
            delattr(self.local, 'conn')
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        
        conn.commit()
    
    def save_message(self, sender, text):
        """Save a message to the database."""
        conn = self.connect()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO messages (sender, text, timestamp) VALUES (?, ?, ?)",
            (sender, text, timestamp)
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def get_recent_messages(self, limit=50):
        """Retrieve recent messages from the database."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        return cursor.fetchall()
    
    def get_messages_by_sender(self, sender):
        """Retrieve messages from a specific sender."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM messages WHERE sender = ? ORDER BY timestamp",
            (sender,)
        )
        
        return cursor.fetchall() 