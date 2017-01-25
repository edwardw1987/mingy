# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2016-07-24 02:22:41
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-25 16:42:18

import threading
import time

import wx

myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)


class CountEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""

    def __init__(self, etype, eid, value=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value


class UpdateEvent(CountEvent):
    pass


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self.setDaemon(True)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class CountingThread(StoppableThread):
    def __init__(self, parent, value, *args, **kw):
        """
        @param parent: The gui object that should recieve the value
        @param value: value to 'calculate' to
        """
        super(CountingThread, self).__init__(*args, **kw)
        self._parent = parent
        self._value = value

    def get_parent(self):
        return self._parent

    def get_value(self):
        return self._value

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        ref, pos = self._value
        s = ref * 60
        s = 0
        while not self.stopped():
            if s % 15 == 0:
                evt = CountEvent(myEVT_COUNT, -1, (pos, s))
                wx.PostEvent(self._parent, evt)
            time.sleep(1)  # our simulated calculation time
            s += 1
