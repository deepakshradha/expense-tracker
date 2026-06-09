import pytest
from app import app as flask_app
from database.db import init_db, get_db


@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': 'test_expense_tracker.db',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        db = get_db()
        db.execute('DELETE FROM expenses')
        db.execute('DELETE FROM users')
        db.commit()
        yield flask_app



@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={'name': 'testuser', 'email': 'test@example.com', 'password': 'testpass'})
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client


@pytest.fixture
def seeded_expense(app, auth_client):
    """Adds one expense for the logged-in user and returns its DB id."""
    auth_client.post('/expenses/add', data={
        'amount': '50.00',
        'category': 'Food',
        'date': '2024-01-15',
        'description': 'Test meal',
    })
    with app.app_context():
        db = get_db()
        user_id = db.execute(
            'SELECT id FROM users WHERE email = ?', ('test@example.com',)
        ).fetchone()[0]
        row = db.execute(
            'SELECT id FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 1',
            (user_id,)
        ).fetchone()
        return row[0]


class TestDeleteExpense:

    def test_delete_unauthenticated_redirects(self, app, seeded_expense):
        """Unauthenticated users should be redirected to login on POST."""
        fresh_client = app.test_client(use_cookies=False)
        response = fresh_client.post(f'/expenses/{seeded_expense}/delete')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_delete_nonexistent_returns_404(self, auth_client):
        """POST to a non-existent expense ID should return 404."""
        response = auth_client.post('/expenses/999999/delete')
        assert response.status_code == 404

    def test_delete_other_users_expense_returns_403(self, app, auth_client):
        """A user should not be able to delete another user's expense (403)."""
        # Register and log in as a second user
        other_client = app.test_client()
        other_client.post('/register', data={
            'name': 'Other User',
            'email': 'other@example.com',
            'password': 'otherpass',
        })
        other_client.post('/login', data={
            'email': 'other@example.com',
            'password': 'otherpass',
        })
        # Add an expense as the second user
        other_client.post('/expenses/add', data={
            'amount': '99.99',
            'category': 'Bills',
            'date': '2024-02-01',
            'description': 'Other bill',
        })
        # Find the other user's expense id
        with app.app_context():
            db = get_db()
            other_user = db.execute(
                'SELECT id FROM users WHERE email = ?', ('other@example.com',)
            ).fetchone()
            other_expense = db.execute(
                'SELECT id FROM expenses WHERE user_id = ? LIMIT 1', (other_user[0],)
            ).fetchone()[0]

        # The first (auth_client) user tries to delete the second user's expense
        response = auth_client.post(f'/expenses/{other_expense}/delete')
        assert response.status_code == 403

    def test_delete_success_removes_from_db(self, app, auth_client, seeded_expense):
        """Successful deletion should remove the record from the database."""
        response = auth_client.post(f'/expenses/{seeded_expense}/delete')
        assert response.status_code == 302

        with app.app_context():
            db = get_db()
            row = db.execute(
                'SELECT * FROM expenses WHERE id = ?', (seeded_expense,)
            ).fetchone()
            assert row is None

    def test_delete_success_redirects_to_profile(self, auth_client, seeded_expense):
        """Successful deletion should redirect to the profile page."""
        response = auth_client.post(f'/expenses/{seeded_expense}/delete')
        assert response.status_code == 302
        assert '/profile' in response.location

    def test_delete_success_flash_message(self, auth_client, seeded_expense):
        """A success flash message should appear after deletion."""
        response = auth_client.post(f'/expenses/{seeded_expense}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'deleted' in response.data.lower() or b'success' in response.data.lower()

    def test_delete_updates_profile_stats(self, app, auth_client, seeded_expense):
        """Deleting an expense should update the user's spending stats on profile page."""
        # Check profile stats before delete
        profile_before = auth_client.get('/profile')
        assert b'50.00' in profile_before.data

        # Delete the expense
        auth_client.post(f'/expenses/{seeded_expense}/delete')

        # Check profile stats after delete
        profile_after = auth_client.get('/profile')
        assert b'50.00' not in profile_after.data
        assert b'0.00' in profile_after.data

    def test_delete_via_get_not_allowed(self, auth_client, seeded_expense):
        """GET request to the delete endpoint should not be allowed (405)."""
        response = auth_client.get(f'/expenses/{seeded_expense}/delete')
        assert response.status_code == 405

    def test_confirm_dialog_present_in_template(self, auth_client, seeded_expense):
        """The profile template should contain the JS confirm confirmation dialog."""
        response = auth_client.get('/profile')
        assert response.status_code == 200
        assert b'confirm(' in response.data
        assert b'/delete' in response.data

