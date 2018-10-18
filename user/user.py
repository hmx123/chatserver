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
		if calldata[0] == 0:
			self.userid = calldata[3]
			self.power = calldata[2]
			self.send(MSG_HEAD_ACCONT,MSG_ACTION_LOGIN,{'accid':self.userid,'token':calldata[1],'power':self.power},['','没有该用户','密码错误'][calldata[0]])
		else:
			self.userid = calldata[1]
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_LOGIN, {'accid':self.userid} ,['', '没有该用户', '密码错误'][calldata[0]])
	# 注册消息回执
	def call_register(self,calldata):
		if len(calldata) > 1:
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_REGISTER,{'account': calldata[0], 'password': calldata[1], 'token': calldata[2]}, '')
		else:
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_REGISTER, None, ['', '注册失败', '用户已注册', '验证码错误'][calldata[0]])

	# 密码修改回执
	def call_pwdalter(self, calldata):
		err = ['密码修改成功，请返回登录', '验证码错误', '用户不存在', '密码修改失败']
		if calldata[0] == 0:
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_PASSWORD, {'account':calldata[1]}, '')
		else:
			self.send(MSG_HEAD_ACCONT, MSG_ACTION_PASSWORD, {'account': calldata[1]}, err[calldata[0]])

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
			self.send(MSG_HEAD_ROOM,MSG_ACTION_CREATE,None,'创建聊天室失败')

		# 获取聊天室回执
	def call_getRoomList(self,listdata):
		if listdata:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_ROOM_LIST,{'roomlist':listdata})
		else:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_ROOM_LIST,None,'没有聊天室')

	# 推送历史回执
	def call_jgpush(self, listdata):
		if listdata:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_ROOM_LIST,{'roomlist':listdata})
		else:
			self.send(MSG_HEAD_ROOM,MSG_ACTION_ROOM_LIST,None,'1没有聊天室')


	def command_action(self,head,action,data):
		# 账号模块
		try:
			if head == MSG_HEAD_ACCONT:
				# 登陆
				if action == MSG_ACTION_LOGIN:
					db_login(self.call_login,data['accont'],data['password'])
				# 发送验证码
				elif action == MSG_ACTION_CODE:
					code = sendcode(data['accont'])
					if code:
						self.send(MSG_HEAD_ACCONT, MSG_ACTION_CODE, {'accont': data['accont'], 'code': 200}, '')
					else:
						self.send(MSG_HEAD_ACCONT, MSG_ACTION_CODE, {'accont': data['accont'], 'code': 400}, '验证码发送失败')
				# 注册
				elif action == MSG_ACTION_REGISTER:
					db_register(self.call_register, data['accont'], data['password'], data['nickname'], data['gender'],
								data['birthday'], data['code'])
				elif action == MSG_ACTION_PASSWORD:
					db_pwdalter(self.call_pwdalter, data['accont'], data['password'], data['code'])
				# 重连
				elif action == MSG_ACTION_RECONNECT:
					db_login(self.call_reconnect,data['accont'],data['password'])
				# 获取推送历史
				elif action == 10:
					db_jgpush(self.call_jgpush)
			else:
				# 业务功能都必须先登陆
				if self.userid == 0:
					#db_login(self.logincall,'longyifu','123456')
					#calldata = db_login('longyifu','123456')
					self.send(head,action,None,'请先登录')
					return

				# 聊天室模块
				if head == MSG_HEAD_ROOM:
					# 创建聊天室
					if action == MSG_ACTION_CREATE:
						if self.power > 0:
							db_createRoom(self.call_createRoom,self.userid,data['name'])
						else:
							self.send(head,action,None,'权限不足')
						# 获取公用聊天室列表
					elif action == MSG_ACTION_ROOM_LIST:
						db_getRoomList(self.call_getRoomList)
		except Exception as e:
			print e
