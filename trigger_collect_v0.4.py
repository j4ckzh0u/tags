#! /usr/bin/env python2.7
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
import Queue
import threading
import uuid

# config
hostlistfile = 'hosts.txt'
port = 63001
apiserverurl='http://192.168.146.131:5000/hwinfo'
command = 'trigger'
# command = 'update'
updateurl = ''

threads = 20
queue1 = Queue.Queue()
queue2 = Queue.Queue() 

nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

#data = uuid + '|' + host + '|' + apiserverurl + '|' + command + '|' + updateurl + '|' + nowtime

def socketTrigger(host,port,data):
    s = socket.socket()
    s.connect((host, port))
    s.send(data.encode('utf8'))
    print s.recv(1024).decode(encoding='utf8')
    s.close()

with open(hostlistfile, 'r') as f:
    for host in f.readlines():
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        uuid = str(uuid.uuid4())
        data = uuid + '|' + host + '|' + apiserverurl + '|' + command + '|' + updateurl + '|' + nowtime
        cryptodata = cryptolib.encryptdata(data)
        queue.put(cryptodata + '\n', True, None)

class worker(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue=queue
        self.thread_stop=False
    def run(self):
        while not self.thread_stop:
            print "thread-[%d] %s: waiting for task " %(self.ident, self.name)
            try:
                task = queue1.get(block=True, timeout=20)
            except:
                print "task all done!!!"
                self.thread_stop = True
                break
            print "task recv: %s, taks NO: %d" % (task[0], task[1])
            

    def stop(self):
        self.thread_stop = True


# for i in range(20):
#     t = threading.Thread(target=socket, args=())