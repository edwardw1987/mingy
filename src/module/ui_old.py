# coding:utf-8

import json
import os
import tempfile
from collections import OrderedDict
from datetime import datetime

import requests
import wx
import wx.lib.mixins.listctrl as listmix

import githubapi
import images
from event import EVT_COUNT, CountingThread, StoppableThread
from mingy.src.module.ui import keyword
from mingy.src.module.ui.util import quick_menu_bar

# --------------------

VERSION = '0.7'
# --------------------
BaseDir = os.path.dirname(__file__)


def path_join(*path):
    return os.path.join(BaseDir, *path)


def get_const():
    constfilepath = path_join("const.json")
    constfilepy = path_join("const.py")
    try:
        import const
    except ImportError:
        jsondict = json.load(open(constfilepath))
        return jsondict
        with open(constfilepy, 'w') as outf:
            outf.write("json=%s" % jsondict)
        from . import const
    return const.json


def get_current_time():
    dt = datetime.now()
    return dt.strftime("%Y-%m-%d %X")


class ModalContext(object):
    def __init__(self):
        self.show = False

    def __enter__(self, *args, **kw):
        self.show = True

    def __exit__(self, *args, **kw):
        self.show = False


class RestartContext(object):
    def __init__(self):
        self._set = False

    def is_set(self):
        return self._set

    def __enter__(self, *args, **kw):
        pass

    def set(self):
        self._set = True

    def __exit__(self, *args, **kw):
        self._set = False


restart_ctx = RestartContext()
modal_context = ModalContext()


class ReceiveListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def construct(self):
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def AddRows(self, data_list):
        # self.DeleteAllColumns()
        self.DeleteAllItems()
        popUpWin = False
        # for pos, heading in enumerate(get_const()["headings"]):
        #     self.InsertColumn(pos, heading, format=wx.LIST_FORMAT_LEFT)
        for key, row in enumerate(data_list):
            count = self.GetItemCount()
            pos = self.InsertStringItem(count, row[0])
            # add values in the other columns on the same row
            for idx, val in enumerate(row[1:]):
                self.SetStringItem(pos, idx + 1, val)
            self.SetItemData(pos, key + 1)
            const_resolveStatus = get_const()["resovle_status"]
            listitem = self.GetItem(pos)

            if row[-1] == const_resolveStatus["closed"]:
                listitem.SetTextColour(wx.NamedColour("GRAY"))
            elif row[-1] == const_resolveStatus["unresolved"]:
                listitem.SetTextColour(wx.NamedColour("RED"))
                listitem.SetFont(listitem.GetFont().Bold())
                # popUpWin = row[2] in get_const()["resource"].values()
                popUpWin = True
            elif row[-1] == const_resolveStatus["resolved"]:
                listitem.SetTextColour(wx.NamedColour("BLUE"))
                listitem.SetFont(listitem.GetFont().Bold())
            self.SetItem(listitem)
        # self.addCache(data_list)
        return popUpWin

    initRows = AddRows

    def AdaptWidth(self, headings_num, proportions):
        num = sum(proportions)
        _w = self.GetSize()[0] / float(num)
        for i in range(headings_num):
            w = _w * proportions[i]
            self.SetColumnWidth(i, w)


class Frame(wx.Frame, listmix.ColumnSorterMixin):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.restart_app = False
        self._threads = []
        # self._initListCtrl()
        self._initMenuBar()
        # self._initToolbar()
        self.statusbar = self.CreateStatusBar()
        # ----- layout -----
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(self.LC, 1, wx.EXPAND | wx.ALL)
        # listmix.ColumnSorterMixin.__init__(self, self.columnNum)
        # self.SetSizer(sizer)
        # self.Layout()
        # ----------
        self.Bind(EVT_COUNT, self.OnCount)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.Center()
        self.SetTitle(self.getTitle())
        icon = path_join('../launcher/rat_head.ico')
        size = (1200, 600)
        minsize = (400, 300)
        self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_ANY))
        self.SetSize(size)
        self.SetMinSize(minsize)

    @property
    def const(self):
        return get_const()

    @property
    def columnNum(self):
        return len(self.const["headings"])




    def _SyncReceiveList(self, *args, **kwargs):
        event = args[0]
        my = MinYuanClient(addr=MINGYUAN_OFFICIAL_ADDR)
        data = my.getJdjl(page_size=30)
        if "Jdjl" in data:
            rl = data["Jdjl"]
            signal = self.LC.AddRows(rl)
            if signal and getattr(event, 'auto', False):
                # ----- 弹窗提醒用户有待分解的记录
                if self.IsIconized():
                    self.Restore()
                m = self.FindItemInMenuBar(menuId=777)
                if not m.IsChecked():
                    m.Check()
                    self.SetWindowStyle(self.GetWindowStyle() | wx.STAY_ON_TOP)
                    # self.SetWindowStyle(self.GetWindowStyle() ^ wx.STAY_ON_TOP)
            datamap = {}
            for idx, val in enumerate(rl):
                datamap[idx + 1] = tuple(val)
            self.itemDataMap = datamap

            self.LC.Hide()
            self.LC.AdaptWidth(self.columnNum, [1.5, 3, 1, 2, 0.5, 1, 1])
            self.LC.Show()
            self.statusbar.SetStatusText(self.const["sync_end_msg"] + ' at ' + get_current_time())
        else:
            self.statusbar.SetStatusText('')
            if modal_context.show is False:
                with modal_context:
                    dlg = wx.MessageDialog(self,
                                           self.const["sync_error_msg"],
                                           self.const["sync_error_title"],
                                           wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()

    def OnSyncData(self, e):
        self.statusbar.SetStatusText(self.const["sync_start_msg"])
        wx.CallAfter(self._SyncReceiveList, e)

    def _initToolbar(self):
        self.tb = tb = self.CreateToolBar()
        tsize = (24, 24)
        new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, tsize)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        copy_bmp = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, tsize)
        paste_bmp = wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, tsize)

        tb.SetToolBitmapSize(tsize)

        # tb.AddSimpleTool(10, new_bmp, "New", "Long help for 'New'")
        tb.AddLabelTool(10, "New", new_bmp, shortHelp="New", longHelp="Long help for 'New'")
        self.Bind(wx.EVT_TOOL, self.OnSyncData, id=10)
        # self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=10)

        # tb.AddSimpleTool(20, open_bmp, "Open", "Long help for 'Open'")
        tb.AddLabelTool(20, "Open", open_bmp, shortHelp="Open", longHelp="Long help for 'Open'")
        # self.Bind(wx.EVT_TOOL, self.OnToolClick, id=20)
        # self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=20)

        tb.AddSeparator()
        tb.AddSimpleTool(30, copy_bmp, "Copy", "Long help for 'Copy'")
        # self.Bind(wx.EVT_TOOL, self.OnToolClick, id=30)
        # self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=30)

        tb.AddSimpleTool(40, paste_bmp, "Paste", "Long help for 'Paste'")
        # self.Bind(wx.EVT_TOOL, self.OnToolClick, id=40)
        # self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=40)

        tb.AddSeparator()

        # tool = tb.AddCheckTool(50, images.Tog1.GetBitmap(), shortHelp="Toggle this")
        tool = tb.AddCheckLabelTool(50, "Checkable", images.Tog1.GetBitmap(),
                                    shortHelp="Toggle this")
        # self.Bind(wx.EVT_TOOL, self.OnToolClick, id=50)

        # self.Bind(wx.EVT_TOOL_ENTER, self.OnToolEnter)
        # self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick)  # Match all
        # self.Bind(wx.EVT_TIMER, self.OnClearSB)

        tb.AddSeparator()
        cbID = wx.NewId()

        tb.AddControl(
            wx.ComboBox(
                tb, cbID, "", choices=["", "This", "is a", "wx.ComboBox"],
                size=(150, -1), style=wx.CB_DROPDOWN
            ))
        # self.Bind(wx.EVT_COMBOBOX, self.OnCombo, id=cbID)

        tb.AddStretchableSpace()
        # search = TestSearchCtrl(tb, size=(150, -1), doSearch=self.DoSearch)
        # tb.AddControl(search)

        # Final thing to do for a toolbar is call the Realize() method. This
        # causes it to render (more or less, that is).
        tb.Realize()

    def OnAdd(self, evt):
        pass

    def OnQuit(self, evt):
        if getattr(self, "syncThd", None) and \
                not self.syncThd.stopped():
            self.syncThd.stop()
        for thd in self.get_threads():
            if not thd.stopped():
                thd.stop()
        self.Destroy()



    def GetListCtrl(self):
        return self.LC

    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

    def OnCount(self, e):
        _, s = e.GetValue()
        print s
        if s % 15 == 0:
            e.auto = True
            self.OnSyncData(e)


    def OnToggleAutoSync(self, e):
        if e.IsChecked():
            thd = CountingThread(self, (1, 1))
            self.syncThd = thd
            thd.start()
        else:
            if not self.syncThd.stopped():
                self.syncThd.stop()

    def popUpUpdatePD(self, url):
        resp = requests.get(url, stream=True)
        clen = int(resp.headers["Content-Length"])
        size = 1024
        max = int(float(clen) / size)
        dlg = wx.ProgressDialog(self.const["update_title"],
                                "updating...",
                                maximum=max,
                                parent=None,
                                style=0
                                      | wx.PD_APP_MODAL
                                      # | wx.PD_CAN_ABORT
                                      # | wx.PD_CAN_SKIP
                                      # | wx.PD_ELAPSED_TIME
                                      | wx.PD_ESTIMATED_TIME
                                      | wx.PD_REMAINING_TIME
                                      | wx.PD_AUTO_HIDE
                                )
        count = 0
        keepGoing = True
        tf = tempfile.TemporaryFile(suffix=".zip")
        for _b in resp.iter_content(chunk_size=size):
            tf.write(_b)
            count += 1
            # wx.MilliSleep(250)
            # wx.Yield()
            if keepGoing and count <= max:
                (keepGoing, skip) = dlg.Update(count,
                                               '%s/%sk' % (count, max))
                # if not (keepGoing and count < max):
        githubapi.replaceSourceWith(tf, path_join('.'))
        dlg.Destroy()

    def asyncUpdate(self):
        thd = StoppableThread(target=self._doUpdate)
        self.push_thread(thd)
        thd.start()

    def _doUpdate(self):
        """
            return int
                0 update successfully
                1 update canceled or no need to update
                -1 connection error
            The program has to be restarted once the source code files updated.

        """
        lr = githubapi.getLatestRelease()
        if 'errMsg' in lr:
            dlg = wx.MessageDialog(None,
                                   self.const["sync_error_msg"],
                                   self.const["sync_error_title"],
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.Destroy()
            return -1
        lr_version = lr.get("tag_name", "0.3")
        if lr_version == VERSION:
            return 1
        dlg = wx.MessageDialog(None,
                               self.const["update_msg"] % lr_version,
                               self.const["update_title"],
                               wx.CANCEL | wx.ICON_INFORMATION)
        if wx.ID_OK == dlg.ShowModal():
            dlg.Destroy()
            self.Hide()
            self.popUpUpdatePD(lr["zipball_url"])

            restart_ctx.set()
            self.Destroy()
            return 0
        dlg.Destroy()
        return 1

    def getTitle(self):
        return self.const["weixin_demo_title"] % VERSION


class Panel01(wx.Panel):
    def __init__(self, parent):
        super(wx.Panel, self).__init__(parent)
        self.parent = parent
        self._initListCtrl()

    def _initListCtrl(self):
        const_headings = self.parent.const["headings"]
        self.LC = ReceiveListCtrl(self,
                                  style=wx.LC_REPORT,
                                  headings=const_headings,
                                  # columnFormat=wx.LIST_FORMAT_CENTER,
                                  fgcolor='#f40',
                                  )
        # self.LC.SetAutoLayout(True)

        self.il = wx.ImageList(16, 16)

        # self.idx1 = self.il.Add(images.Smiles.GetBitmap())
        self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
        self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())
        self.LC.SetImageList(self.il, wx.IMAGE_LIST_SMALL)


class Panel02(wx.Panel):
    pass


class ColoredPanel(wx.Window):
    def __init__(self, parent, color):
        wx.Window.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(color)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)


class TestLB(wx.Listbook):
    def __init__(self, parent, id, log):
        wx.Listbook.__init__(self, parent, id, style=
        wx.BK_DEFAULT
                             # wx.BK_TOP
                             # wx.BK_BOTTOM
                             # wx.BK_LEFT
                             # wx.BK_RIGHT
                             )
        self.log = log

        # make an image list using the LBXX images
        il = wx.ImageList(32, 32)
        for x in range(12):
            obj = getattr(images, 'LB%02d' % (x + 1))
            bmp = obj.GetBitmap()
            il.Add(bmp)
        self.AssignImageList(il)

        # Now make a bunch of panels for the list book
        first = True
        imID = 0
        for colour in colourList:
            win = self.makeColorPanel(colour)
            self.AddPage(win, colour, imageId=imID)
            imID += 1
            if imID == il.GetImageCount(): imID = 0
            if first:
                st = wx.StaticText(win.win, -1,
                                   "You can put nearly any type of window here,\n"
                                   "and the list can be on any side of the Listbook",
                                   wx.Point(10, 10))
                first = False

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    def makeColorPanel(self, color):
        p = wx.Panel(self, -1)
        win = ColoredPanel(p, color)
        p.win = win

        def OnCPSize(evt, win=win):
            win.SetPosition((0, 0))
            win.SetSize(evt.GetSize())

        p.Bind(wx.EVT_SIZE, OnCPSize)
        return p

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        self.log.write('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        self.log.write('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()
