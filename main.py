#!/usr/bin/env python
#--coding:utf-8--

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __parse_content__(self,con):
        dic=json.loads(s=con)
        
        return None
    # POST handler
    def do_POST(self):
        sendReply = False

        if sendReply == True:
            try:
                self.send_response(200)
                self.send_header('Content-type','application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write("success")
            except:
                self.send_error(404,'Error')

def run():
    port = 6666
    print('starting server, port', port)

    # Server settings
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    print('running server...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()