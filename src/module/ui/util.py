# coding:utf-8
'''
All util functions for quick building of UI components
'''
import re


def get_func_doc_args(fn):
    pattern = re.compile('(\w+)=\w+')
    return set(pattern.findall(fn.__doc__))


class WidgetArray(object):
    def __init__(self, *widgets):
        self._widgets = self._handle(widgets)

    def _handle(self, widgets):
        for idx, widget in enumerate(widgets):
            widget.index = idx
            if widget.get('name'):
                widget.set('name',
                           widget.get('name').replace(' ', '_').lower())
        return widgets

    def __getattr__(self, name):
        for w in self._widgets:
            if w.get('name') == name:
                return w.get_instance()

    def __len__(self):
        return len(self._widgets)

    def __repr__(self):
        return str(self._widgets)

    def __getitem__(self, index):
        return self._widgets[index]

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

    def get(self, attr_name):
        return self._attr.get(attr_name)

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
    def handle_widget(cls, widget, *args, **kwargs):
        factory = widget.get_factory()
        if issubclass(factory, Factory):
            factory.create(widget, *args, **kwargs)


class MenuBarFactory(Factory):
    @classmethod
    def create(cls):
        menu_bar = cls()
        for menu_widget in cls.iter_widegts():
            menu = menu_widget.create()
            cls.handle_widget(menu_widget)
            menu_bar.Append(menu, menu_widget.get('text'))
        return menu_bar


class MenuFactory(Factory):
    @classmethod
    def create(cls, menu_widget):
        for mi_widget in cls.iter_widegts():
            menu_widget.instance.AppendItem(mi_widget.create())


if __name__ == '__main__':
    import wx

    arr = WidgetArray(Widget(wx.ListItem))
    # for i in arr:
    #     print i
    # print arr[0]
    # arr.push(88)
    print arr.a
