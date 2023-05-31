import sys, os, time, json, logging
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtUiTools
from shared_modules import all_local_server, format_utils
from server.data_n_json import iter_dict
from server import multi_node
from server.init_first import ini_data

class connect_thread(QThread):
    logging.infoing = Signal(str)
    def __init__(self, handler, cmd_in):
        super(connect_thread, self).__init__()
        self.my_handler = handler
        self.my_cmd = cmd_in

    def run(self):
        self.my_handler.fake_post(
            url_dict = self.my_cmd, call_obj = self
        )
        self.my_handler.fake_get(
            url_dict = {"nod_lst":[0], "cmd_lst":["display"]},
            call_obj = self
        )

    def call_back_str(self, str_out):
        logging.info("..call_back_str.." + str_out)
        self.logging.infoing.emit(str_out)


class MultiRunner(QObject):
    logging.infoing = Signal(str)
    def __init__(self):
        super(MultiRunner, self).__init__()
        self.thread_lst = []

    def run_one_work(self, handler, cmd_in):
        new_thread = connect_thread(handler, cmd_in)
        new_thread.start()
        new_thread.logging.infoing.connect(self.console_out)
        self.thread_lst.append(new_thread)

    def console_out(self, str_out):
        self.logging.infoing.emit(str_out)


class MainGuiObject(QObject):
    def __init__(self, parent = None, cmd_tree_runner = None):
        super(MainGuiObject, self).__init__(parent)
        self.parent_app = parent

        self.handler = all_local_server.ReqHandler(cmd_tree_runner)

        self.ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = self.ui_dir_path + os.sep + "tmp_gui.ui"
        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.setWindowTitle("Test DUI2")

        logging.info("inside QObject")
        self.m_run = MultiRunner()
        self.m_run.logging.infoing.connect(self.console_out)
        self.window.RunPushButton.clicked.connect(self.run_one_clicked)
        self.window.show()

    def run_one_clicked(self):
        logging.info("run_one_clicked(MainGuiObject)")
        cmd_in = {
            "nod_lst":[int(self.window.NumSpinBox.value())],
            "cmd_lst":[str(self.window.CmdLineEdit.text())]
        }
        self.window.OutTextEdit.insertPlainText(str(cmd_in))
        self.m_run.run_one_work(self.handler, cmd_in)

    def console_out(self, str_out):
        self.window.OutTextEdit.moveCursor(QTextCursor.End)
        self.window.OutTextEdit.insertPlainText(str_out)

def main(par_def = None):
    format_utils.print_logo()
    data_init = ini_data()
    data_init.set_data(par_def)

    init_param = format_utils.get_par(par_def, sys.argv[1:])
    logging.info("init_param(server) =" + str(init_param))

    run_local = True

    logging.info("\n run_local =" + str(run_local) + "\n")

    tree_ini_path = init_param["init_path"]
    if tree_ini_path == None:
        logging.info("\n NOT GIVEN init_path")
        logging.info(" using the dir from where the commad 'dui_server' was invoqued")
        tree_ini_path = os.getcwd()

    logging.info(
        "\n using init path as: <<" + tree_ini_path + ">> \n"
    )
    #tree_dic_lst = iter_dict(tree_ini_path, 0)
    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

        cmd_runner = multi_node.Runner(runner_data)

    except FileNotFoundError:
        cmd_runner = multi_node.Runner(None)

    #cmd_runner.set_dir_tree(tree_dic_lst)
    cmd_tree_runner.set_dir_path(tree_ini_path)
    app = QApplication(sys.argv)
    m_obj = MainGuiObject(parent = app, cmd_tree_runner = cmd_runner)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
