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

import json, os, sys, time, logging

from dui2.server import multi_node
from dui2.server.data_n_json import spit_out

from dui2.shared_modules.format_utils import split_w_quotes

class ReqHandler(object):
    def __init__(self, runner_in):
        self.tree_runner = runner_in

    def fake_post(self, url_dict = None, call_obj = None):
        print("\n url_dict =" + str(url_dict))

        tmp_cmd2lst = url_dict["cmd_lst"]
        print("tmp_cmd2lst =" + str(tmp_cmd2lst))

        cmd_lst = []
        for inner_str in tmp_cmd2lst:
            cmd_lst.append(split_w_quotes(inner_str))

        nod_lst = []
        try:
            for inner_str in url_dict["nod_lst"]:
                nod_lst.append(int(inner_str))

        except KeyError:
            logging.info("no node number provided")

        cmd_dict = {"nod_lst":nod_lst,
                    "cmd_lst":cmd_lst}

        found_dials_command = False
        logging.info("cmd_lst = " + str(cmd_lst))
        for inner_lst in cmd_lst:
            for single_str in inner_lst:
                if "dials" in single_str:
                    found_dials_command = True

                logging.info("single_str = " + single_str)

        if found_dials_command:
            self.tree_runner.run_dials_command(cmd_dict, call_obj)
            logging.info("sending /*EOF*/ (Dials CMD)")
            spit_out(
                str_out = '/*EOF*/', req_obj = call_obj, out_type = 'utf-8'
            )

        else:
            self.tree_runner.run_dui_command(cmd_dict, call_obj)
            logging.info("sending /*EOF*/ (Dui CMD)")
            spit_out(
                str_out = '/*EOF*/', req_obj = call_obj, out_type = 'utf-8'
            )

    def fake_get(self, url_dict = None, call_obj = None):
        logging.info("url_dict =" + str(url_dict))
        tmp_cmd2lst = url_dict["cmd_str"]

        nod_lst = []
        try:
            for inner_str in url_dict["nod_lst"]:
                nod_lst.append(int(inner_str))

        except KeyError:
            logging.info("no node number provided")
            print("no node number provided")


        cmd_dict = {"nod_lst":nod_lst,
                    "lst_wt_cmd":tmp_cmd2lst}


        lst_out = self.tree_runner.run_get_data(cmd_dict)

        if type(lst_out) is list or type(lst_out) is dict:
            spit_out(
                str_out = lst_out, req_obj = call_obj, out_type = 'utf-8'
            )

        elif type(lst_out) is bytes:
            siz_dat = str(len(lst_out))
            spit_out(
                str_out = "size =" + " " + str(siz_dat), req_obj = call_obj
            )
            spit_out(str_out = lst_out, req_obj = call_obj)



