# coding:utf-8
import wx
from util import Widget, WidgetArray, MenuBarFactory, MenuFactory


class MenuAction(MenuFactory, wx.Menu):
    items = WidgetArray(
        Widget(wx.MenuItem, text=u"同步接单记录\tCtrl+Alt+J", id=-1, name="sync_data"),
        Widget(wx.MenuItem, id=wx.ID_SEPARATOR),
        Widget(wx.MenuItem, text=u"自动同步接单记录", id=-1, kind=1, name="auto_sync"),
        Widget(wx.MenuItem, id=wx.ID_SEPARATOR),
        Widget(wx.MenuItem, text=u"退出\tCtrl+Q", id=-1, name="close")
    )

class MenuSetting(MenuFactory, wx.Menu):
    auto_sync = Widget(wx.MenuItem, text=u"自动同步", id=-1)


class MenuView(MenuFactory, wx.Menu):
    stay_on_top = Widget(id=-1, wx_factory=wx.MenuItem, text=u"窗口置顶", kind=1)


class MenuBar(MenuBarFactory, wx.MenuBar):
    menus = WidgetArray(
        Widget(MenuAction, text=u'操作(&O)', name="action"),
        Widget(MenuView, text=u"查看(&V)", name="view"),
        Widget(MenuSetting, text=u"设置(&S)", name="settings"),
    )

def main():
    app = wx.App()
    fr = wx.Frame(None)

    fr.SetMenuBar(MenuBar.create())
    fr.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
