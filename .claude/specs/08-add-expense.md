# Spec: Add Expense

## Overview
This feature allows authenticated users to record their spending by adding new expenses to their account. It provides a user-friendly form to capture the amount, category, date, and an optional description for each transaction, enabling the core functionality of the Spendly expense tracker.

## Depends on
- User Authentication (Login/Session)
- Database setup (`users` and `expenses` tables)

## Routes
- `GET /expenses/add` — Renders the expense addition form — logged-in
- `POST /expenses/add` — Processes the form submission and saves the expense to the database — logged-in

## Database changes
No database changes. The `expenses` table already contains the necessary columns: `user_id`, `amount`, `category`, `date`, and `description`.

## Templates
- **Create:** `templates/add_expense.html` (extends `base.html`)

## Files to change
- `app.py`: Implement the `add_expense` route to handle both GET (display form) and POST (save data) requests.
- `database/db.py`: Add a new helper function `add_expense(user_id, amount, category, date, description)` to handle the insertion of a new record.

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (not applicable here, but standard for project)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that all required fields (amount, category, date) are provided.
- Validate that the amount is a positive numerical value.
- Ensure the date is submitted in `YYYY-MM-DD` format.

## Definition of done
- [ ] Logged-in users can access the `/expenses/add` page.
- [ ] Unauthenticated users are redirected to the login page when attempting to access `/expenses/add`.
- [ ] The add expense form contains fields for amount, category (dropdown), date, and description.
- [ ] Submitting a valid form successfully creates a record in the `expenses` table associated with the current user.
- [ ] Submitting a form with missing required fields triggers an appropriate error flash message.
- [ ] Submitting a form with an invalid amount (e.g., negative or non-numeric) triggers an error flash message.
- [ ] Upon successful submission, the user is redirected to the profile page with a success flash message.
- [ ] The newly added expense is immediately visible in the "Recent Expenses" section of the profile page.
