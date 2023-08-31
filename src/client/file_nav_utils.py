import sys, os
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from client.exec_utils import get_req_json_dat

def sort_dict_list(lst_in):
    list_size = len(lst_in)
    for i in range(list_size):
        min_index = i
        for j in range(i + 1, list_size):
            if lst_in[min_index]["name"] > lst_in[j]["name"]:
                min_index = j

        lst_in[i], lst_in[min_index] = lst_in[min_index], lst_in[i]

    return lst_in


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
        lst_in = sort_dict_list(lst_in)
        self.items_list = []
        for single_file in lst_in:
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
        self.back_dir_butt = QPushButton("Go Back\n\n . . \u2B8C")
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


class FileBrowser(QDialog):
    file_or_dir_selected = Signal(str, bool)
    def __init__(self, parent = None, path_in = "/"):
        super(FileBrowser, self).__init__(parent)
        self.setWindowTitle("Open IMGs")
        main_v_layout = QVBoxLayout()
        self.show_hidden_check = QCheckBox("Show Hidden Files")
        self.show_hidden_check.setChecked(False)
        self.show_hidden_check.stateChanged.connect(self.refresh_content)
        hi_h_layout = QHBoxLayout()
        hi_h_layout.addStretch()
        hi_h_layout.addWidget(self.show_hidden_check)
        main_v_layout.addLayout(hi_h_layout)

        self.path_bar = PathBar(self)
        self.path_bar.clicked_up_dir.connect(self.build_content)
        main_v_layout.addWidget(self.path_bar)

        self.lst_vw =  MyDirView_list()
        self.ini_path = path_in
        self.build_content(self.ini_path)
        self.lst_vw.file_clickled.connect(self.fill_clik)
        main_v_layout.addWidget(self.lst_vw)

        low_h_layout = QHBoxLayout()
        low_h_layout.addStretch()

        OpenButton = QPushButton(" Open ")
        OpenButton.clicked.connect(self.open_file)
        low_h_layout.addWidget(OpenButton)

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
        for single_dir in rest_of_path.split("/")[:-1]:
            parents_list.append(single_dir)

        self.path_bar.update_list(parents_list)

    def refresh_content(self):
        show_hidden = self.show_hidden_check.isChecked()
        self.current_file = None
        self.build_paren_list()
        cmd = {"nod_lst":"", "cmd_str":["get_dir_ls", self.curr_path]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = None
        )
        os_listdir = lst_req.result_out()
        lst_dir = []
        for file_dict in os_listdir:
            f_name = file_dict["fname"]
            f_isdir = file_dict["isdir"]
            if f_name[0] != "." or show_hidden:
                f_path = self.curr_path + f_name
                lst_dir.append(
                    {
                        "name": f_name, "isdir":  f_isdir, "path": f_path
                    }
                )

        self.lst_vw.enter_list(lst_dir)

    def fill_clik(self, fl_dic):
        if fl_dic == self.current_file:
            self.open_file()

        self.current_file = fl_dic

    def open_file(self):
        try:
            if self.current_file["isdir"]:
                self.build_content(self.current_file["path"] + "/")

            else:
                self.file_or_dir_selected.emit(self.current_file["path"], False)
                self.close()

        except TypeError:
            print("no file selected yet")

    def cancel_opp(self):
        self.close()



