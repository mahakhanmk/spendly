"""SQLite helpers for Spendly: get_db(), init_db(), seed_db()."""

import calendar
import sqlite3
from datetime import datetime
from pathlib import Path

from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
        if row["n"] > 0:
            return  # already seeded

        password_hash = generate_password_hash("demo123")
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cur.lastrowid

        today = datetime.now()
        year, month = today.year, today.month
        last_day = calendar.monthrange(year, month)[1]

        def month_date(day):
            return f"{year:04d}-{month:02d}-{min(day, last_day):02d}"

        sample_expenses = [
            (12.50, "Food",          month_date(2),  "Grocery run"),
            (8.75,  "Transport",     month_date(3),  "Bus pass top-up"),
            (65.00, "Bills",         month_date(5),  "Electricity bill"),
            (22.30, "Health",        month_date(7),  "Pharmacy"),
            (15.00, "Entertainment", month_date(10), "Cinema ticket"),
            (40.00, "Shopping",      month_date(14), "New shoes"),
            (9.99,  "Other",         month_date(18), "Miscellaneous purchase"),
            (33.60, "Food",          month_date(21), "Dinner out"),
        ]
        conn.executemany(
            """INSERT INTO expenses (user_id, amount, category, date, description)
               VALUES (?, ?, ?, ?, ?)""",
            [(user_id, amt, cat, dt, desc) for amt, cat, dt, desc in sample_expenses],
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def authenticate_user(email, password):
    user = get_user_by_email(email)
    if user is None:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def create_user(name, email, password):
    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
    finally:
        conn.close()
