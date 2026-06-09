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


class TestEditExpense:

    # ------------------------------------------------------------------ #
    # Access Control                                                       #
    # ------------------------------------------------------------------ #

    def test_edit_expense_unauthenticated_redirects(self, app, seeded_expense):
        """Unauthenticated users should be redirected to login."""
        # Use a completely fresh client with no session cookies
        fresh_client = app.test_client(use_cookies=False)
        response = fresh_client.get(f'/expenses/{seeded_expense}/edit')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_edit_expense_authenticated_loads_form(self, auth_client, seeded_expense):
        """Authenticated owner should see the edit form for their expense."""
        response = auth_client.get(f'/expenses/{seeded_expense}/edit')
        assert response.status_code == 200
        assert b'Edit Expense' in response.data

    def test_edit_expense_nonexistent_returns_404(self, auth_client):
        """Requesting an expense ID that does not exist should return 404."""
        response = auth_client.get('/expenses/999999/edit')
        assert response.status_code == 404

    def test_edit_expense_other_users_expense_returns_403(self, app, auth_client):
        """A user should not be able to edit another user's expense (403)."""
        # Register and log in as a second user using a fresh HTTP client
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

        # The first (auth_client) user tries to edit the second user's expense
        response = auth_client.get(f'/expenses/{other_expense}/edit')
        assert response.status_code == 403

    # ------------------------------------------------------------------ #
    # Form Pre-population                                                  #
    # ------------------------------------------------------------------ #

    def test_edit_expense_form_prepopulated(self, auth_client, seeded_expense):
        """The edit form should contain the current expense values."""
        response = auth_client.get(f'/expenses/{seeded_expense}/edit')
        assert response.status_code == 200
        data = response.data
        assert b'50' in data          # amount
        assert b'2024-01-15' in data  # date
        assert b'Test meal' in data   # description
        # Seeded category 'Food' should appear selected
        assert b'Food' in data

    # ------------------------------------------------------------------ #
    # Validation — POST                                                    #
    # ------------------------------------------------------------------ #

    @pytest.mark.parametrize("payload", [
        {'amount': '',     'category': 'Food', 'date': '2024-01-01'},  # missing amount
        {'amount': '10',   'category': '',     'date': '2024-01-01'},  # missing category
        {'amount': '10',   'category': 'Food', 'date': ''},            # missing date
        {'amount': '',     'category': '',     'date': ''},            # all missing
    ])
    def test_edit_expense_missing_fields_fails(self, auth_client, seeded_expense, payload):
        """Missing required fields should trigger an error flash, not update DB."""
        response = auth_client.post(
            f'/expenses/{seeded_expense}/edit', data=payload, follow_redirects=True
        )
        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'error' in response.data.lower()

    @pytest.mark.parametrize("invalid_amount", ['abc', '-10.00', '0', 'ten'])
    def test_edit_expense_invalid_amount_fails(self, auth_client, seeded_expense, invalid_amount):
        """Non-positive or non-numeric amounts should be rejected."""
        payload = {
            'amount': invalid_amount,
            'category': 'Food',
            'date': '2024-01-01',
            'description': 'Test',
        }
        response = auth_client.post(
            f'/expenses/{seeded_expense}/edit', data=payload, follow_redirects=True
        )
        assert response.status_code == 200
        assert b'amount' in response.data.lower() or b'error' in response.data.lower()

    def test_edit_expense_invalid_date_format_fails(self, auth_client, seeded_expense):
        """Dates not in YYYY-MM-DD format should be rejected."""
        payload = {
            'amount': '10.00',
            'category': 'Food',
            'date': '15-01-2024',  # wrong format
            'description': 'Test',
        }
        response = auth_client.post(
            f'/expenses/{seeded_expense}/edit', data=payload, follow_redirects=True
        )
        assert response.status_code == 200
        assert b'date' in response.data.lower() or b'error' in response.data.lower()

    # ------------------------------------------------------------------ #
    # Happy Path & DB Side Effects                                         #
    # ------------------------------------------------------------------ #

    def test_edit_expense_success_updates_db(self, app, auth_client, seeded_expense):
        """Valid submission should update the DB record."""
        payload = {
            'amount': '75.00',
            'category': 'Transport',
            'date': '2024-03-10',
            'description': 'Updated description',
        }
        response = auth_client.post(
            f'/expenses/{seeded_expense}/edit', data=payload, follow_redirects=True
        )
        assert response.status_code == 200

        with app.app_context():
            db = get_db()
            row = db.execute(
                'SELECT amount, category, date, description FROM expenses WHERE id = ?',
                (seeded_expense,)
            ).fetchone()
            assert row is not None
            assert float(row[0]) == 75.00
            assert row[1] == 'Transport'
            assert str(row[2]) == '2024-03-10'
            assert row[3] == 'Updated description'

    def test_edit_expense_success_redirects_to_profile(self, auth_client, seeded_expense):
        """After a successful update the user should land on the profile page."""
        payload = {
            'amount': '30.00',
            'category': 'Health',
            'date': '2024-04-01',
            'description': 'Doctor visit',
        }
        response = auth_client.post(
            f'/expenses/{seeded_expense}/edit', data=payload, follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Profile' in response.data or b'profile' in response.request.path.encode()

    def test_edit_expense_success_flash_message(self, auth_client, seeded_expense):
        """A success flash message should appear after a valid update."""
        payload = {
            'amount': '40.00',
            'category': 'Shopping',
            'date': '2024-05-20',
            'description': 'Clothes',
        }
        response = auth_client.post(
            f'/expenses/{seeded_expense}/edit', data=payload, follow_redirects=True
        )
        assert response.status_code == 200
        assert b'updated' in response.data.lower() or b'success' in response.data.lower()

    def test_edit_expense_updated_values_visible_on_profile(self, auth_client, seeded_expense):
        """Updated expense values should immediately appear on the profile page."""
        payload = {
            'amount': '123.45',
            'category': 'Entertainment',
            'date': '2024-06-15',
            'description': 'Cinema night',
        }
        auth_client.post(f'/expenses/{seeded_expense}/edit', data=payload)

        response = auth_client.get('/profile')
        assert response.status_code == 200
        assert b'123.45' in response.data
        assert b'Cinema night' in response.data
        assert b'Entertainment' in response.data

    def test_edit_expense_optional_description_can_be_blank(self, app, auth_client, seeded_expense):
        """Description is optional — clearing it should save an empty/null value without error."""
        payload = {
            'amount': '10.00',
            'category': 'Other',
            'date': '2024-07-01',
            'description': '',  # intentionally blank
        }
        response = auth_client.post(
            f'/expenses/{seeded_expense}/edit', data=payload, follow_redirects=True
        )
        assert response.status_code == 200
        # Should succeed — no error flash expected
        assert b'error' not in response.data.lower() or b'updated' in response.data.lower()

        with app.app_context():
            db = get_db()
            row = db.execute(
                'SELECT description FROM expenses WHERE id = ?', (seeded_expense,)
            ).fetchone()
            # Description is either empty string or None — both acceptable
            assert row[0] in ('', None)
