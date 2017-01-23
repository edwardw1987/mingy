# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-23 14:54:58
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-23 16:58:22
import os
import subprocess

EXE = 'C:\\Python27\\python.exe'
BaseDir = os.path.dirname(__file__)

def launch_server():
    launch_file = os.path.join(BaseDir, 'launch.py')
    subprocess.Popen(EXE + ' ' + launch_file, shell=True)
    