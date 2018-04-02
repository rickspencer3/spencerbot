#!/usr/bin/env python
"""
UI for a raspberry pi robot

"""

ui_only_mode = False

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from sys import argv
import getopt


import SocketServer
import os
import sys
import cgi

print getopt.getopt(argv[1:],["uionly","u"])

if len(argv) == 2:
    if argv[1] == "--uionly":
        print "running in UI debug mode. Not loading GPIO"
        ui_only_mode = True
else:
    import RPi.GPIO as GPIO


wheels = {"front":{"right":{"forward":40,"reverse":38},"left":{"forward":33,"reverse":37}},"back":{"right":{"forward":18,"reverse":15},"left":{"forward":16,"reverse":12}}}


class S(BaseHTTPRequestHandler):
    def forward(self):
        self.stop()
        GPIO.output(wheels["front"]["right"]["forward"], 1)
        GPIO.output(wheels["front"]["left"]["forward"], 1)
        GPIO.output(wheels["back"]["right"]["forward"], 1)
        GPIO.output(wheels["back"]["left"]["forward"], 1)


    def reverse(self):
        self.stop()
        GPIO.output(wheels["front"]["right"]["reverse"], 1)
        GPIO.output(wheels["front"]["left"]["reverse"], 1)
        GPIO.output(wheels["back"]["right"]["reverse"], 1)
        GPIO.output(wheels["back"]["left"]["reverse"], 1)

    def right(self):
        self.stop()
        GPIO.output(wheels["front"]["left"]["forward"], 1)
        GPIO.output(wheels["back"]["left"]["forward"], 1)
        
    def left(self):
        self.stop()
        GPIO.output(wheels["front"]["right"]["forward"], 1)
        GPIO.output(wheels["back"]["right"]["forward"], 1)
        
    def stop(self):
        GPIO.output(wheels["front"]["right"]["forward"], 0)
        GPIO.output(wheels["front"]["right"]["reverse"], 0)
        GPIO.output(wheels["front"]["left"]["forward"], 0)
        GPIO.output(wheels["front"]["left"]["reverse"], 0)
        GPIO.output(wheels["back"]["right"]["forward"], 0)
        GPIO.output(wheels["back"]["right"]["reverse"], 0)
        GPIO.output(wheels["back"]["left"]["forward"], 0)
        GPIO.output(wheels["back"]["left"]["reverse"], 0)

    
    def _set_headers(self, type):
        self.send_response(200)
        if type == "htlm":
            self.send_header('Content-type', 'text/html')
        if type == "image":
            self.send_header('Content-type', 'image/png')
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self._set_headers("html")
            html = self.file_as_string("home.html")
            self.wfile.write(html)
        else:
            self._set_headers("image")
            img = self.file_as_binary(self.path)
            self.wfile.write(img)
        
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
            
    def file_as_binary(self, filename):
        if filename.startswith("/"):
            filename=filename[1:]
        f = open(os.path.join(sys.path[0], filename), 'rb')
        return f.read()
            
    def file_as_string(self, filename):
        f = open(os.path.join(sys.path[0], filename), 'r')
        return f.read()
        
    def get_post_data(self):
        length = int(self.headers.getheader('content-length'))
        return cgi.parse_qs(self.rfile.read(length), keep_blank_values=0)
        


def run(server_class=HTTPServer, handler_class=S, port=80):
    if not ui_only_mode:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(wheels["front"]["right"]["forward"], GPIO.OUT)
        GPIO.setup(wheels["front"]["right"]["reverse"], GPIO.OUT)
        GPIO.setup(wheels["front"]["left"]["forward"], GPIO.OUT)
        GPIO.setup(wheels["front"]["left"]["reverse"], GPIO.OUT)   
        GPIO.setup(wheels["back"]["right"]["forward"], GPIO.OUT)
        GPIO.setup(wheels["back"]["right"]["reverse"], GPIO.OUT)
        GPIO.setup(wheels["back"]["left"]["forward"], GPIO.OUT)
        GPIO.setup(wheels["back"]["left"]["reverse"], GPIO.OUT)
    
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    if len(argv) == 3:
        if argv[1] == "--port":
            if argv[2].isdigit:
                run(port=int(argv[2]))
            else:
                print "Format for specifying port is --port 8080. Cannot set " + argv[2] + " as port"
    else:
        run()
        
