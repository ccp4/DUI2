import sys, json, os
from client.q_object import MainObject
from client.init_firts import ini_data
from shared_modules import format_utils, all_local_gui_connector
from server.data_n_json import iter_dict
from server import multi_node

from PySide2.QtCore import *
from PySide2.QtWidgets import *


if __name__ == '__main__':

    par_def = (
        ("init_path", None),
        ("windows_exe", "false"),
    )
    data_init = ini_data()
    data_init.set_data(par_def = par_def)

    init_param = format_utils.get_par(par_def, sys.argv[1:])
    run_local = True
    tree_ini_path = init_param["init_path"]
    if tree_ini_path == None:
        print(" using the dir from where the commad 'dui_server' was invoqued")
        tree_ini_path = os.getcwd()

    print("\n using init path as: <<", tree_ini_path, ">> \n")
    tree_dic_lst = iter_dict(tree_ini_path, 0)
    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

        cmd_runner = multi_node.Runner(
            recovery_data = runner_data, dat_ini = data_init
        )

    except FileNotFoundError:
        cmd_runner = multi_node.Runner(
            recovery_data = None, dat_ini = data_init
        )

    cmd_runner.set_dir_tree(tree_dic_lst)
    app = QApplication(sys.argv)

    m_gui_obj = all_local_gui_connector.MainGuiObject(
        parent = app, cmd_tree_runner = cmd_runner
    )
    m_obj = MainObject(parent = app, multi_runner = m_gui_obj)
    sys.exit(app.exec_())


