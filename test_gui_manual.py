"""
Test GUI with manual start (no auto-start)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import our GUI
from BrowserTracker_GUI import BrowserTrackerGUI

class TestGUI(BrowserTrackerGUI):
    def __init__(self):
        # Override auto_start to False
        super().__init__()
        self.auto_start.set(False)  # Disable auto-start
        
        # Add test button using grid (consistent with parent)
        test_frame = ttk.Frame(self.root)
        test_frame.grid(row=10, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(test_frame, text="Manual Test Collection", 
                  command=self.manual_test).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(test_frame, text="Test Connection", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
    
    def manual_test(self):
        """Manual test data collection"""
        try:
            self.log("🧪 Manual test started...")
            
            # Test connection first
            if not self.agent.test_connection():
                self.log("❌ Connection test failed")
                return
            
            # Register if needed
            if not self.agent.client_id:
                if not self.agent.register_client():
                    self.log("❌ Registration failed")
                    return
            
            # Collect and send data
            result = self.agent.collect_and_send_data()
            if result:
                self.log("✅ Manual test completed successfully")
            else:
                self.log("❌ Manual test failed")
                
        except Exception as e:
            self.log(f"❌ Manual test error: {e}")
    
    def test_connection(self):
        """Test server connection"""
        try:
            self.log("🔗 Testing connection...")
            if self.agent.test_connection():
                self.log("✅ Connection successful")
                messagebox.showinfo("Success", "Connection to server successful!")
            else:
                self.log("❌ Connection failed")
                messagebox.showerror("Error", "Connection to server failed!")
        except Exception as e:
            self.log(f"❌ Connection error: {e}")
            messagebox.showerror("Error", f"Connection error: {e}")

def main():
    """Main function"""
    try:
        app = TestGUI()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to start Browser Tracker: {e}")

if __name__ == "__main__":
    main()
