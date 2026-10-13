"""
Root Runner for Browser History Manager
Allows running directly from workspace root: python run.py
"""

import os
import sys

# Set working directory to browser-history-manager
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(current_dir, "browser-history-manager")

if os.path.exists(project_dir):
    os.chdir(project_dir)
    sys.path.insert(0, project_dir)

from app import app

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Browser History Manager — Flask Web Server")
    print("  Open in browser: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
