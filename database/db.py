import sqlite3
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = 'expense_tracker.db'

def get_db():
    """Returns the database connection for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def init_db():
    """Initializes the database and creates all tables."""
    db = get_db()

    # Users Table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Expenses Table
    db.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Food', 'Transport', 'Bills', 'Health', 'Entertainment', 'Shopping', 'Other')),
            date DATE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    db.commit()

def seed_db():
    """Populates the database with sample data for development."""
    db = get_db()

    # Only seed if the users table is empty
    user_count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_count > 0:
        return

    # Create a demo user
    password_hash = generate_password_hash('password123')
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Test User', 'test@example.com', password_hash)
    )
    user_id = cursor.lastrowid

    # Sample expenses
    sample_expenses = [
        (user_id, 15.50, 'Food', '2026-06-01', 'Lunch at Cafe'),
        (user_id, 45.00, 'Transport', '2026-06-01', 'Gas refill'),
        (user_id, 120.00, 'Bills', '2026-06-02', 'Electric bill'),
        (user_id, 30.00, 'Health', '2026-06-02', 'Pharmacy'),
        (user_id, 60.00, 'Entertainment', '2026-06-03', 'Cinema and snacks'),
        (user_id, 100.00, 'Shopping', '2026-06-03', 'New clothes'),
        (user_id, 12.00, 'Food', '2026-06-04', 'Coffee and bagel'),
        (user_id, 25.00, 'Other', '2026-06-04', 'Gift wrap'),
    ]

    db.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        sample_expenses
    )
    db.commit()
