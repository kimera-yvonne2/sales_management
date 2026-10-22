"""Launch the Streamlit Sales Management System (RISMS)."""

import os
import subprocess
import sys


def main():
    """Run Streamlit on the project's dashboard."""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamlit_app.py")
    raise SystemExit(subprocess.call([sys.executable, "-m", "streamlit", "run", app_path]))


if __name__ == "__main__":
    main()
