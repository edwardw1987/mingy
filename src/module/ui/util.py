# coding:utf-8
'''
All util functions for quick building of UI components
'''
import re
import wx


def get_func_doc_args(fn):
    pattern = re.compile('(\w+)=\w+')
    if fn.__doc__:
        return set(pattern.findall(fn.__doc__))


WIDGET_NAME = 'widget_name'


class WidgetArray(object):
    def __init__(self, *widgets):
        self._widgets = self._handle(widgets)

    def _handle(self, widgets):
        for idx, widget in enumerate(widgets):
            widget.index = idx
        return widgets

    def __getattr__(self, widget_name):
        for w in self._widgets:
            if w.get_name() == widget_name:
                return w.get_instance()

    def __len__(self):
        return len(self._widgets)

    def __repr__(self):
        return str(self._widgets)

    def __getitem__(self, index):
        w = self._widgets[index]
        return w.get_instance()

    def __iter__(self):
        return iter(self._widgets)


class Widget(object):
    def __init__(self, wx_factory, **kwargs):
        super(Widget, self).__init__()
        self._instance = None
        self._factory = wx_factory
        self._init_args = {}
        self._attr = {}
        self.handle_args(kwargs)

        if self.get_name():
            self.set(WIDGET_NAME,
                     self.get_name().replace(' ', '_').lower())

    def get(self, attr_name):
        return self._attr.get(attr_name)

    def get_name(self):
        return self.get(WIDGET_NAME)

    def set(self, attr_name, value):
        self._attr[attr_name] = value

    def get_instance(self):
        return self._instance

    @property
    def instance(self):
        return self._instance

    def get_factory(self):
        return self._factory

    def create(self):
        if issubclass(self._factory, Factory):
            self._instance = self._factory.create()
        else:
            self._instance = self._factory(**self._init_args)
        return self._instance

    def handle_args(self, args):
        _init_args = get_func_doc_args(self._factory.__init__)
        if _init_args is None:
            return
        for k, v in args.items():
            if k in _init_args:
                self._init_args[k] = v
            else:
                self._attr[k] = v


# ------------------------------------
class Factory(object):
    @classmethod
    def create(cls, *arg, **kwargs):
        raise NotImplementedError()

    @classmethod
    def iter_widegts(cls):
        for key in dir(cls):
            if not key.startswith('_'):
                val = getattr(cls, key)
                v_cls = val.__class__
                if issubclass(v_cls, Widget):
                    yield val
                elif issubclass(v_cls, WidgetArray):
                    for w in val:
                        yield w

    @classmethod
    def get_widget(cls, widget_name):
        for w in cls.iter_widegts():
            if w.get_name() == widget_name:
                return w


class MenuBarFactory(Factory, wx.MenuBar):
    @classmethod
    def create(cls):
        menu_bar = cls()
        for menu_widget in cls.iter_widegts():
            menu = menu_widget.create()
            menu_bar.Append(menu, menu_widget.get('text'))
        return menu_bar


class MenuFactory(Factory, wx.Menu):
    @classmethod
    def create(cls):
        self = cls()
        for mi_widget in cls.iter_widegts():
            self.AppendItem(mi_widget.create())
        return self
