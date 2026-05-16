import sys
import os

# This tells Vercel to look in the current folder for your app file
sys.path.append(os.path.dirname(__file__))

from app import app as application

app = application
