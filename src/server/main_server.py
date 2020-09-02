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
import time, json

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
            self.wfile.write(bytes('no command in request (KeyError) \n', 'utf-8'))
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
        runner_data = {'step_list': [{'_base_dir': '/tmp/dui', 'lst2run': [['Root']], '_lst_expt': [], '_lst_refl': [], '_run_dir': '/tmp/tst/', '_log_line_lst': [], 'lin_num': 0, 'status': 'Succeeded', 'parent_node_lst': [], 'child_node_lst': [1, 2, 3]}, {'_base_dir': '/tmp/dui', 'lst2run': [['dials.import', '/scratch/dui_tst/X4_wide_0_to_9/*.cbf']], '_lst_expt': [], '_lst_refl': [], '_run_dir': '/tmp/dui/run1', '_log_line_lst': ['DIALS (2018) Acta Cryst. D74, 85-97. https://doi.org/10.1107/S2059798317017235', 'DIALS 3.dev.90-g263177265', 'The following parameters have been modified:', '', 'input {', '  experiments = <image files>', '}', '', '--------------------------------------------------------------------------------', "  format: <class 'dxtbx.format.FormatCBFMiniPilatus.FormatCBFMiniPilatus'>", '  num images: 9', '  sequences:', '    still:    0', '    sweep:    1', '  num stills: 0', '--------------------------------------------------------------------------------', 'Writing experiments to imported.expt', ''], 'lin_num': 1, 'status': 'Succeeded', 'parent_node_lst': [0], 'child_node_lst': []}, {'_base_dir': '/tmp/dui', 'lst2run': [['dials.import', '/scratch/dui_tst/X4_wide_10_to_19/*.cbf']], '_lst_expt': [], '_lst_refl': [], '_run_dir': '/tmp/dui/run2', '_log_line_lst': ['DIALS (2018) Acta Cryst. D74, 85-97. https://doi.org/10.1107/S2059798317017235', 'DIALS 3.dev.90-g263177265', 'The following parameters have been modified:', '', 'input {', '  experiments = <image files>', '}', '', '--------------------------------------------------------------------------------', "  format: <class 'dxtbx.format.FormatCBFMiniPilatus.FormatCBFMiniPilatus'>", '  num images: 10', '  sequences:', '    still:    0', '    sweep:    1', '  num stills: 0', '--------------------------------------------------------------------------------', 'Writing experiments to imported.expt', ''], 'lin_num': 2, 'status': 'Succeeded', 'parent_node_lst': [0], 'child_node_lst': []}, {'_base_dir': '/tmp/dui', 'lst2run': [['dials.import', '/scratch/dui_tst/X4_wide_20_to_29/*.cbf']], '_lst_expt': [], '_lst_refl': [], '_run_dir': '/tmp/dui/run3', '_log_line_lst': ['DIALS (2018) Acta Cryst. D74, 85-97. https://doi.org/10.1107/S2059798317017235', 'DIALS 3.dev.90-g263177265', 'The following parameters have been modified:', '', 'input {', '  experiments = <image files>', '}', '', '--------------------------------------------------------------------------------', "  format: <class 'dxtbx.format.FormatCBFMiniPilatus.FormatCBFMiniPilatus'>", '  num images: 10', '  sequences:', '    still:    0', '    sweep:    1', '  num stills: 0', '--------------------------------------------------------------------------------', 'Writing experiments to imported.expt', ''], 'lin_num': 3, 'status': 'Succeeded', 'parent_node_lst': [0], 'child_node_lst': []}], 'bigger_lin': 3}
        print("\n starting with example")

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

