# Spec: Delete Expense

## Overview
This feature allows authenticated users to permanently remove an expense they own. A "Delete" button is added alongside the existing "Edit" action in the Recent Expenses table on the profile page. Because deletion is destructive and irreversible, the user must confirm the action via a browser confirmation dialog (using a small inline form + `onclick` confirm) before the request is submitted. The server validates ownership before executing the DELETE query. On success, the user is redirected back to the profile page with a success flash message; the summary stats and transaction count update immediately to reflect the removed record.

## Depends on
- User Authentication — Login / Session (Step 03)
- Profile Page with Recent Expenses table (Steps 05 & 06)
- Add Expense feature — `expenses` table must exist (Step 08)
- Edit Expense — `get_expense_by_id` DB helper already in place (Step 09)

## Routes
- `POST /expenses/<int:id>/delete` — Deletes the expense that belongs to the logged-in user — logged-in

> **Note:** The route uses `POST` (not `GET`) to comply with HTTP semantics for destructive operations and to prevent accidental deletion via link pre-fetch or browser history navigation. The existing placeholder `GET` route in `app.py` must be replaced.

## Database changes
No new tables or columns required. A new helper function `delete_expense(expense_id, user_id)` will be added to `database/db.py`. The `expenses` table already has `ON DELETE CASCADE` on `user_id`, so no schema change is needed.

## Templates
- **Modify:** `templates/profile.html`
  - Replace the placeholder `Edit`-only Actions cell with a two-button cell containing both an "Edit" link and a "Delete" form/button.
  - The Delete button must trigger a `window.confirm()` dialog before submitting the form.

## Files to change
- `app.py`:
  - Remove the existing placeholder `GET /expenses/<int:id>/delete` route.
  - Implement a new `POST /expenses/<int:id>/delete` route (`delete_expense` view function) that:
    1. Requires the user to be logged in (redirect to login if not).
    2. Fetches the expense with `db_get_expense_by_id`; returns 404 if not found.
    3. Returns 403 if `expense['user_id'] != session['user_id']`.
    4. Calls `db_delete_expense(expense_id, user_id)`.
    5. Flashes a success message and redirects to `profile`.
  - Update the import line to include `delete_expense as db_delete_expense` from `database.db`.
- `database/db.py`:
  - Add `delete_expense(expense_id, user_id)` function that executes a parameterised `DELETE FROM expenses WHERE id = ? AND user_id = ?` and commits.
- `templates/profile.html`:
  - In the Actions `<td>`, add a `<form>` that POSTs to `/expenses/<id>/delete` with an `onclick="return confirm(...)"` on the submit button, alongside the existing Edit link.

## Files to create
- `static/css/delete_expense.css` *(optional)* — scoped styles for the delete button if the existing `profile.css` variables are insufficient. May be omitted if the delete button styling can be handled purely with CSS variables already defined in `profile.css`.

> If a separate CSS file is created, it must be linked from `profile.html` via `url_for`.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (unchanged — no password operations here)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- The delete route **must** be `POST`, never `GET`
- Ownership must be verified server-side (check `expense['user_id'] == session['user_id']`) before deletion — do not rely solely on the client-side confirm dialog
- The `db_delete_expense` query must scope the `WHERE` clause to both `id` **and** `user_id` for defence-in-depth, matching the pattern used in `update_expense`
- Provide clear user feedback: a success flash on deletion, or an error flash if something goes wrong

## Definition of done
- [ ] A "Delete" button is visible in the Actions column next to each expense on the profile page.
- [ ] Clicking "Delete" shows a browser confirmation dialog; cancelling the dialog does **not** submit the form.
- [ ] Confirming the dialog submits a `POST` request to `/expenses/<id>/delete`.
- [ ] Unauthenticated users attempting to POST to `/expenses/<id>/delete` are redirected to the login page.
- [ ] An authenticated user attempting to delete another user's expense receives a 403 error.
- [ ] Deleting a non-existent expense ID returns a 404 error.
- [ ] After successful deletion the user is redirected to the profile page with a success flash message (e.g. "Expense deleted successfully!").
- [ ] The deleted expense no longer appears in the Recent Expenses table.
- [ ] The Total Spent, Transactions count, and Top Category stats on the profile page update correctly after deletion.
- [ ] The `delete_expense` DB function uses a parameterised query scoped to both `id` and `user_id`.
