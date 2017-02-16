# coding:utf-8

from datetime import datetime

import wx

import listctrls
from context import modal_ctx
from dialogs import AutoSyncDialog
from event import CountingThread, EVT_COUNT
from models import MenuBar, MenuAction, MenuView, MenuSetting
from client import MinYuanClient, MINGYUAN_OFFICIAL_ADDR
from util import Factory

class ColoredPanel(wx.Window):
    def __init__(self, parent, color):
        wx.Window.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(color)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)


class BasePanel(Factory, wx.Panel):
    def __init__(self, parent, log, name):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS, name=name)
        self.log = log
        self.listbook = parent
        self._restore_frame = False



class WeChatReminderPanel(wx.Panel):
    def __init__(self, parent, log, name):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS, name=name)
        self.log = log
        self.listbook = parent
        self._restore_frame = False

        tID = wx.NewId()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.frame = wx.FindWindowById(9999)
        self.list = listctrls.ReceivesListCtrl.create(self)
        li = self.list.headings[0]
        li.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        self.list.SetColumn(0, li)
        sizer.Add(self.list, 1, wx.EXPAND)
        #
        # self.list.SortListItems(0, True)
        #
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        # self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        # self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
        # self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        # self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
        # self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
        # self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
        self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
        # self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
        # self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)
        # self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        # self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        # for wxMSW
        # self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        # self.list.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        # for sync data
        MenuBar.menus.action.Bind(
            wx.EVT_MENU, self.OnSyncReceives, MenuAction.items.sync_data)
        # for auto-sync data
        MenuBar.menus.action.Bind(
            wx.EVT_MENU, self.OnToggleAutoSync, MenuAction.items.auto_sync)
        # for set auto sync
        MenuBar.menus.settings.Bind(
            wx.EVT_MENU, self.OnSetAutoSync, MenuSetting.auto_sync.instance)
        # for count event
        self.list.Bind(EVT_COUNT, self.OnCount)

    def OnCount(self, e):
        _, s = e.GetValue()
        if s % 15 == 0:
            e.auto = True
            # self.frame.start_thread(self.OnSyncData, e)
            self.OnSyncReceives(e)

    def SetStatusText(self, text):
        status_bar = wx.FindWindowById(9999).GetStatusBar()
        status_bar.SetStatusText(text)

    def _handle_restore_frame(self, event):
        # 弹窗提醒用户有待分解的记录
        if not self._restore_frame:
            return
        if getattr(event, 'auto', False):
            if self.frame.IsIconized():
                self.frame.Restore()

            m = MenuView.stay_on_top.instance
            if not m.IsChecked():
                m.Check()
                self.frame.SetWindowStyle(self.frame.GetWindowStyle() | wx.STAY_ON_TOP)

    def _do_sync_receives(self, event):
        '同步接单记录过程'
        self.listbook.SetSelection(0)
        self.frame.Refresh()
        self.SetStatusText(u"正在同步数据......")
        my = MinYuanClient(addr=MINGYUAN_OFFICIAL_ADDR)
        data = my.getJdjl(page_size=30)
        if data.get("rows"):
            rows = data["rows"]
            datamap = {}
            for idx, val in enumerate(rows):
                datamap[idx + 1] = tuple(val)
            self.itemDataMap = datamap
            # self.list.ClearAll()
            wx.CallAfter(self.list.AddRows, rows)
            timestamp = datetime.now().strftime("%Y-%m-%d %X")
            msg = u'%s数据同步成功 at %s' % (self.Name, timestamp)
            self.SetStatusText(msg)
            wx.CallAfter(self.log.WriteText, msg)
            self._handle_restore_frame(event)
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

    def OnSyncReceives(self, event):
        # 新建一个子线程，用来同步接单记录，可以避免界面阻塞卡死
        thd = self.frame.push_thread(self._do_sync_receives, event)
        _sync_thread = getattr(self, '_sync_thread', None)
        # 如果旧线程isAlive则返回, 否则stop, delete旧线程
        if _sync_thread:
            if _sync_thread.isAlive():
                return
            self.frame.delete_thread(_sync_thread)
        self._sync_thread = thd
        thd.start()

    def OnToggleAutoSync(self, e):
        if e.IsChecked():
            thd = CountingThread(self.list, (1, 1))
            self._counting_thread = thd
            self.frame.push_thread(thd)
            thd.start()
        else:
            if not self._counting_thread.stopped():
                self._counting_thread.stop()

    def OnSetAutoSync(self, e):
        dlg = AutoSyncDialog(self, title='title')
        dlg.CenterOnParent()
        dlg.ShowModal()

    # ----------------------------------------------------
    def OnUseNative(self, event):
        wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", not event.IsChecked())
        wx.GetApp().GetTopWindow().LoadDemo("ListCtrl")

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
        self.Layout()
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


class AssignTaskPanel(BasePanel):
    @classmethod
    def create(cls, parent, log, name):
        self = cls(parent, log, name)
        self.list = listctrls.TaskAssignListCtrl.create(self)
        self._layout()
        return self

    def _layout(self):
        sizer = wx.BoxSizer()
        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

