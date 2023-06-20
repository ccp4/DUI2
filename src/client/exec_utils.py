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
import requests, json, os, sys, zlib, time, logging

from client.gui_utils import AdvancedParameters, widgets_defs
from client.init_firts import ini_data
from shared_modules import format_utils

class get_request_shot(QObject):
    def __init__(self, parent = None, params_in = None, main_handler = None):
        super(get_request_shot, self).__init__(parent)
        if main_handler == None:
            data_init = ini_data()
            uni_url = data_init.get_url()
            req = requests.get(uni_url, stream = True, params = params_in)
            compresed = req.content
            try:
                self.to_return = zlib.decompress(compresed)

            except zlib.error:
                logging.info("zlib. err catch (get_request_shot)")
                self.to_return = None

            self.done = True

        else:
            self.done = False
            main_handler.get_from_main_dui(params_in, self)
            #self.to_return = None

    def get_it_str(self, data_comming):
        self.to_return = data_comming
        self.done = True

    def get_it_bin(self, data_comming):
        logging.info("type(data_comming) = " + str(type(data_comming)))
        self.to_return = data_comming
        self.done = True


    def result_out(self):
        while self.done == False:
            time.sleep(0.1)

        return self.to_return


class get_req_json_dat(QObject):
    def __init__(self, parent = None, params_in = None, main_handler = None):
        super(get_req_json_dat, self).__init__(parent)
        if main_handler == None:
            data_init = ini_data()
            uni_url = data_init.get_url()
            try:
                req_get = requests.get(
                    uni_url, stream = True, params = params_in, timeout = 45
                )
                logging.info("starting request")
                print("params_in =", params_in)
                str_lst = ''
                line_str = ''
                json_out = ''
                times_loop = 10
                for count_times in range(times_loop):
                    tmp_dat = req_get.raw.readline()
                    line_str = str(tmp_dat.decode('utf-8'))
                    if '/*EOF*/' in line_str:
                        logging.info('/*EOF*/ received')
                        break

                    else:
                        str_lst = line_str
                        #logging.info("str_lst =", str_lst)

                    if count_times == times_loop - 1:
                        logging.info('to many "lines" in http response')
                        json_out = None

            except ConnectionError:
                logging.info(" ... Connection err catch (get_req_json_dat) ...")
                json_out = None

            except requests.exceptions.RequestException:
                logging.info(
                    "..requests.exceptions.RequestException (get_req_json_dat)"
                )
                json_out = None

            if json_out is not None:
                json_out = json.loads(str_lst)

            self.to_return = json_out

        else:
            logging.info("main_handler =" + str(main_handler))
            main_handler.get_from_main_dui(params_in, self)

    def get_it_str(self, data_comming):
        #logging.info("data_comming =", data_comming)
        self.to_return = data_comming

    def get_it_bin(self, data_comming):
        #logging.info("data_comming =", data_comming)
        self.to_return = data_comming


    def result_out(self):
        return self.to_return ##### search here for the all_local_all_ram issue


class get_request_real_time(QThread):
    prog_new_stat = Signal(int)
    load_ended = Signal(bytes)
    def __init__(self, params_in = None, main_handler = None):
        super(get_request_real_time, self).__init__()
        data_init = ini_data()
        self.url = data_init.get_url()
        self.params = params_in
        self.my_handler = main_handler

    def run(self):
        if self.my_handler == None:
            try:
                req_get = requests.get(
                    self.url, stream = True, params = self.params, timeout = 65
                )
                req_head = req_get.headers.get('content-length', 0)
                total_size = int(req_head) + 1
                logging.info("total_size =" + str(total_size))
                block_size = int(total_size / 6 * 1024)
                max_size = 16384
                #max_size = 65536
                if block_size > max_size:
                    block_size = max_size

                logging.info("block_size =" + str(block_size))

                downloaded_size = 0
                compresed = bytes()
                for data in req_get.iter_content(block_size):
                    compresed += data
                    downloaded_size += block_size
                    progress = int(100.0 * (downloaded_size / total_size))
                    self.prog_new_stat.emit(progress)

                end_data = zlib.decompress(compresed)
                logging.info("get_request_real_time ... downloaded")

            except zlib.error:
                logging.info("zlib. err catch(get_request_real_time) <<")
                end_data = None

            except ConnectionError:
                logging.info("\n Connection err catch (get_request_real_time) \n")
                end_data = None

            except requests.exceptions.RequestException:
                logging.info(
                    "\n requests.exceptions.ReqExp (get_request_real_time) \n"
                )
                end_data = None

            self.load_ended.emit(end_data)

        else:
            self.prog_new_stat.emit(50)
            logging.info("self.my_handler =" + str(self.my_handler))
            self.my_handler.get_from_main_dui(self.params, self)

    def get_it_str(self, data_comming):
        self.prog_new_stat.emit(95)
        self.load_ended.emit(data_comming)

    def get_it_bin(self, data_comming):
        self.prog_new_stat.emit(95)
        self.load_ended.emit(data_comming)


def get_optional_list(cmd_str, handler_in):
    cmd = {"nod_lst":"", "cmd_str":[cmd_str]}
    lst_req = get_req_json_dat(params_in = cmd, main_handler = handler_in)
    lst_opt = lst_req.result_out()
    return lst_opt


def build_advanced_params_widget(cmd_str, h_box_search, handler_in):
    cmd = {"nod_lst":"", "cmd_str":[cmd_str]}

    lst_req = get_req_json_dat(params_in = cmd, main_handler = handler_in)
    lst_params = lst_req.result_out()

    lin_lst = format_utils.param_tree_2_lineal(lst_params)
    par_def = lin_lst()
    advanced_parameters = AdvancedParameters()
    advanced_parameters.build_pars(par_def, h_box_search)
    return advanced_parameters


def get_help_messages(handler_in):
    lst_cmd = [
        "import",
        "generate_mask",
        "apply_mask",
        "find_spots",
        "find_rotation_axis",
        "index",
        "ssx_index",
        "refine_bravais_settings",
        "reindex",
        "refine",
        "integrate",
        "ssx_integrate",
        "symmetry",
        "scale",
        "cosym",
        "slice_sequence",
        "merge",
        "combine_experiments",
        "export"
    ]
    #TODO change the name of one of the cmd_str variables
    help_dict = {}
    for cmd_str in lst_cmd:
        cmd = {"nod_lst":"", "cmd_str":["gh", cmd_str]}
        lst_req = get_req_json_dat(params_in = cmd, main_handler = handler_in)
        json_hlp = lst_req.result_out()
        #lst_hlp.append(json_hlp[0])
        help_dict[cmd_str] = json_hlp[0]

    return help_dict


class Mtz_Data_Request(QThread):
    update_progress = Signal(int)
    done_download = Signal(bytes)
    def __init__(self, cmd, main_handler):
        super(Mtz_Data_Request, self).__init__()
        self.cmd = cmd
        self.my_handler = main_handler
        self.r_time_req_lst = []

    def run(self):
        self.say_goodbye()
        self.r_time_req = get_request_real_time(
            params_in = self.cmd, main_handler = self.my_handler
        )
        self.r_time_req.prog_new_stat.connect(self.new_progress)
        self.r_time_req.load_ended.connect(self.finishing)
        self.r_time_req.start()

    def new_progress(self, prog_persent):
        self.update_progress.emit(prog_persent)

    def finishing(self, mtz_data):
        self.done_download.emit(mtz_data)

    def say_goodbye(self):
        try:
            self.r_time_req.quit()
            self.r_time_req.wait()

        except AttributeError:
            logging.info("not found QThread(get_request_real_time)")


class post_req_w_output(QThread):
    first_line = Signal(int)
    new_line_out = Signal(str, int, str)
    about_to_end = Signal(int, bool)
    def __init__(
        self, do_pred_n_rept = False, cmd_in = None, main_handler = None
    ):
        super(post_req_w_output, self).__init__()

        data_init = ini_data()
        self.uni_url = data_init.get_url()
        self.cmd = cmd_in
        self.my_handler = main_handler
        self.number = None
        self.do_predict_n_report = do_pred_n_rept

    def run(self):
        if self.my_handler == None:
            try:
                self.request = requests.post(
                    self.uni_url, stream = True, data = self.cmd
                )

                line_str = ''
                not_yet_read = True
                while True:
                    tmp_dat = self.request.raw.readline()
                    line_str = str(tmp_dat.decode('utf-8'))
                    if '/*EOF*/' in line_str :
                        #TODO: consider a different Signal to say finished
                        logging.info('>>  /*EOF*/  <<' + str(self.cmd))
                        break

                    if not_yet_read:
                        not_yet_read = False

                        try:
                            nod_p_num = int(line_str.split("=")[1])
                            self.number = nod_p_num
                            logging.info("\n QThread.number =" + str(self.number))
                            self.first_line.emit(self.number)

                        except IndexError:
                            logging.info(
                                "\n post_req_w_output ... Index err catch \n"
                            )
                            not_yet_read = True

                    else:
                        self.new_line_out.emit(line_str, self.number, "Busy")

                    self.usleep(1)

                self.about_to_end.emit(self.number, self.do_predict_n_report)

            except requests.exceptions.RequestException:
                logging.info(
                    "something went wrong with the request of " +
                    str(self.cmd)
                )
                #TODO: put inside this [except] some way to kill [self]

        else:
            self.done = False
            self.already_read = False
            self.my_handler.post_from_main_dui(self.cmd, self)

            while self.done == False:
                time.sleep(0.1)

        logging.info("ended post QThread")

    def get_it_str(self, line_str):
        if not self.already_read:
            try:
                nod_p_num = int(line_str.split("=")[1])
                self.number = nod_p_num
                self.first_line.emit(self.number)
                self.already_read = True

            except IndexError:
                logging.info("\n post_req_w_output ... Index err catch \n")

        elif '/*EOF*/' in line_str :
            self.about_to_end.emit(self.number, self.do_predict_n_report)
            self.done = True
            self.exit()
            self.wait()

        else:
            self.new_line_out.emit(line_str, self.number, "Busy")


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
        logging.info("\n New 'CommandParamControl':")
        logging.info(" par_lst(__init__) =" + str(self.par_lst))

    def reset_all_params(self):
        self.par_lst = [[]]
        self.custm_param = None

    def set_new_main_command(self, new_command):
        dials_command = "dials." + new_command
        self.m_cmd_lst = [dials_command]
        logging.info("\n self.m_cmd_lst  =" + str(self.m_cmd_lst))

    def set_parameter(self, new_name, new_value, lst_num = 0):
        logging.info(" par_lst(set_parameter) ini =" + str(self.par_lst))
        already_here = False
        for single_par in self.par_lst[lst_num]:
            if single_par["name"] == new_name:
                single_par["value"] = new_value
                already_here = True

        if not already_here:
            self.par_lst[lst_num].append({"name":new_name, "value":new_value})

        logging.info(" par_lst(set_parameter) end =" + str(self.par_lst))

    def set_all_parameters(self, lst_of_lst):
        logging.info("set_all_parameters")
        logging.info("lst_of_lst =" + str(lst_of_lst))
        self.par_lst = []
        self.custm_param = None

        for inner_lst in lst_of_lst:
            build_lst = []
            for inner_par_val in inner_lst:
                try:
                    build_lst.append(
                        {
                            "name":str(inner_par_val[0]),
                            "value":str(inner_par_val[1])
                        }
                    )
                except IndexError:
                    logging.info("index err catch, not adding new parameter")

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
        logging.info("New node to add or remove:" + str(nod_num))
        if nod_num not in self.parent_node_lst:
            self.parent_node_lst.append(nod_num)

        elif len(self.parent_node_lst) > 1:
            self.parent_node_lst.remove(nod_num)

        else:
            logging.info("Unable to remove unique parent")

    def clear_parents(self):
        self.parent_node_lst = [int(max(self.parent_node_lst))]

    def clone_from_list(self, lst_par_in):
        logging.info(" clone_from_list ------------")

        self.m_cmd_lst = []
        for inner_lst in lst_par_in:
            self.m_cmd_lst.append(str(inner_lst[0]))

        self.par_lst = []
        for inner_lst in lst_par_in:
            lst_par = []

            for pos, str_elem in enumerate(inner_lst):
                if "=" in str_elem or pos > 0:
                    lst_par.append(str_elem)

            inner_par_lst = []
            for str_elem in lst_par:
                if "=" in str_elem:
                    tmp_lst = str_elem.split("=")
                    inner_par_lst.append(
                        {"name":str(tmp_lst[0]), "value":str(tmp_lst[1])}
                    )
                elif lst_par_in[0][0] == "dials.import":
                    inner_par_lst.append({"name":"", "value":str(str_elem)})

            self.par_lst.append(inner_par_lst)

        logging.info("self.par_lst =" + str(self.par_lst))
        #TODO remember to handle "self.custm_param"

    def get_all_params(self):
        return self.par_lst[0], self.custm_param

    def get_full_command_list(self):
        logging.info("\n *** get_full_command_list")

        lst_out = []
        for lst_num in range(len(self.m_cmd_lst)):
            str_out = str(self.m_cmd_lst[lst_num])
            for par in self.par_lst[lst_num]:
                if par["name"] == "":
                    par_str = " " + par["value"]

                else:
                    par_str = " " + par["name"] + "=" + par["value"]

                str_out += par_str

            if self.custm_param is not None:
                str_out += " " + str(self.custm_param)

            lst_out.append(str_out)

        logging.info("\n lst_out =" + str(lst_out) + "\n")
        return lst_out


if __name__ == "__main__":
    tst_cmd = CommandParamControl(["my_cmd"])

    tst_cmd.set_parameter("new_param", "new_value")
    tst_cmd.set_parameter("new_param_2", "new_value_2")
    tst_cmd.set_parameter("random_param_n", "random_value_n")

    tst_cmd.set_parameter("new_param", "value_2")
    tst_cmd.set_parameter("new_param_2", "value_3")
    tst_cmd.set_parameter("random_param_n", "value_4")
    same = tst_cmd.set_custom_parameter("random_custom command _5")
    tst_cmd.set_all_parameters([[["random_param_#", "value_#"]]])
