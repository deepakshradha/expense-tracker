# Spec: Login

## Overview
Implement the authentication flow to allow users to access their personal expense tracker. This involves verifying user credentials against the database and establishing a secure session using Flask's session management. This is a critical bridge between the public registration process and the private user experience.

## Depends on
- Step 02: Registration

## Routes
- `GET /login` — Renders the sign-in page — Public
- `POST /login` — Authenticates user credentials and starts session — Public

## Database changes
No database changes.

## Templates
- **Modify:** `templates/login.html` — Remove manual error block in favor of `base.html` flash messages.
- **Modify:** `templates/base.html` — Update the navigation links to show "Sign in" and "Get started" when logged out, and "My Profile" and "Logout" when logged in.

## Files to change
- `app.py` — Add POST handler for `/login` and session management.
- `database/db.py` — Add `get_user_by_email(email)` helper function.
- `templates/base.html` — Update navbar based on auth state.
- `templates/login.html` — Cleanup error handling.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (use `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use Flask `session` for tracking the logged-in user

## Definition of done
- [ ] User can access the login page at `/login`.
- [ ] User can successfully log in with a valid email and password.
- [ ] User is redirected to the landing page (or a protected page) with a success message upon login.
- [ ] User sees an error message when attempting to log in with a non-existent email.
- [ ] User sees an error message when attempting to log in with an incorrect password.
- [ ] Navbar updates to show "My Profile" and "Logout" after successful authentication.
- [ ] The `session` object correctly stores the `user_id` after login.
