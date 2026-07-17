import sys
import os

# Add parent directory to path so we can import 'app' module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and create the Flask application
from app import create_app

# Create the app instance - Vercel looks for a top-level 'app' variable
app = create_app()
