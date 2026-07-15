import os
import sys

# Forces Vercel to dynamically recognize adjacent folder layouts for package modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()
