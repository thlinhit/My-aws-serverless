import sys
import os

# Determine the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))

# Add the 'src' directory to the Python path if it isn't already included
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Optionally, print the current PYTHONPATH for debugging purposes
# print("PYTHONPATH:", sys.path)