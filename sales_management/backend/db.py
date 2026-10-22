"""Database connection helpers for RISMS (MySQL).

Connection settings come from environment variables so that no password is
stored in the source code.  Defaults are shown below.

    RISMS_DB_HOST      localhost
    RISMS_DB_PORT      3306
    RISMS_DB_USER      root
    RISMS_DB_PASSWORD  kimerayvonne622
    RISMS_DB_NAME      sales_management_db
"""

import os
from contextlib import contextmanager

import mysql.connector

DB_CONFIG = {
    "host": os.getenv("RISMS_DB_HOST", "localhost"),
    "port": int(os.getenv("RISMS_DB_PORT", "3306")),
    "user": os.getenv("RISMS_DB_USER", "root"),
    "password": os.getenv("RISMS_DB_PASSWORD", "kimerayvonne622"),
    "database": os.getenv("RISMS_DB_NAME", "sales_management_db"),
}


def get_connection():
    """Open and return a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all(sql, params=None):
    """Run a SELECT and return all rows as a list of dictionaries."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


@contextmanager
def transaction():
    """Yield a cursor inside a transaction: commit on success, roll back on error."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
