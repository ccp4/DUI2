"""
DUI2's client's side file navigation main widget and tools

Author: Luis Fuentes-Montero (Luiso)
With strong help from DIALS and CCP4 teams

copyright (c) CCP4 - DLS
"""

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import sys, os, logging

from dui2.shared_modules.qt_libs import *

from dui2.client.exec_utils import get_req_json_dat

def get_number_from_string(dict_in):
    str_in = dict_in['name']
    num_char = ""
    for char_part in str_in:
        if char_part in "0123456789":
            num_char += char_part
    try:
        return int(num_char)

    except ValueError:
        return 0


def f_key(dic_in):
    #return dic_in['name']
    return dic_in['isdir']


def sort_dict_list(lst_in, key_in):
    lst_out = sorted(lst_in, key=key_in)
    return lst_out


class MyDirView_list(QListWidget):
    file_clickled = Signal(dict)
    def __init__(self, parent = None):
        super(MyDirView_list, self).__init__(parent)
        self.itemClicked.connect(self.someting_click)
        self.itemDoubleClicked.connect(self.clicked_twise)
        self.setWrapping(True)
        self.setResizeMode(QListView.Adjust)
        DirPixMapi = getattr(QStyle, 'SP_DirIcon')
        FilePixMapi = getattr(QStyle, 'SP_FileIcon')
        self.icon_dict = {
            "True":self.style().standardIcon(DirPixMapi),
            "False":self.style().standardIcon(FilePixMapi)
        }

    def enter_list(self, lst_in):
        self.ini_dict_list = list(lst_in)

    def refresh_list(self, sorting = "abc"):
        if sorting == "abc":
            self.dict_list = list(self.ini_dict_list)

        elif sorting == "123":
            self.dict_list = list(sort_dict_list(self.ini_dict_list, f_key))

        else:
            self.dict_list = list(sort_dict_list(
                self.ini_dict_list, get_number_from_string
            ))

        self.items_list = []
        for n_widg, single_file in enumerate(self.dict_list):
            tst_item = QListWidgetItem(single_file["name"])
            tst_item.f_isdir = single_file["isdir"]
            tst_item.f_path = str(single_file["path"])
            tst_item.setIcon(self.icon_dict[str(tst_item.f_isdir)])
            self.items_list.append(tst_item)

        self.clear()
        for tst_item in self.items_list:
            self.addItem(tst_item)

    def someting_click(self, item):
        self.file_clickled.emit({"isdir":item.f_isdir, "path":item.f_path})

    def clicked_twise(self, item):
        self.someting_click(item)


class PathButtons(QWidget):
    up_dir_clickled = Signal(str)
    def __init__(self, parent = None):
        super(PathButtons, self).__init__()

        self.main_h_lay = QHBoxLayout()
        self.lst_butt = []
        self.main_h_lay.addStretch()
        self.setLayout(self.main_h_lay)

        dir_path = os.path.dirname(os.path.abspath(__file__))
        self._root_icon = QIcon()
        root_icon_path = dir_path + os.sep + "resources" \
        + os.sep + "root.png"
        self._root_icon.addFile(root_icon_path, mode = QIcon.Normal)

        tmp_lab = QLabel("dummy text")
        p_size = tmp_lab.font().pointSize()
        self._curr_dir_font = QFont()
        self._curr_dir_font.setPointSize(p_size + 3)
        self._curr_dir_font.setBold(True)
        self._curr_dir_font.setUnderline(True)

    def update_list(self, new_list):
        for single_widget in self.lst_butt:
            single_widget.deleteLater()
            self.main_h_lay.removeWidget(single_widget)

        self.lst_butt = []
        path_str = ""
        parent_dir_path = None
        for dir_name in new_list[:-1]:
            new_butt = QPushButton(dir_name)
            if dir_name == "":
                logging.info("empty dir_name")
                new_butt.setIcon(self._root_icon)

            path_str += dir_name + "/"
            new_butt.own_path = path_str
            parent_dir_path = str(path_str)
            new_butt.clicked.connect(self.dir_clicked)
            self.lst_butt.append(new_butt)
            self.main_h_lay.addWidget(new_butt)

            new_lab = QLabel(">")
            self.lst_butt.append(new_lab)
            self.main_h_lay.addWidget(new_lab)

        new_lab = QLabel(new_list[-1])
        new_lab.setFont(self._curr_dir_font)

        self.lst_butt.append(new_lab)
        self.main_h_lay.addWidget(new_lab)

        return parent_dir_path

    def dir_clicked(self):
        next_path = str(self.sender().own_path)
        self.up_dir_clickled.emit(next_path)


class PathBar(QWidget):
    clicked_up_dir = Signal(str)
    def __init__(self, parent = None):
        super(PathBar, self).__init__(parent)
        main_h_layout = QHBoxLayout()
        self.path_buttons = PathButtons(self)
        self.path_buttons.up_dir_clickled.connect(self.up_dir)
        self.scroll_path = QScrollArea()
        self.scroll_path.setWidgetResizable(True)
        self.scroll_path.setWidget(self.path_buttons)
        self.hscrollbar = self.scroll_path.horizontalScrollBar()
        self.hscrollbar.rangeChanged.connect(self.scroll_2_right)
        main_h_layout.addWidget(self.scroll_path)
        self.back_dir_butt = QPushButton("\n Go Back \n . . \u2B8C  \n")
        self.back_dir_butt.clicked.connect(self.back_one_dir)
        main_h_layout.addWidget(self.back_dir_butt)
        self.par_dir = None
        self.setLayout(main_h_layout)
        self.setFixedHeight(self.height() * 2.6)

    def back_one_dir(self):
        self.up_dir(self.par_dir)

    def scroll_2_right(self, minimum, maximum):
        self.hscrollbar.setValue(maximum)

    def update_list(self, new_list):
        self.par_dir = self.path_buttons.update_list(new_list)

    def up_dir(self, next_path):
        if self.par_dir is not None:
            self.clicked_up_dir.emit(next_path)


class ReqDirList(QThread):
    ended = Signal(list)
    def __init__(
        self, show_hidden = False, curr_path = None, my_handler = None
    ):
        super(ReqDirList, self).__init__()
        self.my_handler = my_handler
        self.show_hidden = show_hidden
        try:
            if curr_path[-1] != "/":
                curr_path += "/"

        except IndexError:
            curr_path = "/"

        self.curr_path = str(curr_path)

    def run(self):
        cmd = {"nod_lst":"", "cmd_str":["get_dir_ls", self.curr_path]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = self.my_handler
        )
        os_listdir = lst_req.result_out()
        lst_dir = []
        try:
            for file_dict in os_listdir:
                f_name = file_dict["fname"]
                f_isdir = file_dict["isdir"]
                if f_name[0] != "." or self.show_hidden:
                    f_path = self.curr_path + f_name
                    lst_dir.append(
                        {
                            "name": f_name, "isdir":  f_isdir, "path": f_path
                        }
                    )

        except TypeError:
            lst_dir = []

        self.ended.emit(lst_dir)


class FileBrowser(QDialog):
    select_done = Signal(str, bool)
    def __init__(
        self, parent = None, path_ini = "/", limit_path = "/",
        only_dir = False, runner_handler = None
    ):
        super(FileBrowser, self).__init__(parent)

        self.main_handler = runner_handler

        self.setWindowTitle("Open IMGs")
        main_v_layout = QVBoxLayout()
        self.show_hidden_check = QCheckBox("Show Hidden Files")
        self.show_hidden_check.setChecked(False)
        self.show_hidden_check.stateChanged.connect(self.refresh_content)
        hi_h_layout = QHBoxLayout()

        self.rad_but_file_dir = QRadioButton("File/Dir")
        self.rad_but_name_abc = QRadioButton("Name(ABC)")
        self.rad_but_name_123 = QRadioButton("Name(123)")
        hi_h_layout.addWidget(self.rad_but_file_dir)
        hi_h_layout.addWidget(self.rad_but_name_abc)
        hi_h_layout.addWidget(self.rad_but_name_123)
        self.rad_but_name_abc.setChecked(True)

        self.rad_but_file_dir.toggled.connect(self.refresh_sorted1)
        self.rad_but_name_abc.toggled.connect(self.refresh_sorted1)
        self.rad_but_name_123.toggled.connect(self.refresh_sorted1)

        hi_h_layout.addStretch()
        hi_h_layout.addWidget(self.show_hidden_check)
        main_v_layout.addLayout(hi_h_layout)

        self.only_dir = only_dir
        logging.info("FileBrowser.only_dir =" + str(self.only_dir))

        self.status_label = QLabel(" ")

        self.path_bar = PathBar(self)
        self.path_bar.clicked_up_dir.connect(self.build_content)
        main_v_layout.addWidget(self.path_bar)

        self.lst_vw =  MyDirView_list()

        self.ini_path = limit_path
        self.build_content(path_ini)

        self.lst_vw.file_clickled.connect(self.fill_clik)
        main_v_layout.addWidget(self.lst_vw)

        low_h_layout = QHBoxLayout()

        self.label_pos = -1
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_label)
        timer.start(500)

        self.imp_dir_path = QLineEdit()
        low_h_layout.addWidget(self.imp_dir_path)
        self.imp_dir_path.textChanged.connect(self.new_path_text)

        low_h_layout.addWidget(self.status_label)
        self.OpenButton = QPushButton(" Open ")
        self.OpenButton.clicked.connect(self.open_file)
        low_h_layout.addWidget(self.OpenButton)
        self.OpenButton.setEnabled(True)

        CancelButton = QPushButton(" Cancel ")
        CancelButton.clicked.connect(self.cancel_opp)
        low_h_layout.addWidget(CancelButton)

        main_v_layout.addLayout(low_h_layout)
        self.setLayout(main_v_layout)
        self.show()

    def build_content(self, path_in):
        self.curr_path = path_in
        self.refresh_content()

    def build_paren_list(self):
        parents_list = [self.ini_path[:-1]]
        rest_of_path = self.curr_path[len(self.ini_path):]
        try:
            if rest_of_path[-1] == "/":
                rest_of_path = rest_of_path[:-1]

        except IndexError:
            rest_of_path = ""

        for single_dir in rest_of_path.split("/"):
            parents_list.append(single_dir)

        self.path_bar.update_list(parents_list)

    def refresh_content(self):
        try:
            self.OpenButton.setEnabled(False)

        except AttributeError:
            logging.info("OpenButton not ready yet")

        self.current_file = None
        self.build_paren_list()
        show_hidden = self.show_hidden_check.isChecked()
        self.try_2_kill_thread()
        self.refresh_qthread = ReqDirList(
            show_hidden = show_hidden, curr_path = self.curr_path,
            my_handler = self.main_handler
        )
        self.refresh_qthread.ended.connect(self.done_requesting)
        self.label_pos = 1
        self.refresh_qthread.start()

    def refresh_label(self):
        double_str = "    Opening" * 2
        if self.label_pos > 0:
            self.label_pos += 1
            if self.label_pos > 10:
                self.label_pos = 1

            str_4_label = double_str[self.label_pos:self.label_pos + 9]
            self.status_label.setText(str_4_label)

        else:
            self.OpenButton.setEnabled(True)

    def new_path_text(self, new_path):
        self.typed_path = str(new_path)

    def done_requesting(self, lst_dir):
        self.lst_vw.enter_list(lst_in = lst_dir)
        self.status_label.setText(" ")
        self.label_pos = -1
        self.refresh_sorted1()
        self.imp_dir_path.setText(
            str(self.curr_path)
        )
        self.typed_path = None
        self.try_2_kill_thread()

    def refresh_sorted1(self):
        if self.rad_but_file_dir.isChecked():
            self.lst_vw.refresh_list(sorting = "123")

        elif self.rad_but_name_abc.isChecked():
            self.lst_vw.refresh_list(sorting = "abc")

        else:
            self.lst_vw.refresh_list(sorting = "dir")

        self.OpenButton.setEnabled(True)

    def fill_clik(self, fl_dic):
        if fl_dic == self.current_file:
            self.open_file()

        self.current_file = fl_dic
        self.imp_dir_path.setText(
            str(self.current_file["path"])
        )
        self.typed_path = None

    def open_file(self):
        if self.typed_path != None:
            self.build_content(self.typed_path)

        else:
            try:
                if self.current_file["isdir"]:
                    self.build_content(self.current_file["path"])

                elif self.only_dir:
                    self.select_done.emit(
                        self.curr_path, True
                    )
                    self.OpenButton.setEnabled(True)
                    self.close()

                else:
                    self.select_done.emit(
                        self.current_file["path"], self.only_dir
                    )
                    self.OpenButton.setEnabled(True)
                    self.close()

            except TypeError:
                if self.only_dir:
                    self.select_done.emit(
                        self.curr_path, True
                    )
                    self.close()

                self.OpenButton.setEnabled(True)

    def try_2_kill_thread(self):
        try:
            self.refresh_qthread.quit()
            #self.refresh_qthread.wait()
            logging.info("killed thread (FileBrowser)")

        except AttributeError:
            logging.info("No need to kill thread (FileBrowser)")

    def cancel_opp(self):
        self.label_pos = -1
        self.OpenButton.setEnabled(True)
        self.close()
        self.try_2_kill_thread()

