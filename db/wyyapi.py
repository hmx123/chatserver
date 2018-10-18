#-*- coding:utf-8 –*-
import hashlib,requests,json,time

AppKey = '0151eb211fb26ebf020684cfd8125624'
AppSecret = '269163c64b9e'

apiurl = {
	'create_user':'https://api.netease.im/nimserver/user/create.action',
	'create_room':'https://api.netease.im/nimserver/chatroom/create.action',
	'create_group':'',
	'send_code': 'https://api.netease.im/sms/sendcode.action',
 	'check_code': 'https://api.netease.im/sms/verifycode.action',
}

#状态码 http://dev.netease.im/docs/product/IM%E5%8D%B3%E6%97%B6%E9%80%9A%E8%AE%AF/%E6%9C%8D%E5%8A%A1%E7%AB%AFAPI%E6%96%87%E6%A1%A3/code%E7%8A%B6%E6%80%81%E8%A1%A8

#创建用户	
def wyy_create_user(accont, nickname, acc):
	body = ('accid=%s&name=%s&mobile=%s'%(accont,nickname, acc)).encode("utf-8")
	nonce = '575728120'#随机数（最大长度128个字符）
	curTime = str(int(time.time()))
	checkSum = AppSecret+nonce+curTime
	checkSum = hashlib.sha1(checkSum.encode("utf-8")).hexdigest()
	headers = {'content-type': 'application/x-www-form-urlencoded;charset=utf-8','AppKey':AppKey,'Nonce':nonce,'CurTime':curTime,'CheckSum':checkSum}
	response = requests.post(apiurl['create_user'],data = body,headers = headers)
	if response.status_code == 200:
		print response.text
		try:
			jsonData = json.loads(response.text)
			if jsonData['code'] == 200:
				return jsonData['info']['token']
		except ValueError:
			jsonData = None
	return None
	
#创建房间
#creator		String	是	聊天室属主的账号accid
#name			String	是	聊天室名称，长度限制128个字符
#announcement	String	否	公告，长度限制4096个字符
#broadcasturl	String	否	直播地址，长度限制1024个字符
#ext			String	否	扩展字段，最长4096字符
#queuelevel		int		否	队列管理权限：0:所有人都有权限变更队列，1:只有主播管理员才能操作变更。默认0
def wyy_create_room(accid,name):
	body = ('name=%s&creator=%s'%(name,accid)).encode("utf-8")
	nonce = '575728120'#随机数（最大长度128个字符）
	curTime = str(int(time.time()))
	checkSum = AppSecret+nonce+curTime
	checkSum = hashlib.sha1(checkSum.encode("utf-8")).hexdigest()
	headers = {'content-type': 'application/x-www-form-urlencoded;charset=utf-8','AppKey':AppKey,'Nonce':nonce,'CurTime':curTime,'CheckSum':checkSum}
	response = requests.post(apiurl['create_room'],data = body,headers = headers)
	if response.status_code == 200:
		print response.text
		try:
			jsonData = json.loads(response.text)
			if jsonData['code'] == 200:
				return jsonData['chatroom']
		except ValueError:
			jsonData = None;
	return None

# 验证码发送
def sendcode(mobile):
	TEMPLATEID = "9374242"
	CODELEN = "6"
	body = ('templateid=%s&mobile=%s&codeLen=%s' % (TEMPLATEID, mobile, CODELEN)).encode("utf-8")
	nonce = '575728120'  # 随机数（最大长度128个字符）
	curTime = str(int(time.time()))
	checkSum = AppSecret + nonce + curTime
	checkSum = hashlib.sha1(checkSum.encode("utf-8")).hexdigest()
	headers = {'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
			   'AppKey': AppKey,
			   'Nonce': nonce,
			   'CurTime': curTime,
			   'CheckSum': checkSum}
	response = requests.post(apiurl['send_code'], data=body, headers=headers)
	if response.status_code == 200:
		print response.text
		try:
			jsonData = json.loads(response.text)
			if jsonData['code'] == 200:
				return jsonData['obj']
		except ValueError:
			jsonData = None
	return None
# 验证码校验
def checkcode(mobile, code):
	body = ('mobile=%s&code=%s' % (mobile, code)).encode("utf-8")
	nonce = '575728120'  # 随机数（最大长度128个字符）
	curTime = str(int(time.time()))
	checkSum = AppSecret + nonce + curTime
	checkSum = hashlib.sha1(checkSum.encode("utf-8")).hexdigest()
	headers = {'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
			   'AppKey': AppKey,
			   'Nonce': nonce,
			   'CurTime': curTime,
			   'CheckSum': checkSum}
	response = requests.post(apiurl['check_code'], data=body, headers=headers)
	if response.status_code == 200:
		print response.text
		try:
			jsonData = json.loads(response.text)
			if jsonData['code'] == 200:
				return True
		except ValueError:
			jsonData = None
	return None

# 用户token更新
def updatatoken(acc):
	url = 'https://api.netease.im/nimserver/user/refreshToken.action'
	body = ('accid=%s' % (acc)).encode("utf-8")
	nonce = '575728120'  # 随机数（最大长度128个字符）
	curTime = str(int(time.time()))
	checkSum = AppSecret + nonce + curTime
	checkSum = hashlib.sha1(checkSum.encode("utf-8")).hexdigest()
	headers = {'content-type': 'application/x-www-form-urlencoded;charset=utf-8', 'AppKey': AppKey, 'Nonce': nonce,
			   'CurTime': curTime, 'CheckSum': checkSum}
	response = requests.post(url=url, data=body, headers=headers)
	print response.text
