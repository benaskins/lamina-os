#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Sanctuary Cluster Visualization Dashboard

A web-based dashboard that visualizes Kubernetes cluster state through
Lamina OS abstractions (sanctuaries, agents, breathing patterns).
"""

# CRITICAL: Import eventlet first and patch before any other modules
import eventlet

eventlet.monkey_patch()

import os
import time
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
from flask_wtf.csrf import CSRFProtect

from .config import DashboardConfig
from .core.cluster_translator import ClusterTranslator
from .integrations.kubernetes import KubernetesClient
from .integrations.prometheus import PrometheusClient

# Get the directory where this app.py file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Templates and static are in the parent directory
parent_dir = os.path.dirname(current_dir)

app = Flask(
    __name__,
    template_folder=os.path.join(parent_dir, "templates"),
    static_folder=os.path.join(parent_dir, "static"),
)

# Security Configuration
# Use environment variable for SECRET_KEY, fallback to generating a secure random key
app.config["SECRET_KEY"] = (
    os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY") or os.urandom(24).hex()
)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Configure CSRF settings
app.config["WTF_CSRF_TIME_LIMIT"] = None  # No time limit for dashboard usage
app.config["WTF_CSRF_SSL_STRICT"] = False  # Allow HTTP for local development

# Configure SocketIO with security considerations
# Only allow specific origins in production
allowed_origins = os.getenv("DASHBOARD_ALLOWED_ORIGINS", "*").split(",")
socketio = SocketIO(app, cors_allowed_origins=allowed_origins)

# Load configuration and initialize components
config = DashboardConfig()
monitoring_config = config.get_monitoring_config()

k8s_client = KubernetesClient()
prometheus_client = PrometheusClient()
translator = ClusterTranslator(k8s_client, prometheus_client)

# Global state for real-time updates - use thread-safe approach
cluster_state = {
    "last_updated": None,
    "sanctuaries": {},
    "agents": {},
    "models": {},
    "memory_systems": {},
    "telemetry": {},
}


# Security Headers Middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    # Content Security Policy - restrict resource loading
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Allow inline scripts for dashboard functionality
        "style-src 'self' 'unsafe-inline'; "  # Allow inline styles
        "img-src 'self' data:; "  # Allow data URLs for images
        "connect-src 'self' ws: wss:; "  # Allow WebSocket connections
        "font-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self';"
    )
    response.headers["Content-Security-Policy"] = csp_policy

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # XSS Protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Only send HSTS header over HTTPS
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


def _is_allowed_origin(origin):
    """Check if origin is in allowed list."""
    if "*" in allowed_origins:
        return True
    return origin in allowed_origins


def _validate_origin(func):
    """Decorator to validate request origin for API endpoints."""

    def wrapper(*args, **kwargs):
        origin = request.headers.get("Origin")
        if origin and not _is_allowed_origin(origin):
            return jsonify({"error": "Invalid origin"}), 403
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# No background monitoring in web app - keep it simple and stable
# WebSocket will only send data when API endpoints are called


@app.route("/")
def dashboard():
    """Main dashboard page."""
    # Add cache-busting timestamp
    timestamp = str(int(time.time()))
    return render_template("dashboard.html", cache_bust=timestamp)


@csrf.exempt
@_validate_origin
@app.route("/api/cluster/state")
def get_cluster_state():
    """Get current cluster state in Lamina abstractions."""
    try:
        # Force fresh data fetch to avoid stale global state in multiprocess environment
        print("🔄 Fetching fresh cluster data for API request")
        raw_data = k8s_client.get_cluster_snapshot()
        k8s_translator = ClusterTranslator(k8s_client, None)
        fresh_data = k8s_translator.translate_cluster_state(raw_data)
        fresh_data["last_updated"] = datetime.now().isoformat()
        print(
            f"✅ Fresh data: {fresh_data.get('cluster_health', {}).get('total_pods')} pods, {fresh_data.get('cluster_health', {}).get('overall_health')} health"
        )
        return jsonify(fresh_data)
    except Exception as e:
        print(f"❌ Error fetching fresh cluster state: {e}")
        # Fallback to global state if fresh fetch fails
        return jsonify(cluster_state)


def get_fresh_cluster_data():
    """Helper function to get fresh cluster data."""
    try:
        raw_data = k8s_client.get_cluster_snapshot()
        k8s_translator = ClusterTranslator(k8s_client, None)
        return k8s_translator.translate_cluster_state(raw_data)
    except Exception as e:
        print(f"Error fetching fresh data: {e}")
        return cluster_state


@csrf.exempt
@_validate_origin
@app.route("/api/sanctuaries")
def get_sanctuaries():
    """Get all sanctuary information."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get("sanctuaries", {}))


@csrf.exempt
@_validate_origin
@app.route("/api/agents")
def get_agents():
    """Get all agent status and information."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get("agents", {}))


@csrf.exempt
@_validate_origin
@app.route("/api/models")
def get_models():
    """Get model serving status."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get("models", {}))


@csrf.exempt
@_validate_origin
@app.route("/api/memory")
def get_memory_systems():
    """Get memory system status."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get("memory_systems", {}))


@csrf.exempt
@_validate_origin
@app.route("/api/telemetry")
def get_telemetry():
    """Get telemetry and observability status."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get("telemetry", {}))


@csrf.exempt
@_validate_origin
@app.route("/api/traffic")
def get_network_traffic():
    """Get network traffic flows and metrics."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get("network_traffic", {"flows": [], "metrics": {}}))


@csrf.exempt
@_validate_origin
@app.route("/api/pod-states")
def get_pod_states():
    """Get detailed pod state information including problematic pods."""
    fresh_data = get_fresh_cluster_data()
    cluster_health = fresh_data.get("cluster_health", {})
    return jsonify(
        {
            "pod_states": cluster_health.get("pod_states", {}),
            "problematic_pods": cluster_health.get("problematic_pods", []),
            "summary": {
                "total_pods": cluster_health.get("total_pods", 0),
                "ready_pods": cluster_health.get("ready_pods", 0),
                "failing_pods": cluster_health.get("failing_pods", 0),
                "overall_health": cluster_health.get("overall_health", 0),
            },
        }
    )


@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    print("Client connected")
    # Send fresh data on connect
    fresh_data = get_fresh_cluster_data()
    emit("cluster_update", fresh_data)


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    print("Client disconnected")


@socketio.on("request_update")
def handle_update_request():
    """Handle manual update request from client."""
    # Always send fresh data on request
    fresh_data = get_fresh_cluster_data()
    emit("cluster_update", fresh_data)


# Simplified startup - no background threads
print("🌬️ Sanctuary Dashboard initialized")
print("📊 Using on-demand cluster state fetching")
print("🔗 WebSocket support enabled")

if __name__ == "__main__":
    print("🌬️ Starting Sanctuary Dashboard")
    print("🔗 Access at: http://localhost:5001")
    print("📊 Monitoring Lamina OS cluster state...")
    # Start Flask app with SocketIO - use environment-based debug setting
    debug_mode = config.get("server.debug", False)
    socketio.run(app, host="0.0.0.0", port=5001, debug=debug_mode)
