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

import os, sys, json, requests, logging

default_max_nproc = 4

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

import numpy as np

from client.init_firts import ini_data
from client.exec_utils import Mtz_Data_Request, get_req_json_dat
from client.file_nav_utils import FileBrowser


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

    def __init__(self, local_path, items, default_index = 0):
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
        logging.info("\n update_param (Simple)" + str(param_in) + str(value_in))
        try:
            self.special_check_up(param_in, value_in)

        except AttributeError:
            logging.info("no special_check_up function")

        for widget in self.children():
            widget_path = None
            if isinstance(widget, QLineEdit):
                widget_path = widget.local_path
                widget_value = str(widget.text())

            if isinstance(widget, QDoubleSpinBox) or isinstance(
                widget, QSpinBox
            ):
                widget_path = widget.local_path
                widget_value = str(widget.value())

            if isinstance(widget, DefaultComboBox):
                widget_path = widget.local_path
                widget_value = str(widget.currentText())

            if widget_path == param_in:
                if widget_value == value_in:
                    logging.info("No need to change parameter (same value)")

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
                            logging.info(
                                "skipping convertion of string to float \n"
                            )

                    if isinstance(widget, DefaultComboBox):
                        widget.setCurrentText(str(value_in))

                    self.do_emit = True

    def update_all_pars(self, tup_lst_pars):
        logging.info(
            "(Simple Widget) \n time to update par to:" + str(tup_lst_pars)
        )
        for par_dic in tup_lst_pars[0]:
            if par_dic["name"] != "":
                self.update_param(par_dic["name"], par_dic["value"])

    def do_emit_signal(self, str_path, str_value):
        if self.do_emit:
            self.item_changed.emit(str_path, str_value, 0)

        self.do_emit = True #TODO: find out if this line is needed

    def spnbox_finished(self):
        logging.info("spnbox_finished")
        sender = self.sender()
        value = sender.value()
        str_path = str(sender.local_path)
        str_value = str(value)
        self.do_emit_signal(str_path, str_value)

    def combobox_changed(self, value):
        logging.info("combobox_changed")
        sender = self.sender()
        str_value = str(sender.item_list[value])
        str_path = str(sender.local_path)
        self.do_emit_signal(str_path, str_value)

    def line_changed(self):
        sender = self.sender()
        str_value = sender.text()
        str_path = str(sender.local_path)

        self.do_emit_signal(str_path, str_value)

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")


class ProgBarBox(QProgressDialog):
    def __init__(self, max_val=100, min_val=0, text="Working", parent = None):
        logging.info("ProgBarBox __init__")

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
        logging.info("ProgBarBox ended")
        self.close()


def build_template(str_path_in):
    logging.info("time to build template from:" + str(str_path_in))

    found_a_digit = False
    for pos, single_char in enumerate(str_path_in):
        if single_char in "0123456789":
            last_digit_pos = pos
            found_a_digit = True

    if found_a_digit:
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

    else:
        return None, 0


def get_lst_par_from_str(str_in):
    lst_com = str_in.split(" ")
    lst_pair = []
    for comm in lst_com:
        pair = comm.split("=")
        if len(pair) == 2:
            lst_pair.append(pair)

    return lst_pair


class RootWidg(QWidget):
    def __init__(self, parent = None):
        super(RootWidg, self).__init__(parent)
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        big_label = QLabel("root:")
        big_label.setFont(
            QFont("Courier", font_point_size + 3, QFont.Bold)
        )
        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(
            QLabel("Nothing to do here ... \npress the Import button to start")
        )
        self.setLayout(self.main_vbox)

    def reset_pars(self):
        logging.info("reset_pars(root) ... dummy")

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")

    def update_all_pars(self, tup_lst_pars):
        logging.info("update_all_pars(root)" + str(tup_lst_pars) + "... dummy")

    def update_param(self, str_path, str_value):
        logging.info(
            "update_param(root)" + str(str_path) +
            ", " + str(str_value) + "... dummy"
        )


class ImportWidget(QWidget):
    '''
        This widget behaves differently from most of the other  << simple >>
        parameter widgets, every time the user changes a parameter DUI should
        refresh all parameter since there are some parameter that exclude
        others
    '''
    all_items_changed = Signal(list)
    def __init__(self, parent = None):
        super(ImportWidget, self).__init__(parent)
        self.do_emit = True
        self.dir_selected = None
        self.nexus_type = False
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        self.state_label = QLabel("   ...")
        self.state_label.setFont(
            QFont("Courier", font_point_size + 1, QFont.Bold)
        )
        self.imp_txt = QLineEdit()
        self.extra_label = QLabel("   ...")
        self.extra_label.setFont(
            QFont("Courier", font_point_size + 1, QFont.Bold)
        )
        self.imp_extra_txt = QLineEdit()
        self.open_butt = QPushButton("\n  Open images  \n")

        self.check_rot_axs = QCheckBox("Invert rotation axis")

        #TODO discus how to fix import for ED
        #TODO before removing the next line entirely
        self.check_dist = QCheckBox("Set distance = 2193")

        self.imp_txt.textChanged.connect(self.line_changed)
        self.imp_extra_txt.textChanged.connect(self.line_changed)
        self.open_butt.clicked.connect(self.open_dir_widget)
        self.check_rot_axs.stateChanged.connect(self.rot_axs_changed)

        #TODO discus how to fix import for ED
        #TODO before removing the next line entirely
        self.check_dist.stateChanged.connect(self.dist_changed)


        self.check_shadow = QCheckBox("Set dynamic shadowing")
        self.check_shadow.stateChanged.connect(self.shadow_changed)

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(self.state_label)
        self.main_vbox.addWidget(self.imp_txt)
        self.main_vbox.addWidget(self.open_butt)

        self.main_vbox.addStretch()

        self.small_hbox = QHBoxLayout()
        self.small_hbox.addWidget(self.check_rot_axs)

        self.small_hbox.addWidget(self.check_dist)

        self.small_hbox.addWidget(self.check_shadow)

        self.main_vbox.addLayout(self.small_hbox)

        self.main_vbox.addWidget(self.imp_extra_txt)

        self.main_vbox.addStretch()
        self.setLayout(self.main_vbox)

    def set_selection(self, str_select, isdir):
        if str_select != "":
            self.dir_selected = isdir
            if self.dir_selected:
                self.imp_txt.setText(str_select)

            else:
                if str_select[-4:]  == ".nxs" or str_select[-9:] == "master.h5" :
                    self.nexus_type = True
                    file_path_str = str_select

                else:
                    self.nexus_type = False
                    file_path_str = build_template(str_select)[0]

                self.imp_txt.setText(file_path_str)

            self.line_changed()

        else:
            print("no selection ( canceled? )")
            logging.info("no selection ( canceled? )")

    def open_dir_widget(self):

        data_init = ini_data()
        run_local = data_init.get_if_local()

        if run_local:
            tmp_off = '''
            self.open_widget = LocalFileBrowser(self)
            self.open_widget.resize(self.open_widget.size() * 2)
            self.open_widget.file_or_dir_selected.connect(self.set_selection)
            '''
            # TODO fix custom file browser above
            file_in_path = QFileDialog.getOpenFileName(
                parent = self, caption = "Open Image File",
                dir = "/", filter = "Files (*.*)"
            )[0]
            self.set_selection(str_select = str(file_in_path), isdir = False)

        else:
            cmd = {"nod_lst":"", "cmd_str":["dir_path"]}
            lst_req = get_req_json_dat(
                params_in = cmd, main_handler = None
            )
            dic_str = lst_req.result_out()
            init_path = dic_str[0]

            self.open_widget = FileBrowser(parent = self, path_in = init_path)
            self.open_widget.resize(self.open_widget.size() * 2)
            self.open_widget.file_or_dir_selected.connect(self.set_selection)

    def reset_pars(self):
        self.nexus_type = False
        self.imp_txt.setText("")
        self.imp_extra_txt.setText("")
        self.check_rot_axs.setChecked(False)
        self.check_dist.setChecked(False)
        self.check_shadow.setChecked(False)


    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")

    def line_changed(self):
        logging.info("line_changed")
        str_value = self.imp_txt.text()
        if self.dir_selected:
            str_path = "input.directory"
            lst_par = [[str_path, str_value]]

        else:
            if self.nexus_type == True:
                str_path = "input.experiments"
                lst_par = [[None, str_value]]

            else:
                str_path = "input.template"
                lst_par = [
                    [str_path, "\"" + str_value + "\""]
                ]

        self.state_label.setText(str_path)

        ext_par = str(self.imp_extra_txt.text())
        if len(ext_par) > 0 and not self.nexus_type :
            lst_ext_par = get_lst_par_from_str(ext_par)
            if len(lst_ext_par) > 0:
                for single_ext_par in lst_ext_par:
                    lst_par.append(single_ext_par)

        self.all_items_changed.emit([lst_par])

    def rot_axs_changed(self, stat):
        logging.info("rot_axs_changed, stat:" + str(stat))
        if int(stat) == 2:
            self.add_extra_param("invert_rotation_axis=True")

        else:
            self.remove_one_param("invert_rotation_axis")
            #self.imp_extra_txt.setText("")

    def dist_changed(self, stat):
        logging.info("dist_changed, stat:" + str(stat))
        if int(stat) == 2:
            self.add_extra_param("distance=2193")

        else:
            self.remove_one_param("distance")
            #self.imp_extra_txt.setText("")

    def shadow_changed(self, stat):
        logging.info("shadow_changed, stat:" + str(stat))
        if int(stat) == 2:
            self.add_extra_param("dynamic_shadowing=True")

        else:
            self.remove_one_param("dynamic_shadowing")
            #self.imp_extra_txt.setText("")

    def add_extra_param(self, par_str):
        ini_txt = str(self.imp_extra_txt.text())
        mid_txt = ini_txt + " " + par_str
        if mid_txt[0] == " ":
            end_txt = mid_txt[1:]

        else:
            end_txt = mid_txt

        self.imp_extra_txt.setText(end_txt)

    def remove_one_param(self, par_str):
        ini_txt = str(self.imp_extra_txt.text())
        lst_pars_ini = ini_txt.split(" ")

        lst_par_end = []
        for par in lst_pars_ini:
            if par[0:len(par_str)] != par_str:
                lst_par_end.append(par)

        end_txt = " ".join(lst_par_end)

        self.imp_extra_txt.setText(end_txt)

    def update_all_pars(self, tup_lst_pars):


        self.check_rot_axs.setChecked(False)
        self.check_dist.setChecked(False)
        self.check_shadow.setChecked(False)


        for n, par in enumerate(tup_lst_pars):
            logging.info("n=" + str(n) + " par=" + str(par))

        try:
            self.imp_extra_txt.setText("")
            self.imp_txt.setText("")
            for par_dic in tup_lst_pars[0]:
                if(
                    par_dic["name"] == "input.directory" or
                    par_dic["name"] == "input.template" or
                    par_dic["name"] == ""
                ):
                    if par_dic["name"] == "input.directory":
                        self.dir_selected = True

                    else:
                        self.dir_selected = False

                    if par_dic["name"] == "":
                        self.nexus_type = True

                    first_par_str = str(par_dic["value"])
                    if first_par_str[0] == "\"" and first_par_str[-1] == "\"":
                        first_par_str = first_par_str[1:-1]

                    self.imp_txt.setText(first_par_str)

                elif(
                    par_dic["name"] == "invert_rotation_axis" and
                    par_dic["value"] == "True"
                ):
                    self.check_rot_axs.setChecked(True)
                    #self.imp_extra_txt.setText("invert_rotation_axis=True")

                elif(
                    par_dic["name"] == "dynamic_shadowing" and
                    par_dic["value"] == "True"
                ):
                    self.check_shadow.setChecked(True)
                    #self.imp_extra_txt.setText("dynamic_shadowing=True")

                elif(
                    par_dic["name"] == "distance" and
                    par_dic["value"] == "2193"
                ):
                    self.check_dist.setChecked(True)
                    #self.imp_extra_txt.setText("distance=2193")


        except IndexError:
            logging.info(" Not copying parameters from node (Index err catch )")
            self.imp_txt.setText("")
            self.imp_extra_txt.setText("")
            self.state_label.setText("   ...")

    def update_param(self, str_path, str_value):
        logging.info(
            "update_param(ImportWidget)" +
            str(str_path) + "," + str(str_value) + "... dummy"
        )


class SplitWidget(QWidget):
    """
    This widget is the tool for separating nodes with the
    dials.split_experiments command
    """

    all_items_changed = Signal(list)

    def __init__(self, parent=None):
        super(SplitWidget, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        main_box = QVBoxLayout()

        hbox_lay_by_detector = QHBoxLayout()
        label_by_detector = QLabel("By detector")
        hbox_lay_by_detector.addWidget(label_by_detector)
        self.box_by_detector = DefaultComboBox(
            "by_detector", ["True", "False"], default_index = 1
        )
        self.box_by_detector.currentIndexChanged.connect(self.update_par_dect)
        hbox_lay_by_detector.addWidget(self.box_by_detector)
        main_box.addLayout(hbox_lay_by_detector)

        hbox_lay_by_wavelength = QHBoxLayout()
        label_by_wavelength = QLabel("By wavelength")
        hbox_lay_by_wavelength.addWidget(label_by_wavelength)
        self.box_by_wavelength = DefaultComboBox(
            "by_wavelength", ["True", "False"], default_index = 1
        )
        self.box_by_wavelength.currentIndexChanged.connect(self.update_par_wavl)
        hbox_lay_by_wavelength.addWidget(self.box_by_wavelength)
        main_box.addLayout(hbox_lay_by_wavelength)

        self.main_v_layout.addLayout(main_box)
        self.main_v_layout.addStretch()

    def reset_pars(self):
        self.do_emit = False
        self.box_by_detector.setCurrentIndex(
            self.box_by_detector.default_index
        )
        self.box_by_wavelength.setCurrentIndex(
            self.box_by_wavelength.default_index
        )
        self.pars_def = {"by_detector": "False", "by_wavelength": "False"}
        logging.info("Reset_pars(SplitWidget)")
        self.do_emit = True

    def update_all_pars(self, tup_lst_pars):
        logging.info("update_all_pars(SplitWidget)" + str(tup_lst_pars))

        #self.pars_def = {"by_detector": "False", "by_wavelength": "False"}
        for tup_par in tup_lst_pars[0]:
            if tup_par["name"] == "by_detector":
                self.pars_def["by_detector"] = tup_par["value"]
                self.box_by_detector.setCurrentText(tup_par["value"])

            if tup_par["name"] == "by_wavelength":
                self.pars_def["by_wavelength"] = tup_par["value"]
                self.box_by_wavelength.setCurrentText(tup_par["value"])

    def update_par_dect(self, value):
        logging.info("by_detector")
        sender = self.sender()
        str_value = str(sender.item_list[value])
        self.pars_def["by_detector"] = str_value
        self.update_all_2_pars()

    def update_par_wavl(self, value):
        logging.info("by_wavelength")
        sender = self.sender()
        str_value = str(sender.item_list[value])
        self.pars_def["by_wavelength"] = str_value
        self.update_all_2_pars()

    def update_all_2_pars(self):
        if self.do_emit:
            lst_2_emit = [
                [
                    ["by_detector", self.pars_def["by_detector"]],
                    ["by_wavelength", self.pars_def["by_wavelength"]]
                ]
            ]
            logging.info("lst_2_emit:" + str(lst_2_emit))
            self.all_items_changed.emit(lst_2_emit)


class MaskWidget(QWidget):
    '''
    On this widget the user can choose what shape element to add to the mask
    The elements should be drawn in the image viewer, consequently that part
    of the code is in the << img_view >> module
    '''
    all_items_changed = Signal(list)
    component_changed = Signal(str)
    def __init__(self, parent = None):
        super(MaskWidget, self).__init__(parent)
        self.do_emit = True
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        self.cmd_label = QLabel("")
        self.cmd_label.setFont(QFont(
            "Courier", font_point_size -1, QFont.Bold
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
        logging.info("toggle_funtion")
        if self.rad_but_rect_mask.isChecked():
            self.stat = "rect"

        elif self.rad_but_circ_mask.isChecked():
            self.stat = "circ"

        elif self.rad_but_poly_mask.isChecked():
            self.stat = "poly"

        else:
            self.stat = None

        self.component_changed.emit(str(self.stat))

    def update_all_pars(self, par_lst_0):
        self.comp_list = []
        for par_dic in par_lst_0[0][0:-1]:
            if par_dic["name"] != "":
                single_comp_lst = [str(par_dic["name"]), str(par_dic["value"])]
                self.comp_list.append(single_comp_lst)

        self.update_comp_label()

    def reset_pars(self):
        logging.info("\n reset_pars(MaskWidget) \n")
        self.comp_list = []
        self.update_comp_label()

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")

    def update_comp_label(self):
        label_str = ""
        for comp in self.comp_list:
            single_comp_str = str(comp[0]) + " >> " + str(comp[1])
            label_str += "\n" + single_comp_str

        self.cmd_label.setText(label_str)

    def get_new_comp(self, comp_dict):
        if comp_dict["i23_multipanel"]:
            panel_height = 213
            panel_border = 18
            panel_height_m_border = panel_height - panel_border
            x_max = 2462
            y_max = 5111

        else:
            panel_height = -1

        logging.info(" comp_dict =" + str(comp_dict))

        if comp_dict["type"] == "rect":
            if comp_dict["i23_multipanel"]:
                for p_num in range(24):
                    pan_y_ini = (p_num + 1) * panel_height - panel_border
                    if comp_dict["y_ini"] < pan_y_ini:
                        pan_ini = p_num
                        break

                pan_end = pan_ini
                for p_num in range(24, pan_ini, -1):
                    pan_y_end = (p_num) * panel_height + panel_border
                    if comp_dict["y_end"] > pan_y_end:
                        pan_end = p_num
                        break

                for p_num in range(pan_ini, pan_end + 1):
                    y_orig = panel_height * p_num
                    new_y_ini = 0
                    new_y_end = panel_height_m_border
                    if p_num == pan_ini:
                        new_y_ini = int(comp_dict["y_ini"]) - y_orig
                        if new_y_ini < 0:
                            new_y_ini = 0

                    if p_num == pan_end:
                        new_y_end = int(comp_dict["y_end"]) - y_orig
                        if new_y_end > panel_height_m_border:
                            new_y_end = panel_height_m_border

                    str_cmd_nam = "multipanel.rectangle"
                    str_cmd_param =        str(comp_dict["x_ini"])
                    str_cmd_param += "," + str(comp_dict["x_end"])
                    str_cmd_param += "," + str(new_y_ini)
                    str_cmd_param += "," + str(new_y_end)
                    str_cmd_param += "," + str(p_num)
                    inner_lst_pair = [str_cmd_nam, str_cmd_param]

                    self.comp_list.append(inner_lst_pair)

            else:
                extra_str_param = ""
                y_orig = 0

                new_y_ini = int(comp_dict["y_ini"]) - y_orig
                new_y_end = int(comp_dict["y_end"]) - y_orig

                str_cmd_nam = "untrusted.rectangle"
                str_cmd_param =        str(comp_dict["x_ini"])
                str_cmd_param += "," + str(comp_dict["x_end"])
                str_cmd_param += "," + str(new_y_ini)
                str_cmd_param += "," + str(new_y_end)
                str_cmd_param += extra_str_param
                inner_lst_pair = [str_cmd_nam, str_cmd_param]
                self.comp_list.append(inner_lst_pair)

        elif comp_dict["type"] == "circ":

            tmp_yc = float(comp_dict["y_c"])
            tmp_xc = float(comp_dict["x_c"])
            tmp_r =  float(comp_dict["r"])
            if comp_dict["i23_multipanel"]:

                if comp_dict["x_c"] > 0 and comp_dict["x_c"] < x_max:
                    logging.info("Centre INside panel(regarding X)")

                    y_min = tmp_yc - tmp_r + panel_border
                    y_max = tmp_yc + tmp_r

                    pan_ini = int(y_min / panel_height)
                    pan_end = int(y_max / panel_height) + 1

                    if pan_ini < 0:
                        pan_ini = 0

                    if pan_end < 0:
                        pan_end = 0

                    if pan_ini > 23:
                        pan_ini = 23

                    if pan_end > 24:
                        pan_end = 24

                    logging.info(
                        "pan_ini, pan_end=" + str(pan_ini) + " " + str(pan_end)
                    )

                    for panel_number in range(pan_ini, pan_end):
                        logging.info("panel_number =" + str(panel_number))
                        new_yc = int(tmp_yc - panel_number * panel_height)
                        extra_str_param = "," + str(panel_number)

                        str_cmd_nam = "multipanel.circle"
                        str_cmd_param =        str(comp_dict["x_c"])
                        str_cmd_param += "," + str(new_yc)
                        str_cmd_param += "," + str(int(tmp_r))

                        str_cmd_param += extra_str_param
                        str_cmd_param = str(str_cmd_param)
                        inner_lst_pair = [str_cmd_nam, str_cmd_param]

                        logging.info("inner_lst_pair =" + str(inner_lst_pair))

                        self.comp_list.append(inner_lst_pair)

                else:
                    logging.info("Centre OUTside panel(regarding X)")
                    dx1 = tmp_xc
                    dx2 = tmp_xc - x_max
                    for panel_number in range(24):
                        y_up_panel = panel_number * panel_height
                        y_dw_panel = (panel_number + 1) * panel_height - panel_border

                        dy1 = tmp_yc - y_up_panel
                        dy2 = tmp_yc - y_dw_panel

                        d_sqr_lst = []
                        d_sqr_lst.append(float(dx1 * dx1 + dy1 * dy1))
                        d_sqr_lst.append(float(dx1 * dx1 + dy2 * dy2))
                        d_sqr_lst.append(float(dx2 * dx2 + dy1 * dy1))
                        d_sqr_lst.append(float(dx2 * dx2 + dy2 * dy2))

                        min_dist_sqr = d_sqr_lst[0]
                        for d_sqr in d_sqr_lst[1:]:
                            if d_sqr < min_dist_sqr:
                                min_dist_sqr = d_sqr

                        if min_dist_sqr <  tmp_r * tmp_r:
                            new_yc = int(tmp_yc - panel_number * panel_height)
                            extra_str_param = "," + str(panel_number)

                            str_cmd_nam = "multipanel.circle"
                            str_cmd_param =        str(comp_dict["x_c"])
                            str_cmd_param += "," + str(new_yc)
                            str_cmd_param += "," + str(int(tmp_r))

                            str_cmd_param += extra_str_param
                            str_cmd_param = str(str_cmd_param)
                            inner_lst_pair = [str_cmd_nam, str_cmd_param]

                            logging.info("inner_lst_pair =" + str(inner_lst_pair))

                            self.comp_list.append(inner_lst_pair)

            else:
                new_yc = int(tmp_yc)
                extra_str_param = ""

                str_cmd_nam = "untrusted.circle"
                str_cmd_param =        str(comp_dict["x_c"])
                str_cmd_param += "," + str(new_yc)
                str_cmd_param += "," + str(comp_dict["r"])

                str_cmd_param += extra_str_param
                str_cmd_param = str(str_cmd_param)
                inner_lst_pair = [str_cmd_nam, str_cmd_param]

                logging.info("inner_lst_pair =" + str(inner_lst_pair))

                self.comp_list.append(inner_lst_pair)

        elif comp_dict["type"] == "poly":
            if(
                self.comp_list == [] or
                self.comp_list[-1][0] != "untrusted.polygon"
            ):
                inner_lst_pair = [
                    "untrusted.polygon",
                    str(comp_dict["x_end"]) + ","
                    + str(comp_dict["y_end"]) + ","
                ]
                self.comp_list.append(inner_lst_pair)

            elif self.comp_list[-1][0] == "untrusted.polygon":
                str_tail = str(comp_dict["x_end"]) + "," \
                         + str(comp_dict["y_end"]) + ","
                self.comp_list[-1][1] += str_tail

        self.comp_list_update()

    def build_full_list(self):
        first_list = list(self.comp_list)
        first_list.append(["output.mask", "tmp_mask.pickle"])

        full_list = [
            first_list,
            [
                ["input.mask", "tmp_mask.pickle"]
            ]
        ]
        return full_list

    def comp_list_update(self):
        new_full_list = self.build_full_list()
        self.all_items_changed.emit(new_full_list)
        self.update_comp_label()
        return new_full_list


class FindspotsSimplerParameterTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
    in the spot-finder, this widget is the first to appear once the button
    "Find Sots" is clicked
    """
    def __init__(self, parent=None, add_rad_prof = False):
        super(FindspotsSimplerParameterTab, self).__init__()
        self.do_emit = True
        self.add_rad_prof = add_rad_prof
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        xds_gain_label = QLabel("Gain")
        xds_gain_spn_bx = QDoubleSpinBox()
        xds_gain_spn_bx.local_path = "spotfinder.threshold.dispersion.gain"
        xds_gain_spn_bx.setValue(1.0)
        xds_gain_spn_bx.valueChanged.connect(self.spnbox_finished)
        xds_sigma_background_label = QLabel("Sigma background")
        xds_sigma_background_spn_bx = QDoubleSpinBox()
        xds_sigma_background_spn_bx.setValue(6.0)
        xds_sigma_background_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.sigma_background"
        )
        xds_sigma_background_spn_bx.valueChanged.connect(self.spnbox_finished)

        xds_sigma_strong_label = QLabel("Sigma strong")
        xds_sigma_strong_spn_bx = QDoubleSpinBox()
        xds_sigma_strong_spn_bx.setValue(3.0)
        xds_sigma_strong_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.sigma_strong"
        )
        xds_sigma_strong_spn_bx.valueChanged.connect(self.spnbox_finished)

        xds_global_threshold_label = QLabel("Global threshold")
        xds_global_threshold_spn_bx = QDoubleSpinBox()
        xds_global_threshold_spn_bx.setMaximum(9999.99)
        xds_global_threshold_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.global_threshold"
        )
        xds_global_threshold_spn_bx.valueChanged.connect(self.spnbox_finished)

        self.set_d_max = QCheckBox("Set d_max=20")
        self.set_d_max.stateChanged.connect(self.set_d_max_changed)

        self.set_d_min = QCheckBox("Set d_min=2.5")
        self.set_d_min.stateChanged.connect(self.set_d_min_changed)

        if self.add_rad_prof:
            self.set_rad_pro_alg = QCheckBox("Set threshold.algorithm=radial_profile")
            self.set_rad_pro_alg.stateChanged.connect(self.set_alg_changed)

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

        self.main_v_layout.addWidget(
            QLabel("\n Electron diffraction parameters")
        )
        self.main_v_layout.addWidget(self.set_d_max)
        self.main_v_layout.addWidget(self.set_d_min)
        if self.add_rad_prof:
            self.main_v_layout.addWidget(self.set_rad_pro_alg)

        self.main_v_layout.addStretch()
        self.lst_var_widg = _get_all_direct_layout_widget_children(
            self.main_v_layout
        )

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")
        self.set_d_max.setChecked(True)
        self.set_d_min.setChecked(True)

    def set_d_max_changed(self, stat):
        if int(stat) == 2:
            logging.info("time to add << Set d_max=20 >>")
            self.do_emit_signal(
                "spotfinder.filter.d_max", "20"
            )

        else:
            logging.info("time to remove << Set d_max=20 >>")
            self.do_emit_signal(
                "spotfinder.filter.d_max", "None"
            )

    def set_d_min_changed(self, stat):
        if int(stat) == 2:
            logging.info("time to add << Set d_min=2.5 >>")
            self.do_emit_signal(
                "spotfinder.filter.d_min", "2.5"
            )

        else:
            logging.info("time to remove << Set d_min=2.5 >>")
            self.do_emit_signal(
                "spotfinder.filter.d_min", "None"
            )

    def set_alg_changed(self, stat):
        if int(stat) == 2:
            logging.info("time to add << Set algorithm=radial_profile >>")
            self.do_emit_signal(
                "spotfinder.threshold.algorithm", "radial_profile"
            )

        else:
            logging.info("time to remove << Set algorithm=radial_profile >>")
            self.do_emit_signal(
                "spotfinder.threshold.algorithm", "dispersion_extended"
            )

        #time to add: "spotfinder.threshold.algorithm=radial_profile"
        #default = dispersion_extended

    def special_check_up(self, param_in, value_in):
        if(
            param_in == "spotfinder.filter.d_max"
            and value_in == "20"
        ):
            self.set_d_max.setChecked(True)

        elif(
            param_in == "spotfinder.filter.d_max"
            and value_in != "20"
        ):
            self.set_d_max.setChecked(False)

        if(
            param_in == "spotfinder.filter.d_min"
            and value_in == "2.5"
        ):
            self.set_d_min.setChecked(True)

        elif(
            param_in == "spotfinder.filter.d_min"
            and value_in != "2.5"
        ):
            self.set_d_min.setChecked(False)

        if(
            param_in == "spotfinder.threshold.algorithm"
            and value_in == "radial_profile"
        ):
            self.set_rad_pro_alg.setChecked(True)

        elif(
            param_in == "spotfinder.threshold.algorithm"
            and value_in != "radial_profile"
        ):
            self.set_rad_pro_alg.setChecked(False)


class IndexSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
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
        max_cell_line = QLineEdit()
        max_cell_line.setPlaceholderText("Auto")
        max_cell_line.local_path = "indexing.max_cell"
        max_cell_line.textChanged.connect(self.line_changed)

        space_group_label = QLabel("Space group")
        space_group_line = QLineEdit()
        # Simple validator to allow only characters in H-M symbols
        regex = QRegExp("[ABCPIFR][0-9a-d\-/:nmHR]+")
        validatorHM = QRegExpValidator(regex)
        space_group_line.setValidator(validatorHM)
        space_group_line.local_path = "indexing.known_symmetry.space_group"
        space_group_line.textChanged.connect(self.line_changed)

        unit_cell_label = QLabel("Unit cell")
        unit_cell_line = QLineEdit()
        regex = QRegExp("[0-9\., ]+")
        validatorUC = QRegExpValidator(regex)
        unit_cell_line.setValidator(validatorUC)
        unit_cell_line.local_path = "indexing.known_symmetry.unit_cell"
        unit_cell_line.textChanged.connect(self.line_changed)

        self.detec_fix = QCheckBox("Set detector.fix=distance")
        self.detec_fix.stateChanged.connect(self.detec_fix_changed)

        self.main_v_layout.addLayout(hbox_method)
        qf = QFormLayout()
        qf.addRow(max_cell_label, max_cell_line)
        qf.addRow(space_group_label, space_group_line)
        qf.addRow(unit_cell_label, unit_cell_line)
        self.main_v_layout.addLayout(qf)

        self.main_v_layout.addWidget(
            QLabel("\n Electron diffraction parameter")
        )
        self.main_v_layout.addWidget(self.detec_fix)

        self.main_v_layout.addStretch()

        self.lst_var_widg = _get_all_direct_layout_widget_children(
            self.main_v_layout
        )

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")
        self.detec_fix.setChecked(True)

    def detec_fix_changed(self, stat):
        if int(stat) == 2:
            logging.info("time to add << detector.fix=distance >>")
            self.do_emit_signal(
                "refinement.parameterisation.detector.fix", "distance"
            )

        else:
            logging.info("time to remove << detector.fix=distance >>")
            self.do_emit_signal(
                "refinement.parameterisation.detector.fix", "None"
            )

    def special_check_up(self, param_in, value_in):
        if(
            param_in == "refinement.parameterisation.detector.fix"
            and value_in == "distance"
        ):
            self.detec_fix.setChecked(True)

        elif(
            param_in == "refinement.parameterisation.detector.fix"
            and value_in != "distance"
        ):
            self.detec_fix.setChecked(False)


class SsxIndexSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
    in the indexer, this widget is the first to appear once the button
    "SSX Index" is clicked
    """
    def __init__(self, phl_obj=None, parent=None):
        super(SsxIndexSimplerParamTab, self).__init__()
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
        max_cell_line = QLineEdit()
        max_cell_line.setPlaceholderText("Auto")
        max_cell_line.local_path = "indexing.max_cell"
        max_cell_line.textChanged.connect(self.line_changed)

        space_group_label = QLabel("Space group")
        space_group_line = QLineEdit()
        # Simple validator to allow only characters in H-M symbols
        regex = QRegExp("[ABCPIFR][0-9a-d\-/:nmHR]+")
        validatorHM = QRegExpValidator(regex)
        space_group_line.setValidator(validatorHM)
        space_group_line.local_path = "indexing.known_symmetry.space_group"
        space_group_line.textChanged.connect(self.line_changed)

        unit_cell_label = QLabel("Unit cell")
        unit_cell_line = QLineEdit()
        regex = QRegExp("[0-9\., ]+")
        validatorUC = QRegExpValidator(regex)
        unit_cell_line.setValidator(validatorUC)
        unit_cell_line.local_path = "indexing.known_symmetry.unit_cell"
        unit_cell_line.textChanged.connect(self.line_changed)

        self.main_v_layout.addLayout(hbox_method)
        qf = QFormLayout()
        qf.addRow(max_cell_label, max_cell_line)
        qf.addRow(space_group_label, space_group_line)
        qf.addRow(unit_cell_label, unit_cell_line)
        self.main_v_layout.addLayout(qf)

        self.main_v_layout.addStretch()

        self.lst_var_widg = _get_all_direct_layout_widget_children(
            self.main_v_layout
        )

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

        self.detec_fix = QCheckBox("Set detector.fix=distance")

        box_outlier_algorithm.currentIndexChanged.connect(
            self.combobox_changed
        )
        self.detec_fix.stateChanged.connect(self.detec_fix_changed)

        hbox_lay_outlier_algorithm.addWidget(box_outlier_algorithm)
        self.main_v_layout.addLayout(hbox_lay_outlier_algorithm)
        self.main_v_layout.addWidget(
            QLabel("\n Electron diffraction parameter")
        )
        self.main_v_layout.addWidget(self.detec_fix)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_outlier_algorithm)
        self.lst_var_widg.append(label_outlier_algorithm)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")
        self.detec_fix.setChecked(True)

    def detec_fix_changed(self, stat):
        logging.info(
            "detec_fix_changed(RefineBravaiSimplerParamTab)" + str(stat)
        )
        if int(stat) == 2:
            logging.info("time to add << detector.fix=distance >>")
            self.do_emit_signal(
                "refinement.parameterisation.detector.fix", "distance"
            )

        else:
            logging.info("time to remove << detector.fix=distance >>")
            self.do_emit_signal(
                "refinement.parameterisation.detector.fix", "None"
            )

    def special_check_up(self, param_in, value_in):
        if(
            param_in == "refinement.parameterisation.detector.fix"
            and value_in == "distance"
        ):
            self.detec_fix.setChecked(True)

        elif(
            param_in == "refinement.parameterisation.detector.fix"
            and value_in != "distance"
        ):
            self.detec_fix.setChecked(False)


class RefineSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
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

        box_scan_varying = DefaultComboBox(
            "refinement.parameterisation.scan_varying",
            ["True", "False", "Auto"], default_index=2
        )
        box_scan_varying.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_scan_varying.addWidget(box_scan_varying)
        self.main_v_layout.addLayout(hbox_lay_scan_varying)

        hbox_lay_outlier_algorithm = QHBoxLayout()
        label_outlier_algorithm = QLabel("Outlier rejection algorithm")

        hbox_lay_outlier_algorithm.addWidget(label_outlier_algorithm)
        box_outlier_algorithm = DefaultComboBox(
            "refinement.reflections.outlier.algorithm", ["null", "Auto", "mcd",
            "tukey", "sauter_poon"], default_index=1)
        box_outlier_algorithm.currentIndexChanged.connect(
            self.combobox_changed
        )

        hbox_lay_outlier_algorithm.addWidget(box_outlier_algorithm)
        self.main_v_layout.addLayout(hbox_lay_outlier_algorithm)

        self.detec_fix = QCheckBox("Set detector.fix=distance")
        self.detec_fix.stateChanged.connect(self.detec_fix_changed)
        self.main_v_layout.addWidget(
            QLabel("\n Electron diffraction parameter")
        )
        self.main_v_layout.addWidget(self.detec_fix)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_scan_varying)
        self.lst_var_widg.append(label_scan_varying)

        self.lst_var_widg.append(box_outlier_algorithm)
        self.lst_var_widg.append(label_outlier_algorithm)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")
        self.detec_fix.setChecked(True)

    def detec_fix_changed(self, stat):
        logging.info("detec_fix_changed(RefineSimplerParamTab)" + str(stat))
        if int(stat) == 2:
            logging.info("time to add << detector.fix=distance >>")
            self.do_emit_signal(
                "refinement.parameterisation.detector.fix", "distance"
            )

        else:
            logging.info("time to remove << detector.fix=distance >>")
            self.do_emit_signal(
                "refinement.parameterisation.detector.fix", "None"
            )

    def special_check_up(self, param_in, value_in):
        if(
            param_in == "refinement.parameterisation.detector.fix"
            and value_in == "distance"
        ):
            self.detec_fix.setChecked(True)

        elif(
            param_in == "refinement.parameterisation.detector.fix"
            and value_in != "distance"
        ):
            self.detec_fix.setChecked(False)


class  IntegrateSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
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

        hbox_d_min = QHBoxLayout()
        label_d_min = QLabel("High resolution limit")
        hbox_d_min.addWidget(label_d_min)
        d_min_line = QLineEdit()
        d_min_line.setPlaceholderText("None")
        d_min_line.local_path = "prediction.d_min"
        d_min_line.textChanged.connect(self.line_changed)
        hbox_d_min.addWidget(d_min_line)
        self.main_v_layout.addLayout(hbox_d_min)

        ##############################################################################
        hbox_d_max = QHBoxLayout()
        d_max_label = QLabel("Low resolution limit")
        hbox_d_max.addWidget(d_max_label)
        d_max_line = QLineEdit()
        d_max_line.setPlaceholderText("None")
        d_max_line.local_path = "prediction.d_max"
        d_max_line.textChanged.connect(self.line_changed)
        hbox_d_max.addWidget(d_max_line)
        self.main_v_layout.addLayout(hbox_d_max)
        ##############################################################################

        hbox_lay_algorithm_53 = QHBoxLayout()
        label_algorithm_53 = QLabel("Background algorithm")
        hbox_lay_algorithm_53.addWidget(label_algorithm_53)
        box_algorithm_53 = DefaultComboBox("integration.background.algorithm",
            ["Auto", "glm", "gmodel", "null", "simple"], default_index=0)
        box_algorithm_53.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_algorithm_53.addWidget(box_algorithm_53)
        self.main_v_layout.addLayout(hbox_lay_algorithm_53)

        self.main_v_layout.addStretch()
        self.lst_var_widg = _get_all_direct_layout_widget_children(
            self.main_v_layout
        )

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class  SsxIntegrateSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
    in the integrate algorithm, this widget is the first to appear once the
    button "Integrate" is clicked
    """
    def __init__(self, parent=None):
        super(SsxIntegrateSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        hbox_d_min = QHBoxLayout()
        label_d_min = QLabel("High resolution limit")
        hbox_d_min.addWidget(label_d_min)
        d_min_line = QLineEdit()
        d_min_line.setPlaceholderText("None")
        d_min_line.local_path = "prediction.d_min"
        d_min_line.textChanged.connect(self.line_changed)
        hbox_d_min.addWidget(d_min_line)
        self.main_v_layout.addLayout(hbox_d_min)

        ##############################################################################
        hbox_d_max = QHBoxLayout()
        d_max_label = QLabel("Low resolution limit")
        hbox_d_max.addWidget(d_max_label)
        d_max_line = QLineEdit()
        d_max_line.setPlaceholderText("None")
        d_max_line.local_path = "prediction.d_max"
        d_max_line.textChanged.connect(self.line_changed)
        hbox_d_max.addWidget(d_max_line)
        self.main_v_layout.addLayout(hbox_d_max)
        ##############################################################################

        hbox_lay_algorithm_53 = QHBoxLayout()
        label_algorithm_53 = QLabel("Background algorithm")
        hbox_lay_algorithm_53.addWidget(label_algorithm_53)
        box_algorithm_53 = DefaultComboBox("integration.background.algorithm",
            ["Auto", "glm", "gmodel", "null", "simple"], default_index=0)
        box_algorithm_53.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_algorithm_53.addWidget(box_algorithm_53)
        self.main_v_layout.addLayout(hbox_lay_algorithm_53)

        self.main_v_layout.addStretch()
        self.lst_var_widg = _get_all_direct_layout_widget_children(
            self.main_v_layout
        )

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class SymmetrySimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
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

        d_min_line = QLineEdit()
        d_min_line.setPlaceholderText("Auto")
        d_min_line.local_path = "d_min"
        d_min_line.textChanged.connect(self.line_changed)
        hbox_d_min.addWidget(d_min_line)

        self.main_v_layout.addLayout(hbox_d_min)
        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(d_min_line)
        self.lst_var_widg.append(label_d_min)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class ScaleSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tuning the simpler and most common parameters
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

        hbox_d_min = QHBoxLayout()
        d_min_label = QLabel("High resolution limit")
        hbox_d_min.addWidget(d_min_label)
        d_min_line = QLineEdit()
        d_min_line.setPlaceholderText("None")
        d_min_line.local_path = "cut_data.d_min"
        d_min_line.textChanged.connect(self.line_changed)
        hbox_d_min.addWidget(d_min_line)
        self.main_v_layout.addLayout(hbox_d_min)

        ##############################################################################
        hbox_d_max = QHBoxLayout()
        d_max_label = QLabel("Low resolution limit")
        hbox_d_max.addWidget(d_max_label)
        d_max_line = QLineEdit()
        d_max_line.setPlaceholderText("None")
        d_max_line.local_path = "cut_data.d_max"
        d_max_line.textChanged.connect(self.line_changed)
        hbox_d_max.addWidget(d_max_line)
        self.main_v_layout.addLayout(hbox_d_max)
        ##############################################################################

        hbox_lay_mod = QHBoxLayout()
        label_mod = QLabel("Model")
        hbox_lay_mod.addWidget(label_mod)
        box_mod = DefaultComboBox("model", ["physical", "array", "KB"])
        box_mod.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_mod.addWidget(box_mod)
        self.main_v_layout.addLayout(hbox_lay_mod)


        hbox_lay_wgh_opt_err = QHBoxLayout()
        label_wgh_opt_err = QLabel("Error optimisation model")
        hbox_lay_wgh_opt_err.addWidget(label_wgh_opt_err)
        box_wgh_opt_err = DefaultComboBox("weighting.error_model.error_model",
            ["basic", "None"])
        box_wgh_opt_err.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_wgh_opt_err.addWidget(box_wgh_opt_err)
        self.main_v_layout.addLayout(hbox_lay_wgh_opt_err)


        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_mod)
        self.lst_var_widg.append(label_mod)
        self.lst_var_widg.append(box_wgh_opt_err)
        self.lst_var_widg.append(label_wgh_opt_err)
        self.lst_var_widg.append(d_min_line)
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
        self.main_v_layout.addWidget(QLabel("Reference from experiment"))

        beam_line = QLineEdit()
        beam_line.setPlaceholderText("None")
        beam_line.local_path = "reference_from_experiment.beam"
        beam_line.textChanged.connect(self.line_changed)

        hbox_beam = QHBoxLayout()
        label_beam = QLabel("  -  beam")
        hbox_beam.addWidget(label_beam)
        hbox_beam.addWidget(beam_line)

        detec_line = QLineEdit()
        detec_line.setPlaceholderText("None")
        detec_line.local_path = "reference_from_experiment.detector"
        detec_line.textChanged.connect(self.line_changed)

        hbox_detec = QHBoxLayout()
        label_detec = QLabel("  -  detector")
        hbox_detec.addWidget(label_detec)
        hbox_detec.addWidget(detec_line)

        self.main_v_layout.addLayout(hbox_beam)
        self.main_v_layout.addLayout(hbox_detec)
        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(label_beam)
        self.lst_var_widg.append(beam_line)
        self.lst_var_widg.append(label_detec)
        self.lst_var_widg.append(detec_line)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class OptionalWidget(SimpleParamTab):
    all_items_changed = Signal(list)
    main_command_changed = Signal(str)
    def __init__(self, parent = None, cmd_lst = None):
        super(OptionalWidget, self).__init__(parent)

        self.com_imp_txt = QLineEdit()
        completer = QCompleter(cmd_lst, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.com_imp_txt.setCompleter(completer)

        self.right_vbox = QVBoxLayout()
        self.right_vbox.addWidget(QLabel("Command:   dials...   ?"))
        self.cmd_menu = DefaultComboBox(None, cmd_lst)
        self.right_vbox.addWidget(self.cmd_menu)

        self.top_hbox = QHBoxLayout()
        self.top_hbox.addLayout(self.right_vbox)
        self.top_hbox.addWidget(self.com_imp_txt)

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addLayout(self.top_hbox)
        self.main_vbox.addWidget(QLabel("Parameter(s) ... ?"))
        self.par_imp_txt = QLineEdit()
        self.main_vbox.addWidget(self.par_imp_txt)
        self.setLayout(self.main_vbox)

        self.cmd_menu.currentIndexChanged.connect(self.cmd_menu_changed)
        self.com_imp_txt.textChanged.connect(self.command_line_changed)
        self.par_imp_txt.textChanged.connect(self.param_line_changed)

    def reset_pars(self):
        logging.info("reset_pars(OptionalWidget)")
        self.cmd_menu.setCurrentIndex(0)
        self.com_imp_txt.setText("")
        self.par_imp_txt.setText("")

    def update_all_pars(self, tup_lst_pars):
        logging.info(
            "update_all_pars(OptionalWidget)" + str(tup_lst_pars)
        )

    def param_line_changed(self):
        str_full_line = self.par_imp_txt.text()
        outer_lst_par = str_full_line.split(" ")
        lst_par = []
        for inner_par in outer_lst_par:
            lst_par.append(inner_par.split("="))

        self.all_items_changed.emit([lst_par])

    def cmd_menu_changed(self, value):
        logging.info("cmd_menu_changed")
        sender = self.sender()
        str_value = str(sender.item_list[value])
        self.com_imp_txt.setText(str_value)

    def command_line_changed(self):
        logging.info("command_line_changed(OptionalWidget)")
        str_new_line = str(self.com_imp_txt.text())
        self.main_command_changed.emit(str_new_line)


class ExportWidget(QWidget):
    '''
        This widget is a simplified version of ImportWidget since
        there is no need to interact with a remote << FileBrowser >>
    '''
    all_items_changed = Signal(list)
    find_scaled_before = Signal()
    def __init__(self, parent = None):
        super(ExportWidget, self).__init__(parent)
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        state_label = QLabel("(exported) hklout output name:")
        state_label.setFont(
            QFont("Courier", font_point_size + 1, QFont.Bold)
        )
        self.exp_txt = QLineEdit()
        self.exp_txt.textChanged.connect(self.line_changed)

        extra_label = QLabel("extra parameter:")
        extra_label.setFont(
            QFont("Courier", font_point_size + 1, QFont.Bold)
        )
        self.imp_extra_txt = QLineEdit()
        self.imp_extra_txt.textChanged.connect(self.line_changed)


        self.downl_but = QPushButton("Download/save hklout file")
        self.downl_but.clicked.connect(self.download_hklout)
        self.progress_label = QLabel("...")

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(state_label)
        self.main_vbox.addWidget(self.exp_txt)
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(extra_label)
        self.main_vbox.addWidget(self.imp_extra_txt)
        self.main_vbox.addStretch()
        self.main_vbox.addWidget(self.downl_but)
        self.main_vbox.addWidget(self.progress_label)
        self.main_vbox.addStretch()
        self.setLayout(self.main_vbox)

    def set_parent(self, parent = None):
        self.my_handler = parent.runner_handler
        #self.my_handler = None

    def line_changed(self):
        print("line_changed")
        ext_par = str(self.imp_extra_txt.text())
        print("ext_par =", ext_par)
        if len(ext_par) > 0:
            lst_ext_par = get_lst_par_from_str(ext_par)

            print("lst_ext_par =", lst_ext_par)

            data_format ="mtz"
            if len(lst_ext_par) > 0:
                lst_par = []
                for single_ext_par in lst_ext_par:
                    lst_par.append(single_ext_par)
                    if single_ext_par[0] == "format":
                        data_format = single_ext_par[1]

        str_value = self.exp_txt.text()
        #format = *mtz sadabs nxs mmcif mosflm xds xds_ascii json shelx pets
        if data_format == "mtz":
            if str_value[-3:] != "mtz":
                str_value = str_value + ".mtz"

            lst_par.append(["mtz.hklout", str_value])

        elif data_format == "shelx":
            if str_value[-3:] != "hkl":
                str_value = str_value + ".hkl"

            lst_par.append(["shelx.hklout", str_value])

        print("lst_par = ", lst_par)

        self.all_items_changed.emit([lst_par])

    def reset_pars(self):
        self.find_scaled_before.emit()

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")

    def is_scale_parent1(self, scale_in_parents):
        # This function should be called from main QObject after reset_pars

        self.imp_extra_txt.setText("format=mtz")
        if scale_in_parents:
            self.exp_txt.setText("scaled.mtz")
            #self.exp_txt.setText("scaled")

        else:
            self.exp_txt.setText("integrated.mtz")
            #self.exp_txt.setText("integrated")

        self.line_changed()

    def update_all_pars(self, tup_lst_pars):
        print("update_all_pars(ExportWidget) =  " + str(tup_lst_pars))

        ext_par_full_text = ""
        for tupl_param in tup_lst_pars[0]:
            try:
                if tupl_param["name"][-6:] == 'hklout':
                    inp_val1 = str(tupl_param["value"])
                    self.exp_txt.setText(inp_val1)

                else:
                    inp_par_extra = str(tupl_param["name"])
                    inp_val_extra = str(tupl_param["value"])
                    ext_par = inp_par_extra + "=" + inp_val_extra

                    ext_par_full_text += " " + ext_par

            except IndexError:
                print(" Not copying parameters from node (Index err catch )")
                self.exp_txt.setText("")
                self.imp_extra_txt.setText("")

            self.imp_extra_txt.setText(ext_par_full_text)


    def set_download_stat(self, do_enable = False, nod_num = None):
        self.setEnabled(True)
        self.exp_txt.setEnabled(not do_enable)
        self.imp_extra_txt.setEnabled(not do_enable)
        self.downl_but.setEnabled(do_enable)
        self.cur_nod_num = nod_num

    def download_hklout(self):
        ini_file = os.getcwd() + os.sep + self.exp_txt.text()
        fileResul = QFileDialog.getSaveFileName(
            self, "Download MTZ File", ini_file, "Intensity  (*.mtz)"
        )
        self.file_name = fileResul[0]
        if self.file_name != '':
            self.progress_label.setText("Requesting mtz file ...")

            data_init = ini_data()
            uni_url = data_init.get_url()
            cmd = {"nod_lst":[self.cur_nod_num], "cmd_str":["get_mtz"]}
            self.dowl_thrd = Mtz_Data_Request(cmd, self.my_handler)
            self.dowl_thrd.update_progress.connect(self.show_new_progress)
            self.dowl_thrd.done_download.connect(self.save_mtz_on_disc)
            self.dowl_thrd.finished.connect(self.restore_p_label)
            self.dowl_thrd.start()

        else:
            logging.info("Canceled Operation")

    def show_new_progress(self, new_prog):
        self.progress_label.setText(
            str("Downloading: " + str(new_prog) + " %")
        )

    def save_mtz_on_disc(self, mtz_info):
        self.progress_label.setText("...")
        file_out = open(self.file_name, "wb")
        #try:
        file_out.write(mtz_info)
        #file_out.write(bytes(mtz_info))
        #except TypeError:
        #    logging.info("Type Err catch (save_mtz_on_disc)")
        #    #file_out.write(bytes(mtz_info))

        file_out.close()

    def restore_p_label(self):
        self.progress_label.setText("...")
        self.dowl_thrd.exit()
        logging.info("Done Download")


class MergeWidget(QWidget):
    '''
        This widget is another simplified version of ImportWidget since
        there is no need neither to interact with a remote << FileBrowser >>
    '''
    all_items_changed = Signal(list)
    find_scaled_before = Signal()
    def __init__(self, parent = None):
        super(MergeWidget, self).__init__(parent)
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        state_label = QLabel("(merged) mtz output name:")
        state_label.setFont(
            QFont("Courier", font_point_size + 1, QFont.Bold)
        )

        self.exp_txt = QLineEdit()
        self.exp_txt.textChanged.connect(self.line_changed)
        self.downl_but = QPushButton("Download/save .mtz file")
        self.downl_but.clicked.connect(self.download_hklout)
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

    def set_parent(self, parent = None):
        self.my_handler = parent.runner_handler
        #self.my_handler = None

    def line_changed(self):
        logging.info("\n line_changed")
        str_value = self.exp_txt.text()
        if str_value[-3:] != "mtz":
            str_value = str_value + ".mtz"
        self.all_items_changed.emit([[["output.mtz", str_value]]])

    def reset_pars(self):
        self.find_scaled_before.emit()

    def set_ed_pars(self):
        logging.info("set_ed_pars(SimpleParamTab)")

    def is_scale_parent2(self, scale_in_parents):
        #TODO the logics of next if block should go before
        #TODO desiding if << dials.merge >> is allowed yet:
        '''
        if scale_in_parents:
            self.exp_txt.setText("merged.mtz")

        else:
            self.exp_txt.setText("integrated.mtz")
        '''

        self.exp_txt.setText("merged.mtz")
        self.line_changed()

    def update_all_pars(self, tup_lst_pars):
        try:
            inp_val = str(tup_lst_pars[0][0]["value"])
            self.exp_txt.setText(inp_val)

        except IndexError:
            logging.info(" Not copying parameters from node (Index err catch )")
            self.exp_txt.setText("")

    def set_download_stat(self, do_enable = False, nod_num = None):
        self.setEnabled(True)
        self.exp_txt.setEnabled(not do_enable)
        self.downl_but.setEnabled(do_enable)
        self.cur_nod_num = nod_num

    def download_hklout(self):
        ini_file = os.getcwd() + os.sep + self.exp_txt.text()
        fileResul = QFileDialog.getSaveFileName(
            self, "Download MTZ File", ini_file, "Intensity  (*.mtz)"
        )
        self.file_name = fileResul[0]
        if self.file_name != '':
            self.progress_label.setText("Requesting mtz file ...")

            data_init = ini_data()
            uni_url = data_init.get_url()
            cmd = {"nod_lst":[self.cur_nod_num], "cmd_str":["get_mtz"]}
            self.dowl_thrd = Mtz_Data_Request(cmd, self.my_handler)
            self.dowl_thrd.update_progress.connect(self.show_new_progress)
            self.dowl_thrd.done_download.connect(self.save_mtz_on_disc)
            self.dowl_thrd.finished.connect(self.restore_p_label)
            self.dowl_thrd.start()

        else:
            logging.info("Canceled Operation")

    def show_new_progress(self, new_prog):
        self.progress_label.setText(
            str("Downloading: " + str(new_prog) + " %")
        )

    def save_mtz_on_disc(self, mtz_info):
        self.progress_label.setText("...")
        file_out = open(self.file_name, "wb")
        try:
            file_out.write(mtz_info)

        except TypeError:
            logging.info("Type Err catch (save_mtz_on_disc)")
            #file_out.write(bytes(mtz_info))

        file_out.close()

    def restore_p_label(self):
        self.progress_label.setText("...")
        self.dowl_thrd.exit()
        logging.info("Done Download")

#####################################################################################################

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
