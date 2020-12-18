from PySide2.QtCore import *
import requests, json, os, sys

from gui_utils import AdvancedParameters, widgets_defs

try:
    from shared_modules import format_utils

except ModuleNotFoundError:
    '''
    This trick to import the format_utils module can be
    removed once the project gets properly packaged
    '''
    comm_path = os.path.abspath(__file__)[0:-20] + "shared_modules"
    print("comm_path: ", comm_path, "\n")
    sys.path.insert(1, comm_path)
    import format_utils

uni_url = 'http://localhost:8080/'

def build_advanced_params_widget(cmd_str):
    cmd = {"nod_lst":"", "cmd_lst":[cmd_str]}
    lst_params = json_data_request(uni_url, cmd)
    lin_lst = format_utils.param_tree_2_lineal(lst_params)
    par_def = lin_lst()
    advanced_parameters = AdvancedParameters()
    advanced_parameters.build_pars(par_def)
    return advanced_parameters


def copy_lst_nodes(old_lst_nodes):
    new_lst = []
    for old_node in old_lst_nodes:
        cp_new_node = {
            'lin_num': int(old_node["lin_num"]),
            'status': str(old_node["status"]),
            'cmd2show': list(old_node["cmd2show"]),
            'child_node_lst': list(old_node["child_node_lst"]),
            'parent_node_lst': list(old_node["parent_node_lst"])
        }
        new_lst.append(cp_new_node)

    return new_lst

def json_data_request(url, cmd):
    try:
        req_get = requests.get(url, stream = True, params = cmd)
        str_lst = []
        line_str = ''

        str_lst = []
        while True:
            tmp_dat = req_get.raw.readline()
            line_str = str(tmp_dat.decode('utf-8'))
            if line_str[-7:] == '/*EOF*/':
                print('/*EOF*/ received')
                break

            else:
                str_lst.append(line_str)

        json_out = json.loads(str_lst[0])

    except requests.exceptions.RequestException:
        print("\n requests.exceptions.RequestException \n")
        json_out = None

    return json_out

class Run_n_Output(QThread):
    new_line_out = Signal(str, int)
    first_line = Signal(int)
    def __init__(self, request):
        super(Run_n_Output, self).__init__()
        self.request = request
        self.lin_num = None

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
                nod_lin_num = int(line_str.split("=")[1])
                self.lin_num = nod_lin_num
                print("\n QThread.lin_num =", self.lin_num)
                self.first_line.emit(self.lin_num)

            else:
                self.new_line_out.emit(line_str, self.lin_num)

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

    def set_parameter(self, new_name, new_value):
        already_here = False
        for single_par in self.par_lst:
            if single_par["name"] == new_name:
                single_par["value"] = new_value
                already_here = True

        if not already_here:
            self.par_lst.append({"name":new_name, "value":new_value})

    def set_custom_parameter(self, new_custom_parameter):
        self.custm_param = new_custom_parameter

    def clone_from(self, lst_par_in):
        print(" Clone_from ------------")
        self.par_lst = []
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
    tst_cmd.set_custom_parameter("random_custom command _5")
    print("cmd_lst =", tst_cmd.get_full_command_string())
