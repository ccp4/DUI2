import logging

from dui2.shared_modules.qt_libs import *

from dui2.shared_modules import all_local_server, format_utils

class ConnectGetThread(QThread):
    def __init__(self, handler, cmd_in, obj_out):
        super(ConnectGetThread, self).__init__()
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


class ConnectPostThread(QThread):
    def __init__(self, handler, cmd_in, obj_out):
        super(ConnectPostThread, self).__init__()
        self.my_handler = handler
        self.my_cmd = cmd_in
        self.my_caller = obj_out
        logging.info("my_cmd(ConnectPostThread)=" + str(self.my_cmd))

    def run(self):
        self.my_handler.fake_post(
            url_dict = self.my_cmd, call_obj = self
        )

    def call_back_str(self, data_out):
        self.my_caller.get_it_str(data_out)


class MultiRunner(QObject):
    def __init__(self):
        super(MultiRunner, self).__init__()
        logging.info("MultiRunner start")

    def get_work(self, handler, cmd_in, obj_out):
        new_thread = ConnectGetThread(handler, cmd_in, obj_out)
        new_thread.start()
        new_thread.wait()

    def post_work(self, handler, cmd_in, obj_out):
        new_thread = ConnectPostThread(handler, cmd_in, obj_out)
        new_thread.start()
        new_thread.wait()


class MainGuiObject(QObject):
    def __init__(self, parent = None, cmd_tree_runner = None):
        super(MainGuiObject, self).__init__(parent)
        self.parent_app = parent
        self.handler = all_local_server.ReqHandler(cmd_tree_runner)
        logging.info("inside QObject")
        self.m_run = MultiRunner()

    def get_from_main_dui(self, cmd_in, dui_obj):
        logging.info("cmd_in(get_from_main_dui) =" + str(cmd_in))
        self.m_run.get_work(self.handler, cmd_in, dui_obj)

    def post_from_main_dui(self, cmd_in, dui_obj):
        logging.info("cmd_in(post_from_main_dui) =" + str(cmd_in))
        self.m_run.post_work(self.handler, cmd_in, dui_obj)
