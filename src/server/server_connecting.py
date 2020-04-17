import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import time, subprocess

class ReqHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes('Test #6.5 ... multitasking & GUI \n', 'utf-8'))

        url_path = self.path
        dict_cmd = parse_qs(urlparse(url_path).query)
        cmd_str = dict_cmd['command'][0]
        cmd_lst = cmd_str.split(' ')
        try:
            print("\n Running:", cmd_lst, "\n")
            proc = subprocess.Popen(
                cmd_lst,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            line = None
            while proc.poll() is None or line != '':
                line = proc.stdout.readline()
                #print("StdOut>> ", line)
                self.wfile.write(bytes(line , 'utf-8'))

            proc.stdout.close()

        except:
            print("error running subprocess from server")

        print("sending /*EOF*/")
        self.wfile.write(bytes('/*EOF*/', 'utf-8'))


if __name__ == "__main__":
    PORT = 8080
    with socketserver.ThreadingTCPServer(("", PORT), ReqHandler) as http_daemon:
        print("serving at port", PORT)
        try:
            http_daemon.serve_forever()

        except KeyboardInterrupt:
            http_daemon.server_close()

