#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# auth: zhoujunke
# date: 20190212

import cryptolib
import socket
import time
import threading
import queue
import json

threads = 20
queue1 = queue.Queue()
queue2 = queue.Queue()

nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# time = get from server via 62354, use gettime command
# data = inventory|auto(manual)|time
# data = netscan|ip/''|time
# data = status||time
# data = update|url|destpath|own(拥有者)|authmode(权限类型)|time
#           0    1     2        3          4               5
def cdata(data):
    cdata = cryptolib.encryptdata(data)
    print(cdata)
    return cdata

def ddata(data):
    ddata = cryptolib.decryptdata(data)
    print(ddata)
    return ddata

# cmd_gettime = cdata('gettime|||||')

# time = ddata('H0FdXkFDUA4AG18QBVcCAQIADAcDA09XUAIFVVUCHA==dc31679ce9e04b48525551aca66ec0a8')
def send_data(host, port, data, localip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    cmd = data + '|' + str(localip)
    print('t3: ', cmd)
    cmd = cdata(cmd) + '\n'
    # s.send(cmd.encode(encoding='utf8'))
    s.send(bytes(cmd, 'utf8'))
    recvdata = s.recv(1024).decode(encoding='utf-8')
    print("[info] recvdata: ", recvdata)
    s.close()

def check_status(host):
    pass

if __name__ == '__main__':
    # send_data('192.168.146.180', 62354, 'inventory|manual|||', '192.168.146.180')
    # send_data('192.168.146.180', 62354, 'netscan|192.168.43.1|||', '192.168.146.180')
    # send_data('192.168.146.180', 62354, 'status||||', '192.168.146.180')
    send_data('192.168.88.190', 62354, 'checksta62354||||', '192.168.88.190')
    #send_data('192.168.146.180', 62354, 'update|http://192.168.146.180:8000/q1.txt|/tmp/a11.txt|root|444', '127.255.255.254')
