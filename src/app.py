# coding:utf-8
import wx
import ui
from countdown import resource

class MingYuanApp(wx.App):
    def OnInit(self):
        fr = ui.Frame(
            None,
            icon=resource.rat_head_original.getIcon(),
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