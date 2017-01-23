# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-23 15:40:23
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-23 15:47:12
from flask import request


def args_get(key, default=None):
    val = request.args.get(key, default)
    if not val:
        return default
    return val