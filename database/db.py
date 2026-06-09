import sqlite3
from flask import g, current_app
from werkzeug.security import generate_password_hash

def get_db():
    """Returns the database connection for the current request."""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE', 'expense_tracker.db')
        g.db = sqlite3.connect(
            db_path,
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

def create_user(name, email, password_hash):
    """Creates a new user in the database. Returns user_id or None if email exists."""
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            (name, email, password_hash)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None

def get_user_by_email(email):
    """Retrieves a user by their email. Returns the user record or None."""
    db = get_db()
    return db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

def get_user_by_id(user_id):
    """Retrieves a user by their ID. Returns the user record or None."""
    db = get_db()
    return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

def _apply_date_filter(query, params, start_date, end_date):
    """Helper to apply optional date range filters to a query. Returns updated query and params."""
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    return query, params

def get_user_total_spending(user_id, start_date=None, end_date=None):
    """Calculates the sum of expenses for a given user within an optional date range. Returns the total or 0.0 if none."""
    db = get_db()
    query = 'SELECT SUM(amount) as total FROM expenses WHERE user_id = ?'
    params = [user_id]

    query, params = _apply_date_filter(query, params, start_date, end_date)

    result = db.execute(query, params).fetchone()
    return result['total'] if result and result['total'] is not None else 0.0

def get_user_spending_by_category(user_id, start_date=None, end_date=None):
    """Returns a list of category totals for a user within an optional date range. Result is a list of rows (category, total)."""
    db = get_db()
    query = 'SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?'
    params = [user_id]

    query, params = _apply_date_filter(query, params, start_date, end_date)
    query += ' GROUP BY category ORDER BY total DESC'
    return db.execute(query, params).fetchall()

def get_recent_expenses(user_id, limit=5, start_date=None, end_date=None):
    """Returns the most recent expenses for a user within an optional date range."""
    db = get_db()
    query = 'SELECT * FROM expenses WHERE user_id = ?'
    params = [user_id]

    query, params = _apply_date_filter(query, params, start_date, end_date)
    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)
    return db.execute(query, params).fetchall()

def get_user_transaction_count(user_id, start_date=None, end_date=None):
    """Returns the total number of expenses for a user within an optional date range."""
    db = get_db()
    query = 'SELECT COUNT(*) as count FROM expenses WHERE user_id = ?'
    params = [user_id]

    query, params = _apply_date_filter(query, params, start_date, end_date)

    result = db.execute(query, params).fetchone()
    return result['count'] if result else 0

def add_expense(user_id, amount, category, date, description):
    """Adds a new expense for a user. Returns the ID of the new expense."""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        (user_id, amount, category, date, description)
    )
    db.commit()
    return cursor.lastrowid
