"""Main entry point for the Sales Management System (RISMS).

Run from the project folder:   python main.py
"""

import tkinter as tk

from backend.reports import generate_all_reports
from frontend.ui.app import SalesManagementApp


def main():
    """Initializes and runs the Sales Management application."""
    print("==================================================")
    print("     INITIALIZING SALES MANAGEMENT SYSTEM (RISMS) ")
    print("==================================================")

    # Step 1: generate the text reports and charts in the 'reports/' folder
    print("[1/2] Generating system reports & charts...")
    try:
        generate_all_reports()
        print("Reports generated successfully inside 'reports/' directory!")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Notice: could not generate background reports yet: {exc}")

    # Step 2: launch the graphical user interface (startup menu / login screen first)
    print("[2/2] Launching Graphical User Interface...")
    root = tk.Tk()
    SalesManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()