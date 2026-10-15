import matplotlib.pyplot as plt
from backend.operations import get_connection

def generate_sales_chart():
    """Generates a graphical bar chart for best-selling products."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT p.product_name, SUM(si.quantity) as total_sold
                FROM SALE_ITEM si
                JOIN PRODUCT p ON si.product_id = p.product_id
                GROUP BY p.product_name
                ORDER BY total_sold DESC
                LIMIT 5;
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            products = [row['product_name'] for row in results]
            quantities = [row['total_sold'] for row in results]
            
            plt.figure(figsize=(8, 5))
            plt.bar(products, quantities, color='skyblue')
            plt.xlabel('Products')
            plt.ylabel('Quantity Sold')
            plt.title('Top 5 Best-Selling Products')
            plt.xticks(rotation=15)
            plt.tight_layout()
            plt.savefig('reports/top_selling_products.png')
            plt.close()
            print("Graphical report saved to reports/top_selling_products.png")
    finally:
        conn.close()