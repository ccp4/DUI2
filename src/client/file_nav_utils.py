import sys, os
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import random
'''from client.exec_utils import (
    Mtz_Data_Request, get_request_shot, get_req_json_dat
)'''

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
        self.itemDoubleClicked.connect(self.someting_2_clicks)
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

    def someting_2_clicks(self, item):
        self.someting_click(item)


class PathButtons(QWidget):
    up_dir_clickled = Signal(str)
    def __init__(self, parent = None):
        super(PathButtons, self).__init__()
        self.main_h_lay = QHBoxLayout()
        self.lst_butt = []
        self.main_h_lay.addStretch()
        self.setLayout(self.main_h_lay)

    def update_list(self, new_list):
        for single_widget in self.lst_butt:
            single_widget.deleteLater()
            self.main_h_lay.removeWidget(single_widget)

        self.lst_butt = []
        path_str = ""
        for dir_name in new_list:
            new_butt = QPushButton(dir_name)
            path_str += dir_name + os.sep
            new_butt.own_path = path_str
            new_butt.clicked.connect(self.dir_clicked)
            self.lst_butt.append(new_butt)
            self.main_h_lay.addWidget(new_butt)

            new_lab = QLabel(">")
            self.lst_butt.append(new_lab)
            self.main_h_lay.addWidget(new_lab)


    def dir_clicked(self):
        next_path = str(self.sender().own_path)
        self.up_dir_clickled.emit(next_path)


class PathBar(QWidget):
    clicked_up_dir = Signal(str)
    def __init__(self, parent = None):
        super(PathBar, self).__init__(parent)
        mainLayout = QVBoxLayout()
        self.path_buttons = PathButtons(self)
        self.path_buttons.up_dir_clickled.connect(self.up_dir)
        self.scroll_path = QScrollArea()
        self.scroll_path.setWidgetResizable(True)
        self.scroll_path.setWidget(self.path_buttons)
        self.hscrollbar = self.scroll_path.horizontalScrollBar()
        self.hscrollbar.rangeChanged.connect(self.scroll_2_right)
        mainLayout.addWidget(self.scroll_path)
        self.setLayout(mainLayout)
        self.setFixedHeight(self.height() * 2.6)

    def scroll_2_right(self, minimum, maximum):
        self.hscrollbar.setValue(maximum)

    def update_list(self, new_list):
        self.path_buttons.update_list(new_list)

    def up_dir(self, next_path):
        self.clicked_up_dir.emit(next_path)


class FileBrowser(QDialog):
    file_or_dir_selected = Signal(str, bool)
    def __init__(self, parent=None):
        super(FileBrowser, self).__init__(parent)
        self.setWindowTitle("Open IMGs")
        mainLayout = QVBoxLayout()
        self.show_hidden_check = QCheckBox("Show Hidden Files")
        self.show_hidden_check.setChecked(False)
        self.show_hidden_check.stateChanged.connect(self.refresh_content)
        hi_h_layout = QHBoxLayout()
        hi_h_layout.addStretch()
        hi_h_layout.addWidget(self.show_hidden_check)
        mainLayout.addLayout(hi_h_layout)

        self.path_bar = PathBar(self)
        self.path_bar.clicked_up_dir.connect(self.build_content)
        mainLayout.addWidget(self.path_bar)

        self.lst_vw =  MyDirView_list()
        #self.ini_path = "/home/"
        self.ini_path = "/"
        #self.ini_path = "/Users/luiso/"

        self.build_content(self.ini_path)
        self.lst_vw.file_clickled.connect(self.fill_clik)
        mainLayout.addWidget(self.lst_vw)

        low_h_layout = QHBoxLayout()
        low_h_layout.addStretch()

        OpenButton = QPushButton(" Open ")
        OpenButton.clicked.connect(self.open_file)
        low_h_layout.addWidget(OpenButton)

        CancelButton = QPushButton(" Cancel ")
        CancelButton.clicked.connect(self.cancel_opp)
        low_h_layout.addWidget(CancelButton)

        mainLayout.addLayout(low_h_layout)
        self.setLayout(mainLayout)
        self.show()

    def build_content(self, path_in):
        self.curr_path = path_in
        self.refresh_content()

    def build_paren_list(self):
        print("self.curr_path", self.curr_path)
        parents_list = [self.ini_path[:-1]]
        rest_of_path = self.curr_path[len(self.ini_path):]
        print("rest_of_path = ", rest_of_path, "\n")
        for single_dir in rest_of_path.split(os.sep)[:-1]:
            parents_list.append(single_dir)

        self.path_bar.update_list(parents_list)

    def refresh_content(self):
        show_hidden = self.show_hidden_check.isChecked()
        self.current_file = None
        self.build_paren_list()

        cmd = "get_dir_ls " + self.curr_path
        cmd = {"nod_lst":"", "cmd_lst":["get_dir_ls " + self.curr_path]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = None
        )
        os_listdir = lst_req.result_out()
        lst_dir = []
        for nm, f_name in enumerate(os_listdir):
            if f_name[0] != "." or show_hidden:
                f_path = self.curr_path + f_name
                f_isdir = os.path.isdir(f_path)
                lst_dir.append(
                    {
                        "name": f_name, "isdir":  f_isdir, "path": f_path
                    }
                )

        self.lst_vw.enter_list(lst_dir)

    def fill_clik(self, fl_dic):
        print("path = ", fl_dic["path"])
        if fl_dic == self.current_file:
            self.open_file()

        self.current_file = fl_dic

    def open_file(self):
        try:
            if self.current_file["isdir"]:
                self.build_content(self.current_file["path"] + os.sep)

            else:
                print("Opened: ", self.current_file["path"])
                self.file_or_dir_selected.emit(self.current_file["path"], False)
                self.close()

        except TypeError:
            print("no file selected yet")

    def cancel_opp(self):
        print("Cancel clicked")
        self.close()


old_file_browser_ref = '''

def iter_tree(my_dict, currentItem, show_hidden, icon_dict):
    for child_dict in my_dict["list_child"]:
        new_item_text = str(child_dict["file_name"])
        if new_item_text[0] != "." or show_hidden:
            new_item = QTreeWidgetItem(currentItem)
            new_item.file_path = child_dict["file_path"]
            if child_dict["isdir"]:
                new_item.isdir = True
                my_icon = icon_dict["Dir"]

            else:
                new_item.isdir = False
                my_icon = icon_dict["File"]


            new_item.setText(0, new_item_text)
            new_item.setIcon(0, my_icon)

            if my_dict["isdir"]:
                iter_tree(child_dict, new_item, show_hidden, icon_dict)


class MyTree(QTreeWidget):
    def __init__(self, parent=None):
        super(MyTree, self).__init__(parent=parent)

    def fillTree(self, lst_dic, show_hidden):
        DirPixMapi = getattr(QStyle, 'SP_DirIcon')
        FilePixMapi = getattr(QStyle, 'SP_FileIcon')
        icon_dict = {
            "Dir":self.style().standardIcon(DirPixMapi),
            "File":self.style().standardIcon(FilePixMapi)
        }
        self.clear()
        iter_tree(lst_dic, self, show_hidden, icon_dict)


class FileBrowser(QDialog):
    file_or_dir_selected = Signal(str, bool)
    def __init__(self, parent=None):
        super(FileBrowser, self).__init__(parent)

        self.setWindowTitle("Open IMGs")

        self.my_bar = ProgBarBox(
            min_val = 0, max_val = 10, text = "loading dir tree"
        )
        self.my_bar(1)

        self.t_view = MyTree()
        self.open_select_butt = QPushButton("Open ...")
        self.cancel_butt = QPushButton("Cancel")
        self.show_hidden_check = QCheckBox("Show Hidden Files")
        self.show_hidden_check.setChecked(False)

        mainLayout = QVBoxLayout()

        top_hbox = QHBoxLayout()
        top_hbox.addStretch()
        top_hbox.addWidget(self.show_hidden_check)
        mainLayout.addLayout(top_hbox)

        mainLayout.addWidget(self.t_view)

        bot_hbox = QHBoxLayout()
        bot_hbox.addStretch()
        bot_hbox.addWidget(self.open_select_butt)
        bot_hbox.addWidget(self.cancel_butt)
        mainLayout.addLayout(bot_hbox)

        self.show_hidden_check.stateChanged.connect(self.redraw_dir)
        self.t_view.doubleClicked[QModelIndex].connect(self.node_clicked)
        self.t_view.clicked[QModelIndex].connect(self.node_clicked)
        self.open_select_butt.clicked.connect(self.set_selection)
        self.cancel_butt.clicked.connect(self.cancel_opn)

        self.setLayout(mainLayout)
        cmd = {"nod_lst":[""], "cmd_lst":["dir_tree"]}
        self.my_bar(3)

        data_init = ini_data()
        uni_url = data_init.get_url()

        req_shot = get_request_shot(params_in = cmd, main_handler = None)
        dic_str = req_shot.result_out()

        self.dir_tree_dict = json.loads(dic_str)

        self.my_bar(7)
        self.redraw_dir()
        self.my_bar(9)
        self.my_bar.ended()
        self.show()

    def redraw_dir(self, dummy = None):
        self.last_file_clicked = None
        self.dir_selected = None
        show_hidden = self.show_hidden_check.isChecked()
        self.open_select_butt.setText("Open ...")
        self.t_view.fillTree(self.dir_tree_dict, show_hidden)

    def set_selection(self):
        if self.last_file_clicked == None:
            logging.info("select file first")

        else:
            self.file_or_dir_selected.emit(
                self.last_file_clicked, self.dir_selected
            )
            self.close()

    def node_clicked(self, it_index):
        item = self.t_view.itemFromIndex(it_index)
        if item.isdir:
            self.open_select_butt.setText("Open Dir")

        else:
            self.open_select_butt.setText("Open File")

        str_select_path = str(item.file_path)
        if str_select_path == self.last_file_clicked:
            self.set_selection()

        self.dir_selected = item.isdir
        self.last_file_clicked = str_select_path

    def node_double_clicked(self, it_index):
        self.last_file_clicked = str(item.file_path)
        self.node_clicked(it_index)

    def cancel_opn(self):
        self.close()

'''
