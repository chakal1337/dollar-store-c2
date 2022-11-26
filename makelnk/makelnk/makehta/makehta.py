import sys

if len(sys.argv) < 2:
 print("<command>")
 sys.exit(0)
with open("test.hta", "r") as file:
 data = file.read()
 print(data.replace('{ACOMMAND}', sys.argv[1]))