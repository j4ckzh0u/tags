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

# [工程项目信息]
# 工程项目名称=PAAS一期
# 工程项目编号=XM-PAAS-001
# 资产标签=ZC-PAAS-WL-xxxx
# 工程负责人=张三
# 联系电话=130xxxxxxx
# 邮箱=aaaa@cccc.com


# [设备基础信息]
# 设备品牌=IBM
# 设备型号=X3850M3
# 设备序列号=SNxxxxxxxxxx123
# 数据中心=北环数据中心
# 机房=5楼01
# 机柜=A01
# 柜内开始位置=30U
# 柜内结束位置=40U

import ConfigParser
import os
from pathlib2 import Path

###find all tag file
###the tag file is *.tag

path=['/root','/home']
paths=[]
for fpath in path:
    p = Path(fpath)
    for filepath in list(p.glob('**/*.tag')):
        if os.path.isfile(str(filepath)):
            paths.append(filepath)

labels=[]

for tagfile in paths:
    config=ConfigParser.ConfigParser()
    config.read(tagfile)
    for i in config.sections():
        label={}
        print i
        label["Label"]=i
        tags=[]
        for j in config.items(i):
            item={}
            item["Key"]=j[0]
            item["Value"]=j[1]
            print j[0]+"="+j[1]
            tags.append(item)
        label["Tags"]=tags
        labels.append(label)
print labels