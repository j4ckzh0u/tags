#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# auth: zhoujunke
# date: 20190212

# command: trigger, update 
#       trigger: all host start hw info collect and post the data to API server
#       update:  all host update the script on host

# crypto : data(base64) ^ data(md5) + data(md5)
# data = command + '|' + updateurl + '|' + filepath + '|' + nowtime 

import cryptolib
import time
import subprocess
import urllib2
import sys

#data = raw_input()
data = sys.stdin.readline()
print("data1: " + data)

try:
    data = cryptolib.decryptdata(data.split('\n')[0])
    print("data2: " + data)
    datalist = data.split('|')
    command = datalist[0]
    updateurl = datalist[1]
    filepath = datalist[2]
    time = datalist[3]
except:
    print('data is error!!!')
    sys.exit()


if command == 'trigger':
    res = subprocess.Popen("python /root/py_code/salt_get_hwinfo_not_to_db.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.wait() == 0:
        print(res.stdout.read().split('\n')[0])
    else:
        print('command exec fail!!!')
elif command == 'update':
    d = urllib2.urlopen(updateurl)
    try:
        if d.code == 200:
            data = d.read()
            with open(filepath, 'wb') as f:
                f.write(data)
        print('script update success')
    except:
        print('url error')
        sys.exit()
