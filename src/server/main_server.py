"""
DUI's command simple stacked widgets

Author: Luis Fuentes-Montero (Luiso)
With strong help from DIALS and CCP4 teams

copyright (c) CCP4 - DLS
"""

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import http.server, socketserver
from urllib.parse import urlparse, parse_qs
import json, os, zlib, sys

import multi_node

class ReqHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):

        self.send_response(200)
        url_path = self.path
        url_dict = parse_qs(urlparse(url_path).query)
        print("url_dict =", url_dict)
        try:
            tmp_cmd2lst = url_dict["cmd_lst"]
            print("tmp_cmd2lst =", tmp_cmd2lst)

        except KeyError:
            print("no command in request (KeyError)")
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(
                'no command in request (KeyError) \n', 'utf-8'
            ))
            self.wfile.write(bytes('/*EOF*/', 'utf-8'))
            return

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
            #lst_out = []
            lst_out = cmd_tree_runner.run_dict(cmd_dict, self)

            if type(lst_out) is list or type(lst_out) is dict:
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                json_str = json.dumps(lst_out) + '\n'
                self.wfile.write(bytes(json_str, 'utf-8'))

            elif type(lst_out) is bytes:
                byt_data = zlib.compress(lst_out)
                siz_dat = str(len(byt_data))
                print("size =", siz_dat)

                self.send_header('Content-type', 'application/zlib')
                self.send_header('Content-Length', siz_dat)
                self.end_headers()

                self.wfile.write(bytes(byt_data))

            else:
                #type(lst_out) = <class 'str'> ,# html report
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                try:
                    f = open(lst_out, "r")
                    str_lst = f.readlines()
                    f.close()
                    for lin in str_lst:
                        self.wfile.write(bytes(lin, 'utf-8'))

                    self.wfile.write(bytes("/*EOF*/", 'utf-8'))

                except FileNotFoundError:
                    self.wfile.write(bytes("/*EOF*/", 'utf-8'))


            print("sending /*EOF*/")
            self.wfile.write(bytes('/*EOF*/', 'utf-8'))

        except BrokenPipeError:
            print("\n *** BrokenPipeError *** while sending EOF or JSON \n")

        except ConnectionResetError:
            print("\n *** ConnectionResetError *** while sending EOF or JSON \n")



def iter_dict(file_path):
    file_name = file_path.split("/")[-1]
    local_dict = {
        "file_name": file_name, "file_path": file_path, "list_child": []
    }
    if os.path.isdir(file_path):
        local_dict["isdir"] = True
        for new_file_name in sorted(os.listdir(file_path)):
            new_file_path = os.path.join(file_path, new_file_name)
            local_dict["list_child"].append(iter_dict(new_file_path))

    else:
        local_dict["isdir"] = False

    return local_dict


if __name__ == "__main__":

    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

        cmd_tree_runner = multi_node.Runner(runner_data)

    except FileNotFoundError:
        cmd_tree_runner = multi_node.Runner(None)
        try:
            tree_ini_path = sys.argv[1]

        except IndexError:
            tree_ini_path = os.environ['HOME']
            print(
                "\n\n *** NOT GIVEN init path, assuming:",
                tree_ini_path, " *** \n"
            )

        tree_dic_lst = iter_dict(tree_ini_path)
        #TODO make this set_dir_tree persistent with recoveries
        cmd_tree_runner.set_dir_tree(tree_dic_lst)

    cmd_dict = multi_node.str2dic("display")
    cmd_tree_runner.run_dict(cmd_dict)

    #HOST = "localhost"
    HOST = "serverip"

    PORT = 45678
    with socketserver.ThreadingTCPServer((HOST, PORT), ReqHandler) as http_daemon:
        print("serving at port", PORT)
        try:
            http_daemon.serve_forever()

        except KeyboardInterrupt:
            http_daemon.server_close()

