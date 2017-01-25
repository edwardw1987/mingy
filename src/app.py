# coding:utf-8
import threading

import wx
import ui
from launcher import launcher


restart_app = False


class MingYuanApp(wx.App):

    def OnInit(self):
        self.fr = ui.Frame(
            None,
            icon=ui.path_join('launcher/rat_head.ico'),
            size=(1200, 600),
            minsize=(400, 300),
        )
        self.fr.Show()
        return True



def main():
    app = MingYuanApp()
    app.fr.asyncUpdate()
    app.MainLoop()
    if restart_app:
        launcher.main()


if __name__ == "__main__":
    main()
