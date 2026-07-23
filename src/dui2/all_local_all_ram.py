import sys, json, os, logging, platform

from dui2.shared_modules.format_utils import get_feedback_data
feedback_data_list = get_feedback_data()

from dui2.shared_modules.qt_libs import *

from dui2.client.q_object import MainObject
from dui2.client.init_firts import IniData
from dui2.shared_modules import format_utils, all_local_gui_connector

from dui2.server import multi_node
from dui2.server.init_first import IniData as ServerIniData


#logging.basicConfig(filename='run_dui2_all_local_all_ram.log', level=logging.DEBUG)

def main():
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

    win_str = "false"
    if platform.system() == "Windows":
        print("running on Windows")
        win_str = "true"

    elif platform.system() == "Linux":
        print("running on Linux")
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        os.environ["WAYLAND_DISPLAY"] = ""

    else:
        print("neither Linux or Windows")

    par_def = (
        ("chdir", None),
        ("ask_for_dir", "false"),
        ("limit_path", None),
        ("import_init", None),
        ("all_local", "true"),
        ("windows_exe", win_str),
        ("token", "dummy_4_now"),
        ("upload_mtz_url", "http://localhost:8080/"),
        ("cloudrun_id", "xxxx-xxxx-xxxx-xxxx"),
    )


    init_param = format_utils.get_par(par_def, sys.argv[1:])
    data_init = IniData()
    data_init.set_data(par_def = par_def)
    app = QApplication(sys.argv)

    if init_param["ask_for_dir"] == "false":
        print("Using same dir where Dui2 were invoked from as working dir")
        dir_2_change = os.getcwd()

    else:
        dlg_msg = QDialog()
        dlg_msg.setWindowTitle("Starting DUI")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "\nPlease choose a directory " +
            "\n    to save DUI data in   \n")
        )
        ok_butt = QPushButton("Ok/Close")
        layout.addWidget(ok_butt)
        dlg_msg.setLayout(layout)
        ok_butt.clicked.connect(dlg_msg.accept)

        dlg_msg.exec_()

        dir_2_change = QFileDialog.getExistingDirectory(
            caption = "Chose working directory"
        )

        if dir_2_change != '':
            print("Using ", dir_2_change, " as working dir")

        else:
            print("Canceled Operation")
            dir_2_change = os.getcwd()
            #TODO consider interrupting here with the next t line
            #sys.exit(1)

    format_utils.print_logo()

    server_data_init = ServerIniData()
    server_data_init.set_data(par_def = par_def)

    #TODO: check if the following line is useful
    run_local = True

    if dir_2_change is not None:
        try:
            os.chdir(dir_2_change)
            first_import_init = data_init.get_import_init()
            if first_import_init == None:
                data_init.set_import_init(str(dir_2_change))

        except FileNotFoundError:
            print(
                "unable to change to directory: ", dir_2_change,
                "File Not Found Err Catch"
            )

    if init_param["chdir"] is not None:
        try:
            os.chdir(init_param["chdir"])

        except FileNotFoundError:
            print(
                "unable to change to directory: ", init_param["chdir"],
                "File Not Found Err Catch"
            )

    tmp_dat_dir = format_utils.create_tmp_dir()
    data_init.set_tmp_dir(tmp_dat_dir)

    nodes_dir = "run_dui2_nodes"
    try:
        os.mkdir(nodes_dir)

    except FileExistsError:
        print("assuming Dui2 already ran here")

    os.chdir(nodes_dir)
    tree_ini_path = init_param["limit_path"]
    if tree_ini_path == None:
        tree_ini_path = ""
        '''
        #TODO: consider the approach of the next 3 instructions instead
        logging.info(
            " using the dir from where the commad 'dui2_server_side' was invoqued"
        )
        from pathlib import Path
        tree_ini_path = str(Path.cwd().parent)
        '''

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

    log_path = os.path.join(dir_2_change, 'run_dui2_all_local_all_ram.log')
    logging.basicConfig(filename=log_path, level=logging.DEBUG, force=True)


    logging.info("tree_ini_path(all_loca_all_ram) =" + str(tree_ini_path))

    cmd_runner.set_dir_path(tree_ini_path)

    m_gui_obj = all_local_gui_connector.MainGuiObject(
        parent = app, cmd_tree_runner = cmd_runner
    )
    m_obj = MainObject(parent = app, multi_runner = m_gui_obj)
    sys.exit(app.exec_())


