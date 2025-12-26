"""
WSGI configuration for PythonAnywhere deployment

This file is used by PythonAnywhere to run your Flask application.
Copy the contents of this file to the WSGI configuration file in PythonAnywhere.
"""

import sys
import os
from pathlib import Path

# IMPORTANT: Fix for Prisma 403 Forbidden error on PythonAnywhere
# This bypasses checksum verification which is blocked by PythonAnywhere's firewall
os.environ['PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING'] = '1'

# Add your project directory to the sys.path
# IMPORTANT: Update this path to match your PythonAnywhere directory
project_home = '/home/YOUR_USERNAME/diary-app/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(project_home) / '.env'
load_dotenv(dotenv_path=env_path)

# Import the Flask app
from app import app as application
from app import prisma

# Connect to database on startup
try:
    prisma.connect()
    print("✅ Database connected")
except Exception as e:
    print(f"⚠️  Warning: Could not connect to database: {e}")

# PythonAnywhere will use the 'application' variable
# Don't change the variable name!

