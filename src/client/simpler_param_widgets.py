"""
DUI2's simpler parameters widgets

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

import os, sys, zlib, json, requests

default_max_nproc = 4

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from init_firts import ini_data
from exec_utils import Mtz_Data_Request

def _get_all_direct_layout_widget_children(parent):
    """Walk a widget tree and get all non-QLayout direct children

    Args:
        parent(QLayout): The layout to walk

    Returns:
        (List[QWidget]): Any widgets directly attached to layouts in this
    """
    children = []
    if isinstance(parent, QLayout):
        for child in [parent.itemAt(i) for i in range(parent.count())]:
            children.extend(_get_all_direct_layout_widget_children(child))

    elif hasattr(parent, "widget"):
        if parent.widget():
            children.append(parent.widget())

    return children


class DefaultComboBox(QComboBox):
    """A ComboBox initialised with a list of items and keeps track of which one
    is default"""

    def __init__(self, local_path, items, default_index=0):
        super(DefaultComboBox, self).__init__()
        self.local_path = local_path
        self.item_list = items
        self.default_index = default_index
        for item in items:
            self.addItem(item)

        self.setCurrentIndex(self.default_index)


class SimpleParamTab(QWidget):
    """Base class shared by all simple parameter tabs"""

    item_changed = Signal(str, str, int)
    #item_to_remove = Signal(str)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                else:
                    self.clearLayout(item.layout())


    def update_param(self, param_in, value_in):
        print("\n update_param (Simple)", param_in, value_in)

        for widget in self.children():
            widget_path = None
            if isinstance(widget, QLineEdit):
                widget_path = widget.local_path
                widget_value = str(widget.text())

            if isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
                widget_path = widget.local_path
                widget_value = str(widget.value())

            if isinstance(widget, DefaultComboBox):
                widget_path = widget.local_path
                widget_value = str(widget.currentText())

            if widget_path == param_in:
                if widget_value == value_in:
                    print("No need to change parameter (same value)")

                else:
                    self.do_emit = False
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value_in))

                    if(
                        isinstance(widget, QDoubleSpinBox) or
                        isinstance(widget, QSpinBox)
                    ):
                        try:
                            widget.setValue(float(value_in))

                        except ValueError:
                            print("\n param_in =", param_in)
                            print("value_in =", value_in, "\n")
                            print("skipping attempt to convert string to float \n")


                    if isinstance(widget, DefaultComboBox):
                        widget.setCurrentText(str(value_in))

                    self.do_emit = True

    def update_all_pars(self, tup_lst_pars):
        print("\n (Simple Widget) \n time to update par to:", tup_lst_pars, "\n")
        for par_dic in tup_lst_pars[0]:
            self.update_param(par_dic["name"], par_dic["value"])

    def do_emit_signal(self, str_path, str_value):
        if self.do_emit:
            self.item_changed.emit(str_path, str_value, 0)

        self.do_emit = True #TODO: find out if this line is needed

    def spnbox_finished(self):
        print("spnbox_finished")
        sender = self.sender()
        value = sender.value()
        str_path = str(sender.local_path)
        '''
        #TODO find out why there is a "item_to_remove" signal
        if sender.specialValueText() and value == sender.minimum():
            self.item_to_remove.emit(str_path)

        else:
        '''
        str_value = str(value)
        self.do_emit_signal(str_path, str_value)

    def combobox_changed(self, value):
        print("combobox_changed")
        sender = self.sender()
        str_value = str(sender.item_list[value])
        str_path = str(sender.local_path)
        '''
        #TODO find out why there is a "item_to_remove" signal
        if sender.currentIndex() == sender.default_index:
            self.item_to_remove.emit(str_path)
        else:
        '''
        self.do_emit_signal(str_path, str_value)

    def line_changed(self):
        sender = self.sender()
        str_value = sender.text()
        str_path = str(sender.local_path)

        self.do_emit_signal(str_path, str_value)


class ProgBarBox(QProgressDialog):
    def __init__(self, max_val=100, min_val=0, text="Working", parent = None):
        print("ProgBarBox __init__")

        if max_val <= min_val:
            raise ValueError("max_val must be larger than min_val")

        super(ProgBarBox, self).__init__(
            labelText=text,
            minimum=min_val,
            maximum=max_val,
            parent=None)

        self.setValue(min_val)
        self.setWindowTitle("Import DataSet")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumDuration(50)
        self.setCancelButton(None)
        self.show()

    def __call__(self, updated_val):
        self.setValue(updated_val)
        loop = QEventLoop()
        QTimer.singleShot(10, loop.quit)
        loop.exec_()

    def ended(self):
        self.setValue(100)
        print("ProgBarBox ended")
        self.close()


def iter_tree(my_dict, currentItem, show_hidden):
    for child_dict in my_dict["list_child"]:
        new_item_text = str(child_dict["file_name"])
        if new_item_text[0] != "." or show_hidden:
            new_item = QTreeWidgetItem(currentItem)
            new_item.file_path = child_dict["file_path"]
            if child_dict["isdir"]:
                new_item_text = new_item_text + "  ...  [ Dir ]"
                new_item.isdir = True

            else:
                new_item.isdir = False


            new_item.setText(0, new_item_text)
            if my_dict["isdir"]:
                iter_tree(child_dict, new_item, show_hidden)


class MyTree(QTreeWidget):
    def __init__(self, parent=None):
        super(MyTree, self).__init__(parent=parent)

    def fillTree(self, lst_dic, show_hidden):
        self.clear()
        iter_tree(lst_dic, self, show_hidden)


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
        self.t_view.clicked[QModelIndex].connect(self.node_clicked)
        self.open_select_butt.clicked.connect(self.set_selection)
        self.cancel_butt.clicked.connect(self.cancel_opn)

        self.setLayout(mainLayout)
        cmd = {"nod_lst":[""], "cmd_lst":["dir_tree"]}
        self.my_bar(3)

        data_init = ini_data()
        uni_url = data_init.get_url()

        req_get = requests.get(
            uni_url, stream = True, params = cmd
        )
        compresed = req_get.content
        dic_str = zlib.decompress(compresed)
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
            print("select file first")

        else:
            print(
                "\n set_selection:", self.last_file_clicked,
                "\n dir_selected:", self.dir_selected
            )
            self.file_or_dir_selected.emit(
                self.last_file_clicked, self.dir_selected
            )
            self.close()

    def node_clicked(self, it_index):
        item = self.t_view.itemFromIndex(it_index)
        if item.isdir:
            print("\n Clicked on DIR \n ")
            self.open_select_butt.setText("Open Dir")

        else:
            print("\n Clicked on FILE \n ")
            self.open_select_butt.setText("Open File")

        str_select_path = str(item.file_path)
        if str_select_path == self.last_file_clicked:
            self.set_selection()

        self.dir_selected = item.isdir
        self.last_file_clicked = str_select_path
        print("item.file_path =", self.last_file_clicked)

    def cancel_opn(self):
        self.close()


class LocalFileBrowser(QDialog):
    file_or_dir_selected = Signal(str, bool)
    def __init__(self, parent=None):
        super(LocalFileBrowser, self).__init__(parent)

        self.setWindowTitle("Open IMGs")

        self.last_file_clicked = None

        self.fil_sys_mod = QFileSystemModel()
        self.fil_sys_mod.setRootPath(QDir.homePath())
        self.t_view =  QTreeView()
        self.t_view.setModel(self.fil_sys_mod)
        self.t_view.setSortingEnabled(True)

        tmp_width = self.t_view.columnWidth(0)
        self.t_view.setColumnWidth(0, tmp_width * 3)

        self.open_select_butt = QPushButton("Open ...")
        self.cancel_butt = QPushButton("Cancel")

        mainLayout = QVBoxLayout()

        top_hbox = QHBoxLayout()
        top_hbox.addStretch()
        mainLayout.addLayout(top_hbox)

        mainLayout.addWidget(self.t_view)

        bot_hbox = QHBoxLayout()
        bot_hbox.addStretch()
        bot_hbox.addWidget(self.open_select_butt)
        bot_hbox.addWidget(self.cancel_butt)
        mainLayout.addLayout(bot_hbox)

        self.t_view.clicked.connect(self.node_clicked)
        self.open_select_butt.clicked.connect(self.set_selection)
        self.cancel_butt.clicked.connect(self.cancel_opn)

        self.setLayout(mainLayout)
        self.show()

    def node_clicked(self, it_index):
        index = self.t_view.currentIndex()
        new_path = self.fil_sys_mod.filePath(index)
        new_info = self.fil_sys_mod.fileInfo(index)
        is_dir = new_info.isDir()
        if is_dir:
            print("\n Clicked on DIR \n ")
            self.open_select_butt.setText("Open Dir")

        else:
            print("\n Clicked on FILE \n ")
            self.open_select_butt.setText("Open File")

        str_select_path = str(new_path)
        if str_select_path == self.last_file_clicked:
            self.set_selection()

        self.dir_selected = is_dir
        self.last_file_clicked = str_select_path

    def set_selection(self):
        if self.last_file_clicked == None:
            print("select file first")

        else:
            self.file_or_dir_selected.emit(
                self.last_file_clicked, self.dir_selected
            )
            self.close()

    def cancel_opn(self):
        self.close()

def build_template(str_path_in):
    print("\ntime to build template from:\n", str_path_in)

    found_a_digit = False
    for pos, single_char in enumerate(str_path_in):
        if single_char in "0123456789":
            if found_a_digit:
                last_digit_pos = pos

            found_a_digit = True

        else:
            found_a_digit = False

    for pos in range(last_digit_pos, 0, -1):
        if str_path_in[pos:pos + 1] not in "0123456789":
            begin_digit_pos = pos
            break

    template_str = str_path_in[0:begin_digit_pos + 1] + "#" * (
        last_digit_pos - begin_digit_pos
    ) + str_path_in[last_digit_pos + 1:]

    star_str = str_path_in[
        0:begin_digit_pos + 1
    ] + "*" + str_path_in[last_digit_pos + 1:]

    return template_str, star_str


class RootWidg(QWidget):
    def __init__(self, parent = None):
        super(RootWidg, self).__init__(parent)
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        big_label = QLabel("Root:")
        big_label.setFont(
            QFont("Monospace", font_point_size + 3, QFont.Bold)
        )
        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(QLabel("Nothing to do here ..."))
        self.setLayout(self.main_vbox)

    def reset_pars(self):
        print("reset_pars(Root) ... dummy")

    def update_all_pars(self, tup_lst_pars):
        print("update_all_pars(Root)", tup_lst_pars, "... dummy")

    def update_param(self, str_path, str_value):
        print("update_param(Root)", str_path, str_value, "... dummy")




class ImportWidget(QWidget):
    '''
        This widget behaves differently from mos of the other  << simple >>
        parameter widgets, every time the user changes a parameter DUI should
        refresh all parameter since there are some parameter that exclude others
    '''
    all_items_changed = Signal(list)
    def __init__(self, parent = None):
        super(ImportWidget, self).__init__(parent)
        self.do_emit = True
        self.dir_selected = None
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        self.state_label = QLabel("   ...")
        self.state_label.setFont(
            QFont("Monospace", font_point_size + 1, QFont.Bold)
        )

        self.imp_txt = QLineEdit()
        self.imp_txt.editingFinished.connect(self.line_changed)

        self.open_butt = QPushButton("\n Open Images \n")
        self.open_butt.clicked.connect(self.open_dir_widget)

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.open_butt)
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.state_label)
        self.main_vbox.addWidget(self.imp_txt)
        self.main_vbox.addStretch()
        self.setLayout(self.main_vbox)

    def set_selection(self, str_select, isdir):
        print("str_select =", str_select, "isdir =", isdir)
        self.dir_selected = isdir
        if self.dir_selected:
            self.imp_txt.setText(str_select)

        else:
            self.imp_txt.setText(build_template(str_select)[0])

        self.line_changed()

    def open_dir_widget(self):

        data_init = ini_data()
        run_local = data_init.get_if_local()
        if run_local:
            self.open_widget = LocalFileBrowser(self)

        else:
            self.open_widget = FileBrowser(self)

        self.open_widget.file_or_dir_selected.connect(self.set_selection)

    def reset_pars(self):
        self.imp_txt.setText("")

    def line_changed(self):
        print("line_changed")
        #sender = self.sender()
        str_value = self.imp_txt.text()
        if self.dir_selected:
            str_path = "input.directory"

        else:
            str_path = "input.template"

        self.state_label.setText(str_path)
        self.all_items_changed.emit([[[str_path, str_value]]])

    def update_all_pars(self, tup_lst_pars):
        print(
            "update_all_pars(ImportWidget)",
            tup_lst_pars
        )

        for n, par in enumerate(tup_lst_pars):
            print("n=", n, "par=", par)

        #TODO in the future there will be more than one parameter to update,
        #TODO the next try: will go inside a loop and consequently will be
        #TODO different
        try:
            inp_val = str(tup_lst_pars[0][0]["value"])
            print("inp_val =", inp_val)
            self.imp_txt.setText(inp_val)

            input_parmeter = str(tup_lst_pars[0][0]["name"])
            print("input_parmeter =", input_parmeter)
            self.state_label.setText(input_parmeter)

        except IndexError:
            print(" Not copying parameters from node (IndexError)")
            self.imp_txt.setText("")
            self.state_label.setText("...")

    def update_param(self, str_path, str_value):
        print(
            "update_param(ImportWidget)",
            str_path, str_value, "... dummy"
        )

class MaskWidget(QWidget):
    all_items_changed = Signal(list)
    component_changed = Signal(str)
    def __init__(self, parent = None):
        super(MaskWidget, self).__init__(parent)
        self.do_emit = True
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        self.cmd_label = QLabel("")
        self.cmd_label.setFont(QFont(
            "Monospace", font_point_size -1, QFont.Bold
        ))

        self.main_vbox = QVBoxLayout()

        self.rad_but_rect_mask = QRadioButton("Rectangle")
        self.main_vbox.addWidget(self.rad_but_rect_mask)
        self.rad_but_circ_mask = QRadioButton("Circle")
        self.main_vbox.addWidget(self.rad_but_circ_mask)
        self.rad_but_poly_mask = QRadioButton("Polygon")
        self.main_vbox.addWidget(self.rad_but_poly_mask)
        self.main_vbox.addWidget(self.cmd_label)

        self.rad_but_rect_mask.toggled.connect(self.toggle_funtion)
        self.rad_but_circ_mask.toggled.connect(self.toggle_funtion)
        self.rad_but_poly_mask.toggled.connect(self.toggle_funtion)

        self.setLayout(self.main_vbox)
        self.toggle_funtion()
        self.reset_pars()

    def toggle_funtion(self):
        print("toggle_funtion")
        if self.rad_but_rect_mask.isChecked():
            self.stat = "rect"

        elif self.rad_but_circ_mask.isChecked():
            self.stat = "circ"

        elif self.rad_but_poly_mask.isChecked():
            self.stat = "poly"

        else:
            print("something is wrong here")
            self.stat = None

        print("self.stat =", self.stat)
        self.component_changed.emit(str(self.stat))

    def update_all_pars(self, par_lst_0):
        print("update_all_pars:", par_lst_0)
        self.comp_list = []
        for par_dic in par_lst_0[0][0:-1]:
            single_comp_lst = [str(par_dic["name"]), str(par_dic["value"])]
            self.comp_list.append(single_comp_lst)

        self.update_comp_label()

    def reset_pars(self):
        print("\n reset_pars(MaskWidget) \n")
        self.comp_list = []
        self.update_comp_label()

    def update_comp_label(self):
        label_str = ""
        for comp in self.comp_list:
            single_comp_str = str(comp[0]) + " >> " + str(comp[1])
            label_str += "\n" + single_comp_str

        self.cmd_label.setText(label_str)

    def get_new_comp(self, comp_dict):
        print("mask new comp_dict =", comp_dict)
        if comp_dict["type"] == "rect":
            inner_lst_pair = [
                "untrusted.rectangle",
                str(comp_dict["x_ini"]) + "," + str(comp_dict["x_end"]) + "," +
                str(comp_dict["y_ini"]) + "," + str(comp_dict["y_end"]) + ","
            ]
            self.comp_list.append(inner_lst_pair)

        elif comp_dict["type"] == "circ":
            inner_lst_pair = [
                "untrusted.circle",
                str(comp_dict["x_c"]) + "," + str(comp_dict["y_c"]) + "," +
                str(comp_dict["r"]) + "," ,
            ]
            self.comp_list.append(inner_lst_pair)

        elif comp_dict["type"] == "poly":
            #try:
            if self.comp_list == [] or self.comp_list[-1][0] != "untrusted.polygon":
                inner_lst_pair = [
                    "untrusted.polygon",
                    str(comp_dict["x_end"]) + "," + str(comp_dict["y_end"]) + ","
                ]
                self.comp_list.append(inner_lst_pair)

            elif self.comp_list[-1][0] == "untrusted.polygon":
                str_tail = str(comp_dict["x_end"]) + "," + str(comp_dict["y_end"]) + ","
                self.comp_list[-1][1] += str_tail

            #except IndexError:
            #    print("TMP IndexError")

        self.comp_list_update()


    def build_full_list(self):
        first_list = list(self.comp_list)
        first_list.append(["output.mask", "tmp_mask.pickle"])
        print("first_list =", first_list, "\n")

        full_list = [
            first_list,
            [
                ["input.mask", "tmp_mask.pickle"]
            ]
        ]
        return full_list

    def comp_list_update(self):
        print("\n self.comp_list =", self.comp_list)
        new_full_list = self.build_full_list()
        self.all_items_changed.emit(new_full_list)
        self.update_comp_label()
        return new_full_list


class FindspotsSimplerParameterTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the spot-finder, this widget is the first to appear once the button
    "Find Sots" is clicked
    """

    def __init__(self, parent=None):
        super(FindspotsSimplerParameterTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        xds_gain_label = QLabel("Gain")
        xds_gain_spn_bx = QDoubleSpinBox()
        xds_gain_spn_bx.local_path = "spotfinder.threshold.dispersion.gain"
        xds_gain_spn_bx.setValue(1.0)
        xds_gain_spn_bx.editingFinished.connect(self.spnbox_finished)

        xds_sigma_background_label = QLabel("Sigma background")
        xds_sigma_background_spn_bx = QDoubleSpinBox()
        xds_sigma_background_spn_bx.setValue(6.0)
        xds_sigma_background_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.sigma_background"
        )
        xds_sigma_background_spn_bx.editingFinished.connect(self.spnbox_finished)

        xds_sigma_strong_label = QLabel("Sigma strong")
        xds_sigma_strong_spn_bx = QDoubleSpinBox()
        xds_sigma_strong_spn_bx.setValue(3.0)
        xds_sigma_strong_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.sigma_strong"
        )
        xds_sigma_strong_spn_bx.editingFinished.connect(self.spnbox_finished)

        xds_global_threshold_label = QLabel("Global threshold")
        xds_global_threshold_spn_bx = QDoubleSpinBox()
        xds_global_threshold_spn_bx.setMaximum(9999.99)
        xds_global_threshold_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.global_threshold"
        )
        xds_global_threshold_spn_bx.editingFinished.connect(self.spnbox_finished)


        xds_gain_hb = QHBoxLayout()
        xds_gain_hb.addWidget(xds_gain_label)
        xds_gain_hb.addWidget(xds_gain_spn_bx)
        self.main_v_layout.addLayout(xds_gain_hb)

        xds_sigma_background_hb = QHBoxLayout()
        xds_sigma_background_hb.addWidget(xds_sigma_background_label)
        xds_sigma_background_hb.addWidget(xds_sigma_background_spn_bx)
        self.main_v_layout.addLayout(xds_sigma_background_hb)

        xds_sigma_strong_hb = QHBoxLayout()
        xds_sigma_strong_hb.addWidget(xds_sigma_strong_label)
        xds_sigma_strong_hb.addWidget(xds_sigma_strong_spn_bx)
        self.main_v_layout.addLayout(xds_sigma_strong_hb)

        xds_global_threshold_hb = QHBoxLayout()
        xds_global_threshold_hb.addWidget(xds_global_threshold_label)
        xds_global_threshold_hb.addWidget(xds_global_threshold_spn_bx)
        self.main_v_layout.addLayout(xds_global_threshold_hb)


        self.main_v_layout.addStretch()
        self.lst_var_widg = _get_all_direct_layout_widget_children(self.main_v_layout)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class IndexSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the indexer, this widget is the first to appear once the button
    "Index" is clicked
    """

    def __init__(self, phl_obj=None, parent=None):
        super(IndexSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        hbox_method = QHBoxLayout()
        label_method_62 = QLabel("Indexing method")
        hbox_method.addWidget(label_method_62)
        box_method_62 = DefaultComboBox("indexing.method", ["fft3d", "fft1d",
            "real_space_grid_search", "low_res_spot_match"])
        box_method_62.currentIndexChanged.connect(self.combobox_changed)

        hbox_method.addWidget(box_method_62)

        max_cell_label = QLabel("Max cell")
        max_cell_spn_bx = QDoubleSpinBox()
        max_cell_spn_bx.setSingleStep(5.0)
        max_cell_spn_bx.local_path = "indexing.max_cell"
        max_cell_spn_bx.setSpecialValueText("Auto")
        max_cell_spn_bx.editingFinished.connect(self.spnbox_finished)

        space_group_label = QLabel("Space group")
        space_group_line = QLineEdit()
        # Simple validator to allow only characters in H-M symbols
        regex = QRegExp("[ABCPIFR][0-9a-d\-/:nmHR]+")
        validatorHM = QRegExpValidator(regex)
        space_group_line.setValidator(validatorHM)
        space_group_line.local_path = "indexing.known_symmetry.space_group"
        space_group_line.editingFinished.connect(self.line_changed)

        unit_cell_label = QLabel("Unit cell")
        unit_cell_line = QLineEdit()
        regex = QRegExp("[0-9\., ]+")
        validatorUC = QRegExpValidator(regex)
        unit_cell_line.setValidator(validatorUC)
        unit_cell_line.local_path = "indexing.known_symmetry.unit_cell"
        unit_cell_line.editingFinished.connect(self.line_changed)

        self.main_v_layout.addLayout(hbox_method)

        qf = QFormLayout()
        qf.addRow(max_cell_label, max_cell_spn_bx)
        qf.addRow(space_group_label, space_group_line)
        qf.addRow(unit_cell_label, unit_cell_line)
        self.main_v_layout.addLayout(qf)

        self.main_v_layout.addStretch()

        self.lst_var_widg = _get_all_direct_layout_widget_children(self.main_v_layout)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class RefineBravaiSimplerParamTab(SimpleParamTab):
    def __init__(self, parent=None):
        super(RefineBravaiSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        hbox_lay_outlier_algorithm = QHBoxLayout()
        label_outlier_algorithm = QLabel("Outlier rejection algorithm")

        hbox_lay_outlier_algorithm.addWidget(label_outlier_algorithm)
        box_outlier_algorithm = DefaultComboBox(
            "refinement.reflections.outlier.algorithm", ["null", "Auto", "mcd",
            "tukey", "sauter_poon"], default_index=1)
        box_outlier_algorithm.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_outlier_algorithm.addWidget(box_outlier_algorithm)
        self.main_v_layout.addLayout(hbox_lay_outlier_algorithm)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_outlier_algorithm)
        self.lst_var_widg.append(label_outlier_algorithm)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class RefineSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the refiner, this widget is the first to appear once the button
    "Refine" is clicked
    """

    def __init__(self, parent=None):
        super(RefineSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        hbox_lay_scan_varying = QHBoxLayout()

        label_scan_varying = QLabel("Scan varying refinement")

        hbox_lay_scan_varying.addWidget(label_scan_varying)

        box_scan_varying = DefaultComboBox("refinement.parameterisation.scan_varying",
            ["True", "False", "Auto"], default_index=2)
        box_scan_varying.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_scan_varying.addWidget(box_scan_varying)
        self.main_v_layout.addLayout(hbox_lay_scan_varying)

        ###########################################################################

        hbox_lay_outlier_algorithm = QHBoxLayout()
        label_outlier_algorithm = QLabel("Outlier rejection algorithm")

        hbox_lay_outlier_algorithm.addWidget(label_outlier_algorithm)
        box_outlier_algorithm = DefaultComboBox(
            "refinement.reflections.outlier.algorithm", ["null", "Auto", "mcd",
            "tukey", "sauter_poon"], default_index=1)
        box_outlier_algorithm.currentIndexChanged.connect(self.combobox_changed)

        hbox_lay_outlier_algorithm.addWidget(box_outlier_algorithm)
        self.main_v_layout.addLayout(hbox_lay_outlier_algorithm)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_scan_varying)
        self.lst_var_widg.append(label_scan_varying)

        self.lst_var_widg.append(box_outlier_algorithm)
        self.lst_var_widg.append(label_outlier_algorithm)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class IntegrateSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the integrate algorithm, this widget is the first to appear once the
    button "Integrate" is clicked
    """

    def __init__(self, parent=None):
        super(IntegrateSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        PrFit_lay_out = QHBoxLayout()
        label_PrFit = QLabel("Use profile fitting")
        PrFit_lay_out.addWidget(label_PrFit)

        PrFit_comb_bx = DefaultComboBox("integration.profile.fitting",
            ["True", "False", "Auto"])
        PrFit_comb_bx.currentIndexChanged.connect(self.combobox_changed)

        PrFit_lay_out.addWidget(PrFit_comb_bx)
        self.main_v_layout.addLayout(PrFit_lay_out)

        hbox_lay_algorithm_53 = QHBoxLayout()
        label_algorithm_53 = QLabel("Background algorithm")
        hbox_lay_algorithm_53.addWidget(label_algorithm_53)

        box_algorithm_53 = DefaultComboBox("integration.background.algorithm",
            ["simple", "null", "median", "gmodel", "glm"], default_index=4)
        box_algorithm_53.currentIndexChanged.connect(self.combobox_changed)

        hbox_lay_algorithm_53.addWidget(box_algorithm_53)
        self.main_v_layout.addLayout(hbox_lay_algorithm_53)

        hbox_d_min = QHBoxLayout()
        label_d_min = QLabel("High resolution limit")
        hbox_d_min.addWidget(label_d_min)
        d_min_spn_bx = QDoubleSpinBox()
        d_min_spn_bx.local_path = "prediction.d_min"
        d_min_spn_bx.setSpecialValueText("None")
        d_min_spn_bx.setValue(0.0)
        hbox_d_min.addWidget(d_min_spn_bx)
        d_min_spn_bx.editingFinished.connect(self.spnbox_finished)
        self.main_v_layout.addLayout(hbox_d_min)

        self.main_v_layout.addStretch()
        #self.box_nproc.item_list = None
        self.lst_var_widg = _get_all_direct_layout_widget_children(
            self.main_v_layout
        )

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()

class SymmetrySimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the symmetry command, this widget is the first to appear once the button
    "Symmetry" is clicked
    """

    def __init__(self, parent=None):
        super(SymmetrySimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        label_d_min = QLabel("High resolution limit")
        hbox_d_min = QHBoxLayout()
        hbox_d_min.addWidget(label_d_min)

        d_min_spn_bx = QDoubleSpinBox()
        d_min_spn_bx.local_path = "d_min"
        d_min_spn_bx.setSpecialValueText("Auto")
        d_min_spn_bx.setValue(0.0)
        hbox_d_min.addWidget(d_min_spn_bx)

        d_min_spn_bx.editingFinished.connect(self.spnbox_finished)

        self.main_v_layout.addLayout(hbox_d_min)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(d_min_spn_bx)
        self.lst_var_widg.append(label_d_min)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class ScaleSimplerParamTab(SimpleParamTab):

    """
    This widget is the tool for tunning the simpler and most common parameters
    in the scale command, this widget is the first to appear once the button
    "Scale" is clicked
    """

    def __init__(self, parent=None):
        super(ScaleSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        #TODO: review the parameters here, they need updating

        hbox_lay_mod = QHBoxLayout()
        label_mod = QLabel("Model")

        hbox_lay_mod.addWidget(label_mod)
        box_mod = DefaultComboBox("model", ["physical", "array", "KB"])
        box_mod.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_mod.addWidget(box_mod)

        hbox_lay_wgh_opt_err = QHBoxLayout()
        label_wgh_opt_err = QLabel("Error optimisation model")

        hbox_lay_wgh_opt_err.addWidget(label_wgh_opt_err)
        box_wgh_opt_err = DefaultComboBox("weighting.error_model.error_model",
            ["basic", "None"])
        box_wgh_opt_err.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_wgh_opt_err.addWidget(box_wgh_opt_err)
        """
        weighting {
          error_model {
            error_model = *basic None
        """

        hbox_d_min = QHBoxLayout()
        d_min_label = QLabel("High resolution limit")
        d_min_spn_bx = QDoubleSpinBox()
        d_min_spn_bx.local_path = "cut_data.d_min"
        d_min_spn_bx.setSpecialValueText("None")
        d_min_spn_bx.setValue(0.0)
        hbox_d_min.addWidget(d_min_label)
        hbox_d_min.addWidget(d_min_spn_bx)

        d_min_spn_bx.editingFinished.connect(self.spnbox_finished)

        self.main_v_layout.addLayout(hbox_lay_mod)
        self.main_v_layout.addLayout(hbox_lay_wgh_opt_err)
        self.main_v_layout.addLayout(hbox_d_min)


        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_mod)
        self.lst_var_widg.append(label_mod)
        self.lst_var_widg.append(box_wgh_opt_err)
        self.lst_var_widg.append(label_wgh_opt_err)
        self.lst_var_widg.append(d_min_spn_bx)
        self.lst_var_widg.append(d_min_label)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class CombineExperimentSimplerParamTab(SimpleParamTab):
    def __init__(self, parent=None):
        super(CombineExperimentSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        hbox_lay_dummy_1 = QHBoxLayout()
        label_dummy_1 = QLabel("Dummy TMP selector")

        hbox_lay_dummy_1.addWidget(label_dummy_1)
        box_dummy_2 = DefaultComboBox(
            "scope_1.scope_2.definition", [
                "opt 1", "opt 2", "None", "Auto"
            ], default_index=1)
        box_dummy_2.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_dummy_1.addWidget(box_dummy_2)
        self.main_v_layout.addLayout(hbox_lay_dummy_1)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_dummy_2)
        self.lst_var_widg.append(label_dummy_1)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class ExportWidget(QWidget):
    '''
        This widget is a simplified version of ImportWidget since
        there is no need interact with a remote << FileBrowser >>
    '''
    all_items_changed = Signal(list)
    find_scaled_before = Signal()
    def __init__(self, parent = None):
        super(ExportWidget, self).__init__(parent)
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        state_label = QLabel("mtz output name:")
        state_label.setFont(
            QFont("Monospace", font_point_size + 1, QFont.Bold)
        )

        self.exp_txt = QLineEdit()
        self.exp_txt.editingFinished.connect(self.line_changed)
        self.downl_but = QPushButton("Download MTZ")
        self.downl_but.clicked.connect(self.download_mtz)
        self.progress_label = QLabel("...")

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(state_label)
        self.main_vbox.addWidget(self.exp_txt)
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.downl_but)
        self.main_vbox.addWidget(self.progress_label)
        self.main_vbox.addStretch()
        self.setLayout(self.main_vbox)

    def line_changed(self):
        print("\n line_changed")
        str_value = self.exp_txt.text()
        self.all_items_changed.emit([[["mtz.hklout", str_value]]])
        print("str_value =", str_value)

    def reset_pars(self):
        self.find_scaled_before.emit()

    def is_scale_parent(self, scale_in_parents):
        if scale_in_parents:
            self.exp_txt.setText("scaled.mtz")

        else:
            self.exp_txt.setText("integrated.mtz")

        self.line_changed()

    def update_all_pars(self, tup_lst_pars):
        print(
            "update_all_pars(ImportWidget)",
            tup_lst_pars
        )
        try:
            inp_val = str(tup_lst_pars[0][0]["value"])
            print("inp_val =", inp_val)
            self.exp_txt.setText(inp_val)

        except IndexError:
            print(" Not copying parameters from node (IndexError)")
            self.exp_txt.setText("")

    def set_download_stat(self, do_enable = False, nod_num = None):
        self.setEnabled(True)
        self.exp_txt.setEnabled(not do_enable)
        self.downl_but.setEnabled(do_enable)
        self.cur_nod_num = nod_num

    def download_mtz(self):
        ini_file = os.getcwd() + os.sep + self.exp_txt.text()
        fileResul = QFileDialog.getSaveFileName(
            self, "Download MTZ File", ini_file, "Intensity  (*.mtz)"
        )
        self.file_name = fileResul[0]
        if self.file_name != '':
            self.progress_label.setText("Requesting mtz file ...")

            data_init = ini_data()
            uni_url = data_init.get_url()
            cmd = {"nod_lst":[self.cur_nod_num], "cmd_lst":["get_mtz"]}
            self.dowl_thrd = Mtz_Data_Request(uni_url, cmd)
            self.dowl_thrd.update_progress.connect(self.show_new_progress)
            self.dowl_thrd.done_download.connect(self.save_mtz_on_disc)
            self.dowl_thrd.finished.connect(self.restore_p_label)
            self.dowl_thrd.start()

        else:
            print("Canceled Operation")

    def show_new_progress(self, new_prog):
        self.progress_label.setText(
            str("Downloading: " + str(new_prog) + " %")
        )

    def save_mtz_on_disc(self, mtz_info):
        self.progress_label.setText("...")
        file_out = open(self.file_name, "wb")
        file_out.write(mtz_info)
        file_out.close()
        print(self.file_name, " writen to disk")

    def restore_p_label(self):
        self.progress_label.setText("...")
        print("Done Download")



class TmpTstWidget(QWidget):
    def __init__(self, parent=None):
        super(TmpTstWidget, self).__init__()
        self.do_emit = True

        #my_widget = MaskWidget(self)
        my_widget = ImportWidget(self)
        #my_widget = FindspotsSimplerParameterTab(self)
        #my_widget = IndexSimplerParamTab(self)
        #my_widget = RefineBravaiSimplerParamTab(self)
        #my_widget = RefineSimplerParamTab(self)
        #my_widget = IntegrateSimplerParamTab(self)
        #my_widget = SymmetrySimplerParamTab(self)
        #my_widget = ScaleSimplerParamTab(self)
        #my_widget = CombineExperimentSimplerParamTab(self)


        my_box = QVBoxLayout()
        my_box.addWidget(my_widget)
        self.setLayout(my_box)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TmpTstWidget()
    ex.show()
    sys.exit(app.exec_())
