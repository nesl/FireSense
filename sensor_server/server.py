# Sensor Server
#  Project: FireSense
#   Author: Richard Yu
# Modified: 2013-04-11
#
# This program runs the sensor server that receives and stores data from the
# firewall sensor.
#

import os
import re
import socket
import SocketServer
import ConfigParser
import json
import datetime

class Config:
    print 'Starting Server'
    cparser = ConfigParser.SafeConfigParser()
    cparser.read('server.cfg')

    DATA_FOLDER = cparser.get('server', 'data_folder')
    PORT = cparser.getint('server', 'port')

    if not os.path.isdir(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    ROUTER_FILE = 'router.txt'
    PEER_FILE = 'peer.txt'
    STREAM_FILE = 'stream.txt'
    EVENT_FILE = 'event.txt'
    MAX_PACKET_SIZE = 2048

class TCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # Receive packet
        client_ip = self.client_address[0]
        print str(datetime.datetime.now()), ' Received request from ', client_ip
        data = self.request.recv(Config.MAX_PACKET_SIZE).strip()
        self.data = ''
        self.request.sendall(self.data)

        # Calculate data folder name
	# Store data in: DATA_FOLDER/<DATE>
        folder = Config.DATA_FOLDER + '/' + \
                 re.search('^.+(?= )', str(datetime.datetime.now())).group(0)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        # Parse the JSON
        try:
            jdata = json.loads(data)
            print jdata['Type'], '\t\t', jdata['Event']

            type_str = jdata['Type'].lower()

            # Handle router packets
            if type_str == 'router':
                with open(folder + '/' + Config.ROUTER_FILE, 'a') as f:
                    f.write(data + '\n')
                return

            # Handle non-router packets
            folder = folder + '/' + jdata['LocalIP']
            if not os.path.isdir(folder):
                os.makedirs(folder)
            if jdata['Event'].lower() != 'periodic':
                data_file = folder + '/' + Config.EVENT_FILE
            elif type_str == 'peer':
                data_file = folder + '/' + Config.PEER_FILE
            elif type_str == 'stream':
                data_file = folder + '/' + Config.STREAM_FILE

            with open(data_file, 'a') as f:
                f.write(data + '\n')
        except:
            #Error handler
            print 'Received unknown data format'
            print data
            with open(folder + '/' + 'ErrorLog.txt', 'a') as f:
                f.write(data + '\n')
        return

# Main thread: Initiate server threads
if __name__ == "__main__":
    HOST = ""
    server = SocketServer.TCPServer((HOST, Config.PORT), TCPHandler)
    server.serve_forever()
