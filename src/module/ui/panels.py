# coding:utf-8

from datetime import datetime

import wx

import listctrls
from client import MinYuanClient, MINGYUAN_OFFICIAL_ADDR, MINGYUAN_TEST_ADDR
from context import modal_ctx
from dialogs import AutoSyncDialog
from event import CountingThread, EVT_COUNT
from menus import MenuBar, MenuAction, MenuView, MenuSetting, MenuTaskAssign
from util import Widget


class ColoredPanel(wx.Window):
    def __init__(self, parent, color):
        wx.Window.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(color)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)


class BasePanel(wx.Panel):
    def __init__(self, parent, log, name):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS, name=name)
        self.log = log
        self.parent = parent
        self._restore_frame = False
        self.frame = wx.FindWindowById(9999)
        # for set auto sync duration
        MenuBar.menus.settings.Bind(
            wx.EVT_MENU, self.OnSetAutoSync, MenuSetting.auto_sync.instance)
        self.Bind(EVT_COUNT, self.OnCount)

    def SetStatusText(self, text):
        status_bar = wx.FindWindowById(9999).GetStatusBar()
        status_bar.SetStatusText(text)

    def OnSetAutoSync(self, e):
        dlg = AutoSyncDialog(self, title='title')
        dlg.CenterOnParent()
        dlg.ShowModal()

    def handle_restore_frame(self, event):
        # 弹窗提醒用户有待分解的记录
        if not self._restore_frame:
            return
        if getattr(event, 'auto', False):
            if self.frame.IsIconized():
                self.frame.Restore()
                self._restore_frame = False

            m = MenuView.stay_on_top.instance
            if not m.IsChecked():
                m.Check()
                self.frame.SetWindowStyle(self.frame.GetWindowStyle() | wx.STAY_ON_TOP)

    def run_task(self, task, *args):
        suffix= '_task'
        thd = self.frame.push_thread(task, *args)
        task_name = task.__name__ + suffix
        _task_thread = getattr(self, task_name, None)
        # 如果旧线程isAlive则返回, 否则stop, delete旧线程
        if _task_thread:
            if _task_thread.isAlive():
                return
            self.frame.delete_thread(_task_thread)
        setattr(self, task_name, thd)
        thd.start()

    def OnSyncData(self, event):
        self.run_task(self.run_sync, event)

    def run_sync(self, event):
        raise NotImplementedError()

    def OnToggleAutoSync(self, e):
        if e.IsChecked():
            thd = CountingThread(self, (1, 1))
            self._counting_thread = thd
            self.frame.push_thread(thd)
            thd.start()
        else:
            if not self._counting_thread.stopped():
                self._counting_thread.stop()

    def OnCount(self, e):
        _, s = e.GetValue()
        if s % 15 == 0:
            e.auto = True
            # self.frame.start_thread(self.OnSyncData, e)
            self.OnSyncData(e)


class WeChatReminderPanel(BasePanel):
    listctrl = Widget(listctrls.ReceivesListCtrl)

    def __init__(self, parent, log, name):
        super(WeChatReminderPanel, self).__init__(parent, log, name)
        self.list = self.listctrl.get_factory().create(self)
        self.do_layouts()
        self.do_binds()

    def do_binds(self):
        self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
        # for sync data
        MenuBar.menus.action.Bind(
            wx.EVT_MENU, self.OnSyncData, MenuAction.items.sync_data)
        # for auto-sync data
        MenuBar.menus.action.Bind(
            wx.EVT_MENU, self.OnToggleAutoSync, MenuAction.items.auto_sync)
        # for count event
        self.Bind(EVT_COUNT, self.OnCount)

    def do_layouts(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    # def __init__(self, parent, log, name):
    #     wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS, name=name)
    #     self.log = log
    #     self.listbook = parent
    #     self._restore_frame = False
    #
    #     tID = wx.NewId()
    #     self.frame = wx.FindWindowById(9999)
    #     # li = self.list.headings[0]
    #     # li.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
    #     # self.list.SetColumn(0, li)
    #     # self.list.SortListItems(0, True)
    #     #
    #
    #     # self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
    #     # self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
    #     # self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
    #     # self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
    #     # self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
    #     # self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
    #     # self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
    #     # self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
    #     # self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
    #     # self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)
    #     # self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
    #     # self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
    #
    #     # for wxMSW
    #     # self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
    #
    #     # for wxGTK
    #     # self.list.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

    def run_sync(self, event):
        '同步接单记录过程'
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
            msg = u'%s数据同步成功 at %s\n' % (self.Name, timestamp)
            self.SetStatusText(msg)
            wx.CallAfter(self.log.WriteText, msg)
            self.handle_restore_frame(event)
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


class TaskAssignPanel(BasePanel):
    listctrl = Widget(listctrls.TaskAssignListCtrl)

    def __init__(self, parent, log, name):
        super(TaskAssignPanel, self).__init__(parent, log, name)
        self.list = self.listctrl.get_factory().create(self)
        self.do_layouts()
        self.do_binds()

    def do_layouts(self):
        sizer = wx.BoxSizer()
        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def do_binds(self):
        # self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
        # for sync data
        MenuBar.menus.action.Bind(
            wx.EVT_MENU, self.OnSyncData, MenuAction.items.sync_pb)
        # for auto-sync data
        MenuBar.menus.action.Bind(
            wx.EVT_MENU, self.OnToggleAutoSync, MenuAction.items.auto_sync_pb)
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)

    def run_sync(self, event):
        '同步问题列表过程'
        self.frame.Refresh()
        self.SetStatusText(u"正在同步数据......")
        my = MinYuanClient(addr=MINGYUAN_TEST_ADDR)
        data = my.getProblemList(page_size=30)
        if data.get("rows"):
            rows = data["rows"]
            # datamap = {}
            # for idx, val in enumerate(rows):
            #     datamap[idx + 1] = tuple(val)
            datamap = {}
            for idx, d in enumerate(rows):
                for k, v in d.items():
                    datamap[idx + 1] = k
            self.itemDataMap = datamap
            # self.list.ClearAll()
            wx.CallAfter(self.list.AddRows, rows)
            timestamp = datetime.now().strftime("%Y-%m-%d %X")
            msg = u'%s数据同步成功 at %s\n' % (self.Name, timestamp)
            self.SetStatusText(msg)
            wx.CallAfter(self.log.WriteText, msg)
            self.handle_restore_frame(event)
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

    def OnDoubleClick(self, event):
        pass

    def ShowModalDialog(self, message, caption):
        dlg = wx.MessageDialog(self, message, caption, wx.CANCEL | wx.OK)
        if modal_ctx.set_modal(dlg):
            with modal_ctx as dlg:
                signal = dlg.ShowModal()
                dlg.Destroy()
            return signal

    def OnRightClick(self, event):
        def OnCopyTaskCode(e):
            self.SetStatusText('')
            if not self._taskcode:
                self.SetStatusText(u'任务编号复制失败')
                return
            dataObj = wx.TextDataObject()
            dataObj.SetText(self._taskcode)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(dataObj)
                wx.TheClipboard.Close()
                msg = u"任务编号 %s 复制成功\n" % self._taskcode
                self.SetStatusText(msg)
                self.log.WriteText(msg)

        def OnCopyProblemGUID(event):
            self.SetStatusText('')
            dataObj = wx.TextDataObject()
            dataObj.SetText(str(self._problem_guid))
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(dataObj)
                wx.TheClipboard.Close()
                msg = u"Problem GUID %s 复制成功\n" % self._problem_guid
                self.SetStatusText(msg)
                self.log.WriteText(msg)

        def transfer_task():
            msg = u'转任务开始，请稍候...\n'
            self.SetStatusText(msg)
            self.log.WriteText(msg)
            mingy = MinYuanClient(addr=MINGYUAN_TEST_ADDR)
            data = mingy.transferTask(self._problem_guid)
            msg = u'转任务失败!\n'
            if data.get('taskguid'):
                msg = u'转任务成功！任务编号 %s\n' % data["taskcode"]
            elif data.get('taskcode'):
                msg = u'转任务可能失败! 任务编号 %s\n' % data["taskcode"]
            self.SetStatusText(msg)
            wx.CallAfter(self.log.WriteText, msg)

        def assign_task():
            msg = u'指派任务开始，请稍候...\n'
            self.SetStatusText(msg)
            self.log.WriteText(msg)
            mingy = MinYuanClient(addr=MINGYUAN_TEST_ADDR)
            data = mingy.getTaskGUIDByTaskCode(self._taskcode)
            mingy.assignTask(data['taskguid'], self._problem_guid)

        def OnTransferTask(e):
            def run_transfer():
                transfer_task()
                self.run_sync(e)

            if wx.ID_OK != self.ShowModalDialog(u"是否对该条记录进行转任务操作？", u"询问"):
                return
            self.run_task(run_transfer)

        def OnAssignTask(e):
            def run_assign():
                assign_task()
                self.run_sync(e)

            if wx.ID_OK != self.ShowModalDialog(u"是否对该条记录进行指派任务操作？", u"询问"):
                return
            self.run_task(run_assign)

        def OnTransferAndAssign(e):
            def run_transfer_assign():
                transfer_task()
                assign_task()
                self.run_sync(e)

            if wx.ID_OK != self.ShowModalDialog(u'是否对该条记录进行转任务及指派操作？', u"询问"):
                return
            self.run_task(run_transfer_assign)

        menu = MenuTaskAssign.create()
        menu.Bind(wx.EVT_MENU, OnCopyTaskCode, menu.items.copy_taskcode)
        menu.Bind(wx.EVT_MENU, OnCopyProblemGUID, menu.items.copy_problem_guid)
        menu.Bind(wx.EVT_MENU, OnTransferTask, menu.items.transfer_task)
        menu.Bind(wx.EVT_MENU, OnAssignTask, menu.items.assign_task)
        menu.Bind(wx.EVT_MENU, OnTransferAndAssign, menu.items.transfer_and_assign)

        if self._status_text == u'已转任务':
            # 可以指派, 禁用其他
            menu.items.transfer_task.Enable(False)
            menu.items.transfer_and_assign.Enable(False)
        elif self._status_text == u'未处理':
            # 可以转任务，转任务并指派，禁用指派
            menu.items.assign_task.Enable(False)
        else:
            menu.items.assign_task.Enable(False)
            menu.items.transfer_task.Enable(False)
            menu.items.transfer_and_assign.Enable(False)
            # 禁用所有
        if not self._taskcode:
            menu.items.copy_taskcode.Enable(False)
        self.PopupMenu(menu)
        menu.Destroy()

    def get_problem_id(self, event):
        item = event.GetItem()
        data_key = self.list.GetItemData(item.GetId())
        return self.itemDataMap[data_key]

    def OnItemSelected(self, event):
        self._problem_guid = self.get_problem_id(event)
        self._status_text = self.list.getColumnText(event.GetIndex(), 0)
        self._taskcode = self.list.getColumnText(event.GetIndex(), 6)
