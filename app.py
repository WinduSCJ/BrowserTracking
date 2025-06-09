# Vercel entry point for Flask app
import os
import json

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'
os.environ['CONFIG_FILE'] = 'config_vercel.json'

# Import after setting environment
from server import app

# This is required for Vercel serverless
app.config['ENV'] = 'production'

# Export for Vercel
def handler(event, context):
    """AWS Lambda/Vercel handler"""
    return app(event, context)

# This is required for Vercel
if __name__ == "__main__":
    app.run()
