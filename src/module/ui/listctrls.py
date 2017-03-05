# coding:utf-8
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ColumnSorterMixin, CheckListCtrlMixin

import images
from util import Widget, WidgetArray, Factory


class SortListCtrl(wx.ListCtrl,
                   ListCtrlAutoWidthMixin,
                   ColumnSorterMixin
                   ):
    headings = []

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT |
                                   wx.LC_SORT_DESCENDING
                             )
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
        self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging)

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

    def OnColDragging(self, event):
        pass

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()


class CheckSortListCtrl(SortListCtrl, CheckListCtrlMixin):
    def __init__(self, *args, **kwargs):
        super(CheckSortListCtrl, self).__init__(*args, **kwargs)
        CheckListCtrlMixin.__init__(self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        data = self.GetItemData(index)
        # title = musicdata[data][1]
        if flag:
            what = "checked"
        else:
            what = "unchecked"
        print what


class ReceivesListCtrl(Factory, SortListCtrl):
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
            # if w.get('format'):
            #     li.SetAlign(w.get('format'))
            self.InsertColumnItem(w.index, li)
        return self

    def AddRows(self, data_list):
        # self.DeleteAllColumns()
        self.DeleteAllItems()
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
        self.SetColumnWidth(2, 100)

        return

BATCH_TASK_TYPE = {
    1: u'未处理',
    2: u'已转任务'
}


class TaskAssignListCtrl(Factory, SortListCtrl):
    headings = WidgetArray(
        Widget(wx.ListItem, text=u'状态'),  # 2
        Widget(wx.ListItem, text=u'房产'),  # 3
        Widget(wx.ListItem, text=u'部位'),  # 4
        Widget(wx.ListItem, text=u'问题分类'),  # 5
        Widget(wx.ListItem, text=u'问题描述'),  # 6
        Widget(wx.ListItem, text=u'录入时间'),  # 9
        Widget(wx.ListItem, text=u'任务编号'),  # 13
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
        self.DeleteAllItems()
        # self.ClearAll()
        # for i in range(10):
        #     print ' >> '.join(data_list[i].values()[0])
        # return
        if isinstance(data_list[0], dict):
            data_list = [i.values()[0] for i in data_list]

        for row_num, row_data in enumerate(data_list):
            pos = self.InsertImageStringItem(row_num, row_data[0], self.idx1)
            # add values in the other columns on the same row
            for idx, val in enumerate(row_data[1:self.GetColumnCount()]):
                self.SetStringItem(pos, idx + 1, val)
                self.SetItemData(pos, row_num + 1)
            listitem = self.GetItem(pos)

            if row_data[0] == u'未处理':
                listitem.SetTextColour(wx.NamedColour("RED"))
            elif row_data[0] == u'已转任务':
                listitem.SetTextColour(wx.NamedColour("BLUE"))
                # listitem.SetFont(listitem.GetFont().Bold())
            elif row_data[0] == u'实施中':
                listitem.SetTextColour(wx.NamedColour("PURPLE"))
            elif row_data[0] == u'已关闭':
                listitem.SetTextColour(wx.NamedColour('GRAY'))
            self.SetItem(listitem)
            #
        self.SetItemDataMap(data_list)
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        return

    def has_unhandled_problems(self):
        for _, v in self.itemDataMap.iteritems():
            if v[0] == BATCH_TASK_TYPE[1]:
                return True
        return False

    def has_transfered_task(self):
        for _, v in self.itemDataMap.iteritems():
            if v[0] == BATCH_TASK_TYPE[2]:
                return True
        return False

    def getItemDataList(self, type):
        '''
        type `1` get datalist of `status` `未处理`
            `2`               of `status` `已转任务`
        '''

        ret = []
        for k, v in self.itemDataMap.iteritems():
            line = (' ' * 4).join(v)
            if v[0] == BATCH_TASK_TYPE[type]:
                ret.append(line)
        return ret
