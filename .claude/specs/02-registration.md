# Spec: Registration

## Overview
This feature implements the working `POST /register` flow for Spendly. The `GET /register` route already renders `register.html` with a form, but submitting it currently does nothing — there is no handler to validate input, hash the password, or persist the new user. This step wires that form up to the `users` table (created in Step 1) so a visitor can actually create an account and be showna  success message and then be sent to the login page. Session handling / login-after-register is out of scope and belongs to a later step.

## Depends on
- Step 1 — Database Setup (`database/db.py`: `get_db()`, `init_db()`, `users` table with `name`, `email`, `password_hash`). Already complete.

## Routes
- `POST /register` — validate submitted name/email/password, create the user, redirect to `GET /login` on success or re-render `register.html` with an error on failure — public
- `GET /register` — unchanged, already implemented

## Database changes
No database changes. The `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) already has every column this feature needs. `database/db.py` gains one new function:
- `create_user(name, email, password)` — hashes the password with `werkzeug.security.generate_password_hash` and inserts the row via a parameterized query; lets the caller handle the `sqlite3.IntegrityError` raised on duplicate `email`

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — change `<form method="POST" action="/register">` to use `action="{{ url_for('register') }}"` (currently hardcoded, violates CLAUDE.md rule); no structural/CSS changes needed, the `{% if error %}` block already exists for validation errors

## Files to change
- `app.py` — change `register()` to accept `GET` and `POST`; on `POST`, validate input, call `create_user()`, handle duplicate-email errors, redirect to `login` or re-render `register.html` with `error`
- `database/db.py` — add `create_user(name, email, password)`
- `templates/register.html` — fix hardcoded form action to use `url_for()`

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No new pip packages
- DB logic (the insert, the duplicate-email check) lives in `database/db.py`, never inline in `app.py`
- Server-side validation required even though the form has HTML5 `required`/`type=email` attributes: reject empty name, invalid email, and password under 8 characters
- Duplicate email must show a user-facing error on the re-rendered `register.html`, not a 500

## Definition of done
- [x] `GET /register` still renders the form (unchanged)
- [x] Submitting valid name/email/password on `/register` creates a row in `users` with a hashed (not plaintext) password
- [x] After successful registration, the browser is redirected to `/login`
- [x] Submitting with an email that already exists in `users` re-renders `register.html` with a visible error and does not create a duplicate row
- [x] Submitting with a password under 8 characters re-renders `register.html` with a visible error and does not create a user
- [x] Submitting with an empty name or malformed email re-renders `register.html` with a visible error and does not create a user
- [x] `templates/register.html` form posts via `url_for('register')`, not a hardcoded `/register` string
- [x] App starts and runs on port 5001 without errors
