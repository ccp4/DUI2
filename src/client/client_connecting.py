from PySide2 import QtCore, QtWidgets, QtGui, QtNetwork
import sys

class Client(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Client, self).__init__(parent)

        self.incoming_text = QtWidgets.QTextEdit()
        self.incoming_text.setFont(QtGui.QFont("Monospace"))
        self.dataLineEdit = QtWidgets.QLineEdit('test text')
        self.dataLineEdit.setFont(QtGui.QFont("Monospace"))
        send2serverButton = QtWidgets.QPushButton("send to server")

        self.tcpSocket = QtNetwork.QTcpSocket(self)

        send2serverButton.clicked.connect(self.requestNewConnection)
        self.tcpSocket.readyRead.connect(self.readFromServer)
        self.tcpSocket.error.connect(self.displayError)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.incoming_text)
        mainLayout.addWidget(QtWidgets.QLabel(" \n Type here"))
        mainLayout.addWidget(self.dataLineEdit)
        mainLayout.addWidget(send2serverButton)
        self.setLayout(mainLayout)
        self.setWindowTitle("DUI front end test")

        self.tcpSocket.stateChanged.connect(self.tell_State)

    def tell_State(self):
        print("self.tcpSocket.state()", self.tcpSocket.state())
        print("self.tcpSocket.isValid()", self.tcpSocket.isValid())

    def requestNewConnection(self):
        if not self.tcpSocket.isValid():
            self.tcpSocket.abort()
            self.tcpSocket.connectToHost(QtNetwork.QHostAddress.Any, 12354, QtCore.QIODevice.ReadWrite)

        if self.tcpSocket.waitForConnected(1000):
            print("Connected!")

        else:
            print("Failed to connect")

        txt2send = str.encode(self.dataLineEdit.text())
        self.tcpSocket.write(txt2send)

    def readFromServer(self):
        instr = self.tcpSocket.readAll()
        nxt_str = str(instr.data().decode('utf-8'))
        #print(nxt_str, "<<line")
        self.incoming_text.moveCursor(QtGui.QTextCursor.End)
        self.incoming_text.insertPlainText(nxt_str + "\n")

    def displayError(self, socketError):
        if socketError == QtNetwork.QAbstractSocket.RemoteHostClosedError:
            pass
        elif socketError == QtNetwork.QAbstractSocket.HostNotFoundError:
            QtWidgets.QMessageBox.information(self, " Client",
                    "The host was not found. Please check the host name and "
                    "port settings.")
        elif socketError == QtNetwork.QAbstractSocket.ConnectionRefusedError:
            QtWidgets.QMessageBox.information(self, " Client",
                    "The connection was refused by the peer. Make sure "
                    "the server is running, and check that the host name "
                    "and port settings are correct.")
        else:
            QtWidgets.QMessageBox.information(self, " Client",
                    "The following error occurred: %s." % self.tcpSocket.errorString())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(client.exec_())
