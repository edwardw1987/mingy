# coding:utf-8

class Keyword(object):
    name = None
    default_value = None

    def __init__(self, value=None):
        self._value = value or self.default_value

    def GetValue(self):
        return self._value


class Text(Keyword):
    name = 'text'
    default_value = ''

    def GetValue(self):
        value = super(Text, self).GetValue()
        return unicode(value)


class Handler(Keyword):
    name = 'handler'
    default_value = None


class Kind(Keyword):
    name = 'kind'
    default_value = 0


class ID(Keyword):
    name = 'id'
    default_value = -1


class ParentMenu(Keyword):
    name = 'parentMenu'
    default_value = None


class Enable(Keyword):
    name = 'enable'
    default_value = True
