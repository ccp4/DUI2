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
        while True:
            tmp_dat = req_get.raw.read(1)
            single_char = str(tmp_dat.decode('utf-8'))
            line_str += single_char
            if single_char == '\n':
                str_lst.append(line_str[:-1])
                line_str = ''

            elif line_str[-7:] == '/*EOF*/':
                print('>>  /*EOF*/  <<')
                break

        json_out = json.loads(str_lst[0])

        to_debugg = '''
        try:
            print("json_out:", json_out)

        except UnicodeEncodeError:
            print("UnicodeEncodeError")
        '''

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
            tmp_dat = self.request.raw.read(1)
            single_char = str(tmp_dat.decode('utf-8'))
            line_str += single_char
            if single_char == '\n':
                if not_yet_read:
                    not_yet_read = False
                    nod_lin_num = int(line_str.split("=")[1])
                    self.lin_num = nod_lin_num
                    print("\n QThread.lin_num =", self.lin_num)
                    self.first_line.emit(self.lin_num)

                else:
                    self.new_line_out.emit(line_str, self.lin_num)

                line_str = ''

            elif line_str[-7:] == '/*EOF*/':
                #TODO: consider a different Signal to say finished
                print('>>  /*EOF*/  <<')
                break

            self.usleep(1)


class CommandParamControl:
    '''
    keeps track of command to run with parameters included
    '''
    def __init__(self, main_command = None, param_list = []):
        self.cmd = str(main_command)
        self.par_lst = list(param_list)


    def set_parameter(self, param, value):
        self.par_lst.append([param, value])

    def get_full_command_list(self):
        str_out = self.cmd + " "
        for par in self.par_lst:
            par_str = par[0] + "=" + par[1]
            str_out += par_str

        return str_out


if __name__ == "__main__":
    tst_cmd = CommandParamControl("my_cmd")
    tst_cmd.set_parameter("new_param", "new_value")
    print("cmd_lst =", tst_cmd.get_full_command_list())


