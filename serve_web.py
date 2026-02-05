#!/usr/bin/env python3
"""Simple HTTP server to serve the web app on port 5000."""

import http.server
import socketserver
import os

PORT = 5000
DIRECTORY = "web"

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), NoCacheHTTPRequestHandler) as httpd:
        print(f"Serving web app at http://0.0.0.0:{PORT}")
        print(f"Serving files from: {DIRECTORY}/")
        httpd.serve_forever()
