# coding:utf-8
import wx


class AutoSyncDialog(wx.Dialog):
    pass


class BatchTaskDialog(wx.Dialog):
    def __init__(self, parent, title, data):
        wx.Dialog.__init__(self, parent, title=title)
        self.parent = parent
        self._data = data
        self.do_layouts()
        self.do_binds()
        self.update()

    def do_layouts(self):
        self.lb = lb = wx.CheckListBox(self, -1, (80, 50), wx.DefaultSize, self._data)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(lb, 7, wx.EXPAND)

        self.cb = cb = wx.CheckBox(self, -1, u'全选')
        main_sizer.Add(cb, 1, wx.EXPAND | wx.LEFT, 5)

        btn_sizer = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(self, id=wx.ID_OK, label=u'确定')
        ok_btn.Enable(False)
        self.ok_btn = ok_btn
        cancel_btn = wx.Button(self, id=wx.ID_CANCEL, label=u'取消')
        btn_sizer.AddButton(ok_btn, )
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()  # important!!

        main_sizer.AddSizer(btn_sizer, 2, wx.ALIGN_RIGHT)
        self.SetSizer(main_sizer)
        self.Fit()

    def do_binds(self):
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleSelectAll, self.cb)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnToggleSelectLB, self.lb)

    def update(self):
        raw_title = self.GetTitle()
        frags = raw_title.split()
        suffix = '%d/%d' % self.count_items()
        if len(frags) == 1:
            frags.append(suffix)
        elif len(frags) == 2:
            frags[-1] = suffix
        new_title = ' '.join(frags)
        self.SetTitle(new_title)
    #     toggle`ok` button status
        self.ok_btn.Enable(len(self.get_checked_items()) > 0)

    def get_items_count(self):
        return len(self.lb.GetItems())

    def get_checked_items(self):
        _checked = []
        count = self.get_items_count()
        for i in range(count):
            if self.lb.IsChecked(i):
                _checked.append(i)
        return _checked

    def count_items(self):
        '''

        :return: (checked_items_count, all_items_count)
        '''
        return len(self.get_checked_items()), self.get_items_count()

    def OnToggleSelectAll(self, e):
        items_count = self.get_items_count()
        if e.IsChecked():
            for i in range(items_count):
                self.lb.Check(i)
        else:
            for i in range(items_count):
                self.lb.Check(i, check=False)
        self.update()

    def OnToggleSelectLB(self, event):
        index = event.GetSelection()
        if self.lb.IsChecked(index):
            self.lb.SetSelection(index)  # so that (un)checking also selects (moves the highlight)
        self.update()
