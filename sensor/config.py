import re
import ConfigParser
import threading
import thread
import signal
import random

cparser = ConfigParser.SafeConfigParser()
cparser.read('config.cfg')

re_local_ip1 = re.compile('^128.97.93.')
re_local_ip2 = re.compile('^172.17.5.')

ROUTER_INTERVAL_S = cparser.getfloat('intervals', 'router_interval')
PEER_INTERVAL_S   = cparser.getfloat('intervals', 'peer_interval')
STREAM_INTERVAL_S   = cparser.getfloat('intervals', 'stream_interval')
ROUTER_LOCK = threading.Lock()

SERVER_HOST = cparser.get('server', 'host')
SERVER_PORT = cparser.getint('server', 'port')

PEER_TIMEOUT_S = cparser.getfloat('timeouts', 'peer')
STREAM_TIMEOUT_S = cparser.getfloat('timeouts', 'stream')
INPUT_TIMEOUT_S = cparser.getfloat('timeouts', 'input')

re_local_ip_str = cparser.get('filters', 'local_ip').split(',')
re_local_ips = []
for s in re_local_ip_str:
	re_local_ips.append(re.compile(s))

IP_RAND = random.randint(0, 255)


print 'Configuration properties:'
print '    Router interval:  %f' % (ROUTER_INTERVAL_S)
print '    Peer   interval:  %f' % (PEER_INTERVAL_S)
print '    Stream interval:  %f' % (PEER_INTERVAL_S)
print '    Server Host:     ', SERVER_HOST
print '    Server Port:      %d' % (SERVER_PORT)
print '    Peer   timeout:   %f' % (PEER_TIMEOUT_S)
print '    Stream timeout:   %f' % (STREAM_TIMEOUT_S)
print '    Input  timeout:   %f' % (INPUT_TIMEOUT_S)
print '    Local ip filters: ', re_local_ip_str

def localIP(ip):
	for r in re_local_ips:
		if re.match(r, ip):
			return True
	return False

