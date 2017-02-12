# coding:utf-8
# ----------------------------------------------------------------------------
# Name:         ListCtrl.py
# Purpose:      Testing lots of stuff, controls, window types, etc.
#
# Author:       Robin Dunn & Gary Dumer
#
# Created:
# RCS-ID:       $Id$
# Copyright:    (c) 1998 by Total Control Software
# Licence:      wxWindows license
# ----------------------------------------------------------------------------

import sys
import wx
import wx.lib.mixins.listctrl  as  listmix

import images

# ---------------------------------------------------------------------------

musicdata = {
    1: ("Bad English", "The Price Of Love", "Rock"),
    2: ("DNA featuring Suzanne Vega", "Tom's Diner", "Rock"),
    3: ("George Michael", "Praying For Time", "Rock"),
    4: ("Gloria Estefan", "Here We Are", "Rock"),
    5: ("Linda Ronstadt", "Don't Know Much", "Rock"),
    6: ("Michael Bolton", "How Am I Supposed To Live Without You", "Blues"),
    7: ("Paul Young", "Oh Girl", "Rock"),
    8: ("Paula Abdul", "Opposites Attract", "Rock"),
    9: ("Richard Marx", "Should've Known Better", "Rock"),
    10: ("Rod Stewart", "Forever Young", "Rock"),
    11: ("Roxette", "Dangerous", "Rock"),
    12: ("Sheena Easton", "The Lover In Me", "Rock"),
    13: ("Sinead O'Connor", "Nothing Compares 2 U", "Rock"),
    14: ("Stevie B.", "Because I Love You", "Rock"),
    15: ("Taylor Dayne", "Love Will Lead You Back", "Rock"),
    16: ("The Bangles", "Eternal Flame", "Rock"),
    17: ("Wilson Phillips", "Release Me", "Rock"),
    18: ("Billy Joel", "Blonde Over Blue", "Rock"),
    19: ("Billy Joel", "Famous Last Words", "Rock"),
    20: ("Janet Jackson", "State Of The World", "Rock"),
    21: ("Janet Jackson", "The Knowledge", "Rock"),
    22: ("Spyro Gyra", "End of Romanticism", "Jazz"),
    23: ("Spyro Gyra", "Heliopolis", "Jazz"),
    24: ("Spyro Gyra", "Jubilee", "Jazz"),
    25: ("Spyro Gyra", "Little Linda", "Jazz"),
    26: ("Spyro Gyra", "Morning Dance", "Jazz"),
    27: ("Spyro Gyra", "Song for Lorraine", "Jazz"),
    28: ("Yes", "Owner Of A Lonely Heart", "Rock"),
    29: ("Yes", "Rhythm Of Love", "Rock"),
    30: ("Billy Joel", "Lullabye (Goodnight, My Angel)", "Rock"),
    31: ("Billy Joel", "The River Of Dreams", "Rock"),
    32: ("Billy Joel", "Two Thousand Years", "Rock"),
    33: ("Janet Jackson", "Alright", "Rock"),
    34: ("Janet Jackson", "Black Cat", "Rock"),
    35: ("Janet Jackson", "Come Back To Me", "Rock"),
    36: ("Janet Jackson", "Escapade", "Rock"),
    37: ("Janet Jackson", "Love Will Never Do (Without You)", "Rock"),
    38: ("Janet Jackson", "Miss You Much", "Rock"),
    39: ("Janet Jackson", "Rhythm Nation", "Rock"),
    40: ("Cusco", "Dream Catcher", "New Age"),
    41: ("Cusco", "Geronimos Laughter", "New Age"),
    42: ("Cusco", "Ghost Dance", "New Age"),
    43: ("Blue Man Group", "Drumbone", "New Age"),
    44: ("Blue Man Group", "Endless Column", "New Age"),
    45: ("Blue Man Group", "Klein Mandelbrot", "New Age"),
    46: ("Kenny G", "Silhouette", "Jazz"),
    47: ("Sade", "Smooth Operator", "Jazz"),
    48: ("David Arkenstone", "Papillon (On The Wings Of The Butterfly)", "New Age"),
    49: ("David Arkenstone", "Stepping Stars", "New Age"),
    50: ("David Arkenstone", "Carnation Lily Lily Rose", "New Age"),
    51: ("David Lanz", "Behind The Waterfall", "New Age"),
    52: ("David Lanz", "Cristofori's Dream", "New Age"),
    53: ("David Lanz", "Heartsounds", "New Age"),
    54: ("David Lanz", "Leaves on the Seine", "New Age"),
}


# ---------------------------------------------------------------------------

class TestListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)




RECEIVE_HEADINGS = [
    u"接待时间",
    u"主题",
    u"请求来源",
    u"房间",
    u"服务请求人",
    u"接待人",
    u"分解状态",
]
# class ReceiveList(ListCtrl):
#
#     def AddRows(self, data_list):
#         # self.DeleteAllColumns()
#         self.DeleteAllItems()
#         popUpWin = False
#         # for pos, heading in enumerate(get_const()["headings"]):
#         #     self.InsertColumn(pos, heading, format=wx.LIST_FORMAT_LEFT)
#         for key, row in enumerate(data_list):
#             count = self.GetItemCount()
#             pos = self.InsertStringItem(count, row[0])
#             # add values in the other columns on the same row
#             for idx, val in enumerate(row[1:]):
#                 self.SetStringItem(pos, idx + 1, val)
#             self.SetItemData(pos, key + 1)
#             const_resolveStatus = get_const()["resovle_status"]
#             listitem = self.GetItem(pos)
#
#             if row[-1] == const_resolveStatus["closed"]:
#                 listitem.SetTextColour(wx.NamedColour("GRAY"))
#             elif row[-1] == const_resolveStatus["unresolved"]:
#                 listitem.SetTextColour(wx.NamedColour("RED"))
#                 listitem.SetFont(listitem.GetFont().Bold())
#                 # popUpWin = row[2] in get_const()["resource"].values()
#                 popUpWin = True
#             elif row[-1] == const_resolveStatus["resolved"]:
#                 listitem.SetTextColour(wx.NamedColour("BLUE"))
#                 listitem.SetFont(listitem.GetFont().Bold())
#             self.SetItem(listitem)
#         # self.addCache(data_list)
#         return popUpWin
#
#     initRows = AddRows
#
#     def AdaptWidth(self, headings_num, proportions):
#         num = sum(proportions)
#         _w = self.GetSize()[0] / float(num)
#         for i in range(headings_num):
#             w = _w * proportions[i]
#             self.SetColumnWidth(i, w)
