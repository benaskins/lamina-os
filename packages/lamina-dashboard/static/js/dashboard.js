// Sanctuary Dashboard JavaScript

class SanctuaryDashboard {
    constructor() {
        this.socket = null;
        this.lastUpdateTime = null;
        this.clusterState = {};
        this.init();
    }

    init() {
        this.initWebSocket();
        this.bindEvents();
        this.updateConnectionStatus('connecting');
    }

    initWebSocket() {
        this.socket = io();

        this.socket.on('connect', () => {
            console.log('Connected to sanctuary dashboard');
            this.updateConnectionStatus('connected');
            this.socket.emit('request_update');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from sanctuary dashboard');
            this.updateConnectionStatus('disconnected');
        });

        this.socket.on('cluster_update', (data) => {
            console.log('Received cluster update:', data);
            console.log('📊 Health data received:', data.cluster_health);
            this.clusterState = data;
            this.updateDashboard(data);
            this.lastUpdateTime = new Date();
            this.updateLastUpdateTime();
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateConnectionStatus('error');
        });
    }

    bindEvents() {
        // Add click handlers for components
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('agent-circle')) {
                this.showAgentDetails(e.target.dataset.agentName);
            } else if (e.target.classList.contains('telemetry-item')) {
                this.openTelemetryUrl(e.target.dataset.url);
            }
        });

        // Update time every second
        setInterval(() => {
            this.updateLastUpdateTime();
        }, 1000);

        // Auto-refresh cluster data every 10 seconds
        setInterval(() => {
            if (this.socket && this.socket.connected) {
                this.socket.emit('request_update');
            }
        }, 10000);
    }

    updateConnectionStatus(status) {
        const indicator = document.getElementById('connection-status');
        const statusText = document.getElementById('last-update');

        indicator.className = 'status-indicator';
        
        switch(status) {
            case 'connected':
                indicator.classList.add('connected');
                indicator.style.color = 'var(--lamina-green)';
                statusText.textContent = 'Connected';
                break;
            case 'connecting':
                indicator.style.color = 'var(--lamina-orange)';
                statusText.textContent = 'Connecting...';
                break;
            case 'disconnected':
            case 'error':
                indicator.classList.add('disconnected');
                indicator.style.color = 'var(--lamina-red)';
                statusText.textContent = 'Disconnected';
                break;
        }
    }

    updateLastUpdateTime() {
        if (!this.lastUpdateTime) return;
        
        const now = new Date();
        const diffSeconds = Math.floor((now - this.lastUpdateTime) / 1000);
        const statusText = document.getElementById('last-update');
        
        if (diffSeconds < 60) {
            statusText.textContent = `Updated ${diffSeconds}s ago`;
        } else {
            const diffMinutes = Math.floor(diffSeconds / 60);
            statusText.textContent = `Updated ${diffMinutes}m ago`;
        }
    }

    updateDashboard(data) {
        this.updateIngress(data.ingress || {});
        this.updateAgents(data.agents || {});
        this.updateModels(data.models || {});
        this.updateMemory(data.memory_systems || {});
        this.updateTelemetry(data.telemetry || {});
        this.updateNetworkTraffic(data.network_traffic || {});
        this.updateClusterHealth(data.cluster_health || {});
        this.updatePodStatus();
    }

    async updatePodStatus() {
        try {
            const response = await fetch('/api/pod-states');
            const data = await response.json();
            this.updateProblematicPods(data.problematic_pods || []);
        } catch (error) {
            console.error('Error fetching pod states:', error);
        }
    }

    updateProblematicPods(problematicPods) {
        const container = document.getElementById('problematic-pods');
        container.innerHTML = '';
        
        if (problematicPods.length === 0) {
            container.innerHTML = '<div style="color: var(--lamina-green); text-align: center; padding: 10px;">✅ All pods healthy</div>';
            return;
        }
        
        problematicPods.forEach(pod => {
            const podElement = document.createElement('div');
            podElement.className = `pod-item ${pod.reason.toLowerCase().replace(/\s+/g, '-')}`;
            
            podElement.innerHTML = `
                <div class="pod-name">${pod.name}</div>
                <div class="pod-namespace">${pod.namespace}</div>
                <div class="pod-reason">${pod.reason}</div>
                <div class="pod-details">Phase: ${pod.phase} | Restarts: ${pod.restart_count} | Age: ${pod.age}</div>
            `;
            
            container.appendChild(podElement);
        });
    }

    updateIngress(ingress) {
        const container = document.getElementById('ingress-container');
        container.innerHTML = '';

        if (Object.keys(ingress).length === 0) {
            container.innerHTML = '<div class="empty-state">No ingress components detected</div>';
            return;
        }

        Object.values(ingress).forEach(component => {
            const card = this.createComponentCard(component);
            container.appendChild(card);
        });
    }

    updateAgents(agents) {
        const container = document.getElementById('agents-container');
        container.innerHTML = '';

        if (Object.keys(agents).length === 0) {
            container.innerHTML = '<div class="empty-state">No agents detected</div>';
            return;
        }

        Object.values(agents).forEach(agent => {
            const circle = this.createAgentCircle(agent);
            container.appendChild(circle);
        });
    }

    updateModels(models) {
        const container = document.getElementById('models-container');
        container.innerHTML = '';

        if (Object.keys(models).length === 0) {
            container.innerHTML = '<div class="empty-state">No model instances detected</div>';
            return;
        }

        Object.values(models).forEach(model => {
            const card = this.createComponentCard(model);
            container.appendChild(card);
        });
    }

    updateMemory(memory) {
        const container = document.getElementById('memory-container');
        container.innerHTML = '';

        if (Object.keys(memory).length === 0) {
            container.innerHTML = '<div class="empty-state">No memory systems detected</div>';
            return;
        }

        Object.values(memory).forEach(system => {
            const card = this.createComponentCard(system);
            container.appendChild(card);
        });
    }

    updateTelemetry(telemetry) {
        const container = document.getElementById('telemetry-container');
        container.innerHTML = '';

        if (Object.keys(telemetry).length === 0) {
            container.innerHTML = '<div class="empty-state">No telemetry components</div>';
            return;
        }

        Object.values(telemetry).forEach(component => {
            const item = this.createTelemetryItem(component);
            container.appendChild(item);
        });
    }

    updateNetworkTraffic(traffic) {
        this.updateTrafficMetrics(traffic.metrics || {});
        this.updateTrafficFlows(traffic.flows || []);
        this.drawTrafficVisualization(traffic.flows || []);
    }

    updateTrafficMetrics(metrics) {
        const overview = metrics.overview || {};
        
        // Update traffic overview metrics
        const requestRate = document.getElementById('request-rate');
        const errorRate = document.getElementById('error-rate');
        const activeFlows = document.getElementById('active-flows');

        if (requestRate) {
            const rate = overview.total_requests || 0;
            requestRate.textContent = `${rate.toFixed(2)} req/s`;
        }

        if (errorRate) {
            const error = overview.error_rate || 0;
            errorRate.textContent = `${error.toFixed(1)}%`;
        }

        if (activeFlows) {
            const flows = this.clusterState.network_traffic?.flows?.length || 0;
            activeFlows.textContent = flows.toString();
        }
    }

    updateTrafficFlows(flows) {
        const container = document.getElementById('traffic-flows');
        if (!container) return;
        
        container.innerHTML = '';

        if (flows.length === 0) {
            container.innerHTML = '<div class="empty-state">No active traffic flows</div>';
            return;
        }

        // Sort flows by rate (highest first)
        const sortedFlows = flows.sort((a, b) => (b.rate || 0) - (a.rate || 0));
        
        // Show top 10 flows
        sortedFlows.slice(0, 10).forEach(flow => {
            const flowItem = this.createTrafficFlowItem(flow);
            container.appendChild(flowItem);
        });
    }

    createTrafficFlowItem(flow) {
        const item = document.createElement('div');
        item.className = 'traffic-flow-item';
        
        if (flow.type) {
            item.classList.add(flow.type.replace('_', '-'));
        }

        if (flow.rate > 1) {
            item.classList.add('high-rate');
        }

        const source = document.createElement('div');
        source.className = 'flow-source';
        source.textContent = flow.source;

        const arrow = document.createElement('div');
        arrow.textContent = '→';
        arrow.style.textAlign = 'center';
        arrow.style.color = 'var(--lamina-gray)';

        const destination = document.createElement('div');
        destination.className = 'flow-destination';
        destination.textContent = flow.destination;

        const rate = document.createElement('div');
        rate.className = 'flow-rate';
        rate.textContent = `${flow.rate.toFixed(2)} req/s`;

        item.appendChild(source);
        item.appendChild(arrow);
        item.appendChild(destination);
        item.appendChild(rate);

        return item;
    }

    drawTrafficVisualization(flows) {
        const svg = document.getElementById('traffic-overlay');
        if (!svg) return;

        // Clear existing lines
        svg.innerHTML = '';

        const agentsContainer = document.getElementById('agents-container');
        if (!agentsContainer) return;

        const agentCircles = agentsContainer.querySelectorAll('.agent-circle');
        if (agentCircles.length < 2) return;

        // Create agent position map
        const agentPositions = {};
        agentCircles.forEach(circle => {
            const rect = circle.getBoundingClientRect();
            const containerRect = agentsContainer.getBoundingClientRect();
            
            agentPositions[circle.dataset.agentName] = {
                x: rect.left - containerRect.left + rect.width / 2,
                y: rect.top - containerRect.top + rect.height / 2
            };
        });

        // Draw traffic flows between agents
        flows.forEach(flow => {
            if (flow.type === 'agent_to_agent' && flow.rate > 0) {
                const sourcePos = agentPositions[flow.source];
                const destPos = agentPositions[flow.destination];
                
                if (sourcePos && destPos) {
                    this.drawTrafficLine(svg, sourcePos, destPos, flow);
                }
            }
        });
    }

    drawTrafficLine(svg, source, destination, flow) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        
        line.setAttribute('x1', source.x);
        line.setAttribute('y1', source.y);
        line.setAttribute('x2', destination.x);
        line.setAttribute('y2', destination.y);
        
        line.className = 'traffic-flow-line';
        if (flow.type) {
            line.classList.add(flow.type.replace('_', '-'));
        }
        
        if (flow.rate > 1) {
            line.classList.add('high-traffic');
        }

        // Add title for hover information
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${flow.source} → ${flow.destination}: ${flow.rate.toFixed(2)} req/s`;
        line.appendChild(title);

        svg.appendChild(line);
    }

    updateClusterHealth(health) {
        const healthText = document.getElementById('cluster-health-text');
        const healthFill = document.getElementById('cluster-health-fill');
        const breathingState = document.getElementById('breathing-state');
        const breathingCircle = document.getElementById('breathing-animation');

        if (health.overall_health !== undefined) {
            const healthPercent = Math.round(health.overall_health * 100);
            console.log(`🏥 Updating health display: ${health.overall_health} -> ${healthPercent}%`);
            healthText.textContent = `Cluster Health: ${healthPercent}%`;
            healthFill.style.width = `${healthPercent}%`;
            
            // Update health bar color
            if (healthPercent >= 80) {
                healthFill.style.background = 'var(--lamina-green)';
            } else if (healthPercent >= 50) {
                healthFill.style.background = 'var(--lamina-orange)';
            } else {
                healthFill.style.background = 'var(--lamina-red)';
            }
        }

        if (health.breathing_state) {
            breathingState.textContent = `Breathing: ${this.formatBreathingState(health.breathing_state)}`;
            
            // Update breathing animation
            breathingCircle.className = 'breathing-circle';
            if (health.breathing_state !== 'steady') {
                breathingCircle.classList.add(health.breathing_state);
            }
        }
    }

    createAgentCircle(agent) {
        const circle = document.createElement('div');
        circle.className = 'agent-circle';
        circle.dataset.agentName = agent.name;
        
        if (agent.ready) {
            circle.classList.add('ready');
        } else {
            circle.classList.add('not-ready');
        }

        if (agent.breathing === 'deep' || agent.breathing === 'steady') {
            circle.classList.add('breathing');
        }

        circle.textContent = agent.name;
        circle.title = `${agent.name} - ${agent.status} (${agent.essence})`;

        return circle;
    }

    createComponentCard(component) {
        const card = document.createElement('div');
        card.className = 'component-card';
        
        if (component.ready) {
            card.classList.add('ready');
        } else {
            card.classList.add('not-ready');
        }

        const title = document.createElement('h3');
        title.textContent = component.name;

        const status = document.createElement('div');
        status.className = 'status';
        if (!component.ready) {
            status.classList.add('not-ready');
        }
        status.textContent = component.ready ? 'Ready' : component.status;

        card.appendChild(title);
        card.appendChild(status);
        card.title = `${component.name} - ${component.status}`;

        return card;
    }

    createTelemetryItem(component) {
        const item = document.createElement('div');
        item.className = 'telemetry-item';
        
        if (component.ready) {
            item.classList.add('ready');
        } else {
            item.classList.add('not-ready');
        }

        if (component.url) {
            item.dataset.url = component.url;
            item.style.cursor = 'pointer';
        }

        item.textContent = component.name;
        item.title = `${component.name} - ${component.type}`;

        return item;
    }

    formatBreathingState(state) {
        const stateMap = {
            'steady': 'Steady',
            'shallow': 'Shallow',
            'irregular': 'Irregular',
            'distressed': 'Distressed',
            'silent': 'Silent',
            'deep': 'Deep',
            'held': 'Held'
        };
        return stateMap[state] || state;
    }

    showAgentDetails(agentName) {
        const agent = Object.values(this.clusterState.agents || {})
            .find(a => a.name === agentName);
        
        if (!agent) return;

        alert(`Agent: ${agent.name}\n` +
              `Status: ${agent.status}\n` +
              `Essence: ${agent.essence}\n` +
              `Namespace: ${agent.namespace}\n` +
              `Pod: ${agent.pod_name}\n` +
              `Breathing: ${agent.breathing}\n` +
              `Restarts: ${agent.restart_count}`);
    }

    openTelemetryUrl(url) {
        if (url) {
            window.open(url, '_blank');
        }
    }

    // Manual refresh
    refresh() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('request_update');
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SanctuaryDashboard();
});

// Expose refresh function globally
window.refreshDashboard = () => {
    if (window.dashboard) {
        window.dashboard.refresh();
    }
};