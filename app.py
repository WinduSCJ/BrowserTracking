# Vercel entry point for Flask app
import os

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'

# Import simplified server for Vercel
from vercel_server import app

# This is required for Vercel serverless
app.config['ENV'] = 'production'

# This is required for Vercel
if __name__ == "__main__":
    app.run()
