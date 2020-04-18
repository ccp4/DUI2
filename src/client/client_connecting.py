from PySide2 import QtCore, QtWidgets, QtGui, QtNetwork
import sys, time
import requests


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
                break


class Client(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Client, self).__init__(parent)

        self.incoming_text = QtWidgets.QTextEdit()
        self.incoming_text.setFont(QtGui.QFont("Monospace"))

        self.dataLineEdit = QtWidgets.QLineEdit()
        self.dataLineEdit.setPlaceholderText("Type command")
        self.dataLineEdit.setFont(QtGui.QFont("Monospace"))

        send2serverButton = QtWidgets.QPushButton("Launch command")
        send2serverButton.clicked.connect(self.request_launch)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.incoming_text)
        mainLayout.addWidget(QtWidgets.QLabel(" \n Type here"))
        mainLayout.addWidget(self.dataLineEdit)
        mainLayout.addWidget(send2serverButton)
        self.setLayout(mainLayout)
        self.setWindowTitle("DUI front end test with HTTP")

    def add_line(self, new_line):
        self.incoming_text.moveCursor(QtGui.QTextCursor.End)
        self.incoming_text.insertPlainText(new_line)

    def run_ended(self):
        print("run_ended")

    def request_launch(self):

        cmd_str = str.encode(self.dataLineEdit.text())
        cmd = {'command': [cmd_str]}
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



