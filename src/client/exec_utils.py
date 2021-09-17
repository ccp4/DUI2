"""
DUI2's client's side contol and run utilities

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


from PySide2.QtCore import *
import requests, json, os, sys

from gui_utils import AdvancedParameters, widgets_defs
from init_firts import ini_data


try:
    from shared_modules import format_utils

except ModuleNotFoundError:
    comm_path = os.path.abspath(__file__)[0:-20] + "shared_modules"
    print("comm_path: ", comm_path, "\n")
    sys.path.insert(1, comm_path)
    import format_utils


def build_advanced_params_widget(cmd_str):
    cmd = {"nod_lst":"", "cmd_lst":[cmd_str]}

    data_init = ini_data()
    uni_url = data_init.get_url()
    print("uni_url(build_advanced_params_widget) =", uni_url)

    lst_params = json_data_request(uni_url, cmd)
    lin_lst = format_utils.param_tree_2_lineal(lst_params)
    par_def = lin_lst()
    advanced_parameters = AdvancedParameters()
    advanced_parameters.build_pars(par_def)
    return advanced_parameters


def json_data_request(url, cmd):
    try:
        req_get = requests.get(url, stream = True, params = cmd, timeout = 3)
        str_lst = ''
        line_str = ''

        #while True:
        times_loop = 10
        json_out = ""
        for count_times in range(times_loop):
            tmp_dat = req_get.raw.readline()
            line_str = str(tmp_dat.decode('utf-8'))
            if line_str[-7:] == '/*EOF*/':
                print('/*EOF*/ received')
                break

            else:
                str_lst = line_str

            if count_times == times_loop - 1:
                print('to many "lines" in http response')
                json_out = None

        if json_out is not None:
            json_out = json.loads(str_lst)

    except ConnectionError:
        print("\n ConnectionError (json_data_request) \n")
        json_out = None

    except requests.exceptions.RequestException:
        print("\n requests.exceptions.RequestException (json_data_request) \n")
        json_out = None

    return json_out


class Run_n_Output(QThread):
    new_line_out = Signal(str, int)
    first_line = Signal(int)
    def __init__(self, request):
        super(Run_n_Output, self).__init__()
        self.request = request
        self.number = None

    def run(self):

        line_str = ''
        not_yet_read = True
        while True:
            tmp_dat = self.request.raw.readline()
            line_str = str(tmp_dat.decode('utf-8'))
            if line_str[-7:] == '/*EOF*/':
                #TODO: consider a different Signal to say finished
                print('>>  /*EOF*/  <<')
                break

            if not_yet_read:
                not_yet_read = False

                try:
                    nod_p_num = int(line_str.split("=")[1])
                    self.number = nod_p_num
                    print("\n QThread.number =", self.number)
                    self.first_line.emit(self.number)

                except IndexError:
                    print("\n *** Run_n_Output ... IndexError *** \n")
                    not_yet_read = True

            else:
                self.new_line_out.emit(line_str, self.number)

            self.usleep(1)


class CommandParamControl:
    '''
    keeps track of command to run with parameters included
    '''
    def __init__(self, main_command = None, param_list = []):
        self.cmd = str(main_command)
        self.par_lst = list(param_list)
        self.custm_param = None
        print("\n New 'CommandParamControl':")
        print(
            "(cmd, par_lst) =",
            self.cmd, self.par_lst, " --------- \n"
        )
        print(" par_lst(__init__) =", self.par_lst)

    def reset_all_params(self):
        self.par_lst = []
        self.custm_param = None

    def set_parameter(self, new_name, new_value):
        print(" par_lst(set_parameter) ini =", self.par_lst)
        already_here = False
        for single_par in self.par_lst:
            if single_par["name"] == new_name:
                single_par["value"] = new_value
                already_here = True

        if not already_here:
            self.par_lst.append({"name":new_name, "value":new_value})
        print(" par_lst(set_parameter) end =", self.par_lst)

    def set_custom_parameter(self, new_custom_parameter):
        is_same = False
        if new_custom_parameter == self.custm_param:
            is_same = True

        self.custm_param = new_custom_parameter
        return is_same

    def set_connections(self, nod_lst, parent_s):
        max_nod_num = 0
        for node in nod_lst:
            if node["number"] > max_nod_num:
                max_nod_num = node["number"]

        self.number = max_nod_num + 1
        self.status = 'Ready'
        self.parent_node_lst = list(parent_s)

    def add_or_remove_parent(self, nod_num):
        print("New node to add or remove:", nod_num)

        if nod_num not in self.parent_node_lst:
            self.parent_node_lst.append(nod_num)

        elif len(self.parent_node_lst) > 1:
            self.parent_node_lst.remove(nod_num)

        else:
            print("Unable to remove unique parent")

    def clear_parents(self):
        print("old parent_node_lst =", self.parent_node_lst)
        self.parent_node_lst = [int(max(self.parent_node_lst))]
        print("new parent_node_lst =", self.parent_node_lst)

    def clone_from_command_param(self, cmd_par_obj):
        self.cmd = str(cmd_par_obj.cmd)
        self.par_lst = []
        for elem in cmd_par_obj.par_lst:
            self.par_lst.append(
                {"name":str(elem["name"]), "value":str(elem["value"])}
            )
        self.set_custom_parameter(cmd_par_obj.custm_param)

        print(
            "\n cloning with:\n", self.cmd, "\n",
            self.par_lst, "\n", self.custm_param
        )

    def clone_from_list(self, lst_par_in):
        print(" clone_from_list ------------")
        self.par_lst = list([])
        print("lst_par_in =", lst_par_in)
        lst_par = []
        for str_elem in lst_par_in:
            if "=" in str_elem:
                lst_par.append(str_elem)

        for str_elem in lst_par:
            tmp_lst = str_elem.split("=")
            self.par_lst.append(
                {"name":str(tmp_lst[0]), "value":str(tmp_lst[1])}
            )

        print("lst_par =", lst_par)
        print("self.par_lst =", self.par_lst)
        #TODO remember to handle "self.custm_param"

    def get_all_params(self):
        return self.par_lst, self.custm_param

    def get_full_command_string(self):
        print("\n *** get_full_command_string")
        str_out = str(self.cmd)
        print("self.par_lst =", self.par_lst)
        for par in self.par_lst:
            par_str = " " + par["name"] + "=" + par["value"]
            str_out += par_str

        if self.custm_param is not None:
            str_out += " " + str(self.custm_param)

        print("\n str_out =", str_out, "\n")

        return str_out


if __name__ == "__main__":
    tst_cmd = CommandParamControl("my_cmd")

    tst_cmd.set_parameter("new_param", "new_value")
    print("cmd_lst =", tst_cmd.get_full_command_string())
    tst_cmd.set_parameter("new_param_2", "new_value_2")
    print("cmd_lst =", tst_cmd.get_full_command_string())
    tst_cmd.set_parameter("random_param_n", "random_value_n")
    print("cmd_lst =", tst_cmd.get_full_command_string())

    tst_cmd.set_parameter("new_param", "value_2")
    print("cmd_lst =", tst_cmd.get_full_command_string())
    tst_cmd.set_parameter("new_param_2", "value_3")
    print("cmd_lst =", tst_cmd.get_full_command_string())
    tst_cmd.set_parameter("random_param_n", "value_4")
    print("cmd_lst =", tst_cmd.get_full_command_string())
    same = tst_cmd.set_custom_parameter("random_custom command _5")
    print("cmd_lst =", tst_cmd.get_full_command_string())
    print("same =", same)
