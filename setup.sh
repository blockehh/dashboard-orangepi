#!/bin/bash

# Orange Pi Dashboard - One-Command Setup Script
# Run this after fresh Armbian install: sudo bash setup.sh

set -e  # Exit on any error

echo "================================================"
echo "  Orange Pi Dashboard Setup"
echo "  This will install everything you need"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo bash setup.sh)"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo "Setting up for user: $ACTUAL_USER"
echo "Home directory: $USER_HOME"
echo ""

# Update system
echo "[1/10] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# Install required packages
echo "[2/10] Installing required packages..."
apt-get install -y -qq \
    chromium \
    chromium-driver \
    xorg \
    openbox \
    lightdm \
    git \
    python3 \
    python3-pip \
    python3-flask \
    network-manager \
    unclutter

# Install Python packages
echo "[3/10] Installing Python packages..."
pip3 install flask gitpython requests --quiet

# Create dashboard directory
echo "[4/10] Creating dashboard directory..."
DASHBOARD_DIR="/opt/dashboard"
mkdir -p $DASHBOARD_DIR
chown $ACTUAL_USER:$ACTUAL_USER $DASHBOARD_DIR

# Clone or setup your dashboard repository
echo "[5/10] Setting up dashboard files..."
read -p "Enter your GitHub repository URL (or press Enter to skip): " REPO_URL

if [ -n "$REPO_URL" ]; then
    cd $DASHBOARD_DIR
    sudo -u $ACTUAL_USER git clone $REPO_URL .
    echo "Repository cloned successfully!"
else
    echo "Skipping repository clone - you can add files manually to $DASHBOARD_DIR"
    # Create a basic index.html placeholder
    cat > $DASHBOARD_DIR/index.html <<EOF
<!DOCTYPE html>
<html>
<head><title>Dashboard Setup</title></head>
<body style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
    <div style="text-align:center;">
        <h1>Dashboard Setup Complete!</h1>
        <p>Add your dashboard.html file to: $DASHBOARD_DIR</p>
        <p>Access config at: http://orangepi.local:3000</p>
    </div>
</body>
</html>
EOF
    chown $ACTUAL_USER:$ACTUAL_USER $DASHBOARD_DIR/index.html
fi

# Create configuration directory
echo "[6/10] Creating configuration..."
CONFIG_DIR="/etc/dashboard"
mkdir -p $CONFIG_DIR

cat > $CONFIG_DIR/config.json <<EOF
{
    "nightscout_url": "",
    "nightscout_api_secret": "",
    "auto_update": true,
    "update_time": "07:00",
    "timezone": "America/Denver",
    "day_mode_start": 6,
    "day_mode_end": 20
}
EOF

# Create auto-update script
echo "[7/10] Creating auto-update script..."
cat > /usr/local/bin/dashboard-update.sh <<'EOF'
#!/bin/bash

DASHBOARD_DIR="/opt/dashboard"
LOG_FILE="/var/log/dashboard-update.log"

echo "$(date): Starting update check..." >> $LOG_FILE

if [ -d "$DASHBOARD_DIR/.git" ]; then
    cd $DASHBOARD_DIR
    
    # Fetch latest changes
    git fetch origin main >> $LOG_FILE 2>&1
    
    # Check if there are updates
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "$(date): Updates found, pulling changes..." >> $LOG_FILE
        git pull origin main >> $LOG_FILE 2>&1
        
        # Refresh browser (find and reload Chromium)
        DISPLAY=:0 xdotool search --class chromium key F5 >> $LOG_FILE 2>&1
        
        echo "$(date): Update completed successfully" >> $LOG_FILE
    else
        echo "$(date): No updates available" >> $LOG_FILE
    fi
else
    echo "$(date): Not a git repository, skipping update" >> $LOG_FILE
fi
EOF

chmod +x /usr/local/bin/dashboard-update.sh

# Create cron job for daily updates at 7 AM Mountain Time
echo "[8/10] Setting up automatic updates..."
cat > /etc/cron.d/dashboard-update <<EOF
# Update dashboard daily at 7 AM Mountain Time
0 7 * * * root TZ=America/Denver /usr/local/bin/dashboard-update.sh
EOF

# Create config web server
echo "[9/10] Creating configuration web server..."
cat > /opt/dashboard/config-server.py <<'EOF'
#!/usr/bin/env python3

from flask import Flask, render_template_string, request, jsonify
import json
import os
import subprocess
import socket

app = Flask(__name__)
CONFIG_FILE = '/etc/dashboard/config.json'
DASHBOARD_DIR = '/opt/dashboard'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_git_status():
    try:
        os.chdir(DASHBOARD_DIR)
        current = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
        
        # Check for updates
        subprocess.run(['git', 'fetch', 'origin'], capture_output=True)
        local = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        remote = subprocess.check_output(['git', 'rev-parse', 'origin/main']).decode().strip()
        
        updates_available = local != remote
        
        return {
            'commit': current,
            'branch': branch,
            'updates_available': updates_available
        }
    except:
        return {'commit': 'N/A', 'branch': 'N/A', 'updates_available': False}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Configuration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #1a1a2e; margin-bottom: 30px; }
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .card h2 { 
            color: #4a7ba7;
            margin-bottom: 16px;
            font-size: 18px;
        }
        .form-group { margin-bottom: 16px; }
        label {
            display: block;
            margin-bottom: 6px;
            color: #5a5a6a;
            font-weight: 500;
            font-size: 14px;
        }
        input, select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #e4e5e8;
            border-radius: 6px;
            font-size: 14px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #4a7ba7;
        }
        button {
            background: #4a7ba7;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 14px;
        }
        button:hover { background: #3d6589; }
        button.secondary {
            background: #6b5b95;
        }
        button.secondary:hover { background: #584a7a; }
        .status { 
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 12px;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .status.warning { background: #fff3cd; color: #856404; }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .info-row:last-child { border-bottom: none; }
        .info-label { color: #8a8a9a; font-size: 13px; }
        .info-value { font-weight: 500; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎛️ Dashboard Configuration</h1>
        
        <!-- System Info -->
        <div class="card">
            <h2>System Information</h2>
            <div class="info-row">
                <span class="info-label">Device</span>
                <span class="info-value">Orange Pi Zero 2</span>
            </div>
            <div class="info-row">
                <span class="info-label">Hostname</span>
                <span class="info-value">{{ hostname }}</span>
            </div>
            <div class="info-row">
                <span class="info-label">IP Address</span>
                <span class="info-value">{{ ip_address }}</span>
            </div>
        </div>

        <!-- Git Status -->
        <div class="card">
            <h2>Updates</h2>
            <div class="info-row">
                <span class="info-label">Current Version</span>
                <span class="info-value">{{ git_status.commit }}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Branch</span>
                <span class="info-value">{{ git_status.branch }}</span>
            </div>
            {% if git_status.updates_available %}
            <div class="status warning">Updates available!</div>
            {% else %}
            <div class="status success">Up to date ✓</div>
            {% endif %}
            <button onclick="updateNow()">Update Now</button>
            <button class="secondary" onclick="restartDisplay()">Restart Display</button>
        </div>

        <!-- Nightscout Config -->
        <div class="card">
            <h2>Nightscout Configuration</h2>
            <form onsubmit="saveConfig(event)">
                <div class="form-group">
                    <label>Nightscout URL</label>
                    <input type="url" name="nightscout_url" value="{{ config.nightscout_url }}" 
                           placeholder="https://yourname.herokuapp.com">
                </div>
                <div class="form-group">
                    <label>API Secret (optional)</label>
                    <input type="password" name="nightscout_api_secret" value="{{ config.nightscout_api_secret }}">
                </div>
                <button type="submit">Save Configuration</button>
            </form>
        </div>

        <!-- Display Settings -->
        <div class="card">
            <h2>Display Settings</h2>
            <form onsubmit="saveConfig(event)">
                <div class="form-group">
                    <label>Day Mode Start (Hour)</label>
                    <input type="number" name="day_mode_start" value="{{ config.day_mode_start }}" min="0" max="23">
                </div>
                <div class="form-group">
                    <label>Day Mode End (Hour)</label>
                    <input type="number" name="day_mode_end" value="{{ config.day_mode_end }}" min="0" max="23">
                </div>
                <button type="submit">Save Settings</button>
            </form>
        </div>

        <!-- System Actions -->
        <div class="card">
            <h2>System Actions</h2>
            <button onclick="rebootDevice()">Reboot Device</button>
            <button class="secondary" onclick="viewLogs()">View Update Logs</button>
        </div>
    </div>

    <script>
        function saveConfig(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const config = Object.fromEntries(formData);
            
            fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            }).then(r => r.json()).then(data => {
                alert(data.message);
                location.reload();
            });
        }

        function updateNow() {
            if (confirm('Update dashboard now?')) {
                fetch('/api/update', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => alert(data.message));
            }
        }

        function restartDisplay() {
            if (confirm('Restart the dashboard display?')) {
                fetch('/api/restart-display', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => alert(data.message));
            }
        }

        function rebootDevice() {
            if (confirm('Reboot the entire device? This will take ~30 seconds.')) {
                fetch('/api/reboot', {method: 'POST'});
                alert('Device is rebooting...');
            }
        }

        function viewLogs() {
            window.open('/api/logs', '_blank');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    config = load_config()
    git_status = get_git_status()
    hostname = socket.gethostname()
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        ip_address = 'N/A'
    
    return render_template_string(HTML_TEMPLATE, 
                                config=config, 
                                git_status=git_status,
                                hostname=hostname,
                                ip_address=ip_address)

@app.route('/api/config', methods=['POST'])
def update_config():
    config = load_config()
    new_config = request.json
    config.update(new_config)
    save_config(config)
    return jsonify({'message': 'Configuration saved successfully!'})

@app.route('/api/update', methods=['POST'])
def update_now():
    result = subprocess.run(['/usr/local/bin/dashboard-update.sh'], capture_output=True)
    return jsonify({'message': 'Update completed! Check logs for details.'})

@app.route('/api/restart-display', methods=['POST'])
def restart_display():
    subprocess.run(['pkill', '-f', 'chromium'])
    return jsonify({'message': 'Display restarting...'})

@app.route('/api/reboot', methods=['POST'])
def reboot():
    subprocess.Popen(['reboot'])
    return jsonify({'message': 'Rebooting...'})

@app.route('/api/logs')
def view_logs():
    try:
        with open('/var/log/dashboard-update.log', 'r') as f:
            logs = f.read()
        return f'<pre>{logs}</pre>'
    except:
        return '<pre>No logs available</pre>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
EOF

chmod +x /opt/dashboard/config-server.py

# Create systemd service for config server
cat > /etc/systemd/system/dashboard-config.service <<EOF
[Unit]
Description=Dashboard Configuration Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dashboard
ExecStart=/usr/bin/python3 /opt/dashboard/config-server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create Openbox autostart for kiosk mode
echo "[10/10] Setting up kiosk mode..."
mkdir -p $USER_HOME/.config/openbox
cat > $USER_HOME/.config/openbox/autostart <<EOF
# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Hide cursor after 1 second of inactivity
unclutter -idle 1 &

# Start Chromium in kiosk mode
chromium --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble --check-for-update-interval=31536000 file:///opt/dashboard/dashboard.html &
EOF

chown -R $ACTUAL_USER:$ACTUAL_USER $USER_HOME/.config

# Enable auto-login
mkdir -p /etc/lightdm/lightdm.conf.d
cat > /etc/lightdm/lightdm.conf.d/autologin.conf <<EOF
[Seat:*]
autologin-user=$ACTUAL_USER
autologin-user-timeout=0
user-session=openbox
EOF

# Enable services
systemctl enable lightdm
systemctl enable dashboard-config
systemctl start dashboard-config

echo ""
echo "================================================"
echo "  Installation Complete! 🎉"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Reboot: sudo reboot"
echo "2. Dashboard will auto-start on boot"
echo "3. Access config at: http://orangepi.local:3000"
echo "4. Add your dashboard.html to: $DASHBOARD_DIR"
echo ""
echo "Daily updates: 7 AM Mountain Time"
echo "Manual update: Use web interface"
echo ""
echo "Rebooting in 10 seconds... (Ctrl+C to cancel)"
sleep 10
reboot
