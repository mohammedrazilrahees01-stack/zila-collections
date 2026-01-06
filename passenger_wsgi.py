import os
import sys

# Add the current directory to the path so it can find 'core'
sys.path.insert(0, os.path.dirname(__file__))

# Set the settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Import the application object from core/wsgi.py
from core.wsgi import application