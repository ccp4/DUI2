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
import json

import multi_node

class ReqHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        first_str_out = 'Received request:' + str(self) + '\n'

        url_path = self.path
        url_dict = parse_qs(urlparse(url_path).query)
        print("url_dict =", url_dict)
        try:
            tmp_cmd2lst = url_dict["cmd_lst"]
            print("tmp_cmd2lst =", tmp_cmd2lst)

        except KeyError:
            print("no command in request (KeyError)")
            self.wfile.write(bytes(
                'no command in request (KeyError) \n', 'ascii', 'ignore'
            ))
            self.wfile.write(bytes('/*EOF*/', 'ascii', 'ignore'))
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
            lst_out = []
            lst_out = cmd_tree_runner.run_dict(cmd_dict, self)
            json_str = json.dumps(lst_out) + '\n'
            self.wfile.write(bytes(json_str, 'ascii', 'ignore'))
            print("sending /*EOF*/")
            self.wfile.write(bytes('/*EOF*/', 'ascii', 'ignore'))

        except BrokenPipeError:
            print("\n *** BrokenPipeError *** while sending EOF or JSON \n")


if __name__ == "__main__":

    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

        cmd_tree_runner = multi_node.Runner(runner_data)


    except FileNotFoundError:
        print("Starting from hacked multiple import")
        cmd_tree_runner = multi_node.Runner(None)
        '''
        #temp hack
        lst_dic = [
            {'nod_lst': [0], 'cmd_lst': [['ip', 'x41']]},
            {'nod_lst': [0], 'cmd_lst': [['ip', 'x42']]},
            {'nod_lst': [0], 'cmd_lst': [['ip', 'x43']]}
        ]
        for cmd_dict in lst_dic:
            cmd_tree_runner.run_dict(cmd_dict)

        #'''

    cmd_tree_runner.run_dict({'nod_lst': [0], 'cmd_lst': [['ip', 'x41']]})
    cmd_dict = multi_node.str2dic("display")
    cmd_tree_runner.run_dict(cmd_dict)

    PORT = 8080
    with socketserver.ThreadingTCPServer(("", PORT), ReqHandler) as http_daemon:
        print("serving at port", PORT)
        try:
            http_daemon.serve_forever()

        except KeyboardInterrupt:
            http_daemon.server_close()

