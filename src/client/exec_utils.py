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
import requests, json, os, sys, zlib

from client.gui_utils import AdvancedParameters, widgets_defs
from client.init_firts import ini_data
from shared_modules import format_utils

def get_optional_list(cmd_str):
    cmd = {"nod_lst":"", "cmd_lst":[cmd_str]}

    data_init = ini_data()
    uni_url = data_init.get_url()
    print("uni_url(get_optional_list) =", uni_url)

    lst_opt = json_data_request(uni_url, cmd)

    return lst_opt


def build_advanced_params_widget(cmd_str, h_box_search):
    cmd = {"nod_lst":"", "cmd_lst":[cmd_str]}

    data_init = ini_data()
    uni_url = data_init.get_url()
    print("uni_url(build_advanced_params_widget) =", uni_url)

    lst_params = json_data_request(uni_url, cmd)
    lin_lst = format_utils.param_tree_2_lineal(lst_params)
    par_def = lin_lst()
    advanced_parameters = AdvancedParameters()
    advanced_parameters.build_pars(par_def, h_box_search)
    return advanced_parameters


def json_data_request(url, cmd):
    try:
        print("attempting to request to:", url, ", with:", cmd)
        req_get = requests.get(url, stream = True, params = cmd, timeout = 3)
        print("starting request")
        str_lst = ''
        line_str = ''
        json_out = ""
        times_loop = 10
        for count_times in range(times_loop):
            print("count_times =", count_times)
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
        print(" ... Connection err catch  (json_data_request) ...")
        json_out = None

    except requests.exceptions.RequestException:
        print(" ... requests.exceptions.RequestException (json_data_request)")
        json_out = None

    return json_out


class Mtz_Data_Request(QThread):
    update_progress = Signal(int)
    done_download = Signal(bytes)
    def __init__(self, url, cmd):
        super(Mtz_Data_Request, self).__init__()
        self.url = url
        self.cmd = cmd

    def run(self):
        try:
            req_get = requests.get(
                self.url, stream = True, params = self.cmd, timeout = 3
            )
            total_size = int(req_get.headers.get('content-length', 0)) + 1
            print("total_size =", total_size)

            block_size = 65536
            downloaded_size = 0
            compresed = bytes()
            for data in req_get.iter_content(block_size):
                compresed += data
                downloaded_size += block_size
                progress = int(100.0 * (downloaded_size / total_size))
                self.update_progress.emit(progress)

            mtz_data = zlib.decompress(compresed)
            print("mtz downloaded")
            print("type(mtz_data) =", type(mtz_data))

        except zlib.error:
            print("zlib. err catch(Mtz_Data_Request)")
            mtz_data = None

        except ConnectionError:
            print("\n Connection err catch (Mtz_Data_Request) \n")
            mtz_data = None

        except requests.exceptions.RequestException:
            print(
                "\n requests.exceptions.RequestException (Mtz_Data_Request) \n"
            )
            mtz_data = None

        self.done_download.emit(mtz_data)


class Run_n_Output(QThread):
    new_line_out = Signal(str, int, str)
    first_line = Signal(int)
    about_to_end = Signal(int)
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
                    print("\n *** Run_n_Output ... Index err catch *** \n")
                    not_yet_read = True

            else:
                self.new_line_out.emit(line_str, self.number, "Busy")

            self.usleep(1)

        self.about_to_end.emit(self.number)


class CommandParamControl:
    '''
    keeps track of command to run with parameters included
    '''
    def __init__(self, main_list = []):
        self.m_cmd_lst = main_list
        self.par_lst = []
        for n in range(len(self.m_cmd_lst)):
            self.par_lst.append([])

        self.custm_param = None
        print("\n New 'CommandParamControl':")
        print(
            "(cmd, par_lst) =",
            self.m_cmd_lst, self.par_lst, " --------- \n"
        )
        print(" par_lst(__init__) =", self.par_lst)

    def reset_all_params(self):
        self.par_lst = [[]]
        self.custm_param = None

    def set_new_main_command(self, new_command):
        print("CommandParamControl ... set_new_main_command:", new_command)
        dials_command = "dials." + new_command
        self.m_cmd_lst = [dials_command]
        print("\n self.m_cmd_lst  =", self.m_cmd_lst)

    def set_parameter(self, new_name, new_value, lst_num = 0):
        print(" par_lst(set_parameter) ini =", self.par_lst)
        already_here = False
        for single_par in self.par_lst[lst_num]:
            if single_par["name"] == new_name:
                single_par["value"] = new_value
                already_here = True

        if not already_here:
            self.par_lst[lst_num].append({"name":new_name, "value":new_value})

        print(" par_lst(set_parameter) end =", self.par_lst)

    def set_all_parameters(self, lst_of_lst):
        print("set_all_parameters")
        print("lst_of_lst =", lst_of_lst)
        self.par_lst = []
        self.custm_param = None

        for inner_lst in lst_of_lst:
            print("inner_lst =", inner_lst)
            build_lst = []
            for inner_par_val in inner_lst:
                print("inner_par_val =", inner_par_val)
                try:
                    build_lst.append(
                        {
                            "name":str(inner_par_val[0]),
                            "value":str(inner_par_val[1])
                        }
                    )
                except IndexError:
                    print("index err catch, not adding new parameter")

            self.par_lst.append(build_lst)

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

    def clone_from_list(self, lst_par_in):
        print(" clone_from_list ------------")
        print("lst_par_in =", lst_par_in)

        self.m_cmd_lst = []
        for inner_lst in lst_par_in:
            self.m_cmd_lst.append(str(inner_lst[0]))

        self.par_lst = []
        for inner_lst in lst_par_in:
            lst_par = []
            for str_elem in inner_lst:
                if "=" in str_elem:
                    lst_par.append(str_elem)

            inner_par_lst = []
            for str_elem in lst_par:
                tmp_lst = str_elem.split("=")
                inner_par_lst.append(
                    {"name":str(tmp_lst[0]), "value":str(tmp_lst[1])}
                )

            self.par_lst.append(inner_par_lst)

        print("self.par_lst =", self.par_lst)
        #TODO remember to handle "self.custm_param"

    def get_all_params(self):
        return self.par_lst[0], self.custm_param

    def get_full_command_list(self):
        print("\n *** get_full_command_list")
        print("self.par_lst =", self.par_lst)
        print("self.m_cmd_lst =", self.m_cmd_lst)

        lst_out = []
        for lst_num in range(len(self.m_cmd_lst)):
            str_out = str(self.m_cmd_lst[lst_num])
            for par in self.par_lst[lst_num]:
                par_str = " " + par["name"] + "=" + par["value"]
                str_out += par_str

            if self.custm_param is not None:
                str_out += " " + str(self.custm_param)

            lst_out.append(str_out)

        print("\n lst_out =", lst_out, "\n")
        return lst_out


if __name__ == "__main__":
    tst_cmd = CommandParamControl(["my_cmd"])

    tst_cmd.set_parameter("new_param", "new_value")
    print("cmd_lst =", tst_cmd.get_full_command_list())
    tst_cmd.set_parameter("new_param_2", "new_value_2")
    print("cmd_lst =", tst_cmd.get_full_command_list())
    tst_cmd.set_parameter("random_param_n", "random_value_n")
    print("cmd_lst =", tst_cmd.get_full_command_list())

    tst_cmd.set_parameter("new_param", "value_2")
    print("cmd_lst =", tst_cmd.get_full_command_list())
    tst_cmd.set_parameter("new_param_2", "value_3")
    print("cmd_lst =", tst_cmd.get_full_command_list())
    tst_cmd.set_parameter("random_param_n", "value_4")
    print("cmd_lst =", tst_cmd.get_full_command_list())
    same = tst_cmd.set_custom_parameter("random_custom command _5")
    print("cmd_lst =", tst_cmd.get_full_command_list())
    print("same =", same)

    print("\n" * 3)

    tst_cmd.set_all_parameters([[["random_param_#", "value_#"]]])
    print("cmd_lst =", tst_cmd.get_full_command_list())
