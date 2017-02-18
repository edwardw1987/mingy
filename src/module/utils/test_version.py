# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2016-07-26 11:33:01
# @Last Modified by:   edward
# @Last Modified time: 2016-07-26 12:17:53
import requests
import datetime
def expired(*args):
    expired_date = args
    url = "http://apis.baidu.com/3023/time/time"
    headers = {
        'apikey': 'a5c704025f1c76f6970b052a6cf67bc2'
    }
    try:
        res = requests.get(url, headers=headers)
    except:
        return -1
    dt = datetime.datetime.fromtimestamp(res.json()['stime'])
    net_date = dt.year, dt.month, dt.day
    return net_date >= expired_date

