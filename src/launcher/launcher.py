import os
import sys
import subprocess
import _winreg as winreg

BASE_DIR = os.path.dirname(sys.argv[0])


EXE = os.path.join(BASE_DIR, 'env\\Scripts\\python.exe')
RIDE = os.path.join(BASE_DIR, 'src\\app.py')
subprocess.Popen(EXE + ' ' + RIDE, shell=True, stdout=subprocess.PIPE)
