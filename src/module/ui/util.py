# coding:utf-8
'''
All util functions for quick building of UI components
'''
import re
import time


def get_func_doc_args(fn):
    pattern = re.compile('(\w+)=\w+')
    return set(pattern.findall(fn.__doc__))


class Widget(object):
    def __init__(self, wx_factory, pos=-1, **kwargs):
        super(Widget, self).__init__()
        self._pos = pos
        self._handler = None
        self._factory = wx_factory
        self._init_args = {}
        self._attr = {}
        self.handle_args(kwargs)

    def set_handler(self, handler):
        self._handler = handler

    def get_handler(self):
        return self._handler

    def get(self, attr_name):
        return self._attr.get(attr_name)

    def get_instance(self):
        return self._instance

    def get_factory(self):
        return self._factory

    def create(self):
        self._instance = self._factory(**self._init_args)
        return self._instance

    def handle_args(self, args):
        _init_args = get_func_doc_args(self._factory.__init__)
        for k, v in args.items():
            if k in _init_args:
                self._init_args[k] = v
            else:
                self._attr[k] = v


# ------------------------------------
class Factory(object):
    _pos = 0

    @classmethod
    def create(cls, *arg, **kwargs):
        raise NotImplementedError()

    @classmethod
    def iter_widegts(cls):
        ws = {}
        for key in dir(cls):
            if not key.startswith('_'):
                val = getattr(cls, key)
                if issubclass(val.__class__, Widget):
                    ws[key] = val

        return sorted(ws.values(), key=lambda x: x._pos)

    @classmethod
    def handle_widget(cls, widget, *args, **kwargs):
        factory = widget.get_factory()
        if issubclass(factory, Factory):
            factory.create(widget, *args, **kwargs)


class MenuFactory(Factory):
    @classmethod
    def create(cls, widget):
        menu = widget.get_instance()
        for w in cls.iter_widegts():
            menu.AppendItem(w.create())
