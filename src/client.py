# -*- coding: utf-8 -*-
# @Author: vivi
# @Date:   2016-12-23 22:07:12
# @Last Modified by:   edward
# @Last Modified time: 2017-01-21 23:51:26
import requests
import random
import hashlib
import urllib
import argparse
from requests.exceptions import ConnectTimeout
from bs4 import BeautifulSoup

MINGYUAN_OFFICIAL_ADDR = '192.168.0.103'
MINGYUAN_TEST_ADDR = '192.168.0.123'
# ---------- URI ----------
URI_LOGIN = '/Default_Login.aspx'
URI_GRID_DATA = '/_grid/griddata.aspx'
URI_USER_TREE = '/Kfxt/RWGL/Rwcl_Edit_Rwcl_Assign_UserTree.aspx'
URI_RWCL_EDIT = '/Kfxt/RWGL/Rwcl_Edit.aspx'

def handle_args():
    parser = argparse.ArgumentParser(description="MingYun CLI")
    parser.add_argument('-n', '--num', dest="page_num",
                        type=int, default=1, help="page number")
    parser.add_argument('-s', '--size', dest="page_size",
                        type=int, default=20, help="page size")
    args = parser.parse_args()
    return args


class MinYuanClient(requests.Session):
    default_usr = "wubin1"
    default_pwd = "aaa111"

    def __init__(self, username=None, password=None, addr=MINGYUAN_OFFICIAL_ADDR):
        super(MinYuanClient, self).__init__()
        if username is None and password is None:
            username = self.default_usr
            password = self.default_pwd
        self.addr = addr
        self.login(username, password)

    def postUrl(self, url, *args, **kwargs):
        kwargs["timeout"] = kwargs.get("timeout", 6)
        url = 'http://%s%s' % (self.addr, url)
        ret = {}
        try:
            ret["response"] = self.post(url, *args, **kwargs)
        except ConnectTimeout:
            ret["errMsg"] = ConnectTimeout.__name__
        except Exception as e:
            ret["errMsg"] = e
        return ret

    def fetch(self, url, *args, **kwargs):
        kwargs["timeout"] = kwargs.get("timeout", 6)
        url = 'http://%s%s' % (self.addr, url)
        ret = {}
        try:
            ret["response"] = self.get(url, *args, **kwargs)
        except ConnectTimeout:
            ret["errMsg"] = ConnectTimeout.__name__
        except Exception as e:
            ret["errMsg"] = e
        return ret

    def login(self, username, password):
        resp = self.fetch(URI_LOGIN, params={
            "usercode": username,
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
        params = dict(
            xml="/Kfxt/RWGL/Jdjl_Grid.xml",  # <= 所有记录, Jdjl_Grid_My.xml 我的记录
            pageSize=page_size,
            pageNum=page_num,
            gridId="appGrid",
            sortCol="ReceiveDate",
            sortDir="descend",
            vscrollmode="0",
            multiSelect="1",
            selectByCheckBox="0",
            processNullFilter="1",
            customFilter="",
            customFilter2="",
            dependencySQLFilter="",
            location="",
            showPageCount="1",
            appName="Default",
            application="",
            cp="",
            filter="""<filter type="and"><filter type="and"><filter type="or"><condition operator="api" attribute="TsProjGUID" value="4975b69c-9953-4dd0-a65e-9a36db8c66df" datatype="buprojectfilter" application="0102"/><condition operator="null" attribute="TsProjGUID" application="0102"/></filter></filter><filter type="and"/></filter>""",

        )
        resp_data = self.fetch(URI_GRID_DATA, params=params)
        if "response" in resp_data:
            resp = resp_data.pop("response")
            # q = Q(resp.content)
            soup = BeautifulSoup(resp.text, 'lxml')
            table = soup.find(attrs={"id": "gridBodyTable"})
            if not table:
                return resp_data
            receive_list = []
            for tr in table.find_all(name="tr"):
                r = [td.getText() for td in tr.find_all(name="td")[3:]]
                receive_list.append(tuple(r))
            resp_data["receiveList"] = receive_list
        return resp_data

    def getUsers(self):
        resp_data = self.fetch(URI_USER_TREE)
        if "response" in resp_data:
            resp = resp_data.pop("response")
            stuff = resp.text
            startPos = stuff.find('<table class="layout"')
            if startPos == -1:
                return resp_data
            soup = BeautifulSoup(stuff[startPos:], 'xml')
            users = []
            uuidset = set()
            for tr in soup.select("tr[allowselect='1']"):
                username = tr.attrs["text"]
                uuid = tr.attrs["value"]
                if len(username) > 0 and uuid not in uuidset:
                    u = dict(
                        uuid=uuid,
                        text=username,
                        email=tr.attrs["email"],
                        mobile=tr.attrs["mobile"]
                    )
                    uuidset.add(uuid)
                    users.append(u)
                    print ';'.join(u[k] for k in ["text", "uuid", "mobile", "email"] if u[k]).encode("utf-8")
            resp_data["users"] = users
            print len(users)
        return resp_data

    def getProblemList(self):
        params = dict(
            xml="/Kfxt/ZSJF/JFWTCL_GRID_WCL_JfRoom.xml",
            gridId="appGrid",
            sortCol="TsFcInfo",
            sortDir="ascend",
            vscrollmode="0",
            multiSelect="1",
            selectByCheckBox="0",
            filter='''<filter type="and"><filter type="and"><condition operator="in" attribute="ProjGUID" value="7bbc819c-a561-e411-9927-e41f13c5183a"/></filter>
            <filter type="and"/></filter>''',
            processNullFilter="1",
            customFilter="",
            customFilter2="",
            dependencySQLFilter="",
            location="",
            pageNum="1",
            pageSize="20",
            showPageCount="1",
            appName="Default",
            application="",
            cp="",
        )
        resp_data = self.fetch(URI_GRID_DATA, params=params)
        if "response" in resp_data:
            resp = resp_data.pop("response")
            # q = Q(resp.content)
            soup = BeautifulSoup(resp.text, 'lxml')
            table = soup.find(attrs={"id": "gridBodyTable"})
            if not table:
                return resp_data
            rows = []
            for tr in table.find_all(attrs={"otype": "1"}):
                ProblemGUID =  tr.attrs["ProblemGUID".lower()]
                r = [td.getText() for td in tr.find_all(name="td")]
                rows.append({ProblemGUID:tuple(r)})
            resp_data["rows"] = rows
        return resp_data

    def _preTransferTask(self, problemGUID, workerGUID=None):
        if workerGUID is None:
            workerGUID = 'b23e6df4-e2f7-e411-891a-e41f13c5183a' # 曹伟忠
        # ----------交付任务处理----------
        params = dict(
            mode=1,
            tasksource=2,
            taskguid='',
            receiveguid='',
            WorkerGUIDStr=workerGUID,
            funcid='01020502',
        )
        # -------------------------
        # BODY
        data = dict(
            ProblemGUIDStr=problemGUID
        )
        # ----------任务编号----------
        resp_data = self.fetch(URI_RWCL_EDIT, params=params, data=data)
        if "response" in resp_data:
            resp = resp_data.pop("response")
            # q = Q(resp.content)
            soup = BeautifulSoup(resp.text, 'lxml')
            # ---------- Prepare Params for Transfering Task ----------
            for key in {
                "__VIEWSTATE", "txtTaskCode", "txtClStatus", "txtForeAction",
                "txtForePara", "txtDoneMode", "txtTaskGUID", "txtSlrGUID",
                "txtProjGUID", "txtFcInfo", "txtJfRoom", "txtBldGUID",
                "txtUnit", "txtRoom", "txtRoomGUID", "txtTsProjGUID",
                "txtTsFcInfo", "txtTsBldGUID", "txtTsUnit", "txtTsRoom",
                "txtTsRoomGUID", "txtCstGUID", "txtRequestMan", "txtBUGUID",
                "txtTaskSource", "Relation2Receive", "Relation2CstName", "Relation2Room",
                "txtReceiveGUID", "txtReceiveGUIDstr", "txtReceiveDate", "txtProblemGUIDstr",
                "txtIDOfShowSht", "txtIDOfEnabledSht", "txtTimeLimitXML", "IsReport",
                "txtZrrGUID", "txtUserGUID", "hidNewSlr", "txtWorkerGUIDstr",
                "txtZrrHfSx", "txtDfkhSx", "txtRwclSx", "txtJfRoomDisplay",
                "txtProbleState", "txtReceptType", "ddlTaskType", "ddlTaskLevel",
                "txtSlDate", "txtSlr", "txtZrr", "txtTopic", "txtContent", "txtZzJjfa",
            }:
                e = soup.find(attrs={"name": key})
                if e:
                    resp_data[key] = e.attrs.get("value", "")
            iframe = soup.find(attrs=dict(id='_AppUpFile_frmFile'))
            if iframe:
                resp_data["_AppUpFile_frmFile"] = iframe.attrs["src"]
            resp_data.update(dict(
                __btnUpFile="上 传",
                __EVENTTARGET="__Submit",
                __EVENTARGUMENT="2",
            ))
        return resp_data

    def transferTask(self, problemGUID, workerGUID=None):
        data = self._preTransferTask(problemGUID, workerGUID)
        params = dict(
            mode="1",
            tasksource="2",
            taskguid="",
            receiveguid="",
            WorkerGUIDStr="b23e6df4-e2f7-e411-891a-e41f13c5183a",
            funcid="01020502",
        )
        resp_data = self.postUrl(URI_RWCL_EDIT, params=params, data=data)
        self.fetch(data["_AppUpFile_frmFile"])
        print resp_data["response"]

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
    mingy = MinYuanClient("shenkai", "aaa111", addr=MINGYUAN_TEST_ADDR)
    # print urllib.unquote_plus(s)
    problems =  mingy.getProblemList()
    print len(problems["rows"])
    pbs = problems.get("rows")
    if pbs:
        pid = pbs[0].keys()[0]
        print mingy.transferTask(pid)
    # resp_data = mingy.fetch('/Kfxt/PUB/Verify_Public.aspx?p_Func=%u4EFB%u52A1%u7BA1%u7406&p_Mode=%u95EE%u9898%u89E3%u9501&rdnum=0.17257182981973673')
    # print resp_data["response"].text.encode('utf-8')
    # print mingy.getReceiveList()
    # mingy.getUsers()
    # for i in my.getReceiveList()["receiveList"]:
    #     print ' '.join(i).encode('utf-8')
if __name__ == '__main__':
    main()
