# coding:utf-8
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ColumnSorterMixin
from util import Widget, WidgetArray, Factory
import images


class BaseListCtrl(wx.ListCtrl,
                   ListCtrlAutoWidthMixin,
                   ColumnSorterMixin
                   ):
    headings = []

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT |
                                   wx.LC_SORT_DESCENDING|
                                   wx.LC_ALIGN_LEFT)
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, len(self.headings))
        # show how to select an item
        # self.list.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        # show how to change the colour of a couple items
        # item = self.list.GetItem(1)
        # item.SetTextColour(wx.BLUE)
        # self.list.SetItem(item)
        # item = self.list.GetItem(4)
        # item.SetTextColour(wx.RED)
        # self.list.SetItem(item)
        self.il = wx.ImageList(16, 16)
        self.idx1 = self.il.Add(images.Smiles.GetBitmap())
        self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

    def AddRows(self, data_list):
        raise NotImplementedError()

    def SetItemDataMap(self, data_list):
        datamap = {}
        for idx, val in enumerate(data_list):
            datamap[idx + 1] = tuple(val)
        self.itemDataMap = datamap


class ReceivesListCtrl(Factory, BaseListCtrl):
    headings = WidgetArray(
        Widget(wx.ListItem, text=u'接待时间'),
        Widget(wx.ListItem, text=u'主题'),
        Widget(wx.ListItem, text=u'请求来源'),
        Widget(wx.ListItem, text=u'房间'),
        Widget(wx.ListItem, text=u'服务请求人'),
        Widget(wx.ListItem, text=u'接待人'),
        Widget(wx.ListItem, text=u"分解状态"),
    )

    @classmethod
    def create(cls, parent):
        self = cls(parent)
        for w in self.iter_widegts():
            li = w.create()
            li.SetText(w.get('text'))
            self.InsertColumnItem(w.index, li)
        return self

    def AddRows(self, data_list):
        # self.DeleteAllColumns()
        # self.DeleteAllItems()
        # self.ClearAll()

        for row_num, row_data in enumerate(data_list):
            pos = self.InsertImageStringItem(row_num, row_data[0], self.idx1)
            # add values in the other columns on the same row
            for idx, val in enumerate(row_data[1:self.GetColumnCount()]):
                self.SetStringItem(pos, idx + 1, val)
                self.SetItemData(pos, row_num + 1)
            listitem = self.GetItem(pos)

            if row_data[-1] == u'已关闭':
                listitem.SetTextColour(wx.NamedColour("GRAY"))
            elif row_data[-1] == u'待分解':
                listitem.SetTextColour(wx.NamedColour("RED"))
                # listitem.SetFont(listitem.GetFont().Bold())
            elif row_data[-1] == u'分解完毕':
                listitem.SetTextColour(wx.NamedColour("BLUE"))
            self.SetItem(listitem)
            #
        self.SetItemDataMap(data_list)
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        return


if __name__ == '__main__':
    app = wx.App()
    fr = wx.Frame(None)
    lc = ReceivesListCtrl.create(fr)
    rows = [(u'2017-02-27 15:27',
             u'\u4fdd\u5229\u827e\u8f69-\u516c\u5bd3-\u84dd\u975b\u8def1688\u5f04121\u53f7-1-702-\u54a8\u8be2-20170227',
             u'\u5fae\u4fe1', u'\u4fdd\u5229\u827e\u8f69-\u516c\u5bd3-\u84dd\u975b\u8def1688\u5f04121\u53f7-1-702',
             u'\u8881\u9716', u'\u5f90\u8bd7\u4fca', u'\u5df2\u5173\u95ed'), (u'2017-02-24 15:24',
                                                                              u'\u4fdd\u5229\u827e\u8f69-\u516c\u5bd3-\u84dd\u975b\u8def1688\u5f04138\u53f7-1802-\u54a8\u8be2-20170224',
                                                                              u'\u5fae\u4fe1',
                                                                              u'\u4fdd\u5229\u827e\u8f69-\u516c\u5bd3-\u84dd\u975b\u8def1688\u5f04138\u53f7-1802',
                                                                              u'\u9ec4\u83b9', u'\u5f90\u8bd7\u4fca',
                                                                              u'\u5df2\u5173\u95ed'), (
                u'2017-02-23 15:23',
                u'\u4fdd\u5229\u827e\u8f69-\u516c\u5bd3-\u84dd\u975b\u8def1688\u5f04138\u53f7-1702-\u54a8\u8be2-20170223',
                u'\u5fae\u4fe1', u'\u4fdd\u5229\u827e\u8f69-\u516c\u5bd3-\u84dd\u975b\u8def1688\u5f04138\u53f7-1702',
                u'\u987e\u5b89\u821f', u'\u5f90\u8bd7\u4fca', u'\u5df2\u5173\u95ed'), (u'2017-02-23 12:43',
                                                                                       u'\u4e0a\u6d77\u53f6\u4e0a\u6d77-\u4fdd\u5229\u53f6\u90fd-\u516c\u5bd3\u533a-\u8054\u6768\u8def1078\u5f047\u53f7-604-\u6295\u8bc9-20170223',
                                                                                       u'\u5fae\u4fe1',
                                                                                       u'\u4e0a\u6d77\u53f6\u4e0a\u6d77-\u4fdd\u5229\u53f6\u90fd-\u516c\u5bd3\u533a-\u8054\u6768\u8def1078\u5f047\u53f7-604',
                                                                                       u'\u970d\u6842\u5c71',
                                                                                       u'\u5f90\u8bd7\u4fca',
                                                                                       u'\u5206\u89e3\u5b8c\u6bd5'), (
                u'2017-02-21 13:38',
                u'\u4e0a\u6d77\u53f6\u4e0a\u6d77-\u4fdd\u5229\u53f6\u90fd-\u516c\u5bd3\u533a-\u8054\u6768\u8def1078\u5f045\u53f7-3204-\u54a8\u8be2-20170221',
                u'\u5fae\u4fe1',
                u'\u4e0a\u6d77\u53f6\u4e0a\u6d77-\u4fdd\u5229\u53f6\u90fd-\u516c\u5bd3\u533a-\u8054\u6768\u8def1078\u5f045\u53f7-3204',
                u'\u4fdd\u5229\u827e\u8f69-\u516c\u5bd3-\u84dd\u975b\u8def1688\u5f04120\u53f7-1001', u'\u8d75\u8f89',
                u'\u5468\u4f73\u8363', u'\u5206\u89e3\u5b8c\u6bd5')]
    lc.AddRows(rows)
    fr.Show()
    app.MainLoop()
