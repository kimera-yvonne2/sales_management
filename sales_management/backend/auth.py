"""Authentication for RISMS.

Passwords are stored as SHA-256 hashes. Only ACTIVE accounts can log in.
"""

from .db import get_connection


def authenticate(username, password):
    """Return a dict (user_id, username, role, employee_id, branch_id, full_name)
    when the credentials are valid, otherwise None."""
    username = (username or "").strip()
    if not username or not password:
        return None

    conn = get_connection()
    try:
        # Query directly rather than calling SP_LOGIN. This keeps login working
        # when the schema has been installed without stored routine privileges.
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT u.user_id, u.username, u.role, e.employee_id, e.branch_id, "
            "CONCAT(e.first_name, ' ', e.last_name) AS full_name "
            "FROM `USER` AS u "
            "JOIN EMPLOYEE AS e ON e.employee_id = u.employee_id "
            "WHERE u.username = %s AND u.password_hash = SHA2(%s, 256) "
            "AND u.status = 'Active'",
            (username, password),
        )
        user = cur.fetchone()
        cur.close()
        return user
    finally:
        conn.close()
