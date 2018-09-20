#-*- coding:utf-8 –*-
from pymysqlpool import ConnectionPool
import gevent
from gevent.queue import Queue
from wyyapi import *
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
	
# 注册 0成功 1失败 2已存在账号 3数据库写入异常
def db_register(handle,acc,pwd):
	AddCachingQueue([_db_register,handle,acc,pwd]);
def _db_register(attr,cursor):
	handle = attr[1]
	acc = attr[2]
	pwd = attr[3]
	pwd = hashlib.sha1(pwd.encode("utf-8")).hexdigest()
	
	#检测是否存在
	sql = "select password from l_accont where account='%s' limit 1"
	cursor.execute(sql % acc)
	if cursor.fetchone():
		handle(2)
		return None
		
	#注册到网易云
	token = wyy_create_user(acc)
	if token == None:
		handle(1)
		return None
	
	sql = "INSERT INTO l_accont (id, account, password,userid,token,phone,mail,weixin,qq,create_time,last_time,lkey,power) VALUES (%d,'%s','%s',%d,'%s','%s','%s','%s','%s',%d,%d,%d,%d)"
	data = (0,acc,pwd,0,token,'','','','',0,0,0,0)
	if cursor.execute(sql % data) > 0:
		handle(0)
		return True
	else:
		handle(1)
	return None
	
#登陆 0成功 1没有该用户 2密码错误

def db_login(handle,acc,pwd):
	AddCachingQueue([_db_login,handle,acc,pwd])


def _db_login(attr,cursor):
	handle = attr[1]
	acc = attr[2]
	pwd = attr[3]
	pwd = hashlib.sha1(pwd.encode("utf-8")).hexdigest()
	# 设置缓存，从缓存中查询
	key = 'DataCache-%s-%s-%s' % (handle, acc, pwd)
	data = REDIS.get(key)
	print 'from redis %s' % data
	if data:
		# print data
		data = eval(data)  # 将字符串字典转化为字典
		accont = data['account']
		curpsw = data['password']
		token = data['token']
		power = int(data['power'])
		if curpsw == None:
			handle([1, token, power, accont])
		elif curpsw == pwd:
			handle([0, token, power, accont])
		else:
			handle([2, token, power, accont])
		print('get from cache: %s' % data)
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
			REDIS.set(key, data, 5)  # 添加到缓存,设置过期时间
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
	AddCachingQueue([_db_getRoomList,handle]);
def _db_getRoomList(attr,cursor):
	handle = attr[1]
	sql = 'select * from l_room'
	count=cursor.execute(sql)
	#data=cursor.fetchone()
	# 每次获取时会从上次游标的位置开始移动size个位置，返回size条数据
	listdata = None
	if count >0:
		data = cursor.fetchmany(count)
		listdata = []
		count = 0
		for d in data:
			count+=1
			listdata.append({'roomid':d['roomid'],'name':d['name'],'index':count})
	handle(listdata)
	
	
def AddCachingQueue(attr):
	if not CachingQueue.empty():
		CachingQueue.put(attr);
	else:
		CachingQueue.put(attr);
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
		if attr[0](attr,cursor):
			bCommit=True
		
	#print 'CachingQueue:',nums
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