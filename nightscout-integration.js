// Add this to your dashboard.html to enable real Nightscout integration

// ===== NIGHTSCOUT CONFIGURATION =====
// These will be loaded from /etc/dashboard/config.json via the config server
let NIGHTSCOUT_CONFIG = {
    url: '',
    apiSecret: '',
    enabled: false
};

// Load config from local server
async function loadNightscoutConfig() {
    try {
        const response = await fetch('http://localhost:3000/api/config');
        const config = await response.json();
        
        if (config.nightscout_url) {
            NIGHTSCOUT_CONFIG.url = config.nightscout_url;
            NIGHTSCOUT_CONFIG.apiSecret = config.nightscout_api_secret || '';
            NIGHTSCOUT_CONFIG.enabled = true;
            
            console.log('Nightscout config loaded:', NIGHTSCOUT_CONFIG.url);
            
            // Start fetching data immediately
            updateDexcomData();
            // Then fetch every 5 minutes
            setInterval(updateDexcomData, 5 * 60 * 1000);
        }
    } catch (error) {
        console.log('Config not available, using mock data');
        // Continue with mock data for testing
    }
}

// ===== REAL NIGHTSCOUT DATA FETCHING =====
async function updateDexcomData() {
    if (!NIGHTSCOUT_CONFIG.enabled) {
        // Use mock data if Nightscout not configured
        useMockDexcomData();
        return;
    }

    try {
        const url = `${NIGHTSCOUT_CONFIG.url}/api/v1/entries.json?count=1`;
        const headers = {};
        
        // Add API secret if provided
        if (NIGHTSCOUT_CONFIG.apiSecret) {
            headers['API-SECRET'] = NIGHTSCOUT_CONFIG.apiSecret;
        }

        const response = await fetch(url, { headers });
        const data = await response.json();
        
        if (data && data.length > 0) {
            const entry = data[0];
            const glucoseValue = entry.sgv;
            const direction = entry.direction;
            const timestamp = new Date(entry.date);
            const minutesAgo = Math.round((Date.now() - timestamp) / 60000);
            
            // Update display
            document.getElementById('glucose-value').textContent = glucoseValue;
            document.getElementById('glucose-trend').textContent = getTrendArrow(direction);
            document.getElementById('glucose-time').textContent = `${minutesAgo} min ago`;
            
            // Update styling based on value
            updateGlucoseStatus(glucoseValue);
            
            console.log(`Glucose: ${glucoseValue} mg/dL, Trend: ${direction}, ${minutesAgo} min ago`);
        }
    } catch (error) {
        console.error('Error fetching Nightscout data:', error);
        // Fall back to mock data if fetch fails
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadNightscoutConfig();
});


// ===== REMINDERS INTEGRATION =====
// This will fetch reminders from the config server
// You can add/edit reminders via the web interface at http://orangepi.local:3000

async function loadReminders() {
    try {
        const response = await fetch('http://localhost:3000/api/reminders');
        const reminders = await response.json();
        
        const container = document.getElementById('reminders');
        if (reminders.length > 0) {
            container.innerHTML = reminders.map(text => 
                `<div class="reminder">${text}</div>`
            ).join('');
        }
    } catch (error) {
        console.log('Using default reminders');
        // Keep existing hardcoded reminders if API not available
    }
}

// Call this on page load
document.addEventListener('DOMContentLoaded', function() {
    loadReminders();
});


// ===== EXAMPLE: FULL INTEGRATION IN YOUR DASHBOARD.HTML =====
/*

Replace the existing updateDexcomData() function and initialization code 
at the bottom of your dashboard.html with this:

<script>
    // ... existing clock, theme, ticker functions ...

    // ===== NIGHTSCOUT CONFIGURATION =====
    let NIGHTSCOUT_CONFIG = { url: '', apiSecret: '', enabled: false };

    async function loadNightscoutConfig() {
        try {
            const response = await fetch('http://localhost:3000/api/config');
            const config = await response.json();
            if (config.nightscout_url) {
                NIGHTSCOUT_CONFIG.url = config.nightscout_url;
                NIGHTSCOUT_CONFIG.apiSecret = config.nightscout_api_secret || '';
                NIGHTSCOUT_CONFIG.enabled = true;
                updateDexcomData();
                setInterval(updateDexcomData, 5 * 60 * 1000);
            }
        } catch (error) {
            console.log('Using mock data');
        }
    }

    async function updateDexcomData() {
        if (!NIGHTSCOUT_CONFIG.enabled) {
            useMockDexcomData();
            return;
        }

        try {
            const url = `${NIGHTSCOUT_CONFIG.url}/api/v1/entries.json?count=1`;
            const headers = {};
            if (NIGHTSCOUT_CONFIG.apiSecret) {
                headers['API-SECRET'] = NIGHTSCOUT_CONFIG.apiSecret;
            }
            const response = await fetch(url, { headers });
            const data = await response.json();
            
            if (data && data.length > 0) {
                const entry = data[0];
                document.getElementById('glucose-value').textContent = entry.sgv;
                document.getElementById('glucose-trend').textContent = getTrendArrow(entry.direction);
                const minutesAgo = Math.round((Date.now() - new Date(entry.date)) / 60000);
                document.getElementById('glucose-time').textContent = `${minutesAgo} min ago`;
                updateGlucoseStatus(entry.sgv);
            }
        } catch (error) {
            console.error('Nightscout fetch error:', error);
            useMockDexcomData();
        }
    }

    function getTrendArrow(direction) {
        const arrows = {
            'DoubleUp': '↑↑', 'SingleUp': '↑', 'FortyFiveUp': '↗',
            'Flat': '→', 'FortyFiveDown': '↘', 'SingleDown': '↓', 
            'DoubleDown': '↓↓'
        };
        return arrows[direction] || '→';
    }

    function updateGlucoseStatus(value) {
        const container = document.getElementById('dexcom');
        container.classList.remove('warning', 'danger');
        if (value < 70 || value > 180) container.classList.add('danger');
        else if (value < 80 || value > 160) container.classList.add('warning');
    }

    function useMockDexcomData() {
        const mock = {
            value: Math.floor(Math.random() * 100) + 80,
            trend: ['↑↑', '↑', '→', '↓', '↓↓'][Math.floor(Math.random() * 5)],
            minutesAgo: Math.floor(Math.random() * 15) + 1
        };
        document.getElementById('glucose-value').textContent = mock.value;
        document.getElementById('glucose-trend').textContent = mock.trend;
        document.getElementById('glucose-time').textContent = `${mock.minutesAgo} min ago`;
        updateGlucoseStatus(mock.value);
    }

    // ... rest of your code (circuit board, etc) ...

    // INITIALIZATION
    const circuit = new CircuitBoard(document.getElementById('circuit-canvas'));
    circuit.animate();
    
    updateClock();
    updateTheme();
    updateTicker();
    loadNightscoutConfig();  // Load Nightscout config and start fetching
    updateReminders();

    setInterval(updateClock, 1000);
    setInterval(updateTheme, 60000);
    setInterval(updateTicker, 60000);
</script>

*/
