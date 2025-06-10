#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Lamina Dashboard CLI Entry Point
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for lamina-dashboard CLI."""
    import os
    from .config import DashboardConfig
    
    # Load configuration
    config = DashboardConfig()
    server_config = config.get_server_config()
    
    print("🌬️ Starting Lamina Sanctuary Dashboard")
    print(f"🔧 Environment: {config.environment}")
    print(f"🔗 Access at: http://{server_config['host']}:{server_config['port']}")
    print("📊 Monitoring Lamina OS cluster state...")
    
    if config.should_use_gunicorn():
        # Production mode: Use Gunicorn
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gunicorn.conf.py')
        
        cmd = ['gunicorn', '--config', config_path]
        
        # Add configuration overrides
        if server_config.get('autoreload'):
            cmd.append('--reload')
        
        cmd.extend([
            '--bind', f"{server_config['host']}:{server_config['port']}",
            '--workers', str(server_config['workers']),
            '--worker-class', server_config['worker_class'],
            '--timeout', str(server_config['timeout']),
            'lamina_dashboard.app:app'
        ])
        
        print(f"🚀 Starting Gunicorn server: {' '.join(cmd)}")
        os.execvp(cmd[0], cmd)
    
    else:
        # Development mode: Use Flask dev server with auto-reload
        from .app import app, socketio, update_cluster_state
        import threading
        
        print("🔄 Starting development server with auto-reload")
        
        # Start background cluster monitoring
        update_thread = threading.Thread(target=update_cluster_state, daemon=True)
        update_thread.start()
        
        # Run with Flask dev server
        socketio.run(
            app, 
            host=server_config['host'], 
            port=server_config['port'], 
            debug=server_config['debug']
        )

if __name__ == '__main__':
    main()