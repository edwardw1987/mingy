# coding:utf-8
import wx
import ui
import rest
import githubapi
import subprocess
from launcher import launcher

GITHUB_OWNER = 'edwardw1987'
GITHUB_REPO = 'mingy'
# rest.launch_server()
VERSION = '0.2'
restart_app = False

class MingYuanApp(wx.App):
    const = ui.get_const()
    def doUpdate(self):
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
            # max = 80
            # dlg = wx.ProgressDialog(self.const["update_title"],
            #                         "updating...",
            #                         maximum=max,
            #                         parent=None,
            #                         style=0
            #                         | wx.PD_APP_MODAL
            #                         #| wx.PD_CAN_ABORT
            #                         #| wx.PD_CAN_SKIP
            #                         #| wx.PD_ELAPSED_TIME
            #                         | wx.PD_ESTIMATED_TIME
            #                         | wx.PD_REMAINING_TIME
            #                         | wx.PD_AUTO_HIDE
            #                         )

            # keepGoing = True
            # count = 0

            # while keepGoing and count < max:
            #     count += 1
            #     wx.MilliSleep(250)
            #     wx.Yield()

            #     if count >= max / 2:
            #         (keepGoing, skip) = dlg.Update(count, "Half-time!")
            #     else:
            #         (keepGoing, skip) = dlg.Update(count)

            # dlg.Destroy()
            global restart_app
            restart_app = True
            return 0
            # githubapi.updateByZipball(lr["zipball_url"])
        dlg.Destroy()
        return 1

    def OnInit(self):
        signal = self.doUpdate()
        if signal == 1:
            fr = ui.Frame(
                None,
                title=self.const["weixin_demo_title"] % VERSION,
                icon=ui.path_join('launcher/rat_head.ico'),
                size=(1200, 600),
                minsize=(400, 300),
            )
            fr.Show()
        return True


def main():
    app = MingYuanApp()
    app.MainLoop()
    if restart_app:
        launcher.main()

if __name__ == "__main__":
    main()
