# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2016-07-24 21:21:09
# @Last Modified by:   edward
# @Last Modified time: 2017-01-01 20:16:52
from distutils.core import setup
import py2exe
import sys
import os
if len(sys.argv) == 1:
    sys.argv.append('py2exe')
includes = ["encodings", "encodings.*"]
options = {"py2exe":
         { "compressed": 1,
            "optimize": 2,
            "includes": includes,
            "bundle_files": 1,
           "dll_excludes":["w9xpopen.exe",'MSVCP90.dll']
         }
      }
setup( 
version = "0.1.0",
description = "MingYuan Demo",
name = "MingYuan Demo",
options = options,
zipfile=None,

# windows = [{"script":"freess.py", "icon_resources": [(1, "godusevpn.ico")]} ]
# data_files= [('images', ['godusevpn.png'])],
windows=[{"script":"app.py",
          "icon_resources": [(1,"countdown/rat_head.ico")]}],
# data_files= [('config', ['const.json'])]
)
if os.path.isfile('dist/MingYuan Demo.exe'):
    os.remove('dist/MingYuan Demo.exe')
os.rename('dist/app.exe', 'dist/MingYuan Demo.exe')
