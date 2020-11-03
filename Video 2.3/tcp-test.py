import socket
hostname = '192.168.086.003'
port = 49152
addr = (hostname,port)
clientsock = socket.socket()
clientsock.connect(addr)
say = input("ACK[0D 0A]")
clientsock.send(bytes(say,encoding='gbk'))
recvdata = clientsock.recv(1024)
print(str(recvdata,encoding='gbk'))
clientsock.close()
