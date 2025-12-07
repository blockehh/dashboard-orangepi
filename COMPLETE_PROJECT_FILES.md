# Complete Orange Pi Dashboard Project Files

Copy each section below into separate files in your project.

---

## FILE: dashboard.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;700&family=Libre+Franklin:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f0f14;
            --bg-secondary: #1a1a22;
            --bg-tertiary: #25252f;
            --accent-primary: #6b9bd1;
            --accent-secondary: #8b7ec8;
            --text-primary: #e8e8f0;
            --text-secondary: #9898a8;
            --text-tertiary: #68687a;
            --glucose-good: #5fb884;
            --glucose-warning: #d6a461;
            --glucose-danger: #d67373;
            --border-subtle: #2a2a38;
        }

        .light-mode {
            --bg-primary: #fafbfc;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f4f5f7;
            --accent-primary: #4a7ba7;
            --accent-secondary: #6b5b95;
            --text-primary: #1a1a24;
            --text-secondary: #5a5a6a;
            --text-tertiary: #8a8a9a;
            --glucose-good: #3d9970;
            --glucose-warning: #b8883b;
            --glucose-danger: #b84d4d;
            --border-subtle: #e4e5e8;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'DM Sans', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            position: relative;
            transition: background 0.8s ease, color 0.8s ease;
        }

        /* Circuit Board Background */
        #circuit-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.08;
            transition: opacity 0.8s ease;
        }

        .light-mode #circuit-canvas {
            opacity: 0.04;
        }

        /* Main Container */
        .dashboard {
            position: relative;
            z-index: 1;
            height: 100vh;
            display: grid;
            grid-template-columns: 280px 1fr auto;
            grid-template-rows: 1fr auto;
            padding: 16px;
            gap: 16px;
        }

        /* Left Sidebar - Reminders */
        .reminders-bar {
            display: flex;
            flex-direction: column;
            gap: 10px;
            grid-row: 1 / 2;
            grid-column: 1;
            align-content: start;
        }

        .reminder {
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-primary);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .reminder::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: var(--accent-primary);
        }

        /* Center Content */
        .center-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 20px;
            grid-row: 1 / 2;
            grid-column: 2;
        }

        /* Clock */
        .clock-container {
            display: flex;
            align-items: baseline;
            gap: 12px;
        }

        .clock {
            font-family: 'Libre Franklin', sans-serif;
            font-size: 120px;
            font-weight: 800;
            letter-spacing: -3px;
            line-height: 1;
            color: var(--accent-primary);
        }

        .period {
            font-family: 'DM Sans', sans-serif;
            font-size: 36px;
            font-weight: 300;
            color: var(--accent-secondary);
            letter-spacing: 2px;
        }

        /* Dexcom Display */
        .dexcom-container {
            display: flex;
            align-items: center;
            gap: 24px;
            background: var(--bg-secondary);
            padding: 24px 40px;
            border-radius: 12px;
            border: 2px solid var(--border-subtle);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            transition: all 0.4s ease;
        }

        .dexcom-value {
            font-family: 'Libre Franklin', sans-serif;
            font-size: 72px;
            font-weight: 800;
            color: var(--glucose-good);
            line-height: 1;
            letter-spacing: -2px;
        }

        .dexcom-trend {
            font-size: 52px;
            line-height: 1;
            color: var(--text-secondary);
        }

        .dexcom-info {
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            color: var(--text-tertiary);
            font-weight: 500;
        }

        .dexcom-time {
            font-size: 12px;
            color: var(--text-tertiary);
            margin-top: 6px;
            font-weight: 400;
        }

        /* Warning/Danger states */
        .dexcom-container.warning {
            border-color: var(--glucose-warning);
            background: var(--bg-tertiary);
        }

        .dexcom-container.warning .dexcom-value {
            color: var(--glucose-warning);
        }

        .dexcom-container.danger {
            border-color: var(--glucose-danger);
            background: var(--bg-tertiary);
            border-width: 3px;
        }

        .dexcom-container.danger .dexcom-value {
            color: var(--glucose-danger);
        }

        /* Motivational Text Ticker */
        .ticker-container {
            width: 100%;
            overflow: hidden;
            background: linear-gradient(90deg, var(--bg-primary) 0%, transparent 5%, transparent 95%, var(--bg-primary) 100%);
            padding: 12px 0;
            grid-row: 2;
            grid-column: 1 / -1;
        }

        .ticker {
            display: flex;
            animation: scroll 40s linear infinite;
            white-space: nowrap;
        }

        .ticker-text {
            font-family: 'DM Sans', sans-serif;
            font-size: 16px;
            font-weight: 500;
            color: var(--accent-primary);
            padding: 0 50px;
            letter-spacing: 0.5px;
        }

        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        /* Date Display */
        .date {
            font-family: 'DM Sans', sans-serif;
            font-size: 15px;
            color: var(--text-tertiary);
            letter-spacing: 1px;
            text-align: center;
            font-weight: 500;
            text-transform: uppercase;
        }

        /* Status Indicators */
        .status-bar {
            position: absolute;
            bottom: 16px;
            right: 16px;
            display: flex;
            gap: 16px;
            font-size: 11px;
            color: var(--text-tertiary);
            font-weight: 500;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--glucose-good);
        }
    </style>
</head>
<body>
    <!-- Circuit Board Animation Canvas -->
    <canvas id="circuit-canvas"></canvas>

    <!-- Main Dashboard -->
    <div class="dashboard">
        <!-- Left Sidebar - Reminders -->
        <div class="reminders-bar" id="reminders">
            <!-- Reminders will be injected here -->
        </div>

        <!-- Center Content -->
        <div class="center-content">
            <div class="date" id="date"></div>
            <div class="clock-container">
                <div class="clock" id="clock"></div>
                <div class="period" id="period"></div>
            </div>
            
            <!-- Dexcom Display -->
            <div class="dexcom-container" id="dexcom">
                <div>
                    <div class="dexcom-value" id="glucose-value">127</div>
                    <div class="dexcom-time" id="glucose-time">2 min ago</div>
                </div>
                <div class="dexcom-trend" id="glucose-trend">→</div>
                <div class="dexcom-info">
                    <div>mg/dL</div>
                </div>
            </div>
        </div>

        <!-- Motivational Text Ticker -->
        <div class="ticker-container" id="ticker-container" style="display: none;">
            <div class="ticker">
                <span class="ticker-text">Focus on progress, not perfection</span>
                <span class="ticker-text">Small consistent steps lead to remarkable results</span>
                <span class="ticker-text">Today is an opportunity to grow</span>
                <span class="ticker-text">Focus on progress, not perfection</span>
                <span class="ticker-text">Small consistent steps lead to remarkable results</span>
            </div>
        </div>
    </div>

    <!-- Status Bar -->
    <div class="status-bar">
        <div class="status-item">
            <div class="status-dot"></div>
            <span>System</span>
        </div>
        <div class="status-item" id="mode-indicator">
            <span>Day Mode</span>
        </div>
    </div>

    <script>
        // ===== CONFIGURATION =====
        let CONFIG = {
            nightscout: { url: '', apiSecret: '', enabled: false },
            supabase: { url: '', anonKey: '', remindersTable: 'reminders', motivationalTable: 'motivational_messages', enabled: false },
            display: { timezone: 'America/Denver', dayModeStart: 6, dayModeEnd: 20, motivationalHoursStart: 7, motivationalHoursEnd: 10 }
        };

        // Load all configuration from local server
        async function loadConfig() {
            try {
                const response = await fetch('http://localhost:3000/api/config');
                const config = await response.json();
                
                // Nightscout config
                if (config.nightscout && config.nightscout.url) {
                    CONFIG.nightscout.url = config.nightscout.url;
                    CONFIG.nightscout.apiSecret = config.nightscout.api_secret || '';
                    CONFIG.nightscout.enabled = true;
                    console.log('Nightscout configured');
                }
                
                // Supabase config
                if (config.supabase && config.supabase.url) {
                    CONFIG.supabase.url = config.supabase.url;
                    CONFIG.supabase.anonKey = config.supabase.anon_key || '';
                    CONFIG.supabase.remindersTable = config.supabase.reminders_table || 'reminders';
                    CONFIG.supabase.motivationalTable = config.supabase.motivational_table || 'motivational_messages';
                    CONFIG.supabase.enabled = true;
                    console.log('Supabase configured');
                }
                
                // Display config
                if (config.display) {
                    CONFIG.display = { ...CONFIG.display, ...config.display };
                }
                
                // Start data fetching
                updateDexcomData();
                updateReminders();
                updateMotivationalMessages();
                
                // Set intervals
                setInterval(updateDexcomData, 5 * 60 * 1000); // Every 5 minutes
                setInterval(updateReminders, 5 * 60 * 1000);
                setInterval(updateMotivationalMessages, 60 * 60 * 1000); // Every hour
                
            } catch (error) {
                console.log('Config not available, using defaults and mock data');
                useMockDexcomData();
            }
        }

        // ===== CLOCK =====
        function updateClock() {
            const now = new Date();
            
            // Convert to Mountain Time
            const options = { timeZone: 'America/Denver', hour: 'numeric', minute: '2-digit', hour12: true };
            const timeString = now.toLocaleTimeString('en-US', options);
            
            // Split time and period
            const [time, period] = timeString.split(' ');
            
            document.getElementById('clock').textContent = time;
            document.getElementById('period').textContent = period;
            
            // Update date
            const dateOptions = { 
                timeZone: 'America/Denver',
                weekday: 'long', 
                month: 'long', 
                day: 'numeric', 
                year: 'numeric' 
            };
            document.getElementById('date').textContent = now.toLocaleDateString('en-US', dateOptions).toUpperCase();
        }

        // ===== LIGHT/DARK MODE =====
        function updateTheme() {
            const now = new Date();
            const mountainTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/Denver' }));
            const hour = mountainTime.getHours();
            
            // Day mode: 6am-8pm, Night mode: 8pm-6am
            const isDayMode = hour >= 6 && hour < 20;
            
            if (isDayMode) {
                document.body.classList.add('light-mode');
                document.getElementById('mode-indicator').innerHTML = '<span>Day Mode</span>';
            } else {
                document.body.classList.remove('light-mode');
                document.getElementById('mode-indicator').innerHTML = '<span>Night Mode</span>';
            }
        }

        // ===== MOTIVATIONAL TICKER =====
        function updateTicker() {
            const now = new Date();
            const mountainTime = new Date(now.toLocaleString('en-US', { timeZone: 'America/Denver' }));
            const hour = mountainTime.getHours();
            
            // Show ticker between 7am-10am
            const showTicker = hour >= 7 && hour < 10;
            document.getElementById('ticker-container').style.display = showTicker ? 'block' : 'none';
        }

        // ===== DEXCOM DATA =====
        async function updateDexcomData() {
            if (!CONFIG.nightscout.enabled) {
                useMockDexcomData();
                return;
            }

            try {
                const url = `${CONFIG.nightscout.url}/api/v1/entries.json?count=1`;
                const headers = {};
                
                if (CONFIG.nightscout.apiSecret) {
                    headers['API-SECRET'] = CONFIG.nightscout.apiSecret;
                }

                const response = await fetch(url, { headers });
                const data = await response.json();
                
                if (data && data.length > 0) {
                    const entry = data[0];
                    const glucoseValue = entry.sgv;
                    const direction = entry.direction;
                    const timestamp = new Date(entry.date);
                    const minutesAgo = Math.round((Date.now() - timestamp) / 60000);
                    
                    document.getElementById('glucose-value').textContent = glucoseValue;
                    document.getElementById('glucose-trend').textContent = getTrendArrow(direction);
                    document.getElementById('glucose-time').textContent = `${minutesAgo} min ago`;
                    
                    updateGlucoseStatus(glucoseValue);
                    console.log(`Glucose: ${glucoseValue} mg/dL, Trend: ${direction}, ${minutesAgo} min ago`);
                }
            } catch (error) {
                console.error('Error fetching Nightscout data:', error);
                useMockDexcomData();
            }
        }

        // Convert Nightscout direction to arrow
        function getTrendArrow(direction) {
            const arrows = {
                'DoubleUp': '↑↑',
                'SingleUp': '↑',
                'FortyFiveUp': '↗',
                'Flat': '→',
                'FortyFiveDown': '↘',
                'SingleDown': '↓',
                'DoubleDown': '↓↓',
                'NOT COMPUTABLE': '?',
                'RATE OUT OF RANGE': '?'
            };
            return arrows[direction] || '→';
        }

        // Update glucose container styling based on value
        function updateGlucoseStatus(glucoseValue) {
            const container = document.getElementById('dexcom');
            container.classList.remove('warning', 'danger');
            
            // Danger: <70 or >180
            if (glucoseValue < 70 || glucoseValue > 180) {
                container.classList.add('danger');
            } 
            // Warning: 70-80 or 160-180
            else if (glucoseValue < 80 || glucoseValue > 160) {
                container.classList.add('warning');
            }
        }

        // Mock data for testing (when Nightscout not configured)
        function useMockDexcomData() {
            const mockData = {
                value: Math.floor(Math.random() * 100) + 80,
                trend: ['↑↑', '↑', '→', '↓', '↓↓'][Math.floor(Math.random() * 5)],
                minutesAgo: Math.floor(Math.random() * 15) + 1
            };

            document.getElementById('glucose-value').textContent = mockData.value;
            document.getElementById('glucose-trend').textContent = mockData.trend;
            document.getElementById('glucose-time').textContent = `${mockData.minutesAgo} min ago`;
            
            updateGlucoseStatus(mockData.value);
        }

        // ===== REMINDERS =====
        async function updateReminders() {
            if (!CONFIG.supabase.enabled) {
                // Use mock reminders
                const sampleReminders = [
                    "Take medication at 3pm",
                    "Team meeting at 2:30pm"
                ];
                displayReminders(sampleReminders);
                return;
            }

            try {
                const url = `${CONFIG.supabase.url}/rest/v1/${CONFIG.supabase.remindersTable}?active=eq.true&order=priority.desc&limit=5`;
                const headers = {
                    'apikey': CONFIG.supabase.anonKey,
                    'Authorization': `Bearer ${CONFIG.supabase.anonKey}`
                };

                const response = await fetch(url, { headers });
                const data = await response.json();
                
                const reminderTexts = data.map(r => r.text);
                displayReminders(reminderTexts);
                console.log(`Loaded ${reminderTexts.length} reminders from Supabase`);
            } catch (error) {
                console.error('Error fetching reminders from Supabase:', error);
                // Fallback to empty or mock data
                displayReminders([]);
            }
        }

        function displayReminders(reminders) {
            const container = document.getElementById('reminders');
            if (reminders.length > 0) {
                container.innerHTML = reminders.map(text => 
                    `<div class="reminder">${text}</div>`
                ).join('');
            } else {
                container.innerHTML = '';
            }
        }

        // ===== MOTIVATIONAL MESSAGES =====
        async function updateMotivationalMessages() {
            if (!CONFIG.supabase.enabled) {
                // Use default messages (already in HTML)
                return;
            }

            try {
                const url = `${CONFIG.supabase.url}/rest/v1/${CONFIG.supabase.motivationalTable}?active=eq.true&order=display_order.asc`;
                const headers = {
                    'apikey': CONFIG.supabase.anonKey,
                    'Authorization': `Bearer ${CONFIG.supabase.anonKey}`
                };

                const response = await fetch(url, { headers });
                const data = await response.json();
                
                if (data && data.length > 0) {
                    const messages = data.map(m => m.text);
                    displayMotivationalMessages(messages);
                    console.log(`Loaded ${messages.length} motivational messages from Supabase`);
                }
            } catch (error) {
                console.error('Error fetching motivational messages from Supabase:', error);
                // Keep default messages in HTML
            }
        }

        function displayMotivationalMessages(messages) {
            const ticker = document.querySelector('.ticker');
            if (ticker && messages.length > 0) {
                // Duplicate messages for seamless scrolling
                const duplicatedMessages = [...messages, ...messages];
                ticker.innerHTML = duplicatedMessages.map(text => 
                    `<span class="ticker-text">${text}</span>`
                ).join('');
            }
        }

        // ===== CIRCUIT BOARD ANIMATION =====
        class CircuitBoard {
            constructor(canvas) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.particles = [];
                this.lines = [];
                this.resize();
                this.init();
                
                window.addEventListener('resize', () => this.resize());
            }

            resize() {
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
            }

            init() {
                // Create subtle circuit lines
                const numLines = 8;
                for (let i = 0; i < numLines; i++) {
                    this.lines.push({
                        x1: Math.random() * this.canvas.width,
                        y1: Math.random() * this.canvas.height,
                        x2: Math.random() * this.canvas.width,
                        y2: Math.random() * this.canvas.height,
                        opacity: Math.random() * 0.15 + 0.05
                    });
                }

                // Create subtle particles
                const numParticles = 15;
                for (let i = 0; i < numParticles; i++) {
                    this.particles.push({
                        x: Math.random() * this.canvas.width,
                        y: Math.random() * this.canvas.height,
                        vx: (Math.random() - 0.5) * 0.2,
                        vy: (Math.random() - 0.5) * 0.2,
                        radius: Math.random() * 1.5 + 0.5,
                        opacity: Math.random() * 0.3 + 0.1
                    });
                }
            }

            draw() {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

                // Only draw in dark mode
                const isDark = !document.body.classList.contains('light-mode');
                if (!isDark) return;
                
                const lineColor = '107, 155, 209'; // accent-primary in dark mode
                
                this.lines.forEach(line => {
                    this.ctx.strokeStyle = `rgba(${lineColor}, ${line.opacity})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.beginPath();
                    this.ctx.moveTo(line.x1, line.y1);
                    this.ctx.lineTo(line.x2, line.y2);
                    this.ctx.stroke();

                    // Subtle connection points
                    this.ctx.fillStyle = `rgba(${lineColor}, ${line.opacity * 1.2})`;
                    this.ctx.beginPath();
                    this.ctx.arc(line.x1, line.y1, 2, 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.beginPath();
                    this.ctx.arc(line.x2, line.y2, 2, 0, Math.PI * 2);
                    this.ctx.fill();
                });

                // Draw and update particles
                this.particles.forEach(particle => {
                    particle.x += particle.vx;
                    particle.y += particle.vy;

                    // Wrap around edges
                    if (particle.x < 0) particle.x = this.canvas.width;
                    if (particle.x > this.canvas.width) particle.x = 0;
                    if (particle.y < 0) particle.y = this.canvas.height;
                    if (particle.y > this.canvas.height) particle.y = 0;

                    // Subtle opacity variation
                    particle.opacity += (Math.random() - 0.5) * 0.02;
                    particle.opacity = Math.max(0.1, Math.min(0.4, particle.opacity));

                    // Draw particle
                    this.ctx.fillStyle = `rgba(${lineColor}, ${particle.opacity})`;
                    this.ctx.beginPath();
                    this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                    this.ctx.fill();
                });
            }

            animate() {
                this.draw();
                requestAnimationFrame(() => this.animate());
            }
        }

        // ===== INITIALIZATION =====
        const circuit = new CircuitBoard(document.getElementById('circuit-canvas'));
        circuit.animate();

        // Initial updates
        updateClock();
        updateTheme();
        updateTicker();
        loadConfig();  // Load all config and start data fetching

        // Set intervals for time-based updates
        setInterval(updateClock, 1000);
        setInterval(updateTheme, 60000);
        setInterval(updateTicker, 60000);
    </script>
</body>
</html>
```

---

## FILE: supabase-schema.sql

```sql
-- Supabase Database Schema for Orange Pi Dashboard
-- Run this in your Supabase SQL Editor

-- Table: reminders
CREATE TABLE IF NOT EXISTS reminders (
  id BIGSERIAL PRIMARY KEY,
  text TEXT NOT NULL,
  active BOOLEAN DEFAULT true,
  priority INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reminders_active_priority 
ON reminders(active, priority DESC);

ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON reminders
FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write access" ON reminders
FOR ALL USING (auth.role() = 'authenticated');

INSERT INTO reminders (text, active, priority) VALUES
  ('Take medication at 3pm', true, 1),
  ('Team meeting at 2:30pm', true, 2),
  ('Exercise for 30 minutes', true, 3)
ON CONFLICT DO NOTHING;

-- Table: motivational_messages
CREATE TABLE IF NOT EXISTS motivational_messages (
  id BIGSERIAL PRIMARY KEY,
  text TEXT NOT NULL,
  active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_motivational_active_order 
ON motivational_messages(active, display_order ASC);

ALTER TABLE motivational_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON motivational_messages
FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write access" ON motivational_messages
FOR ALL USING (auth.role() = 'authenticated');

INSERT INTO motivational_messages (text, active, display_order) VALUES
  ('Focus on progress, not perfection', true, 1),
  ('Small consistent steps lead to remarkable results', true, 2),
  ('Today is an opportunity to grow', true, 3),
  ('Your health is your wealth', true, 4),
  ('Every positive choice compounds over time', true, 5)
ON CONFLICT DO NOTHING;

-- Helper function for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_reminders_updated_at 
BEFORE UPDATE ON reminders
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_motivational_messages_updated_at 
BEFORE UPDATE ON motivational_messages
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## FILE: .gitignore

```
# System files
.DS_Store
Thumbs.db
*~

# Logs
*.log

# Config files with sensitive data
config.json
.env

# IDE
.vscode/
.idea/
*.swp

# Python
__pycache__/
*.py[cod]

# Node
node_modules/
```

---

## FILE: README.md

```markdown
# Orange Pi Dashboard - Health Monitoring Display

A beautiful 7-inch health dashboard for Orange Pi that displays time, glucose readings from Nightscout, reminders, and motivational messages.

## Features

- **Clock:** Mountain Time, 12-hour format with AM/PM
- **Glucose Display:** Real-time from Nightscout API, color-coded by range
- **Reminders:** From Supabase database, displayed in left sidebar
- **Motivational Messages:** From Supabase, scrolling ticker (7-10 AM only)
- **Auto Light/Dark Mode:** 6 AM - 8 PM day mode, 8 PM - 6 AM night mode
- **Web Configuration:** Manage everything from your phone
- **Auto-Updates:** Daily at 7 AM Mountain Time from GitHub

## Quick Start

### 1. Flash SD Card
- Download Armbian for Orange Pi Zero 2W
- Flash with Balena Etcher
- Boot Orange Pi

### 2. Run Setup
```bash
ssh root@orangepi.local
wget https://raw.githubusercontent.com/YOUR_USERNAME/dashboard-orangepi/main/setup.sh
chmod +x setup.sh
sudo bash setup.sh
```

### 3. Configure
Open `http://orangepi.local:3000` from your phone:
- Set Nightscout URL
- Set Supabase credentials
- Configure WiFi
- Adjust settings

## Supabase Setup

Run `supabase-schema.sql` in your Supabase SQL Editor to create tables.

## Configuration

Settings stored in `/etc/dashboard/config.json`:
- Nightscout URL & API secret
- Supabase URL & anon key
- Display preferences
- Update schedule

## Updates

- **Automatic:** Every day at 7 AM
- **Manual:** Click "Update Now" in config GUI

## Documentation

See `AI_AGENT_INSTRUCTIONS.md` for complete technical documentation.
```

---

## PROJECT STRUCTURE

```
dashboard-orangepi/
├── dashboard.html          # Main display (fullscreen browser)
├── setup.sh               # Orange Pi installer
├── supabase-schema.sql    # Database setup
├── README.md              # User documentation
├── .gitignore            # Git ignore rules
└── AI_AGENT_INSTRUCTIONS.md  # Technical docs (create from briefing)
```

---

## NEXT STEPS FOR AI AGENT

1. **Create these files** in your project directory
2. **Push to GitHub repository**
3. **Wait for Blake to flash SD card** and boot Orange Pi
4. **Help build config-server.py** with:
   - WiFi management interface
   - Hotspot mode toggle
   - Phone-friendly GUI
   - Settings management

5. **Key features to implement:**
   - Network configuration page
   - Supabase credentials form
   - Nightscout settings form
   - Display customization options
   - Manual update button

6. **Remember:**
   - Mobile-first design
   - Error handling everywhere
   - Graceful fallbacks
   - Test before deploying
   - Mountain Time is critical

---

## CONFIGURATION SCHEMA

```json
{
  "nightscout": {
    "url": "https://yourname.herokuapp.com",
    "api_secret": ""
  },
  "supabase": {
    "url": "https://your-project.supabase.co",
    "anon_key": "your-anon-key",
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
    "update_time": "07:00"
  }
}
```

---

## DATA FLOW

```
Nightscout API → dashboard.html → Displays glucose (every 5 min)
Supabase API → dashboard.html → Displays reminders (every 5 min)
Supabase API → dashboard.html → Displays motivational (every hour, 7-10 AM only)
Config GUI (port 3000) → config.json → dashboard.html reads settings
GitHub → Auto-update (7 AM daily) → Browser refresh
```
