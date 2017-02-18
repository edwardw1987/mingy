# coding:utf-8

import wx

from module.ui.frame import Frame
from module.utils import test_version


class MingYuanApp(wx.App):
    def OnInit(self):
        self.fr = Frame()
        self.fr.Show()
        return True


def main():
    app = MingYuanApp()
    # app.fr.asyncUpdate()
    app.MainLoop()
    # if ui.restart_ctx.is_set():
    #     with ui.restart_ctx:
    #         launcher.main()


if __name__ == "__main__":
    main()
