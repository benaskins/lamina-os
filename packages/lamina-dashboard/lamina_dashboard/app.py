#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Sanctuary Cluster Visualization Dashboard

A web-based dashboard that visualizes Kubernetes cluster state through
Lamina OS abstractions (sanctuaries, agents, breathing patterns).
"""

import asyncio
import json
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time

from .core.cluster_translator import ClusterTranslator
from .integrations.kubernetes import KubernetesClient
from .integrations.prometheus import PrometheusClient
from .config import DashboardConfig

import os

# Get the directory where this app.py file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Templates and static are in the parent directory
parent_dir = os.path.dirname(current_dir)

app = Flask(__name__, 
           template_folder=os.path.join(parent_dir, 'templates'),
           static_folder=os.path.join(parent_dir, 'static'))
app.config['SECRET_KEY'] = 'lamina-sanctuary-dashboard'
socketio = SocketIO(app, cors_allowed_origins="*")

# Load configuration and initialize components
config = DashboardConfig()
monitoring_config = config.get_monitoring_config()

k8s_client = KubernetesClient()
prometheus_client = PrometheusClient()
translator = ClusterTranslator(k8s_client, prometheus_client)

# Global state for real-time updates
cluster_state = {
    'last_updated': None,
    'sanctuaries': {},
    'agents': {},
    'models': {},
    'memory_systems': {},
    'telemetry': {}
}

def update_cluster_state():
    """Background task to continuously update cluster state."""
    while True:
        try:
            # Get raw cluster data
            raw_data = k8s_client.get_cluster_snapshot()
            
            # Create translator without Prometheus to avoid failing queries
            k8s_translator = ClusterTranslator(k8s_client, None)
            lamina_data = k8s_translator.translate_cluster_state(raw_data)
            
            # Update global state
            global cluster_state
            cluster_state.update(lamina_data)
            cluster_state['last_updated'] = datetime.now().isoformat()
            
            # Emit updates to connected clients
            socketio.emit('cluster_update', cluster_state)
            print(f"✅ Cluster state updated: {len(lamina_data.get('sanctuaries', {}))} sanctuaries, {len(lamina_data.get('telemetry', {}))} telemetry")
            
        except Exception as e:
            print(f"Error updating cluster state: {e}")
            import traceback
            traceback.print_exc()
        
        # Use configurable update interval
        time.sleep(monitoring_config.get('update_interval', 5))

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/cluster/state')
def get_cluster_state():
    """Get current cluster state in Lamina abstractions."""
    return jsonify(cluster_state)

@app.route('/api/sanctuaries')
def get_sanctuaries():
    """Get all sanctuary information."""
    return jsonify(cluster_state.get('sanctuaries', {}))

@app.route('/api/agents')
def get_agents():
    """Get all agent status and information."""
    return jsonify(cluster_state.get('agents', {}))

@app.route('/api/models')
def get_models():
    """Get model serving status."""
    return jsonify(cluster_state.get('models', {}))

@app.route('/api/memory')
def get_memory_systems():
    """Get memory system status."""
    return jsonify(cluster_state.get('memory_systems', {}))

@app.route('/api/telemetry')
def get_telemetry():
    """Get telemetry and observability status."""
    return jsonify(cluster_state.get('telemetry', {}))

@app.route('/api/traffic')
def get_network_traffic():
    """Get network traffic flows and metrics."""
    return jsonify(cluster_state.get('network_traffic', {'flows': [], 'metrics': {}}))

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('cluster_update', cluster_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request from client."""
    emit('cluster_update', cluster_state)

# Start background monitoring when module is loaded (for Gunicorn)
def start_monitoring():
    """Start the background monitoring thread."""
    try:
        if not hasattr(app, '_monitoring_started'):
            update_thread = threading.Thread(target=update_cluster_state, daemon=True)
            update_thread.start()
            app._monitoring_started = True
            print("🔄 Background cluster monitoring started")
            
            # Force an immediate update
            try:
                raw_data = k8s_client.get_cluster_snapshot()
                k8s_translator = ClusterTranslator(k8s_client, None)
                lamina_data = k8s_translator.translate_cluster_state(raw_data)
                global cluster_state
                cluster_state.update(lamina_data)
                cluster_state['last_updated'] = datetime.now().isoformat()
                print(f"🚀 Initial cluster state loaded: {len(lamina_data.get('sanctuaries', {}))} sanctuaries, {len(lamina_data.get('telemetry', {}))} telemetry")
            except Exception as e:
                print(f"Failed to load initial cluster state: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"Failed to start monitoring: {e}")
        import traceback
        traceback.print_exc()

# Start monitoring immediately
start_monitoring()

if __name__ == '__main__':
    print("🌬️ Starting Sanctuary Dashboard")
    print("🔗 Access at: http://localhost:5001")
    print("📊 Monitoring Lamina OS cluster state...")
    
    # Start Flask app with SocketIO (development mode)
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)