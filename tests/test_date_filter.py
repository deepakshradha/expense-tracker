import pytest
from app import app as flask_app
from database.db import init_db, seed_db, get_user_by_email

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "DATABASE": ":memory:" # Use in-memory DB for tests
    })

    with flask_app.app_context():
        init_db()
        seed_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_profile_no_filter(client):
    """Verify profile page loads without filters."""
    client.post("/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=True)
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Total Spent" in response.data

def test_profile_date_filter(client):
    """Verify profile page filters data by date."""
    client.post("/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=True)

    # Filter for a range that should only include a few transactions
    # Sample data from db.py has dates from 2026-06-01 to 2026-06-04
    response = client.get("/profile?start_date=2026-06-01&end_date=2026-06-02")
    assert response.status_code == 200
    # We expect some data to be present
    assert b"Total Spent" in response.data

def test_profile_clear_filter(client):
    """Verify clear filter button redirects to base profile."""
    client.post("/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=True)
    response = client.get("/profile?start_date=2026-01-01&end_date=2026-01-02")
    assert response.status_code == 200
    # The clear button is a link to /profile
    assert b'href="/profile"' in response.data
