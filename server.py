#!/usr/bin/env python
"""
UI for a raspberry pi robot

"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import argparse
import getopt

import SocketServer
import os
import sys
import cgi

#run time options
wheel_motors_enabled = False
lcd_enabled = False
port = 80

#initial state
ui_served = False

#cli args
parser = argparse.ArgumentParser()
parser.add_argument('-w', '--disable-wheel-motors', default=0)
parser.add_argument('-l', '--disable-lcd', default=0)
parser.add_argument('-p', '--port', default=80)

args = parser.parse_args()
options = vars(args)
if options["disable_wheel_motors"] == 0:
    wheel_motors_enabled = True
if options["disable_lcd"] == 0:
    lcd_enabled = True
port = int(options["port"])

# Conditional imports
if wheel_motors_enabled:
        import RPi.GPIO as GPIO

if lcd_enabled:
    import lcd1602 as lcd
    lcd.lcd_init()


#set up pins to wheels
wheel_pins = {"front":{"right":{"forward":40,"reverse":38},"left":{"forward":33,"reverse":37}},"back":{"right":{"forward":18,"reverse":15},"left":{"forward":16,"reverse":12}}}

f_wheels = [wheel_pins["front"]["right"]["forward"],
        wheel_pins["front"]["left"]["forward"],
        wheel_pins["back"]["right"]["forward"], 
        wheel_pins["back"]["left"]["forward"]]

b_wheels = [wheel_pins["front"]["right"]["reverse"], 
        wheel_pins["front"]["left"]["reverse"], 
        wheel_pins["back"]["right"]["reverse"],
        wheel_pins["back"]["left"]["reverse"]]

r_wheels = [wheel_pins["front"]["left"]["forward"],
        wheel_pins["back"]["left"]["forward"]]

l_wheels = [wheel_pins["front"]["right"]["forward"],
        wheel_pins["back"]["right"]["forward"]]

wheel_commands = {"F":{"command":"Forward","wheels":f_wheels},
                 "B":{"command":"Reverse","wheels":b_wheels},
                 "R":{"command":"Right","wheels":r_wheels},
                 "L":{"command":"Left","wheels":l_wheels}}
                
              
class S(BaseHTTPRequestHandler):
    ui_served = ui_served
    
    def display_status(self, text):
        print(text)
        if lcd_enabled:
            lcd.lcd_text(text,lcd.LCD_LINE_1)

    def drive_wheels(self, wc):
        self.stop()
        
        self.display_status("CMD: " + wc["command"])
        
        if not wheel_motors_enabled:
            return
            
        wheels = wc["wheels"]
        for wheel in wheels:
            GPIO.output(wheel,1)

        
    def stop(self):
    
        if not wheel_motors_enabled:
            return
            
        GPIO.output(wheel_pins["front"]["right"]["forward"], 0)
        GPIO.output(wheel_pins["front"]["right"]["reverse"], 0)
        GPIO.output(wheel_pins["front"]["left"]["forward"], 0)
        GPIO.output(wheel_pins["front"]["left"]["reverse"], 0)
        GPIO.output(wheel_pins["back"]["right"]["forward"], 0)
        GPIO.output(wheel_pins["back"]["right"]["reverse"], 0)
        GPIO.output(wheel_pins["back"]["left"]["forward"], 0)
        GPIO.output(wheel_pins["back"]["left"]["reverse"], 0)

    
    def _set_headers(self, type):
        self.send_response(200)
        if type == "htlm":
            self.send_header('Content-type', 'text/html')
        if type == "image":
            self.send_header('Content-type', 'image/png')
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            if (not self.ui_served) and lcd_enabled:
                lcd.lcd_text("Spencerbot", lcd.LCD_LINE_1)
                lcd.lcd_text("Ready", lcd.LCD_LINE_2)
                self.ui_served = True
            self._set_headers("html")
            html = self.file_as_string("home.html")
            self.wfile.write(html)
        else:
            self._set_headers("image")
            img = self.file_as_binary(self.path)
            self.wfile.write(img)
        
    def do_HEAD(self):
        self._set_headers(None)
        
    def do_POST(self):
        data = self.get_post_data()
        if data["dir"][0] == "S":
            self.stop()
            self.display_status("CMD: Stop")
        elif data["dir"][0] in wheel_commands.keys():
            self.drive_wheels(wheel_commands[data["dir"][0]])
            
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
        
def initialize_pins():
    if wheel_motors_enabled:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(wheel_pins["front"]["right"]["forward"], GPIO.OUT)
        GPIO.setup(wheel_pins["front"]["right"]["reverse"], GPIO.OUT)
        GPIO.setup(wheel_pins["front"]["left"]["forward"], GPIO.OUT)
        GPIO.setup(wheel_pins["front"]["left"]["reverse"], GPIO.OUT)   
        GPIO.setup(wheel_pins["back"]["right"]["forward"], GPIO.OUT)
        GPIO.setup(wheel_pins["back"]["right"]["reverse"], GPIO.OUT)
        GPIO.setup(wheel_pins["back"]["left"]["forward"], GPIO.OUT)
        GPIO.setup(wheel_pins["back"]["left"]["reverse"], GPIO.OUT)


def run(server_class=HTTPServer, handler_class=S):
    initialize_pins()
    import host_ip
    ip = host_ip.get_ip()
    ip_add = ip
    if port != 80:
        ip_add += ":" + str(port)
    print ("serving on " + ip_add)
    if lcd_enabled:
        lcd.lcd_text("Controls at", lcd.LCD_LINE_1)
        lcd.lcd_text(ip_add, lcd.LCD_LINE_2)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":    
    run()
        
