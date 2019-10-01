import http.server
import socketserver
import socket

PORT = 8080
class showipHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
    def do_GET(self):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        retstr = "<html><head><title>hello</title></head><body> hello %s </body></html>" \
        % socket.gethostbyname(socket.gethostname())
        s.wfile.write(retstr.encode())
httpd  = socketserver.TCPServer(("", PORT), showipHTTPHandler)
print("serving at port", PORT)
httpd.serve_forever()
