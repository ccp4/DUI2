nod_lst = [{"lin_num": 0, "status": "Succeeded", "cmd2show": ["Root"], "child_node_lst": [], "parent_node_lst": []}]

new_nod_lst = [
{"lin_num": 0, "status": "Succeeded", "cmd2show": ["Root"], "child_node_lst": [1, 2, 3, 19, 20], "parent_node_lst": []},
{"lin_num": 1, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [4], "parent_node_lst": [0]},
{"lin_num": 2, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [5], "parent_node_lst": [0]},
{"lin_num": 3, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [6], "parent_node_lst": [0]},
{"lin_num": 4, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [7, 10, 11, 12], "parent_node_lst": [1]},
{"lin_num": 5, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [8, 13, 14], "parent_node_lst": [2]},
{"lin_num": 6, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [9, 15], "parent_node_lst": [3]},
{"lin_num": 7, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [4]},
{"lin_num": 8, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [5]},
{"lin_num": 9, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [6]},
{"lin_num": 10, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [4]},
{"lin_num": 11, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [4]},
{"lin_num": 12, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [4]},
{"lin_num": 13, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [5]},
{"lin_num": 14, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [5]},
{"lin_num": 15, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [6]},
{"lin_num": 16, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [7, 10, 8, 13, 15]},
{"lin_num": 17, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [7, 10, 8, 13, 15]},
{"lin_num": 18, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [15, 13, 8, 10, 7]},
{"lin_num": 19, "status": "Failed", "cmd2show": ["0", "ls"], "child_node_lst": [], "parent_node_lst": [0]},
{"lin_num": 20, "status": "Ready", "cmd2show": ["None"], "child_node_lst": [], "parent_node_lst": [0]}
]

import sys
import time, json
import requests
import tree_draw_tmp
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from gui_utils import draw_inner_graph

class Run_n_Output(QThread):
    line_out = Signal(str)
    def __init__(self, request):
        super(Run_n_Output, self).__init__()
        self.request = request

    def run(self):
        line_str = ''
        while True:
            tmp_dat = self.request.raw.read(1)
            single_char = str(tmp_dat.decode('utf-8'))
            line_str += single_char
            if single_char == '\n':
                #print(line_str[:-1])
                self.line_out.emit(line_str)
                line_str = ''

            elif line_str[-7:] == '/*EOF*/':
                print('>>  /*EOF*/  <<')
                self.line_out.emit(' \n /*EOF*/ \n')
                break


class MainObject(QObject):
    def __init__(self, parent = None):
        super(MainObject, self).__init__(parent)
        self.window = QtUiTools.QUiLoader().load("tree_test.ui")
        self.window.CmdSend2server.clicked.connect(self.request_launch)
        self.tree_obj = tree_draw_tmp.TreeShow()

        self.window.ButtonSelect.clicked.connect(self.on_select)
        self.window.ButtonClear.clicked.connect(self.on_clear)
        self.window.ButtonMkChild.clicked.connect(self.on_make)
        self.window.incoming_text.setFont(QFont("Monospace"))

        self.window.show()
        self.my_scene = QGraphicsScene()
        self.window.graphicsView.setScene(self.my_scene)
        self.draw_graph(nod_lst)

    def draw_graph(self, new_nod_lst):
        self.nod_lst = new_nod_lst
        draw_inner_graph(self.my_scene, self.nod_lst)
        #self.my_scene.update()

    def on_select(self):
        print("on_select")

    def on_clear(self):
        print("on_clear")

    def on_make(self):
        print("on_make")
        self.draw_graph(new_nod_lst)

    def add_line(self, new_line):
        self.window.incoming_text.moveCursor(QTextCursor.End)
        self.window.incoming_text.insertPlainText(new_line)
        self.window.incoming_text.moveCursor(QTextCursor.End)

    def run_ended(self):
        print("run ended")

        cmd = {"nod_lst":"", "cmd_lst":["display"]}
        req_get = requests.get('http://localhost:8080/', stream = True, params = cmd)

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

        lst_nodes = json.loads(str_lst[1])
        lst_str = self.tree_obj(lst_nod = lst_nodes)

        for tree_line in lst_str:
            self.add_line(tree_line + "\n")

        print("show tree ended")

    def request_launch(self):
        cmd_str = str(self.window.CmdEdit.text())
        print("cmd_str", cmd_str)
        nod_str = str(self.window.NumLin.value())

        cmd = {"nod_lst":nod_str, "cmd_lst":[cmd_str]}
        req_get = requests.get('http://localhost:8080/', stream = True, params = cmd)

        self.thrd = Run_n_Output(req_get)
        self.thrd.line_out.connect(self.add_line)
        self.thrd.finished.connect(self.run_ended)
        self.thrd.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m_obj = MainObject()
    sys.exit(app.exec_())


