# coding:utf-8
import wx
from util import quick_menu_bar
import sys
from models import MenuB
reload(sys)
sys.setdefaultencoding("utf-8")


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self._threads = []
        self._create_menubar()
        self.status_bar = self.CreateStatusBar()

        # ==========common apply==========
        self.SetTitle(u"明源自动化客户端v%s")
        icon = 'launcher\\rat_head.ico'
        size = (1200, 600)
        minsize = (400, 300)
        self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_ANY))
        self.SetSize(size)
        self.SetMinSize(minsize)
        self.Center()
        # ==========event==========
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def _create_menubar(self):

        MenuB.stay_on_top.set_handler(self.OnSwitchTop)
        mb = quick_menu_bar(data)
        self.SetMenuBar(mb)

    def push_thread(self, thread):
        self._threads.append(thread)

    def get_threads(self):
        return self._threads

    def clear_threads(self):
        for thd in self.get_threads():
            if not thd.stopped():
                thd.stop()

    def OnClose(self, e):
        self.clear_threads()
        self.Destroy()

    def OnSwitchTop(self, e):
        if e.IsChecked():
            self.SetWindowStyle(self.GetWindowStyle() | wx.STAY_ON_TOP)
        else:
            self.SetWindowStyle(self.GetWindowStyle() ^ wx.STAY_ON_TOP)
