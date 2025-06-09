"""
Create Desktop and Start Menu Shortcuts for Browser Tracker GUI
"""

import os
import sys

def create_shortcuts():
    """Create desktop and start menu shortcuts"""
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        # Paths
        gui_script = os.path.join(os.path.dirname(__file__), "BrowserTracker_GUI.py")
        python_exe = sys.executable
        
        # Desktop shortcut
        desktop = winshell.desktop()
        desktop_shortcut = os.path.join(desktop, "Browser Tracker.lnk")
        
        # Start menu shortcut
        start_menu = winshell.start_menu()
        start_menu_shortcut = os.path.join(start_menu, "Browser Tracker.lnk")
        
        # Create shortcuts
        shell = Dispatch('WScript.Shell')
        
        # Desktop shortcut
        shortcut = shell.CreateShortCut(desktop_shortcut)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{gui_script}"'
        shortcut.WorkingDirectory = os.path.dirname(gui_script)
        shortcut.IconLocation = python_exe
        shortcut.Description = "Browser Tracker - Monitor browser activity"
        shortcut.save()
        
        # Start menu shortcut
        shortcut = shell.CreateShortCut(start_menu_shortcut)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{gui_script}"'
        shortcut.WorkingDirectory = os.path.dirname(gui_script)
        shortcut.IconLocation = python_exe
        shortcut.Description = "Browser Tracker - Monitor browser activity"
        shortcut.save()
        
        print("✅ Desktop shortcut created: Browser Tracker")
        print("✅ Start menu shortcut created: Browser Tracker")
        print("\nYou can now:")
        print("1. Double-click 'Browser Tracker' on desktop")
        print("2. Find 'Browser Tracker' in Start Menu")
        print("3. Pin to taskbar for easy access")
        
        return True
        
    except ImportError:
        print("❌ Missing packages. Installing...")
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "pywin32", "winshell"], 
                         capture_output=True)
            print("✅ Packages installed. Please run again.")
        except:
            print("❌ Please install manually: pip install pywin32 winshell")
        return False
        
    except Exception as e:
        print(f"❌ Error creating shortcuts: {e}")
        return False

def create_batch_launcher():
    """Create simple batch file launcher as backup"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        batch_content = f'''@echo off
title Browser Tracker
cd /d "{current_dir}"
python BrowserTracker_GUI.py
pause'''
        
        batch_path = os.path.join(current_dir, "Browser Tracker.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print(f"✅ Batch launcher created: {batch_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating batch launcher: {e}")
        return False

if __name__ == "__main__":
    print("Creating Browser Tracker shortcuts...")
    
    # Try to create proper shortcuts
    if not create_shortcuts():
        # Fallback to batch file
        print("\nCreating batch file launcher as backup...")
        create_batch_launcher()
    
    print("\n" + "="*50)
    print("Browser Tracker GUI is ready!")
    print("="*50)
