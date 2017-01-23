# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-23 14:57:08
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-23 15:51:21
from flask import Flask, jsonify
from client import MinYuanClient, MINGYUAN_TEST_ADDR
from util import args_get
import config


app = Flask(__name__)

@app.route('/api/jftask')
def api_jftask():
    project_id = args_get('pid', config.DEFAULT_PROJECT_ID)
    mingy = MinYuanClient(addr=MINGYUAN_TEST_ADDR)
    ret = mingy.getJFTaskList(project_id)
    return jsonify(ret)