"""Reporting module for generating text and graphical analytics."""

import os
import matplotlib.pyplot as plt
from backend.operations import fetch_low_stock_products, get_best_selling_products


def generate_text_low_stock_report(output_path="reports/low_stock_report.txt"):
    """Generates and saves a text report for products below reorder levels."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    products = fetch_low_stock_products()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("          LOW STOCK INVENTORY REPORT              \n")
        f.write("==================================================\n\n")
        
        if not products:
            f.write("Status: All stock levels are sufficient.\n")
        else:
            for item in products:
                f.write(f"Product: {item['product_name']}\n")
                f.write(f"Branch: {item['branch_name']}\n")
                f.write(f"Qty on Hand: {item['quantity_on_hand']} (Reorder Level: {item['reorder_level']})\n")
                f.write("-" * 40 + "\n")
                
    print(f"Text report successfully saved to {output_path}")


def generate_graphical_sales_chart(output_path="reports/best_sellers.png"):
    """Generates and saves a bar chart of best-selling products."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    results = get_best_selling_products()

    if not results:
        # Fallback dummy data if no sales exist yet
        products = ["Coca Cola", "Water", "USB Cable", "Flour", "Soap"]
        sales = [5, 10, 4, 8, 6]
    else:
        products = [item['product_name'] for item in results]
        sales = [item['total_quantity_sold'] for item in results]

    plt.figure(figsize=(8, 5))
    plt.bar(products, sales, color="#2a9d8f")
    plt.xlabel("Products", fontweight="bold")
    plt.ylabel("Total Quantity Sold", fontweight="bold")
    plt.title("Best-Selling Products Performance", fontweight="bold", fontsize=12)
    plt.xticks(rotation=15)
    plt.tight_layout()
    
    plt.savefig(output_path)
    plt.close()
    print(f"Graphical chart successfully saved to {output_path}")