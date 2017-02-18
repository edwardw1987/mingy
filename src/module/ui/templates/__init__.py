# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-23 13:39:13
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-23 13:42:06
from jinja2 import Template
import os

FILTER = '''
<filter type="and">
    <condition operator="in" attribute="TsProjGUID" value="{{ project_id }}" />
{% if task_code %}
    <condition attribute="taskcode" operator="like" datatype="varchar" value="{{ task_code }}" />
{% endif %}
</filter>
'''


def render_template(template_string, **context):
    ret = Template(template_string).render(context)
    return ret
