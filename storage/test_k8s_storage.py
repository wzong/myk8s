from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import os
import subprocess
import traceback

def GetFiles(path):
  res = subprocess.run(["ls", "-l", path], stdout = subprocess.PIPE).stdout.decode()
  return path + '\n' + res + '\n\n'

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
  daemon_threads = True

class CheckVolumnsHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path.startswith('/healthz'):
      self.Respond(200, 'ok')
    try:
      lines = [
        'Pod: ' + os.getenv('MY_POD_NAME') + '\n',
        'Mounted Persistent Volumnes\n',
      ]
      for path in os.getenv('PV_PATHS').split(','):
        lines.append(GetFiles(path))
      self.Respond(200, '\n'.join(lines))
    except Exception as e:
      self.Respond(500, traceback.format_exc())

  def Respond(self, code, message):
    self.send_response(code)
    self.send_header("Content-type", "text/plain")
    self.end_headers()
    self.wfile.write(message.encode())

if __name__ == "__main__":
  webServer = ThreadingHTTPServer(('0.0.0.0', 8080), CheckVolumnsHandler)
  print("Server started http://0.0.0.0:8080")
  try:
    webServer.serve_forever()
  except KeyboardInterrupt:
    pass
  webServer.server_close()
  print("Server stopped.")
