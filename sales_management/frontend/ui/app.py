"""User Interface module for the Sales Management System (RISMS).

Flow:  Open directly to the main window with all application tabs.
All data entry is validated here first, then validated again by the backend and
by the database (constraints and triggers).
"""

import tkinter as tk
from tkinter import messagebox, ttk

from backend import operations as ops
from backend import reports
from backend.operations import OperationError

BG = "#f4f6f9"
DARK = "#2b2d42"
GREEN = "#2a9d8f"
ORANGE = "#e76f51"
GREY = "#6c757d"

# Which tabs each role can see (matches the user roles in the proposal)
ROLE_TABS = {
    "Administrator": ["sale", "purchase", "customers", "expenses", "stock", "lowstock", "reports", "users"],
    "Manager": ["stock", "lowstock", "expenses", "reports"],
    "Sales Employee": ["sale", "customers", "stock"],
    "Inventory Employee": ["purchase", "stock", "lowstock"],
}
TAB_TITLES = {
    "sale": "Record Sale", "purchase": "Record Purchase", "customers": "Customers",
    "expenses": "Expenses", "stock": "Stock Levels", "lowstock": "Low Stock Alert",
    "reports": "Reports", "users": "Users",
}


def money(value):
    return f"{float(value or 0):,.0f}"


def combo_id(text):
    """'3 - Brian Opio' -> 3"""
    return int(text.split(" - ", 1)[0])


class SalesManagementApp:
    """Main application class for the Sales Management GUI."""

    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Retail Inventory & Sales Management System")
        self.root.geometry("980x700")
        self.root.minsize(900, 640)
        self.root.config(bg=BG)

        # Local single-user mode: skip application login and show all tabs.
        self.user = {
            "user_id": 0,
            "username": "local",
            "role": "Administrator",
            "employee_id": None,
            "branch_id": None,
            "full_name": "Local database access",
        }
        self.refreshers = []          # functions that reload lists after data changes
        self.notebook = None
        self.show_main_window()

    # ================================================================ helpers
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.refreshers = []

    def refresh_all(self):
        for func in self.refreshers:
            func()

    def new_tab(self, key):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text=TAB_TITLES[key])
        return frame

    @staticmethod
    def make_tree(parent, columns, height=8):
        """columns: list of (key, heading, width, anchor)."""
        holder = ttk.Frame(parent)
        tree = ttk.Treeview(holder, columns=[c[0] for c in columns], show="headings", height=height)
        for key, heading, width, anchor in columns:
            tree.heading(key, text=heading)
            tree.column(key, width=width, minwidth=width, stretch=False, anchor=anchor)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(holder, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll.set, xscrollcommand=xscroll.set)
        xscroll.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return holder, tree

    @staticmethod
    def fill_tree(tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

    def error(self, message, title="Validation Error"):
        messagebox.showerror(title, message)

    def branch_combo(self, parent, row):
        """Branch selector. Employees with a branch are locked to it; admins can choose."""
        ttk.Label(parent, text="Branch:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        values = [f"{b['branch_id']} - {b['branch_name']}" for b in ops.get_branches()]
        combo = ttk.Combobox(parent, values=values, state="readonly", width=42)
        own = self.user.get("branch_id")
        if own:
            for value in values:
                if value.startswith(f"{own} - "):
                    combo.set(value)
            combo.config(state="disabled")
        elif values:
            combo.current(0)
        combo.grid(row=row, column=1, sticky="w", pady=5)
        return combo

    # ============================================================ main window
    def show_main_window(self):
        self.clear_window()
        header = tk.Frame(self.root, bg=DARK)
        header.pack(fill="x")
        tk.Label(header, text="Retail Sales & Inventory Management", font=("Arial", 14, "bold"),
                 bg=DARK, fg="white").pack(side="left", padx=15, pady=10)
        tk.Button(header, text="Exit", bg=ORANGE, fg="white", command=self.root.destroy
                  ).pack(side="right", padx=15)
        tk.Label(header, text=f"{self.user['full_name']}  |  {self.user['role']}",
                 bg=DARK, fg="#d8dee9").pack(side="right", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)
        for key in ROLE_TABS[self.user["role"]]:
            getattr(self, f"build_{key}_tab")()

    # ================================================================ SALE TAB
    def build_sale_tab(self):
        tab = self.new_tab("sale")
        self.sale_cart = []                           # [{id, name, qty, price}]
        ttk.Label(tab, text="New Customer Transaction", font=("Arial", 12, "bold")).pack(anchor="w")

        form = ttk.Frame(tab)
        form.pack(fill="x", pady=6)
        self.sale_branch = self.branch_combo(form, 0)

        ttk.Label(form, text="Customer:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.sale_customer = ttk.Combobox(form, state="readonly", width=42)
        self.sale_customer.grid(row=1, column=1, sticky="w")

        ttk.Label(form, text="Product:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.sale_product = ttk.Combobox(form, state="readonly", width=42)
        self.sale_product.grid(row=2, column=1, sticky="w")

        ttk.Label(form, text="Quantity:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.sale_qty = ttk.Entry(form, width=10)
        self.sale_qty.insert(0, "1")
        self.sale_qty.grid(row=3, column=1, sticky="w")
        tk.Button(form, text="Add to Cart", bg=GREEN, fg="white", command=self.add_to_sale_cart
                  ).grid(row=3, column=1, sticky="e")

        holder, self.sale_tree = self.make_tree(tab, [
            ("product", "Product", 330, "w"), ("qty", "Qty", 70, "center"),
            ("price", "Unit Price", 110, "e"), ("subtotal", "Subtotal", 120, "e")], height=6)
        holder.pack(fill="both", expand=True, pady=6)

        bar = ttk.Frame(tab)
        bar.pack(fill="x")
        tk.Button(bar, text="Remove Selected", command=self.remove_from_sale_cart).pack(side="left")
        self.sale_total_label = ttk.Label(bar, text="Total: UGX 0", font=("Arial", 12, "bold"))
        self.sale_total_label.pack(side="right")

        pay = ttk.Frame(tab)
        pay.pack(fill="x", pady=8)
        ttk.Label(pay, text="Payment method:").grid(row=0, column=0, padx=5)
        self.sale_method = ttk.Combobox(pay, values=ops.PAYMENT_METHODS, state="readonly", width=16)
        self.sale_method.current(0)
        self.sale_method.grid(row=0, column=1)
        ttk.Label(pay, text="Amount paid (blank = full):").grid(row=0, column=2, padx=8)
        self.sale_paid = ttk.Entry(pay, width=14)
        self.sale_paid.grid(row=0, column=3)
        ttk.Label(pay, text="Reference:").grid(row=0, column=4, padx=8)
        self.sale_ref = ttk.Entry(pay, width=16)
        self.sale_ref.grid(row=0, column=5)

        tk.Button(tab, text="Complete Sale", bg=GREEN, fg="white", font=("Arial", 11, "bold"),
                  padx=12, pady=4, command=self.submit_sale_action).pack(pady=6)

        self.refreshers.append(self.reload_sale_lists)
        self.reload_sale_lists()

    def reload_sale_lists(self):
        customers = ops.get_customers()
        self.sale_customer["values"] = ["0 - Walk-in (no customer record)"] + \
            [f"{c['customer_id']} - {c['customer_name']}" for c in customers]
        if not self.sale_customer.get():
            self.sale_customer.current(0)
        self.sale_products = {p["product_id"]: p for p in ops.get_products()}
        self.sale_product["values"] = [f"{p['product_id']} - {p['product_name']}  (UGX {money(p['selling_price'])})"
                                       for p in self.sale_products.values()]
        if self.sale_product["values"] and not self.sale_product.get():
            self.sale_product.current(0)

    def add_to_sale_cart(self):
        if not self.sale_product.get():
            self.error("Choose a product.")
            return
        try:
            qty = ops.parse_positive_int(self.sale_qty.get(), "Quantity")
        except OperationError as exc:
            self.error(str(exc))
            return
        product = self.sale_products[combo_id(self.sale_product.get())]
        for line in self.sale_cart:
            if line["id"] == product["product_id"]:
                line["qty"] += qty
                break
        else:
            self.sale_cart.append({"id": product["product_id"], "name": product["product_name"],
                                   "qty": qty, "price": float(product["selling_price"])})
        self.sale_qty.delete(0, tk.END)
        self.sale_qty.insert(0, "1")
        self.refresh_sale_cart()

    def remove_from_sale_cart(self):
        selected = self.sale_tree.selection()
        if not selected:
            return
        index = self.sale_tree.index(selected[0])
        del self.sale_cart[index]
        self.refresh_sale_cart()

    def refresh_sale_cart(self):
        self.fill_tree(self.sale_tree, [(l["name"], l["qty"], money(l["price"]), money(l["qty"] * l["price"]))
                                        for l in self.sale_cart])
        total = sum(l["qty"] * l["price"] for l in self.sale_cart)
        self.sale_total_label.config(text=f"Total: UGX {money(total)}")

    def submit_sale_action(self):
        """Validate the form, then save the sale, its items and the payment."""
        if not self.sale_cart:
            self.error("Add at least one product to the cart.")
            return
        total = sum(l["qty"] * l["price"] for l in self.sale_cart)
        try:
            paid_text = self.sale_paid.get().strip()
            paid = total if not paid_text else ops.parse_money(paid_text, "Amount paid", allow_zero=True)
            if paid > total:
                raise OperationError("Amount paid cannot be more than the sale total.")
            customer_id = combo_id(self.sale_customer.get()) or None
            sale_id, saved_total = ops.record_sale(
                customer_id, combo_id(self.sale_branch.get()), self.user["employee_id"],
                [(l["id"], l["qty"]) for l in self.sale_cart],
                self.sale_method.get(), paid, self.sale_ref.get().strip() or None)
        except OperationError as exc:
            self.error(str(exc), "Sale Not Saved")
            return
        except Exception as exc:                      # pylint: disable=broad-except
            self.error(str(exc), "Database Error")
            return

        balance = float(saved_total) - paid
        note = f"\nBalance owed: UGX {money(balance)}" if balance > 0 else ""
        messagebox.showinfo("Success", f"Sale #{sale_id} recorded.\nTotal: UGX {money(saved_total)}{note}")
        self.sale_cart.clear()
        self.sale_paid.delete(0, tk.END)
        self.sale_ref.delete(0, tk.END)
        self.refresh_sale_cart()
        self.refresh_all()

    # ============================================================ PURCHASE TAB
    def build_purchase_tab(self):
        tab = self.new_tab("purchase")
        self.purchase_cart = []                       # [{id, name, qty, cost}]
        ttk.Label(tab, text="Restock From Supplier", font=("Arial", 12, "bold")).pack(anchor="w")

        form = ttk.Frame(tab)
        form.pack(fill="x", pady=6)
        self.purchase_branch = self.branch_combo(form, 0)

        ttk.Label(form, text="Supplier:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.purchase_supplier = ttk.Combobox(form, state="readonly", width=42)
        self.purchase_supplier.grid(row=1, column=1, sticky="w")

        ttk.Label(form, text="Product:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.purchase_product = ttk.Combobox(form, state="readonly", width=42)
        self.purchase_product.grid(row=2, column=1, sticky="w")
        self.purchase_product.bind("<<ComboboxSelected>>", self.fill_default_cost)

        ttk.Label(form, text="Quantity:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.purchase_qty = ttk.Entry(form, width=10)
        self.purchase_qty.grid(row=3, column=1, sticky="w")
        ttk.Label(form, text="Unit cost (UGX):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.purchase_cost = ttk.Entry(form, width=14)
        self.purchase_cost.grid(row=4, column=1, sticky="w")
        tk.Button(form, text="Add Item", bg=GREEN, fg="white", command=self.add_to_purchase_cart
                  ).grid(row=4, column=1, sticky="e")

        holder, self.purchase_tree = self.make_tree(tab, [
            ("product", "Product", 330, "w"), ("qty", "Qty", 70, "center"),
            ("cost", "Unit Cost", 110, "e"), ("subtotal", "Subtotal", 120, "e")], height=6)
        holder.pack(fill="both", expand=True, pady=6)

        bar = ttk.Frame(tab)
        bar.pack(fill="x")
        tk.Button(bar, text="Remove Selected", command=self.remove_from_purchase_cart).pack(side="left")
        self.purchase_total_label = ttk.Label(bar, text="Total: UGX 0", font=("Arial", 12, "bold"))
        self.purchase_total_label.pack(side="right")

        tk.Button(tab, text="Save Purchase", bg=GREEN, fg="white", font=("Arial", 11, "bold"),
                  padx=12, pady=4, command=self.submit_purchase_action).pack(pady=10)

        self.refreshers.append(self.reload_purchase_lists)
        self.reload_purchase_lists()

    def reload_purchase_lists(self):
        self.purchase_suppliers = ops.get_suppliers()
        self.purchase_supplier["values"] = [f"{s['supplier_id']} - {s['supplier_name']}"
                                            for s in self.purchase_suppliers]
        if self.purchase_supplier["values"] and not self.purchase_supplier.get():
            self.purchase_supplier.current(0)
        self.purchase_products = {p["product_id"]: p for p in ops.get_products()}
        self.purchase_product["values"] = [f"{p['product_id']} - {p['product_name']}"
                                           for p in self.purchase_products.values()]
        if self.purchase_product["values"] and not self.purchase_product.get():
            self.purchase_product.current(0)
            self.fill_default_cost()

    def fill_default_cost(self, _event=None):
        if self.purchase_product.get():
            product = self.purchase_products[combo_id(self.purchase_product.get())]
            self.purchase_cost.delete(0, tk.END)
            self.purchase_cost.insert(0, f"{float(product['cost_price']):.2f}")

    def add_to_purchase_cart(self):
        if not self.purchase_product.get():
            self.error("Choose a product.")
            return
        try:
            qty = ops.parse_positive_int(self.purchase_qty.get(), "Quantity")
            cost = ops.parse_money(self.purchase_cost.get(), "Unit cost", allow_zero=True)
        except OperationError as exc:
            self.error(str(exc))
            return
        product = self.purchase_products[combo_id(self.purchase_product.get())]
        for line in self.purchase_cart:
            if line["id"] == product["product_id"]:
                line["qty"] += qty
                line["cost"] = cost
                break
        else:
            self.purchase_cart.append({"id": product["product_id"], "name": product["product_name"],
                                       "qty": qty, "cost": cost})
        self.purchase_qty.delete(0, tk.END)
        self.refresh_purchase_cart()

    def remove_from_purchase_cart(self):
        selected = self.purchase_tree.selection()
        if selected:
            del self.purchase_cart[self.purchase_tree.index(selected[0])]
            self.refresh_purchase_cart()

    def refresh_purchase_cart(self):
        self.fill_tree(self.purchase_tree, [(l["name"], l["qty"], money(l["cost"]), money(l["qty"] * l["cost"]))
                                            for l in self.purchase_cart])
        total = sum(l["qty"] * l["cost"] for l in self.purchase_cart)
        self.purchase_total_label.config(text=f"Total: UGX {money(total)}")

    def submit_purchase_action(self):
        if not self.purchase_cart:
            self.error("Add at least one item to the purchase.")
            return
        if not self.purchase_supplier.get():
            self.error("Choose a supplier.")
            return
        try:
            purchase_id, total = ops.record_purchase(
                combo_id(self.purchase_supplier.get()), combo_id(self.purchase_branch.get()),
                self.user["employee_id"], [(l["id"], l["qty"], l["cost"]) for l in self.purchase_cart])
        except OperationError as exc:
            self.error(str(exc), "Purchase Not Saved")
            return
        except Exception as exc:                      # pylint: disable=broad-except
            self.error(str(exc), "Database Error")
            return
        messagebox.showinfo("Success", f"Purchase #{purchase_id} saved.\nTotal: UGX {money(total)}\n"
                                       "Stock levels have been updated.")
        self.purchase_cart.clear()
        self.refresh_purchase_cart()
        self.refresh_all()

    # ============================================================ CUSTOMERS TAB
    def build_customers_tab(self):
        tab = self.new_tab("customers")
        ttk.Label(tab, text="Customer Registration", font=("Arial", 12, "bold")).pack(anchor="w")
        form = ttk.Frame(tab)
        form.pack(fill="x", pady=6)
        self.cust_fields = {}
        for row, (key, label) in enumerate([("name", "Name *"), ("phone", "Phone"),
                                            ("email", "Email"), ("address", "Address")]):
            ttk.Label(form, text=label + ":").grid(row=row, column=0, sticky="w", pady=4, padx=5)
            entry = ttk.Entry(form, width=40)
            entry.grid(row=row, column=1, sticky="w")
            self.cust_fields[key] = entry
        tk.Button(form, text="Save Customer", bg=GREEN, fg="white", command=self.save_customer_action
                  ).grid(row=4, column=1, sticky="w", pady=8)

        holder, self.cust_tree = self.make_tree(tab, [
            ("id", "ID", 50, "center"), ("name", "Name", 220, "w"), ("phone", "Phone", 130, "w"),
            ("email", "Email", 200, "w"), ("address", "Address", 200, "w")], height=10)
        holder.pack(fill="both", expand=True)
        self.refreshers.append(self.reload_customers)
        self.reload_customers()

    def reload_customers(self):
        self.fill_tree(self.cust_tree, [(c["customer_id"], c["customer_name"], c["phone"] or "",
                                         c["email"] or "", c["address"] or "") for c in ops.get_customers()])

    def save_customer_action(self):
        try:
            ops.add_customer(*(self.cust_fields[k].get() for k in ("name", "phone", "email", "address")))
        except OperationError as exc:
            self.error(str(exc))
            return
        for entry in self.cust_fields.values():
            entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Customer saved.")
        self.refresh_all()

    # ============================================================= EXPENSES TAB
    def build_expenses_tab(self):
        tab = self.new_tab("expenses")
        ttk.Label(tab, text="Record Business Expense", font=("Arial", 12, "bold")).pack(anchor="w")
        form = ttk.Frame(tab)
        form.pack(fill="x", pady=6)
        self.expense_branch = self.branch_combo(form, 0)
        ttk.Label(form, text="Type:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.expense_type = ttk.Combobox(form, values=ops.EXPENSE_TYPES, width=24)
        self.expense_type.current(0)
        self.expense_type.grid(row=1, column=1, sticky="w")
        ttk.Label(form, text="Amount (UGX):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.expense_amount = ttk.Entry(form, width=18)
        self.expense_amount.grid(row=2, column=1, sticky="w")
        ttk.Label(form, text="Description:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.expense_desc = ttk.Entry(form, width=50)
        self.expense_desc.grid(row=3, column=1, sticky="w")
        tk.Button(form, text="Save Expense", bg=GREEN, fg="white", command=self.save_expense_action
                  ).grid(row=4, column=1, sticky="w", pady=8)

        holder, self.expense_tree = self.make_tree(tab, [
            ("id", "ID", 50, "center"), ("branch", "Branch", 150, "w"), ("type", "Type", 110, "w"),
            ("amount", "Amount", 100, "e"), ("date", "Date", 100, "center"), ("desc", "Description", 300, "w")],
            height=9)
        holder.pack(fill="both", expand=True)
        self.refreshers.append(self.reload_expenses)
        self.reload_expenses()

    def reload_expenses(self):
        self.fill_tree(self.expense_tree, [(e["expense_id"], e["branch_name"], e["expense_type"],
                                            money(e["amount"]), e["expense_date"], e["description"] or "")
                                           for e in ops.get_recent_expenses()])

    def save_expense_action(self):
        try:
            amount = ops.parse_money(self.expense_amount.get(), "Amount")
            ops.add_expense(combo_id(self.expense_branch.get()), self.user["employee_id"],
                            self.expense_type.get(), amount, self.expense_desc.get())
        except OperationError as exc:
            self.error(str(exc))
            return
        self.expense_amount.delete(0, tk.END)
        self.expense_desc.delete(0, tk.END)
        messagebox.showinfo("Success", "Expense saved.")
        self.refresh_all()

    # ===================================================== STOCK + LOW STOCK
    def build_stock_tab(self):
        tab = self.new_tab("stock")
        ttk.Label(tab, text="Current Stock Levels", font=("Arial", 12, "bold")).pack(anchor="w")
        bar = ttk.Frame(tab)
        bar.pack(fill="x", pady=6)
        ttk.Label(bar, text="Branch:").pack(side="left", padx=5)
        branches = ["0 - All branches"] + [f"{b['branch_id']} - {b['branch_name']}" for b in ops.get_branches()]
        self.stock_filter = ttk.Combobox(bar, values=branches, state="readonly", width=30)
        self.stock_filter.current(0)
        self.stock_filter.pack(side="left")
        self.stock_filter.bind("<<ComboboxSelected>>", lambda _e: self.reload_stock())
        tk.Button(bar, text="Refresh", bg=GREEN, fg="white", command=self.reload_stock).pack(side="left", padx=8)

        holder, self.stock_tree = self.make_tree(tab, [
            ("branch", "Branch", 160, "w"), ("product", "Product", 240, "w"),
            ("qty", "Qty On Hand", 100, "center"), ("reorder", "Reorder Level", 100, "center"),
            ("status", "Status", 80, "center")], height=16)
        holder.pack(fill="both", expand=True)
        self.stock_tree.tag_configure("LOW", foreground=ORANGE)
        self.refreshers.append(self.reload_stock)
        self.reload_stock()

    def reload_stock(self):
        branch_id = combo_id(self.stock_filter.get()) or None
        self.stock_tree.delete(*self.stock_tree.get_children())
        for r in ops.get_stock(branch_id):
            self.stock_tree.insert("", "end", tags=(r["status"],), values=(
                r["branch_name"], r["product_name"], r["quantity_on_hand"], r["reorder_level"], r["status"]))

    def build_lowstock_tab(self):
        tab = self.new_tab("lowstock")
        ttk.Label(tab, text="Products Below Reorder Level", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(tab, text="Load Low Stock Items", bg=ORANGE, fg="white", font=("Arial", 9, "bold"),
                  command=self.load_inventory_data).pack(pady=5)
        holder, self.tree = self.make_tree(tab, [
            ("Product", "Product Name", 220, "w"), ("Branch", "Branch Name", 160, "w"),
            ("Qty", "Qty On Hand", 100, "center"), ("Reorder", "Reorder Level", 100, "center")], height=14)
        holder.pack(pady=10, fill="both", expand=True)
        self.refreshers.append(self.load_inventory_data_quiet)
        self.load_inventory_data_quiet()

    def load_inventory_data_quiet(self):
        self.fill_tree(self.tree, [(i["product_name"], i["branch_name"], i["quantity_on_hand"],
                                    i["reorder_level"]) for i in ops.fetch_low_stock_products()])

    def load_inventory_data(self):
        """Fetches low stock data from the backend query and populates the UI table."""
        try:
            self.load_inventory_data_quiet()
            if not self.tree.get_children():
                messagebox.showinfo("Inventory Status", "No products are currently below reorder level.")
        except Exception as exc:                      # pylint: disable=broad-except
            self.error(f"Could not fetch inventory data:\n{exc}", "Database Error")

    # ================================================================ REPORTS
    def build_reports_tab(self):
        tab = self.new_tab("reports")
        ttk.Label(tab, text="Reports and Insights", font=("Arial", 12, "bold")).pack(anchor="w")
        bar = ttk.Frame(tab)
        bar.pack(fill="x", pady=6)
        choices = [("Low-stock report", reports.generate_text_low_stock_report, "text"),
                   ("Sales summary", reports.generate_text_sales_summary, "text"),
                   ("Daily sales chart", reports.generate_graphical_sales_chart, "image"),
                   ("Best sellers chart", reports.generate_best_sellers_chart, "image"),
                   ("Inventory value chart", reports.generate_inventory_value_chart, "image")]
        for label, func, kind in choices:
            tk.Button(bar, text=label, bg=GREEN, fg="white",
                      command=lambda f=func, k=kind: self.show_report(f, k)).pack(side="left", padx=3)

        self.report_text = tk.Text(tab, wrap="none", font=("Courier", 10), height=24)
        self.report_image = tk.Label(tab)
        self.report_photo = None
        self.report_text.pack(fill="both", expand=True, pady=6)
        self.report_text.insert("1.0", "Choose a report above. Files are also saved in the 'reports' folder.")
        self.report_text.config(state="disabled")

    def show_report(self, func, kind):
        try:
            path = func()
        except Exception as exc:                      # pylint: disable=broad-except
            self.error(f"Could not generate the report:\n{exc}", "Report Error")
            return
        if kind == "text":
            self.report_image.pack_forget()
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.report_text.config(state="normal")
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert("1.0", content)
            self.report_text.config(state="disabled")
            self.report_text.pack(fill="both", expand=True, pady=6)
        else:
            self.report_text.pack_forget()
            self.report_photo = tk.PhotoImage(file=path)
            self.report_image.config(image=self.report_photo)
            self.report_image.pack(expand=True, pady=6)

    # ================================================================== USERS
    def build_users_tab(self):
        tab = self.new_tab("users")
        ttk.Label(tab, text="User Accounts (Administrator)", font=("Arial", 12, "bold")).pack(anchor="w")
        holder, self.users_tree = self.make_tree(tab, [
            ("id", "ID", 50, "center"), ("username", "Username", 150, "w"), ("name", "Employee", 180, "w"),
            ("role", "Role", 150, "w"), ("status", "Status", 80, "center")], height=7)
        holder.pack(fill="x", pady=6)
        tk.Button(tab, text="Activate / Deactivate Selected", command=self.toggle_user_action).pack(anchor="w")

        form = ttk.LabelFrame(tab, text="Create login", padding=8)
        form.pack(fill="x", pady=12)
        ttk.Label(form, text="Username:").grid(row=0, column=0, sticky="w", pady=4)
        self.new_username = ttk.Entry(form, width=24)
        self.new_username.grid(row=0, column=1, padx=6)
        ttk.Label(form, text="Password (6+):").grid(row=0, column=2, sticky="w")
        self.new_password = ttk.Entry(form, width=20, show="*")
        self.new_password.grid(row=0, column=3, padx=6)
        ttk.Label(form, text="Role:").grid(row=1, column=0, sticky="w", pady=4)
        self.new_role = ttk.Combobox(form, values=ops.USER_ROLES, state="readonly", width=22)
        self.new_role.current(0)
        self.new_role.grid(row=1, column=1, padx=6)
        ttk.Label(form, text="Employee:").grid(row=1, column=2, sticky="w")
        self.new_employee = ttk.Combobox(form, state="readonly", width=28)
        self.new_employee.grid(row=1, column=3, padx=6)
        tk.Button(form, text="Create User", bg=GREEN, fg="white", command=self.create_user_action
                  ).grid(row=2, column=1, sticky="w", pady=6)
        self.refreshers.append(self.reload_users)
        self.reload_users()

    def reload_users(self):
        users = ops.get_users()
        self.fill_tree(self.users_tree, [(u["user_id"], u["username"], u["full_name"], u["role"], u["status"])
                                         for u in users])
        self.new_employee["values"] = [f"{e['employee_id']} - {e['full_name']} ({e['branch_name']})"
                                       for e in ops.get_employees()]
        if self.new_employee["values"] and not self.new_employee.get():
            self.new_employee.current(0)

    def toggle_user_action(self):
        selected = self.users_tree.selection()
        if not selected:
            self.error("Select a user first.")
            return
        values = self.users_tree.item(selected[0])["values"]
        user_id, current = int(values[0]), values[4]
        if user_id == self.user["user_id"]:
            self.error("You cannot deactivate your own account.")
            return
        try:
            ops.set_user_status(user_id, "Inactive" if current == "Active" else "Active")
        except OperationError as exc:
            self.error(str(exc))
            return
        self.refresh_all()

    def create_user_action(self):
        if not self.new_employee.get():
            self.error("Choose an employee.")
            return
        try:
            ops.add_user(self.new_username.get(), self.new_password.get(), self.new_role.get(),
                         combo_id(self.new_employee.get()))
        except OperationError as exc:
            self.error(str(exc))
            return
        self.new_username.delete(0, tk.END)
        self.new_password.delete(0, tk.END)
        messagebox.showinfo("Success", "User created.")
        self.refresh_all()
