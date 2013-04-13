import re
import sys
import json
import time
import thread
import threading
import signal
import config
import line_parser
import data_managers
import reporter
import select
import datetime
import client

router = data_managers.RouterManager()

router_rep = reporter.RouterReporter(1, router)
peer_rep = reporter.PeerReporter(2, router)
stream_rep = reporter.StreamReporter(3, router)

router_rep.start()
peer_rep.start()
stream_rep.start()

while True:
	# Check if input exists, wait up to timeout_s seconds
	rlist, wlist, xlist = select.select([sys.stdin], [], [], config.INPUT_TIMEOUT_S)
	if len(rlist) == 0: 
		sys.exit('Error: Input Timeout ' + str(datetime.datetime.now()))
	
	# Get and parse input
	line = sys.stdin.readline()
	start_time = datetime.datetime.now()
	while len(line) < 1:
		if (datetime.datetime.now() - start_time).seconds > config.INPUT_TIMEOUT_S:
			client.send('Input Timeout ' + str(datetime.datetime.now()))
			sys.exit('Error: Input Timeout ' + str(datetime.datetime.now()))
		line = sys.stdin.readline()

	ret = line_parser.parse(line)
	protocol = ret[0]
	
	# Skip bad lines
	if protocol == '':
		continue

	packet = ret[1]

	# Skip local -> local connections
	# print 'Protocol: ', protocol
	# if re.match(re_local_ip, packet.ip_source) and re.match(re_local_ip, packet.ip_dest):
	if config.localIP(packet.ip_source) and config.localIP(packet.ip_dest):
		continue
	# if (not re.match(re_local_ip, packet.ip_source)) and (not re.match(re_local_ip, packet.ip_dest)):
	if (not config.localIP(packet.ip_source)) and (not config.localIP(packet.ip_dest)):
		continue

	with config.ROUTER_LOCK:
		if protocol == 'tcp':
			router.addTCPPacket(packet)
		elif protocol == 'udp':
			router.addUDPPacket(packet)

