# coding:utf-8
import wx
from util import Widget, WidgetArray, MenuBarFactory, MenuFactory


class MenuAction(MenuFactory):
    items = WidgetArray(
        Widget(wx.MenuItem, text=u"同步接单记录\tCtrl+Alt+J", id=-1, widget_name="sync_data"),
        Widget(wx.MenuItem, text=u"同步问题列表\tCtrl+Alt+K", id=-1, widget_name="sync_pb"),
        Widget(wx.MenuItem, id=wx.ID_SEPARATOR),
        Widget(wx.MenuItem, text=u"自动同步接单记录", id=-1, kind=1, widget_name="auto_sync"),
        Widget(wx.MenuItem, text=u"自动同步问题列表", id=-1, kind=1, widget_name="auto_sync_pb"),
        Widget(wx.MenuItem, id=wx.ID_SEPARATOR),
        Widget(wx.MenuItem, text=u"退出\tCtrl+Q", id=-1, widget_name="close")
    )


class MenuSetting(MenuFactory):
    auto_sync = Widget(wx.MenuItem, text=u"自动同步", id=-1)


class MenuView(MenuFactory):
    stay_on_top = Widget(id=-1, wx_factory=wx.MenuItem, text=u"窗口置顶", kind=1)


class MenuTaskAssign(MenuFactory):
    items = WidgetArray(
        Widget(wx.MenuItem, id=-1, text=u"复制任务编号", widget_name="copy_taskcode"),
        Widget(wx.MenuItem, id=wx.ID_SEPARATOR),
        Widget(wx.MenuItem, id=-1, text=u"转任务并指派", widget_name="transfer_and_assign"),
        Widget(wx.MenuItem, id=-1, text=u"指派任务", widget_name="assign_task"),
        Widget(wx.MenuItem, id=-1, text=u"转任务", widget_name="transfer_task"),
        Widget(wx.MenuItem, id=wx.ID_SEPARATOR),
        Widget(wx.MenuItem, id=-1, text=u'Copy ProblemGUID', widget_name='copy_problem_guid')
    )


# ------------------------------
class MenuBar(MenuBarFactory):
    menus = WidgetArray(
        Widget(MenuAction, text=u'操作(&O)', widget_name="action"),
        Widget(MenuView, text=u"查看(&V)", widget_name="view"),
        Widget(MenuSetting, text=u"设置(&S)", widget_name="settings"),
    )
