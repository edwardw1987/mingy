# coding:utf-8

class ModalContext(object):
    """
    with the `modal_ctx` instance,
    we can block dialogs if one is shown.
    > dlg = wx.MessageDialog(...)
    > if modal_ctx.set_modal(dlg):
          with modal_ctx as dlg:
             dlg.ShowModal()
             dlg.Destory()
    """

    def __init__(self):
        self._show = False
        self._modal = None

    def __enter__(self, *args, **kw):
        self._show = True
        return self._modal

    def __exit__(self, *args, **kw):
        self._show = False
        self._modal = None

    def set_modal(self, modal):
        if self._show:
            return
        self._modal = modal
        return modal


class RestartContext(object):
    def __init__(self):
        self._set = False

    def is_set(self):
        return self._set

    def __enter__(self, *args, **kw):
        pass

    def set(self):
        self._set = True

    def __exit__(self, *args, **kw):
        self._set = False


restart_ctx = RestartContext()
modal_ctx = ModalContext()
