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
import json, os, zlib, sys, time

from data_n_json import iter_dict
from img_uploader import flex_arr_2_json

from dxtbx.model.experiment_list import ExperimentListFactory

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
        cmd_lst = cmd_dict["cmd_lst"][0].split(" ")
        print("\n cmd_lst: ", cmd_lst)

        return_list = []
        uni_cmd = cmd_lst[0]
        print("uni_cmd = <<", uni_cmd, ">>")
        if uni_cmd == "dir_tree":
            print("\n *** dir_tree *** \n")
            str_dir_tree = json.dumps(self._dir_tree_dict)
            byt_data = bytes(str_dir_tree.encode('utf-8'))
            return_list = byt_data

        #elif uni_cmd == "get_image_slice":
        elif uni_cmd == "gis":
            img_num = int(cmd_lst[1])
            print("generating slice of image", img_num)
            '''
            cmd_lst = ['gis', '0', 'inv_scale=1', 'view_rect=319,463,693,1089']

            '''
            inv_scale = 1
            for sub_par in cmd_lst[2:]:
                eq_pos = sub_par.find("=")
                left_side = sub_par[0:eq_pos]
                right_side = sub_par[eq_pos + 1:]
                if left_side == "inv_scale":
                    inv_scale = int(right_side)
                    print("inv_scale =", inv_scale)

                elif left_side == "view_rect":
                    print("view_rect =", right_side)
                    [x1, y1, x2, y2] = right_side.split(",")
                    print("x1, y1, x2, y2 =", x1, y1, x2, y2)

            exp_path = cmd_dict["path"][0]
            str_json = flex_arr_2_json.get_json_w_2d_slise(
                [exp_path], img_num, inv_scale, x1, y1, x2, y2
            )
            if str_json is not None:
                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

        elif uni_cmd == "gi":
            img_num = int(cmd_lst[1])
            print("generating image", img_num)
            exp_path = cmd_dict["path"][0]
            str_json = flex_arr_2_json.get_json_w_img_2d(
                [exp_path], img_num,
            )

            if str_json is not None:
                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

        ############################## START copy

        elif uni_cmd == "gmi":
            img_num = int(cmd_lst[1])
            print("generating slice of mask image", img_num)
            exp_path = cmd_dict["path"][0]
            str_json = flex_arr_2_json.get_json_w_mask_img_2d(
                [exp_path], img_num,
            )

            if str_json is not None:
                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data


        ############################## FINISH copy

        elif uni_cmd == "get_template":

            print("cmd_dict =", cmd_dict)

            exp_path = cmd_dict["path"][0]
            print("\n exp_path =", exp_path, "\n")

            experiments = ExperimentListFactory.from_json_file(
                exp_path
            )
            my_sweep = experiments.imagesets()[0]
            str_json = my_sweep.get_template()

            data_xy_flex = my_sweep.get_raw_data(0)[0].as_double()
            img_with, img_height = data_xy_flex.all()[0:2]
            return_list = [str_json, img_with, img_height]


        elif uni_cmd == "get_reflection_list":

            print("cmd_dict =", cmd_dict)
            exp_path = cmd_dict["path"][0]
            print("\n exp_path =", exp_path, "\n")
            ref_path = exp_path[:-4] + "refl"
            print("\n ref_path =", ref_path, "\n")



            refl_lst = flex_arr_2_json.get_refl_lst(
                [exp_path], [ref_path],
                int(cmd_lst[1])
            )
            return_list = refl_lst

        return return_list


def main():
    class ReqHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            url_path = self.path
            url_dict = parse_qs(urlparse(url_path).query)
            print("\n url_dict =", url_dict, "\n")
            cmd_dict = url_dict

            try:
                #lst_out = []
                lst_out = browser_runner.run_get_data(cmd_dict)

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
        ("init_path", "."),
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

    browser_runner = Browser(tree_dic_lst)
    launch_success = False
    n_secs = 5
    while launch_success == False:
        try:
            with socketserver.ThreadingTCPServer(
                (HOST, PORT), ReqHandler
            ) as http_daemon:
                print("\n serving at: \n  { host:", HOST, " port:", PORT, "} \n")
                launch_success = True
                try:
                    http_daemon.serve_forever()

                except KeyboardInterrupt:
                    http_daemon.server_close()

        except OSError:
            launch_success = False

            print("OSError, trying again in",  n_secs, "secs")
            time.sleep(n_secs)


if __name__ == "__main__":
    main()
