# coding:utf-8
import wx
import images
import panels

sidebar_list = [u"微信提醒", u"派单",
                ]


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
        for colour in sidebar_list:
            if imID == 0:
                win = self.makeColorPanel(colour, panel=panels.TestListCtrlPanel(self, -1))
            else:
                win = self.makeColorPanel(colour)
            self.AddPage(win, colour, imageId=imID)
            imID += 1
            if imID == il.GetImageCount(): imID = 0
            # if first:
            #     st = wx.StaticText(win.win, -1,
            #                        "You can put nearly any type of window here,\n"
            #                        "and the list can be on any side of the Listbook",
            #                        wx.Point(10, 10))
            #     first = False

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    def makeColorPanel(self, color, panel=None):
        p = panel
        if p is None:
            p = wx.Panel(self, -1)
        win = panels.ColoredPanel(p, color)
        p.win = win

        def OnCPSize(evt, win=win):
            win.SetPosition((0, 0))
            win.SetSize(evt.GetSize())
            wins = wx.FindWindowById(evt.GetId())
            if hasattr(wins, 'list'):
                wins.list.SetSize(evt.GetSize())

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

