# 🚀 Quick Start Guide

## What You Have

You now have everything you need to turn your Orange Pi into a professional dashboard display:

✅ **dashboard.html** - The 7" optimized display with Nightscout integration
✅ **setup.sh** - One-command installer that sets up everything
✅ **README.md** - Complete documentation  
✅ **.gitignore** - For your GitHub repository
✅ **nightscout-integration.js** - Reference code (already integrated in dashboard.html)

---

## Setup in 5 Steps

### 1️⃣ Create GitHub Repository

```bash
# On your computer
mkdir dashboard-orangepi
cd dashboard-orangepi
git init
# Copy all files into this directory
git add .
git commit -m "Initial dashboard setup"
git remote add origin https://github.com/YOUR_USERNAME/dashboard-orangepi.git
git push -u origin main
```

### 2️⃣ Flash Armbian to SD Card

1. Download Armbian from: https://www.armbian.com/orange-pi-zero-2/
2. Use Balena Etcher to flash to SD card
3. Insert into Orange Pi and boot

### 3️⃣ Connect via SSH

```bash
# From your computer
ssh root@orangepi.local
# Password: 1234 (will force change)

# Set timezone during setup
# Choose: America/Denver
```

### 4️⃣ Run Setup Script

```bash
# On Orange Pi
wget https://raw.githubusercontent.com/YOUR_USERNAME/dashboard-orangepi/main/setup.sh
chmod +x setup.sh
sudo bash setup.sh
# Enter your GitHub repo URL when prompted
```

**Script will automatically:**
- Install all dependencies
- Set up auto-start kiosk mode
- Configure auto-updates (daily 7 AM)
- Start config web server
- Reboot

### 5️⃣ Configure Nightscout

After reboot, from any device on your network:

```
http://orangepi.local:3000
```

1. Enter your Nightscout URL
2. Add API secret (if needed)
3. Save

**Done!** Dashboard will now pull real glucose data every 5 minutes.

---

## Update Workflow

### When You're Developing

**On your computer:**
```bash
# Make changes to dashboard.html
git add dashboard.html
git commit -m "Updated clock size"
git push
```

**On Orange Pi:**
- Open `http://orangepi.local:3000`
- Click **"Update Now"**
- Dashboard refreshes instantly

### Automatic Updates

Every morning at **7 AM Mountain Time**, the Orange Pi:
1. Checks GitHub for changes
2. Pulls new commits
3. Refreshes browser automatically
4. Logs results

**Why 7 AM?** If something breaks, you'll notice during the day!

---

## Accessing Your Dashboard

### Main Display
Auto-starts on boot in fullscreen kiosk mode

### Config Interface
```
http://orangepi.local:3000
```
or
```
http://YOUR_ORANGE_PI_IP:3000
```

Features:
- View system info & current version
- **Update Now** button
- Configure Nightscout URL
- Adjust display settings
- Reboot device
- View logs

---

## Troubleshooting

### Can't Access orangepi.local

Use IP address instead. Find it by:
```bash
ssh root@orangepi.local
ip addr show
```

### Dashboard Not Loading

```bash
# Restart display
pkill chromium

# Or reboot
reboot
```

### Updates Not Working

```bash
# Check logs
tail -f /var/log/dashboard-update.log

# Manual update
/usr/local/bin/dashboard-update.sh
```

### Nightscout Data Not Showing

1. Check config at `http://orangepi.local:3000`
2. Verify Nightscout URL is correct
3. Test URL in browser: `https://your-nightscout.com/api/v1/entries.json?count=1`
4. Check browser console (F12) for errors

---

## Next Steps

### Customize It

Edit `dashboard.html`:
- Change colors (CSS variables)
- Adjust font sizes
- Modify motivational messages
- Change update schedule

Then push to GitHub and click "Update Now"!

### Add Features

- Weather display
- Calendar events
- Custom reminders via web interface
- Other APIs

### Make It Yours

This is YOUR dashboard. Customize it however you want!

---

## Important Files

**On Orange Pi:**
- Dashboard: `/opt/dashboard/dashboard.html`
- Config: `/etc/dashboard/config.json`
- Update script: `/usr/local/bin/dashboard-update.sh`
- Update logs: `/var/log/dashboard-update.log`
- Cron schedule: `/etc/cron.d/dashboard-update`

**Services:**
- Config server: `systemctl status dashboard-config`
- Display: Chromium in kiosk mode

---

## Tips

✨ **Screen brightness:** Adjust from Orange Pi settings or monitor controls

✨ **WiFi changes:** Use web interface or `nmtui` command

✨ **Development:** Use "Update Now" button liberally while testing

✨ **Backups:** Keep your GitHub repo updated - it's your backup!

✨ **Power:** Use at least 5V 2A power supply for stability

---

## Support

📖 Full documentation in `README.md`

🐛 Issues? Check the logs:
```bash
# Update logs
tail -f /var/log/dashboard-update.log

# Config server logs  
journalctl -u dashboard-config -f

# System logs
journalctl -f
```

---

**You're all set! Enjoy your professional health dashboard! 🎉**
