import http.server, socketserver
from urllib.parse import urlparse, parse_qs
import time, subprocess, json

import multi_node

class ReqHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        str_out = 'Running request:' + str(self) + '\n'
        self.wfile.write(bytes(str_out, 'utf-8'))

        url_path = self.path
        url_dict = parse_qs(urlparse(url_path).query)
        print("url_dict =", url_dict)
        tmp_cmd2lst = url_dict["cmd_lst"]
        print("tmp_cmd2lst =", tmp_cmd2lst)
        cmd_lst = []
        for inner_str in tmp_cmd2lst:
            cmd_lst.append(inner_str.split(" "))
        nod_lst = []
        try:
            for inner_str in url_dict["nod_lst"]:
                nod_lst.append(int(inner_str))

        except KeyError:
            print("no node number provided")

        cmd_dict = {"nod_lst":nod_lst,
                    "cmd_lst":cmd_lst}

        print("parse_qs(urlparse(url_path).query", cmd_dict)

        try:
            lst_out = []
            lst_out = cmd_tree_runner.run_dict(cmd_dict, self)
            json_str = json.dumps(lst_out) + '\n'
            self.wfile.write(bytes(json_str, 'utf-8'))

            print("sending /*EOF*/")
            self.wfile.write(bytes('/*EOF*/', 'utf-8'))

        except BrokenPipeError:
            print("\n *** BrokenPipeError *** while sending EOF or JSON \n")


if __name__ == "__main__":

    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

    except FileNotFoundError:
        runner_data = None
        print("Nothing to recover")

    cmd_tree_runner = multi_node.Runner(runner_data)
    cmd_dict = multi_node.str2dic("display")
    cmd_tree_runner.run_dict(cmd_dict)

    PORT = 8080
    with socketserver.ThreadingTCPServer(("", PORT), ReqHandler) as http_daemon:
        print("serving at port", PORT)
        try:
            http_daemon.serve_forever()

        except KeyboardInterrupt:
            http_daemon.server_close()

