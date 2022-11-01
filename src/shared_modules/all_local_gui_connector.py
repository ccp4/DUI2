import sys, os, time, json
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtUiTools
from shared_modules import all_local_server, format_utils

class connect_thread(QThread):
    def __init__(self, handler, cmd_in, obj_out):
        super(connect_thread, self).__init__()
        self.my_handler = handler
        self.my_cmd = cmd_in
        self.my_caller = obj_out

    def run(self):
        self.my_handler.fake_get(
            url_dict = self.my_cmd, call_obj = self
        )

    def call_back_str(self, data_out):
        #print("[call_back_str] <<<", data_out, ">>>")
        self.my_caller.get_it(data_out)

class MultiRunner(QObject):
    def __init__(self):
        super(MultiRunner, self).__init__()
        self.thread_lst = []

    def run_one_work(self, handler, cmd_in, obj_out):
        self.n_thread = connect_thread(handler, cmd_in, obj_out)
        self.thread_lst.append(self.n_thread)
        self.n_thread.start()
        return self.n_thread


class MainGuiObject(QObject):
    def __init__(self, parent = None, cmd_tree_runner = None):
        super(MainGuiObject, self).__init__(parent)
        self.parent_app = parent
        self.handler = all_local_server.ReqHandler(cmd_tree_runner)
        print("inside QObject")
        self.dui_txt_out = None
        self.m_run = MultiRunner()

    def run_from_main_dui(self, cmd_in, dui_handle):
        print("cmd_in(run_from_main_dui) =", cmd_in)
        self.dui_txt_out = dui_handle
        this_thread = self.m_run.run_one_work(self.handler, cmd_in, dui_handle)
        while not this_thread.isFinished():
            time.sleep(0.05)
