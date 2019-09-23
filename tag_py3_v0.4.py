#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# -*- coding:gbk _*-
######## data format
# [
#   {
#       "Label":"YWa",
#       "Tags":
#           [
#               {"Key":"aa","Value":"bb"},
#               {"Key":"cc","Value":"dd"}
#           ]
#   },
# ]
# list->dict->list->lsit->dict->k,v

#windows tag 文件存在于c:\tags或者d:\tags目录下，tag文件必须以.tag结尾. eg: c:\tags\xiangmu.tag
#unix 的tag文件存在于/root和/home下的.tags目录下，tag文件必须以.tag结尾. eg: /root/.tags/xiangmu.tag
###############xiangmu.tag##################
# [工程项目信息]
# 工程项目名称=PAAS一期
# 工程项目编号=XM-PAAS-001
# 资产标签=ZC-PAAS-WL-xxxx
# 工程负责人=张三
# 联系电话=130xxxxxxx
# 邮箱=aaaa@cccc.com
#################################

import configparser
import os
import sys
from pathlib2 import Path
import json
import subprocess
from urllib import parse
import requests
import socket

###find all tag file in /root and /home on linux; in c:\tags and d:\tags on windows
###the tag file is *.tag
fusionagent_path = '/opt/FusionInventory-Agent/'
fusionagentcfg = fusionagent_path + 'etc/fusioninventory/agent.cfg'
# get cmdb server url
with open(fusionagentcfg, 'r') as cfg:
    for line in cfg.readlines():
        if line.strip().startswith('server'):
            cmdbserver = parse.urlparse(line.split('=')[1].strip().split('\n')[0]).netloc
            serverip = cmdbserver.split(':')[0]
            print("[+] CMDBserver IP: ", cmdbserver)

# get host ip
def get_host_ip():
    try:
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.connect(('1.2.3.4', 8008))
        ip = sc.getsockname()[0]
    finally:
        sc.close()
        print("[+] local IP: ", ip)
    return ip

ostype = sys.platform
print("[+] OSType is: ", ostype)
unix = ['linux', 'linux2', 'hpux', 'aix']
if ostype in unix:
    path = ['/root', '/home']

    pingcmd = 'ping -c 3 ' + serverip

    fusionagent_start_shell = fusionagent_path + 'start.sh'
    perlenv = fusionagent_path + '.perl_env'
    fusioncmd = fusionagent_path + '.fusion_cmd'
    if not os.path.exists(perlenv):
        with open(fusionagent_start_shell, 'r') as f:
            for line in f.readlines():
                if line.strip().startswith('export PERL'):
                    with open(perlenv, 'w') as penv:
                        penv.write(line)

    if not os.path.exists(fusioncmd):
        with open(fusionagent_start_shell,'r') as f:
            for line in f.readlines():
                if line.strip().startswith('perl /opt/FusionInventory-Agent'):
                    with open(fusioncmd, 'w') as fcmd:
                        if '-d' in line:
                            line = line.replace('-d', ' -t')
                        else:
                            line = line + ' -t'
                        fcmd.write(line)

else:
    path = ['c:\\tags','d:\\tags']
    pingcmd = 'ping -n 3 ' + serverip
paths = []
for fpath in path:
    p = Path(fpath)
    for filepath in list(p.glob('**/*.tag')):
        filepath = str(filepath)
        if os.path.isfile(filepath):
            print("[+] tag file path:", filepath)
            paths.append(filepath)

labels = []

for tagfile in paths:
    config = configparser.ConfigParser()
    config.read(tagfile)
    for i in config.sections():
        label = {}
        print("[+] Label:", i)
        label["Label"] = i
        tags = []
        for j in config.items(i):
            item = {}
            item["Key"] = j[0]
            item["Value"] = j[1]
            print("[+] tag: ", j[0]+" = "+j[1])
            tags.append(item)
        label["Tags"] = tags
        labels.append(label)
# print labels
print("[+] Json Dump data is :", json.dumps(labels))
tag_info = json.dumps(labels)

hostip = get_host_ip()
statusapi = 'http://' + cmdbserver + '/ft/status.php'
print("[ INFO ] The Status API URL is: ", statusapi)
pingres = subprocess.Popen(pingcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if pingres.wait() == 0:
    vatsping = 1
else:
    vatsping = 0
statuscode = 0
if vatsping:
    try:
        req = requests.get(url=statusapi, headers={"User-Agent":"python-Fusioninventory"}, timeout=5)
        ctx = req.json()
        statuscode = req.status_code
    finally:
        req.close()
    '''
    response data : {"action": "remoteaddress", "value": "192.168.146.1"}
    '''
    if statuscode == 200:
        print("[ INFO ] connect status api %s is successfull ! " % statusapi)
        vats10080 = 1
        if ctx["action"] == 'remoteaddress':
            remoetip = ctx["value"]
        if remoetip == hostip:
            nettype = "direct"
        else:
            nettype = "nat"
    else:
        vats10080 = 0
        print("[ ERR ] connot connect status api %s , Please Check it !!! " % statusapi)

if len(sys.argv) > 1:
    if sys.argv[1] == 'manual':
        module = 'manual'
else:
    module = 'auto'

# post data

'''
    {
        'id': ip, 
        'module': 'manual|auto', 
        'nettype': 'nat|direct',
        'result': 
            [
                {'action': 'atsping', 'value': 1}, 
                {'action': 'ats10080', 'value': 1}
            ]
    }

'''

'''post result data'''
if statuscode == 200:
    data = {}
    data["id"] = hostip
    data["module"] = module
    data["nettype"] = nettype
    result = []
    d1 = {}
    d2 = {}
    d1["action"] = "atsping"
    d1["value"] = vatsping
    d2["action"] = "ats10080"
    d2["value"] = vats10080
    result.append(d1)
    result.append(d2)
    data["result"] = result
    print("[ INFO ] POST DATA: ", data)

    postreq = requests.post(url=statusapi, data=json.dumps(data), headers={"User-Agent":"python-Fusioninventory"}, timeout=5)
    if postreq.status_code == 200:
        print("[ INFO ] status data post successfull! ")
    else:
        print("[ ERR ] the URL: %s is cannot connect !!! " % statusapi)

with open(perlenv) as f:
    env_cmd = f.readlines()[0].split('\n')[0]
with open(fusioncmd) as f:
    fusion_cmd = f.readlines()[0].split('\n')[0]
print("[ INFO ] set perl env command is :", env_cmd)
print("[ INFO ] Fusion agent run command is :", fusion_cmd)
cmd = env_cmd + ';' + fusion_cmd + ' ' + "'" + str(tag_info) + "'"
print("[ INFO ] run in shell cmd: ", cmd)
res = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
if res.wait() == 0:
    print("[ INFO ] This is command stdout -------------[start]-------------------")
    for stdinfo in res.stdout.readlines():
        print(stdinfo)
    print("[ INFO ] This is command stdout --------------[END]--------------------")
