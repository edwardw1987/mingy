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
                                   wx.LC_SORT_DESCENDING)
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, len(self.headings))

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        self.il = wx.ImageList(16, 16)
        # self.idx1 = self.il.Add(images.Smiles.GetBitmap())
        self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        return (self.sm_dn, self.sm_up)


class ReceivesListCtrl(Factory, BaseListCtrl):
    headings = WidgetArray(
        Widget(wx.ListItem, text=u"分解状态"),
        Widget(wx.ListItem, text=u'接待时间'),
        Widget(wx.ListItem, text=u'主题'),
        Widget(wx.ListItem, text=u'请求来源'),
        Widget(wx.ListItem, text=u'房间'),
        Widget(wx.ListItem, text=u'服务请求人'),
        Widget(wx.ListItem, text=u'接待人'),
    )

    @classmethod
    def create(cls, parent):
        self = cls(parent)
        for w in self.iter_widegts():
            li = w.create()
            li.SetText(w.get('text'))
            self.InsertColumnItem(w.index, li)
