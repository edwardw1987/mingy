# -*- coding: utf-8 -*-
# @Author: vivi
# @Date:   2016-12-23 22:07:12
# @Last Modified by:   vivi
# @Last Modified time: 2016-12-30 21:17:29
import requests
import random
import hashlib
import urllib
from pyquery import PyQuery as Q
import argparse

def handle_args():
    parser = argparse.ArgumentParser(description="MingYun CLI")
    parser.add_argument('-n', '--num', dest="page_num", type=int, default=1, help="page number")
    parser.add_argument('-s', '--size', dest="page_size", type=int, default=20, help="page size")
    args = parser.parse_args()
    return args
class MinYuanClient(requests.Session):
    addr = '192.168.0.103'
    loginurl = '/Default_Login.aspx?'
    default_usr = "wubin1"
    default_pwd = "aaa111"
    def __init__(self, username=None, password=None):
        super(MinYuanClient, self).__init__()
        if username is None and password is None:
            username = self.default_usr
            password = self.default_pwd
        self.login(username, password)

    def fetch(self, url, *args, **kwargs):
        url = 'http://%s%s' % (self.addr, url)
        return self.get(url, *args, **kwargs)

    def login(self, username, password):
        resp = self.fetch(self.loginurl, params={
            "usercode":username, 
            "password": hashlib.md5(password).hexdigest(),
            "rdnum": random.random()
            })
        # print resp.content

    def getReceiveList(self, page_size=20, page_num=1):
        path = "/_grid/griddata.aspx?gridId=appGrid&sortCol=ReceiveDate&sortDir=descend&vscrollmode=0&multiSelect=1&selectByCheckBox=0&processNullFilter=1&customFilter=&customFilter2=&dependencySQLFilter=&location=&showPageCount=1&appName=Default&application=&cp="
        params = {
            "xml": "/Kfxt/RWGL/Jdjl_Grid.xml",  # <= 所有记录, Jdjl_Grid_My.xml 我的记录
            "pageSize": page_size,
            "pageNum": page_num,
            "filter": """<filter type="and"><filter type="and"><filter type="or"><condition operator="api" attribute="TsProjGUID" value="4975b69c-9953-4dd0-a65e-9a36db8c66df" datatype="buprojectfilter" application="0102"/><condition operator="null" attribute="TsProjGUID" application="0102"/></filter></filter><filter type="and"/></filter>""",
        }
        resp = self.fetch(path, params=params)
        q = Q(resp.content)
        tr_arr = q('#gridBodyTable tr')
        ret = []
        for tr in tr_arr:
            trq = Q(tr)
            r = []
            for td in trq.children('td')[3:]:
                r.append(Q(td).text())
            ret.append(tuple(r))
        return ret
def main():
    """
    视图(xml)：
        所有记录 Jdjl_Grid.xml
        我的记录 Jdjl_Grid_My.xml
        待明确记录 /Kfxt/RWGL/Jdjl_Grid_ReBuild.xml
        报修 /Kfxt/RWGL/Jdjl_Grid_Repairs.xml
        投诉 /Kfxt/RWGL/Jdjl_Grid_Complain.xml
        咨询 /Kfxt/RWGL/Jdjl_Grid_Counsel.xml
        建议 /Kfxt/RWGL/Jdjl_Grid_Suggest.xml
    """
    my = MinYuanClient("wubin1", "aaa111")
    for i in my.getReceiveList():
        print ' '.join(i).encode('utf-8')
if __name__ == '__main__':
    main()
