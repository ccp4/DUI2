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
        self.wfile.write(bytes('Test #6.5 ... multitasking & GUI \n', 'utf-8'))

        url_path = self.path
        dict_cmd = parse_qs(urlparse(url_path).query)
        cmd_str = dict_cmd['command'][0]

        lst_cmd = cmd_str.split(";")

        lst_cmd_lst = []
        for sub_str in lst_cmd:
            lst_cmd_lst.append(sub_str.split(" "))

        print("lst_cmd_lst:", lst_cmd_lst)
        cmd_tree_runner.run(lst_cmd_lst)
        tree_output(cmd_tree_runner)


        '''
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

        '''

        print("sending /*EOF*/")
        self.wfile.write(bytes('/*EOF*/', 'utf-8'))

        lst_test.append(cmd_str)


tree_output = out_utils.TreeShow()
cmd_tree_runner = multi_node.Runner()
'''
if __name__ == "__main__":

    command = ""

    while command.strip() != "exit" and command.strip() != "quit":
        try:
            inp_str = "lin [" + str(cmd_tree_runner.current_line) + "] >>> "
            command = str(input(inp_str))

        except EOFError:
            print("Caught << EOFError >> \n  ... interrupting")
            sys.exit(0)

        except:
            print("Caught << some error >>", e, " ... interrupting")
            sys.exit(1)

        print("command =", command)

        lst_cmd = command.split(";")

        lst_cmd_lst = []
        for sub_str in lst_cmd:
            lst_cmd_lst.append(sub_str.split(" "))

        print("lst_cmd_lst:", lst_cmd_lst)
        cmd_tree_runner.run(lst_cmd_lst)

        #out_utils.print_list(cmd_tree_runner.step_list, cmd_tree_runner.current_line)

        tree_output(cmd_tree_runner)
'''


if __name__ == "__main__":
    lst_test = []
    PORT = 8080
    with socketserver.ThreadingTCPServer(("", PORT), ReqHandler) as http_daemon:
        print("serving at port", PORT)
        try:
            http_daemon.serve_forever()

        except KeyboardInterrupt:
            http_daemon.server_close()

