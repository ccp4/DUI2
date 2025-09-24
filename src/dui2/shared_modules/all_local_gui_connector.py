import sys, os, time, json, logging

from dui2.shared_modules.qt_libs import *

from dui2.shared_modules import all_local_server, format_utils

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
        logging.info("my_cmd(connect_post_thread)=" + str(self.my_cmd))

    def run(self):
        self.my_handler.fake_post(
            url_dict = self.my_cmd, call_obj = self
        )

    def call_back_str(self, data_out):
        self.my_caller.get_it_str(data_out)
        #logging.info("data going(connect_post_thread)=", data_out)


class MultiRunner(QObject):
    def __init__(self):
        super(MultiRunner, self).__init__()
        self.thread_lst = []

        self._my_timer = QTimer(self)
        self._my_timer.timeout.connect(self.clean_memory)
        self._my_timer.start(2000)

    def get_work(self, handler, cmd_in, obj_out):
        new_thread = connect_get_thread(handler, cmd_in, obj_out)
        new_thread.start()
        self.thread_lst.append(new_thread)

        while not new_thread.isFinished():
            time.sleep(0.1)

    def post_work(self, handler, cmd_in, obj_out):
        new_thread = connect_post_thread(handler, cmd_in, obj_out)
        self.thread_lst.append(new_thread)
        new_thread.start()

        while not new_thread.isFinished():
            time.sleep(0.1)

    def clean_memory(self):
        for trd in self.thread_lst:
            if trd.isFinished():
                # del trd
                # or
                self.thread_lst.remove(trd)


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
