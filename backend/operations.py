from backend.db_config import get_connection

def fetch_all_branches():
    """Fetches all store branches from the database."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM BRANCH;")
            return cursor.fetchall()
    finally:
        conn.close()

def fetch_low_stock_products():
    """Display all products currently below their reorder level."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT p.product_name, b.branch_name, i.quantity_on_hand, p.reorder_level
                FROM INVENTORY i
                JOIN PRODUCT p ON i.product_id = p.product_id
                JOIN BRANCH b ON i.branch_id = b.branch_id
                WHERE i.quantity_on_hand <= p.reorder_level;
            """
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()

def get_best_selling_products():
    """Identify the best-selling products."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT p.product_name, SUM(si.quantity) AS total_quantity_sold 
                FROM SALE_ITEM si
                JOIN PRODUCT p ON si.product_id = p.product_id
                GROUP BY p.product_id, p.product_name
                ORDER BY total_quantity_sold DESC
                LIMIT 5;
            """
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()