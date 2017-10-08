#!/usr/bin/env python
"""
UI for a raspberry pi robot

"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import os
import sys
import cgi
import RPi.GPIO as GPIO

wheels = {"right":{"forward":40,"reverse":38},"left":{"forward":33,"reverse":37}}

class S(BaseHTTPRequestHandler):


    def forward(self):
        self.stop()
        GPIO.output(wheels["right"]["forward"], 1)
        GPIO.output(wheels["left"]["forward"], 1)

    def reverse(self):
        self.stop()
        GPIO.output(wheels["right"]["reverse"], 1)
        GPIO.output(wheels["left"]["reverse"], 1)

    def right(self):
        self.stop()
        GPIO.output(wheels["right"]["forward"], 1)
        GPIO.output(wheels["left"]["reverse"], 1)
        
    def left(self):
        self.stop()
        GPIO.output(wheels["right"]["reverse"], 1)
        GPIO.output(wheels["left"]["forward"], 1)
        
    def stop(self):
        GPIO.output(wheels["right"]["forward"], 0)
        GPIO.output(wheels["right"]["reverse"], 0)
        GPIO.output(wheels["left"]["forward"], 0)
        GPIO.output(wheels["left"]["reverse"], 0)
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        html = self.file_as_string("home.html")
        self.wfile.write(html)

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        self._set_headers()
        data = self.get_post_data()
        if data["dir"][0] == "F":
            self.forward()
        elif data["dir"][0] == "S":
            self.stop()
        elif data["dir"][0] == "B":
            self.reverse()
        elif data["dir"][0] == "R":
            self.right()
         elif data["dir"][0] == "L":
            self.left()
            
    def file_as_string(self, filename):
        f = open(os.path.join(sys.path[0], filename), 'r')
        return f.read()
        
    def get_post_data(self):
        length = int(self.headers.getheader('content-length'))
        return cgi.parse_qs(self.rfile.read(length), keep_blank_values=0)
        


def run(server_class=HTTPServer, handler_class=S, port=80):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(wheels["right"]["forward"], GPIO.OUT)
    GPIO.setup(wheels["right"]["reverse"], GPIO.OUT)
    GPIO.setup(wheels["left"]["forward"], GPIO.OUT)
    GPIO.setup(wheels["left"]["reverse"], GPIO.OUT)   

    
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
