import os
import sys
import subprocess

BASE_DIR = os.path.dirname(sys.argv[0]).partition('\\src')[0]
EXE = os.path.join(BASE_DIR, 'env\\Scripts\\python.exe')
RIDE = os.path.join(BASE_DIR, 'src\\app.py')
cmdstr = EXE + ' ' + RIDE

def main():
    subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE)
if __name__ == '__main__':
    main()