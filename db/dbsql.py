#-*- coding:utf-8 –*-
from pymysqlpool import ConnectionPool
import gevent
import hashlib
from gevent.queue import Queue
from wyyapi import wyy_create_room, wyy_create_user, sendcode
from user.base import REDIS

config = {
    'pool_name': 'test',
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'accont'
}

CachingQueue = Queue()

def connection_pool():
	pool = ConnectionPool(**config)
	return pool

# 发送验证码  0 失败 1用户存在 2成功
def db_sendcode(handle, acc):
	AddCachingQueue([_db_sendcode, handle, acc])
def _db_sendcode(attr, cursor):
	handle = attr[1]
	acc = attr[2]
	# 检测是否存在
	sql = "select password from l_accont where account='%s' limit 1"
	if cursor.execute(sql % acc):
		handle([1])
		return False
	# 调用网易云验证码发送
	code = sendcode(acc)
	if code == None:
		handle([0])
		return False
	# 创建用户
	sqlu = "INSERT INTO l_accont (id, account, password,userid,token,phone,mail,weixin,qq,create_time,last_time,lkey,power,nickname,gender,birthday,code) VALUES (%d,'%s','%s',%d,'%s','%s','%s','%s','%s',%d,%d,%d,%d,'%s','%s','%s','%s')"
	data = (0, acc, '', 0, '', '', '', '', '', 0, 0, 0, 0, '', '', '',str(code))
	if cursor.execute(sqlu % data) > 0:
		handle([2, acc])
		return True
	else:
		handle(1)
	return None
# 注册 0成功 1失败 2已存在账号 3数据库写入异常"nickname":"xxxx","gender":"1","birthday":"xxxx"
def db_register(handle,acc,pwd, nickname, gender, birthday, code):
	AddCachingQueue([_db_register,handle,acc, pwd, nickname, gender, birthday, code])
def _db_register(attr,cursor):
	acc = attr[2]
	code = attr[7]
	# 获取用户的code
	sqlc = "select code from l_accont where account='%s' limit 1"
	acode = cursor.execute(sqlc % acc)
	results = cursor.fetchone()
	if results['code'] == code:
		handle = attr[1]
		pwd = attr[3]
		nickname = attr[4]
		gender = attr[5]
		birthday = attr[6]
		new_pwd = hashlib.sha1(pwd.encode("utf-8")).hexdigest()
		# 注册到网易云
		token = wyy_create_user(acc, nickname, acc)
		if token == None:
			handle(1)
			return None
		sql = "update l_accont set password='%s',userid='%d',token='%s',phone='%s',mail='%s',weixin='%s',qq='%s',create_time='%d',last_time='%d',lkey='%d',power='%d',nickname='%s',gender='%s',birthday='%s' where account='%s'"
		data = (new_pwd,0,token,'','','','',0,0,0,0, nickname, gender, birthday, acc)
		if cursor.execute(sql % data) > 0:
			handle([acc, pwd, token])
			return True
		else:
			handle(1)
		return None
	
#登陆 0成功 1没有该用户 2密码错误
# db_login(self.call_login,data['accont'],data['passward'])
def db_login(handle,acc,pwd):
	AddCachingQueue([_db_login,handle,acc,pwd])

def _db_login(attr,cursor):
	# def call_login(self,calldata):
	handle = attr[1]
	acc = attr[2]
	pwd = attr[3]
	pwd = hashlib.sha1(pwd.encode("utf-8")).hexdigest()
	# 设置缓存，从缓存中查询
	key = 'DataCache-%s-%s-%s' % (handle, acc, pwd)
	data = REDIS.get(key)
	# print 'from redis %s' % data
	if data:
		# print data
		data = eval(data)  # 将字符串字典转化为字典
		accont = data['account']
		curpsw = data['password']
		token = data['token']
		power = int(data['power'])
		if curpsw == None:
			# call_login(self,calldata):
			handle([1, token, power, accont])
		elif curpsw == pwd:
			handle([0, token, power, accont])
		else:
			handle([2, token, power, accont])
		# print('get from cache: %s' % data)
	if data is None:
		sql = "select * from l_accont where account='%s' limit 1"
		count=cursor.execute(sql % acc)
		data=cursor.fetchone()
		token = None
		curpsw = None
		accont = None
		power = 0
		if data:
			#print data
			REDIS.set(key, data, 20)  # 添加到缓存,设置过期时间
			accont = data['account']
			curpsw = data['password']
			token = data['token']
			power = int(data['power'])
		if curpsw == None:
			handle([1,token,power,accont])
		elif curpsw == pwd:
			handle([0,token,power,accont])
		else:
			handle([2,token,power,accont])

# 创建聊天室
def db_createRoom(handle,accid,name):
	AddCachingQueue([_db_createRoom,handle,accid,name]);
def _db_createRoom(attr,cursor):
	handle = attr[1]
	accid = attr[2]
	name = attr[3]
	calldata = wyy_create_room(accid,name)
	if calldata:
		sql = "INSERT INTO l_room (roomid, name, creator) VALUES (%d,'%s','%s')"
		data = (calldata['roomid'],calldata['name'],calldata['creator'])
		count=cursor.execute(sql % data)
		if count > 0:
			handle([calldata['roomid'],calldata['name']])
			return True
	handle(None)
	
# 获取公用聊天室列表
def db_getRoomList(handle):
	AddCachingQueue([_db_getRoomList,handle])
def _db_getRoomList(attr,cursor):
	'''
	[<function _db_login at 0x000000000350AD68>, <bound method User.call_login of <user.user.User instance at 0x0000000003FAB148>>
, u'goudan11', u'123456']
'''
	handle = attr[1]
	sql = 'select * from l_room'
	count=cursor.execute(sql)
	# 设置房间缓存
	key = 'RoomCache-%s' % handle
	data = REDIS.get(key)
	if data:
		data = eval(data)
		print 'from roomdata is %s' % data
		handle(data)
	elif data is None:
		data = cursor.fetchmany(count)
		REDIS.set(key, data, 20)
		handle(data)
# 搜索聊天室
# handle def call_searchRoom(self, listdata)
def db_searchRoom(handle):
	AddCachingQueue([_db_searchRoomList, handle])

def _db_searchRoomList(attr, cursor):
	handle = attr[1]
	sql = 'SELECT * FROM l_room WHERE %s'

def AddCachingQueue(attr):
	if not CachingQueue.empty():
		CachingQueue.put(attr)
	else:
		CachingQueue.put(attr)
		gevent.spawn(updataCachingQueue)
		
def updataCachingQueue():
	#获取数据库连接
	connection = connection_pool().borrow_connection()
	cursor = connection.cursor()
	#print 'connection mysql'
	#数据库批量操作
	bCommit = None
	nums = 0
	while not CachingQueue.empty():
		nums+=1
		attr = CachingQueue.get()
		# AddCachingQueue([_db_login,handle,acc,pwd])
		if attr[0](attr,cursor):
			bCommit=True
		
	# print 'CachingQueue:',nums
	#统一提交
	if bCommit:
		connection.commit()
		
	#回收连接
	cursor.close()
	connection_pool().return_connection(connection)
		
		
#方式1	
#with connection_pool().connection() as conn:
#	print '123445'
	
#方式2
#获取一个游标
#connection = connection_pool().borrow_connection()
#回收一个游标
#connection_pool().return_connection(connection)