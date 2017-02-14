# coding:utf-8
import wx

class LogTextCtrl(wx.TextCtrl):
    def __init__(self, parent):

        wx.TextCtrl.__init__(self, parent, style=wx.TE_READONLY
                                                | wx.TE_MULTILINE
                             )
