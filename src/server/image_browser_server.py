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
import json, os, zlib, sys, time, logging

#from server.data_n_json import iter_dict, spit_out
from server.data_n_json import spit_out

from server.img_uploader import flex_arr_2_json
from shared_modules import format_utils

class Browser(object):
    def __init__(self, path_str):
        self._init_path = path_str

    def run_get_data(self, cmd_dict):
        cmd_lst = cmd_dict["cmd_lst"][0].split(" ")

        return_list = []
        uni_cmd = cmd_lst[0]

        if uni_cmd == "gis":
            img_num = int(cmd_lst[1])
            inv_scale = 1
            for sub_par in cmd_lst[2:]:
                eq_pos = sub_par.find("=")
                left_side = sub_par[0:eq_pos]
                right_side = sub_par[eq_pos + 1:]
                if left_side == "inv_scale":
                    inv_scale = int(right_side)

                elif left_side == "view_rect":
                    [x1, y1, x2, y2] = right_side.split(",")

            exp_path = cmd_dict["path"][0]
            str_json = flex_arr_2_json.get_json_w_2d_slise(
                [exp_path], img_num, inv_scale, x1, y1, x2, y2
            )
            if str_json is not None:
                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

        elif uni_cmd == "gmis":
            img_num = int(cmd_lst[1])
            inv_scale = 1
            for sub_par in cmd_lst[2:]:
                eq_pos = sub_par.find("=")
                left_side = sub_par[0:eq_pos]
                right_side = sub_par[eq_pos + 1:]
                if left_side == "inv_scale":
                    inv_scale = int(right_side)

                elif left_side == "view_rect":
                    [x1, y1, x2, y2] = right_side.split(",")

            exp_path = cmd_dict["path"][0]
            str_json = flex_arr_2_json.get_json_w_2d_mask_slise(
                [exp_path], img_num, inv_scale, x1, y1, x2, y2
            )
            if str_json is not None:
                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

        elif uni_cmd == "gi":
            img_num = int(cmd_lst[1])
            exp_path = cmd_dict["path"][0]
            str_json = flex_arr_2_json.get_json_w_img_2d(
                [exp_path], img_num,
            )

            if str_json is not None:
                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

        elif uni_cmd == "gmi":
            img_num = int(cmd_lst[1])
            exp_path = cmd_dict["path"][0]
            str_json = flex_arr_2_json.get_json_w_mask_img_2d(
                [exp_path], img_num,
            )
            if str_json is not None:
                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

        elif uni_cmd == "get_template":
            exp_path = cmd_dict["path"][0]
            img_num = int(cmd_lst[1])
            return_list = flex_arr_2_json.get_template_info(
                exp_path, img_num
            )

        elif uni_cmd == "get_reflection_list":
            exp_path = cmd_dict["path"][0]
            ref_path = exp_path[:-4] + "refl"
            refl_lst = flex_arr_2_json.get_refl_lst(
                [exp_path], [ref_path],
                int(cmd_lst[1])
            )
            return_list = refl_lst

        elif uni_cmd == "get_dir_ls":

            print("Hi there")
            print("cmd_lst =", cmd_lst)

            try:
                curr_path = cmd_lst[1].replace("/", os.sep)
                print("curr_path =", curr_path)
                f_name_list =  os.listdir(curr_path)
                dict_list = []
                for f_name in f_name_list:
                    f_path = curr_path + f_name
                    f_isdir = os.path.isdir(f_path)
                    file_dict = {"fname": f_name, "isdir":f_isdir}
                    dict_list.append(file_dict)

                return_list = dict_list

            except FileNotFoundError:
                err_msg = "file not found err catch, not sending file list"
                logging.info(err_msg)
                print(err_msg)
                return_list = []

            except PermissionError:
                err_msg = "permission denied err catch, " + \
                "attempt to open not allowed path, not sending file list"
                logging.info(err_msg)
                print(err_msg)
                return_list = []

        elif uni_cmd == "dir_path":
            return_list = [self._init_path]

        return return_list


def main(par_def = None, connection_out = None):
    class ReqHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                self.send_response(200)

            except AttributeError:
                logging.info(
                    "Attribute Err catch, not supposed send header info #1"
                )

            url_path = self.path
            url_dict = parse_qs(urlparse(url_path).query)
            cmd_dict = url_dict

            print("cmd_dict = ", cmd_dict)

            try:
                #lst_out = []
                lst_out = browser_runner.run_get_data(cmd_dict)

                if type(lst_out) is list or type(lst_out) is dict:
                    try:
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()

                    except AttributeError:
                        logging.info(
                            "Attribute Err catch," +
                            " not supposed send header info"
                        )

                    json_str = json.dumps(lst_out) + '\n'
                    spit_out(
                        str_out = json_str, req_obj = self, out_type = 'utf-8'
                    )

                elif type(lst_out) is bytes:
                    byt_data = zlib.compress(lst_out)
                    siz_dat = str(len(byt_data))
                    try:
                        self.send_header('Content-type', 'application/zlib')
                        self.send_header('Content-Length', siz_dat)
                        self.end_headers()

                    except AttributeError:
                        logging.info(
                            "Attribute Err catch," +
                            " not supposed send header info"
                        )
                    spit_out(str_out = byt_data, req_obj = self)

                logging.info("sending /*EOF*/")
                spit_out(
                    str_out = '/*EOF*/', req_obj = self, out_type = 'utf-8'
                )

            except BrokenPipeError:
                logging.info(
                    "<< BrokenPipe err catch >>  while sending EOF or JSON"
                )

            except ConnectionResetError:
                logging.info(
                    "<< ConnectionReset err catch >> while sending EOF or JSON"
                )

    ################################################ PROPER MAIN BROWSER


    init_param = format_utils.get_par(par_def, sys.argv[1:])

    PORT = int(init_param["port"])
    HOST = init_param["host"]

    #global run_local
    if init_param["all_local"].lower() == "true":
        run_local = True

    else:
        run_local = False

    logging.info("run_local =" + str(run_local))

    tree_ini_path = init_param["init_path"]
    if tree_ini_path == None:
        print("\n NOT GIVEN init path, using ", os.getcwd())
        tree_ini_path = os.getcwd()

    if tree_ini_path[-1] != os.sep:
        tree_ini_path += os.sep

    logging.info("\n << using init path as: " + tree_ini_path + ">>")
    print("\n << using init path as: " + tree_ini_path + ">>")
    browser_runner = Browser(tree_ini_path)
    launch_success = False
    n_secs = 5
    while launch_success == False:
        try:
            with socketserver.ThreadingTCPServer(
                (HOST, PORT), ReqHandler
            ) as http_daemon:
                logging.info(
                    "serving at:{host:" + str(HOST) + " port:" + str(PORT), "}"
                )
                print(
                    "serving at:{host:" + str(HOST) + " port:" + str(PORT), "}"
                )
                launch_success = True
                try:
                    http_daemon.serve_forever()

                except KeyboardInterrupt:
                    http_daemon.server_close()

        except OSError:
            launch_success = False
            print("OS Err catch, waiting ", n_secs)
            time.sleep(n_secs)

