
import os, sys
import time, json
import requests

try:
    from shared_modules import out_utils

except ModuleNotFoundError:
    '''
    This trick to import the out_utils module can be
    removed once the project gets properly packaged
    '''

    comm_path = os.path.abspath(__file__)[0:-21] + "shared_modules"
    print("comm_path: ", comm_path)
    sys.path.insert(1, comm_path)
    import out_utils


from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from gui_utils import TreeScene

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
        self.window = QtUiTools.QUiLoader().load("main_dui.ui")
        self.window.CmdSend2server.clicked.connect(self.request_launch)
        self.tree_obj = out_utils.TreeShow()

        self.window.ButtonSelect.clicked.connect(self.on_select)
        self.window.ButtonClear.clicked.connect(self.on_clear)
        self.window.incoming_text.setFont(QFont("Monospace"))

        self.window.show()
        self.my_scene = TreeScene(self)
        self.window.gitView.setScene(self.my_scene)
        self.my_scene.draw_inner_graph([])

    def on_select(self):
        print("on_select")

    def on_clear(self):
        print("on_clear")

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

        self.my_scene.clear()
        self.my_scene.draw_inner_graph(lst_nodes)
        self.my_scene.update()

    def request_launch(self):
        cmd_str = str(self.window.CmdEdit.text())
        print("cmd_str", cmd_str)
        nod_str = str(self.window.NumLinLst.text())
        nod_lst = nod_str.split(" ")
        print("nod_lst", nod_lst)
        cmd = {"nod_lst":nod_lst, "cmd_lst":[cmd_str]}
        req_get = requests.get('http://localhost:8080/', stream = True, params = cmd)

        self.thrd = Run_n_Output(req_get)
        self.thrd.line_out.connect(self.add_line)
        self.thrd.finished.connect(self.run_ended)
        self.thrd.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m_obj = MainObject()
    sys.exit(app.exec_())


