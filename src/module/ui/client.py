# -*- coding: utf-8 -*-
# @Author: vivi
# @Date:   2016-12-23 22:07:12
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-02-16 16:13:22
import argparse
import hashlib
import random

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout

from templates import render_template

# ---------- PROJECT ID ----------
PROJECT_IDS = {
    'default': '7bbc819c-a561-e411-9927-e41f13c5183a',  # 艾卢
}
# ---------- WORKER ID ----------
WORKER_IDS = {
    'default': 'b23e6df4-e2f7-e411-891a-e41f13c5183a',  # 曹伟忠
}
# ---------- ADDR ----------
MINGYUAN_OFFICIAL_ADDR = '192.168.0.103'
MINGYUAN_TEST_ADDR = '192.168.0.123'
# ---------- URI ----------
URI_LOGIN = '/Default_Login.aspx'
URI_GRID_DATA = '/_grid/griddata.aspx'
URI_USER_TREE = '/Kfxt/RWGL/Rwcl_Edit_Rwcl_Assign_UserTree.aspx'
URI_RWCL_EDIT = '/Kfxt/RWGL/Rwcl_Edit.aspx'
URI_RWCL_WORK = '/Kfxt/Rwgl/Rwcl_Edit_Rwcl_WorkForm.aspx'


def handle_args():
    parser = argparse.ArgumentParser(description="MingYun CLI")
    parser.add_argument('-n', '--num', dest="page_num",
                        type=int, default=1, help="page number")
    parser.add_argument('-s', '--size', dest="page_size",
                        type=int, default=20, help="page size")
    parser.add_argument('-t', '--taskcode', dest="taskcode",
                        help="get taskguid by taskcode"
                        )
    parser.add_argument('-p', '--project', dest="project",
                        default='7bbc819c-a561-e411-9927-e41f13c5183a', help="project id")
    args = parser.parse_args()
    return args


def init_filter(project_id, task_code=None):
    return render_template("filter.xml", **locals())


def get_soup(html):
    return BeautifulSoup(html, 'html.parser')


class MinYuanClient(requests.Session):
    test_usr = "shenkai"
    test_pwd = "aaa111"
    official_usr = "shenkai"
    official_pwd = "aaa222"

    def __init__(self, username=None, password=None, addr=MINGYUAN_OFFICIAL_ADDR):
        super(MinYuanClient, self).__init__()
        if username is None and password is None:
            if addr == MINGYUAN_TEST_ADDR:
                username = self.test_usr
                password = self.test_pwd
            else:
                username = self.official_usr
                password = self.official_pwd
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

    def validate_response(self, response):
        return 'response' in response

    def login(self, username, password):
        resp = self.fetch(URI_LOGIN, params={
            "usercode": username,
            "password": hashlib.md5(password).hexdigest(),
            "rdnum": random.random()
        })
        if self.validate_response(resp):
            soup = get_soup(resp["response"].content)
            fr = soup.find(attrs={"result": "true"})
            if not fr:
                raise Exception("login failed")
            return
        return resp

    def getJdjl(self, page_num=1, page_size=20):
        """
        :param page_size:
        :param page_num:
        :return: {"Jdjl": [], "errMsg": xx}
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
        if self.validate_response(resp_data):
            resp = resp_data.pop("response")
            # q = Q(resp.content)
            soup = get_soup(resp.text)
            table = soup.find(attrs={"id": "gridBodyTable"})
            if not table:
                return resp_data
            rows = []
            for tr in table.find_all(name="tr"):
                r = [td.getText() for td in tr.find_all(name="td")[3:]]
                rows.append(tuple(r))
            resp_data["rows"] = rows
        return resp_data

    def getUsers(self):
        resp_data = self.fetch(URI_USER_TREE)
        if self.validate_response(resp_data):
            resp = resp_data.pop("response")
            stuff = resp.text
            startPos = stuff.find('<table class="layout"')
            if startPos == -1:
                return resp_data
            soup = get_soup(stuff[startPos:])
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

    def getProblemList(self, project_id=PROJECT_IDS["default"], page_num=1, page_size=20):
        '''
        获取`交付问题列表`
        xml="/Kfxt/ZSJF/JFWTCL_GRID.xml" (所有记录)
        xml="/Kfxt/ZSJF/JFWTCL_GRID_WCL.xml" (未处理)
        xml="/Kfxt/ZSJF/JFWTCL_GRID_YCL.xml" (已处理)
        输出列表按 录入日期 `LrDate` 降序排序 `descend`
        '''
        params = dict(
            xml="/Kfxt/ZSJF/JFWTCL_GRID.xml",
            gridId="appGrid",
            sortCol="LrDate",
            sortDir="descend",
            vscrollmode="0",
            multiSelect="1",
            selectByCheckBox="0",
            filter=init_filter(project_id),
            processNullFilter="1",
            customFilter="",
            customFilter2="",
            dependencySQLFilter="",
            location="",
            pageNum=page_num,
            pageSize=page_size,
            showPageCount="1",
            appName="Default",
            application="",
            cp="",
        )
        resp_data = self.fetch(URI_GRID_DATA, params=params)
        if self.validate_response(resp_data):
            resp = resp_data.pop("response")
            soup = get_soup(resp.text)
            table = soup.find(attrs={"id": "gridBodyTable"})
            if not table:
                return resp_data
            rows = []
            for tr in table.find_all(attrs={"otype": "1"}):
                ProblemGUID = tr.attrs["ProblemGUID".lower()]
                r = [td.getText() for td in tr.find_all(name="td")]
                vals = []
                for idx, val in enumerate(r):
                    if idx in {2, 3, 4, 5, 6, 9, 13}:
                        vals.append(val)
                rows.append({ProblemGUID: tuple(vals)})
            resp_data["rows"] = rows
        return resp_data

    def _preTransferTask(self, problemGUID, workerGUID):
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
        if self.validate_response(resp_data):
            resp = resp_data.pop("response")
            soup = get_soup(resp.text)
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
                    if key == 'ddlTaskLevel':
                        selected = e.find(attrs={"selected": "selected"})
                        val = selected.attrs["value"]
                    elif key == 'ddlTaskType':
                        val = u'地产保修'
                    elif key == 'txtContent':
                        val = e.getText()
                    else:
                        val = e.attrs.get("value", "")
                        if key in {
                            'txtTaskCode',
                        }:
                            print key, val

                    if isinstance(val, unicode):
                        val = val.encode('gb2312')
                    else:
                        val = val.decode('utf-8').encode('gb2312')
                    resp_data[key] = val
            resp_data.update(dict(
                __btnUpFile=u"上 传".encode("gb2312"),
                __EVENTTARGET="__Submit",
                __EVENTARGUMENT="2",
            ))
        return resp_data

    def transferTask(self, problemGUID, workerGUID=WORKER_IDS["default"]):
        """
        return: {'taskguid':xx}
        """
        data = self._preTransferTask(problemGUID, workerGUID)
        # print urllib.urlencode(data)
        # self.getTaskByCode(data["txtTaskCode"])
        params = dict(
            mode="1",
            tasksource="2",
            taskguid="",
            receiveguid="",
            WorkerGUIDStr=workerGUID,
            funcid="01020502",
        )
        resp_data = self.postUrl(URI_RWCL_EDIT, params=params, data=data)
        if self.validate_response(resp_data):
            resp = resp_data.pop('response')
            soup = get_soup(resp.text)
            e = soup.find(attrs={"name": "txtTaskGUID"})
            if not e: return
            resp_data["taskguid"] = e.attrs["value"]
        return resp_data

    def _createWorkSheet(self, taskguid, problemGUID):
        params = dict(
            mode="1",
            type="touch",
            taskguid=taskguid,
            workguid="",
            funcid="01020504",
        )
        data = dict(
            problemGUID=problemGUID,
        )

        resp_data = self.postUrl(URI_RWCL_WORK, params=params, data=data)
        if self.validate_response(resp_data):
            resp = resp_data.pop("response")
            # q = Q(resp.content)
            soup = get_soup(resp.text)
            # ---------- Prepare Params for Transfering Task ----------
            for key in {
                "__VIEWSTATE", "txtWorkCode", "txtForeAction", "txtForePara",
                "txtBackAction", "txtTaskGUID", "txtWorkGUID", "txtProblemGUIDStr",
                "txtTsProjGUID", "TxtBdsxDate", "txtWorkType", "txtClStatus",
                "txtTaskType", "txtTaskSource", "txtProblemPower", "txtZrdwGUID",
                "txtToDw", "txtZrDw", "txtProviderName", "txtProviderGUID", "txtFxdd",
                "txtCheckPlace", "txtWorkContent", "txtClfa", "txtJdr",
                "txtHandSet", "txtPdr", "txtPdDate",
            }:
                e = soup.find(attrs={"name": key})
                if e:
                    val = e.attrs.get("value", "")
                    if isinstance(val, unicode):
                        val = val.encode('gb2312')
                    else:
                        val = val.decode('utf-8').encode('gb2312')
                    resp_data[key] = val
            resp_data.update(dict(
                __EVENTTARGET="__Submit",
                __EVENTARGUMENT="1",
            ))
        return resp_data

    def assignTask(self, taskguid, problemguid):
        data = self._createWorkSheet(taskguid, problemguid)
        params = dict(
            mode="1",
            type="touch",
            taskguid=taskguid,
            workguid="",
            funcid="01020504",
        )
        resp = self.postUrl(URI_RWCL_WORK, params=params, data=data)
        return resp

    def getJFTaskList(self, project_id, task_code=None, page_num=1, page_size=20):
        """
            获取交付任务列表
            return [{'taskguid': xx, 'display': (xx,...)}...]
        """
        params = dict(
            filter=init_filter(project_id, task_code),
            xml="/kfxt/rwgl/Rwcl_Grid_JF_JfRoom.xml",
            funcid="01020504",
            gridId="appGrid",
            sortCol="",
            sortDir="",
            vscrollmode="0",
            multiSelect="1",
            selectByCheckBox="0",
            processNullFilter="1",
            customFilter="",
            customFilter2="",
            dependencySQLFilter="",
            location="",
            pageNum=page_num,
            pageSize=page_size,
            showPageCount="1",
            appName="Default",
            application="",
            cp="",
        )
        resp_data = self.fetch(URI_GRID_DATA, params=params)
        if self.validate_response(resp_data):
            response = resp_data.pop('response')
            soup = get_soup(response.text)
            ret = []
            for tr in soup.select('tr[taskguid]'):
                d = {'taskguid': tr.attrs["taskguid"]}
                display = []
                for td in tr.find_all('td'):
                    display.append(td.getText())
                d["display"] = tuple(display)
                ret.append(d)
            resp_data = ret
        return resp_data

    def run_assign_task(self, problemGUID):
        data = self.transferTask(problemGUID)
        self.assignTask(data["taskguid"], problemGUID)


def main():
    # args = handle_args()
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
    # pprint(mingy.getJFTaskList(args.project, args.taskcode))
    # r1 = mingy.fetch(
    #     '/_grid/griddata.aspx?xml=%2fkfxt%2frwgl%2fRwcl_Grid_JF_JfRoom.xml&funcid=01020504&gridId=appGrid&sortCol=&sortDir=&vscrollmode=0&multiSelect=1&selectByCheckBox=0&filter=%3cfilter+type%3d%22and%22%3e%3cfilter+type%3d%22and%22%3e%3ccondition+operator%3d%22in%22+attribute%3d%22TsProjGUID%22+value%3d%227bbc819c-a561-e411-9927-e41f13c5183a%22+%2f%3e%3c%2ffilter%3e%3cfilter+type%3d%22and%22%3e%3cfilter+type%3d%22or%22%3e%3ccondition+attribute%3d%22taskcode%22+operator%3d%22like%22+datatype%3d%22varchar%22+value%3d%221002%22+%2f%3e%3c%2ffilter%3e%3c%2ffilter%3e%3c%2ffilter%3e&processNullFilter=1&customFilter=&customFilter2=&dependencySQLFilter=&location=&pageNum=1&pageSize=18&showPageCount=1&appName=Default&application=&cp=')
    # r2 = mingy.fetch(
    #     '/_grid/griddata.aspx?xml=%2fkfxt%2frwgl%2fRwcl_Grid_JF_JfRoom.xml&funcid=01020504&gridId=appGrid&sortCol=&sortDir=&vscrollmode=0&multiSelect=1&selectByCheckBox=0&filter=%3cfilter+type%3d%22and%22%3e%3ccondition+operator%3d%22in%22+attribute%3d%22TsProjGUID%22+value%3d%227bbc819c-a561-e411-9927-e41f13c5183a%22+%2f%3e%3ccondition+attribute%3d%22taskcode%22+operator%3d%22like%22+datatype%3d%22varchar%22+value%3d%221002%22+%2f%3e%3c%2ffilter%3e&processNullFilter=1&customFilter=&customFilter2=&dependencySQLFilter=&location=&pageNum=1&pageSize=18&showPageCount=1&appName=Default&application=&cp=')
    # a = r1["response"].content
    # b = r1["response"].content
    # print len(a)
    # print '========================='
    # print len(b)
    # print a == b
    # print init_filter(project_id="7bbc819c-a561-e411-9927-e41f13c5183a",
    #     task_code="1002")
    # print urllib.unquote_plus(s)
    # problems = mingy.getProblemList()
    # print len(problems["rows"])
    # pbs = problems.get("rows")
    # if pbs:
    #     pid = pbs[0].keys()[0]
    #     print pid
    #     data =  mingy.transferTask(pid)
    #     mingy.assignTask(data["taskguid"], data["problemGUID"])
    # resp_data = mingy.fetch('/Kfxt/PUB/Verify_Public.aspx?p_Func=%u4EFB%u52A1%u7BA1%u7406&p_Mode=%u95EE%u9898%u89E3%u9501&rdnum=0.17257182981973673')
    # print resp_data["response"].text.encode('utf-8')
    # print mingy.getReceiveList()
    # mingy.getUsers()
    # for i in my.getReceiveList()["receiveList"]:
    #     print ' '.join(i).encode('utf-8')
    resp = mingy.run_assign_task('261b3db9-21d7-4aa4-876f-ad7fdeca4d51')
    print resp.text


if __name__ == '__main__':
    main()
