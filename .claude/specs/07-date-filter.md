# Spec: Date Filter

## Overview
The Date Filter feature allows users to filter their expenses by a specific date range on the profile page. This improves the utility of the expense tracker by letting users analyze their spending over specific periods (e.g., last 30 days, specific month) rather than just seeing a total lifetime sum.

## Depends on
- 05-profile-page
- 06-redesign-profile-page

## Routes
No new routes. The existing `GET /profile` route will be modified to handle optional `start_date` and `end_date` query parameters.

## Database changes
No database changes. The existing `expenses` table has a `date` column that will be used for filtering.

## Templates
- **Modify:** `templates/profile.html` — Add a date filter form (start date and end date inputs) that submits to the same page via GET.

## Files to change
- `app.py` — Update the `/profile` route to retrieve query parameters and pass them to the database helper.
- `database/db.py` — Create a new helper function or update existing ones to support date range filtering.

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
- Use HTML5 date inputs (`type="date"`) for the filter form.
- Ensure the filter handles cases where only one date is provided or no dates are provided.

## Definition of done
- [ ] The profile page displays a date filter form with "Start Date" and "End Date" inputs.
- [ ] Selecting a date range and clicking "Filter" updates the total spending, category breakdown, and recent expenses list to only include items within that range.
- [ ] The "Clear Filter" button resets the date range and returns the view to the lifetime spending data.
- [ ] The app does not crash when invalid dates are provided.
- [ ] The date range is preserved in the URL (query parameters) so the page can be bookmarked or refreshed.
