# Spec: Login and Logout

## Overview
This feature implements the working `POST /login` flow and the real `GET /logout` route for Spendly. `GET /login` already renders `login.html`, but submitting the form does nothing — there is no handler to verify credentials or start a session. `GET /logout` is currently a stub string response. This step wires both up using Flask's built-in signed-cookie session: a successful login stores the user's identity in the session, and logout clears it. This is the first feature to introduce an authenticated state, so `base.html`'s nav also needs to reflect whether a visitor is signed in.

## Depends on
- Step 1 — Database Setup (`database/db.py`: `get_db()`, `init_db()`, `users` table). Already complete.
- Step 2 — Registration (`create_user()`, `get_user_by_email()` in `database/db.py`; users can already be created with hashed passwords). Already complete.

## Routes
- `POST /login` — validate submitted email/password against the `users` table, start a session on success, redirect to landing page; re-render `login.html` with an error on failure — public
- `GET /login` — unchanged, already implemented
- `GET /logout` — clear the session, flash a confirmation message, redirect to `GET /login` — logged-in (safe to hit while logged out too; it just no-ops the session clear)

## Database changes
No database changes. The `users` table already has everything needed (`email`, `password_hash`). `database/db.py` gains one new function:
- `authenticate_user(email, password)` — looks up the user by email via `get_user_by_email()`, verifies the password with `werkzeug.security.check_password_hash`, and returns the user row on success or `None` on failure (bad email or bad password treated identically, no distinction leaked to caller)

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change `<form method="POST" action="/login">` to use `action="{{ url_for('login') }}"` (currently hardcoded, violates CLAUDE.md rule); reuse the existing `{% if error %}` block for invalid-credential errors
  - `templates/base.html` — nav links become conditional on session state: when logged in, show the user's name / a "Logout" link (`url_for('logout')`) instead of "Sign in" / "Get started"

## Files to change
- `app.py` — change `login()` to accept `GET` and `POST`; on `POST`, call `authenticate_user()`, set `session["user_id"]` and `session["user_name"]` on success and redirect to `landing`, or re-render `login.html` with `error` on failure; implement `logout()` to call `session.clear()`, flash a message, and redirect to `login`
- `database/db.py` — add `authenticate_user(email, password)`
- `templates/login.html` — fix hardcoded form action to use `url_for()`
- `templates/base.html` — conditional nav based on `session`

## Files to create
None.

## New dependencies
No new dependencies. Flask's built-in `session` (backed by `app.secret_key`, already set in `app.py`) covers this — no server-side session store needed.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash` / `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No new pip packages
- DB logic (the lookup, the hash check) lives in `database/db.py`, never inline in `app.py`
- Do not reveal whether a failed login was due to an unknown email or a wrong password — always show one generic error
- `GET /logout` must not error when hit by a visitor who isn't logged in — `session.clear()` is a safe no-op in that case

## Definition of done
- [x] `GET /login` still renders the form (unchanged)
- [x] Submitting valid email/password on `/login` starts a session and redirects to the landing page
- [x] Submitting an unknown email or a wrong password re-renders `login.html` with a single generic error and does not start a session
- [x] After a successful login, `base.html`'s nav no longer shows "Sign in" / "Get started" and instead shows a way to sign out
- [x] Visiting `/logout` while logged in clears the session and redirects to `/login` with a flashed confirmation
- [x] Visiting `/logout` while logged out does not raise an error and redirects to `/login`
- [x] `templates/login.html` form posts via `url_for('login')`, not a hardcoded `/login` string
- [x] App starts and runs on port 5001 without errors
