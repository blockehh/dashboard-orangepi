# Orange Pi Dashboard - Complete Setup Guide

A beautiful, health-focused dashboard for Orange Pi that displays time, Dexcom glucose readings from Nightscout, reminders, and motivational text.

## 🎯 What You'll Get

- **Auto-starting kiosk display** - Boots directly to your dashboard
- **Web-based configuration** - Change WiFi, Nightscout settings, etc. from your phone
- **Automatic updates** - Pulls from GitHub every morning at 7 AM
- **Manual update button** - Update immediately when you're developing
- **Zero maintenance** - Set it and forget it

---

## 📦 Hardware Requirements

- **Orange Pi Zero 2** (or similar model)
- **microSD card** (16GB+ recommended, Class 10)
- **7-inch HDMI display**
- **Power supply** (5V 2A minimum)
- **WiFi connection**

---

## 🚀 Quick Start (Complete Setup)

### Step 1: Flash Armbian to SD Card

1. **Download Armbian**
   - Go to: https://www.armbian.com/orange-pi-zero-2/
   - Download the "Armbian Bookworm" image (Debian-based)

2. **Flash to SD Card**
   - Download [Balena Etcher](https://www.balena.io/etcher/)
   - Insert microSD card into your computer
   - Open Etcher → Select Armbian image → Select SD card → Flash!
   - Wait ~5 minutes for completion

3. **Insert SD Card**
   - Put the flashed microSD card into your Orange Pi
   - Connect HDMI display, keyboard (for first boot)
   - Connect power

### Step 2: First Boot Setup

1. **Boot Orange Pi**
   - First boot takes ~2 minutes
   - You'll see Armbian setup wizard

2. **Initial Configuration**
   - Default credentials: `root` / `1234`
   - You'll be forced to change password on first login
   - Create a new user when prompted (e.g., `pi`)
   - Set timezone to **America/Denver** (Mountain Time)

3. **Connect to WiFi**
   ```bash
   nmtui
   ```
   - Select "Activate a connection"
   - Choose your WiFi network
   - Enter password
   - Exit

4. **Get IP Address** (optional, for SSH)
   ```bash
   ip addr show
   ```
   - Note the IP address (e.g., 192.168.1.100)

### Step 3: Run Installation Script

**Option A: Via SSH** (recommended)
```bash
# From your computer
ssh root@orangepi.local
# Or use the IP: ssh root@192.168.1.100

# Download and run setup script
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/setup.sh
chmod +x setup.sh
sudo bash setup.sh
```

**Option B: Directly on Orange Pi**
```bash
# If you have keyboard/monitor connected
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/setup.sh
chmod +x setup.sh
sudo bash setup.sh
```

The script will:
- ✅ Update system packages
- ✅ Install Chromium browser
- ✅ Set up kiosk mode (auto-start)
- ✅ Install configuration web server
- ✅ Set up auto-updates from GitHub
- ✅ Configure auto-login
- ✅ Disable screen blanking

**Installation takes ~10 minutes**

### Step 4: Reboot

The setup script will automatically reboot after completion. After reboot:
- Dashboard launches automatically
- Chromium opens in fullscreen kiosk mode
- Configuration server starts on port 3000

---

## 🎛️ Configuration Interface

Access the web interface from **any device on your network**:

```
http://orangepi.local:3000
```

Or use the IP address:
```
http://192.168.1.100:3000
```

### Features Available:

**System Information**
- Device hostname
- IP address
- Current version

**Updates**
- View current version (git commit)
- See if updates are available
- **"Update Now"** button for instant updates
- "Restart Display" to refresh browser
- Auto-updates daily at 7 AM Mountain Time

**Nightscout Configuration**
- Set your Nightscout URL
- Add API secret (if required)
- Test connection

**Display Settings**
- Configure day mode hours (default 6 AM - 8 PM)
- Customize motivational messages

**System Actions**
- Reboot device
- View update logs
- Restart display

---

## 📁 GitHub Repository Structure

Your repository should look like this:

```
your-dashboard-repo/
├── dashboard.html          # Main dashboard file
├── setup.sh               # Installation script
├── README.md              # This file
└── .gitignore             # Git ignore file
```

### Example `.gitignore`:

```
# System files
.DS_Store
Thumbs.db

# Logs
*.log

# Config (don't commit sensitive data)
config.json
```

---

## 🔄 Update Workflow

### Automatic Updates (Daily)

Updates run automatically every morning at **7 AM Mountain Time**:
- Script checks GitHub for changes
- Pulls new commits if available
- Refreshes browser automatically
- Logs results to `/var/log/dashboard-update.log`

**Why 7 AM?** If an update breaks something, you'll notice during the day (not wake up to a bright broken screen at 3 AM!)

### Manual Updates (While Developing)

When you're actively working on the dashboard:

1. **Make changes on your computer**
   ```bash
   git add dashboard.html
   git commit -m "Updated clock size"
   git push
   ```

2. **Update Orange Pi instantly**
   - Open `http://orangepi.local:3000`
   - Click **"Update Now"**
   - Dashboard refreshes automatically

---

## 🌐 Changing WiFi

### Method 1: Via Web Interface (Coming Soon)
- Navigate to web interface
- Click "WiFi Settings"
- Select network and enter password

### Method 2: Via SSH
```bash
ssh root@orangepi.local
nmtui
```
- Select "Activate a connection"
- Choose new network
- Enter password

### Method 3: If Completely Offline
- Connect keyboard and monitor
- Press `Ctrl+Alt+F1` to switch to terminal
- Login as root
- Run `nmtui` to configure WiFi

---

## 🔧 Troubleshooting

### Dashboard Not Loading

1. **Check if Chromium is running:**
   ```bash
   ps aux | grep chromium
   ```

2. **Restart display:**
   ```bash
   pkill chromium
   # It will auto-restart
   ```

3. **Check dashboard file:**
   ```bash
   ls -la /opt/dashboard/dashboard.html
   ```

### Config Interface Not Accessible

1. **Check if service is running:**
   ```bash
   systemctl status dashboard-config
   ```

2. **Restart service:**
   ```bash
   systemctl restart dashboard-config
   ```

3. **View logs:**
   ```bash
   journalctl -u dashboard-config -f
   ```

### Updates Not Working

1. **Check update logs:**
   ```bash
   tail -f /var/log/dashboard-update.log
   ```

2. **Test update manually:**
   ```bash
   /usr/local/bin/dashboard-update.sh
   ```

3. **Check git repository:**
   ```bash
   cd /opt/dashboard
   git status
   git remote -v
   ```

### Screen Blanking

If screen goes black after inactivity:
```bash
# Check if xset is configured
cat ~/.config/openbox/autostart

# Manually disable blanking
DISPLAY=:0 xset s off
DISPLAY=:0 xset -dpms
```

---

## 📊 Nightscout Integration

### Setting Up Nightscout Connection

1. **Get your Nightscout URL:**
   - Example: `https://yourname.herokuapp.com`
   - Or your custom domain

2. **Configure via web interface:**
   - Go to `http://orangepi.local:3000`
   - Enter Nightscout URL
   - Add API secret (if required)
   - Save configuration

3. **Dashboard will:**
   - Fetch glucose data every 5 minutes
   - Display current value with trend arrow
   - Color-code based on range (green/yellow/red)
   - Show time since last reading

### Nightscout API Details

The dashboard makes requests to:
```
GET https://your-nightscout.com/api/v1/entries.json?count=1
```

Optional authentication:
```javascript
headers: {
  'API-SECRET': 'your-api-secret-hash'
}
```

---

## 🎨 Customization

### Changing Colors

Edit `dashboard.html` CSS variables:

```css
:root {
    --bg-primary: #0f0f14;
    --accent-primary: #6b9bd1;
    --glucose-good: #5fb884;
    /* ... */
}
```

### Adjusting Font Sizes

```css
.clock {
    font-size: 120px;  /* Change this */
}

.dexcom-value {
    font-size: 72px;   /* And this */
}
```

### Changing Update Schedule

Edit cron job:
```bash
sudo nano /etc/cron.d/dashboard-update
```

Change time (uses 24-hour format):
```
0 7 * * *    # 7 AM
0 9 * * *    # 9 AM
0 18 * * *   # 6 PM
```

---

## 🔐 Security Notes

- **Config interface runs on port 3000** - only accessible on local network
- **No authentication** - assumes trusted network (home WiFi)
- **API secrets stored** in `/etc/dashboard/config.json`
- **File permissions** - config files owned by root

For public networks, consider:
- Adding password protection to Flask app
- Using HTTPS with self-signed cert
- Restricting to localhost only

---

## 📈 Performance

**Typical resource usage:**
- **RAM**: ~200MB (Chromium) + ~50MB (config server)
- **CPU**: <5% idle, ~10% during updates
- **Disk**: ~1GB total installation
- **Network**: ~1KB every 5 min (Nightscout checks)

**Boot time:**
- Cold boot to dashboard: ~30 seconds
- Reboot: ~20 seconds

---

## 🛠️ Advanced Configuration

### Running Commands on Boot

Edit Openbox autostart:
```bash
nano ~/.config/openbox/autostart
```

### Changing Display Resolution

```bash
# List available modes
xrandr

# Set resolution
xrandr --output HDMI-1 --mode 1024x600
```

### Disabling Automatic Updates

```bash
# Remove cron job
sudo rm /etc/cron.d/dashboard-update

# Or disable in web interface (config.json)
{
  "auto_update": false
}
```

### Viewing System Logs

```bash
# Config server logs
journalctl -u dashboard-config -f

# Update logs
tail -f /var/log/dashboard-update.log

# System logs
journalctl -f
```

---

## 🆘 Support & Issues

### Common Issues

1. **"Cannot connect to orangepi.local"**
   - Use IP address instead
   - Check if mDNS is working: `ping orangepi.local`

2. **Dashboard shows blank screen**
   - Check if file exists: `ls /opt/dashboard/dashboard.html`
   - View browser console: Connect keyboard, press F12

3. **Git updates failing**
   - Check repository: `cd /opt/dashboard && git status`
   - Check network: `ping github.com`
   - Check logs: `tail /var/log/dashboard-update.log`

### Getting Help

- Check update logs: `/var/log/dashboard-update.log`
- Check service status: `systemctl status dashboard-config`
- SSH in and investigate: `ssh root@orangepi.local`

---

## 📝 License

This project is provided as-is for personal use.

---

## 🎉 Credits

Built with:
- Armbian OS
- Chromium Browser
- Flask (Python)
- Nightscout API
- Love ❤️
