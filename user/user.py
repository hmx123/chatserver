#-*- coding:utf-8 –*-
'''
每个用户协程
'''

import const
from base import *
from db.dbsql import *
from db.wyyapi import sendcode

class User(Base):
	def __init__(self,_server,_conn,_addr):
		#print("\nadd user %s:%s"%(_addr[0],_addr[1]))
		self.initbase(_conn,_addr,self.command_action)
		self.userid = 0
		self.power = 0

	# 登陆消息回执
	def call_login(self,calldata):
		# handle([0, token, power, accont])
		if calldata[0] == 0:
			self.userid = calldata[3]
			self.power = calldata[2]
			self.send(MSG_HEAD_ACCONT,MSG_ACTION_LOGIN,{'accid':self.userid,'token':calldata[1],'power':self.power},['','没有该用户','密码错误'][calldata[0]])
	# 发送验证码回执
	def call_sendcode(self, calldata):
		if len(calldata) > 1:
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_CODECHECK, {'account':calldata[1], 'code': 200}, '')
		else:
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_CODECHECK, None, ['phone err', 'user already'][calldata[0]])
	# 注册消息回执
	def call_register(self,calldata):
		if len(calldata) > 1:
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_REGISTER, {'account':calldata[0], 'passward':calldata[1], 'token':calldata[2]}, '')  # acc, pwd, token
		else:
			self.send(MSG_HEAD_ACCONT,MSG_ACTION_REGISTER,None,['','没有该用户','密码错误'][calldata])

	# 重连消息回执
	def call_reconnect(self,calldata):
		if calldata[0] == 0:
			self.userid = calldata[3]
			self.power = calldata[2]
			self.send(MSG_HEAD_ACCONT,MSG_ACTION_RECONNECT,{'accid':self.userid,'power':self.power},['','没有该用户','密码错误'][calldata[0]])

		# 创建聊天室回执
	def call_createRoom(self,calldata):
		if calldata:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_CREATE,{'roomid':calldata[0],'name':calldata[1]})
		else:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_CREATE,None,'Failed to create a room')

		# 获取聊天室回执
	def call_getRoomList(self,listdata):
		if listdata:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_ROOM_LIST,{'roomlist':listdata})
		else:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_ROOM_LIST,None,'No chat room available')

	# 聊天室搜索回执
	def call_searchRoom(self, listdata):
		if listdata:
			self.send()
		else:
			self.send()

	def command_action(self,head,action,data):
		# 账号模块
		if head == MSG_HEAD_ACCONT:
			# 登陆
			if action == MSG_ACTION_LOGIN:
				db_login(self.call_login,data['accont'],data['passward'])
			# 发送验证码
			elif action == MSG_ACTION_CODECHECK:
				db_sendcode(self.call_sendcode, data['accont'])
			# 注册
			elif action == MSG_ACTION_REGISTER:
				# 增加注册信息 用户昵称，性别，生日 "nickname":"xxxx", "gender":"1","birthday":"xxxx"
				db_register(self.call_register,data['accont'],data['passward'], data['nickname'], data['gender'], data['birthday'], data['code'])
			# 重连
			elif action == MSG_ACTION_RECONNECT:
				db_login(self.call_reconnect,data['accont'],data['passward'])
		else:
			# 业务功能都必须先登陆
			if self.userid == 0:
				#db_login(self.logincall,'longyifu','123456')
				#calldata = db_login('longyifu','123456')
				self.send(head,action,None,'please login first')
				return

			# 聊天室模块
			if head == MSG_HEAD_ROOM:
				# 创建聊天室
				if action == MSG_ACTION_CREATE:
					if self.power > 0:
						db_createRoom(self.call_createRoom,self.userid,data['name'])
					else:
						self.send(head,action,None,'permission denied')
					# 获取公用聊天室列表
				elif action == MSG_ACTION_ROOM_LIST:
					db_getRoomList(self.call_getRoomList)
				# 聊天室搜索
				elif action == 'search':
					db_searchRoom(self.call_searchRoom)
