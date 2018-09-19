#-*- coding:utf-8 -*-
import psutil
import socket,os,gevent
from user.user import *
from gevent.queue import Queue
from gevent import socket,monkey;monkey.patch_all()

host = '0.0.0.0'
port = 8080
BUFSIZE = 1024             #缓冲区大小1K

#from multiprocessing import Manager #数据共享
#mapclient = Manager().dict()
#l = Manager().list(range(5))  # 同样声明一个列表

recovery = Queue()
clientNum = Queue()

data, addr = 'test', 'test'

class Server_UDP():
	def __init__(self, host , port):
		self.start_server(host,port)

	def start_server(self,host, port):
		udpSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		udpSock.bind((host,port))
		print 'Server started successfully'
		clients = {}
		while True:
			try:
				global data, addr
				data,addr = udpSock.recvfrom(BUFSIZE)          #接受UDP
				# 回收断线用户
				while not recovery.empty():
					key = recovery.get()
					print 'recovery:',key
					if key in clients.keys():del clients[key]
				# 处理消息
				if len(data) > 0:
					clienturl='%s:%s'%(addr[0],addr[1])
					if clienturl in clients.keys():
						clients[clienturl].append(data)
					else:
						clients[clienturl]=[]
						clients[clienturl].append(data)
						gevent.spawn(self.handle_request,udpSock,addr,clients[clienturl])
					#gevent.sleep(0.001)
			except Exception as e:
				print("Server is colse:%s"%e)
		udpSock.close()

	def handle_request(self,sock,addr,dataList):
		clienturl='%s:%s'%(addr[0],addr[1])
		gUser = User(self,sock,addr)
		bUpdate = True
		clientNum.put_nowait(1)
		while bUpdate:
			sData = None
			if dataList and len(dataList) > 0:
				sData = dataList.pop(0)
			if gUser.updata(sData) == False:
				recovery.put(clienturl)
				bUpdate = False
			gevent.sleep(0.001)
		clientNum.put_nowait(-1)

class Server_Info():
	def __init__(self):
		gevent.spawn(self.handle_testing)

	def handle_testing(self):
		curpid = os.getpid()
		info = psutil.virtual_memory()
		maxmemory = info.total/1024/1024
		fomat = '@echo off&title 服务器 在线人数:%d 使用内存:%dMB'
		curNum = 0
		while True:
			while not clientNum.empty():
				curNum+=clientNum.get()

			curmemory = psutil.Process(curpid).memory_info().rss/1024/1024

			os.system(fomat%(curNum,curmemory))
			gevent.sleep(1)

# 清屏
def clearWin():
	if os.name == 'posix':
		os.system('clear')
	elif os.name == 'nt':
		os.system('cls')
	else:
		import curses
		curses.setupterm()
		lines = curses.tigetnum('lines')
		for x in xrange(lines):
			print
		print '\x1b[H\x1b2J'
	os.system('@echo off&title 服务器')


if __name__ == '__main__':
	clearWin()
	Server_Info()
	Server_UDP(host,port)

