#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# auth: zhoujunke
# date: 20190212

# crypto : data(base64) ^ data(md5) + data(md5)

import cryptolib
import subprocess
import requests
import sys
import socket
import json
import time

currpath = '/opt/FusionInventory-Agent/tags'
inventory_tag = currpath + '/inventory_tag'

def cdata(data):
    cdata = cryptolib.encryptdata(data)
    return cdata
    #print(cdata)

def csplitdata(data):
    try:
        data = cryptolib.decryptdata(data.split('\n')[0])
        # print("[ DEBUG ] get DATA: " + data)
        datalist = data.split('|')
        command = datalist[0]
        args1 = datalist[1]
        args2 = datalist[2]
        args3 = datalist[3]
        args4 = datalist[4]
        authip = datalist[5]
        authtime = datalist[6]
        return command, args1, args2, args3, args4, authip, authtime
    except:
        print('data is error!!!')
        sys.exit()

def get_host_ip():
    try:
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.connect(('10.0.0.1', 8008))

    finally:
        ip = sc.getsockname()[0]
        sc.close()
        # print("[ INFO ] Local IP: ", ip)
    return ip
nowtime = str(time.time())
tdate = {}
tdate["nowtime"] = nowtime
# first print, second flush, then it will print out.
print(cdata(json.dumps(tdate)))
sys.stdout.flush()

readdata = sys.stdin.readline()
#data = input('Please input data: ')
command, args1, args2, args3, args4, authip, authtime = csplitdata(data=readdata)
# print(command, args1, args2, args3, args4, authip)

localip = get_host_ip()

if authtime == nowtime and (authip == localip or authip == '127.255.255.254'):
    if command == 'inventory':
        cmd = "{0} {1}".format(inventory_tag, args1)
        # print('[ EXEC ] inventory: {0}'.format(cmd))
        cmdstatus, cmdresult = subprocess.getstatusoutput(cmd)
        if cmdstatus == 0:
            print('*' * 10 + '[ EXEC ] inventory success' + '*' * 10)
        else:
            print('[ ERR ], {0}'.format(cmdresult))
    elif command == 'update':
        d = requests.get(args1)
        try:
            if d.status_code == 200:
                with open(args2, 'wb') as f:
                    for data in d.iter_content(100000):
                        f.write(data)
                print('[ EXEC ] update success')
                cmd = 'chown {0}:{0} {1}; chmod {2} {1}'.format(args3, args2, args4)
                print(cmd)
                cmdstatus, cmdresult = subprocess.getstatusoutput(cmd)
                if cmdstatus == 0:
                    print('*' * 10 + '[ EXEC ] chown && chmod success' + '*' * 10)
                else:
                    print('[ ERR ], {0}'.format(cmdresult))
            else:
                print('[ ERR ] update Faild,file url error')
        except:
            print('url error')
            sys.exit()
    elif command == 'netscan':
        cmd = "{0} netscan {1}".format(inventory_tag, args1)
        print('[ EXEC ] netscan: {0}'.format(cmd))
        cmdstatus, cmdresult = subprocess.getstatusoutput(cmd)
        if cmdstatus == 0:
            print('*' * 10 + '[ EXEC ] netscan success' + '*' * 10)
        else:
            print('[ ERR ], {0}'.format(cmdresult))

    elif command == 'status':
        print('[ EXEC ] status: {0} status'.format(inventory_tag))
        cmdstatus, cmdresult = subprocess.getstatusoutput("{0} status".format(inventory_tag))
        if cmdstatus == 0:
            print('*' * 10 + '[ EXEC ] status success' + '*' * 10)
        else:
            print('[ ERR ], {0}'.format(cmdresult))
    elif command == 'checksta62354':
        data = dict()
        data["action"] = 'sta62354'
        data["result"] = 1
        data = json.dumps(data)
        sys.stdout.write(data)
    else:
        print('[ ERR ] Unknow what to do!')
else:
    print('[ ERR ] auth error!')
    sys.exit()
