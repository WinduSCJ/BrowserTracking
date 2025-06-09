import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
import time
from datetime import datetime
import requests
from database import BrowserTrackingDB

class BrowserTrackingMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser Tracking Monitor")
        self.root.geometry("1200x800")
        
        self.config = self.load_config()
        self.db = BrowserTrackingDB(self.config['database']['path'])
        
        self.auto_refresh = tk.BooleanVar(value=False)
        self.refresh_interval = 30  # seconds
        
        self.setup_ui()
        self.refresh_data()
    
    def load_config(self):
        """Load configuration"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'database': {'path': 'browser_tracking.db'},
                'server': {'host': 'localhost', 'port': 5000}
            }
    
    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Browser Tracking Monitor", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(control_frame, text="Refresh", command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto refresh checkbox
        auto_refresh_cb = ttk.Checkbutton(control_frame, text="Auto Refresh (30s)", 
                                         variable=self.auto_refresh,
                                         command=self.toggle_auto_refresh)
        auto_refresh_cb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Recent Activity tab
        self.setup_activity_tab(notebook)
        
        # Clients tab
        self.setup_clients_tab(notebook)
        
        # Statistics tab
        self.setup_stats_tab(notebook)
    
    def setup_activity_tab(self, notebook):
        """Setup recent activity tab"""
        activity_frame = ttk.Frame(notebook)
        notebook.add(activity_frame, text="Recent Activity")
        
        # Activity controls
        controls_frame = ttk.Frame(activity_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Hours:").pack(side=tk.LEFT)
        self.hours_var = tk.StringVar(value="24")
        hours_entry = ttk.Entry(controls_frame, textvariable=self.hours_var, width=5)
        hours_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(controls_frame, text="Limit:").pack(side=tk.LEFT)
        self.limit_var = tk.StringVar(value="100")
        limit_entry = ttk.Entry(controls_frame, textvariable=self.limit_var, width=5)
        limit_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        filter_btn = ttk.Button(controls_frame, text="Filter", command=self.refresh_data)
        filter_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Activity treeview
        columns = ('Time', 'Hostname', 'User', 'URL', 'Title', 'Profile', 'Gmail')
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.activity_tree.heading('Time', text='Time')
        self.activity_tree.heading('Hostname', text='Hostname')
        self.activity_tree.heading('User', text='User')
        self.activity_tree.heading('URL', text='URL')
        self.activity_tree.heading('Title', text='Title')
        self.activity_tree.heading('Profile', text='Profile')
        self.activity_tree.heading('Gmail', text='Gmail')
        
        self.activity_tree.column('Time', width=150)
        self.activity_tree.column('Hostname', width=100)
        self.activity_tree.column('User', width=80)
        self.activity_tree.column('URL', width=300)
        self.activity_tree.column('Title', width=200)
        self.activity_tree.column('Profile', width=80)
        self.activity_tree.column('Gmail', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        h_scrollbar = ttk.Scrollbar(activity_frame, orient=tk.HORIZONTAL, command=self.activity_tree.xview)
        self.activity_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
    
    def setup_clients_tab(self, notebook):
        """Setup clients tab"""
        clients_frame = ttk.Frame(notebook)
        notebook.add(clients_frame, text="Clients")
        
        # Clients treeview
        columns = ('Hostname', 'MAC', 'IP', 'User', 'OS', 'First Seen', 'Last Seen')
        self.clients_tree = ttk.Treeview(clients_frame, columns=columns, show='headings')
        
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=120)
        
        self.clients_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for clients
        clients_scrollbar = ttk.Scrollbar(clients_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=clients_scrollbar.set)
        clients_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_stats_tab(self, notebook):
        """Setup statistics tab"""
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def refresh_data(self):
        """Refresh all data"""
        self.status_label.config(text="Refreshing...")
        self.root.update()
        
        try:
            # Get parameters
            hours = int(self.hours_var.get())
            limit = int(self.limit_var.get())
            
            # Refresh activity
            activity = self.db.get_recent_activity(hours, limit)
            self.update_activity_tree(activity)
            
            # Refresh clients
            self.update_clients_tree()
            
            # Refresh statistics
            self.update_statistics()
            
            self.status_label.config(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")
    
    def update_activity_tree(self, activity):
        """Update activity treeview"""
        # Clear existing items
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Add new items
        for entry in activity:
            # Format time
            try:
                visit_time = datetime.fromisoformat(entry['visit_time'].replace('Z', '+00:00'))
                time_str = visit_time.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = entry['visit_time']
            
            # Truncate long URLs and titles
            url = entry['url'][:50] + '...' if len(entry['url']) > 50 else entry['url']
            title = entry['title'][:30] + '...' if len(entry['title']) > 30 else entry['title']
            
            self.activity_tree.insert('', tk.END, values=(
                time_str,
                entry['hostname'],
                entry['username'],
                url,
                title,
                entry['profile_name'] or '',
                entry['gmail_account'] or ''
            ))
    
    def update_clients_tree(self):
        """Update clients treeview"""
        # This would need to be implemented in the database class
        # For now, just clear the tree
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
    
    def update_statistics(self):
        """Update statistics"""
        try:
            # Get basic stats
            activity = self.db.get_recent_activity(24, 10000)
            
            stats = f"""Browser Tracking Statistics
{'=' * 40}

Recent Activity (24 hours):
- Total visits: {len(activity)}
- Unique hostnames: {len(set(entry['hostname'] for entry in activity))}
- Unique users: {len(set(entry['username'] for entry in activity))}
- Unique URLs: {len(set(entry['url'] for entry in activity))}

Top Websites:
"""
            
            # Count URL visits
            url_counts = {}
            for entry in activity:
                domain = entry['url'].split('/')[2] if '://' in entry['url'] else entry['url']
                url_counts[domain] = url_counts.get(domain, 0) + 1
            
            # Sort and show top 10
            top_urls = sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for domain, count in top_urls:
                stats += f"- {domain}: {count} visits\n"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"Error generating statistics: {str(e)}")
    
    def toggle_auto_refresh(self):
        """Toggle auto refresh"""
        if self.auto_refresh.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Start auto refresh thread"""
        def auto_refresh_worker():
            while self.auto_refresh.get():
                time.sleep(self.refresh_interval)
                if self.auto_refresh.get():
                    self.root.after(0, self.refresh_data)
        
        self.auto_refresh_thread = threading.Thread(target=auto_refresh_worker, daemon=True)
        self.auto_refresh_thread.start()
    
    def stop_auto_refresh(self):
        """Stop auto refresh"""
        # Auto refresh will stop when the flag is False
        pass

def main():
    root = tk.Tk()
    app = BrowserTrackingMonitor(root)
    root.mainloop()

if __name__ == '__main__':
    main()
