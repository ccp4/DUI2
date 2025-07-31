import sys, json, os, logging, platform

from dui2.client.q_object import MainObject
from dui2.client.init_firts import ini_data
from dui2.shared_modules import format_utils, all_local_gui_connector

from dui2.server import multi_node
from dui2.server.init_first import ini_data as server_ini_data

from dui2.shared_modules.qt_libs import *

def main():

    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["WAYLAND_DISPLAY"] = ""

    print("\n platform.system()", platform.system())
    if platform.system() == "Windows":
        win_str = "true"

    else:
        win_str = "false"

    print("win_str =", win_str, "\n")
    par_def = (
        ("init_path", None),
        ("import_init", None),
        ("all_local", "true"),
        ("windows_exe", win_str),
    )
    data_init = ini_data()
    data_init.set_data(par_def = par_def)

    format_utils.print_logo()

    server_data_init = server_ini_data()
    server_data_init.set_data(par_def = par_def)

    tmp_dat_dir = format_utils.create_tmp_dir()

    data_init.set_tmp_dir(tmp_dat_dir)

    init_param = format_utils.get_par(par_def, sys.argv[1:])
    run_local = True
    tree_ini_path = init_param["init_path"]
    if tree_ini_path == None:
        logging.info(
            " using the dir from where the commad 'dui2_server_side' was invoqued"
        )
        tree_ini_path = os.getcwd()

    #tree_dic_lst = iter_dict(tree_ini_path, 0)
    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

        cmd_runner = multi_node.Runner(
            recovery_data = runner_data, dat_ini = server_data_init
        )

    except FileNotFoundError:
        cmd_runner = multi_node.Runner(
            recovery_data = None, dat_ini = server_data_init
        )

    cmd_runner.set_dir_path(tree_ini_path)
    app = QApplication(sys.argv)

    m_gui_obj = all_local_gui_connector.MainGuiObject(
        parent = app, cmd_tree_runner = cmd_runner
    )
    m_obj = MainObject(parent = app, multi_runner = m_gui_obj)
    sys.exit(app.exec_())


