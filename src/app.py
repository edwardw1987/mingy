# coding:utf-8
import threading

import wx

import githubapi
import ui
from launcher import launcher

GITHUB_OWNER = 'edwardw1987'
GITHUB_REPO = 'mingy'
# rest.launch_server()
VERSION = '0.3'
restart_app = False


class MingYuanApp(wx.App):
    const = ui.get_const()

    def asyncUpdate(self):
        t = threading.Thread(target=self._doUpdate)
        t.setDaemon(True)
        t.start()

    def _doUpdate(self):
        """
            return int
                0 update successfully
                1 update canceled or no need to update
                -1 connection error
            The program has to be restarted once the source code files updated.

        """
        lr = githubapi.getLatestRelease(GITHUB_OWNER, GITHUB_REPO)
        if 'errMsg' in lr:
            dlg = wx.MessageDialog(None,
                                   self.const["sync_error_msg"],
                                   self.const["sync_error_title"],
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.fr.Destroy()
            return -1
        lr_version = lr.get("tag_name", "0.3")
        if lr_version == VERSION:
            return 1
        dlg = wx.MessageDialog(None,
                               self.const["update_msg"] % lr_version,
                               self.const["update_title"],
                               wx.CANCEL | wx.ICON_INFORMATION)
        if wx.ID_OK == dlg.ShowModal():
            dlg.Destroy()
            self.fr.Hide()
            self.fr.popUpUpdatePD(lr["zipball_url"])
            global restart_app
            restart_app = True
            self.fr.Destroy()
            return 0
        dlg.Destroy()
        return 1

    def OnInit(self):
        self.fr = ui.Frame(
            None,
            title=self.const["weixin_demo_title"] % VERSION,
            icon=ui.path_join('launcher/rat_head.ico'),
            size=(1200, 600),
            minsize=(400, 300),
        )
        self.fr.Show()
        return True


def main():
    app = MingYuanApp()
    app.asyncUpdate()
    app.MainLoop()
    if restart_app:
        launcher.main()


if __name__ == "__main__":
    main()
