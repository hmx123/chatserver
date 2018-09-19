#-*- coding:utf-8 –*-
import hashlib,requests,json,time

AppKey = '0151eb211fb26ebf020684cfd8125624'
AppSecret = '269163c64b9e'

apiurl = {
	'create_user':'https://api.netease.im/nimserver/user/create.action',
	'create_room':'https://api.netease.im/nimserver/chatroom/create.action',
	'create_group':''
}

#状态码 http://dev.netease.im/docs/product/IM%E5%8D%B3%E6%97%B6%E9%80%9A%E8%AE%AF/%E6%9C%8D%E5%8A%A1%E7%AB%AFAPI%E6%96%87%E6%A1%A3/code%E7%8A%B6%E6%80%81%E8%A1%A8

#创建用户	
def wyy_create_user(accont):
	body = ('accid=%s&name=%s'%(accont,accont)).encode("utf-8")
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
			jsonData = None;
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
	