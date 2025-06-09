"""
Create desktop shortcuts for Browser Tracking Agent GUI
"""

import os
import sys

def create_desktop_shortcut():
    """Create desktop shortcut for the GUI"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Browser Tracking Agent.lnk")
        target = sys.executable
        wDir = os.path.dirname(os.path.abspath(__file__))
        arguments = f'"{os.path.join(wDir, "simple_gui.py")}"'
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = wDir
        shortcut.Description = "Browser Tracking Agent Control Panel"
        shortcut.save()
        
        print(f"Desktop shortcut created: {path}")
        return True
        
    except ImportError:
        print("winshell and pywin32 packages required for shortcuts")
        print("Install with: pip install winshell pywin32")
        return False
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False

def create_batch_launcher():
    """Create batch file launcher"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        batch_content = f'''@echo off
cd /d "{current_dir}"
python simple_gui.py
pause'''
        
        batch_path = os.path.join(current_dir, "Launch GUI.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print(f"Batch launcher created: {batch_path}")
        return True
        
    except Exception as e:
        print(f"Error creating batch launcher: {e}")
        return False

def main():
    """Main function"""
    print("Creating shortcuts for Browser Tracking Agent GUI...")
    print()
    
    # Create batch launcher (always works)
    if create_batch_launcher():
        print("✓ Batch launcher created successfully")
    else:
        print("✗ Failed to create batch launcher")
    
    print()
    
    # Try to create desktop shortcut
    if create_desktop_shortcut():
        print("✓ Desktop shortcut created successfully")
    else:
        print("✗ Failed to create desktop shortcut")
        print("  You can manually create a shortcut to 'Launch GUI.bat'")
    
    print()
    print("Setup complete!")
    print()
    print("To start the GUI:")
    print("1. Double-click 'Launch GUI.bat'")
    print("2. Or run: python simple_gui.py")
    print("3. Or use the desktop shortcut (if created)")

if __name__ == "__main__":
    main()
