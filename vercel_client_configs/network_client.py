import requests
import json
import time
from logger import setup_logger

logger = setup_logger(__name__)

class NetworkClient:
    def __init__(self, config):
        self.server_url = config['client']['server_url']
        self.api_token = config['client']['api_token']
        self.retry_attempts = config['client'].get('retry_attempts', 3)
        self.retry_delay = config['client'].get('retry_delay', 60)
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'BrowserTrackingAgent/1.0'
        })
        
        # Set timeout
        self.timeout = 30
    
    def _make_request(self, method, endpoint, data=None):
        """Make HTTP request with retry logic"""
        url = f"{self.server_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.retry_attempts):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All retry attempts failed for {url}")
                    raise
    
    def test_connection(self):
        """Test connection to server"""
        try:
            response = self._make_request('GET', '/health')
            logger.info("Successfully connected to server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            return False
    
    def register_client(self, system_info):
        """Register client with server"""
        try:
            response = self._make_request('POST', '/api/register', system_info)
            
            if response.get('success'):
                client_id = response.get('client_id')
                logger.info(f"Client registered successfully with ID: {client_id}")
                return client_id
            else:
                logger.error(f"Failed to register client: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error registering client: {e}")
            return None
    
    def send_browsing_data(self, client_id, browsing_data):
        """Send browsing history data to server"""
        try:
            if not browsing_data:
                logger.info("No browsing data to send")
                return True
            
            payload = {
                'client_id': client_id,
                'browsing_data': browsing_data
            }
            
            response = self._make_request('POST', '/api/browsing-data', payload)
            
            if response.get('success'):
                logger.info(f"Successfully sent {len(browsing_data)} browsing entries")
                return True
            else:
                logger.error(f"Failed to send browsing data: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending browsing data: {e}")
            return False
    
    def send_profiles_data(self, client_id, profiles):
        """Send browser profiles data to server"""
        try:
            if not profiles:
                logger.info("No profiles data to send")
                return True
            
            payload = {
                'client_id': client_id,
                'profiles': profiles
            }
            
            response = self._make_request('POST', '/api/profiles', payload)
            
            if response.get('success'):
                logger.info(f"Successfully sent {len(profiles)} profiles")
                return True
            else:
                logger.error(f"Failed to send profiles data: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending profiles data: {e}")
            return False
    
    def send_batch_data(self, client_id, browsing_data, profiles):
        """Send both browsing data and profiles in sequence"""
        success = True
        
        # Send profiles first
        if profiles:
            if not self.send_profiles_data(client_id, profiles):
                success = False
        
        # Send browsing data
        if browsing_data:
            if not self.send_browsing_data(client_id, browsing_data):
                success = False
        
        return success
