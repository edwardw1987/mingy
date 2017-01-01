# coding:utf-8
import wx
import ui

class MingYuanApp(wx.App):
    def OnInit(self):
        fr = ui.Frame(
            None,
            icon="countdown/rat_head.ico",
            size=(1200, 600),
            minsize=(400, 300),
        )
        fr.Show()
        return True
def main():
    app = MingYuanApp()
    app.MainLoop()
if __name__ == "__main__":
    main()