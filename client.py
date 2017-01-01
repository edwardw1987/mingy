# -*- coding: utf-8 -*-
# @Author: vivi
# @Date:   2016-12-23 22:07:12
# @Last Modified by:   edward
# @Last Modified time: 2017-01-01 20:40:37
import requests
import random
import hashlib
from requests.exceptions import ConnectTimeout
from BeautifulSoup import BeautifulSoup

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
        kwargs["timeout"] = kwargs.get("timeout", 3)
        url = 'http://%s%s' % (self.addr, url)
        ret = {}
        try:
            ret["response"] = self.get(url, *args, **kwargs)
        except ConnectTimeout:
            ret["errMsg"] = ConnectTimeout.__name__
        return ret


    def login(self, username, password):
        resp = self.fetch(self.loginurl, params={
            "usercode":username, 
            "password": hashlib.md5(password).hexdigest(),
            "rdnum": random.random()
            })
        # print resp.content

    def getReceiveList(self, page_size=20, page_num=1):
        """

        :param page_size:
        :param page_num:
        :return: {"receiveList": [], "errMsg": xx}
        """
        path = "/_grid/griddata.aspx?gridId=appGrid&sortCol=ReceiveDate&sortDir=descend&vscrollmode=0&multiSelect=1&selectByCheckBox=0&processNullFilter=1&customFilter=&customFilter2=&dependencySQLFilter=&location=&showPageCount=1&appName=Default&application=&cp="
        params = {
            "xml": "/Kfxt/RWGL/Jdjl_Grid.xml",  # <= 所有记录, Jdjl_Grid_My.xml 我的记录
            "pageSize": page_size,
            "pageNum": page_num,
            "filter": """<filter type="and"><filter type="and"><filter type="or"><condition operator="api" attribute="TsProjGUID" value="4975b69c-9953-4dd0-a65e-9a36db8c66df" datatype="buprojectfilter" application="0102"/><condition operator="null" attribute="TsProjGUID" application="0102"/></filter></filter><filter type="and"/></filter>""",
        }
        resp_data = self.fetch(path, params=params)
        if "response" in resp_data:
            resp = resp_data.pop("response")
            # q = Q(resp.content)
            soup = BeautifulSoup(resp.content)
            table = soup.find(attrs={"id":"gridBodyTable"})
            receive_list = []
            for tr in table.findAll(name="tr"):
                r = [ td.getText() for td in tr.findAll(name="td")[3:]]
                receive_list.append(tuple(r))
            resp_data["receiveList"] = receive_list
            return resp_data
            tr_arr = q('#gridBodyTable tr')
            receive_list = []
            for tr in tr_arr:
                trq = Q(tr)
                r = []
                for td in trq.children('td')[3:]:
                    r.append(Q(td).text())
                receive_list.append(tuple(r))
        return resp_data
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
    print my.getReceiveList()
    # for i in my.getReceiveList()["receiveList"]:
    #     print ' '.join(i).encode('utf-8')
if __name__ == '__main__':
    main()
