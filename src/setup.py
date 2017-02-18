# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2016-07-24 21:21:09
# @Last Modified by:   edward
# @Last Modified time: 2016-07-24 21:27:24
from distutils.core import setup
import py2exe
import sys
if len(sys.argv) == 1:
    sys.argv.append('py2exe')
includes = ["encodings", "encodings.*"]
options = {"py2exe":
         { "compressed": 2,
            "optimize": 0,
            "includes": includes,
            "excludes": ['jinja2.asyncsupport'],
            "bundle_files": 1,
           "dll_excludes":["w9xpopen.exe",'MSVCP90.dll']
         }
      }
setup( 
version = "0.1.0",
description = "MINGYUAN_AUTOMATION",
name = "MINGYUAN_AUTOMATION",
options = options,
zipfile=None,

# windows = [{"script":"freess.py", "icon_resources": [(1, "godusevpn.ico")]} ]
# data_files= [('images', ['godusevpn.png'])],
windows=[{"script":"app.py",
            "icon_resources": [(1,"rat_head.ico")]
          }
         ]
)
