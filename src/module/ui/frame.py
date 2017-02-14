# coding:utf-8
import wx
import sys
from models import MenuBar, MenuView, MenuAction
from os import path
from listbook import TestLB
from event import StoppableThread
from types import InstanceType, FunctionType, UnboundMethodType

reload(sys)
sys.setdefaultencoding("utf-8")

basedir = path.dirname(__file__)


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, id=9999)
        self._threads = {}
        self.init_menubar()
        self.status_bar = self.CreateStatusBar()
        TestLB(self, -1, None)
        # ==========common apply==========
        self.SetTitle(u"明源自动化客户端")
        icon = path.join(basedir, '..\\..\\launcher\\rat_head.ico')
        size = (1200, 600)
        minsize = (400, 300)
        self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_ANY))
        self.SetSize(size)
        self.SetMinSize(minsize)
        self.Center()
        # ==========event==========
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def init_menubar(self):
        mb = MenuBar.create()
        MenuBar.view.instance.Bind(
            wx.EVT_MENU, self.OnSwitchTop, MenuView.stay_on_top.instance
        )
        MenuBar.action.instance.Bind(
            wx.EVT_MENU, self.OnClose, MenuAction.close.instance
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
        elif type(thread) is InstanceType:
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
