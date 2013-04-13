import config
import data_managers
import threading
import time

# This class reports router statistics
class RouterReporter (threading.Thread):
	router = None    # RouterManager object
	cont = True      # Indicator to continue running
	def __init__(self, threadID, router):
		self.threadID = threadID
		self.router = router
		threading.Thread.__init__(self)
		self.setDaemon(True)
		return

	def run(self):
		while self.cont:
			time.sleep(config.ROUTER_INTERVAL_S)
			with config.ROUTER_LOCK:
				# print 'Periodic Router Update'
				self.router.report('Periodic')
				self.router.clearStats()
		return

	def stop(self):
		self.cont = False
		return

# This class reports all peer statistics
class PeerReporter (threading.Thread):
	router = None    # RouterManager object
	cont = True      # Indicator to continue running
	def __init__(self, threadID, router):
		self.threadID = threadID
		self.router = router
		threading.Thread.__init__(self)
		self.setDaemon(True)
		return

	def run(self):
		while self.cont:
			time.sleep(config.PEER_INTERVAL_S)
			with config.ROUTER_LOCK:
				# print 'Periodic Peer Update'
				self.router.clearInactivePeers()
				for p in self.router.peer_list.values():
					p.report('Periodic')
					p.clearStats()
		return

	def stop(self):
		self.cont = False
		return

# This class reports all stream statistics
class StreamReporter (threading.Thread):
	router = None    # RouterManager object
	cont = True      # Indicator to continue running
	def __init__(self, threadID, router):
		self.threadID = threadID
		self.router = router
		threading.Thread.__init__(self)
		self.setDaemon(True)
		return

	def run(self):
		while self.cont:
			time.sleep(config.STREAM_INTERVAL_S)
			with config.ROUTER_LOCK:
				# print 'Periodic Stream Update'
				for p in self.router.peer_list.values():
					p.clearInactiveStreams()
					for s in p.tcp_stream_list.values():
						if s.tcp_packet_count > 0:
							s.report('Periodic')
							s.clearStats()
		return

	def stop(self):
		self.cont = False
		return
