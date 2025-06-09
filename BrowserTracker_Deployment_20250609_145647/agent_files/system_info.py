import platform
import socket
import psutil
import os
import getpass
from uuid import getnode

def get_mac_address():
    """Get MAC address of the current machine"""
    try:
        mac = getnode()
        mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        return mac_address
    except:
        return "00:00:00:00:00:00"

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_hostname():
    """Get computer hostname"""
    try:
        return socket.gethostname()
    except:
        return "unknown"

def get_username():
    """Get current username"""
    try:
        return getpass.getuser()
    except:
        return "unknown"

def get_os_info():
    """Get operating system information"""
    try:
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    except:
        return {'system': 'unknown'}

def get_system_info():
    """Get comprehensive system information"""
    return {
        'hostname': get_hostname(),
        'mac_address': get_mac_address(),
        'local_ip': get_local_ip(),
        'username': get_username(),
        'os_info': get_os_info()
    }

def is_admin():
    """Check if running with admin privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_network_interfaces():
    """Get all network interfaces"""
    try:
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    interfaces.append({
                        'interface': interface,
                        'ip': addr.address,
                        'netmask': addr.netmask
                    })
        return interfaces
    except:
        return []

def get_running_processes():
    """Get list of running processes (limited info for privacy)"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    except:
        return []

def get_chrome_processes():
    """Get Chrome-related processes"""
    try:
        chrome_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    chrome_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return chrome_processes
    except:
        return []
