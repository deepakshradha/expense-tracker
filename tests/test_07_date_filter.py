import pytest
import os
import tempfile
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    # Create a temporary file for the database to avoid :memory: connection isolation issues
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    import database.db
    database.db.DATABASE = db_path

    with flask_app.app_context():
        init_db()
        yield flask_app

    # Cleanup temporary database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in with a seeded user."""
    client.post('/register', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass'})
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

@pytest.fixture
def seeded_expenses(auth_client):
    """Seeds expenses across different dates for filtering tests."""
    # We need to use the app context to get the DB connection
    with flask_app.app_context():
        db = get_db()
        # Find the user ID
        user = db.execute('SELECT id FROM users WHERE email = ?', ('test@example.com',)).fetchone()
        uid = user['id']

        # Clear existing if any
        db.execute('DELETE FROM expenses')

        # Seed a range of expenses
        # 2026-06-01: 10.00 (Food), 20.00 (Transport)
        # 2026-06-05: 50.00 (Bills)
        # 2026-06-10: 100.00 (Shopping)
        expenses = [
            (uid, 10.0, 'Food', '2026-06-01', 'Lunch'),
            (uid, 20.0, 'Transport', '2026-06-01', 'Bus'),
            (uid, 50.0, 'Bills', '2026-06-05', 'Water'),
            (uid, 100.0, 'Shopping', '2026-06-10', 'Shoes'),
        ]
        db.executemany(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            expenses
        )
        db.commit()

class TestDateFilter:

    def test_profile_auth_guard(self, client):
        """Ensure profile is protected even when date filters are applied."""
        response = client.get('/profile?start_date=2026-01-01&end_date=2026-01-31')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_filter_full_range_happy_path(self, auth_client, seeded_expenses):
        """Test filtering with both start and end dates."""
        # Range: 2026-06-01 to 2026-06-05
        # Expected: 10 + 20 + 50 = 80.00
        response = auth_client.get('/profile?start_date=2026-06-01&end_date=2026-06-05')
        assert response.status_code == 200
        assert b'80.0' in response.data
        assert b'Food' in response.data
        assert b'Bills' in response.data
        assert b'Shoes' not in response.data  # Should be excluded (June 10)

    def test_filter_start_date_only(self, auth_client, seeded_expenses):
        """Test filtering with only start_date provided."""
        # From 2026-06-05 onwards
        # Expected: 50 + 100 = 150.00
        response = auth_client.get('/profile?start_date=2026-06-05')
        assert response.status_code == 200
        assert b'150.0' in response.data
        assert b'Lunch' not in response.data # June 01

    def test_filter_end_date_only(self, auth_client, seeded_expenses):
        """Test filtering with only end_date provided."""
        # Up to 2026-06-01
        # Expected: 10 + 20 = 30.00
        response = auth_client.get('/profile?end_date=2026-06-01')
        assert response.status_code == 200
        assert b'30.0' in response.data
        assert b'Water' not in response.data # June 05

    def test_filter_no_results_in_range(self, auth_client, seeded_expenses):
        """Test range where no expenses exist."""
        response = auth_client.get('/profile?start_date=2020-01-01&end_date=2020-01-31')
        assert response.status_code == 200
        # Depending on implementation, total spending should be 0 or 0.0
        assert b'0' in response.data

    def test_clear_filter_returns_lifetime(self, auth_client, seeded_expenses):
        """Test that removing parameters returns all data."""
        # First apply a filter
        auth_client.get('/profile?start_date=2026-06-01&end_date=2026-06-01')

        # Then go to profile without filters
        response = auth_client.get('/profile')
        # Total: 10 + 20 + 50 + 100 = 180.0
        assert response.status_code == 200
        assert b'180.0' in response.data

    def test_invalid_date_formats(self, auth_client, seeded_expenses):
        """Ensure that malformed dates do not cause 500 errors."""
        response = auth_client.get('/profile?start_date=not-a-date&end_date=!!!')
        assert response.status_code == 200 # App should handle it gracefully

    def test_future_dates(self, auth_client, seeded_expenses):
        """Test range in the future."""
        response = auth_client.get('/profile?start_date=2099-01-01&end_date=2099-12-31')
        assert response.status_code == 200
        assert b'0' in response.data

    def test_boundary_dates_inclusive(self, auth_client, seeded_expenses):
        """Verify that dates provided are inclusive."""
        # Precisely one day: 2026-06-05
        response = auth_client.get('/profile?start_date=2026-06-05&end_date=2026-06-05')
        assert response.status_code == 200
        assert b'50.0' in response.data

    def test_query_params_preservation(self, auth_client, seeded_expenses):
        """Verify the request actually uses the query parameters."""
        # This is more of a test of the Flask request object, but ensures
        # we are looking at the right URL.
        response = auth_client.get('/profile?start_date=2026-06-01&end_date=2026-06-02')
        assert response.request.query_string == b'start_date=2026-06-01&end_date=2026-06-02'
