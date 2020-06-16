from PySide2 import QtCore, QtWidgets, QtGui, QtNetwork
import os, sys, time, json
import requests

try:
    from shared_modules import out_utils

except ModuleNotFoundError:
    '''
    This trick to import the out_utils module can be
    removed once the project gets properly packaged
    '''

    comm_path = os.path.abspath(__file__)[0:-31] + "shared_modules"
    sys.path.insert(1, comm_path)
    import out_utils


class Run_n_Output(QtCore.QThread):
    line_out = QtCore.Signal(str)
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


class Client(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Client, self).__init__(parent)

        self.incoming_text = QtWidgets.QTextEdit()
        self.incoming_text.setFont(QtGui.QFont("Monospace"))

        self.CmdEdit = QtWidgets.QLineEdit()
        self.CmdEdit.setPlaceholderText("Type command")
        self.CmdEdit.setFont(QtGui.QFont("Monospace"))

        self.NumLin = QtWidgets.QSpinBox()

        self.CmdSend2server = QtWidgets.QPushButton("Launch command")
        self.CmdSend2server.clicked.connect(self.request_launch)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.incoming_text)
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.NumLin)
        h_layout.addWidget(self.CmdEdit)
        mainLayout.addLayout(h_layout)
        mainLayout.addWidget(self.CmdSend2server)
        self.setLayout(mainLayout)
        self.setWindowTitle("DUI front end test with HTTP")

        self.tree_obj = out_utils.TreeShow()

    def add_line(self, new_line):
        self.incoming_text.moveCursor(QtGui.QTextCursor.End)
        self.incoming_text.insertPlainText(new_line)
        self.incoming_text.moveCursor(QtGui.QTextCursor.End)

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
        cmd_str = str(self.CmdEdit.text())
        print("cmd_str", cmd_str)
        nod_str = str(self.NumLin.value())

        cmd = {"nod_lst":nod_str, "cmd_lst":[cmd_str]}
        req_get = requests.get('http://localhost:8080/', stream = True, params = cmd)

        self.thrd = Run_n_Output(req_get)
        self.thrd.line_out.connect(self.add_line)
        self.thrd.finished.connect(self.run_ended)
        self.thrd.start()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(client.exec_())



