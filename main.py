"""Main entry point for the Sales Management System (RISMS)."""

import tkinter as tk
from frontend.ui.app import SalesManagementApp
from backend.reports import generate_text_low_stock_report, generate_graphical_sales_chart

def main():
    """Initializes and runs the Sales Management application."""
    print("==================================================")
    print("     INITIALIZING SALES MANAGEMENT SYSTEM (RISMS) ")
    print("==================================================")
    
    # Step 1: Run background report and chart generators
    print("[1/2] Generating system reports & charts...")
    try:
        generate_text_low_stock_report()
        generate_graphical_sales_chart()
        print("Reports generated successfully inside 'reports/' directory!")
    except Exception as e:
        print(f"Notice: Could not auto-generate background reports yet: {e}")

    # Step 2: Launch the Graphical User Interface
    print("[2/2] Launching Graphical User Interface...")
    root = tk.Tk()
    SalesManagementApp(root)
    
    # Start the Tkinter main event loop
    root.mainloop()


if __name__ == "__main__":
    main()