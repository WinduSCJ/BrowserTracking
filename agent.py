import os
import sys
import json
import time
import schedule
import threading
from datetime import datetime
import signal

from system_info import get_system_info
from browser_reader import ChromeHistoryReader
from network_client import NetworkClient
from logger import setup_logger

class BrowserTrackingAgent:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = setup_logger(__name__)
        
        self.client_id = None
        self.running = False
        self.last_sync_time = None
        
        # Initialize components
        self.browser_reader = ChromeHistoryReader()
        self.network_client = NetworkClient(self.config)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Return default config
            return {
                "client": {
                    "server_url": "http://localhost:5000",
                    "api_token": "default-token",
                    "check_interval": 300,
                    "batch_size": 100
                }
            }
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def _register_client(self):
        """Register this client with the server"""
        try:
            system_info = get_system_info()
            self.logger.info(f"Registering client: {system_info['hostname']} ({system_info['mac_address']})")
            
            client_id = self.network_client.register_client(system_info)
            if client_id:
                self.client_id = client_id
                self.logger.info(f"Successfully registered with client ID: {client_id}")
                return True
            else:
                self.logger.error("Failed to register client")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during client registration: {e}")
            return False
    
    def _collect_and_send_data(self):
        """Collect browsing data and send to server"""
        try:
            self.logger.info("Collecting browsing data...")
            
            # Get recent browsing data
            check_interval_hours = self.config['client']['check_interval'] / 3600
            browsing_data = self.browser_reader.get_recent_history(
                hours=max(check_interval_hours * 2, 1),  # Get a bit more than interval
                limit=self.config['client'].get('batch_size', 100)
            )
            
            if not browsing_data['browsing_history'] and not browsing_data['profiles']:
                self.logger.info("No new data to send")
                return True
            
            # Send data to server
            success = self.network_client.send_batch_data(
                self.client_id,
                browsing_data['browsing_history'],
                browsing_data['profiles']
            )
            
            if success:
                self.last_sync_time = datetime.now()
                self.logger.info(f"Data sync completed successfully at {self.last_sync_time}")
            else:
                self.logger.error("Failed to sync data with server")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error collecting and sending data: {e}")
            return False
    
    def _run_scheduled_tasks(self):
        """Run scheduled tasks in a separate thread"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in scheduled tasks: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the browser tracking agent"""
        self.logger.info("Starting Browser Tracking Agent...")
        
        # Test server connection
        if not self.network_client.test_connection():
            self.logger.error("Cannot connect to server. Exiting.")
            return False
        
        # Register client
        if not self._register_client():
            self.logger.error("Failed to register client. Exiting.")
            return False
        
        # Set running flag
        self.running = True
        
        # Schedule data collection
        check_interval = self.config['client']['check_interval']
        schedule.every(check_interval).seconds.do(self._collect_and_send_data)
        
        # Initial data collection
        self._collect_and_send_data()
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self._run_scheduled_tasks, daemon=True)
        scheduler_thread.start()
        
        self.logger.info(f"Agent started successfully. Data collection interval: {check_interval} seconds")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        
        self.stop()
        return True
    
    def stop(self):
        """Stop the browser tracking agent"""
        self.logger.info("Stopping Browser Tracking Agent...")
        self.running = False
        
        # Clear scheduled jobs
        schedule.clear()
        
        self.logger.info("Agent stopped successfully")
    
    def run_once(self):
        """Run data collection once (for testing)"""
        self.logger.info("Running one-time data collection...")
        
        if not self.network_client.test_connection():
            self.logger.error("Cannot connect to server")
            return False
        
        if not self._register_client():
            self.logger.error("Failed to register client")
            return False
        
        return self._collect_and_send_data()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Browser Tracking Agent')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon (background)')
    
    args = parser.parse_args()
    
    # Create agent
    agent = BrowserTrackingAgent(args.config)
    
    if args.once:
        # Run once and exit
        success = agent.run_once()
        sys.exit(0 if success else 1)
    else:
        # Run continuously
        if args.daemon:
            # TODO: Implement proper daemon mode for Windows
            pass
        
        success = agent.start()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
