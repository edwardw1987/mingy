# coding:utf-8
import sys

import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin

import images
import listctrls
from models import MenuBar, MenuAction, MenuView
from context import modal_ctx
from event import CountingThread, EVT_COUNT

headings = [
    u"接待时间",
    u"主题",
    u"请求来源",
    u"房间",
    u"服务请求人",
    u"接待人",
    u"分解状态",
]


class ColoredPanel(wx.Window):
    def __init__(self, parent, color):
        wx.Window.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(color)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)


class Panel01(wx.Panel, ColumnSorterMixin):
    def __init__(self, parent):
        super(wx.Panel, self).__init__(parent)
        self.parent = parent
        self._init_listctrl()

    def _init_listctrl(self):
        self.listctrl = listctrls.ReceiveList(self)

        # ----- layout -----
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(self.listctrl, 1, wx.EXPAND | wx.ALL)
        # self.SetSizer(sizer)
        # self.Layout()
        # self.listctrl.SetAutoLayout(True)
        # ----------
        self.il = wx.ImageList(16, 16)

        # self.idx1 = self.il.Add(images.Smiles.GetBitmap())
        self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())
        self.listctrl.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

    def GetListCtrl(self):
        return self.listctrl

    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)


from client import MinYuanClient, MINGYUAN_OFFICIAL_ADDR


class TestListCtrlPanel(wx.Panel, ColumnSorterMixin):
    def __init__(self, parent, log):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        self.log = log
        tID = wx.NewId()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.frame = wx.FindWindowById(9999)
        if wx.Platform == "__WXMAC__" and \
                hasattr(wx.GetApp().GetTopWindow(), "LoadDemo"):
            self.useNative = wx.CheckBox(self, -1, "Use native listctrl")
            self.useNative.SetValue(
                not wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic"))
            self.Bind(wx.EVT_CHECKBOX, self.OnUseNative, self.useNative)
            sizer.Add(self.useNative, 0, wx.ALL | wx.ALIGN_RIGHT, 4)

        self.il = wx.ImageList(16, 16)

        self.idx1 = self.il.Add(images.Smiles.GetBitmap())
        self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())

        self.list = listctrls.TestListCtrl(self, tID,
                                           style=wx.LC_REPORT
                                                 # | wx.BORDER_SUNKEN
                                                 | wx.BORDER_NONE
                                                 | wx.LC_EDIT_LABELS
                                                 | wx.LC_SORT_ASCENDING
                                           # | wx.LC_NO_HEADER
                                           # | wx.LC_VRULES
                                           # | wx.LC_HRULES
                                           # | wx.LC_SINGLE_SEL
                                           )

        self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        sizer.Add(self.list, 1, wx.EXPAND)

        self.PopulateList(heading_only=True)

        # Now that the list exists we can init the other base class,
        # see wx/lib/mixins/listctrl.py
        # self.itemDataMap = musicdata
        ColumnSorterMixin.__init__(self, len(headings))
        # self.SortListItems(0, True)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
        self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        # for wxMSW
        self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.list.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        # for sync data
        MenuBar.action.instance.Bind(
            wx.EVT_MENU, self.OnSyncData, MenuAction.sync_data.instance)
        # for auto-sync data
        MenuBar.action.instance.Bind(
            wx.EVT_MENU, self.OnToggleAutoSync, MenuAction.auto_sync.instance)
        # for count event
        self.frame.Bind(EVT_COUNT, self.OnCount)

    def OnCount(self, e):
        _, s = e.GetValue()
        print s
        if s % 15 == 0:
            e.auto = True
            wx.CallAfter(self.OnSyncData, e)

    def SetStatusText(self, text):
        status_bar = wx.FindWindowById(9999).GetStatusBar()
        status_bar.SetStatusText(text)

    def _handle_popup(self, event):
        # 弹窗提醒用户有待分解的记录
        if getattr(event, 'auto', False):

            if self.frame.IsIconized():
                self.frame.Restore()

            m = MenuView.stay_on_top.instance
            if not m.IsChecked():
                m.Check()
                self.frame.SetWindowStyle(self.frame.GetWindowStyle() | wx.STAY_ON_TOP)

    def OnSyncData(self, event):
        self.SetStatusText(u"正在同步数据......")
        my = MinYuanClient(addr=MINGYUAN_OFFICIAL_ADDR)
        data = my.getJdjl(page_size=30)
        if data.get("rows"):
            rows = data["rows"]
            datamap = {}
            for idx, val in enumerate(rows):
                datamap[idx + 1] = tuple(val)
            self.itemDataMap = datamap
            self.list.ClearAll()
            self.PopulateList()
            self.SetStatusText(u'数据同步成功')
            self._handle_popup(event)
        else:
            self.SetStatusText('')
            dlg = wx.MessageDialog(self,
                                   u"请确认网络正常并且VPN已开启",
                                   u"连接错误",
                                   wx.OK | wx.ICON_ERROR)
            if modal_ctx.set_modal(dlg):
                with modal_ctx as dlg:
                    dlg.ShowModal()
                    dlg.Destroy()

    def OnToggleAutoSync(self, e):
        if e.IsChecked():
            thd = CountingThread(self.frame, (1, 1))
            self._auto_sync_thread = thd
            self.frame.push_thread(thd)
            thd.start()
        else:
            if not self._auto_sync_thread.stopped():
                self._auto_sync_thread.stop()

    def OnUseNative(self, event):
        wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", not event.IsChecked())
        wx.GetApp().GetTopWindow().LoadDemo("ListCtrl")

    def PopulateList(self, heading_only=False):

        if 0:
            # for normal, simple columns, you can add them like this:
            self.list.InsertColumn(0, "Artist")
            self.list.InsertColumn(1, "Title", wx.LIST_FORMAT_RIGHT)
            self.list.InsertColumn(2, "Genre")
        else:
            # but since we want images on the column header we have to do it the hard way:
            info = wx.ListItem()
            info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
            info.m_image = -1
            info.m_format = 0
            info.m_text = headings[0]
            self.list.InsertColumnInfo(0, info)

            info.m_format = wx.LIST_FORMAT_RIGHT
            info.m_text = headings[1]
            self.list.InsertColumnInfo(1, info)

            info.m_format = 0
            info.m_text = headings[2]
            self.list.InsertColumnInfo(2, info)
            info.m_format = 0
            info.m_text = headings[3]
            self.list.InsertColumnInfo(3, info)
            info.m_format = 0
            info.m_text = headings[4]
            self.list.InsertColumnInfo(4, info)
            info.m_format = 0
            info.m_text = headings[5]
            self.list.InsertColumnInfo(5, info)
            info.m_format = 0
            info.m_text = headings[6]
            self.list.InsertColumnInfo(6, info)
        if heading_only:
            return
        items = self.itemDataMap.items()
        for key, data in items:
            index = self.list.InsertImageStringItem(sys.maxint, data[0], self.idx1)
            item = self.list.GetItem(index)
            for pos, val in enumerate(data[1:]):
                self.list.SetStringItem(index, pos + 1, val)
                if data[-1] == u"已关闭":
                    item.SetTextColour(wx.NamedColour("GRAY"))
                elif data[-1] == u'待分解':
                    item.SetTextColour(wx.NamedColour("RED"))
                    item.SetFont(item.GetFont().Bold())
                    self._popup = True
                elif data[-1] == u'分解完毕':
                    item.SetTextColour(wx.NamedColour("BLUE"))
                    item.SetFont(item.GetFont().Bold())
                self.list.SetItem(item)
            self.list.SetItemData(index, key)

        self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        # show how to select an item
        self.list.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        # show how to change the colour of a couple items
        # item = self.list.GetItem(1)
        # item.SetTextColour(wx.BLUE)
        # self.list.SetItem(item)
        # item = self.list.GetItem(4)
        # item.SetTextColour(wx.RED)
        # self.list.SetItem(item)

        self.currentItem = 0

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

    def OnRightDown(self, event):
        x = event.GetX()
        y = event.GetY()
        self.log.WriteText("x, y = %s\n" % str((x, y)))
        item, flags = self.list.HitTest((x, y))

        if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
            self.list.Select(item)

        event.Skip()

    def getColumnText(self, index, col):
        item = self.list.GetItem(index, col)
        return item.GetText()

    def OnItemSelected(self, event):
        ##print event.GetItem().GetTextColour()
        self.currentItem = event.m_itemIndex
        self.log.WriteText("OnItemSelected: %s, %s, %s, %s\n" %
                           (self.currentItem,
                            self.list.GetItemText(self.currentItem),
                            self.getColumnText(self.currentItem, 1),
                            self.getColumnText(self.currentItem, 2)))

        if self.currentItem == 10:
            self.log.WriteText("OnItemSelected: Veto'd selection\n")
            # event.Veto()  # doesn't work
            # this does
            self.list.SetItemState(10, 0, wx.LIST_STATE_SELECTED)

        event.Skip()

    def OnItemDeselected(self, evt):
        item = evt.GetItem()
        self.log.WriteText("OnItemDeselected: %d" % evt.m_itemIndex)

        # Show how to reselect something we don't want deselected
        if evt.m_itemIndex == 11:
            wx.CallAfter(self.list.SetItemState, 11, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        self.log.WriteText("OnItemActivated: %s\nTopItem: %s" %
                           (self.list.GetItemText(self.currentItem), self.list.GetTopItem()))

    def OnBeginEdit(self, event):
        self.log.WriteText("OnBeginEdit")
        event.Allow()

    def OnItemDelete(self, event):
        self.log.WriteText("OnItemDelete\n")

    def OnColClick(self, event):
        self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
        event.Skip()

    def OnColRightClick(self, event):
        item = self.list.GetColumn(event.GetColumn())
        self.log.WriteText("OnColRightClick: %d %s\n" %
                           (event.GetColumn(), (item.GetText(), item.GetAlign(),
                                                item.GetWidth(), item.GetImage())))
        if self.list.HasColumnOrderSupport():
            self.log.WriteText("OnColRightClick: column order: %d\n" %
                               self.list.GetColumnOrder(event.GetColumn()))

    def OnColBeginDrag(self, event):
        self.log.WriteText("OnColBeginDrag\n")
        ## Show how to not allow a column to be resized
        # if event.GetColumn() == 0:
        #    event.Veto()

    def OnColDragging(self, event):
        self.log.WriteText("OnColDragging\n")

    def OnColEndDrag(self, event):
        self.log.WriteText("OnColEndDrag\n")

    def OnDoubleClick(self, event):
        self.log.WriteText("OnDoubleClick item %s\n" % self.list.GetItemText(self.currentItem))
        event.Skip()

    def OnRightClick(self, event):
        self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))

        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.popupID5 = wx.NewId()
            self.popupID6 = wx.NewId()

            # self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            # self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            # self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            # self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            # self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            # self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, "FindItem tests")
        menu.Append(self.popupID2, "Iterate Selected")
        menu.Append(self.popupID3, "ClearAll and repopulate")
        menu.Append(self.popupID4, "DeleteAllItems")
        menu.Append(self.popupID5, "GetItem")
        menu.Append(self.popupID6, "Edit")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, event):
        self.log.WriteText("Popup one\n")
        print "FindItem:", self.list.FindItem(-1, "Roxette")
        print "FindItemData:", self.list.FindItemData(-1, 11)

    def OnPopupTwo(self, event):
        self.log.WriteText("Selected items:\n")
        index = self.list.GetFirstSelected()

        while index != -1:
            self.log.WriteText("      %s: %s\n" % (self.list.GetItemText(index), self.getColumnText(index, 1)))
            index = self.list.GetNextSelected(index)

    def OnPopupThree(self, event):
        self.log.WriteText("Popup three\n")
        self.list.ClearAll()
        wx.CallAfter(self.PopulateList)

    def OnPopupFour(self, event):
        self.list.DeleteAllItems()

    def OnPopupFive(self, event):
        item = self.list.GetItem(self.currentItem)
        print item.m_text, item.m_itemId, self.list.GetItemData(self.currentItem)

    def OnPopupSix(self, event):
        self.list.EditLabel(self.currentItem)
