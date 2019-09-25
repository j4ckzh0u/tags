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


if len(sys.argv) > 1:
    if sys.argv[1] == 'manual':
        module = 'manual'
else:
    module = 'auto'

# get host ip
def get_host_ip():
    try:
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.connect(('1.2.3.4', 8008))

    finally:
        ip = sc.getsockname()[0]
        sc.close()
        print("[ INFO ] local IP: ", ip)
    return ip

def urlparserhostip(url):
    domain = parse.urlparse(url.strip().split('\n')[0]).netloc
    if ':' in domain:
        ip = domain.split(':')[0]
        port = domain.split(':')[1]
    else:
        ip = domain
        port = 80
    return domain, ip, port

def gettags(paths, ostype):
    for fpath in paths:
        p = Path(fpath)
        for filepath in list(p.glob('**/*.tag')):
            filepath = str(filepath)
            if os.path.isfile(filepath):
                print("[ INFO ] tag file path:", filepath)
                paths.append(filepath)
    labels = []
    for tagfile in paths:
        config = configparser.ConfigParser()
        if ostype == 'win32':
            config.read(tagfile, encoding='gbk')
        else:
            config.read(tagfile, encoding='utf-8')
        for i in config.sections():
            label = {}
            print("[ INFO ] Label:", i)
            label["Label"] = i
            tags = []
            for j in config.items(i):
                tagitem = {}
                tagitem["Key"] = j[0]
                tagitem["Value"] = j[1]
                print("[ INFO ] tag: ", j[0]+" = "+j[1])
                tags.append(tagitem)
            label["Tags"] = tags
            labels.append(label)
    # print labels
    print("[ INFO ] Json Dump data is :", json.dumps(labels))
    return json.dumps(labels)


def post_status(cmdb_domain, pingcmd, module):
    '''
    # post data
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
    hostip = get_host_ip()
    statusapi = 'http://' + cmdb_domain + '/ft/status.php'
    print("[ INFO ] The Status API URL is: ", statusapi)
    pingres = subprocess.Popen(pingcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if pingres.wait() == 0:
        print("[ INFO ] Ping Server {0} From Agent {1} is successful !!! ".format(cmdb_domain.split(':')[0], hostip))
        vatsping = 1
    else:
        vatsping = 0
        print("[ ERR ] Can Not Ping Server {0} From Agent {1} !!! ".format(cmdb_domain.split(':')[0], hostip))
        return False

    if vatsping:
        try:
            req = requests.get(url=statusapi, headers={"User-Agent": "python-Fusioninventory"}, timeout=5)
            ctx = req.json()
            statuscode = req.status_code
        except Exception as e:
            print("[ ERR ] {0}, POST status to {1} Failed, Please check server address !!!".format(e, statusapi))
            return False
        # finally:
        #     req.close()
        '''
        response data : {"action": "remoteaddress", "value": "192.168.146.1"}
        '''
        if statuscode == 200:
            print("[ INFO ] connect status api {0} is successfull ! ".format(statusapi))
            vats10080 = 1
            if ctx["action"] == 'remoteaddress':
                remoetip = ctx["value"]
                hostip = get_host_ip()
            if remoetip == hostip:
                nettype = "direct"
            else:
                nettype = "nat"

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

            postreq = requests.post(url=statusapi, data=json.dumps(data),
                                    headers={"User-Agent": "python-Fusioninventory"}, timeout=5)
            if postreq.status_code == 200:
                print("[ INFO ] status data post successfull! ")
                return True
            else:
                print("[ ERR ] the URL: {0} is cannot connect !!! ".format(statusapi))
                return False

        else:
            vats10080 = 0
            print("[ ERR ] connot connect status api {0} , Please Check it !!! ".format(statusapi))
            return False

def doinventory(cmd):
    print("[ INFO ] run in shell cmd: ", cmd)
    res = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if res.wait() == 0:
        print(res.stdout.readlines())
        return True
    else:
        return False
        # print("[ INFO ] This is command stdout -------------[start]-------------------")
        # for stdinfo in res.stdout.readlines():
        #     print(stdinfo)
        # print("[ INFO ] This is command stdout --------------[END]--------------------")


ostype = sys.platform
print("[ INFO ] OSType is: ", ostype)
unix = ['linux', 'linux2', 'hpux', 'aix']

if ostype in unix:
    path = ['/root', '/home']
    fusionagent_path = '/opt/FusionInventory-Agent/'
    fusionagentcfg = fusionagent_path + 'etc/fusioninventory/agent.cfg'
    fusionagent_start_shell = fusionagent_path + 'start.sh'
    # get cmdb server url
    try:
        with open(fusionagentcfg, 'r') as cfg:
            for line in cfg.readlines():
                if line.strip().startswith('server'):
                    # cmdbserver = parse.urlparse(line.split('=')[1].strip().split('\n')[0]).netloc
                    # serverip = cmdbserver.split(':')[0]
                    cmdb_domain, cmdb_ip, cmdb_port = urlparserhostip(line.split('=')[1])
                    print("[ INFO ] CMDBserver IP: ", cmdb_domain)

        sedCmd = "sed -i 's#-d##g' {0}".format(fusionagent_start_shell)
        subprocess.Popen(sedCmd, shell=True)
    except Exception as e:
        print("[ ERR ] {0}, please check agent.cfg file !!!".format(e))
        sys.exit(8001)

    pingcmd = 'ping -c 3 ' + cmdb_ip
    result = post_status(cmdb_domain, pingcmd, module)
    if result:
        perlenv = fusionagent_path + '.perl_env'
        fusioncmd = fusionagent_path + '.fusion_cmd'

        tag_info = gettags(path, ostype)

        with open(fusionagent_start_shell, 'r') as f:
            for line in f.readlines():
                line = line.strip().split('\n')[0]
                if line.startswith('export PERL'):
                    perlenv = line
                elif line.startswith('perl /opt/FusionInventory-Agent'):
                    if line.endswith("-d"):
                        fusion_cmd = line.split('-d', ' -t')
                    else:
                        fusion_cmd = line + ' -t'

        print("[ INFO ] set perl env command is :", perlenv)
        print("[ INFO ] Fusion agent run command is :", fusion_cmd)
        cmd = perlenv + ';' + fusion_cmd + ' ' + "'" + str(tag_info) + "'"
        result = doinventory(cmd)
        if result:
            print("[ INFO ] FusionInventory run success ! ")
        else:
            print("[ ERR ] FusionInventory run Failed !!! ")

else:
    path = ['c:\\tags', 'd:\\tags']
    import winreg
    try:
        reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        reg_keys = winreg.OpenKey(reg_conn, r"SOFTWARE\FusionInventory-Agent")
        cmdb_url, t = winreg.QueryValueEx(reg_keys, "server")
        winreg.CloseKey(reg_keys)
        cmdb_domain, cmdb_ip, cmdb_port = urlparserhostip(cmdb_url)
        print("[ INFO ] CMDBserver IP: {0} ".format(cmdb_ip))
    except Exception as e:
        print("[ ERR ] {0}, please check Fusioninventory installed !!!".format(e))
        sys.exit(8002)

    finally:
        pass
    pingcmd = 'ping -n 3 {0}'.format(cmdb_ip)
    result = post_status(cmdb_domain, pingcmd, module)
    if result:
        tag_info = gettags(path, ostype)
        print("[ INFO ] tag is: {0}".format(tag_info))
        '''
        # modeify the win registry value ,the key name is 'HKEY_LOCAL_MACHINE\SOFTWARE\FusionInventory-Agent\\tag'
        '''
        reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        reg_keys = winreg.OpenKey(reg_conn, r"SOFTWARE\FusionInventory-Agent", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_keys, "tag", 0, winreg.REG_SZ, tag_info)
        winreg.CloseKey(reg_keys)

        cmd = "'c:\\Program Files\\FusionInventory-Agent\\fusioninventory-agent.bat' "
        result = doinventory(cmd)
        if result:
            print("[ INFO ] FusionInventory run success! ")
        else:
            print("[ ERR ] FusionInventory run Failed !!! ")