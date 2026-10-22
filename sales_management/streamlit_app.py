
"""Streamlit dashboard for the Retail Inventory and Sales Management System."""

from datetime import date
from pathlib import Path
import re

import pandas as pd
import streamlit as st

from backend import operations as ops
from backend import reports
from backend.db import fetch_all
from backend.db import transaction
from backend.operations import OperationError


st.set_page_config(
    page_title="RISMS | Retail Operations",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .stApp { background: #263f61; }
      [data-testid="stAppViewContainer"] { background: #263f61; }
      [data-testid="stMain"] { background: #263f61; color: #dce7f5; }
      [data-testid="stSidebar"] { background: #111c35; }
      [data-testid="stSidebar"] * { color: #e8eefb; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .45rem .2rem; }
      h1, h2, h3 { font-family: 'Manrope', sans-serif; color: #dce7f5; }
      .hero { padding: 1.35rem 1.6rem; border-radius: 18px; color: white;
        background: linear-gradient(115deg, #172747 0%, #245b72 58%, #2b9b8f 100%);
        margin: .2rem 0 1.2rem 0; box-shadow: 0 12px 28px #1b35551c; }
      .hero h1 { color: white; margin: 0; font-size: 2rem; }
      .hero p { color: #d5e5ee; margin: .3rem 0 0 0; }
      div[data-testid="stMetric"] { background: white; padding: 1rem 1.1rem;
        border: 1px solid #e8edf4; border-radius: 14px; box-shadow: 0 4px 14px #1b35550a; }
      div[data-testid="stMetricLabel"] { color: #7c8da4; }
      div[data-testid="stMetricValue"] { color: #4b627d; font-family: 'Manrope', sans-serif; }
      div.stButton > button, div[data-testid="stFormSubmitButton"] button {
        border-radius: 9px; font-weight: 600; min-height: 2.65rem; }
      div[data-testid="stDataFrame"] { border: 1px solid #e8edf4; border-radius: 12px; overflow: hidden; }
      [data-testid="stCaptionContainer"] { color: #bac9dc; }
      .caption { color: #bac9dc; }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value):
    return f"UGX {float(value or 0):,.0f}"


def frame(rows):
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def notify_error(exc):
    if isinstance(exc, OperationError):
        st.error(str(exc))
    else:
        st.error(f"Database operation failed: {exc}")


def choices(rows, id_key, label_key, prefix=None):
    result = {}
    for row in rows:
        label = str(row[label_key])
        if prefix:
            label = f"{row[prefix]} · {label}"
        result[label] = row[id_key]
    return result


def load_shell():
    st.sidebar.markdown("<div style='font-size:1.55rem;font-weight:800;color:white'>RISMS</div>",
                        unsafe_allow_html=True)
    st.sidebar.caption("RETAIL OPERATIONS")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "WORKSPACE",
        ["Overview", "Tables", "Queries", "Form designs", "Reports", "Data dictionary", "ERD"],
        label_visibility="visible",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Connected to the configured MySQL database")
    return page


def page_erd():
    hero("Entity relationship diagram", "How the 14 database tables connect to each other.")
    dot = r'''digraph RISMS {
      graph [rankdir=LR, bgcolor="transparent", pad="0.25", nodesep="0.45", ranksep="0.8",
             fontname="Helvetica", label="Retail Inventory & Sales Management System", labelloc="t", fontsize=20];
      node [shape=box, style="rounded,filled", fillcolor="#eef6f7", color="#2b9b8f",
            fontname="Helvetica", fontsize=11, margin="0.18,0.12"];
      edge [color="#72839b", fontname="Helvetica", fontsize=9, arrowsize=0.7];
      BRANCH -> EMPLOYEE [label="1 : many"];
      EMPLOYEE -> USER [label="1 : 0..1"];
      CATEGORY -> PRODUCT [label="1 : many"];
      SUPPLIER -> PURCHASE [label="1 : many"];
      BRANCH -> PURCHASE [label="1 : many"];
      EMPLOYEE -> PURCHASE [label="1 : many"];
      PURCHASE -> PURCHASE_ITEM [label="1 : many"];
      PRODUCT -> PURCHASE_ITEM [label="1 : many"];
      BRANCH -> INVENTORY [label="1 : many"];
      PRODUCT -> INVENTORY [label="1 : many"];
      CUSTOMER -> SALE [label="0..1 : many"];
      BRANCH -> SALE [label="1 : many"];
      EMPLOYEE -> SALE [label="1 : many"];
      SALE -> SALE_ITEM [label="1 : many"];
      PRODUCT -> SALE_ITEM [label="1 : many"];
      SALE -> PAYMENT [label="1 : many"];
      BRANCH -> EXPENSE [label="1 : many"];
      EMPLOYEE -> EXPENSE [label="1 : many"];
    }'''
    st.graphviz_chart(dot, use_container_width=True)
    st.caption("PURCHASE_ITEM and SALE_ITEM connect products to their purchase and sale records. INVENTORY tracks product quantities per branch.")


def page_dictionary():
    hero("Data dictionary", "Fields and constraints parsed from the active schema definition.")
    schema_path = Path(__file__).with_name("database").joinpath("schema.sql")
    schema = schema_path.read_text(encoding="utf-8")
    descriptions = {
        "BRANCH": "Retail locations.", "EMPLOYEE": "Staff assigned to a branch.",
        "USER": "Application user accounts and role assignments.", "CATEGORY": "Product categories.",
        "PRODUCT": "Product catalogue, prices, and reorder settings.", "SUPPLIER": "Product suppliers.",
        "CUSTOMER": "Customer contact records.", "PURCHASE": "Supplier deliveries received at a branch.",
        "PURCHASE_ITEM": "Product lines belonging to purchases.",
        "INVENTORY": "Current product quantities per branch.", "SALE": "Customer transactions.",
        "SALE_ITEM": "Product lines belonging to sales.", "PAYMENT": "Payments applied to sales.",
        "EXPENSE": "Operating expenses recorded by branch.",
    }
    definitions = re.findall(r"CREATE TABLE\s+(\w+)\s*\((.*?)\n\) ENGINE", schema, flags=re.I | re.S)
    for table_name, body in definitions:
        field_rows = []
        for line in body.splitlines():
            raw = re.sub(r"\s+--.*$", "", line.strip()).rstrip(",")
            match = re.match(r"([A-Za-z_]\w*)\s+(.+)$", raw)
            if not match or match.group(1).upper() in {"CONSTRAINT", "PRIMARY", "UNIQUE", "INDEX", "KEY"}:
                continue
            name, definition = match.groups()
            data_type = definition.strip().split()[0]
            flags = []
            if "PRIMARY KEY" in definition.upper():
                flags.append("Primary key")
            if "AUTO_INCREMENT" in definition.upper():
                flags.append("Auto increment")
            if "NOT NULL" in definition.upper():
                flags.append("Required")
            if "UNIQUE" in definition.upper():
                flags.append("Unique")
            if "DEFAULT" in definition.upper():
                flags.append("Default value")
            field_rows.append({"Field": name, "Type": data_type, "Rules": ", ".join(flags) or "Nullable"})
        with st.expander(f"{table_name} · {descriptions.get(table_name, '')}"):
            st.dataframe(frame(field_rows), hide_index=True, use_container_width=True)


def hero(title, subtitle):
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def page_overview():
    hero("Good business starts with a clear view.", "Your sales, stock, and daily operations at a glance.")
    totals = fetch_all(
        "SELECT (SELECT COUNT(*) FROM PRODUCT) AS products, "
        "(SELECT COUNT(*) FROM CUSTOMER) AS customers, "
        "(SELECT COUNT(*) FROM SALE WHERE DATE(sale_date)=CURDATE()) AS today_sales, "
        "(SELECT IFNULL(SUM(total_amount),0) FROM SALE WHERE DATE(sale_date)=CURDATE()) AS today_revenue, "
        "(SELECT COUNT(*) FROM V_LOW_STOCK) AS low_stock"
    )[0]
    cols = st.columns(5)
    cols[0].metric("Products", f"{totals['products']:,}")
    cols[1].metric("Customers", f"{totals['customers']:,}")
    cols[2].metric("Sales today", f"{totals['today_sales']:,}")
    cols[3].metric("Today's revenue", money(totals["today_revenue"]))
    cols[4].metric("Low stock alerts", f"{totals['low_stock']:,}",
                   delta="Needs attention" if totals["low_stock"] else "All clear",
                   delta_color="inverse" if totals["low_stock"] else "normal")
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Sales trend")
        trend = fetch_all("SELECT DATE(sale_date) AS day, SUM(total_amount) AS revenue "
                          "FROM SALE WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 13 DAY) "
                          "GROUP BY DATE(sale_date) ORDER BY day")
        st.line_chart(frame(trend).set_index("day") if trend else pd.DataFrame(), height=300,
                      color="#258f88")
    with right:
        st.subheader("Stock needing attention")
        low = ops.fetch_low_stock_products()
        if low:
            st.dataframe(frame(low), hide_index=True, use_container_width=True, height=300)
        else:
            st.success("All products are above their reorder levels.")
    st.subheader("Recent sales")
    recent = fetch_all(
        "SELECT s.sale_id AS Sale, s.sale_date AS Date, b.branch_name AS Branch, "
        "CONCAT(e.first_name,' ',e.last_name) AS Employee, s.total_amount AS Total "
        "FROM SALE s JOIN BRANCH b ON b.branch_id=s.branch_id "
        "JOIN EMPLOYEE e ON e.employee_id=s.employee_id "
        "ORDER BY s.sale_date DESC LIMIT 10"
    )
    st.dataframe(frame(recent), hide_index=True, use_container_width=True)


def page_sales():
    hero("Sales", "Record a sale and keep branch stock in sync.")
    branches = choices(ops.get_branches(), "branch_id", "branch_name")
    employees = choices(ops.get_employees(), "employee_id", "full_name")
    customers = {"Walk-in customer": None, **choices(ops.get_customers(), "customer_id", "customer_name")}
    products = ops.get_products()
    product_options = {f"{p['product_name']} · {money(p['selling_price'])}": p for p in products}
    product_labels = list(product_options)
    with st.form("sale_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        branch = c1.selectbox("Branch", list(branches))
        employee = c2.selectbox("Handled by", list(employees))
        customer = c3.selectbox("Customer", list(customers))
        st.markdown("**Items in this sale**")
        default_items = pd.DataFrame([{"Product": product_labels[0], "Quantity": 1}]) if product_labels else pd.DataFrame(
            columns=["Product", "Quantity"])
        items = st.data_editor(
            default_items, num_rows="dynamic", hide_index=True, use_container_width=True,
            column_config={
                "Product": st.column_config.SelectboxColumn("Product", options=product_labels, required=True),
                "Quantity": st.column_config.NumberColumn("Quantity", min_value=1, step=1, required=True),
            }, key="sale_items_editor",
        )
        c3, c4 = st.columns(2)
        method = c3.selectbox("Payment method", ops.PAYMENT_METHODS)
        paid = c4.number_input("Amount paid (UGX)", min_value=0.0, step=1000.0)
        reference = st.text_input("Payment reference (optional)")
        submitted = st.form_submit_button("Complete sale", type="primary", use_container_width=True)
    if submitted:
        try:
            line_items = [
                (product_options[row["Product"]]["product_id"], int(row["Quantity"]))
                for _, row in items.iterrows()
                if row.get("Product") in product_options and pd.notna(row.get("Quantity"))
            ]
            sale_id, total = ops.record_sale(
                customers[customer], branches[branch], employees[employee],
                line_items, method, paid or None, reference,
            )
            st.success(f"Sale #{sale_id} recorded · Total {money(total)}")
        except Exception as exc:
            notify_error(exc)
    st.subheader("Recent sales")
    rows = fetch_all("SELECT s.sale_id AS Sale, s.sale_date AS Date, c.customer_name AS Customer, "
                     "b.branch_name AS Branch, s.total_amount AS Total "
                     "FROM SALE s LEFT JOIN CUSTOMER c ON c.customer_id=s.customer_id "
                     "JOIN BRANCH b ON b.branch_id=s.branch_id ORDER BY s.sale_date DESC LIMIT 100")
    st.dataframe(frame(rows), hide_index=True, use_container_width=True)


def page_purchases():
    hero("Purchases", "Receive goods from suppliers and update inventory.")
    suppliers = choices(ops.get_suppliers(), "supplier_id", "supplier_name")
    branches = choices(ops.get_branches(), "branch_id", "branch_name")
    employees = choices(ops.get_employees(), "employee_id", "full_name")
    products = ops.get_products()
    product_options = {p["product_name"]: p for p in products}
    product_names = list(product_options)
    with st.form("purchase_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        supplier = c1.selectbox("Supplier", list(suppliers))
        branch = c2.selectbox("Receiving branch", list(branches))
        employee = c3.selectbox("Received by", list(employees))
        st.markdown("**Items in this purchase**")
        default_items = (pd.DataFrame([{"Product": product_names[0], "Quantity": 1,
                                        "Unit cost (UGX)": float(products[0]["cost_price"])}])
                         if product_names else pd.DataFrame(columns=["Product", "Quantity", "Unit cost (UGX)"]))
        items = st.data_editor(
            default_items, num_rows="dynamic", hide_index=True, use_container_width=True,
            column_config={
                "Product": st.column_config.SelectboxColumn("Product", options=product_names, required=True),
                "Quantity": st.column_config.NumberColumn("Quantity", min_value=1, step=1, required=True),
                "Unit cost (UGX)": st.column_config.NumberColumn("Unit cost (UGX)", min_value=0, step=500),
            }, key="purchase_items_editor",
        )
        submitted = st.form_submit_button("Save purchase", type="primary", use_container_width=True)
    if submitted:
        try:
            line_items = [
                (product_options[row["Product"]]["product_id"], int(row["Quantity"]), float(row["Unit cost (UGX)"]))
                for _, row in items.iterrows()
                if row.get("Product") in product_options and pd.notna(row.get("Quantity"))
                and pd.notna(row.get("Unit cost (UGX)"))
            ]
            purchase_id, total = ops.record_purchase(
                suppliers[supplier], branches[branch], employees[employee],
                line_items,
            )
            st.success(f"Purchase #{purchase_id} saved · Total {money(total)}")
        except Exception as exc:
            notify_error(exc)


def page_inventory():
    hero("Inventory", "On-hand quantities and reorder signals across your branches.")
    branch_rows = ops.get_branches()
    branch_map = {"All branches": None, **choices(branch_rows, "branch_id", "branch_name")}
    selected = st.selectbox("Branch", list(branch_map))
    rows = ops.get_stock(branch_map[selected])
    if rows:
        low_count = sum(1 for row in rows if row["status"] == "LOW")
        c1, c2, c3 = st.columns(3)
        c1.metric("Product lines", len(rows))
        c2.metric("Units on hand", f"{sum(int(row['quantity_on_hand']) for row in rows):,}")
        c3.metric("Below reorder level", low_count)
    st.dataframe(frame(rows), hide_index=True, use_container_width=True, height=520)
    with st.expander("Low stock only"):
        st.dataframe(frame(ops.fetch_low_stock_products()), hide_index=True, use_container_width=True)


def page_customers():
    hero("Customers", "Keep customer details ready for their next visit.")
    with st.expander("Add a customer", expanded=True):
        with st.form("customer_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Customer name *")
            phone = c2.text_input("Phone")
            email = c1.text_input("Email")
            address = c2.text_input("Address")
            submitted = st.form_submit_button("Save customer", type="primary")
        if submitted:
            try:
                customer_id = ops.add_customer(name, phone, email, address)
                st.success(f"Customer #{customer_id} added.")
            except Exception as exc:
                notify_error(exc)
    st.subheader("Customer directory")
    st.dataframe(frame(ops.get_customers()), hide_index=True, use_container_width=True)


def page_expenses():
    hero("Expenses", "Capture operating costs and review recent spending.")
    branches = choices(ops.get_branches(), "branch_id", "branch_name")
    employees = choices(ops.get_employees(), "employee_id", "full_name")
    with st.form("expense_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        branch = c1.selectbox("Branch", list(branches))
        employee = c2.selectbox("Recorded by", list(employees))
        kind = c3.selectbox("Expense type", ops.EXPENSE_TYPES)
        amount = st.number_input("Amount (UGX)", min_value=0.0, step=1000.0)
        description = st.text_input("Description")
        submitted = st.form_submit_button("Save expense", type="primary")
    if submitted:
        try:
            ops.add_expense(branches[branch], employees[employee], kind, amount, description)
            st.success("Expense recorded.")
        except Exception as exc:
            notify_error(exc)
    st.subheader("Recent expenses")
    rows = ops.get_recent_expenses(100)
    st.dataframe(frame(rows), hide_index=True, use_container_width=True)


def page_products():
    hero("Products", "Product catalogue, prices, and reorder settings.")
    with st.expander("Add a product"):
        categories = choices(ops.get_categories(), "category_id", "category_name")
        with st.form("product_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            category = c1.selectbox("Category", list(categories))
            name = c2.text_input("Product name")
            barcode = c1.text_input("Barcode (optional)")
            reorder = c2.number_input("Reorder level", min_value=0, step=1)
            cost = c1.number_input("Cost price (UGX)", min_value=0.0, step=500.0)
            price = c2.number_input("Selling price (UGX)", min_value=0.0, step=500.0)
            submitted = st.form_submit_button("Add product", type="primary")
        if submitted:
            try:
                product_id = ops.add_product(categories[category], name, barcode, cost, price, int(reorder))
                st.success(f"Product #{product_id} added.")
            except Exception as exc:
                notify_error(exc)
    st.subheader("Catalogue")
    products = ops.get_products()
    st.dataframe(frame(products), hide_index=True, use_container_width=True)


def page_users():
    hero("Users", "Manage the accounts stored in the database.")
    with st.expander("Create a user account"):
        employees = ops.get_employees()
        employee_options = choices(employees, "employee_id", "full_name", prefix="employee_id")
        with st.form("user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            username = c1.text_input("Username")
            password = c2.text_input("Password", type="password")
            role = c1.selectbox("Role", ops.USER_ROLES)
            employee = c2.selectbox("Employee", list(employee_options))
            submitted = st.form_submit_button("Create account", type="primary")
        if submitted:
            try:
                ops.add_user(username, password, role, employee_options[employee])
                st.success("User account created.")
            except Exception as exc:
                notify_error(exc)
    users = ops.get_users()
    st.dataframe(frame(users), hide_index=True, use_container_width=True)
    if users:
        by_name = {f"{u['username']} · {u['full_name']} · {u['status']}": u for u in users}
        selected = st.selectbox("Account to activate/deactivate", list(by_name))
        if st.button("Toggle account status"):
            user = by_name[selected]
            try:
                new_status = "Inactive" if user["status"] == "Active" else "Active"
                ops.set_user_status(user["user_id"], new_status)
                st.success(f"{user['username']} is now {new_status.lower()}.")
                st.rerun()
            except Exception as exc:
                notify_error(exc)


TABLES = [
    "BRANCH", "EMPLOYEE", "USER", "CATEGORY", "PRODUCT", "SUPPLIER", "CUSTOMER",
    "PURCHASE", "PURCHASE_ITEM", "INVENTORY", "SALE", "SALE_ITEM", "PAYMENT", "EXPENSE",
]


def page_database():
    hero("Tables", "Browse database records or open an operational workspace.")
    workspaces = {
        "Browse all 14 tables": None,
        "Sales": page_sales,
        "Purchases": page_purchases,
        "Inventory": page_inventory,
        "Customers": page_customers,
        "Expenses": page_expenses,
        "Products": page_products,
        "Users": page_users,
    }
    selected_workspace = st.selectbox("Tables workspace", list(workspaces))
    if workspaces[selected_workspace]:
        workspaces[selected_workspace]()
        return
    table_name = st.selectbox("Choose a table", TABLES)
    limit = st.selectbox("Rows to show", [100, 500, 1000, 5000], index=2)
    rows = fetch_all(f"SELECT * FROM `{table_name}` LIMIT %s", (limit,))
    st.caption(f"Showing {len(rows):,} row(s) from {table_name} · maximum {limit:,} per view")
    if rows:
        data = frame(rows)
        st.dataframe(data, hide_index=True, use_container_width=True, height=560)
        st.download_button(
            f"Download {table_name} as CSV",
            data=data.to_csv(index=False).encode("utf-8"),
            file_name=f"{table_name.lower()}.csv",
            mime="text/csv",
        )
    else:
        st.info("This table has no records yet.")


QUERY_CATALOG = {
    "Q1 · Low stock by branch": """SELECT p.product_name, b.branch_name, i.quantity_on_hand, p.reorder_level
FROM INVENTORY i JOIN PRODUCT p ON i.product_id=p.product_id
JOIN BRANCH b ON i.branch_id=b.branch_id
WHERE i.quantity_on_hand <= p.reorder_level ORDER BY b.branch_name, p.product_name""",
    "Q2 · Sales total for March 2026": """SELECT IFNULL(SUM(total_amount),0) AS total_sales, COUNT(sale_id) AS total_transactions
FROM SALE WHERE sale_date BETWEEN '2026-03-01 00:00:00' AND '2026-03-31 23:59:59'""",
    "Q2 · Daily sales": "SELECT * FROM V_DAILY_SALES ORDER BY sale_day",
    "Q2 · Weekly sales": "SELECT YEARWEEK(sale_date,1) AS year_week, SUM(total_amount) AS total_sales FROM SALE GROUP BY YEARWEEK(sale_date,1) ORDER BY year_week",
    "Q2 · Monthly sales": "SELECT DATE_FORMAT(sale_date,'%Y-%m') AS month, SUM(total_amount) AS total_sales FROM SALE GROUP BY DATE_FORMAT(sale_date,'%Y-%m') ORDER BY month",
    "Q3 · Products supplied by supplier 1": """SELECT DISTINCT p.product_name, c.category_name, sup.supplier_name
FROM PURCHASE_ITEM pi JOIN PURCHASE pur ON pi.purchase_id=pur.purchase_id
JOIN PRODUCT p ON pi.product_id=p.product_id JOIN CATEGORY c ON p.category_id=c.category_id
JOIN SUPPLIER sup ON pur.supplier_id=sup.supplier_id WHERE sup.supplier_id=1""",
    "Q4 · Sales by employee": """SELECT e.employee_id, CONCAT(e.first_name,' ',e.last_name) AS employee_name,
COUNT(s.sale_id) AS total_sales_made, IFNULL(SUM(s.total_amount),0) AS total_revenue
FROM EMPLOYEE e LEFT JOIN SALE s ON e.employee_id=s.employee_id
GROUP BY e.employee_id, employee_name ORDER BY total_revenue DESC""",
    "Q5 · Inventory value at branch 1": """SELECT b.branch_name, SUM(i.quantity_on_hand*p.cost_price) AS total_inventory_cost_value,
SUM(i.quantity_on_hand*p.selling_price) AS total_inventory_retail_value
FROM INVENTORY i JOIN PRODUCT p ON i.product_id=p.product_id JOIN BRANCH b ON i.branch_id=b.branch_id
WHERE i.branch_id=1 GROUP BY b.branch_name""",
    "Q6 · Best-selling products": """SELECT p.product_name, SUM(si.quantity) AS total_quantity_sold, SUM(si.subtotal) AS total_revenue
FROM SALE_ITEM si JOIN PRODUCT p ON si.product_id=p.product_id
GROUP BY p.product_id,p.product_name ORDER BY total_quantity_sold DESC LIMIT 5""",
    "Q7 · Purchase history for supplier 1": """SELECT pur.purchase_id,sup.supplier_name,b.branch_name,pur.purchase_date,pur.total_amount
FROM PURCHASE pur JOIN SUPPLIER sup ON pur.supplier_id=sup.supplier_id
JOIN BRANCH b ON pur.branch_id=b.branch_id WHERE sup.supplier_id=1 ORDER BY pur.purchase_date""",
    "Q8 · Sales history for customer 1": """SELECT s.sale_id,c.customer_name,s.sale_date,s.total_amount,b.branch_name
FROM SALE s JOIN CUSTOMER c ON s.customer_id=c.customer_id JOIN BRANCH b ON s.branch_id=b.branch_id
WHERE c.customer_id=1 ORDER BY s.sale_date""",
    "Q9 · Expenses by type": """SELECT expense_type,SUM(amount) AS total_expense_amount FROM EXPENSE
WHERE expense_date BETWEEN '2026-02-01' AND '2026-03-31'
GROUP BY expense_type ORDER BY total_expense_amount DESC""",
    "C1 · Detailed sale lines": """SELECT s.sale_id,s.sale_date,b.branch_name,CONCAT(e.first_name,' ',e.last_name) AS cashier,
IFNULL(c.customer_name,'Walk-in') AS customer,p.product_name,si.quantity,si.unit_price,si.subtotal
FROM SALE s JOIN SALE_ITEM si ON si.sale_id=s.sale_id JOIN PRODUCT p ON p.product_id=si.product_id
JOIN BRANCH b ON b.branch_id=s.branch_id JOIN EMPLOYEE e ON e.employee_id=s.employee_id
LEFT JOIN CUSTOMER c ON c.customer_id=s.customer_id ORDER BY s.sale_id,p.product_name""",
    "C2 · Outstanding balances": """SELECT sb.sale_id,IFNULL(c.customer_name,'Walk-in') AS customer,
sb.total_amount,sb.paid,sb.balance FROM V_SALE_BALANCE sb
LEFT JOIN CUSTOMER c ON c.customer_id=sb.customer_id WHERE sb.balance>0""",
    "C3 · Gross profit by product": """SELECT p.product_name,SUM(si.quantity) AS units_sold,SUM(si.subtotal) AS revenue,
SUM(si.quantity*p.cost_price) AS cost_of_goods,SUM(si.subtotal-si.quantity*p.cost_price) AS gross_profit
FROM SALE_ITEM si JOIN PRODUCT p ON p.product_id=si.product_id
GROUP BY p.product_name ORDER BY gross_profit DESC""",
    "C4 · Revenue versus expenses by branch": """SELECT b.branch_name,
IFNULL((SELECT SUM(total_amount) FROM SALE WHERE branch_id=b.branch_id),0) AS revenue,
IFNULL((SELECT SUM(amount) FROM EXPENSE WHERE branch_id=b.branch_id),0) AS expenses FROM BRANCH b""",
    "C5 · Payments by method": "SELECT payment_method,COUNT(*) AS payments,SUM(amount) AS total_received FROM PAYMENT GROUP BY payment_method",
    "C6 · Revenue by category": """SELECT c.category_name,SUM(si.subtotal) AS revenue
FROM SALE_ITEM si JOIN PRODUCT p ON p.product_id=si.product_id
JOIN CATEGORY c ON c.category_id=p.category_id GROUP BY c.category_name ORDER BY revenue DESC""",
    "C7 · Stock by branch and product": """SELECT b.branch_name,p.product_name,i.quantity_on_hand,p.reorder_level
FROM INVENTORY i JOIN BRANCH b ON b.branch_id=i.branch_id JOIN PRODUCT p ON p.product_id=i.product_id
ORDER BY b.branch_name,p.product_name""",
    "C8 · Inventory value view": "SELECT * FROM V_INVENTORY_VALUE",
    "C8 · Sales by employee view": "SELECT * FROM V_SALES_BY_EMPLOYEE ORDER BY total_sales DESC",
}


def page_queries():
    hero("Query library", "Run the proposal queries and management reports against live data.")
    selected = st.selectbox("Saved query", list(QUERY_CATALOG))
    st.code(QUERY_CATALOG[selected], language="sql")
    if st.button("Run query", type="primary"):
        try:
            rows = fetch_all(QUERY_CATALOG[selected])
            st.success(f"Query returned {len(rows):,} row(s).")
            st.dataframe(frame(rows), hide_index=True, use_container_width=True, height=500)
            if rows:
                st.download_button("Download query results", frame(rows).to_csv(index=False).encode("utf-8"),
                                   file_name="query_results.csv", mime="text/csv")
        except Exception as exc:
            notify_error(exc)
    with st.expander("Full queries.sql script, including write and constraint examples"):
        script = Path(__file__).with_name("database").joinpath("queries.sql").read_text(encoding="utf-8")
        st.code(script, language="sql", line_numbers=True)


def page_forms():
    hero("Database forms", "Add master records and take additional customer payments.")
    st.info("Inventory quantities and purchase/sale line-item tables update automatically from the transaction forms.")
    branch_tab, employee_tab, category_tab, supplier_tab, payment_tab = st.tabs(
        ["Branch", "Employee", "Category", "Supplier", "Payment"]
    )
    with branch_tab:
        with st.form("branch_form", clear_on_submit=True):
            name = st.text_input("Branch name")
            location = st.text_input("Location")
            phone = st.text_input("Phone")
            submitted = st.form_submit_button("Add branch", type="primary")
        if submitted:
            try:
                with transaction() as cur:
                    cur.execute("INSERT INTO BRANCH (branch_name,location,phone) VALUES (%s,%s,%s)",
                                (name.strip(), location.strip(), phone.strip() or None))
                st.success("Branch added.")
            except Exception as exc:
                notify_error(exc)
        st.dataframe(frame(ops.get_branches()), hide_index=True, use_container_width=True)
    with employee_tab:
        branches = choices(ops.get_branches(), "branch_id", "branch_name")
        with st.form("employee_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            first = c1.text_input("First name")
            last = c2.text_input("Last name")
            phone = c1.text_input("Phone")
            email = c2.text_input("Email")
            branch_label = st.selectbox("Branch assignment", ["No branch (system level)", *branches])
            hire_date = st.date_input("Hire date", value=date.today())
            submitted = st.form_submit_button("Add employee", type="primary")
        if submitted:
            try:
                branch_id = branches.get(branch_label)
                with transaction() as cur:
                    cur.execute("INSERT INTO EMPLOYEE (first_name,last_name,phone,email,branch_id,hire_date) "
                                "VALUES (%s,%s,%s,%s,%s,%s)",
                                (first.strip(), last.strip(), phone.strip() or None, email.strip() or None,
                                 branch_id, hire_date))
                st.success("Employee added.")
            except Exception as exc:
                notify_error(exc)
        st.dataframe(frame(ops.get_employees()), hide_index=True, use_container_width=True)
    with category_tab:
        with st.form("category_form", clear_on_submit=True):
            name = st.text_input("Category name")
            description = st.text_area("Description")
            submitted = st.form_submit_button("Add category", type="primary")
        if submitted:
            try:
                with transaction() as cur:
                    cur.execute("INSERT INTO CATEGORY (category_name,description) VALUES (%s,%s)",
                                (name.strip(), description.strip() or None))
                st.success("Category added.")
            except Exception as exc:
                notify_error(exc)
        st.dataframe(frame(ops.get_categories()), hide_index=True, use_container_width=True)
    with supplier_tab:
        with st.form("supplier_form", clear_on_submit=True):
            name = st.text_input("Supplier name")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_area("Address")
            submitted = st.form_submit_button("Add supplier", type="primary")
        if submitted:
            try:
                with transaction() as cur:
                    cur.execute("INSERT INTO SUPPLIER (supplier_name,phone,email,address) VALUES (%s,%s,%s,%s)",
                                (name.strip(), phone.strip() or None, email.strip() or None, address.strip() or None))
                st.success("Supplier added.")
            except Exception as exc:
                notify_error(exc)
        st.dataframe(frame(ops.get_suppliers()), hide_index=True, use_container_width=True)
    with payment_tab:
        sales = fetch_all("SELECT sale_id,total_amount FROM SALE ORDER BY sale_id DESC")
        sale_options = {f"Sale #{s['sale_id']} · {money(s['total_amount'])}": s["sale_id"] for s in sales}
        if sale_options:
            with st.form("payment_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                sale = c1.selectbox("Sale", list(sale_options))
                method = c2.selectbox("Payment method", ops.PAYMENT_METHODS)
                amount = c3.number_input("Amount (UGX)", min_value=0.0, step=1000.0)
                reference = st.text_input("Reference")
                submitted = st.form_submit_button("Record payment", type="primary")
            if submitted:
                try:
                    with transaction() as cur:
                        cur.execute("INSERT INTO PAYMENT (sale_id,payment_method,amount,reference) "
                                    "VALUES (%s,%s,%s,%s)",
                                    (sale_options[sale], method, amount, reference.strip() or None))
                    st.success("Payment recorded.")
                except Exception as exc:
                    notify_error(exc)
        else:
            st.info("Record a sale before adding a payment.")
        payments = fetch_all("SELECT payment_id,sale_id,payment_method,amount,payment_date,reference "
                             "FROM PAYMENT ORDER BY payment_date DESC LIMIT 100")
        st.dataframe(frame(payments), hide_index=True, use_container_width=True)


def page_reports():
    hero("Reports", "Explore performance and inventory signals visually.")
    sales = fetch_all("SELECT DATE(sale_date) AS day, SUM(total_amount) AS revenue "
                      "FROM SALE GROUP BY DATE(sale_date) ORDER BY day")
    products = fetch_all("SELECT product_name, units_sold FROM V_BEST_SELLERS "
                         "ORDER BY units_sold DESC LIMIT 10")
    stock_value = fetch_all("SELECT branch_name, cost_value, retail_value FROM V_INVENTORY_VALUE "
                            "ORDER BY branch_name")
    left, right = st.columns(2)
    with left:
        st.subheader("Daily sales revenue")
        st.bar_chart(frame(sales).set_index("day") if sales else pd.DataFrame(), color="#258f88")
    with right:
        st.subheader("Best sellers · units")
        st.bar_chart(frame(products).set_index("product_name") if products else pd.DataFrame(),
                     color="#e58a57")
    st.subheader("Inventory value by branch")
    st.bar_chart(frame(stock_value).set_index("branch_name") if stock_value else pd.DataFrame())
    st.subheader("Sales and payments summary")
    balances = fetch_all("SELECT COUNT(*) AS sales, IFNULL(SUM(total_amount),0) AS revenue "
                         "FROM SALE")[0]
    payment = fetch_all("SELECT IFNULL(SUM(amount),0) AS received FROM PAYMENT")[0]
    owed = fetch_all("SELECT IFNULL(SUM(balance),0) AS outstanding FROM V_SALE_BALANCE")[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("All-time sales", f"{balances['sales']:,}")
    c2.metric("Revenue", money(balances["revenue"]))
    c3.metric("Outstanding", money(owed["outstanding"]))
    st.caption(f"Payments received: {money(payment['received'])} · Refreshed {date.today():%d %b %Y}")
    st.divider()
    st.subheader("Saved report pack")
    st.caption("Generate the project's two text reports and three chart reports from the live database.")
    if st.button("Generate all five reports", type="primary"):
        try:
            paths = reports.generate_all_reports()
            st.success("All five reports generated.")
            for key, title in [("sales_summary", "Sales summary"), ("low_stock", "Low stock report")]:
                st.markdown(f"**{title}**")
                st.code(Path(paths[key]).read_text(encoding="utf-8"), language="text")
            chart_columns = st.columns(3)
            for col, key, title in zip(
                chart_columns,
                ["daily_sales_chart", "best_sellers_chart", "inventory_value_chart"],
                ["Daily sales", "Best sellers", "Inventory value"],
            ):
                with col:
                    st.markdown(f"**{title}**")
                    st.image(paths[key], use_container_width=True)
        except Exception as exc:
            notify_error(exc)


def main():
    try:
        page = load_shell()
        pages = {
            "Overview": page_overview,
            "Tables": page_database,
            "Queries": page_queries,
            "Form designs": page_forms,
            "Reports": page_reports,
            "Data dictionary": page_dictionary,
            "ERD": page_erd,
        }
        pages[page]()
    except Exception as exc:  # Keep connection/setup errors visible in the app.
        st.error(f"Could not load this page: {exc}")
        st.info("Check that MySQL is running, the schema and seed data are installed, and RISMS_DB_* settings are correct.")


if __name__ == "__main__":
    main()
