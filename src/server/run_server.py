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

import http.server, socketserver
from urllib.parse import urlparse, parse_qs
import json, os, zlib, sys, time, logging

from server import multi_node
from server.data_n_json import iter_dict, spit_out
from server.init_first import ini_data
from shared_modules import format_utils


def main(par_def = None, connection_out = None):
    format_utils.print_logo()
    class ReqHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            body_str = str(post_body.decode('utf-8'))
            url_dict = parse_qs(body_str)
            logging.info("\n url_dict =" + str(url_dict) + "\n")
            try:
                tmp_cmd2lst = url_dict["cmd_lst"]
                logging.info("tmp_cmd2lst =" + str(tmp_cmd2lst))

            except KeyError:
                logging.info("no command in request (KeyError)")
                try:
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()

                except AttributeError:
                    logging.info(
                        "Attribute Err catch," +
                        " not supposed send header info"
                    )

                spit_out(
                    str_out = 'no command in request (Key err catch ) ',
                    req_obj = self, out_type = 'utf-8'
                )
                spit_out(
                    str_out = '/*EOF*/', req_obj = self,
                    out_type = 'utf-8'
                )
                return

            cmd_lst = []
            for inner_str in tmp_cmd2lst:
                cmd_lst.append(inner_str.split(" "))

            nod_lst = []
            try:
                for inner_str in url_dict["nod_lst"]:
                    nod_lst.append(int(inner_str))

            except KeyError:
                logging.info("no node number provided")

            cmd_dict = {"nod_lst":nod_lst,
                        "cmd_lst":cmd_lst}

            found_dials_command = False
            for inner_lst in cmd_lst:
                for single_str in inner_lst:
                    if "dials" in single_str:
                        found_dials_command = True


            if found_dials_command:
                try:
                    cmd_tree_runner.run_dials_command(cmd_dict, self)
                    logging.info("sending /*EOF*/ (Dials CMD)")
                    spit_out(
                        str_out = '/*EOF*/', req_obj = self,
                        out_type = 'utf-8',
                    )

                except BrokenPipeError:
                    logging.info(
                        "BrokenPipe err catch  ** while sending EOF or JSON"
                    )

                except ConnectionResetError:
                    logging.info(
                        "ConnectionReset err catch  ** while sending EOF or JSON"
                    )

            else:
                try:
                    cmd_tree_runner.run_dui_command(cmd_dict, self)
                    logging.info("sending /*EOF*/ (Dui2 CMD)")
                    spit_out(
                        str_out = '/*EOF*/', req_obj = self,
                        out_type = 'utf-8'
                    )

                except BrokenPipeError:
                    logging.info(
                        "** BrokenPipe err catch  ** while sending EOF or JSON"
                    )

                except ConnectionResetError:
                    logging.info(
                        "ConnectionReset err catch  ** while sending EOF or JSON"
                    )

        def do_GET(self):

            try:
                self.send_response(200)

            except AttributeError:
                logging.info("Attribute Err catch, not supposed send header info #3")

            url_path = self.path
            url_dict = parse_qs(urlparse(url_path).query)
            try:
                tmp_cmd2lst = url_dict["cmd_lst"]
                logging.info("tmp_cmd2lst =" + str(tmp_cmd2lst))

            except KeyError:
                logging.info("no command in request (Key err catch )")
                try:
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()

                except AttributeError:
                    logging.info(
                        "Attribute Err catch, not supposed send header info #4"
                    )

                spit_out(
                    str_out = 'no command in request (KeyError) ',
                    req_obj = self, out_type = 'utf-8'
                )
                spit_out(
                    str_out = '/*EOF*/', req_obj = self, out_type = 'utf-8'
                )
                return

            cmd_lst = []
            for inner_str in tmp_cmd2lst:
                cmd_lst.append(inner_str.split(" "))

            nod_lst = []
            try:
                for inner_str in url_dict["nod_lst"]:
                    nod_lst.append(int(inner_str))

            except KeyError:
                logging.info("no node number provided")

            cmd_dict = {"nod_lst":nod_lst,
                        "cmd_lst":cmd_lst}
            try:
                #lst_out = []
                lst_out = cmd_tree_runner.run_get_data(cmd_dict)

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
                        str_out = json_str, req_obj = self,
                        out_type = 'utf-8'
                    )
                    if lst_out == ['closed received']:
                        logging.info("Client app closed")
                        logging.info("run_local =" + str(run_local))
                        sep_lin = "#" * 44 + "\n"
                        if run_local == True:
                            logging.info(
                                " closing the server as it is running in " +
                                "\n  the same computer as the client \n"
                            )
                            self.server.shutdown()

                        else:
                            logging.info(
                                " keeping server running as the client might" +
                                "\n  need to continue processing the same \n" +
                                " images latter \n"
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

                logging.info("sending /*EOF*/ (Get)")
                spit_out(
                    str_out = '/*EOF*/', req_obj = self, out_type = 'utf-8'
                )

            except BrokenPipeError:
                logging.info("BrokenPipe err catch  while sending EOF or JSON")

            except ConnectionResetError:
                logging.info(
                    "ConnectionReset err catch  ** while sending EOF or JSON"
                )

        def log_message(self, format, *args):
            if run_local:
                return
                log_full_str = self.address_string() + " => " + \
                               self.log_date_time_string() + "  " + str(args)

                print(log_full_str)

            else:
                return

    ################################################ PROPER MAIN

    data_init = ini_data()
    data_init.set_data(par_def)

    init_param = format_utils.get_par(par_def, sys.argv[1:])
    logging.info("init_param(server) =" + str(init_param))

    PORT = int(init_param["port"])
    HOST = init_param["host"]

    if init_param["all_local"].lower() == "true":
        run_local = True

    else:
        run_local = False

    logging.info("run_local = " + str(run_local))

    if run_local:
        tree_dic_lst = []

    else:
        tree_ini_path = init_param["init_path"]
        if tree_ini_path == None:
            logging.info("\n NOT GIVEN init_path")
            logging.info(" using the dir from where the commad 'dui_server' was invoqued")
            tree_ini_path = os.getcwd()

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

    launch_success = False
    n_secs = 2
    while launch_success == False:
        try:
            with socketserver.ThreadingTCPServer(
                (HOST, PORT), ReqHandler
            ) as http_daemon:

                logging.info(
                    "serving at:{host:" + str(HOST) + " port:" + str(PORT) + "}"
                )
                launch_success = True

                connection_out.send(PORT)
                connection_out.close()

                try:
                    http_daemon.serve_forever()

                except KeyboardInterrupt:
                    logging.info("caling server_close()")
                    http_daemon.server_close()

        except OSError:
            PORT += 1
            launch_success = False
            logging.info("OS err catch, trying again in" + str(n_secs) + "secs")
            time.sleep(n_secs)
