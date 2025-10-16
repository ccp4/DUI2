import sys, os, requests, json

try:
    from PySide6 import QtUiTools
    from PySide6.QtCore import *
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    print("Using PySide6 as Qt bindings")

except ModuleNotFoundError:
    from PySide2 import QtUiTools
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    print("Using PySide2 as Qt bindings")

class Form(QWidget):
    def __init__(self, parent = None):
        super(Form, self).__init__(parent)
        main_box = QVBoxLayout()
        top_layout_1 = QHBoxLayout()
        top_layout_1.addWidget(QLabel("User"))
        self.LineEditUser = QLineEdit()
        top_layout_1.addWidget(self.LineEditUser)
        main_box.addLayout(top_layout_1)
        top_layout_2 = QHBoxLayout()
        top_layout_2.addWidget(QLabel("Password"))
        self.LineEditPass = QLineEdit()
        top_layout_2.addWidget(self.LineEditPass)
        main_box.addLayout(top_layout_2)
        low_h_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_clicked)
        low_h_layout.addWidget(self.login_button)
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_clicked)
        low_h_layout.addWidget(self.register_button)
        main_box.addLayout(low_h_layout)
        self.setLayout(main_box)
        self.show()

    def login_clicked(self):
        self.post_clicked(new_command = "login")

    def register_clicked(self):
        self.post_clicked(new_command = "register")

    def post_clicked(self, new_command):
        print("Post clicked")
        command = str(new_command)
        data_user = str(self.LineEditUser.text())
        data_pass = str(self.LineEditPass.text())
        print("PostCommadEdit =", command)
        print("LineEditUser =", data_user)
        print("LineEditPass =", data_pass)

        obj_dat = {
            "command":command,
            "data_user":data_user,
            "data_pass":data_pass
        }
        print("obj_dat =", obj_dat)
        try:
            req_post = requests.post(
                "http://127.0.0.1:34567", data = json.dumps(obj_dat)
            )
            lst_out = req_post.content
            dict_resp = json.loads(lst_out)
            print("lst_out =" + str(dict_resp))

        except requests.exceptions.RequestException:
            print(
                "something went wrong  << RequestException >> "
            )

        except json.decoder.JSONDecodeError:
            print(
                "something went wrong  << JSONDecodeError >> "
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())

