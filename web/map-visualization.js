/**
 * IoT Network Selection Map Visualization
 * 
 * JavaScript module để visualize map simulation với:
 * - Base stations (Wi-Fi, 5G, BLE)
 * - IoT device movement
 * - Network coverage visualization
 * - Real-time decision making
 */

class MapVisualization {
    constructor() {
        this.canvas = document.getElementById('mapCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        // API configuration
        this.apiBaseUrl = 'http://localhost:8000';
        
        // Map configuration
        this.mapSize = { width: 1000, height: 1000 };
        this.canvasSize = { width: 800, height: 600 };
        this.scale = {
            x: this.canvasSize.width / this.mapSize.width,
            y: this.canvasSize.height / this.mapSize.height
        };
        
        // Simulation state
        this.devicePosition = { x: 0, y: 0 };
        this.currentTask = 'IDLE_MONITORING';
        this.availableNetworks = [];
        this.simulationStep = 0;
        this.isAutoRunning = false;
        this.baseStations = [];
        this.decisionResult = null;
        
        // Colors for different networks
        this.networkColors = {
            'Wi-Fi': '#2196F3',
            '5G': '#9C27B0', 
            'BLE': '#FF9800',
            '4G': '#4CAF50'
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkApiStatus();
        this.initializeBaseStations();
        this.draw();
        this.startAutoRunTimer();
    }
    
    setupEventListeners() {
        // Simulation controls
        document.getElementById('stepBtn').addEventListener('click', () => this.runSimulationStep());
        document.getElementById('decisionBtn').addEventListener('click', () => this.makeDecision());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetSimulation());
        
        // Auto-run toggle
        const autoToggle = document.getElementById('autoToggle');
        autoToggle.addEventListener('click', () => this.toggleAutoRun());
        
        // Canvas click for manual device placement
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        
        // Resize handling
        window.addEventListener('resize', () => this.handleResize());
    }
    
    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('apiStatus').textContent = '✅ Online';
                document.getElementById('apiStatus').style.color = '#4CAF50';
                this.updateStatusBar('API connected successfully');
            } else {
                throw new Error('API not responding');
            }
        } catch (error) {
            document.getElementById('apiStatus').textContent = '❌ Offline';
            document.getElementById('apiStatus').style.color = '#F44336';
            this.updateStatusBar('❌ API connection failed - Please start the server');
            console.error('API connection failed:', error);
        }
    }
    
    initializeBaseStations() {
        // Initialize base stations in a grid pattern (matching simulation.py)
        this.baseStations = [];
        
        // Wi-Fi stations (4 stations)
        const wifiStations = [
            { x: 200, y: 200, type: 'Wi-Fi' },
            { x: 800, y: 200, type: 'Wi-Fi' },
            { x: 200, y: 800, type: 'Wi-Fi' },
            { x: 800, y: 800, type: 'Wi-Fi' }
        ];
        
        // 5G stations (4 stations)  
        const fiveGStations = [
            { x: 500, y: 150, type: '5G' },
            { x: 150, y: 500, type: '5G' },
            { x: 850, y: 500, type: '5G' },
            { x: 500, y: 850, type: '5G' }
        ];
        
        // BLE stations (4 stations)
        const bleStations = [
            { x: 350, y: 350, type: 'BLE' },
            { x: 650, y: 350, type: 'BLE' },
            { x: 350, y: 650, type: 'BLE' },
            { x: 650, y: 650, type: 'BLE' }
        ];
        
        this.baseStations = [...wifiStations, ...fiveGStations, ...bleStations];
        this.updateStatusBar(`Initialized ${this.baseStations.length} base stations`);
    }
    
    async runSimulationStep() {
        try {
            this.updateStatusBar('🔄 Running simulation step...');
            
            const response = await fetch(`${this.apiBaseUrl}/simulation/step`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Update device state
            this.devicePosition = {
                x: data.device_state.position[0],
                y: data.device_state.position[1]
            };
            this.currentTask = data.device_state.current_task;
            this.availableNetworks = data.device_state.available_networks;
            this.simulationStep = data.step;
            
            // Update decision result if available
            if (data.decision && !data.decision.error) {
                this.decisionResult = {
                    selectedNetwork: data.decision.selected_network,
                    cost: data.decision.cost
                };
            } else {
                this.decisionResult = null;
            }
            
            this.updateUI();
            this.draw();
            
            this.updateStatusBar(`Step ${this.simulationStep}: Device at (${this.devicePosition.x}, ${this.devicePosition.y})`);
            
        } catch (error) {
            console.error('Simulation step failed:', error);
            this.updateStatusBar('❌ Simulation step failed - Check API connection');
        }
    }
    
    async makeDecision() {
        if (this.availableNetworks.length === 0) {
            this.updateStatusBar('⚠️ No networks available for decision making');
            return;
        }
        
        try {
            this.updateStatusBar('🧠 Making network decision...');
            
            const payload = {
                position: [this.devicePosition.x, this.devicePosition.y],
                current_task: this.currentTask,
                available_networks: this.availableNetworks
            };
            
            const response = await fetch(`${this.apiBaseUrl}/decision`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            this.decisionResult = {
                selectedNetwork: data.optimal_network,
                cost: data.optimal_cost,
                allCosts: data.all_network_costs,
                algorithm: data.algorithm
            };
            
            this.updateDecisionDisplay();
            this.draw();
            
            this.updateStatusBar(`Decision: Selected ${data.optimal_network} (cost: ${data.optimal_cost})`);
            
        } catch (error) {
            console.error('Decision making failed:', error);
            this.updateStatusBar('❌ Decision making failed');
        }
    }
    
    async resetSimulation() {
        try {
            this.updateStatusBar('🔄 Resetting simulation...');
            
            const response = await fetch(`${this.apiBaseUrl}/simulation/reset`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Reset local state
            this.devicePosition = { x: 0, y: 0 };
            this.currentTask = 'IDLE_MONITORING';
            this.availableNetworks = [];
            this.simulationStep = 0;
            this.decisionResult = null;
            
            this.updateUI();
            this.draw();
            
            this.updateStatusBar('✅ Simulation reset successfully');
            
        } catch (error) {
            console.error('Reset failed:', error);
            this.updateStatusBar('❌ Reset failed');
        }
    }
    
    toggleAutoRun() {
        this.isAutoRunning = !this.isAutoRunning;
        const toggle = document.getElementById('autoToggle');
        
        if (this.isAutoRunning) {
            toggle.classList.add('active');
            this.updateStatusBar('🔄 Auto-run enabled');
        } else {
            toggle.classList.remove('active');
            this.updateStatusBar('⏸️ Auto-run disabled');
        }
    }
    
    startAutoRunTimer() {
        setInterval(() => {
            if (this.isAutoRunning) {
                this.runSimulationStep();
            }
        }, 2000); // Run every 2 seconds
    }
    
    handleCanvasClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left) / this.scale.x;
        const y = (event.clientY - rect.top) / this.scale.y;
        
        // Manually set device position (for debugging)
        this.devicePosition = { x: Math.round(x), y: Math.round(y) };
        this.draw();
        this.updateUI();
        
        this.updateStatusBar(`Device moved to (${Math.round(x)}, ${Math.round(y)}) manually`);
    }
    
    handleResize() {
        // Handle responsive canvas resizing if needed
        this.draw();
    }
    
    updateUI() {
        // Update device information
        document.getElementById('devicePosition').textContent = `(${this.devicePosition.x}, ${this.devicePosition.y})`;
        document.getElementById('simulationStep').textContent = this.simulationStep;
        
        // Update current task badge
        const taskElement = document.getElementById('currentTask');
        taskElement.textContent = this.currentTask;
        taskElement.className = 'task-badge ' + this.getTaskBadgeClass(this.currentTask);
        
        // Update available networks
        this.updateNetworksList();
        
        // Update decision result
        this.updateDecisionDisplay();
    }
    
    getTaskBadgeClass(task) {
        const taskMap = {
            'IDLE_MONITORING': 'task-idle',
            'DATA_BURST_ALERT': 'task-burst',
            'VIDEO_STREAMING': 'task-video'
        };
        return taskMap[task] || 'task-idle';
    }
    
    updateNetworksList() {
        const networkList = document.getElementById('networkList');
        
        if (this.availableNetworks.length === 0) {
            networkList.innerHTML = `
                <div class="network-item">
                    <span class="network-name">No networks detected</span>
                </div>
            `;
            return;
        }
        
        networkList.innerHTML = this.availableNetworks.map(network => {
            const badgeClass = `network-${network.name.toLowerCase().replace('-', '')}`;
            return `
                <div class="network-item">
                    <div>
                        <div class="network-name">
                            <span class="network-badge ${badgeClass}">${network.name}</span>
                        </div>
                        <div class="network-stats">
                            ${network.bandwidth.toFixed(1)} Mbps • ${network.latency}ms
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    updateDecisionDisplay() {
        const decisionElement = document.getElementById('decisionResult');
        
        if (!this.decisionResult) {
            decisionElement.style.display = 'none';
            return;
        }
        
        decisionElement.style.display = 'block';
        
        document.getElementById('selectedNetwork').textContent = this.decisionResult.selectedNetwork;
        document.getElementById('selectedCost').textContent = this.decisionResult.cost.toFixed(2);
        
        // Update cost comparison if available
        const costComparison = document.getElementById('costComparison');
        if (this.decisionResult.allCosts) {
            const sortedCosts = Object.entries(this.decisionResult.allCosts)
                .sort((a, b) => a[1] - b[1]);
            
            costComparison.innerHTML = sortedCosts.map(([network, cost]) => {
                const isWinner = network === this.decisionResult.selectedNetwork;
                return `
                    <div class="cost-item ${isWinner ? 'winner' : ''}">
                        <span>${network}</span>
                        <span>${cost.toFixed(2)}</span>
                    </div>
                `;
            }).join('');
        }
    }
    
    updateStatusBar(message) {
        document.getElementById('statusBar').textContent = message;
    }
    
    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvasSize.width, this.canvasSize.height);
        
        // Draw background grid
        this.drawGrid();
        
        // Draw base stations
        this.drawBaseStations();
        
        // Draw network coverage areas
        this.drawCoverageAreas();
        
        // Draw IoT device
        this.drawDevice();
        
        // Draw connections to available networks
        this.drawNetworkConnections();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#e0e0e0';
        this.ctx.lineWidth = 0.5;
        
        // Vertical lines
        for (let x = 0; x <= this.canvasSize.width; x += 100 * this.scale.x) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvasSize.height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.canvasSize.height; y += 100 * this.scale.y) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvasSize.width, y);
            this.ctx.stroke();
        }
    }
    
    drawBaseStations() {
        this.baseStations.forEach(station => {
            const x = station.x * this.scale.x;
            const y = station.y * this.scale.y;
            const radius = 8;
            
            // Draw station circle
            this.ctx.fillStyle = this.networkColors[station.type] || '#666';
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.fill();
            
            // Draw station border
            this.ctx.strokeStyle = 'white';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Draw station label
            this.ctx.fillStyle = '#333';
            this.ctx.font = '10px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(station.type, x, y + 20);
        });
    }
    
    drawCoverageAreas() {
        // Draw coverage areas for available networks
        this.availableNetworks.forEach(network => {
            // Find corresponding base station
            const station = this.baseStations.find(s => s.type === network.name);
            if (!station) return;
            
            const x = station.x * this.scale.x;
            const y = station.y * this.scale.y;
            
            // Calculate coverage radius based on signal quality
            const maxRadius = 150 * this.scale.x; // Max coverage radius
            const signalQuality = Math.min(network.bandwidth / 100, 1); // Normalize to 0-1
            const radius = maxRadius * signalQuality;
            
            // Draw coverage area
            this.ctx.fillStyle = this.networkColors[network.name] + '20'; // Semi-transparent
            this.ctx.strokeStyle = this.networkColors[network.name] + '60';
            this.ctx.lineWidth = 1;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.stroke();
        });
    }
    
    drawDevice() {
        const x = this.devicePosition.x * this.scale.x;
        const y = this.devicePosition.y * this.scale.y;
        const radius = 12;
        
        // Draw device circle
        this.ctx.fillStyle = '#FF4444';
        this.ctx.strokeStyle = 'white';
        this.ctx.lineWidth = 3;
        
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.stroke();
        
        // Draw device icon (simple IoT symbol)
        this.ctx.fillStyle = 'white';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('📱', x, y + 3);
        
        // Draw task indicator
        const taskColors = {
            'IDLE_MONITORING': '#2196F3',
            'DATA_BURST_ALERT': '#FF9800', 
            'VIDEO_STREAMING': '#E91E63'
        };
        
        this.ctx.fillStyle = taskColors[this.currentTask] || '#666';
        this.ctx.beginPath();
        this.ctx.arc(x + 15, y - 15, 4, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    drawNetworkConnections() {
        if (!this.decisionResult) return;
        
        // Find the selected network base station
        const selectedStation = this.baseStations.find(s => s.type === this.decisionResult.selectedNetwork);
        if (!selectedStation) return;
        
        const deviceX = this.devicePosition.x * this.scale.x;
        const deviceY = this.devicePosition.y * this.scale.y;
        const stationX = selectedStation.x * this.scale.x;
        const stationY = selectedStation.y * this.scale.y;
        
        // Draw connection line
        this.ctx.strokeStyle = this.networkColors[this.decisionResult.selectedNetwork];
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash([5, 5]);
        
        this.ctx.beginPath();
        this.ctx.moveTo(deviceX, deviceY);
        this.ctx.lineTo(stationX, stationY);
        this.ctx.stroke();
        
        this.ctx.setLineDash([]); // Reset line dash
        
        // Draw connection label
        const midX = (deviceX + stationX) / 2;
        const midY = (deviceY + stationY) / 2;
        
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        this.ctx.fillRect(midX - 30, midY - 8, 60, 16);
        
        this.ctx.fillStyle = this.networkColors[this.decisionResult.selectedNetwork];
        this.ctx.font = '11px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(`${this.decisionResult.cost.toFixed(1)}`, midX, midY + 3);
    }
}

// Initialize the visualization when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.mapVisualization = new MapVisualization();
});

// Error handling for API calls
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});