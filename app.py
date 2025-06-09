# Vercel entry point for Flask app
import os
import json

# Force use of Vercel config for production
os.environ['CONFIG_FILE'] = 'config_vercel.json'

from server import app

# This is required for Vercel
if __name__ == "__main__":
    app.run()
