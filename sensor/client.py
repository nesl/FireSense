import socket
import sys
import ConfigParser
import config

def send(data):
	try:
		# print 'Connecting to server: %s Port: %s' % (config.SERVER_HOST, config.SERVER_PORT)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((config.SERVER_HOST, config.SERVER_PORT))
		sock.sendall(data)
		sock.recv(1)
	finally:
		sock.close()
	return
