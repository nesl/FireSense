import re
import json
import client
import datetime
import config

local_ip_pattern = re.compile('^192.168.')

# Manages information gathering on the router level
class RouterManager:
	# peer_list = list()           # list of peers by local ip
	# peer_managers = list()       # list of peer managers
	peer_list = {}               # list of peers managers by local ip
	active_peers = set()         # Set of currently active peers
	tcp_packet_count = 0         # TCP packet count
	udp_packet_count = 0         # UDP packet count
	tcp_out_pkt_count = 0        # TCP outgoing packet count
	tcp_in_pkt_count = 0         # TCP incoming packet count
	udp_out_pkt_count = 0        # UDP outgoing packet count
	udp_in_pkt_count = 0         # UDP incoming packet count
	tcp_max_out_pkt_size = 0     # Size of largest outgoing TCP packet
	tcp_max_in_pkt_size = 0      # Size of largest incoming TCP packet
	udp_max_out_pkt_size = 0     # Size of largest outgoing UDP packet
	udp_max_in_pkt_size = 0      # Size of largest incoming UDP packet

	# Print information about this router manager
	def printRM(self):
		print 'PRINTING RouterManager'
		print 'peer_list: ', self.peer_list.keys()
		print 'peer_managers: ', self.peer_managers.values()
		print 'tcp_packet_count:  %d' % (self.tcp_packet_count)
		print 'tcp_out_pkt_count:  %d' % (self.tcp_out_pkt_count)
		print 'tcp_in_pkt_count:  %d' % (self.tcp_in_pkt_count)
		print 'tcp_max_out_size: %d' % (self.tcp_max_out_pkt_size)
		print 'tcp_max_in_size: %d' % (self.tcp_max_in_pkt_size)
		print 'udp_packet_count:  %d' % (self.udp_packet_count)
		print 'udp_out_pkt_count:  %d' % (self.udp_out_pkt_count)
		print 'udp_in_pkt_count:  %d' % (self.udp_in_pkt_count)
		print 'udp_max_out_size: %d' % (self.udp_max_out_pkt_size)
		print 'udp_max_in_size: %d' % (self.udp_max_in_pkt_size)
		return

	# Report router details to server
	def report(self, event):
		anon_peer_list = list()
		for p in self.peer_list.keys():
			psplit = p.split('.')
			psplit[3] = str(int(psplit[3]) ^ config.IP_RAND)
			anon_peer_list.append('.'.join(psplit))

		# Generate JSON
		s = json.dumps({
			'Type': 'Router',
			'Event': event,
			'Time': str(datetime.datetime.now()),
			'Peers': ','.join(anon_peer_list),
			'PeerCount': len(self.peer_list),
			'ActivePeers': len(self.active_peers),
			'TcpStats': {
				'Counts': {
					'Total': self.tcp_packet_count,
					'Incoming': self.tcp_in_pkt_count,
					'Outgoing': self.tcp_out_pkt_count},
				'MaxSizes': {
					'Incoming': self.tcp_max_in_pkt_size,
					'Outgoing': self.tcp_max_out_pkt_size}
			            },
			'UdpStats': {
				'Counts': {
					'Total': self.udp_packet_count,
					'Incoming': self.udp_in_pkt_count,
					'Outgoing': self.udp_out_pkt_count},
				'MaxSizes': {
					'Incoming': self.udp_max_in_pkt_size,
					'Outgoing': self.udp_max_out_pkt_size}}
			},sort_keys=True) 
		#print(s)
		client.send(s)
		return s

	# Clear router statistics
	def clearStats(self):
		self.tcp_packet_count = 0
		self.udp_packet_count = 0
		self.tcp_out_pkt_count = 0
		self.tcp_in_pkt_count = 0
		self.udp_out_pkt_count = 0
		self.udp_in_pkt_count = 0
		self.tcp_max_out_pkt_size = 0
		self.tcp_max_in_pkt_size = 0
		self.udp_max_out_pkt_size = 0
		self.udp_max_in_pkt_size = 0
		self.active_peers.clear()
		return

	# Remove inactive peers from the peers list
	def clearInactivePeers(self):
		time_now = datetime.datetime.now()
		# Loop through the peer/managers lists backwards
		for i in self.peer_list.keys():
			if len(self.peer_list[i].tcp_stream_list) == 0 and\
			       len(self.peer_list[i].udp_streams) == 0 and\
			       self.peer_list[i].tcp_packet_count == 0 and\
			       self.peer_list[i].udp_packet_count == 0:
				self.peer_list[i].clearAllStreams()
				self.peer_list.pop(i)
			else:
				td = time_now - self.peer_list[i].last_packet_time
				if td.seconds > config.PEER_TIMEOUT_S:
					self.peer_list[i].clearAllStreams()
					self.peer_list.pop(i)
					print 'Peer timeout ', i

	# Add a tcp packet to this router manager
	def addTCPPacket(self, data):
		self.tcp_packet_count += 1
		local = config.localIP(data.ip_source)
		
		# Determine inbound/outbound traffic
		if local:
			self.tcp_out_pkt_count += 1
			if self.tcp_max_out_pkt_size < data.length:
				self.tcp_max_out_pkt_size = data.length
			ip = data.ip_source
		else:
			self.tcp_in_pkt_count += 1
			if self.tcp_max_in_pkt_size < data.length:
				self.tcp_max_in_pkt_size = data.length
			ip = data.ip_dest
		
		# Add a new client if necessary
		if not self.peer_list.has_key(ip):
			self.peer_list[ip] = PeerManager()
			self.peer_list[ip].initialize(ip)
		
		self.active_peers.add(ip)
		self.peer_list[ip].addTCPPacket(data)
		return

	# Add a udp packet to this router manager
	def addUDPPacket(self, data):
		self.udp_packet_count += 1
		local = config.localIP(data.ip_source)
		
		# Determine inbound/outbound traffic
		if local:
			self.udp_out_pkt_count += 1
			if self.udp_max_out_pkt_size < data.length:
				self.udp_max_out_pkt_size = data.length
			ip = data.ip_source
		else:
			self.udp_in_pkt_count += 1
			if self.udp_max_in_pkt_size < data.length:
				self.udp_max_in_pkt_size = data.length
			ip = data.ip_dest
		# Add a new client if necessary
		if not self.peer_list.has_key(ip):
			self.peer_list[ip] = PeerManager()
			self.peer_list[ip].initialize(ip)
		
		self.active_peers.add(ip)
		self.peer_managers[-1].addUDPPacket(data)
		return

# Manages information gathering on the peer level
class PeerManager:
	tcp_stream_list = {}         # List of open tcp stream managers by foreign ip
	tcp_streams = set()          # Set of active tcp streams by foreign ip
	udp_streams = set()          # Set of active udp streams by foreign ip
	ip_local = ""                # Local ip address of peer
	tcp_packet_count = 0         # TCP packet count
	udp_packet_count = 0         # UDP packet count
	tcp_out_pkt_count = 0        # TCP outgoing packet count
	tcp_in_pkt_count = 0         # TCP incoming packet count
	udp_out_pkt_count = 0        # UDP outgoing packet count
	udp_in_pkt_count = 0         # UDP incoming packet count
	tcp_max_out_pkt_size = 0     # Size of largest outgoing TCP packet
	tcp_max_in_pkt_size = 0      # Size of largest incoming TCP packet
	udp_max_out_pkt_size = 0     # Size of largest outgoing UDP packet
	udp_max_in_pkt_size = 0      # Size of largest incoming UDP packet
	last_packet_time = datetime.datetime.now() # Time of last packet

	# Print information about this peer manager
	def printPM(self):
		print 'PRINTING PeerManager'
		print 'tcp_streams: ', self.tcp_stream_list.keys()
		print 'tcp_stream_managers: ', self.tcp_stream_list.values()
		print 'udp_streams: ', self.udp_streams
		print 'ip_local: %s' % (self.ip_local)
		print 'tcp_packet_count: %d' % (self.tcp_packet_count)
		print 'tcp_out_packets: %d' % (self.tcp_out_pkt_count)
		print 'tcp_in_packets: %d' % (self.tcp_in_pkt_count)
		print 'tcp_max_out_size: %d' % (self.tcp_max_out_pkt_size)
		print 'tcp_max_in_size: %d' % (self.tcp_max_in_pkt_size)
		print 'udp_packet_count: %d' % (self.udp_packet_count)
		print 'udp_out_packets: %d' % (self.udp_out_pkt_count)
		print 'udp_in_packets: %d' % (self.udp_in_pkt_count)
		print 'udp_max_out_size: %d' % (self.udp_max_out_pkt_size)
		print 'udp_max_in_size: %d' % (self.udp_max_in_pkt_size)

	# Report peer details to server
	def report(self, event):
		ip_split = self.ip_local.split('.')
		ip_split[3] = str(int(ip_split[3]) ^ config.IP_RAND)
		ip_anonymous = '.'.join(ip_split)

		# Generate JSON
		s = json.dumps({
			'Type': 'Peer',
			'Event': event,
			'Time': str(datetime.datetime.now()),
			'LocalIP': ip_anonymous,
			'TcpStats': {
				'ActiveStreamCount': len(self.tcp_streams),
				# 'ActiveStreams': ','.join(str(l) for l in self.tcp_streams),
				'OpenStreamCount': len(self.tcp_stream_list),
				'Counts': {
					'Total': self.tcp_packet_count,
					'Incoming': self.tcp_in_pkt_count,
					'Outgoing': self.tcp_out_pkt_count},
				'MaxSizes': {
					'Incoming': self.tcp_max_in_pkt_size,
					'Outgoing': self.tcp_max_out_pkt_size}
			            },
			'UdpStats': {
				# 'ActiveStreams': ','.join(str(l) for l in self.udp_streams),
				'ActiveStreamCount': len(self.udp_streams),
				'Counts': {
					'Total': self.udp_packet_count,
					'Incoming': self.udp_in_pkt_count,
					'Outgoing': self.udp_out_pkt_count},
				'MaxSizes': {
					'Incoming': self.udp_max_in_pkt_size,
					'Outgoing': self.udp_max_out_pkt_size}}
			},sort_keys=True) 
		# print s
		client.send(s)
		return s

	def clearStats(self):
		self.tcp_streams.clear()
		self.udp_streams.clear()
		self.tcp_packet_count = 0
		self.udp_packet_count = 0
		self.tcp_out_pkt_count = 0
		self.tcp_in_pkt_count = 0
		self.udp_out_pkt_count = 0
		self.udp_in_pkt_count = 0
		self.tcp_max_out_pkt_size = 0
		self.tcp_max_in_pkt_size = 0
		self.udp_max_out_pkt_size = 0
		self.udp_max_in_pkt_size = 0
		return
	
	# Clear old streams
	def clearInactiveStreams(self):
		time_now = datetime.datetime.now()
		for i in self.tcp_stream_list.keys():
			td = time_now - self.tcp_stream_list[i].last_packet_time
			if td.seconds > config.STREAM_TIMEOUT_S:
				self.tcp_stream_list[i].removeStream('Timeout')
				self.tcp_stream_list.pop(i)
				print 'Stream timeout ', self.ip_local
		return
	
	# Clear all streams
	def clearAllStreams(self):
		for i in self.tcp_stream_list.keys():
			self.tcp_stream_list[i].removeStream('Timeout')
			self.tcp_stream_list.pop(i)
		return
	
	def initialize(self, ip):
		self.tcp_streams.clear()
		self.udp_streams.clear()
		self.ip_local = ip
		return

	# Add a tcp packet to this peer manager
	def addTCPPacket(self, data):
		self.tcp_packet_count += 1

		# Determine incoming/outgoing packet
		# Find the foreign stream to match
		if data.ip_source == self.ip_local:
			ip_foreign = data.ip_dest
			self.tcp_out_pkt_count += 1
			if self.tcp_max_out_pkt_size < data.length:
				self.tcp_max_out_pkt_size = data.length
		else:
			ip_foreign = data.ip_source
			self.tcp_in_pkt_count += 1
			if self.tcp_max_in_pkt_size < data.length:
				self.tcp_max_in_pkt_size = data.length

		# Add a new stream or update an existing stream
		if not self.tcp_stream_list.has_key(ip_foreign):
			self.tcp_stream_list[ip_foreign] = TCPStreamManager()
			self.tcp_stream_list[ip_foreign].initialize(self.ip_local,
			                                            ip_foreign, data)
		else:
			self.tcp_stream_list[ip_foreign].addPacket(data)

		# If this packet is a stream teardown,
		# remove the stream
		if (data.reset or (data.fin and data.ack)):
			self.tcp_stream_list[ip_foreign].removeStream('Close')
			self.tcp_stream_list.pop(ip_foreign)

		# Add the stream to the set of active tcp streams
		self.tcp_streams.add(ip_foreign)
		self.last_packet_time = datetime.datetime.now()
		return

	# Add a udp packet to this peer manager
	def addUDPPacket(self, data):
		self.udp_packet_count += 1
		# Determine incoming/outgoing packet
		# Find the foreign stream to match
		if data.ip_source == self.ip_local:
			ip_foreign = data.ip_dest
			self.udp_out_pkt_count += 1
			if self.udp_max_out_pkt_size < data.length:
				self.udp_max_out_pkt_size = data.length
		else:
			ip_foreign = data.ip_source
			self.udp_in_pkt_count += 1
			if self.udp_max_in_pkt_size < data.length:
				self.udp_max_in_pkt_size = data.length
		
		# Add the stream to the set of active udp streams
		self.last_packet_time = datetime.datetime.now()
		self.udp_streams.add(ip_foreign)
		return

# Manages information gathering on the stream level
class TCPStreamManager:
	ip_local = ""               # Local peer IP address
	ip_foreign = ""             # Foreign peer IP address
	local_ports = set()         # Set of local ports
	foreign_ports = set()       # Set of foreign ports
	tcp_packet_count = 0        # TCP packet count
	tcp_out_pkt_count = 0       # TCP outgoing packet count
	tcp_in_pkt_count = 0        # TCP incoming packet count
	tcp_max_out_pkt_size = 0    # Size of largest outgoing TCP packet
	tcp_max_in_pkt_size = 0     # Size of largest incoming TCP packet
	http_user_agent = ""        # HTTP user agent string
	last_packet_time = datetime.datetime.now() # Last packet time

	# Print information about this tcp stream manager
	def printTSM(self):
		print 'PRINTING TCPStreamManager'
		print 'ip_local: %s' % (self.ip_local)
		print 'ip_foreign: %s' % (self.ip_foreign)
		print 'local_ports: ', self.local_ports
		print 'foreign_ports: ', self.foreign_ports
		print 'tcp_packet_count: %d' % (self.tcp_packet_count)
		print 'tcp_out_packets: %d' % (self.tcp_out_pkt_count)
		print 'tcp_in_packets: %d' % (self.tcp_in_pkt_count)
		print 'tcp_max_out_size: %d' % (self.tcp_max_out_pkt_size)
		print 'tcp_max_in_size: %d' % (self.tcp_max_in_pkt_size)
		return

	# Report stream details to server
	def report(self, event):
		ip_split = self.ip_local.split('.')
		ip_split[3] = str(int(ip_split[3]) ^ config.IP_RAND)
		ip_anonymous = '.'.join(ip_split)

		# Generate JSON
		s = json.dumps({
			'Type': 'Stream',
			'Event': event,
			'Time': str(datetime.datetime.now()),
			'UserAgent': self.http_user_agent,
			'LocalIP': ip_anonymous,
			'ForeignIP': self.ip_foreign,
			'LocalPorts': ','.join(str(l) for l in self.local_ports),
			'ForeignPorts': ','.join(str(l) for l in self.foreign_ports),
			'Counts': {
				'Total': self.tcp_packet_count,
				'Incoming': self.tcp_in_pkt_count,
				'Outgoing': self.tcp_out_pkt_count},
			'MaxSizes': {
				'Incoming': self.tcp_max_in_pkt_size,
				'Outgoing': self.tcp_max_out_pkt_size}
			},sort_keys=True) 
		# print s
		client.send(s)
		return s

	def clearStats(self):
		self.local_ports.clear()
		self.foreign_ports.clear()
		self.tcp_packet_count = 0
		self.tcp_out_pkt_count = 0
		self.tcp_in_pkt_count = 0
		self.tcp_max_out_pkt_size = 0
		self.tcp_max_in_pkt_size = 0
		return


	def initialize(self, ip_local, ip_foreign, data):
		print('New Stream for IP ' + ip_local)
		self.local_ports.clear()
		self.foreign_ports.clear()
		self.ip_local = ip_local
		self.ip_foreign = ip_foreign
		self.http_user_agent = data.http_user_agent
		self.addPacket(data)
		self.report('Open')
		return

	# Add a tcp packet to this tcp stream manager
	def addPacket(self, data):
		# if not (self.ip_local):
			# if config.localIP(data.ip_source):
				# self.ip_local = data.ip_source
				# self.ip_foreign = data.ip_dest
			# else:
				# self.ip_local = data.ip_dest
				# self.ip_foreign = data.ip_source

		self.tcp_packet_count += 1

		if data.ip_source == self.ip_local:
			self.tcp_out_pkt_count += 1
			if self.tcp_max_out_pkt_size < data.length:
				self.tcp_max_out_pkt_size = data.length
			self.local_ports.add(data.port_source)
			self.foreign_ports.add(data.port_dest)
		else:
			self.tcp_in_pkt_count += 1
			if self.tcp_max_in_pkt_size < data.length:
				self.tcp_max_in_pkt_size = data.length
			self.local_ports.add(data.port_dest)
			self.foreign_ports.add(data.port_source)
		
		self.last_packet_time = datetime.datetime.now()
		return
	
	def removeStream(self, event):
		# print "REMOVING STREAM %s : %s" % (self.ip_local, self.ip_foreign)
		self.report(event)
		return

class UDPPacket:
	ip_source = ""
	ip_dest = ""
	length = 0
	port_source = 0
	port_dest = 0

class TCPPacket:
	ip_source = ""
	ip_dest = ""
	length = 0
	port_source = 0
	port_dest = 0
	ack = 0
	fin = 0
	reset = 0
	http_user_agent = ""
