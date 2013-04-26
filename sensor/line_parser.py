import re
import data_managers

# tshark options list
# 0 ip.proto
# 1 ip.src
# 2 ip.dst
# 3 ip.len
# 4 udp.srcport
# 5 udp.dstport
# 6 tcp.srcport
# 7 tcp.dstport
# 8 tcp.flags.ack
# 9 tcp.flags.fin
#10 tcp.flags.reset
#11 http.user_agent
#12 frame.time

separator = re.compile('\|')
def parse(line):
	#split_line = re.split(separator, line)
	split_line = line.split('|')

	# print 'Protocol: ', split_line[0]
	if len(split_line) < 10:
		return ['']

	if split_line[11] == '\n':
		split_line[11] = ''
	#print 'ip.src   %s' % (split_line[1])
	#print 'ip.dst   %s' % (split_line[2])
	#print 'length   %s' % (split_line[3])
	#print 'udp.src  %s' % (split_line[4])
	#print 'udp.dst  %s' % (split_line[5])
	#print 'tcp.src  %s' % (split_line[6])
	#print 'tcp.dst  %s' % (split_line[7])
	#print 'tcp.ack  %s' % (split_line[8])
	#print 'tcp.fin  %s' % (split_line[9])
	#print 'tcp.rset %s' % (split_line[10])
	#print 'http.usr %s' % (split_line[11])
	#print 'arr_time %s' % (split_line[12])

	# Non-IP Traffic
	if split_line[0] == "":
		return ['']
	if split_line[0] == "0x06":
		return ['tcp', tcp_parse(split_line)]
	#	return tcp_parse(split_line)
	if split_line[0] == "0x11":
		# print 'udp'
		return ['udp', udp_parse(split_line)]
	return ['']

# tcp tuple format:
# ip.src    0
# ip.dst    1
# time      2
# length    3
# srcport   4
# dstport   5
# sequence  6
# ack       7
# fin       8
# reset     9
# http.usr 10
def tcp_parse(l):
	tcp_obj = data_managers.TCPPacket()
	tcp_obj.ip_source = l[1]
	tcp_obj.ip_dest = l[2]
	tcp_obj.length = int(l[3])
	tcp_obj.port_source = int(l[6])
	tcp_obj.port_dest = int(l[7])
	try:
		tcp_obj.ack = int(l[8])
	except:
		tcp_obj.ack = 0
	try:
		tcp_obj.fin = int(l[9])
	except:
		tcp_obj.fin = 0
	try:
		tcp_obj.reset = int(l[10])
	except:
		tcp_obj.reset = 0
	tcp_obj.http_user_agent = l[11]
	tcp_obj.time = l[12]
	return tcp_obj

def udp_parse(l):
	udp_obj = data_managers.UDPPacket()
	udp_obj.ip_source = l[1]
	udp_obj.ip_dest = l[2]
	udp_obj.length = int(l[3])
	udp_obj.port_source = int(l[4])
	udp_obj.port_dest = int(l[5])
	udp_obj.time = int(l[12])

	return udp_obj
