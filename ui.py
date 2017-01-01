# coding:utf-8

import wx
from mixin import constructor
from collections import OrderedDict
import json
import os
from client import MinYuanClient
import  wx.lib.mixins.listctrl  as  listmix

def get_const():
    constfilepath = os.path.join(os.path.dirname(__file__), "const.json")
    return json.load(open(constfilepath))


def create_menu(frame, data):
    for title, args in data.items():
        m = wx.Menu()
        for arg in args:
            if arg == -1:
                m.AppendSeparator()
            else:
                # kind: 0 normal, 1 check, 2 radio, -1 seprator
                arg["id"] = arg.get('id', -1)
                arg["kind"] = arg.get('kind', 0)
                mi = MenuItem(parentMenu=m, **arg)
                m.AppendItem(mi)
                frame.Bind(wx.EVT_MENU, mi.get_arg("handler"), mi)
                mi.Enable({1: 1, 0: 0, None: 1}[mi.get_arg("enable")])
        yield (m, title)

def create_menubar(frame, data):
    mb = wx.MenuBar()
    # create menu
    for m, title in create_menu(frame, data):
        mb.Append(m, title)
    return mb


@constructor
class MenuItem(wx.MenuItem):
    pass

@constructor
class ReceiveListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def construct(self):
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def AddRows(self, data_list):
        for key, row in enumerate(data_list):
            count = self.GetItemCount()
            pos = self.InsertStringItem(count, row[0])
            # add values in the other columns on the same row
            for idx, val in enumerate(row[1:]):
                self.SetStringItem(pos, idx + 1, val)
            self.SetItemData(pos, key + 1)
        # self.addCache(data_list)

    initRows = AddRows

    def AdaptWidth(self, headings_num, proportions):
        num = sum(proportions)
        _w = self.GetParent().GetClientSize()[0] / float(num)
        for i in range(headings_num):
            w = _w * proportions[i]
            self.SetColumnWidth(i, w)
@constructor
class Frame(wx.Frame, listmix.ColumnSorterMixin):

    @property
    def const(self):
        return get_const()

    @property
    def columnNum(self):
        return len(self.const["headings"])

    def construct(self):
        self.initAll()
        listmix.ColumnSorterMixin.__init__(self, self.columnNum)
        self.Center()
        self.SetTitle(self.const["weixin_demo_title"])

    def initAll(self):
        for i in dir(self):
            if i.startswith('_init'):
                getattr(self, i)()

    def _initEventBinding(self):
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def _initMenuBar(self):
        _OD = OrderedDict()
        const_menubar = self.const["menubar"]
        _OD[const_menubar[0]["title"]] = [
            dict(text=const_menubar[0]["items"][0], handler=self.OnAdd),
            -1,
            dict(text=const_menubar[0]["items"][1], handler=self.OnQuit),
        ]
        _OD[const_menubar[1]["title"]] = [
            dict(text=const_menubar[1]["items"][0], kind=1, handler=self.OnSwitchTop),
        ]
        _OD[const_menubar[2]["title"]] = [
            dict(text=const_menubar[2]["items"][0], handler=self.OnClockSet)
        ]

        mb = create_menubar(self, _OD)

        # final
        self.SetMenuBar(mb)

    def _initListCtrl(self):
        const_headings = self.const["headings"]
        self.LC = ReceiveListCtrl(self,
                                  style=wx.LC_REPORT,
                                  headings=const_headings,
                                  # columnFormat=wx.LIST_FORMAT_CENTER,
                                  fgcolor='#f40',

                                  )
        my = MinYuanClient()
        data = my.getReceiveList(page_size=30)
        if "receiveList" in data:
            rl = data["receiveList"]
            self.LC.AddRows(rl)
            datamap = {}
            for idx, val in enumerate(rl):
                datamap[idx + 1] = tuple(val)
            self.itemDataMap = datamap
            self.LC.AdaptWidth(len(const_headings), [1, 3, 1, 2, 1, 1, 1])

    def OnAdd(self, evt):
        pass
    def OnQuit(self, evt):
        self.Destroy()

    def OnSwitchTop(self, evt):
        pass
    def OnClockSet(self, evt):
        pass

    def OnResize(self, e):
        def call():
            self.LC.Hide()
            self.LC.AdaptWidth(7, proportions=[1, 3, 1, 2, 1, 1, 1])
            self.LC.SetClientSize(self.GetClientSize())
            self.LC.Show()
        wx.CallAfter(call)

    def GetListCtrl(self):
        return self.LC