# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-23 16:37:14
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-23 16:40:36
from flask import jsonify, Blueprint
from client import MinYuanClient, MINGYUAN_TEST_ADDR
from util import args_get
import config


mingy = Blueprint('MingYuan', __name__)

@mingy.route('/jf/task')
def api_jftask():
    project_id = args_get('pid', config.DEFAULT_PROJECT_ID)
    taskcode = args_get('tc')
    mingy = MinYuanClient(addr=MINGYUAN_TEST_ADDR)
    ret = mingy.getJFTaskList(project_id, taskcode)
    return jsonify(ret)
