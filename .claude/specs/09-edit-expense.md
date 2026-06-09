# Spec: Edit Expense

## Overview
This feature allows authenticated users to modify details of their existing expenses. Users can access an edit form pre-populated with the current expense data (amount, category, date, and description). When the form is submitted, the expense is updated in the database, and the user is redirected back to their profile page. This ensures users can correct mistakes or update expense details seamlessly.

## Depends on
- User Authentication (Login/Session)
- Database setup (`users` and `expenses` tables)
- Add Expense feature (or at least `expenses` data view on Profile page)

## Routes
- `GET /expenses/<int:id>/edit` — Renders the expense editing form, pre-populated with current details — logged-in
- `POST /expenses/<int:id>/edit` — Processes the form submission and updates the expense in the database — logged-in

## Database changes
No database changes. The `expenses` table already contains the necessary columns: `id`, `user_id`, `amount`, `category`, `date`, and `description`.

## Templates
- **Create:** `templates/edit_expense.html` (extends `base.html`)
- **Modify:** `templates/profile.html` (add an "Edit" action link/icon for each expense in the transactions table)

## Files to change
- `app.py`:
  - Implement `edit_expense(id)` route to handle GET (retrieve and render form with current values) and POST (validate and update database).
  - Ensure users can only edit expenses belonging to them (check `expense['user_id'] == session['user_id']`).
- `database/db.py`:
  - Add `get_expense_by_id(expense_id)` function to fetch a single expense record.
  - Add `update_expense(expense_id, amount, category, date, description)` function to update an existing expense record.
- `templates/profile.html`:
  - Add an edit action link/icon next to each expense in the "Recent Expenses" list.

## Files to create
- `templates/edit_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Ensure users can only edit their own expenses (prevent ID-based horizontal privilege escalation).
- Validate that all required fields (amount, category, date) are provided.
- Validate that the amount is a positive numerical value.
- Ensure the date is submitted in `YYYY-MM-DD` format.

## Definition of done
- [ ] Logged-in users can click an "Edit" link next to an expense on the profile page and be navigated to `/expenses/<id>/edit`.
- [ ] Unauthenticated users attempting to access `/expenses/<id>/edit` are redirected to the login page.
- [ ] An authenticated user trying to edit someone else's expense gets a 403 or 404 error (or is redirected with an error flash message).
- [ ] The edit page displays a form pre-populated with the current amount, category, date, and description.
- [ ] Submitting the form with valid data updates the expense in the database and redirects the user to the profile page with a success flash message.
- [ ] Submitting the form with missing required fields triggers an appropriate error flash message.
- [ ] Submitting the form with an invalid amount (e.g., negative or non-numeric) triggers an error flash message.
- [ ] The updated details are immediately reflected on the profile page.
