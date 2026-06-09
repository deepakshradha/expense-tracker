import pytest
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': 'test_expense_tracker.db',  # Use a file-based DB for consistency across requests
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

class TestAddExpense:

    # --- Access Control ---

    def test_add_expense_page_unauthenticated_redirects(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get('/expenses/add')
        assert response.status_code == 302
        assert response.location == '/login'

    def test_add_expense_page_authenticated_loads(self, auth_client):
        """Authenticated users should be able to view the add expense form."""
        response = auth_client.get('/expenses/add')
        assert response.status_code == 200
        assert b'Add Expense' in response.data  # Assuming header/title exists

    # --- Validation ---

    @pytest.mark.parametrize("payload", [
        {'amount': '', 'category': 'Food', 'date': '2023-01-01'}, # missing amount
        {'amount': '10.00', 'category': '', 'date': '2023-01-01'}, # missing category
        {'amount': '10.00', 'category': 'Food', 'date': ''},     # missing date
        {'amount': '', 'category': '', 'date': ''},              # all missing
    ])
    def test_add_expense_missing_fields_fails(self, auth_client, payload):
        """Missing required fields should trigger an error flash."""
        response = auth_client.post('/expenses/add', data=payload, follow_redirects=True)
        assert response.status_code == 200
        # The spec mentions "appropriate error flash message"
        assert b'Error' in response.data or b'required' in response.data.lower()

    @pytest.mark.parametrize("invalid_amount", [
        'abc',
        '-10.00',
        '0',
        'ten'
    ])
    def test_add_expense_invalid_amount_fails(self, auth_client, invalid_amount):
        """Amounts must be positive numerical values."""
        payload = {
            'amount': invalid_amount,
            'category': 'Food',
            'date': '2023-01-01',
            'description': 'Test'
        }
        response = auth_client.post('/expenses/add', data=payload, follow_redirects=True)
        assert response.status_code == 200
        assert b'Error' in response.data or b'amount' in response.data.lower()

    def test_add_expense_invalid_date_format_fails(self, auth_client):
        """Dates must be in YYYY-MM-DD format."""
        payload = {
            'amount': '10.00',
            'category': 'Food',
            'date': '01-01-2023', # Wrong format
            'description': 'Test'
        }
        response = auth_client.post('/expenses/add', data=payload, follow_redirects=True)
        assert response.status_code == 200
        assert b'Error' in response.data or b'date' in response.data.lower()

    # --- Happy Path & DB Side Effects ---

    def test_add_expense_success_creates_record(self, app, auth_client):
        """Valid submission should create a DB record and redirect to profile."""
        payload = {
            'amount': '25.50',
            'category': 'Transport',
            'date': '2023-10-27',
            'description': 'Taxi to office'
        }

        response = auth_client.post('/expenses/add', data=payload, follow_redirects=True)

        # 1. Verify redirection to profile (implied by spec)
        assert response.status_code == 200
        assert b'Profile' in response.data or '/profile' in response.request.path

        # 2. Verify success flash message
        assert b'success' in response.data.lower() or b'added' in response.data.lower()

        # 3. Verify DB side effect
        with app.app_context():
            db = get_db()
            # Get current user id
            user_id = db.execute('SELECT id FROM users WHERE email = ?', ('test@example.com',)).fetchone()[0]

            expense = db.execute(
                'SELECT amount, category, date, description FROM expenses WHERE user_id = ?',
                (user_id,)
            ).fetchone()

            assert expense is not None
            assert float(expense[0]) == 25.50
            assert expense[1] == 'Transport'
            assert str(expense[2]) == '2023-10-27'
            assert expense[3] == 'Taxi to office'

    def test_add_expense_visible_on_profile(self, auth_client):
        """The newly added expense should be visible in the Recent Expenses section."""
        payload = {
            'amount': '99.99',
            'category': 'Shopping',
            'date': '2023-10-27',
            'description': 'New Shoes'
        }
        auth_client.post('/expenses/add', data=payload)

        # Visit profile page
        response = auth_client.get('/profile')
        assert response.status_code == 200
        assert b'99.99' in response.data
        assert b'New Shoes' in response.data
        assert b'Shopping' in response.data
