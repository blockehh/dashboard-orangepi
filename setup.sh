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
    unclutter \
    xdotool

# Install Python packages
echo "[3/10] Installing Python packages..."
pip3 install flask --quiet --break-system-packages 2>/dev/null || pip3 install flask --quiet

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
    cat > $DASHBOARD_DIR/dashboard.html <<EOF
<!DOCTYPE html>
<html>
<head><title>Dashboard Setup</title></head>
<body style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;background:#0f0f14;color:#e8e8f0;">
    <div style="text-align:center;">
        <h1>Dashboard Setup Complete!</h1>
        <p>Clone your repository to: $DASHBOARD_DIR</p>
        <p>Or access config at: http://orangepi.local:3000</p>
    </div>
</body>
</html>
EOF
    chown $ACTUAL_USER:$ACTUAL_USER $DASHBOARD_DIR/dashboard.html
fi

# Create configuration directory
echo "[6/10] Creating configuration..."
CONFIG_DIR="/etc/dashboard"
mkdir -p $CONFIG_DIR

cat > $CONFIG_DIR/config.json <<EOF
{
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
        "auto_update": true,
        "update_time": "07:00",
        "hostname": "orangepi"
    }
}
EOF

chmod 644 $CONFIG_DIR/config.json

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

# The config-server.py should already be in the repo, make it executable
echo "[9/10] Setting up configuration web server..."
if [ -f "$DASHBOARD_DIR/config-server.py" ]; then
    chmod +x $DASHBOARD_DIR/config-server.py
    echo "Using config-server.py from repository"
else
    echo "Warning: config-server.py not found in repository"
fi

# Create systemd service for config server
cat > /etc/systemd/system/dashboard-config.service <<EOF
[Unit]
Description=Dashboard Configuration Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dashboard
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 /opt/dashboard/config-server.py
Restart=always
RestartSec=5

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

# Wait for network
sleep 5

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

# Enable and start services
systemctl daemon-reload
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
echo "4. Configure Nightscout and Supabase via web GUI"
echo ""
echo "Dashboard location: $DASHBOARD_DIR"
echo "Config location: $CONFIG_DIR/config.json"
echo ""
echo "Daily updates: 7 AM Mountain Time"
echo "Manual update: Use web interface"
echo ""
echo "Rebooting in 10 seconds... (Ctrl+C to cancel)"
sleep 10
reboot
