#!/usr/bin/env python3
"""
Orange Pi Dashboard Configuration Server
Flask-based web GUI for managing dashboard settings
Accessible via phone at http://orangepi.local:3000
"""

import os
import json
import subprocess
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

# ===== CONFIGURATION =====
CONFIG_DIR = '/etc/dashboard'
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
DASHBOARD_DIR = '/opt/dashboard'
UPDATE_LOG = '/var/log/dashboard-update.log'
DEFAULT_PORT = 3000

# For development/testing on Windows
if os.name == 'nt':
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
    CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
    DASHBOARD_DIR = os.path.dirname(__file__)
    UPDATE_LOG = os.path.join(os.path.dirname(__file__), 'update.log')

# ===== FLASK APP =====
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== DEFAULT CONFIGURATION =====
DEFAULT_CONFIG = {
    "nightscout": {
        "url": "",
        "api_secret": ""
    },
    "supabase": {
        "url": "",
        "anon_key": "",
        "reminders_table": "reminders",
        "motivational_table": "motivational_messages"
    },
    "display": {
        "timezone": "America/Denver",
        "day_mode_start": 6,
        "day_mode_end": 20,
        "motivational_hours_start": 7,
        "motivational_hours_end": 10
    },
    "system": {
        "auto_update": True,
        "update_time": "07:00",
        "hostname": "orangepi"
    }
}

# ===== UTILITY FUNCTIONS =====
def ensure_config_dir():
    """Create config directory if it doesn't exist"""
    if not os.path.exists(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
        except PermissionError:
            logger.warning(f"Cannot create {CONFIG_DIR}, using current directory")
            return False
    return True

def load_config():
    """Load configuration from file"""
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = DEFAULT_CONFIG.copy()
                for section, values in config.items():
                    if section in merged and isinstance(values, dict):
                        merged[section].update(values)
                    else:
                        merged[section] = values
                return merged
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def run_command(cmd, timeout=30):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def get_wifi_networks():
    """Get list of available WiFi networks"""
    if os.name == 'nt':
        return [{"ssid": "TestNetwork1", "signal": 80}, {"ssid": "TestNetwork2", "signal": 60}]
    
    success, output = run_command("nmcli -t -f SSID,SIGNAL device wifi list")
    if success:
        networks = []
        for line in output.strip().split('\n'):
            if ':' in line:
                parts = line.split(':')
                if parts[0]:
                    networks.append({"ssid": parts[0], "signal": int(parts[1]) if parts[1].isdigit() else 0})
        return sorted(networks, key=lambda x: x['signal'], reverse=True)
    return []

def get_current_wifi():
    """Get currently connected WiFi network"""
    if os.name == 'nt':
        return "TestNetwork"
    
    success, output = run_command("nmcli -t -f ACTIVE,SSID dev wifi | grep '^yes'")
    if success and ':' in output:
        return output.split(':')[1].strip()
    return None

def connect_wifi(ssid, password):
    """Connect to a WiFi network"""
    if os.name == 'nt':
        return True, "Simulated connection"
    
    cmd = f'nmcli device wifi connect "{ssid}" password "{password}"'
    return run_command(cmd)

def get_ip_address():
    """Get current IP address"""
    if os.name == 'nt':
        return "192.168.1.100"
    
    success, output = run_command("hostname -I | awk '{print $1}'")
    return output.strip() if success else "Unknown"

def get_hostname():
    """Get system hostname"""
    if os.name == 'nt':
        return "orangepi-dev"
    
    success, output = run_command("hostname")
    return output.strip() if success else "orangepi"

def is_hotspot_active():
    """Check if hotspot mode is active"""
    if os.name == 'nt':
        return False
    
    success, output = run_command("nmcli -t -f NAME,TYPE con show --active | grep hotspot")
    return success and 'hotspot' in output.lower()

def toggle_hotspot(enable, ssid="OrangePi-Setup", password="dashboard123"):
    """Enable or disable WiFi hotspot mode"""
    if os.name == 'nt':
        return True, "Simulated hotspot toggle"
    
    if enable:
        # Stop any existing hotspot
        run_command("nmcli con down Hotspot 2>/dev/null")
        # Create and start hotspot
        cmd = f'nmcli device wifi hotspot ssid "{ssid}" password "{password}"'
        return run_command(cmd)
    else:
        return run_command("nmcli con down Hotspot")

def get_git_version():
    """Get current git commit hash"""
    if os.name == 'nt':
        success, output = run_command(f'cd "{DASHBOARD_DIR}" && git rev-parse --short HEAD')
    else:
        success, output = run_command(f'cd {DASHBOARD_DIR} && git rev-parse --short HEAD')
    return output.strip() if success else "unknown"

def check_for_updates():
    """Check if updates are available from git"""
    if os.name == 'nt':
        run_command(f'cd "{DASHBOARD_DIR}" && git fetch')
        success, output = run_command(f'cd "{DASHBOARD_DIR}" && git rev-list HEAD...origin/main --count')
    else:
        run_command(f'cd {DASHBOARD_DIR} && git fetch')
        success, output = run_command(f'cd {DASHBOARD_DIR} && git rev-list HEAD...origin/main --count')
    
    try:
        count = int(output.strip())
        return count > 0
    except:
        return False

def do_update():
    """Pull latest updates from git"""
    if os.name == 'nt':
        return run_command(f'cd "{DASHBOARD_DIR}" && git pull')
    return run_command(f'cd {DASHBOARD_DIR} && git pull')

def restart_display():
    """Restart the dashboard display"""
    if os.name == 'nt':
        return True, "Simulated restart"
    
    # Kill and restart chromium
    run_command("pkill -f chromium")
    return True, "Display restarting..."

def reboot_system():
    """Reboot the Orange Pi"""
    if os.name == 'nt':
        return True, "Simulated reboot"
    return run_command("sudo reboot")

# ===== HTML TEMPLATE =====
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Dashboard Config</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0d1117;
            --bg-card: #161b22;
            --bg-input: #21262d;
            --border: #30363d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent-hover: #79b8ff;
            --success: #3fb950;
            --warning: #d29922;
            --danger: #f85149;
            --radius: 12px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 16px;
            padding-bottom: 100px;
        }

        .header {
            text-align: center;
            margin-bottom: 24px;
            padding: 20px 0;
            border-bottom: 1px solid var(--border);
        }

        .header h1 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(135deg, var(--accent), #a371f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header .subtitle {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .status-bar {
            display: flex;
            justify-content: center;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--text-secondary);
            background: var(--bg-card);
            padding: 8px 12px;
            border-radius: 20px;
            border: 1px solid var(--border);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
        }

        .status-dot.warning { background: var(--warning); }
        .status-dot.error { background: var(--danger); }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px;
            margin-bottom: 16px;
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .card-title {
            font-size: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card-icon {
            font-size: 20px;
        }

        .form-group {
            margin-bottom: 16px;
        }

        .form-group:last-child {
            margin-bottom: 0;
        }

        label {
            display: block;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }

        input[type="text"],
        input[type="password"],
        input[type="url"],
        input[type="number"],
        select {
            width: 100%;
            padding: 12px 14px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 15px;
            font-family: inherit;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.15);
        }

        input::placeholder {
            color: var(--text-secondary);
            opacity: 0.6;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 600;
            font-family: inherit;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
        }

        .btn-primary {
            background: var(--accent);
            color: #fff;
        }

        .btn-primary:hover {
            background: var(--accent-hover);
            transform: translateY(-1px);
        }

        .btn-primary:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: var(--bg-input);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }

        .btn-secondary:hover {
            background: var(--border);
        }

        .btn-success {
            background: var(--success);
            color: #fff;
        }

        .btn-warning {
            background: var(--warning);
            color: #000;
        }

        .btn-danger {
            background: var(--danger);
            color: #fff;
        }

        .btn-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .btn-group .btn {
            flex: 1;
            min-width: 120px;
        }

        .toggle-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }

        .toggle-container:last-child {
            border-bottom: none;
        }

        .toggle-label {
            font-size: 14px;
            font-weight: 500;
        }

        .toggle-desc {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 2px;
        }

        .toggle {
            position: relative;
            width: 48px;
            height: 28px;
            flex-shrink: 0;
        }

        .toggle input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .toggle-slider {
            position: absolute;
            cursor: pointer;
            inset: 0;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 14px;
            transition: 0.3s;
        }

        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 3px;
            bottom: 3px;
            background: var(--text-secondary);
            border-radius: 50%;
            transition: 0.3s;
        }

        .toggle input:checked + .toggle-slider {
            background: var(--accent);
            border-color: var(--accent);
        }

        .toggle input:checked + .toggle-slider:before {
            background: #fff;
            transform: translateX(20px);
        }

        .wifi-network {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 14px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: border-color 0.2s;
        }

        .wifi-network:hover {
            border-color: var(--accent);
        }

        .wifi-network.active {
            border-color: var(--success);
            background: rgba(63, 185, 80, 0.1);
        }

        .wifi-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .wifi-signal {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .alert {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .alert-success {
            background: rgba(63, 185, 80, 0.15);
            border: 1px solid var(--success);
            color: var(--success);
        }

        .alert-error {
            background: rgba(248, 81, 73, 0.15);
            border: 1px solid var(--danger);
            color: var(--danger);
        }

        .alert-info {
            background: rgba(88, 166, 255, 0.15);
            border: 1px solid var(--accent);
            color: var(--accent);
        }

        .hidden {
            display: none !important;
        }

        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid transparent;
            border-top-color: currentColor;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .nav-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            overflow-x: auto;
            padding-bottom: 4px;
        }

        .nav-tab {
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }

        .nav-tab:hover {
            color: var(--text-primary);
            background: var(--bg-card);
        }

        .nav-tab.active {
            color: var(--accent);
            background: var(--bg-card);
            border-color: var(--border);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .version-info {
            text-align: center;
            padding: 16px;
            color: var(--text-secondary);
            font-size: 12px;
        }

        .row {
            display: flex;
            gap: 12px;
        }

        .row > * {
            flex: 1;
        }

        @media (max-width: 400px) {
            .row {
                flex-direction: column;
            }
            
            .btn-group {
                flex-direction: column;
            }
            
            .btn-group .btn {
                width: 100%;
            }
        }

        /* Modal styles */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 16px;
        }

        .modal {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px;
            width: 100%;
            max-width: 400px;
        }

        .modal-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🍊 Dashboard Config</h1>
        <div class="subtitle">Orange Pi Health Monitor</div>
    </div>

    <div class="status-bar">
        <div class="status-item">
            <div class="status-dot {{ 'success' if wifi_connected else 'error' }}"></div>
            <span>{{ current_wifi or 'Not Connected' }}</span>
        </div>
        <div class="status-item">
            <span>📍 {{ ip_address }}</span>
        </div>
        <div class="status-item">
            <div class="status-dot {{ 'warning' if updates_available else 'success' }}"></div>
            <span>v{{ version }}</span>
        </div>
    </div>

    {% if message %}
    <div class="alert alert-{{ message_type }}">
        {{ message }}
    </div>
    {% endif %}

    <div class="nav-tabs">
        <button class="nav-tab active" onclick="showTab('wifi')">📶 WiFi</button>
        <button class="nav-tab" onclick="showTab('nightscout')">💉 Nightscout</button>
        <button class="nav-tab" onclick="showTab('supabase')">🗄️ Supabase</button>
        <button class="nav-tab" onclick="showTab('display')">🎨 Display</button>
        <button class="nav-tab" onclick="showTab('system')">⚙️ System</button>
    </div>

    <!-- WiFi Tab -->
    <div id="tab-wifi" class="tab-content active">
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">📶</span>
                    WiFi Networks
                </div>
                <button class="btn btn-secondary" style="width: auto; padding: 8px 12px;" onclick="refreshNetworks()">
                    🔄 Scan
                </button>
            </div>
            
            <div id="wifi-list">
                {% for network in wifi_networks %}
                <div class="wifi-network {{ 'active' if network.ssid == current_wifi else '' }}" 
                     onclick="selectNetwork('{{ network.ssid }}')">
                    <div class="wifi-info">
                        <span>{{ '🔒' if network.signal > 50 else '📶' }}</span>
                        <span>{{ network.ssid }}</span>
                    </div>
                    <span class="wifi-signal">{{ network.signal }}%</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">📡</span>
                    Hotspot Mode
                </div>
            </div>
            
            <div class="toggle-container">
                <div>
                    <div class="toggle-label">Enable Hotspot</div>
                    <div class="toggle-desc">Create "OrangePi-Setup" network for initial setup</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="hotspot-toggle" {{ 'checked' if hotspot_active else '' }}
                           onchange="toggleHotspot(this.checked)">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        </div>
    </div>

    <!-- Nightscout Tab -->
    <div id="tab-nightscout" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">💉</span>
                    Nightscout Configuration
                </div>
            </div>
            
            <form action="/save/nightscout" method="POST">
                <div class="form-group">
                    <label>Nightscout URL</label>
                    <input type="url" name="url" value="{{ config.nightscout.url }}"
                           placeholder="https://yoursite.herokuapp.com">
                </div>
                
                <div class="form-group">
                    <label>API Secret (optional)</label>
                    <input type="password" name="api_secret" value="{{ config.nightscout.api_secret }}"
                           placeholder="Leave blank if not required">
                </div>
                
                <div class="btn-group">
                    <button type="button" class="btn btn-secondary" onclick="testNightscout()">
                        🔍 Test Connection
                    </button>
                    <button type="submit" class="btn btn-primary">
                        💾 Save
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Supabase Tab -->
    <div id="tab-supabase" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">🗄️</span>
                    Supabase Configuration
                </div>
            </div>
            
            <form action="/save/supabase" method="POST">
                <div class="form-group">
                    <label>Supabase Project URL</label>
                    <input type="url" name="url" value="{{ config.supabase.url }}"
                           placeholder="https://xxxxx.supabase.co">
                </div>
                
                <div class="form-group">
                    <label>Anon/Public Key</label>
                    <input type="password" name="anon_key" value="{{ config.supabase.anon_key }}"
                           placeholder="eyJhbGciOiJIUzI1NiIs...">
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label>Reminders Table</label>
                        <input type="text" name="reminders_table" 
                               value="{{ config.supabase.reminders_table }}"
                               placeholder="reminders">
                    </div>
                    
                    <div class="form-group">
                        <label>Motivational Table</label>
                        <input type="text" name="motivational_table" 
                               value="{{ config.supabase.motivational_table }}"
                               placeholder="motivational_messages">
                    </div>
                </div>
                
                <div class="btn-group">
                    <button type="button" class="btn btn-secondary" onclick="testSupabase()">
                        🔍 Test Connection
                    </button>
                    <button type="submit" class="btn btn-primary">
                        💾 Save
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Display Tab -->
    <div id="tab-display" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">🎨</span>
                    Display Settings
                </div>
            </div>
            
            <form action="/save/display" method="POST">
                <div class="form-group">
                    <label>Timezone</label>
                    <select name="timezone">
                        <option value="America/Denver" {{ 'selected' if config.display.timezone == 'America/Denver' else '' }}>
                            Mountain Time (Denver)
                        </option>
                        <option value="America/New_York" {{ 'selected' if config.display.timezone == 'America/New_York' else '' }}>
                            Eastern Time (New York)
                        </option>
                        <option value="America/Chicago" {{ 'selected' if config.display.timezone == 'America/Chicago' else '' }}>
                            Central Time (Chicago)
                        </option>
                        <option value="America/Los_Angeles" {{ 'selected' if config.display.timezone == 'America/Los_Angeles' else '' }}>
                            Pacific Time (Los Angeles)
                        </option>
                        <option value="America/Phoenix" {{ 'selected' if config.display.timezone == 'America/Phoenix' else '' }}>
                            Arizona (Phoenix)
                        </option>
                    </select>
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label>Day Mode Start (hour)</label>
                        <input type="number" name="day_mode_start" min="0" max="23"
                               value="{{ config.display.day_mode_start }}">
                    </div>
                    
                    <div class="form-group">
                        <label>Day Mode End (hour)</label>
                        <input type="number" name="day_mode_end" min="0" max="23"
                               value="{{ config.display.day_mode_end }}">
                    </div>
                </div>
                
                <div class="row">
                    <div class="form-group">
                        <label>Motivational Start (hour)</label>
                        <input type="number" name="motivational_hours_start" min="0" max="23"
                               value="{{ config.display.motivational_hours_start }}">
                    </div>
                    
                    <div class="form-group">
                        <label>Motivational End (hour)</label>
                        <input type="number" name="motivational_hours_end" min="0" max="23"
                               value="{{ config.display.motivational_hours_end }}">
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary">
                    💾 Save Display Settings
                </button>
            </form>
        </div>
    </div>

    <!-- System Tab -->
    <div id="tab-system" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">🔄</span>
                    Updates
                </div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: var(--text-secondary);">Current Version</span>
                    <span style="font-family: monospace;">{{ version }}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary);">Updates Available</span>
                    <span style="color: {{ 'var(--warning)' if updates_available else 'var(--success)' }};">
                        {{ 'Yes' if updates_available else 'Up to date' }}
                    </span>
                </div>
            </div>
            
            <div class="btn-group">
                <button class="btn btn-primary" onclick="doUpdate()">
                    ⬇️ Update Now
                </button>
                <button class="btn btn-secondary" onclick="restartDisplay()">
                    🔄 Restart Display
                </button>
            </div>
            
            <div class="toggle-container" style="margin-top: 16px;">
                <div>
                    <div class="toggle-label">Auto-Update</div>
                    <div class="toggle-desc">Update daily at 7 AM Mountain Time</div>
                </div>
                <label class="toggle">
                    <input type="checkbox" id="auto-update-toggle" 
                           {{ 'checked' if config.system.auto_update else '' }}
                           onchange="toggleAutoUpdate(this.checked)">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">⚙️</span>
                    System Actions
                </div>
            </div>
            
            <div class="btn-group">
                <button class="btn btn-warning" onclick="if(confirm('Reboot the Orange Pi?')) rebootSystem()">
                    🔄 Reboot System
                </button>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">📋</span>
                    System Information
                </div>
            </div>
            
            <div style="font-size: 13px; color: var(--text-secondary);">
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border);">
                    <span>Hostname</span>
                    <span style="color: var(--text-primary);">{{ hostname }}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border);">
                    <span>IP Address</span>
                    <span style="color: var(--text-primary);">{{ ip_address }}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                    <span>Config Port</span>
                    <span style="color: var(--text-primary);">3000</span>
                </div>
            </div>
        </div>
    </div>

    <!-- WiFi Password Modal -->
    <div id="wifi-modal" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-title">Connect to <span id="modal-ssid"></span></div>
            <form action="/wifi/connect" method="POST" id="wifi-form">
                <input type="hidden" name="ssid" id="modal-ssid-input">
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" placeholder="Enter WiFi password" required>
                </div>
                <div class="btn-group">
                    <button type="button" class="btn btn-secondary" onclick="closeWifiModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Connect</button>
                </div>
            </form>
        </div>
    </div>

    <div class="version-info">
        Dashboard Config Server v1.0<br>
        Mountain Time: {{ current_time }}
    </div>

    <script>
        // Tab navigation
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }

        // WiFi functions
        function selectNetwork(ssid) {
            document.getElementById('modal-ssid').textContent = ssid;
            document.getElementById('modal-ssid-input').value = ssid;
            document.getElementById('wifi-modal').classList.remove('hidden');
        }

        function closeWifiModal() {
            document.getElementById('wifi-modal').classList.add('hidden');
        }

        function refreshNetworks() {
            location.reload();
        }

        // Hotspot toggle
        function toggleHotspot(enabled) {
            fetch('/hotspot/' + (enabled ? 'enable' : 'disable'), { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (!data.success) {
                        alert('Error: ' + data.message);
                        document.getElementById('hotspot-toggle').checked = !enabled;
                    }
                });
        }

        // Test connections
        function testNightscout() {
            const url = document.querySelector('input[name="url"]').value;
            if (!url) {
                alert('Please enter a Nightscout URL first');
                return;
            }
            
            fetch('/test/nightscout?url=' + encodeURIComponent(url))
                .then(r => r.json())
                .then(data => {
                    alert(data.success ? '✅ Connection successful!' : '❌ Connection failed: ' + data.message);
                });
        }

        function testSupabase() {
            alert('Supabase test coming soon');
        }

        // System functions
        function doUpdate() {
            if (!confirm('Pull latest updates from GitHub?')) return;
            
            fetch('/update', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert(data.success ? '✅ Update successful! Restarting display...' : '❌ Update failed: ' + data.message);
                    if (data.success) {
                        setTimeout(() => location.reload(), 2000);
                    }
                });
        }

        function restartDisplay() {
            fetch('/restart-display', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert(data.success ? '✅ Display restarting...' : '❌ Error: ' + data.message);
                });
        }

        function rebootSystem() {
            fetch('/reboot', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('🔄 System rebooting... Page will reload in 30 seconds.');
                        setTimeout(() => location.reload(), 30000);
                    }
                });
        }

        function toggleAutoUpdate(enabled) {
            fetch('/save/auto-update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: enabled })
            });
        }

        // Close modal on outside click
        document.getElementById('wifi-modal').addEventListener('click', function(e) {
            if (e.target === this) closeWifiModal();
        });
    </script>
</body>
</html>
'''

# ===== ROUTES =====

@app.route('/')
def index():
    """Main configuration page"""
    config = load_config()
    
    # Get current time in Mountain Time
    from datetime import timezone, timedelta
    mt = timezone(timedelta(hours=-7))
    current_time = datetime.now(mt).strftime('%I:%M %p')
    
    return render_template_string(
        HTML_TEMPLATE,
        config=config,
        wifi_networks=get_wifi_networks(),
        current_wifi=get_current_wifi(),
        wifi_connected=get_current_wifi() is not None,
        hotspot_active=is_hotspot_active(),
        ip_address=get_ip_address(),
        hostname=get_hostname(),
        version=get_git_version(),
        updates_available=check_for_updates(),
        current_time=current_time,
        message=request.args.get('message'),
        message_type=request.args.get('type', 'info')
    )

@app.route('/api/config')
def api_config():
    """Return configuration as JSON for dashboard"""
    config = load_config()
    return jsonify(config)

@app.route('/save/nightscout', methods=['POST'])
def save_nightscout():
    """Save Nightscout configuration"""
    config = load_config()
    config['nightscout']['url'] = request.form.get('url', '').strip()
    config['nightscout']['api_secret'] = request.form.get('api_secret', '').strip()
    
    if save_config(config):
        return redirect(url_for('index', message='Nightscout settings saved!', type='success'))
    return redirect(url_for('index', message='Error saving settings', type='error'))

@app.route('/save/supabase', methods=['POST'])
def save_supabase():
    """Save Supabase configuration"""
    config = load_config()
    config['supabase']['url'] = request.form.get('url', '').strip()
    config['supabase']['anon_key'] = request.form.get('anon_key', '').strip()
    config['supabase']['reminders_table'] = request.form.get('reminders_table', 'reminders').strip()
    config['supabase']['motivational_table'] = request.form.get('motivational_table', 'motivational_messages').strip()
    
    if save_config(config):
        return redirect(url_for('index', message='Supabase settings saved!', type='success'))
    return redirect(url_for('index', message='Error saving settings', type='error'))

@app.route('/save/display', methods=['POST'])
def save_display():
    """Save display configuration"""
    config = load_config()
    config['display']['timezone'] = request.form.get('timezone', 'America/Denver')
    config['display']['day_mode_start'] = int(request.form.get('day_mode_start', 6))
    config['display']['day_mode_end'] = int(request.form.get('day_mode_end', 20))
    config['display']['motivational_hours_start'] = int(request.form.get('motivational_hours_start', 7))
    config['display']['motivational_hours_end'] = int(request.form.get('motivational_hours_end', 10))
    
    if save_config(config):
        return redirect(url_for('index', message='Display settings saved!', type='success'))
    return redirect(url_for('index', message='Error saving settings', type='error'))

@app.route('/save/auto-update', methods=['POST'])
def save_auto_update():
    """Toggle auto-update setting"""
    config = load_config()
    data = request.get_json()
    config['system']['auto_update'] = data.get('enabled', True)
    save_config(config)
    return jsonify({'success': True})

@app.route('/wifi/connect', methods=['POST'])
def wifi_connect():
    """Connect to a WiFi network"""
    ssid = request.form.get('ssid', '')
    password = request.form.get('password', '')
    
    if not ssid:
        return redirect(url_for('index', message='No network selected', type='error'))
    
    success, message = connect_wifi(ssid, password)
    if success:
        return redirect(url_for('index', message=f'Connected to {ssid}!', type='success'))
    return redirect(url_for('index', message=f'Failed to connect: {message}', type='error'))

@app.route('/hotspot/<action>', methods=['POST'])
def hotspot_action(action):
    """Enable or disable hotspot"""
    enable = action == 'enable'
    success, message = toggle_hotspot(enable)
    return jsonify({'success': success, 'message': message})

@app.route('/test/nightscout')
def test_nightscout():
    """Test Nightscout connection"""
    url = request.args.get('url', '')
    if not url:
        return jsonify({'success': False, 'message': 'No URL provided'})
    
    try:
        import urllib.request
        test_url = f"{url.rstrip('/')}/api/v1/status.json"
        req = urllib.request.Request(test_url, headers={'User-Agent': 'OrangePi-Dashboard'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': False, 'message': 'Unknown error'})

@app.route('/update', methods=['POST'])
def update():
    """Pull updates from git"""
    success, message = do_update()
    if success:
        restart_display()
    return jsonify({'success': success, 'message': message})

@app.route('/restart-display', methods=['POST'])
def restart_display_route():
    """Restart the display"""
    success, message = restart_display()
    return jsonify({'success': success, 'message': message})

@app.route('/reboot', methods=['POST'])
def reboot():
    """Reboot the system"""
    success, message = reboot_system()
    return jsonify({'success': success, 'message': message})

# ===== NIGHTSCOUT PROXY (avoids CORS issues) =====
@app.route('/api/nightscout/entries')
def nightscout_entries():
    """Proxy Nightscout entries to avoid CORS issues"""
    config = load_config()
    ns_url = config.get('nightscout', {}).get('url', '')
    ns_secret = config.get('nightscout', {}).get('api_secret', '')
    
    if not ns_url:
        return jsonify({'error': 'Nightscout URL not configured'}), 400
    
    try:
        import urllib.request
        count = request.args.get('count', '1')
        api_url = f"{ns_url.rstrip('/')}/api/v1/entries.json?count={count}"
        
        req = urllib.request.Request(api_url)
        req.add_header('api-secret', ns_secret)
        req.add_header('User-Agent', 'OrangePi-Dashboard')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode('utf-8')
            return app.response_class(response=data, status=200, mimetype='application/json')
    except Exception as e:
        logger.error(f"Nightscout proxy error: {e}")
        return jsonify({'error': str(e)}), 500

# ===== MAIN =====
if __name__ == '__main__':
    # Ensure config directory exists
    ensure_config_dir()
    
    # Create default config if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        logger.info(f"Created default config at {CONFIG_FILE}")
    
    # Run the server
    logger.info(f"Starting config server on port {DEFAULT_PORT}")
    logger.info(f"Access at http://localhost:{DEFAULT_PORT} or http://orangepi.local:{DEFAULT_PORT}")
    
    app.run(host='0.0.0.0', port=DEFAULT_PORT, debug=False)

