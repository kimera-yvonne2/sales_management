"""Report generation for RISMS: text insights and graphical charts.

Every generate_* function writes a file into the 'reports/' folder next to
main.py and returns the file path.
"""

import os
from datetime import datetime

import matplotlib

matplotlib.use("Agg")          # draw to files only; no window needed
import matplotlib.pyplot as plt  # noqa: E402  (must come after matplotlib.use)
import matplotlib.ticker  # noqa: E402

from .db import fetch_all  # noqa: E402

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
COLORS = {"primary": "#2a9d8f", "accent": "#e76f51", "dark": "#2b2d42"}


# ------------------------------------------------------------------ helpers
def _path(filename):
    os.makedirs(REPORT_DIR, exist_ok=True)
    return os.path.join(REPORT_DIR, filename)


def _money(value):
    return f"UGX {float(value or 0):,.0f}"


def _write_text(filename, title, body_lines):
    path = _path(filename)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [title.upper(), f"Generated: {stamp}", "=" * 64, ""] + body_lines
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def _table(rows, columns):
    """Format rows (list of dicts) as an aligned text table. columns = [(key, heading)]."""
    if not rows:
        return ["(no records)"]
    data = [[str(r[k]) if r[k] is not None else "" for k, _ in columns] for r in rows]
    widths = [max(len(h), *(len(row[i]) for row in data)) for i, (_, h) in enumerate(columns)]
    out = ["  ".join(h.ljust(w) for (_, h), w in zip(columns, widths)),
           "  ".join("-" * w for w in widths)]
    out += ["  ".join(cell.ljust(w) for cell, w in zip(row, widths)) for row in data]
    return out


def _empty_chart(title, filename):
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=100)
    ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=14)
    ax.set_title(title)
    ax.axis("off")
    path = _path(filename)
    fig.savefig(path)
    plt.close(fig)
    return path


# -------------------------------------------------------------- text reports
def generate_text_low_stock_report():
    """Text report of products at or below their reorder level, with insights."""
    rows = fetch_all("SELECT branch_name, product_name, quantity_on_hand, reorder_level "
                     "FROM V_LOW_STOCK ORDER BY branch_name, product_name")
    body = _table(rows, [("branch_name", "Branch"), ("product_name", "Product"),
                         ("quantity_on_hand", "On hand"), ("reorder_level", "Reorder level")])
    body += ["", "INSIGHTS", "-" * 64]
    if not rows:
        body.append("All products are above their reorder levels. No restocking is needed.")
    else:
        body.append(f"{len(rows)} product line(s) need restocking.")
        worst = min(rows, key=lambda r: r["quantity_on_hand"] / max(r["reorder_level"], 1))
        body.append(f"Most urgent: {worst['product_name']} at {worst['branch_name']} "
                    f"({worst['quantity_on_hand']} left, reorder level {worst['reorder_level']}).")
        per_branch = {}
        for r in rows:
            per_branch[r["branch_name"]] = per_branch.get(r["branch_name"], 0) + 1
        top = max(per_branch, key=per_branch.get)
        body.append(f"Branch with most low-stock lines: {top} ({per_branch[top]}).")
    return _write_text("low_stock_report.txt", "Low Stock Report", body)


def generate_text_sales_summary():
    """Text summary of sales, payments, expenses and outstanding balances, with insights."""
    totals = fetch_all("SELECT COUNT(*) AS n, IFNULL(SUM(total_amount),0) AS revenue, "
                       "IFNULL(AVG(total_amount),0) AS average FROM SALE")[0]
    top_products = fetch_all("SELECT product_name, units_sold, revenue FROM V_BEST_SELLERS "
                             "ORDER BY units_sold DESC LIMIT 5")
    staff = fetch_all("SELECT employee_name, num_sales, total_sales FROM V_SALES_BY_EMPLOYEE "
                      "WHERE num_sales > 0 ORDER BY total_sales DESC")
    methods = fetch_all("SELECT payment_method, COUNT(*) AS payments, SUM(amount) AS received "
                        "FROM PAYMENT GROUP BY payment_method ORDER BY received DESC")
    owed = fetch_all("SELECT IFNULL(SUM(balance),0) AS owed, COUNT(*) AS n "
                     "FROM V_SALE_BALANCE WHERE balance > 0")[0]
    expenses = fetch_all("SELECT IFNULL(SUM(amount),0) AS total FROM EXPENSE")[0]["total"]
    purchases = fetch_all("SELECT IFNULL(SUM(total_amount),0) AS total FROM PURCHASE")[0]["total"]

    body = ["OVERVIEW", "-" * 64,
            f"Number of sales      : {totals['n']}",
            f"Total sales revenue  : {_money(totals['revenue'])}",
            f"Average sale value   : {_money(totals['average'])}",
            f"Total purchases      : {_money(purchases)}",
            f"Total expenses       : {_money(expenses)}",
            f"Outstanding balances : {_money(owed['owed'])} on {owed['n']} sale(s)",
            "", "TOP SELLING PRODUCTS", "-" * 64]
    body += _table(top_products, [("product_name", "Product"), ("units_sold", "Units"), ("revenue", "Revenue")])
    body += ["", "SALES BY EMPLOYEE", "-" * 64]
    body += _table(staff, [("employee_name", "Employee"), ("num_sales", "Sales"), ("total_sales", "Total")])
    body += ["", "PAYMENTS BY METHOD", "-" * 64]
    body += _table(methods, [("payment_method", "Method"), ("payments", "Payments"), ("received", "Received")])

    body += ["", "INSIGHTS", "-" * 64]
    if totals["n"] == 0:
        body.append("No sales have been recorded yet.")
    else:
        body.append(f"Best seller by units: {top_products[0]['product_name']} "
                    f"({top_products[0]['units_sold']} units).")
        if staff:
            body.append(f"Top performer: {staff[0]['employee_name']} with {_money(staff[0]['total_sales'])}.")
        if methods:
            body.append(f"Most used payment method by value: {methods[0]['payment_method']}.")
        body.append(f"Revenue minus expenses: {_money(float(totals['revenue']) - float(expenses))} "
                    f"(before the cost of stock bought).")
        if owed["n"]:
            body.append(f"Follow up {owed['n']} unpaid/part-paid sale(s) worth {_money(owed['owed'])}.")
    return _write_text("sales_summary_report.txt", "Sales Summary Report", body)


# ------------------------------------------------------------ graphical reports
def generate_graphical_sales_chart():
    """Bar chart of total sales per day."""
    rows = fetch_all("SELECT sale_day, total_sales FROM V_DAILY_SALES ORDER BY sale_day")
    if not rows:
        return _empty_chart("Daily Sales", "daily_sales_chart.png")
    days = [str(r["sale_day"]) for r in rows]
    values = [float(r["total_sales"]) for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=100)
    ax.bar(days, values, color=COLORS["primary"])
    ax.set_title("Daily Sales (UGX)", color=COLORS["dark"], fontweight="bold")
    ax.set_ylabel("Total sales (UGX)")
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    path = _path("daily_sales_chart.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def generate_best_sellers_chart():
    """Horizontal bar chart of the best-selling products by units."""
    rows = fetch_all("SELECT product_name, units_sold FROM V_BEST_SELLERS "
                     "ORDER BY units_sold DESC LIMIT 8")
    if not rows:
        return _empty_chart("Best Selling Products", "best_sellers_chart.png")
    rows.reverse()                                   # largest bar on top
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=100)
    ax.barh([r["product_name"] for r in rows], [int(r["units_sold"]) for r in rows],
            color=COLORS["accent"])
    ax.set_title("Best Selling Products (units sold)", color=COLORS["dark"], fontweight="bold")
    ax.set_xlabel("Units sold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    path = _path("best_sellers_chart.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def generate_inventory_value_chart():
    """Grouped bars: stock value at cost and at retail price for each branch."""
    rows = fetch_all("SELECT branch_name, cost_value, retail_value FROM V_INVENTORY_VALUE "
                     "ORDER BY branch_name")
    if not rows:
        return _empty_chart("Inventory Value", "inventory_value_chart.png")
    names = [r["branch_name"] for r in rows]
    cost = [float(r["cost_value"]) for r in rows]
    retail = [float(r["retail_value"]) for r in rows]
    x = range(len(names))

    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=100)
    ax.bar([i - 0.2 for i in x], cost, width=0.4, label="At cost", color=COLORS["dark"])
    ax.bar([i + 0.2 for i in x], retail, width=0.4, label="At selling price", color=COLORS["primary"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_title("Inventory Value by Branch (UGX)", color=COLORS["dark"], fontweight="bold")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    path = _path("inventory_value_chart.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def generate_all_reports():
    """Generate every report and return {name: path}."""
    return {
        "low_stock": generate_text_low_stock_report(),
        "sales_summary": generate_text_sales_summary(),
        "daily_sales_chart": generate_graphical_sales_chart(),
        "best_sellers_chart": generate_best_sellers_chart(),
        "inventory_value_chart": generate_inventory_value_chart(),
    }