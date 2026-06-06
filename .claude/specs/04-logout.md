# Spec: Logout

## Overview
The Logout feature allows authenticated users to terminate their session, effectively signing out of the application. This is a critical security and usability feature, ensuring that users can protect their account when using shared devices.

## Depends on
- Step 03: Login

## Routes
- `GET /logout` — Clears the user session and redirects to the landing page — Logged-in

## Database changes
No database changes.

## Templates
- **Modify:** `templates/base.html` — Add a logout link/button that appears only when the user is authenticated.

## Files to change
- `app.py`
- `templates/base.html`

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `session.pop('user_id', None)` or `session.clear()` to remove the user session.
- Redirect to `url_for('landing')` after logout.
- Flash a success message "You have been logged out successfully".

## Definition of done
- [ ] Visiting `/logout` when logged in clears the session and redirects to the landing page.
- [ ] A success flash message "You have been logged out successfully" is displayed after logout.
- [ ] The navigation bar in `templates/base.html` correctly toggles between "Login/Register" and "Logout" based on the session status.
