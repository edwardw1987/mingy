# coding:utf-8
import wx
from util import Widget, MenuBarFactory, MenuFactory


class MenuAction(MenuFactory, wx.Menu):
    sync_data = Widget(wx.MenuItem, text=u"同步接单记录\tCtrl+Alt+J", id=-1, pos=1)
    sp1 = Widget(wx.MenuItem, id=wx.ID_SEPARATOR, pos=2)
    auto_sync = Widget(wx.MenuItem, text=u"自动同步接单记录", id=-1, pos=3, kind=1)
    sp2 = Widget(wx.MenuItem, id=wx.ID_SEPARATOR, pos=4)
    close = Widget(wx.MenuItem, text=u"退出\tCtrl+Q", id=-1, pos=5)


class MenuSetting(MenuFactory, wx.Menu):
    auto_sync = Widget(wx.MenuItem, kind=1, text=u"自动同步", id=-1)


class MenuView(MenuFactory, wx.Menu):
    stay_on_top = Widget(id=-1, wx_factory=wx.MenuItem, text=u"窗口置顶", kind=1)


class MenuBar(MenuBarFactory, wx.MenuBar):
    action = Widget(MenuAction, pos=1, text=u'操作(&O)')
    view = Widget(MenuView, pos=2, text=u"查看(&V)")
    settings = Widget(MenuSetting, pos=3, text=u"设置(&S)")


def main():
    app = wx.App()
    fr = wx.Frame(None)

    fr.SetMenuBar(MenuBar.create())
    fr.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
