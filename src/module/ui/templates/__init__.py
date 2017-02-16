# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-23 13:39:13
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-23 13:42:06
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os

def render_template(template_name, **context):
    globals = context.pop('globals', {})
    jinja_env = Environment(
        loader=FileSystemLoader(os.path.join(
            os.path.dirname(__file__), '.')),
        trim_blocks=True,
        extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", ])
    jinja_env.globals.update(globals)
    return jinja_env.get_template(template_name).render(context)
