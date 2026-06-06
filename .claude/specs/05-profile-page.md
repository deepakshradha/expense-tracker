# Spec: Profile Page

## Overview
The Profile Page allows authenticated users to view their account details and a summary of their spending. This is a key part of the user experience, providing a personalized space for the user to see their identity within the application and their overall financial footprint in Spendly.

## Depends on
- Step 3: Login (User must be authenticated)
- Step 4: Logout (User must be able to exit the session)

## Routes
- `GET /profile` — Displays the user's profile information and total spending summary — logged-in

## Database changes
No new tables or columns. 
A new helper function `get_user_by_id(user_id)` will be added to `database/db.py` to retrieve user records.
A new helper function `get_user_total_spending(user_id)` will be added to `database/db.py` to calculate the sum of all expenses for a user.

## Templates
- **Create:** `templates/profile.html` (extends `base.html`)
- **Modify:** None

## Files to change
- `app.py` (Implement `/profile` route logic)
- `database/db.py` (Add `get_user_by_id` and `get_user_total_spending`)

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Redirect unauthenticated users to the login page if they attempt to access `/profile`

## Definition of done
- [ ] Accessing `/profile` while logged out redirects to `/login`.
- [ ] Accessing `/profile` while logged in renders `profile.html`.
- [ ] The page displays the user's correct name and email address.
- [ ] The page displays the correct total sum of all expenses associated with the user.
- [ ] The layout is consistent with the rest of the app (extends `base.html`).
