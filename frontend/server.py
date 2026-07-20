import os
import http.server
import socketserver

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    # Disable caching for seamless local development
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"============================================================")
        print(f"🚀 Avashya Drop Web Tier (S3 / Nginx Pattern) Running!")
        print(f"👉 Local Web URL: http://127.0.0.1:{PORT}")
        print(f"👉 Backend API  : http://127.0.0.1:8000")
        print(f"============================================================")
        httpd.serve_forever()
