"""Business operations for RISMS: lookups, validated data entry and transactions.

Every write runs inside one database transaction.  The database triggers do the
final validation (stock levels, overpayment, ...); their messages are raised to
the interface as OperationError.
"""

import re

import mysql.connector

from .db import fetch_all, transaction

PAYMENT_METHODS = ["Cash", "Mobile Money", "Card", "Bank Transfer"]
USER_ROLES = ["Administrator", "Manager", "Sales Employee", "Inventory Employee"]
EXPENSE_TYPES = ["Rent", "Utility", "Transport", "Maintenance", "Licence", "Salaries", "Other"]


class OperationError(Exception):
    """A readable error that the interface can show to the user."""


# ---------------------------------------------------------------- validation
def parse_positive_int(text, field="Value"):
    text = str(text).strip()
    if not text.isdigit() or int(text) <= 0:
        raise OperationError(f"{field} must be a whole number greater than 0.")
    return int(text)


def parse_money(text, field="Amount", allow_zero=False):
    cleaned = str(text).strip().replace(",", "")
    try:
        value = float(cleaned)
    except ValueError:
        raise OperationError(f"{field} must be a number.") from None
    if value < 0 or (value == 0 and not allow_zero):
        raise OperationError(f"{field} must be greater than 0.")
    return round(value, 2)


def _required(text, field):
    text = (text or "").strip()
    if not text:
        raise OperationError(f"{field} is required.")
    return text


def _optional_phone(text):
    text = (text or "").strip()
    if text and not re.fullmatch(r"[0-9+ ]{7,20}", text):
        raise OperationError("Phone must contain 7-20 digits (+ and spaces allowed).")
    return text or None


def _optional_email(text):
    text = (text or "").strip()
    if text and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", text):
        raise OperationError("Email address is not valid.")
    return text or None


def _db_error(exc):
    """Turn a MySQL error into a short readable message."""
    msg = getattr(exc, "msg", str(exc))
    if "Duplicate entry" in msg:
        if "USER.username" in msg:
            return "That username is already taken."
        if "USER.employee_id" in msg:
            return "That employee already has a login account."
        if "barcode" in msg:
            return "That barcode is already used by another product."
        return "That value already exists (duplicate entry)."
    if "foreign key constraint" in msg.lower():
        return "That record refers to something that does not exist or is still in use."
    if "Check constraint" in msg:
        return "A value breaks a data rule (for example a negative number or a price below cost)."
    return msg


# ------------------------------------------------------------------- lookups
def get_branches():
    return fetch_all("SELECT branch_id, branch_name, location FROM BRANCH ORDER BY branch_name")


def get_categories():
    return fetch_all("SELECT category_id, category_name FROM CATEGORY ORDER BY category_name")


def get_customers():
    return fetch_all("SELECT customer_id, customer_name, phone, email, address "
                     "FROM CUSTOMER ORDER BY customer_name")


def get_suppliers():
    return fetch_all("SELECT supplier_id, supplier_name, phone FROM SUPPLIER ORDER BY supplier_name")


def get_products():
    return fetch_all(
        "SELECT p.product_id, p.product_name, p.barcode, c.category_name, "
        "       p.cost_price, p.selling_price, p.reorder_level "
        "  FROM PRODUCT p JOIN CATEGORY c ON c.category_id = p.category_id "
        " ORDER BY p.product_name")


def get_employees():
    return fetch_all(
        "SELECT e.employee_id, CONCAT(e.first_name, ' ', e.last_name) AS full_name, "
        "       IFNULL(b.branch_name, 'All branches') AS branch_name "
        "  FROM EMPLOYEE e LEFT JOIN BRANCH b ON b.branch_id = e.branch_id "
        " ORDER BY e.first_name")


def get_users():
    return fetch_all(
        "SELECT u.user_id, u.username, u.role, u.status, "
        "       CONCAT(e.first_name, ' ', e.last_name) AS full_name "
        "  FROM USER u JOIN EMPLOYEE e ON e.employee_id = u.employee_id ORDER BY u.user_id")


def get_stock(branch_id=None):
    sql = ("SELECT b.branch_name, p.product_name, i.quantity_on_hand, p.reorder_level, "
           "       CASE WHEN i.quantity_on_hand <= p.reorder_level THEN 'LOW' ELSE 'OK' END AS status "
           "  FROM INVENTORY i JOIN BRANCH b ON b.branch_id = i.branch_id "
           "  JOIN PRODUCT p ON p.product_id = i.product_id ")
    params = ()
    if branch_id:
        sql += "WHERE i.branch_id = %s "
        params = (branch_id,)
    return fetch_all(sql + "ORDER BY b.branch_name, p.product_name", params)


def fetch_low_stock_products():
    """Products at or below their reorder level (used by the Low Stock tab and report)."""
    return fetch_all(
        "SELECT product_name, branch_name, quantity_on_hand, reorder_level "
        "  FROM V_LOW_STOCK ORDER BY branch_name, product_name")


def get_recent_expenses(limit=20):
    return fetch_all(
        "SELECT x.expense_id, b.branch_name, x.expense_type, x.amount, x.expense_date, x.description "
        "  FROM EXPENSE x JOIN BRANCH b ON b.branch_id = x.branch_id "
        " ORDER BY x.expense_date DESC, x.expense_id DESC LIMIT %s", (limit,))


# -------------------------------------------------------------- transactions
def record_sale(customer_id, branch_id, employee_id, items,
                payment_method="Cash", amount_paid=None, reference=None):
    """Record a sale with its items and (optionally) a payment.

    items        list of (product_id, quantity); prices are read from PRODUCT.
    amount_paid  None/0 means no payment yet (credit sale).
    Returns (sale_id, total_amount).
    """
    if not items:
        raise OperationError("A sale must contain at least one item.")
    if payment_method not in PAYMENT_METHODS:
        raise OperationError("Choose a valid payment method.")

    merged = {}                                   # one line per product
    for product_id, qty in items:
        merged[product_id] = merged.get(product_id, 0) + qty

    try:
        with transaction() as cur:
            cur.execute("INSERT INTO SALE (customer_id, branch_id, employee_id) VALUES (%s, %s, %s)",
                        (customer_id, branch_id, employee_id))
            sale_id = cur.lastrowid
            for product_id, qty in merged.items():
                cur.execute(
                    "INSERT INTO SALE_ITEM (sale_id, product_id, quantity, unit_price) "
                    "SELECT %s, product_id, %s, selling_price FROM PRODUCT WHERE product_id = %s",
                    (sale_id, qty, product_id))
                if cur.rowcount == 0:
                    raise OperationError(f"Product {product_id} does not exist.")
            cur.execute("SELECT total_amount FROM SALE WHERE sale_id = %s", (sale_id,))
            total = cur.fetchone()["total_amount"]
            if amount_paid:
                cur.execute(
                    "INSERT INTO PAYMENT (sale_id, payment_method, amount, reference) "
                    "VALUES (%s, %s, %s, %s)",
                    (sale_id, payment_method, amount_paid, reference or None))
        return sale_id, total
    except mysql.connector.Error as exc:
        raise OperationError(_db_error(exc)) from exc


def record_purchase(supplier_id, branch_id, employee_id, items):
    """Record a supplier purchase; the trigger adds the stock.

    items  list of (product_id, quantity, unit_cost).  Returns (purchase_id, total).
    """
    if not items:
        raise OperationError("A purchase must contain at least one item.")

    merged = {}
    for product_id, qty, cost in items:
        old_qty, _ = merged.get(product_id, (0, cost))
        merged[product_id] = (old_qty + qty, cost)

    try:
        with transaction() as cur:
            cur.execute("INSERT INTO PURCHASE (supplier_id, branch_id, employee_id) VALUES (%s, %s, %s)",
                        (supplier_id, branch_id, employee_id))
            purchase_id = cur.lastrowid
            for product_id, (qty, cost) in merged.items():
                cur.execute("INSERT INTO PURCHASE_ITEM (purchase_id, product_id, quantity, unit_cost) "
                            "VALUES (%s, %s, %s, %s)", (purchase_id, product_id, qty, cost))
            cur.execute("SELECT total_amount FROM PURCHASE WHERE purchase_id = %s", (purchase_id,))
            total = cur.fetchone()["total_amount"]
        return purchase_id, total
    except mysql.connector.Error as exc:
        raise OperationError(_db_error(exc)) from exc


def add_customer(name, phone="", email="", address=""):
    name = _required(name, "Customer name")
    phone, email = _optional_phone(phone), _optional_email(email)
    try:
        with transaction() as cur:
            cur.execute("INSERT INTO CUSTOMER (customer_name, phone, email, address) "
                        "VALUES (%s, %s, %s, %s)", (name, phone, email, (address or "").strip() or None))
            return cur.lastrowid
    except mysql.connector.Error as exc:
        raise OperationError(_db_error(exc)) from exc


def add_product(category_id, name, barcode, cost_price, selling_price, reorder_level):
    name = _required(name, "Product name")
    if selling_price < cost_price:
        raise OperationError("Selling price cannot be below the cost price.")
    try:
        with transaction() as cur:
            cur.execute(
                "INSERT INTO PRODUCT (category_id, product_name, barcode, cost_price, selling_price, "
                "reorder_level) VALUES (%s, %s, %s, %s, %s, %s)",
                (category_id, name, (barcode or "").strip() or None, cost_price, selling_price, reorder_level))
            return cur.lastrowid
    except mysql.connector.Error as exc:
        raise OperationError(_db_error(exc)) from exc


def add_expense(branch_id, employee_id, expense_type, amount, description=""):
    expense_type = _required(expense_type, "Expense type")
    try:
        with transaction() as cur:
            cur.execute(
                "INSERT INTO EXPENSE (branch_id, employee_id, expense_type, amount, expense_date, description) "
                "VALUES (%s, %s, %s, %s, CURDATE(), %s)",
                (branch_id, employee_id, expense_type, amount, (description or "").strip() or None))
            return cur.lastrowid
    except mysql.connector.Error as exc:
        raise OperationError(_db_error(exc)) from exc


def add_user(username, password, role, employee_id):
    username = _required(username, "Username")
    if len(password or "") < 6:
        raise OperationError("Password must be at least 6 characters.")
    if role not in USER_ROLES:
        raise OperationError("Choose a valid role.")
    try:
        with transaction() as cur:
            cur.execute(
                "INSERT INTO USER (username, password_hash, role, employee_id, status) "
                "VALUES (%s, SHA2(%s, 256), %s, %s, 'Active')", (username, password, role, employee_id))
            return cur.lastrowid
    except mysql.connector.Error as exc:
        raise OperationError(_db_error(exc)) from exc


def set_user_status(user_id, status):
    if status not in ("Active", "Inactive"):
        raise OperationError("Invalid status.")
    try:
        with transaction() as cur:
            cur.execute("UPDATE USER SET status = %s WHERE user_id = %s", (status, user_id))
    except mysql.connector.Error as exc:
        raise OperationError(_db_error(exc)) from exc