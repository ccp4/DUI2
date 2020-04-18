import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import time, subprocess

import out_utils, multi_node


class ReqHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("lst_test =", lst_test)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        str_out = 'Running request:' + str(self) + '\n'
        self.wfile.write(bytes(str_out, 'utf-8'))

        url_path = self.path
        dict_cmd = parse_qs(urlparse(url_path).query)
        cmd_str = dict_cmd['command'][0]

        lst_cmd = cmd_str.split(";")

        lst_cmd_lst = []
        for sub_str in lst_cmd:
            lst_cmd_lst.append(sub_str.split(" "))

        print("lst_cmd_lst:", lst_cmd_lst)
        cmd_tree_runner.run(lst_cmd_lst, self)
        tree_output(cmd_tree_runner)

        print("sending /*EOF*/")
        self.wfile.write(bytes('/*EOF*/', 'utf-8'))

        lst_test.append(cmd_str)


tree_output = out_utils.TreeShow()
cmd_tree_runner = multi_node.Runner()



if __name__ == "__main__":
    lst_test = []
    PORT = 8080
    with socketserver.ThreadingTCPServer(("", PORT), ReqHandler) as http_daemon:
        print("serving at port", PORT)
        try:
            http_daemon.serve_forever()

        except KeyboardInterrupt:
            http_daemon.server_close()

