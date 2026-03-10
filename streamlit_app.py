import sys
import os

# Ensure the project root is on sys.path before any imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import runpy
runpy.run_path(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "main.py"),
    run_name="__main__"
)
