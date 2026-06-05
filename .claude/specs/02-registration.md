# Spec: Registration

## Overview
Registration allows new users to create an account in Spendly. This feature implements the backend logic for the registration form, including input validation, password hashing, and database persistence, ensuring that only valid and unique users can sign up.

## Depends on
- 01-database-setup

## Routes
- `GET /register` — Renders the registration form — public
- `POST /register` — Validates and processes registration data, creates a new user in the database — public

## Database changes
No database changes. Uses the existing `users` table.

## Templates
- **Modify:** `templates/register.html` — Update to be a functional HTML form that posts to `/register`.

## Files to change
- `app.py` — Add `POST /register` route logic and necessary imports (e.g., `request`, `redirect`, `url_for`, `flash`).
- `database/db.py` — Add a helper function `create_user(name, email, password_hash)` to handle the insertion.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] `GET /register` renders a registration form with fields for name, email, and password.
- [ ] `POST /register` ensures all required fields (name, email, password) are provided; otherwise, it returns an error.
- [ ] `POST /register` prevents registration with an email that already exists in the database, returning a user-friendly error message.
- [ ] `POST /register` hashes the password before saving it to the database.
- [ ] A new user record is successfully created in the `users` table upon valid submission.
- [ ] Successful registration redirects the user to the login page (`/login`) with a success flash message.
- [ ] Registration errors are displayed as flash messages on the `register.html` page.
