# Camera Server
#  Project: FireSense
#   Author: Richard Yu
# Modified: 2013-04-11
#
# This program runs the camera server that snaps images while doors are open.
# TCP messages received from door sensors trigger camera captures.
# Camera captures are obtained by reading the image in a specified url from
# the camera. The url is assumed to contain the most updated image from the
# camera.
# 
# Sensor messages are expected in the following format:
#    Door Open / Begin Capture: '<ID> Open'
#    Door Close / End Capture: '<ID> Close'
# 
# Camera IDs and urls are defined in the cameras dictionary structure

import os
import re
import socket
import SocketServer
import ConfigParser
import json
import datetime
import urllib2
import time
import threading

# Entry Format: '<Camera_ID>' : {'enable': False, 'url': '<Camera URL>'}
# Camera_ID cannot contain a space.
cameras = {'conf'  : {'enable': False, 'url': 'http://172.17.5.103/oneshotimage.jpg'},
           'solder': {'enable': False, 'url': 'http://172.17.5.106/oneshotimage.jpg'}}

class Config:
    print 'Starting Server'
    cparser = ConfigParser.SafeConfigParser()
    cparser.read('server.cfg')

    DATA_FOLDER = cparser.get('server', 'data_folder')
    PORT = cparser.getint('server', 'port')
    CAPTURE_INTERVAL = cparser.getfloat('server', 'interval')
    try:
        LOG_FILE = cparser.get('server', 'log_file')
    except:
        LOG_FILE = ''
    if not os.path.isdir(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    MAX_PACKET_SIZE = 2048

# This class reports all stream statistics
class Worker (threading.Thread):
    name = ''        # Related camera name
    cont = True      # Indicator to continue running
    def __init__(self, threadID, name):
        self.threadID = threadID
        self.name = name
        cameras[self.name]['enable'] = False
        threading.Thread.__init__(self)
        self.setDaemon(True)
        return

    def run(self):
        while self.cont:
            if cameras[self.name]['enable']:
                folder = self.getFolder()
                count = 0
                while cameras[self.name]['enable']:
                    cam = urllib2.urlopen(cameras[self.name]['url'])
                    with open(folder + 'cam_capture' + str(count).zfill(3) + '.jpg', 'wb') as f:
                        f.write(cam.read())
                    count += 1
                    time.sleep(Config.CAPTURE_INTERVAL)
        return

    def stop(self):
        self.cont = False
        return

    def getFolder(self):
        time_now = str(datetime.datetime.now()).split(' ')
        time_now[1] = time_now[1].replace(':', '-')
        folder = Config.DATA_FOLDER + '/' + time_now[0] 
        if not os.path.isdir(folder):
            os.makedirs(folder)
        folder = folder + '/' + time_now[1]
        if not os.path.isdir(folder):
            os.makedirs(folder)
        folder = folder + '/'
        return folder

class TCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # Receive packet
        client_ip = self.client_address[0]
        print str(datetime.datetime.now()), ' Received request from ', client_ip
        data = self.request.recv(Config.MAX_PACKET_SIZE).strip()
        self.data = ''
        self.request.sendall(self.data)
        try:
            data  = data.split(' ')
            print data
            cameras[data[0]]['enable'] = (data[1] == 'Open')
            print cameras[data[0]]['enable']
        except:
            if not Config.LOG_FILE == '':
                with open(Config.LOG_FILE, 'a'):
                    print 'Error for line: ', data
        return

# Main thread: Initiate server threads
if __name__ == "__main__":
    HOST = ""
    print('Now Serving on port: ' + str(Config.PORT))
    workerThreads = []
    index = 1
    for i in cameras.keys():
        workerThreads.append(Worker(index, i))
        index += 1

    server = SocketServer.TCPServer((HOST, Config.PORT), TCPHandler)
    
    for i in workerThreads:
        i.start()
    server.serve_forever()
