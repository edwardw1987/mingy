# coding:utf-8
import wx
import sys
from menus import MenuBar, MenuView, MenuAction
from os import path
from listbook import TestLB
from event import StoppableThread
from types import FunctionType, UnboundMethodType
from textctrls import LogTextCtrl

reload(sys)
sys.setdefaultencoding("utf-8")

basedir = path.dirname(__file__)


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, id=9999)
        self._threads = {}
        self.init_menubar()
        self.status_bar = self.CreateStatusBar()
        # ==========common apply==========
        self.SetTitle(u"明源自动化客户端")
        icon = path.join(basedir, '..\\..\\launcher\\rat_head.ico')
        size = (1200, 600)
        minsize = (400, 300)
        self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_ANY))
        self.SetSize(size)
        self.SetMinSize(minsize)
        self.Center()

        self._layout()
        # ==========event==========
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def _layout(self):
        splitter = wx.SplitterWindow(self)

        sty = wx.BORDER_SUNKEN

        p1 = wx.Window(splitter, style=sty)

        p2 = wx.Window(splitter, style=sty)

        splitter.SetMinimumPaneSize(20)
        splitter.SplitHorizontally(p1, p2, -100)

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.log = LogTextCtrl(p2)
        listbook = TestLB(p1, -1, None)
        sizer1.Add(listbook, 1, wx.EXPAND)
        sizer2.Add(self.log, 1, wx.EXPAND)
        p1.SetSizer(sizer1)
        p2.SetSizer(sizer2)

    def init_menubar(self):
        mb = MenuBar.create()
        MenuBar.menus.view.Bind(
            wx.EVT_MENU, self.OnSwitchTop, MenuView.stay_on_top.instance
        )
        MenuBar.menus.action.Bind(
            wx.EVT_MENU, self.OnClose, MenuAction.items.close
        )
        self.SetMenuBar(mb)

    def _handle_thread(self, thread, *args, **kwargs):
        """
        :param thread:
        accepts `callable`, or instances of subclass derived from `StoppableThread`
        :param args:
        :param kwargs:
        :return:
        """
        if type(thread) in (FunctionType, UnboundMethodType):
            thread = StoppableThread(target=thread, args=args, kwargs=kwargs)
        elif hasattr(thread, '__class__'):
            t_cls = thread.__class__
            if not issubclass(t_cls, StoppableThread):
                raise TypeError("'%' is not dervied from `StoppableThread`" % type(t_cls))
        else:
            raise TypeError("Invalid type '%s'" % type(thread))
        return thread

    def push_thread(self, thread, *args, **kwargs):
        handled_thread = self._handle_thread(thread, *args, **kwargs)
        self._threads[handled_thread.getName()] = handled_thread
        return handled_thread

    def pop_thread(self, thread):
        return self._threads.pop(thread.getName(), None)

    def delete_thread(self, thread):
        thread_name = thread.getName()
        if thread_name in self._threads:
            del self._threads[thread_name]

    def iter_threads(self):
        return self._threads.itervalues()

    def clear_threads(self):
        for thd in self.iter_threads():
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
