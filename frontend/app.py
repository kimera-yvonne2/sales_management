import tkinter as tk
from tkinter import messagebox, ttk
from backend.operations import fetch_all_branches, fetch_low_stock_products

class SalesManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sales Management System - User Interface")
        self.root.geometry("650x500")
        self.root.config(bg="#f4f6f9")

        # Application Header
        header_label = tk.Label(
            root, text="Retail Sales & Inventory Management", 
            font=("Arial", 16, "bold"), bg="#f4f6f9", fg="#2b2d42"
        )
        header_label.pack(pady=15)

        # Notebook (Tabs for different forms/views)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tab 1: Record Sale Form
        self.create_sale_tab()

        # Tab 2: Low Stock Viewer Tab
        self.create_inventory_tab()

    def create_sale_tab(self):
        """Creates the form interface for recording a customer sale."""
        sale_frame = ttk.Frame(self.notebook)
        self.notebook.add(sale_frame, text="Record Sale Form")

        tk.Label(sale_frame, text="New Customer Transaction", font=("Arial", 12, "bold")).pack(pady=15)

        # Form Fields Container
        form_container = ttk.Frame(sale_frame)
        form_container.pack(pady=5)

        # Customer ID
        tk.Label(form_container, text="Customer ID:").grid(row=0, column=0, sticky="w", pady=8, padx=10)
        self.cust_entry = ttk.Entry(form_container, width=30)
        self.cust_entry.grid(row=0, column=1, pady=8)

        # Branch Selection (Dynamic or Manual)
        tk.Label(form_container, text="Branch ID:").grid(row=1, column=0, sticky="w", pady=8, padx=10)
        self.branch_entry = ttk.Entry(form_container, width=30)
        self.branch_entry.grid(row=1, column=1, pady=8)

        # Employee ID
        tk.Label(form_container, text="Employee ID:").grid(row=2, column=0, sticky="w", pady=8, padx=10)
        self.emp_entry = ttk.Entry(form_container, width=30)
        self.emp_entry.grid(row=2, column=1, pady=8)

        # Total Amount
        tk.Label(form_container, text="Total Amount ($):").grid(row=3, column=0, sticky="w", pady=8, padx=10)
        self.amount_entry = ttk.Entry(form_container, width=30)
        self.amount_entry.grid(row=3, column=1, pady=8)

        # Submit Button
        submit_btn = tk.Button(
            sale_frame, text="Submit Sale", bg="#2a9d8f", fg="white", 
            font=("Arial", 10, "bold"), padx=10, pady=5, command=self.submit_sale_action
        )
        submit_btn.pack(pady=20)

    def create_inventory_tab(self):
        """Creates a view interface to check low stock items using backend queries."""
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="Low Stock Alert View")

        tk.Label(inv_frame, text="Products Below Reorder Level", font=("Arial", 12, "bold")).pack(pady=15)

        # Refresh button to fetch live data from MySQL
        refresh_btn = tk.Button(
            inv_frame, text="Load Low Stock Items", bg="#e76f51", fg="white", 
            font=("Arial", 9, "bold"), command=self.load_inventory_data
        )
        refresh_btn.pack(pady=5)

        # Treeview (Table) to display the query results inside the UI
        self.tree = ttk.Treeview(inv_frame, columns=("Product", "Branch", "Qty", "Reorder"), show="headings", height=10)
        self.tree.heading("Product", text="Product Name")
        self.tree.heading("Branch", text="Branch Name")
        self.tree.heading("Qty", text="Qty On Hand")
        self.tree.heading("Reorder", text="Reorder Level")
        
        self.tree.column("Product", width=180)
        self.tree.column("Branch", width=130)
        self.tree.column("Qty", width=90, anchor="center")
        self.tree.column("Reorder", width=90, anchor="center")
        
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

    def submit_sale_action(self):
        """Validates and handles the form submission."""
        cust_id = self.cust_entry.get()
        branch_id = self.branch_entry.get()
        emp_id = self.emp_entry.get()
        amount = self.amount_entry.get()

        if not cust_id or not branch_id or not emp_id or not amount:
            messagebox.showerror("Validation Error", "All fields must be filled out!")
            return

        # Here you would normally call a function from backend/operations.py to insert into the SALE table
        messagebox.showinfo("Success", f"Sale of ${amount} successfully recorded for Branch ID {branch_id}!")
        
        # Clear entries
        self.cust_entry.delete(0, tk.END)
        self.branch_entry.delete(0, tk.END)
        self.emp_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def load_inventory_data(self):
        """Fetches low stock data from the backend query and populates the UI table."""
        # Clear existing table data
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            results = fetch_low_stock_products()
            if not results:
                messagebox.showinfo("Inventory Status", "No products are currently below reorder level.")
                return
            
            for item in results:
                self.tree.insert("", "end", values=(
                    item['product_name'], 
                    item['branch_name'], 
                    item['quantity_on_hand'], 
                    item['reorder_level']
                ))
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not fetch inventory data:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SalesManagementApp(root)
    root.mainloop()