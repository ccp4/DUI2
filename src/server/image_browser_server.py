"""
server side of image viewer

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

from data_n_json import iter_dict

try:
    from shared_modules import format_utils

except ModuleNotFoundError:
    comm_path = os.path.abspath(__file__)[0:-30] + "shared_modules"
    print("comm_path =", comm_path)
    sys.path.insert(1, comm_path)
    import format_utils

class Browser(object):
    def __init__(self, tree_dic_lst):
        self._dir_tree_dict = tree_dic_lst

    def run_get_data(self, cmd_dict):
        cmd_lst = cmd_dict["cmd_lst"]
        print("\n cmd_lst: ", cmd_lst)

        return_list = []
        for uni_cmd in cmd_lst:
            if uni_cmd == ["dir_tree"]:
                str_dir_tree = json.dumps(self._dir_tree_dict)
                byt_data = bytes(str_dir_tree.encode('utf-8'))
                return_list = byt_data

        return return_list


def main():
    class ReqHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            url_path = self.path
            url_dict = parse_qs(urlparse(url_path).query)
            print("\n url_dict =", url_dict, "\n")
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
            try:
                #lst_out = []
                lst_out = cmd_tree_runner.run_get_data(cmd_dict)

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

                print("sending /*EOF*/")
                self.wfile.write(bytes('/*EOF*/', 'utf-8'))

            except BrokenPipeError:
                print("\n ** BrokenPipeError ** while sending EOF or JSON \n")

            except ConnectionResetError:
                print(
                    "\n ** ConnectionResetError ** while sending EOF or JSON\n"
                )

    ################################################ PROPER MAIN BROWSER

    par_def = (
        ("port", 45678),
        ("host", "localhost"),
        #("host", "serverip"),
        ("init_path", None),
    )

    init_param = format_utils.get_par(par_def, sys.argv[1:])
    print("init_param =", init_param)

    PORT = int(init_param["port"])
    HOST = init_param["host"]

    tree_ini_path = init_param["init_path"]
    if tree_ini_path == None:
        print("\n NOT GIVEN init path, using << HOME env >>")
        tree_ini_path = os.environ['HOME']

    print(
        "\n * using init path as: ",
        tree_ini_path, " * \n"
    )
    tree_dic_lst = iter_dict(tree_ini_path)

    #####################################################

    cmd_tree_runner = Browser(tree_dic_lst)

    with socketserver.ThreadingTCPServer(
        (HOST, PORT), ReqHandler
    ) as http_daemon:

        print("\n serving at: \n  { host:", HOST, " port:", PORT, "} \n")
        try:
            http_daemon.serve_forever()

        except KeyboardInterrupt:
            http_daemon.server_close()


if __name__ == "__main__":
    main()
