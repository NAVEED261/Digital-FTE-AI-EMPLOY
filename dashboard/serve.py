#!/usr/bin/env python3
"""
Simple HTTP server for Digital FTE Dashboard - Development Use Only
Run: python3 serve.py
Access: http://localhost:8080
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
DASHBOARD_DIR = Path(__file__).parent

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def end_headers(self):
        # Add cache control headers for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        # Enhanced logging
        print(f'[{self.log_date_time_string()}] {format % args}')

def run_server():
    """Start the development server"""
    os.chdir(DASHBOARD_DIR)

    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════╗
║   Digital FTE Dashboard - Development Server          ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║   🌐 Server running at: http://localhost:{PORT}          ║
║   📁 Serving from: {DASHBOARD_DIR}
║                                                        ║
║   📊 Dashboard: http://localhost:{PORT}/index.html       ║
║   📡 API Status: http://localhost:{PORT}/api/status.json║
║                                                        ║
║   Press Ctrl+C to stop the server                     ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
        """)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            raise

if __name__ == '__main__':
    run_server()
