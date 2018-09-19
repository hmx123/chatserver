import socket
import time

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server = ('192.168.181.1', 8080)

# 用户登录
data_user = '{"head":1000,"action":1,"error":"","data":{"accont":"goudan11","passward":"123456"}}'
udp_socket.sendto(data_user.encode(), udp_server)

# 心跳连接
count = 0
while 1:
	data_conn = '{"head":999,"action":1,"error":"","data":{"accont":"goudan11","passward":"123456"}}'
	udp_socket.sendto(data_conn.encode(), udp_server)
	# 接受服务端数据
	new_data, address = udp_socket.recvfrom(1024)
	print(new_data.decode())
	time.sleep(170)
	count += 1
	if count == 2:
		break
# 获取聊天室列表
data_room = '{"head":1001,"action":2,"error":"","data":{"accont":"goudan11","passward":"123456","name":"liaotian"}}'
udp_socket.sendto(data_room.encode(), udp_server)
new_data, address = udp_socket.recvfrom(1024)
print(new_data, address)
udp_socket.close()