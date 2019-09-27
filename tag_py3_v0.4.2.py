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
# from gevent import monkey; monkey.patch_all()
import gevent
import gevent.monkey
gevent.monkey.patch_all()
import configparser
import os
import sys
from pathlib2 import Path
import json
import subprocess
from urllib import parse
import requests
import socket
import gevent
from IPy import IP
import locale

###find all tag file in /root and /home on linux; in c:\tags and d:\tags on windows
###the tag file is *.tag

# get host ip
def get_host_ip():
    try:
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.connect(('10.0.0.1', 8008))

    finally:
        ip = sc.getsockname()[0]
        sc.close()
        print("[ INFO ] Local IP: ", ip)
    return ip

# get remote ip via /ft/status.php use HTTP mothod GET

def get_remote_ip(url):
    try:
        req = requests.get(url=url, headers={"User-Agent": "python-Fusioninventory"}, timeout=5)
        ctx = req.json()
        # print("[ DEBUG ] ctx is {0}".format(ctx))
        statuscode = req.status_code
        if statuscode == 200 and ctx["action"] == 'remoteaddress':
            return ctx["value"]
    except Exception as e:
        print("[ ERR ] {0}, GET status From {1} Failed, Please check server address !!!".format(e, statusapi))
        return False

if len(sys.argv) > 1:
    if sys.argv[1] == 'manual':
        module = 'manual'
    elif sys.argv[1] == 'status':
        module = 'status'
    elif sys.argv[1] == 'netscan':
        module = 'netscan'
        if len(sys.argv) == 3:
            scanip = sys.argv[2]
        else:
            scanip = get_host_ip()
        print("[ INFO ] Scan IP Net: {0}".format(IP(scanip).make_net('255.255.255.0').strNormal(1)))
else:
    module = 'auto'
print('[ INFO ] Module is: {0}'.format(module))

# parser domain like '192.168.1.1:10080', after parsered ip=192.168.1.1, port=10080
def urlparserhostip(url):
    domain = parse.urlparse(url.strip().split('\n')[0]).netloc
    if ':' in domain:
        ip = domain.split(':')[0]
        port = domain.split(':')[1]
    else:
        ip = domain
        port = 80
    return domain, ip, port

# get tags on windows  or  linux
def gettags(paths):
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
        defaultencoding = locale.getpreferredencoding(False)
        try:
            config.read(tagfile, encoding=defaultencoding)
            # print('gbk read')
        except:
            config.read(tagfile, encoding='utf-8')
            # print('utf8 read')
        # if ostype == 'win32':
        #     config.read(tagfile, encoding='utf-8')
        # else:
        #     config.read(tagfile, encoding='utf-8')
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

'''
post status data
'''

def post_status(cmdb_domain, pingcmd, module):
    '''
    # post data
        {
            'remoetip': ip,
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
    pingstatus, pingresult = subprocess.getstatusoutput(pingcmd)
    if pingstatus == 0:
        print("[ INFO ] Ping Server {0} From Agent {1} is successful !!! ".format(cmdb_domain.split(':')[0], hostip))
        vatsping = 1
    else:
        vatsping = 0
        print("[ !ERR ] Can Not Ping Server {0} From Agent {1} !!! ".format(cmdb_domain.split(':')[0], hostip))
        return False

    if vatsping:
        # try:
        #     req = requests.get(url=statusapi, headers={"User-Agent": "python-Fusioninventory"}, timeout=5)
        #     ctx = req.json()
        #     print("[ DEBUG ] ctx is {0}".format(ctx))
        #     statuscode = req.status_code
        # except Exception as e:
        #     print("[ ERR ] {0}, GET status From {1} Failed, Please check server address !!!".format(e, statusapi))
        #     return False
        # # finally:
        # #     req.close()
        '''
        response data : {"action": "remoteaddress", "value": "192.168.146.1"}
        '''
        remoetip = get_remote_ip(statusapi)
        if remoetip:
            vats10080 = 1
            hostip = get_host_ip()
            if remoetip == hostip:
                nettype = "direct"
            else:
                nettype = "nat"

            data = {}
            data["remoetip"] = remoetip
            data["localip"] = hostip
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

            # postreq = requests.post(url=statusapi, data=json.dumps(data),
            #                         headers={"User-Agent": "python-Fusioninventory"}, timeout=5)
            postreq = do_post(url=statusapi, data=data)
            if postreq:
                print("[ INFO ] POST status data successfull! ")
                return True

        else:
            vats10080 = 0
            print("[ ERR ] connot connect status api {0} , Please Check it !!! ".format(statusapi))
            return False

def doinventory(cmd):
    print("[ INFO ] run in shell cmd: ", cmd)
    cmdstatus, cmdresult = subprocess.getstatusoutput(cmd)
    if cmdstatus == 0 and '':
        print("[ INFO ] run inventory seccuss, {0}".format(cmdresult))
        return True, cmdresult
    else:
        print("[ ERR ] run inventory failed, {0}".format(cmdresult))
        return False, cmdresult

        # print("[ INFO ] This is command stdout -------------[start]-------------------")
        # for stdinfo in res.stdout.readlines():
        #     print(stdinfo)
        # print("[ INFO ] This is command stdout --------------[END]--------------------")

'''ping_scan'''
def pingscan(ip):
    if ostype == 'win32':
        pingcmd = 'ping -n 2 -w 2 {0}'.format(ip)
    else:
        pingcmd = 'ping -c 2 -w 2 {0}'.format(ip)
    try:
        pingstatus, pingresult = subprocess.getstatusoutput(pingcmd)
        if pingstatus == 0:
            print('[ INFO ] Host {0} is UP .'.format(ip))
            return ip
        else:
            # print('[ ERR ] {0} is Down .'.format(ip))
            return False
    except Exception as e:
        return False

def netscan(netip):
    print("*" * 10 + "NetScan Start" + "*" * 10)
    net = IP(netip).make_net('255.255.255.0')
    g_l = [gevent.spawn(pingscan, ip) for ip in net]
    gevent.joinall(g_l)
    uplist = []
    for i, g in enumerate(g_l):
        if g.value:
            # print('i: {0}'.format(i))
            # print('g: {0}'.format(g.value))
            # print(type(g.value))
            uplist.append(g.value.strNormal(0))
    data = {}
    data["action"] = "netscan"
    data["lenth"] = len(uplist)
    data["result"] = uplist
    data["scanip"] = get_host_ip()
    print("[ INFO ] UP host data: {0}".format(data))
    print("*" * 10 + "NetScan Finish" + "*" * 10)
    return data

'''do post or get '''
def do_post(url, data, headers={"User-Agent": "python-Fusioninventory"}, timeout=5):
    try:
        pst = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=timeout)
        pstatus = pst.status_code
    except Exception as e:
        print("[ ERR ] {0}, connect to {1} Failed, please check it !!!".format(e, url))
        return False
    if pstatus == 200:
        return True
    else:
        return False

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

    pingcmd = 'ping -c 2  ' + cmdb_ip
    statusapi = 'http://' + cmdb_domain + '/ft/status.php'
    result = post_status(cmdb_domain, pingcmd, module)
    if result:
        if module == 'status':
            print("*" * 10 + "status data upload success!" + "*" * 10)
            pass
        elif module == 'netscan':
            scandata = netscan(scanip)
            pstdata = do_post(url=statusapi, data=scandata)
            if pstdata:
                print('[ INFO ] post net scan data success !')
            else:
                print("[ ERR ] post net scan data Failed !!! ")

        elif module in ['manual', 'auto']:

            tag_info = gettags(path)

            # modify value of tag key in agent.cfg
            sedCmd = "sed -i 's#^tag=.*#tag={0}#g' {1}".format(tag_info, fusionagentcfg)
            subprocess.Popen(sedCmd, shell=True)

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

            # print("[ INFO ] set perl env command is :", perlenv)
            # print("[ INFO ] Fusion agent run command is :", fusion_cmd)
            cmd = perlenv + ';' + fusion_cmd + ' ' + "'" + str(tag_info) + "'"
            result, resultinfo = doinventory(cmd)
            if result:
                inventory = 1
                print("[ INFO ] FusionInventory run success! ")
            else:
                inventory = 0
                print("[ ERR ] {0}, FusionInventory run Failed !!! ".format(resultinfo))
            data = {}
            data["action"] = 'runinventory'
            data["result"] = inventory
            data["localip"] = get_host_ip()
            data["remoetip"] = get_remote_ip(statusapi)
            data["resultinfo"] = resultinfo
            pstd = do_post(url=statusapi, data=data)
            if pstd:
                print('[ INFO ] post inventory data success !')
            else:
                print("[ ERR ] post inventory data Failed !!! ")

else:
    path = ['c:\\tags', 'd:\\tags']
    import winreg
    try:
        reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        reg_keys = winreg.OpenKey(reg_conn, r"SOFTWARE\FusionInventory-Agent")
        cmdb_url, t = winreg.QueryValueEx(reg_keys, "server")
        cmdb_domain, cmdb_ip, cmdb_port = urlparserhostip(cmdb_url)
        print("[ INFO ] CMDBserver IP: {0} ".format(cmdb_ip))

    except Exception as e:
        print("[ ERR ] {0}, please check Fusioninventory installed !!!".format(e))

        sys.exit(8002)

    finally:
        winreg.CloseKey(reg_keys)
    pingcmd = 'ping -n 3 -w 5 {0}'.format(cmdb_ip)
    statusapi = 'http://' + cmdb_domain + '/ft/status.php'
    result = post_status(cmdb_domain, pingcmd, module)
    if result and module in ['manual', 'auto']:
        tag_info = gettags(path)
        print("[ INFO ] tag is: {0}".format(tag_info))
        '''
        # modeify the win registry value ,the key name is 'HKEY_LOCAL_MACHINE\SOFTWARE\FusionInventory-Agent\\tag'
        '''
        try:
            reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            reg_keys = winreg.OpenKey(reg_conn, r"SOFTWARE\FusionInventory-Agent", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_keys, "tag", 0, winreg.REG_SZ, tag_info)
            winreg.CloseKey(reg_keys)
        except Exception as e:
            print("[ ERR ] {0}, Modify Regedit tag value Failed !!! ".format(e))

        cmd = '"c:\\Program Files\\FusionInventory-Agent\\fusioninventory-agent.bat" '
        result, resultinfo = doinventory(cmd)
        remoteip = get_remote_ip(statusapi)
        if result:
            inventory = 1
            print("[ INFO ] FusionInventory run success! ")
        else:
            inventory = 0
            print("[ ERR ] {0}, FusionInventory run Failed !!! ".format(resultinfo))
        data = {}
        data["action"] = 'runinventory'
        data["result"] = inventory
        data["localip"] = get_host_ip()
        data["remoteip"] = remoteip
        data["resultinfo"] = resultinfo
        pstd = do_post(url=statusapi, data=data)
        if pstd:
            print('[ INFO ] post inventory data success !')
        else:
            print("[ ERR ] post inventory data Failed !!! ")
    elif result and module == 'netscan':
        scandata = netscan(scanip)
        pstdata = do_post(url=statusapi, data=scandata)
        if pstdata:
            print('[ INFO ] post net scan data success !')
        else:
            print("[ ERR ] post net scan data Failed !!! ")
    elif result and module == 'status':
        print('*' * 10 + "status data upload success!" + '*' * 10)
        pass