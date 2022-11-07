import sys, os, time, json
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtUiTools
from shared_modules import all_local_server, format_utils

class connect_get_thread(QThread):
    def __init__(self, handler, cmd_in, obj_out):
        super(connect_get_thread, self).__init__()
        self.my_handler = handler
        self.my_cmd = cmd_in
        self.my_caller = obj_out

    def run(self):
        self.my_handler.fake_get(
            url_dict = self.my_cmd, call_obj = self
        )

    def call_back_str(self, data_out):
        self.my_caller.get_it_str(data_out)

    def call_back_bin(self, data_out):
        self.my_caller.get_it_bin(data_out)


class connect_post_thread(QThread):
    def __init__(self, handler, cmd_in, obj_out):
        super(connect_post_thread, self).__init__()
        self.my_handler = handler
        self.my_cmd = cmd_in
        self.my_caller = obj_out

    def run(self):
        self.my_handler.fake_post(
            url_dict = self.my_cmd, call_obj = self
        )

    def call_back_str(self, data_out):
        self.my_caller.get_it_str(data_out)


class MultiRunner(QObject):
    def __init__(self):
        super(MultiRunner, self).__init__()
        self.thread_lst = []

    def get_work(self, handler, cmd_in, obj_out):
        self.n_thread = connect_get_thread(handler, cmd_in, obj_out)
        self.thread_lst.append(self.n_thread)
        self.n_thread.start()
        while not self.n_thread.isFinished():
            time.sleep(0.1)

    def post_work(self, handler, cmd_in, obj_out):
        self.n_thread = connect_post_thread(handler, cmd_in, obj_out)
        self.thread_lst.append(self.n_thread)
        self.n_thread.start()
        while not self.n_thread.isFinished():
            time.sleep(0.1)


class MainGuiObject(QObject):
    def __init__(self, parent = None, cmd_tree_runner = None):
        super(MainGuiObject, self).__init__(parent)
        self.parent_app = parent
        self.handler = all_local_server.ReqHandler(cmd_tree_runner)
        print("inside QObject")
        self.m_run = MultiRunner()

    def get_from_main_dui(self, cmd_in, dui_obj):
        print("cmd_in(get_from_main_dui) =", cmd_in)
        self.m_run.get_work(self.handler, cmd_in, dui_obj)

    def post_from_main_dui(self, cmd_in, dui_obj):
        print("cmd_in(post_from_main_dui) =", cmd_in)
        self.m_run.post_work(self.handler, cmd_in, dui_obj)
