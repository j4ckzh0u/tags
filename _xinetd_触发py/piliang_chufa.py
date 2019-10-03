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
import sys

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
    # print(cdata)
    return cdata

def ddata(data):
    ddata = cryptolib.decryptdata(data)
    # print(ddata)
    return ddata

# cmd_gettime = cdata('gettime|||||')

# time = ddata('H0FdXkFDUA4AG18QBVcCAQIADAcDA09XUAIFVVUCHA==dc31679ce9e04b48525551aca66ec0a8')
def send_data(host, port, data, localip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    gettime = s.recv(1024).decode(encoding='utf-8').strip()
    print('gettime: {0}'.format(gettime))
    print('gettimeaaaa: {0}'.format(ddata(gettime)))
    try:
        nowtime = json.loads(ddata(gettime))["nowtime"]
        print('[ INFO ] Now time is : {0}'.format(nowtime))
    except Exception as e:
        print('[ ERR ] Can not get time from agent via 62354, {0}'.format(e))
        sys.exit(1010)

    cmd = data + '|' + str(localip) + '|' + str(nowtime)
    print('[ INFO ] CMD: {0}'.format(cmd))
    # print('t3: ', cmd)
    cmd = cdata(cmd) + '\n'
    # s.send(cmd.encode(encoding='utf8'))
    s.send(bytes(cmd, 'utf8'))
    recvdata = s.recv(1024).decode(encoding='utf-8')
    print("[info] recvdata: ", recvdata)
    try:
        jdata = json.loads(recvdata)
        print(jdata["action"])
        print(jdata["result"])
    except Exception as e:
        pass
    s.close()

def check_status(host):
    pass

if __name__ == '__main__':
    if len(sys.argv) == 4:
        cmd1 = sys.argv[1]
        cmd2 = sys.argv[2]
        cmd3 = sys.argv[3]
        cmd4 = sys.argv[4]
        print(cmd1, int(cmd2), cmd3, cmd4)
        send_data(cmd1, int(cmd2), cmd3, cmd4)
    else:
        print('''please set 4 args.
command like this:
    piliang_chufa "192.168.146.180" 62354 "inventory|manual|||" "192.168.146.180"
    piliang_chufa "192.168.146.180" 62354 "netscan|(null or ip)|||" "192.168.146.180"
    piliang_chufa "192.168.146.180" 62354 "status||||" "192.168.146.180"
    piliang_chufa "192.168.146.180" 62354 "update|downloadurl|destfilepath|owner|authmode" "192.168.146.180"
        ''')
    # send_data('192.168.146.180', 62354, 'inventory|manual|||', '192.168.146.180')
    # send_data('192.168.146.180', 62354, 'netscan|192.168.3.1|||', '192.168.146.180')
    # send_data('192.168.146.180', 62354, 'status||||', '127.255.255.254')
    # send_data('192.168.146.180', 62354, 'checksta62354||||', '192.168.146.180')
    # send_data('192.168.146.180', 62354, 'update|http://192.168.146.180:8000/1.txt|/tmp/a11.txt|root|444 & mkdir -p /tmp/FFFFFFx', '127.255.255.254')
