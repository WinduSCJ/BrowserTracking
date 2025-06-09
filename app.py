# Vercel entry point for Flask app
import os
import json

# Use Vercel config if available
if os.path.exists('config_vercel.json'):
    os.environ['CONFIG_FILE'] = 'config_vercel.json'

from server import app

# This is required for Vercel
if __name__ == "__main__":
    app.run()
