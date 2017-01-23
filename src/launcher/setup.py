from distutils.core import setup
import py2exe
import sys
import shutil

if len(sys.argv) == 1:
    sys.argv.append('py2exe')
includes = ["encodings", "encodings.*"]
options = {"py2exe":
         { "compressed": 1,
            "optimize": 2,
            "includes": includes,
            "bundle_files": 1,
           "dll_excludes":"w9xpopen.exe"
         }
      }
setup( 
version = "0.1",
description = "WX Launcher",
name = "WX Launcher",
options = options,
zipfile=None,
# console=['winss.py']
#data_files= [('images', ['bing.ico'])],
windows=[{"script":"launcher.py",
          "icon_resources": [(1,"rat_head.ico")]}]  
)

# copy executable to the directory of RideIDE
shutil.copy('dist/launcher.exe', '../../launcher.exe')
