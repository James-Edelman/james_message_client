# ripped from https://pythonbasics.org/webserver/
# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

hostName = "localhost"
PORT = 8080
myfile = open("textfile.txt", "wt")

test_html = r"""
<html>
    <form action="/textfile.txt" method="post">
        <input type="text" id="text" name="text">
    </form>
</html>
"""

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(test_html, "utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = urllib.parse.parse_qs(post_data)
        post_data = post_data.get('text', [''])[0]

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST request received")
        print(post_data)
  
webServer = HTTPServer((hostName, PORT), MyServer)

print(f"Server started http://{hostName}:{PORT}")

webServer.serve_forever()
webServer.server_close()

print("Server stopped.")