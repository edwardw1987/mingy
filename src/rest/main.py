# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-23 14:57:08
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-23 16:52:04
from flask import Flask
from mingy.app import mingy

app = Flask(__name__)

app.register_blueprint(mingy, url_prefix='/api/mingy')
