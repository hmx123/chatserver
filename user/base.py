#-*- coding:utf-8 –*-
import struct,json,re,time, redis

MSG_UPTIME_ACCONT = 999

MSG_HEAD_ACCONT = 1000
MSG_ACTION_LOGIN = 1	  # 登陆
MSG_ACTION_REGISTER = 2	  # 注册
MSG_ACTION_RECONNECT = 3  # 重连
MSG_ACTION_CODE = 4       # 验证码
MSG_ACTION_PASSWORD = 5   # 密码修改

MSG_HEAD_ROOM = 1001
MSG_ACTION_CREATE = 1		#创建房间
MSG_ACTION_ROOM_LIST = 2	#房间列表

# Redis 配置
REDIS = redis.Redis(host='127.0.0.1', port=6379, db=1)


class Base():
	def initbase(self,_conn,_addr,_hadle):
		self.conn = _conn
		self.addr = _addr
		self.hadle = _hadle
		self.uptime = int(time.time())
		
	def updata(self,datas):
		head,action,data = self.request(datas)
		if head > 0:
			self.hadle(head,action,data)
		elif head == -1:
			return False
		return True

	# 发送消息
	def send(self,head,action=1,data=None,error=''):
		if data == None:data={}
		data = {'head':head,"action":action,'error':error.decode('UTF-8'),'data':data}
		data = json.dumps(data)
		if head!= MSG_UPTIME_ACCONT:print 'return:%s'%data
		try:
			self.conn.sendto(data,self.addr)
		except Exception as e:
			print("client is colse:%s"%e)

	# 数据监听
	def request(self,data):
		# 数据解析
		if data != None and len(data) > 0:
			try:
				jsonData = json.loads(data)
			except ValueError:
				jsonData = None;
			if jsonData and type(jsonData) == dict and jsonData['head'] and jsonData['action'] and jsonData['data'] != None:
				self.uptime = int(time.time())
				if jsonData['head'] == MSG_UPTIME_ACCONT:
					self.send(jsonData['head'],jsonData['action'])
					return 0,0,0
					#return jsonData['head'],jsonData['action'],jsonData['data']
				else:
					print 'receive:%s'%data
					return jsonData['head'],jsonData['action'],jsonData['data']
		# 心跳超时
		if int(time.time()) - self.uptime > 180:
			print 'client close : overtime ',self.addr
			return -1,-1,-1
		# 正常循环
		if data == None:
			return 0,0,0
		# 异常断开
		print 'client close : dataerr',self.addr
		return -1,0,0