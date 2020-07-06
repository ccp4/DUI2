
import os, sys
import time, json
import requests

try:
    from shared_modules import format_utils

except ModuleNotFoundError:
    '''
    This trick to import the format_utils module can be
    removed once the project gets properly packaged
    '''
    comm_path = os.path.abspath(__file__)[0:-21] + "shared_modules"
    print("comm_path: ", comm_path)
    sys.path.insert(1, comm_path)
    import format_utils

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from gui_utils import TreeDirScene, AdvancedParameters

def json_data_request(url, cmd):
    req_get = requests.get(url, stream = True, params = cmd)
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

    json_out = json.loads(str_lst[1])
    return json_out


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

        ui_path = os.path.dirname(os.path.abspath(__file__))
        ui_path += os.sep + "client.ui"
        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.incoming_text.setFont(QFont("Monospace"))

        self.tree_obj = format_utils.TreeShow()
        self.tree_scene = TreeDirScene(self)
        self.window.treeView.setScene(self.tree_scene)

        self.my_url = 'http://localhost:8080/'

        self.advanced_parameters = AdvancedParameters()
        vbox = QVBoxLayout()
        vbox.addWidget(self.advanced_parameters)
        self.window.AdavancedParamsTab.setLayout(vbox)

        self.tree_scene.node_clicked.connect(self.on_node_click)
        self.window.CmdSend2server.clicked.connect(self.request_launch)
        self.window.pushButton.clicked.connect(self.request_params)
        self.tree_scene.draw_tree_graph([])

        self.window.show()

    def on_node_click(self, nod_num):
        print("clicked node number ", nod_num)
        prev_text = str(self.window.NumLinLst.text())
        self.window.NumLinLst.setText(
            str(prev_text + " " + str(nod_num))
        )

    def add_line(self, new_line):
        self.window.incoming_text.moveCursor(QTextCursor.End)
        self.window.incoming_text.insertPlainText(new_line)
        self.window.incoming_text.moveCursor(QTextCursor.End)

    def request_display(self):
        cmd = {"nod_lst":"", "cmd_lst":["display"]}
        lst_nodes = json_data_request(self.my_url, cmd)

        lst_str = self.tree_obj(lst_nod = lst_nodes)
        lst_2d_dat = self.tree_obj.get_tree_data()

        for tree_line in lst_str:
            self.add_line(tree_line + "\n")

        self.tree_scene.clear()
        self.tree_scene.draw_tree_graph(lst_2d_dat)
        self.tree_scene.update()

    def request_params(self):
        cmd = {"nod_lst":"", "cmd_lst":["smp"]}
        lst_params = json_data_request(self.my_url, cmd)

        lin_lst = format_utils.param_tree_2_lineal(lst_params)
        new_lin_lst = lin_lst()

        self.advanced_parameters.build_pars(new_lin_lst)


    def request_launch(self):
        cmd_str = str(self.window.CmdEdit.text())
        print("cmd_str", cmd_str)
        nod_str = str(self.window.NumLinLst.text())
        self.window.NumLinLst.clear()
        nod_lst = nod_str.split(" ")
        print("nod_lst", nod_lst)
        cmd = {"nod_lst":nod_lst, "cmd_lst":[cmd_str]}
        req_get = requests.get(self.my_url, stream = True, params = cmd)

        self.thrd = Run_n_Output(req_get)
        self.thrd.line_out.connect(self.add_line)
        self.thrd.finished.connect(self.request_display)
        self.thrd.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m_obj = MainObject()
    sys.exit(app.exec_())


