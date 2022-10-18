"""
DUI clouds's server side main program

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

#import http.server, socketserver
#from urllib.parse import urlparse, parse_qs
import json, os, zlib, sys, time

from server import multi_node
from server.data_n_json import iter_dict
from shared_modules import format_utils
from server.init_first import ini_data

class ReqHandler(object):
    def __init__(self, runner_in):
        self.tree_runner = runner_in

    def fake_post(self, url_dict):
        print("\n url_dict =", url_dict, "\n")

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

        found_dials_command = False
        print("cmd_lst = ", cmd_lst)
        for inner_lst in cmd_lst:
            for single_str in inner_lst:
                if "dials" in single_str:
                    found_dials_command = True

                print("single_str = ", single_str)

        if found_dials_command:
            self.tree_runner.run_dials_command(cmd_dict, None)
            print("sending /*EOF*/ (Dials CMD)")
            #self.wfile.write(bytes('/*EOF*/', 'utf-8'))
            print('/*EOF*/')

        else:
            print("sending /*EOF*/ (Dui2 CMD)")
            #self.wfile.write(bytes('/*EOF*/', 'utf-8'))
            print('/*EOF*/')


    def fake_get(self, url_dict):
        '''
        self.send_response(200)
        url_path = self.path
        url_dict = parse_qs(urlparse(url_path).query)
        '''

        print("\n url_dict =", url_dict, "\n")
        tmp_cmd2lst = url_dict["cmd_lst"]

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

        lst_out = self.tree_runner.run_get_data(cmd_dict)

        if type(lst_out) is list or type(lst_out) is dict:
            json_str = json.dumps(lst_out) + '\n'

            #self.wfile.write(bytes(json_str, 'utf-8'))
            print(json_str)


        elif type(lst_out) is bytes:
            byt_data = zlib.compress(lst_out)
            siz_dat = str(len(byt_data))
            print("size =", siz_dat)

            #self.wfile.write(bytes(byt_data))
            print(bytes(byt_data))


        print("sending /*EOF*/")
        #self.wfile.write(bytes('/*EOF*/', 'utf-8'))
        print('/*EOF*/')


def main(par_def = None, connection_out = None):
    format_utils.print_logo()
    data_init = ini_data()
    data_init.set_data(par_def)

    init_param = format_utils.get_par(par_def, sys.argv[1:])
    print("init_param(server) =", init_param)

    PORT = int(init_param["port"])
    HOST = init_param["host"]

    run_local = True

    print("\n run_local =", run_local, "\n")

    tree_ini_path = init_param["init_path"]
    if tree_ini_path == None:
        print("\n NOT GIVEN init_path")
        print(" using the dir from where the commad 'dui_server' was invoqued")
        tree_ini_path = os.getcwd()

    print(
        "\n using init path as: <<", tree_ini_path, ">> \n"
    )
    tree_dic_lst = iter_dict(tree_ini_path, 0)
    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

        cmd_tree_runner = multi_node.Runner(runner_data)

    except FileNotFoundError:
        cmd_tree_runner = multi_node.Runner(None)

    cmd_tree_runner.set_dir_tree(tree_dic_lst)

    cmd_dict = multi_node.str2dic("display")
    cmd_tree_runner.run_get_data(cmd_dict)
    my_handler = ReqHandler(cmd_tree_runner)

    for times_do in range(5):
        cmd_in = input("type: \"Node,command\":")
        try:
            [parent, cmd] = cmd_in.split(",")

        except ValueError:
            [parent, cmd] = ["", cmd_in]

        full_cmd = {"nod_lst":[parent], "cmd_lst":[cmd]}
        my_handler.fake_post(full_cmd)
        #my_handler.fake_get(full_cmd)
        my_handler.fake_get({"nod_lst":[0], "cmd_lst":["display"]})

    print("\n ... Done")
