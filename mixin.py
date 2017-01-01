# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2016-12-30 10:18:02
# @Last Modified by:   wangwh8
# @Last Modified time: 2016-12-30 13:56:55
import wx


class ConstructorMixin(object):

    def construct_icon(self):
        icon = self.get_arg('icon')
        if not icon:
            return
        if isinstance(icon, basestring):
            icon = wx.Icon(icon, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def construct_fgcolor(self):
        fgcolor = self.get_arg('fgcolor')
        if not fgcolor:
            return
        self.SetForegroundColour(fgcolor)

    def construct_headings(self):
        headings = self.get_arg("headings")
        columnFormat = self.get_arg("columnFormat")
        if not headings:
            return
        elif headings == -1:
            self.InsertColumn(0, "", format=wx.LIST_FORMAT_LEFT)
            return
        for pos, heading in enumerate(headings):
            fmt = columnFormat or wx.LIST_FORMAT_LEFT
            self.InsertColumn(pos, heading, format=fmt)

    def construct_minsize(self):
        minsize = self.get_arg("minsize")
        if not minsize:
            return
        self.SetMinSize(minsize)

    def get_arg(self, key):
        return self._args.get(key)

    def _init_args(self, **kw):
        self._args = {}
        keys = {
            'icon',
            'fgcolor',
            'headings',
            'columnFormat',
            'minsize',
            'enable',
            'handler',
            'fgsCtrls',
            'fgsCols',
            'fgsGrowCols',
        }
        for k in keys:
            v = kw.pop(k, None)
            if v:
                self._args[k] = v
        return kw

    def _construct(self):
        self.construct_icon()
        self.construct_fgcolor()
        self.construct_headings()
        self.construct_minsize()
        cst = getattr(self, 'construct', None)
        if cst: cst()

def constructor(cls):
    class ret(ConstructorMixin, cls):
        def __init__(self, *args, **kwargs):
            kw = self._init_args(**kwargs)
            super(cls, self).__init__(*args, **kw)
            self._construct()
    return ret