import sys, os, requests, json, subprocess, platform

from dui2 import only_client
from dui2.shared_modules import format_utils

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


def url_vs_domain_plus_port(domain = None, port_num = None, url_opt = None):
    if url_opt == None:
        domain_ini = domain + ":"
        main_url = domain_ini + str(port_num)
        return domain_ini, main_url

    else:
        for pos, single_char in enumerate(url_opt):
            if single_char == ":":
                domain_ini = url_opt[:pos + 1]

        return domain_ini, url_opt


class Form(QWidget):
    def __init__(
        self, parent = None, domain = None, port_num = None, url_opt = None
    ):
        super(Form, self).__init__(parent)

        self.domain_ini, self.main_url = url_vs_domain_plus_port(
            domain, port_num, url_opt
        )

        print(
            "\n self.domain_ini, self.main_url = \n",
            str(self.domain_ini), str(self.main_url) , "\n"
        )

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

        self.lst_procs = []
        self.show()

    def login_clicked(self):
        dict_resp = self.post_clicked(new_command = "login")
        print("dict_resp(login) =" + str(dict_resp))
        try:
            if dict_resp['body']['success']:
                token = dict_resp['body']['message']['token']
                port =  dict_resp['body']['message']['port']
                #cutting the last part from ~/ ... /DUI2/src/dui2/only_client.py
                dui_main_path = str(only_client.__file__)[:-20]
                code_path = dui_main_path + os.sep + "run_dui2_client.py"
                token_str = "token=" + str(token)
                url_str = 'url=' + self.domain_ini + str(port) + '/'
                cmd_lst = [
                    str(sys.executable), str(code_path), token_str, url_str
                ]
                print("\n Running: \n", cmd_lst, "\n")

                new_proc = subprocess.Popen(args = cmd_lst, shell = False)
                self.lst_procs.append(new_proc)

            else:
                print("\n failed to login \n")

        except TypeError:
            print("something went wrong  << TypeError >>")

    def register_clicked(self):
        dict_resp = self.post_clicked(new_command = "register")
        print("dict_resp(register) =" + str(dict_resp))

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
        try:
            req_post = requests.post(
                self.main_url, data = json.dumps(obj_dat)
            )
            lst_out = req_post.content
            dict_resp = json.loads(lst_out)
            return dict_resp

        except requests.exceptions.RequestException:
            print("something went wrong  << RequestException >> ")

        except json.decoder.JSONDecodeError:
            print("something went wrong  << JSONDecodeError >> ")


def main():

    if platform.system() == "Windows":
        print("running on Windows")

    elif platform.system() == "Linux":
        print("running on Linux")
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        os.environ["WAYLAND_DISPLAY"] = ""

    else:
        print("nether Linux or Windows")

    par_def = (
        ("domain", "http://127.0.0.1"),
        ("port", 34567),
        ("url", None)
    )
    init_param = format_utils.get_par(par_def, sys.argv[1:])

    domain = init_param["domain"]
    port_num = int(init_param["port"])
    url_opt = init_param["url"]

    app = QApplication(sys.argv)
    form = Form(
        parent = None, domain = domain, port_num = port_num, url_opt = url_opt
    )

    sys.exit(app.exec_())

