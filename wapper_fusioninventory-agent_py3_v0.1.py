#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# auth: zhoujunke
# date: 20190212
# crypto : data(base64) ^ data(md5) + data(md5)
# data = command + '|' + updateurl + '|' + filepath + '|' + nowtime 

import cryptolib
import time
import subprocess
import requests
import sys

#data = raw_input()
def cprint(data):
    cdata = cryptolib.encryptdata(data)
    print(cdata)

nowtime = time.time()
print("[ INFO ] now time is: {0}".format(nowtime))
data = sys.stdin.readline()
try:
    data = cryptolib.decryptdata(data.split('\n')[0])
    print("[ DEBUG ] get DATA: " + data)
    datalist = data.split('|')
    command = datalist[0]
    updateurl = datalist[1]
    filepath = datalist[2]
    ctime = datalist[3]
    print(command)
except:
    print('data is error!!!')
    sys.exit()

if command == 'gettime':
    cprint({'nowtime': nowtime})

elif ctime == nowtime:
    if command == 'inventory':
        res = subprocess.Popen("python /root/py_code/salt_get_hwinfo_not_to_db.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.wait() == 0:
            print(res.stdout.read().split('\n')[0])
        else:
            print('command exec fail!!!')
    elif command == 'update':
        d = requests.get(updateurl)
        try:
            if d.code == 200:
                data = d.read()
                with open(filepath, 'wb') as f:
                    f.write(data)
            print('script update success')
        except:
            print('url error')
            sys.exit()
