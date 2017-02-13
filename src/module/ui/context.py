# coding:utf-8

class ModalContext(object):
    """
    `Modal Dialog Context`
    Attribute `show` defaults to `False`
    if some modal dialog has been popup and shown,
    `with` the `modal_ctx` instance that will change `show` to be `True`,
    and hold it's value, till exit `modal_ctx` (user closed the modal dialog).
    """
    def __init__(self):
        self.show = False

    def __enter__(self, *args, **kw):
        self.show = True

    def __exit__(self, *args, **kw):
        self.show = False


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
