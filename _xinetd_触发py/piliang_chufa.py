#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# auth: zhoujunke
# date: 20190212

# command: trigger, update
#       trigger: all host start hw info collect and post the data to API server
#       update:  all host update the script on host

# crypto : data(base64) ^ data(md5) + data(md5)
# data = uuid + '|' + host + '|' + apiserverurl + '|' + command + '|' + updateurl + '|' + nowtime
# python trigger_collect.py hostlist.txt

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

def cdata(data):
    cdata = cryptolib.encryptdata(data)
    print(cdata)
    return cdata

def ddata(data):
    ddata = cryptolib.decryptdata(data)
    print(ddata)
    return ddata

cmd_gettime = cdata('gettime|||||')

time = ddata('H0FdXkFDUA4AG18QBVcCAQIADAcDA09XUAIFVVUCHA==dc31679ce9e04b48525551aca66ec0a8')
def send_data(host, port, data):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host, port))
    ntime = cmd_gettime + '\n'
    s.send(ntime.encode('utf8'))
    time_data = str(s.recv(1024))
    if time_data[-1] == '\n':
        time_data = time_data[:-1]
    # print(type(time_data))
    # time_data = str(time_data).split('\n')[0]
    # print(type(time_data))
    print('ttt:', time_data)
    nowtime = json.loads(ddata(time_data))["nowtime"]
    print(nowtime)
    # s.send()



def netscan(netip):

    pass

def inventory(module='manual'):
    pass

def status():
    pass

def update(url, destpath, owner, authmode):
    pass


if __name__ == '__main__':
    send_data('192.168.146.180', 62354, 'aa')
#
# with open(hostlistfile, 'r') as f:
#     for host in f.readlines():
#         nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         uuid = str(uuid.uuid4())
#         data = uuid + '|' + host + '|' + apiserverurl + '|' + command + '|' + updateurl + '|' + nowtime
#         cryptodata = cryptolib.encryptdata(data)
#         queue.put(cryptodata + '\n', True, None)
#
#
# class worker(threading.Thread):
#     def __init__(self, queue):
#         threading.Thread.__init__(self)
#         self.queue = queue
#         self.thread_stop = False
#
#     def run(self):
#         while not self.thread_stop:
#             print
#             "thread-[%d] %s: waiting for task " % (self.ident, self.name)
#             try:
#                 task = queue1.get(block=True, timeout=20)
#             except:
#                 print
#                 "task all done!!!"
#                 self.thread_stop = True
#                 break
#             print
#             "task recv: %s, taks NO: %d" % (task[0], task[1])
#
#     def stop(self):
#         self.thread_stop = True
#
# # for i in range(20):
# #     t = threading.Thread(target=socket, args=())