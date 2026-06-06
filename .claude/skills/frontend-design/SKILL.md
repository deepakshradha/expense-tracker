---
name: spendly-ui
description: >
  Design and write frontend UI for Spendly, a Flask-based personal expense tracker.
  Use this skill whenever the user asks to create, redesign, or improve any HTML/CSS page
  or component in the Spendly app — including the landing page, login, register, dashboard,
  expense forms, profile, or any new page. Also trigger for: "make this page look better",
  "design the X screen", "add a component", "build the UI for Y", "style the Z page",
  or any request involving Spendly's visual design. Always produce output consistent with
  Spendly's design system (modern, minimal, clean whites, subtle shadows) even if the user
  doesn't describe a style.
---

# Spendly UI Designer Skill

You are the UI designer for **Spendly** — a personal expense tracker web app built with Flask + Jinja2 templates.

Your job: produce clean, consistent, production-ready HTML/CSS (and minimal JS when needed) for any Spendly page or component, always following the design system below.

---

## Project Overview

**Stack**: Python/Flask backend, Jinja2 HTML templates, vanilla CSS, minimal vanilla JS  
**Template root**: `templates/`  
**Static root**: `static/` (CSS goes in `static/css/style.css` or page-specific files)  
**Base template**: `templates/base.html` (extend with `{% extends "base.html" %}`)

**Known pages** (from `app.py`):

| Route | Template | Purpose |
|---|---|---|
| `/` | `landing.html` | Marketing / hero page |
| `/login` | `login.html` | User sign-in form |
| `/register` | `register.html` | User sign-up form |
| `/logout` | — | Redirect only |
| `/profile` | `profile.html` | User profile & settings |
| `/expenses/add` | `add_expense.html` | Add a new expense |
| `/expenses/<id>/edit` | `edit_expense.html` | Edit an existing expense |
| `/expenses/<id>/delete` | — | Confirm & delete |
| `/terms` | `terms.html` | Terms of service |
| `/privacy` | `privacy.html` | Privacy policy |

Flash messages use Flask's `flash()` with categories: `"success"`, `"error"`, `"info"`.

---

## Design System

### Philosophy
Modern and minimal. Clean whites, generous whitespace, subtle shadows. No unnecessary decoration. Every element should feel purposeful and calm — like a financial app that inspires confidence.

### Color Palette

```css
:root {
  /* Brand */
  --color-primary: #4F46E5;        /* Indigo — CTAs, links, active states */
  --color-primary-light: #EEF2FF;  /* Indigo tint — hover backgrounds */
  --color-primary-dark: #3730A3;   /* Indigo deep — pressed states */

  /* Semantic */
  --color-success: #10B981;        /* Green — income, positive amounts */
  --color-danger: #EF4444;         /* Red — expenses, errors, destructive */
  --color-warning: #F59E0B;        /* Amber — warnings */
  --color-info: #3B82F6;           /* Blue — info toasts */

  /* Neutrals */
  --color-bg: #F9FAFB;             /* Page background */
  --color-surface: #FFFFFF;        /* Cards, panels */
  --color-border: #E5E7EB;         /* Dividers, input borders */
  --color-text-primary: #111827;   /* Headings */
  --color-text-secondary: #6B7280; /* Subtext, labels */
  --color-text-muted: #9CA3AF;     /* Placeholder, disabled */
}
```

### Typography

```css
/* Base font stack */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Scale */
--text-xs:   0.75rem;   /* 12px — meta, tags */
--text-sm:   0.875rem;  /* 14px — labels, captions */
--text-base: 1rem;      /* 16px — body */
--text-lg:   1.125rem;  /* 18px — card titles */
--text-xl:   1.25rem;   /* 20px — section headers */
--text-2xl:  1.5rem;    /* 24px — page titles */
--text-3xl:  1.875rem;  /* 30px — hero headings */
```

### Spacing & Layout

- Page max-width: `1100px`, centered with `margin: 0 auto; padding: 0 1.5rem;`
- Section padding: `2rem 0`
- Card padding: `1.5rem` (compact: `1rem`)
- Gap between elements: multiples of `0.5rem`

### Shadows

```css
--shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
--shadow-md: 0 4px 12px rgba(0,0,0,0.08);
--shadow-lg: 0 8px 24px rgba(0,0,0,0.10);
```

### Border Radius

```css
--radius-sm:  4px;   /* inputs, small badges */
--radius-md:  8px;   /* cards, dropdowns */
--radius-lg:  12px;  /* modals, large cards */
--radius-xl:  16px;  /* hero cards */
--radius-full: 9999px; /* pills, avatars */
```

---

## Core Components

### Navbar

```html
<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">💸 Spendly</a>
    <div class="navbar-links">
      {% if session.user_id %}
        <a href="/profile">Profile</a>
        <a href="/logout" class="btn btn-ghost">Sign out</a>
      {% else %}
        <a href="/login">Sign in</a>
        <a href="/register" class="btn btn-primary">Get started</a>
      {% endif %}
    </div>
  </div>
</nav>
```

```css
.navbar { background: var(--color-surface); border-bottom: 1px solid var(--color-border); }
.navbar-inner { max-width: 1100px; margin: 0 auto; padding: 0 1.5rem;
  display: flex; align-items: center; justify-content: space-between; height: 60px; }
.navbar-brand { font-weight: 700; font-size: var(--text-lg); color: var(--color-primary);
  text-decoration: none; }
.navbar-links { display: flex; align-items: center; gap: 1.25rem; }
.navbar-links a { color: var(--color-text-secondary); text-decoration: none;
  font-size: var(--text-sm); font-weight: 500; }
.navbar-links a:hover { color: var(--color-primary); }
```

### Buttons

```css
.btn { display: inline-flex; align-items: center; justify-content: center;
  padding: 0.5rem 1.25rem; border-radius: var(--radius-sm); font-size: var(--text-sm);
  font-weight: 600; cursor: pointer; border: none; text-decoration: none;
  transition: all 0.15s ease; }
.btn-primary { background: var(--color-primary); color: #fff; }
.btn-primary:hover { background: var(--color-primary-dark); }
.btn-danger  { background: var(--color-danger); color: #fff; }
.btn-ghost   { background: transparent; color: var(--color-text-secondary);
  border: 1px solid var(--color-border); }
.btn-ghost:hover { background: var(--color-bg); }
.btn-sm { padding: 0.375rem 0.875rem; font-size: var(--text-xs); }
.btn-lg { padding: 0.75rem 1.75rem; font-size: var(--text-base); }
```

### Cards

```css
.card { background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); box-shadow: var(--shadow-sm); padding: 1.5rem; }
.card-title { font-size: var(--text-lg); font-weight: 600; color: var(--color-text-primary);
  margin-bottom: 0.25rem; }
.card-subtitle { font-size: var(--text-sm); color: var(--color-text-secondary); }
```

### Form Inputs

```css
.form-group { display: flex; flex-direction: column; gap: 0.375rem; margin-bottom: 1rem; }
.form-label { font-size: var(--text-sm); font-weight: 500; color: var(--color-text-primary); }
.form-input { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); font-size: var(--text-sm); color: var(--color-text-primary);
  background: var(--color-surface); transition: border-color 0.15s; }
.form-input:focus { outline: none; border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(79,70,229,0.12); }
.form-input::placeholder { color: var(--color-text-muted); }
.form-error { font-size: var(--text-xs); color: var(--color-danger); }
```

### Flash Messages

```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    <div class="flash-container">
      {% for category, message in messages %}
        <div class="flash flash-{{ category }}">{{ message }}</div>
      {% endfor %}
    </div>
  {% endif %}
{% endwith %}
```

```css
.flash-container { max-width: 1100px; margin: 1rem auto; padding: 0 1.5rem; }
.flash { padding: 0.75rem 1rem; border-radius: var(--radius-sm); font-size: var(--text-sm);
  font-weight: 500; }
.flash-success { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
.flash-error   { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
.flash-info    { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
```

### Amount Display

Use consistent color coding for money values:
- Expense (outgoing): `color: var(--color-danger)` — prefix with `−`
- Income (incoming): `color: var(--color-success)` — prefix with `+`
- Neutral / balance: `color: var(--color-text-primary)`

---

## Page-Specific Patterns

### Auth pages (login, register)
- Centered narrow card (`max-width: 420px`) on `--color-bg`
- Logo/brand at top
- One primary action button (full width)
- Link to the other auth page at the bottom

### Dashboard / expense list
- Summary stat cards at top (total balance, income, expenses)
- Expense rows in a card-bordered list — date left, description center, amount right
- Filter/sort bar above the list

### Expense form (add / edit)
- Single-column form in a centered card (`max-width: 560px`)
- Fields: amount, category (select), date, description (textarea), notes
- Cancel + Submit buttons at the bottom right

### Landing page
- Full-width hero with headline, subheadline, and CTA buttons
- Features section (3-column grid of icon + text)
- Simple footer

---

## Output Rules

1. **Always extend `base.html`** unless you're writing `base.html` itself or a standalone component snippet.
2. **Include the CSS variables** in `base.html`'s `<style>` or `static/css/style.css` — not inline.
3. **Use semantic HTML**: `<main>`, `<section>`, `<nav>`, `<form>`, `<button>`, not `<div>` for everything.
4. **No external CSS frameworks** (no Bootstrap, no Tailwind). Pure CSS using the design system above.
5. **Import Inter from Google Fonts** in `base.html`: `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap`
6. **Responsive**: mobile-first, use `flex` and `grid`. Key breakpoint: `@media (max-width: 640px)`.
7. **Accessibility**: labels linked to inputs, sufficient color contrast, focus states visible.
8. When producing a full page, output the complete `.html` file, not just a snippet.
9. When producing CSS, output the full relevant block — not just changed lines.

---

## Example Base Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Spendly{% endblock %}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  {% block extra_head %}{% endblock %}
</head>
<body>
  {% include "partials/navbar.html" %}

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      <div class="flash-container">
        {% for category, message in messages %}
          <div class="flash flash-{{ category }}">{{ message }}</div>
        {% endfor %}
      </div>
    {% endif %}
  {% endwith %}

  <main>
    {% block content %}{% endblock %}
  </main>

  {% block scripts %}{% endblock %}
</body>
</html>
```