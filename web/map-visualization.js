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

        // CRITICAL: Read actual canvas size from element (not hardcoded!)
        this.canvasSize = {
            width: this.canvas.width,   // Get from canvas.width attribute
            height: this.canvas.height  // Get from canvas.height attribute
        };

        this.scale = {
            x: this.canvasSize.width / this.mapSize.width,    // 800/1000 = 0.8
            y: this.canvasSize.height / this.mapSize.height   // 600/1000 = 0.6
        };

        console.log('Canvas initialized:', {
            canvasElement: { width: this.canvas.width, height: this.canvas.height },
            mapSize: this.mapSize,
            scale: this.scale
        });

        // Simulation state
        this.devicePosition = { x: 0, y: 0 };
        this.currentTask = 'IDLE_MONITORING';
        this.availableNetworks = [];
        this.simulationStep = 0;
        this.isAutoRunning = false;
        this.autoRunTimer = null; // Store timer reference
        this.baseStations = [];
        this.decisionResult = null;
        this.connectedStation = null; // Track which specific station device is connected to
        this.animationFrameId = null; // Store animation frame ID

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
        document.getElementById('stepBtn').addEventListener('click', () => {
            console.log('Step button clicked');
            this.runSimulationStep();
        });
        document.getElementById('decisionBtn').addEventListener('click', () => {
            console.log('Decision button clicked');
            this.makeDecision();
        });
        document.getElementById('resetBtn').addEventListener('click', () => {
            console.log('Reset button clicked');
            this.resetSimulation();
        });

        // Auto-run toggle
        const autoToggle = document.getElementById('autoToggle');
        autoToggle.addEventListener('click', () => {
            console.log('Auto-run toggle clicked');
            this.toggleAutoRun();
        });

        // AI/ML toggle
        const useAIToggle = document.getElementById('useAIToggle');
        useAIToggle.addEventListener('click', () => {
            useAIToggle.classList.toggle('active');
            const isAI = useAIToggle.classList.contains('active');
            console.log('AI mode:', isAI ? 'ENABLED' : 'DISABLED');

            // Toggle body class for theme change
            if (isAI) {
                document.body.classList.remove('mcdm-mode');
                document.body.classList.add('ai-mode');
                document.getElementById('modeIndicator').textContent = 'AI MODE';
                this.updateStatusBar('🤖 AI/ML Mode enabled');
            } else {
                document.body.classList.remove('ai-mode');
                document.body.classList.add('mcdm-mode');
                document.getElementById('modeIndicator').textContent = 'MCDM MODE';
                this.updateStatusBar('📐 MCDM Mode enabled');
            }
        });

        // Canvas click for manual device placement
        this.canvas.addEventListener('click', (e) => {
            console.log('Canvas clicked at', e.clientX, e.clientY);
            this.handleCanvasClick(e);
        });

        // Resize handling
        window.addEventListener('resize', () => {
            console.log('Window resized');
            this.handleResize();
        });

        // Task selector
        const taskSelector = document.getElementById('taskSelector');
        taskSelector.addEventListener('change', (event) => {
            this.currentTask = event.target.value;
            console.log(`Task changed to: ${this.currentTask}`);
            this.updateUI();
            this.updateStatusBar(`Task changed to: ${this.currentTask}`);
        });
    }

    async checkApiStatus() {
        try {
            // Use /status endpoint instead of /health (which doesn't exist)
            const response = await fetch(`${this.apiBaseUrl}/status`);
            const data = await response.json();

            if (response.ok) {
                document.getElementById('apiStatus').textContent = '✅ Online';
                document.getElementById('apiStatus').style.color = '#4CAF50';
                this.updateStatusBar('API connected successfully');
                console.log('API Status:', data);
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
        // Initialize base stations - MUST MATCH app/services/simulation.py exactly!
        this.baseStations = [];

        // Wi-Fi stations (4 stations) - positions from simulation.py
        const wifiStations = [
            { id: 'WiFi-1', x: 100, y: 100, type: 'Wi-Fi' },
            { id: 'WiFi-2', x: 300, y: 250, type: 'Wi-Fi' },
            { id: 'WiFi-3', x: 600, y: 400, type: 'Wi-Fi' },
            { id: 'WiFi-4', x: 800, y: 750, type: 'Wi-Fi' }
        ];

        // 5G stations (4 stations) - positions from simulation.py
        const fiveGStations = [
            { id: '5G-1', x: 200, y: 200, type: '5G' },
            { id: '5G-2', x: 500, y: 300, type: '5G' },
            { id: '5G-3', x: 700, y: 600, type: '5G' },
            { id: '5G-4', x: 900, y: 100, type: '5G' }
        ];

        // BLE stations (4 stations) - positions from simulation.py
        const bleStations = [
            { id: 'BLE-1', x: 150, y: 150, type: 'BLE' },
            { id: 'BLE-2', x: 350, y: 350, type: 'BLE' },
            { id: 'BLE-3', x: 550, y: 550, type: 'BLE' },
            { id: 'BLE-4', x: 750, y: 750, type: 'BLE' }
        ];

        this.baseStations = [...wifiStations, ...fiveGStations, ...bleStations];
        console.log('Base stations initialized:', this.baseStations.length);
        this.updateStatusBar(`Initialized ${this.baseStations.length} base stations (4 Wi-Fi, 4 5G, 4 BLE)`);
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
            // Check AI/ML toggle state
            const useAIToggle = document.getElementById('useAIToggle');
            const useAI = useAIToggle.classList.contains('active');
            const endpoint = useAI ? '/decision/ml' : '/decision';

            this.updateStatusBar(useAI ? '🤖 Making AI/ML decision...' : '📐 Making MCDM decision...');

            const payload = {
                position: [this.devicePosition.x, this.devicePosition.y],
                current_task: this.currentTask,
                available_networks: this.availableNetworks
            };

            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
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

            // Handle different response formats (ML vs MCDM)
            if (useAI) {
                // ML response format
                this.decisionResult = {
                    selectedNetwork: data.selected_network,
                    stationId: data.station_id,
                    method: data.method,
                    confidence: data.confidence,
                    cost: null,
                    allCosts: null,
                    algorithm: 'Machine Learning'
                };
                this.connectedStation = data.station_id;
                this.updateStatusBar(`✅ [AI] Selected: ${data.selected_network} (Conf: ${(data.confidence * 100).toFixed(1)}%)`);
            } else {
                // MCDM response format
                this.decisionResult = {
                    selectedNetwork: data.optimal_network,
                    stationId: null,
                    method: 'MCDM',
                    confidence: null,
                    cost: data.optimal_cost,
                    allCosts: data.all_network_costs,
                    algorithm: data.decision_summary?.algorithm || 'MCDM'
                };
                this.updateStatusBar(`✅ [MCDM] Selected: ${data.optimal_network} (Cost: ${data.optimal_cost.toFixed(2)})`);
            }

            this.updateDecisionDisplay();
            this.draw();

        } catch (error) {
            console.error('Decision making failed:', error);
            this.updateStatusBar('❌ Decision making failed');
        }
    }

    async resetSimulation() {
        try {
            this.updateStatusBar('🔄 Resetting simulation...');

            // CRITICAL: Stop auto-run before reset
            if (this.isAutoRunning) {
                console.log('Stopping auto-run before reset');
                this.toggleAutoRun();
            }

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
            console.log('Simulation reset complete');

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
            console.log('Auto-run STARTED');
        } else {
            toggle.classList.remove('active');
            this.updateStatusBar('⏸️ Auto-run disabled');
            console.log('Auto-run STOPPED');
        }
    }

    startAutoRunTimer() {
        // Clear any existing timer
        if (this.autoRunTimer) {
            clearInterval(this.autoRunTimer);
        }

        // Start new timer
        this.autoRunTimer = setInterval(() => {
            if (this.isAutoRunning) {
                console.log('Auto-run tick: running simulation step');
                this.runSimulationStep();
            }
        }, 2000); // Run every 2 seconds

        console.log('Auto-run timer initialized');
    }

    handleCanvasClick(event) {
        const rect = this.canvas.getBoundingClientRect();

        // Get click position relative to canvas bounds
        const clickX = event.clientX - rect.left;
        const clickY = event.clientY - rect.top;

        // Scale from displayed size to canvas internal size
        const displayToCanvasScaleX = this.canvas.width / rect.width;
        const displayToCanvasScaleY = this.canvas.height / rect.height;

        const canvasX = clickX * displayToCanvasScaleX;
        const canvasY = clickY * displayToCanvasScaleY;

        // Convert canvas pixels to map coordinates
        const mapX = canvasX / this.scale.x;
        const mapY = canvasY / this.scale.y;

        // Round and clamp to map bounds
        const clampedX = Math.max(0, Math.min(this.mapSize.width, Math.round(mapX)));
        const clampedY = Math.max(0, Math.min(this.mapSize.height, Math.round(mapY)));

        // Update device position
        this.devicePosition = { x: clampedX, y: clampedY };

        // Clear decision result when manually placing device
        this.decisionResult = null;
        this.connectedStation = null;

        // Recalculate available networks for new position
        this.updateNetworksForPosition();

        // Redraw map and update UI
        this.draw();
        this.updateUI();

        this.updateStatusBar(`Device moved to (${clampedX}, ${clampedY}) manually`);
    }

    updateNetworksForPosition() {
        // Calculate which networks are available at current device position
        // This is a client-side approximation - backend has the physics model

        this.availableNetworks = [];

        // Check EVERY base station individually
        this.baseStations.forEach(station => {
            const dx = this.devicePosition.x - station.x;
            const dy = this.devicePosition.y - station.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // Rough approximation of availability (backend has exact physics)
            const maxRange = station.type === 'BLE' ? 100 : (station.type === 'Wi-Fi' ? 200 : 400);

            // If station is in range, add it to available networks
            if (distance < maxRange) {
                // Approximate QoS (not accurate - use backend for real values)
                const signalStrength = 1 - (distance / maxRange);
                const bandwidth = station.type === '5G' ? 100 * signalStrength :
                    station.type === 'Wi-Fi' ? 80 * signalStrength :
                        2 * signalStrength;
                const latency = Math.round(10 + (distance / 10));

                this.availableNetworks.push({
                    name: station.type,
                    station_id: station.id,
                    bandwidth: bandwidth,
                    latency: latency,
                    distance: distance,
                    is_available: true
                });
            }
        });

        console.log(`Position (${this.devicePosition.x}, ${this.devicePosition.y}): ${this.availableNetworks.length} stations available`);
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
            const stationLabel = network.station_id || network.name;
            const distanceText = network.distance ? ` • ${network.distance.toFixed(0)}m` : '';

            return `
                <div class="network-item">
                    <div>
                        <div class="network-name">
                            <span class="network-badge ${badgeClass}">${stationLabel}</span>
                        </div>
                        <div class="network-stats">
                            ${network.bandwidth.toFixed(1)} Mbps • ${network.latency}ms${distanceText}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateDecisionDisplay() {
        const decisionElement = document.getElementById('decisionResult');

        if (!this.decisionResult) {
            decisionElement.classList.remove('visible');
            return;
        }

        decisionElement.classList.add('visible');

        // Update selected network name
        document.getElementById('selectedNetwork').textContent = this.decisionResult.selectedNetwork;

        // Update decision method label
        const decisionMethod = document.getElementById('decisionMethod');
        const confidenceMetric = document.getElementById('confidenceMetric');
        const costMetric = document.getElementById('costMetric');

        if (this.decisionResult.method === 'ML' || this.decisionResult.method === 'MCDM_Fallback') {
            // AI/ML mode
            decisionMethod.textContent = 'AI SELECTED';

            // Show confidence, hide cost
            confidenceMetric.style.display = 'block';
            costMetric.style.display = 'none';

            const confidence = this.decisionResult.confidence !== null
                ? this.decisionResult.confidence * 100
                : 0;
            document.getElementById('confidenceValue').textContent = `${confidence.toFixed(1)}%`;
            document.getElementById('confidenceBar').style.width = `${confidence}%`;
        } else {
            // MCDM mode
            decisionMethod.textContent = 'MATH CALCULATED';

            // Show cost, hide confidence
            confidenceMetric.style.display = 'none';
            costMetric.style.display = 'block';

            const cost = this.decisionResult.cost !== null ? this.decisionResult.cost : 0;
            document.getElementById('costValue').textContent = cost.toFixed(2);
            // Normalize cost to 0-100 for progress bar (assume max cost = 50)
            const costPercent = Math.min(100, (cost / 50) * 100);
            document.getElementById('costBar').style.width = `${costPercent}%`;
        }

        // Update cost comparison if available (MCDM only)
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
        } else {
            // Clear cost comparison for ML mode
            costComparison.innerHTML = `<div style="text-align: center; color: rgba(255,255,255,0.5); padding: 10px; font-size: 12px;">Method: ${this.decisionResult.method || 'ML'}</div>`;
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
        const time = Date.now() / 1000;

        this.baseStations.forEach(station => {
            const x = station.x * this.scale.x;
            const y = station.y * this.scale.y;
            const radius = 10;

            // Check if this station is connected
            const isConnected = this.connectedStation && this.connectedStation === station.id;

            // Draw glow effect for connected station
            if (isConnected) {
                const glowRadius = radius + 8 + Math.sin(time * 3) * 3;
                this.ctx.shadowColor = this.networkColors[station.type];
                this.ctx.shadowBlur = 20;
                this.ctx.strokeStyle = this.networkColors[station.type];
                this.ctx.lineWidth = 3;
                this.ctx.beginPath();
                this.ctx.arc(x, y, glowRadius, 0, 2 * Math.PI);
                this.ctx.stroke();
                this.ctx.shadowBlur = 0;
            }

            // Draw station circle
            this.ctx.fillStyle = this.networkColors[station.type] || '#666';
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.fill();

            // Draw station border (brighter if connected)
            this.ctx.strokeStyle = isConnected ? '#FFD700' : 'white';
            this.ctx.lineWidth = isConnected ? 3 : 2;
            this.ctx.stroke();

            // Draw antenna icon in center
            this.ctx.fillStyle = 'white';
            this.ctx.font = 'bold 12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText('📡', x, y);

            // Draw station ID label with background
            const label = station.id || station.type;
            const labelWidth = this.ctx.measureText(label).width + 8;

            this.ctx.fillStyle = isConnected ? 'rgba(255, 215, 0, 0.9)' : 'rgba(255, 255, 255, 0.9)';
            this.ctx.fillRect(x - labelWidth / 2, y + 14, labelWidth, 14);

            this.ctx.strokeStyle = this.networkColors[station.type];
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(x - labelWidth / 2, y + 14, labelWidth, 14);

            this.ctx.fillStyle = '#333';
            this.ctx.font = 'bold 9px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(label, x, y + 21);
        });
    }

    drawCoverageAreas() {
        // Draw coverage areas for all base stations (not just available)
        // Show realistic range based on network type

        const coverageRanges = {
            'Wi-Fi': 200,   // meters - indoor coverage
            '5G': 400,      // meters - outdoor urban
            'BLE': 100      // meters - short range
        };

        this.baseStations.forEach(station => {
            const x = station.x * this.scale.x;
            const y = station.y * this.scale.y;
            const maxRange = coverageRanges[station.type] || 200;
            const radius = maxRange * this.scale.x;

            // Check if device is within this station's range
            const dx = this.devicePosition.x - station.x;
            const dy = this.devicePosition.y - station.y;
            const deviceDistance = Math.sqrt(dx * dx + dy * dy);
            const isInRange = deviceDistance < maxRange;

            // Draw coverage circle
            this.ctx.fillStyle = this.networkColors[station.type] + (isInRange ? '30' : '10');
            this.ctx.strokeStyle = this.networkColors[station.type] + (isInRange ? '80' : '30');
            this.ctx.lineWidth = isInRange ? 2 : 1;
            this.ctx.setLineDash(isInRange ? [] : [5, 5]);

            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.stroke();

            this.ctx.setLineDash([]);
        });
    }

    drawDevice() {
        const x = this.devicePosition.x * this.scale.x;
        const y = this.devicePosition.y * this.scale.y;
        const radius = 14;

        // Draw animated pulse effect (expanding circles)
        const time = Date.now() / 1000;
        const pulseRadius1 = radius + 10 + Math.sin(time * 2) * 5;
        const pulseRadius2 = radius + 20 + Math.sin(time * 2 + Math.PI) * 5;

        this.ctx.strokeStyle = 'rgba(255, 68, 68, 0.3)';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(x, y, pulseRadius1, 0, 2 * Math.PI);
        this.ctx.stroke();

        this.ctx.strokeStyle = 'rgba(255, 68, 68, 0.15)';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(x, y, pulseRadius2, 0, 2 * Math.PI);
        this.ctx.stroke();

        // Draw device circle with glow
        this.ctx.shadowColor = '#FF4444';
        this.ctx.shadowBlur = 15;
        this.ctx.fillStyle = '#FF4444';
        this.ctx.strokeStyle = 'white';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;

        // Draw center dot for precise position
        this.ctx.fillStyle = 'white';
        this.ctx.beginPath();
        this.ctx.arc(x, y, 3, 0, 2 * Math.PI);
        this.ctx.fill();

        // Draw device icon
        this.ctx.fillStyle = 'white';
        this.ctx.font = '16px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('📡', x, y);

        // Task indicator badge
        const taskColors = {
            'IDLE_MONITORING': '#4CAF50',
            'DATA_BURST_ALERT': '#FF9800',
            'VIDEO_STREAMING': '#E91E63'
        };

        const taskLabels = {
            'IDLE_MONITORING': 'I',
            'DATA_BURST_ALERT': 'A',
            'VIDEO_STREAMING': 'V'
        };

        const badgeX = x + 20;
        const badgeY = y - 20;

        this.ctx.fillStyle = taskColors[this.currentTask] || '#666';
        this.ctx.strokeStyle = 'white';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(badgeX, badgeY, 7, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.fillStyle = 'white';
        this.ctx.font = 'bold 10px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(taskLabels[this.currentTask] || '?', badgeX, badgeY);

        // Request animation frame for continuous pulse effect
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        this.animationFrameId = requestAnimationFrame(() => this.draw());
        // Position label
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.fillRect(x - 35, y + 25, 70, 16);

        this.ctx.fillStyle = 'white';
        this.ctx.font = 'bold 10px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(`(${this.devicePosition.x}, ${this.devicePosition.y})`, x, y + 33);
    }

    drawNetworkConnections() {
        if (!this.decisionResult) return;

        const networkType = this.decisionResult.selectedNetwork;
        const stationsOfType = this.baseStations.filter(s => s.type === networkType);

        if (stationsOfType.length === 0) return;

        // Find closest station of the selected type
        let closestStation = null;
        let minDistance = Infinity;

        stationsOfType.forEach(station => {
            const dx = this.devicePosition.x - station.x;
            const dy = this.devicePosition.y - station.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < minDistance) {
                minDistance = distance;
                closestStation = station;
            }
        });

        if (!closestStation) return;

        // Store for reference
        this.connectedStation = closestStation;

        const deviceX = this.devicePosition.x * this.scale.x;
        const deviceY = this.devicePosition.y * this.scale.y;
        const stationX = closestStation.x * this.scale.x;
        const stationY = closestStation.y * this.scale.y;

        // Draw connection line
        this.ctx.strokeStyle = this.networkColors[networkType];
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash([8, 4]);
        this.ctx.beginPath();
        this.ctx.moveTo(deviceX, deviceY);
        this.ctx.lineTo(stationX, stationY);
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // Highlight connected station
        this.ctx.strokeStyle = this.networkColors[networkType];
        this.ctx.lineWidth = 4;
        this.ctx.setLineDash([2, 2]);
        this.ctx.beginPath();
        this.ctx.arc(stationX, stationY, 16, 0, 2 * Math.PI);
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // Find network state for detailed metrics
        const networkState = this.availableNetworks.find(n => n.name === networkType);

        // Draw detailed info box
        const midX = (deviceX + stationX) / 2;
        const midY = (deviceY + stationY) / 2;

        const boxWidth = 150;
        const boxHeight = networkState ? 95 : 45;
        const boxX = midX - boxWidth / 2;
        const boxY = midY - boxHeight / 2;

        // Box background
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
        this.ctx.strokeStyle = this.networkColors[networkType];
        this.ctx.lineWidth = 2;
        this.ctx.fillRect(boxX, boxY, boxWidth, boxHeight);
        this.ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);

        // Header with station ID
        this.ctx.fillStyle = this.networkColors[networkType];
        this.ctx.fillRect(boxX, boxY, boxWidth, 20);

        this.ctx.fillStyle = 'white';
        this.ctx.font = 'bold 11px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(`📡 ${closestStation.id}`, midX, boxY + 10);

        if (networkState) {
            // Metrics
            this.ctx.fillStyle = '#333';
            this.ctx.font = '9px Consolas, monospace';
            this.ctx.textAlign = 'left';

            let lineY = boxY + 30;
            const lineHeight = 11;
            const leftMargin = boxX + 8;

            this.ctx.fillText(`📶 BW: ${networkState.bandwidth.toFixed(1)} Mbps`, leftMargin, lineY);
            lineY += lineHeight;
            this.ctx.fillText(`⏱️ Lat: ${networkState.latency} ms`, leftMargin, lineY);
            lineY += lineHeight;

            if (networkState.rssi !== undefined) {
                this.ctx.fillText(`📡 RSSI: ${networkState.rssi.toFixed(1)} dBm`, leftMargin, lineY);
                lineY += lineHeight;
            }

            if (networkState.snr !== undefined) {
                this.ctx.fillText(`🔊 SNR: ${networkState.snr.toFixed(1)} dB`, leftMargin, lineY);
                lineY += lineHeight;
            }

            if (networkState.packet_loss_rate !== undefined) {
                this.ctx.fillText(`📉 PLR: ${(networkState.packet_loss_rate * 100).toFixed(1)}%`, leftMargin, lineY);
                lineY += lineHeight;
            }

            // Distance and cost footer
            this.ctx.fillStyle = '#666';
            this.ctx.font = 'bold 9px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(`${minDistance.toFixed(0)}m • Cost: ${this.decisionResult.cost.toFixed(2)}`, midX, boxY + boxHeight - 8);
        } else {
            this.ctx.fillStyle = '#666';
            this.ctx.font = '10px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(`Distance: ${minDistance.toFixed(0)}m`, midX, boxY + 32);
        }
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