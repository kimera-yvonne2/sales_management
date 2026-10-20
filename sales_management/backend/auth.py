"""Authentication for RISMS.

Passwords are never stored in plain text: the database keeps a SHA-256 hash and
the stored procedure SP_LOGIN compares it with SHA2(<typed password>, 256).
Only ACTIVE accounts can log in.
"""

import warnings

from .db import get_connection


def authenticate(username, password):
    """Return a dict (user_id, username, role, employee_id, branch_id, full_name)
    when the credentials are valid, otherwise None."""
    username = (username or "").strip()
    if not username or not password:
        return None

    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        user = None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")      # connector deprecation notice for stored_results()
            cur.callproc("SP_LOGIN", (username, password))
            for result in cur.stored_results():
                user = result.fetchone()
        cur.close()
        return user
    finally:
        conn.close()