# coding:utf-8
import wx
from util import Factory, Widget, MenuFactory


class MenuAction(MenuFactory, wx.Menu):
    sync_data = Widget(wx.MenuItem, text=u"同步数据\tCtrl+S", id=-1, pos=1)
    sp1 = Widget(wx.MenuItem, id=wx.ID_SEPARATOR, pos=2)
    auto_sync = Widget(wx.MenuItem, text=u"自动同步", id=-1, pos=3, kind=1)
    sp2 = Widget(wx.MenuItem, id=wx.ID_SEPARATOR, pos=4)
    close = Widget(wx.MenuItem, text=u"退出\tCtrl+Q", id=-1, pos=5)


class MenuSetting(MenuFactory, wx.Menu):
    auto_sync = Widget(wx.MenuItem, kind=1, text=u"自动同步", id=-1)


class MenuView(MenuFactory, wx.Menu):
    auto_sync = Widget(id=-1, wx_factory=wx.MenuItem, text=u"自动同步", kind=1)


class MenuBar(Factory, wx.MenuBar):
    action = Widget(MenuAction, pos=1, text=u'操作(&O)')
    view = Widget(MenuView, pos=2, text=u"查看(&V)")
    settings = Widget(MenuSetting, pos=3, text=u"设置(&S)")

    @classmethod
    def create(cls):
        menu_bar = cls()
        for widget in cls.iter_widegts():
            menu = widget.create()
            cls.handle_widget(widget)
            menu_bar.Append(menu, widget.get('text'))
        return menu_bar


def main():
    app = wx.App()
    fr = wx.Frame(None)

    fr.SetMenuBar(MenuBar.create())
    fr.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
