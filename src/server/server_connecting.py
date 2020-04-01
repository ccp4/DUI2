from PySide2 import QtCore, QtWidgets, QtNetwork
import time
import sys
import subprocess

class CommandThread (QtCore.QThread):

    str_print_signal = QtCore.Signal(str)

    def __init__(self, parent = None):
        super(CommandThread, self).__init__()

    def set_cmd(self, cmd_in = None):
        self.cmd_to_run = cmd_in

    def run(self):
        print("... from CommandThread(run)")

        proc = subprocess.Popen(
            self.cmd_to_run,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        line = None
        while proc.poll() is None or line != '':
            line = proc.stdout.readline()[:-1]
            print("line>>", line)
            self.str_print_signal.emit(line)
            '''
            line_err = proc.stderr.readline()[:-1]
            if line_err != '':
                print("_err>>", line_err)
            '''


        proc.stdout.close()

class TransferThread (QtCore.QThread):
    def __init__(self, parent = None):
        super(TransferThread, self).__init__()
        self.str_lst = []
        self.str_pos = 0

    def set_socket(self, socket_out = None):
        self.socket = socket_out
        print("set_socket")

    def add_str(self, new_str):
        self.str_lst.append(new_str)

    def transfer_str(self, new_str):
        #print("line>>", new_str)
        txt2send = str.encode(new_str)

        self.socket.write(txt2send)
        time.sleep(0.02)
        self.socket.waitForBytesWritten()
        #time.sleep(0.01)

        self.str_pos += 1
        if new_str == "/*EOF*/":
            self.EOF = True

    def run(self):
        self.EOF = False
        print("... from TransferThread(run)")
        print("self.str_pos", self.str_pos)
        print("len(self.str_lst)", len(self.str_lst))

        while self.EOF == False:
            time.sleep(0.02)
            if len(self.str_lst) > self.str_pos:
                self.transfer_str(self.str_lst[self.str_pos])

        print("EOF = True")


class Server(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Server, self).__init__(parent)

        statusLabel = QtWidgets.QLabel()

        self.tcpServer = QtNetwork.QTcpServer(self)
        if not self.tcpServer.listen(address =QtNetwork.QHostAddress.Any, port = 12354):
            QtWidgets.QMessageBox.critical(self, "DUI Server",
                    "Unable to start the server: %s." % self.tcpServer.errorString())
            self.close()
            return

        print("self.tcpServer.serverAddress()", self.tcpServer.serverAddress())

        statusLabel.setText("The server is running on port %d.\nRun the "
                "DUI Client example now." % self.tcpServer.serverPort())

        self.tcpServer.newConnection.connect(self.new_connection)
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(statusLabel)

        send_count_butt = QtWidgets.QPushButton("send counting")
        send_count_butt.clicked.connect(self.send_str)
        mainLayout.addWidget(send_count_butt)

        self.setLayout(mainLayout)
        self.setWindowTitle("DUI Server")

    def new_connection(self):
        self.new_socket = self.tcpServer.nextPendingConnection()
        self.new_socket.waitForReadyRead()
        self.launch_thread()
        self.new_socket.channelReadyRead.connect(self.channel_ready_read)

    def channel_ready_read(self):
        print("channel_ready_read(server)")
        self.launch_thread()

    def launch_thread(self):
        instr = self.new_socket.readAll()
        str_instr = str(instr.data().decode('utf-8'))
        print("New command: \n <<", str(str_instr), ">>")

        self.cmd_thrd = CommandThread()

        self.cmd_thrd.finished.connect(self.tell_cmd_thrd_finished)
        self.cmd_thrd.set_cmd(cmd_in = str_instr)

        self.tranf_thrd = TransferThread()
        self.tranf_thrd.set_socket(socket_out = self.new_socket)
        self.tranf_thrd.finished.connect(self.tell_tranf_thrd_finished)
        self.tranf_thrd.start()

        self.cmd_thrd.str_print_signal.connect(self.tranf_thrd.add_str)
        self.cmd_thrd.start()

    def tell_cmd_thrd_finished(self):
        print("... cmd_thrd() finished")
        time.sleep(0.5)
        self.tranf_thrd.add_str("/*EOF*/")
    def tell_tranf_thrd_finished(self):
        print("... tranf_thrd() finished")

    def send_str(self):
        self.tranf_thrd.add_str("dummy_str")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    server = Server()
    sys.exit(server.exec_())
