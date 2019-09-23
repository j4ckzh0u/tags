#! /usr/bin/env python2.7
# -*- coding:utf-8 -*-
# auth: zhoujunke
# date: 20190212

# command: trigger, update 
#       trigger: all host start hw info collect and post the data to API server
#       update:  all host update the script on host

# crypto : data(base64) ^ data(md5) + data(md5)
# data = uuid + '|' + host + '|' + apiserverurl + '|' + command + '|' + updateurl + '|' + nowtime 

import cryptolib
import sys

#data = raw_input()
data = sys.stdin.readline()
# print "data1: " + data

try:
    data = cryptolib.decryptdata(data.split('\n')[0])
    # print "data2: " + data
    uuid = data.split('|')[0]
    host = data.split('|')[1]
    apiserverurl = data.split('|')[2]
    command = data.split('|')[3]
    updateurl = data.split('|')[4]
except:
    print '10001:data split is error'
    sys.exit()

# print 'APIServer: ', apiserver
# print 'APIServerPort: ', apiserverport
# print 'Command: ', command

if command == 'trigger':
    import saltlib
    # import requests
    import json
    postdata = json.dumps(saltlib.data)
    try:
        # req = requests.post(apiserverurl, data=postdata)
        res = {}
        res['uuid'] = uuid
        res['host'] = host
        res['data'] = postdata
        rdata = json.dumps(res)
        print rdata
    except:
        print "10010:url error"
        sys.exit()
    sys.exit(0)
elif command == 'update':
    import urllib2
    d = urllib2.urlopen(updateurl)
    try:
        if d.code == 200:
            data = d.read()
            with open("saltlib.py", 'wb') as f:
                f.write(data)
        print 'script update success'
    except:
        print '10011:url error'
        sys.exit()