"""
DUI2's client's side GUI utilities

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

import numpy as np

from dui2.shared_modules import format_utils

def check_if_predict_n_report(str_key):
    should_skip = True
    if str_key in [
        "refine_bravais_settings",
        "generate_mask",
        "apply_mask",
        "export",
    ]:
        return False

    else:
        return True

widgets_defs = {
    "root" : {
        "tooltip"       : "root node ... Not supposed to run any code",
        "icon"          : "resources/root.png",
        "main_cmd"      :["# root node"],
        "nxt_widg_lst"  :["import"]
    },
    "import" : {
        "tooltip"       : "dials.import ...",
        "icon"          : "resources/import.png",
        "main_cmd"      :["dials.import"],
        "nxt_widg_lst"  :["find_spots", "apply_mask", "split_experiments"]
    },
    "apply_mask" : {
        "tooltip"       : "dials.generate_mask && dials.apply_mask ...",
        "icon"          : "resources/mask.png",
        "main_cmd"      :['dials.generate_mask','dials.apply_mask'],
        "nxt_widg_lst"  :["find_spots"]
    },
    "find_spots" : {
        "tooltip"       : "dials.find_spots ...",
        "icon"          : "resources/find_spots.png",
        "main_cmd"      :["dials.find_spots"],
        "nxt_widg_lst"  :[
            "index", "filter_reflections", "combine_experiments",
            "ssx_index", "split_experiments", "optional"
        ]
    },
    "filter_reflections" : {
        "tooltip"       : "dials.filter_reflections ...",
        "icon"          : "resources/filter_reflections.png",
        "main_cmd"      :["dials.filter_reflections"],
        "nxt_widg_lst"  :[
            "index", "combine_experiments", "ssx_index", "optional"
        ]
    },
    "index" : {
        "tooltip"       : "dials.index ...",
        "icon"          : "resources/index.png",
        "main_cmd"      :["dials.index"],
        "nxt_widg_lst"  :[
            "refine_bravais_settings",
            "refine",
            "combine_experiments",
            "split_experiments",
            "optional"
        ]
    },
    "ssx_index" : {
        "tooltip"       : "dials.ssx_index ...",
        "icon"          : "resources/ssx_index.png",
        "main_cmd"      :["dials.ssx_index"],
        "nxt_widg_lst"  :[
            "ssx_integrate",
            "optional"
        ]
    },
    "refine_bravais_settings" : {
        "tooltip"       : "dials.refine_bravais_settings ...",
        "icon"          : "resources/refine_bv_set.png",
        "main_cmd"      :["dials.refine_bravais_settings"],
        "nxt_widg_lst"  :["reindex"]
    },
    "reindex" : {
        "tooltip"       : "dials.reindex ...",
        "icon"          : "resources/reindex.png",
        "main_cmd"      :["dials.reindex"],
        "nxt_widg_lst"  :[
            "refine", "integrate", "combine_experiments", "optional"
        ]
    },
    "refine" : {
        "tooltip"       : "dials.refine ...",
        "icon"          : "resources/refine.png",
        "main_cmd"      :["dials.refine"],
        "nxt_widg_lst"  :[
            "integrate",
            "refine_bravais_settings",
            "combine_experiments",
            "split_experiments",
            "optional"
        ]
    },
    "integrate" : {
        "tooltip"       : "dials.integrate ...",
        "icon"          : "resources/integrate.png",
        "main_cmd"      :["dials.integrate"],
        "nxt_widg_lst"  :[
            "symmetry", "scale", "cosym",
            "export", "combine_experiments",
            "split_experiments", "optional"
        ]
    },
    "ssx_integrate" : {
        "tooltip"       : "dials.ssx_integrate ...",
        "icon"          : "resources/ssx_integrate.png",
        "main_cmd"      :["dials.ssx_integrate"],
        "nxt_widg_lst"  :[
            "symmetry", "scale", "cosym", "export", "optional"
        ]
    },
    "symmetry" : {
        "tooltip"       : "dials.symmetry ...",
        "icon"          : "resources/symmetry.png",
        "main_cmd"      :["dials.symmetry"],
        "nxt_widg_lst"  :[
            "scale", "export", "merge", "combine_experiments",
            "split_experiments", "optional"
        ]
    },
    "cosym" : {
        "tooltip"       : "dials.cosym ...",
        "icon"          : "resources/cosym.png",
        "main_cmd"      :["dials.cosym"],
        "nxt_widg_lst"  :[
            "scale", "export", "merge", "combine_experiments",
            "split_experiments", "optional"
        ]
    },
    "scale" : {
        "tooltip"       : "dials.scale ...",
        "icon"          : "resources/scale.png",
        "main_cmd"      :["dials.scale"],
        "nxt_widg_lst"  :[
            "symmetry", "cosym", "merge", "export", "combine_experiments",
            "split_experiments", "optional"
        ]
    },
    "export" : {
        "tooltip"       : "dials.export ...",
        "icon"          : "resources/export.png",
        "main_cmd"      :["dials.export"],
        "nxt_widg_lst"  :[]
    },
    "merge" : {
        "tooltip"       : "dials.merge ...",
        "icon"          : "resources/merge.png",
        "main_cmd"      :["dials.merge"],
        "nxt_widg_lst"  :[]
    },
    "combine_experiments"   : {
        "tooltip"           : "dials.combine_experiments ...",
        "icon"              : "resources/combine.png",
        "main_cmd"          :["dials.combine_experiments"],
        "nxt_widg_lst"      :[
            "index", "refine", "integrate", "export",
            "merge", "split_experiments", "optional"
        ]
    },
    "split_experiments"   : {
        "tooltip"           : "dials.split_experiments ...",
        "icon"              : "resources/split.png",
        "main_cmd"          :["dials.split_experiments"],
        "nxt_widg_lst"      :[
            "find_spots", "apply_mask", "refine", "integrate", "export",
            "merge", "combine_experiments","optional"
        ]
    },
    "optional" : {
        "tooltip"       : "choose from a list",
        "icon"          : "resources/optional.png",
        "main_cmd"      :["dials.optional"],
        "nxt_widg_lst"  :[
            "find_spots", "index", "refine",
            "integrate", "export", "merge",
        ]
    }
}


def get_widget_def_dict(in_dic, ui_path):
    out_dic = {}
    logging.info("Loading Icons")
    for key, value in in_dic.items():
        new_inner_dict = dict(value)
        nxt_ico = QIcon()
        icon_path = ui_path + os.sep + new_inner_dict["icon"]
        nxt_ico.addFile(icon_path, mode = QIcon.Normal)
        new_inner_dict["icon"] = nxt_ico
        out_dic[str(key)] = dict(new_inner_dict)

    return out_dic


class find_scale_cmd(object):
    '''
    This class works as a function that internally navigates with
    recursive calls to find out if there is a << dials.scale >> command
    '''
    def __init__(self, nod_lst, parent_num_lst):
        self.nod_lst = nod_lst
        self.found_scale = False
        for nod_num in parent_num_lst:
            self.get_parent_num(nod_num)

    def get_parent_num(self, nod_num):
        if self.nod_lst[nod_num]["cmd2show"][0] == "dials.scale":
            self.found_scale = True

        for new_nod_num in self.nod_lst[nod_num]["parent_node_lst"]:
            self.get_parent_num(new_nod_num)

    def founded_scale(self):
        return self.found_scale


class find_next_cmd(object):
    '''
    This class works as a function that internally navigates with
    recursive calls to find the possible command to run next
    '''
    def __init__(
        self, nod_lst_in, parent_nod_num_lst,
        str_key, param_widgets, opt_cmd_lst
    ):
        self.nod_lst = nod_lst_in
        self.remove_combine = False
        self.remove_split = False
        if str_key == "combine_experiments":
            parent_num = parent_nod_num_lst[0]
            str_key = self.nod_lst[parent_num]["cmd2show"][0][6:]
            self.remove_combine = True

        elif str_key == "split_experiments":
            parent_num = parent_nod_num_lst[0]
            str_key = self.nod_lst[parent_num]["cmd2show"][0][6:]
            self.remove_split = True

        try:
            self.default_list = param_widgets[str_key]["nxt_widg_lst"]

        except KeyError:
            self.default_list = ["optional"]

        self.par_cmd_lst = []
        for nod_num in parent_nod_num_lst:
            self.get_parent_num(nod_num)

    def get_parent_num(self, nod_num):
        self.par_cmd_lst.append(self.nod_lst[nod_num]["cmd2show"][0][6:])
        for new_nod_num in self.nod_lst[nod_num]["parent_node_lst"]:
            self.get_parent_num(new_nod_num)

    def get_nxt_cmd(self):
        fin_cmd_lst = []
        for cmd in self.default_list:
            if cmd not in self.par_cmd_lst or cmd == "refine":
                fin_cmd_lst.append(cmd)

        if self.remove_combine:
            try:
                fin_cmd_lst.remove("combine_experiments")

            except ValueError:
                return ["optional"]

        elif self.remove_split:
            try:
                fin_cmd_lst.remove("split_experiments")

            except ValueError:
                return ["optional"]

        still_2_prove = '''
        if fin_cmd_lst == []:
            fin_cmd_lst = ["optional"]
        '''

        return fin_cmd_lst


class MyQComboBox(QComboBox):
    def __init__(self, parent=None):
        super(MyQComboBox, self).__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)

    def wheelEvent(self, event):
        logging.info(
            "event: " + str(event) + " not suposed to change with wheel event"
        )
        return


class AdvancedParameters(QWidget):
    item_changed = Signal(str, str)
    def __init__(self, parent = None):
        super(AdvancedParameters, self).__init__(parent)
        self.do_emit = True
        self.main_vbox = QVBoxLayout()
        sys_font = QFont()
        self.font_point_size = sys_font.pointSize()
        self.setLayout(self.main_vbox)

    def set_scroll_parent(self, scroll_parent):
        self.my_scroll_area = scroll_parent

    def build_pars(self, lst_phil_obj, h_box_search):
        h_box_search.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_changed)
        h_box_search.addWidget(self.search_input)

        self.fnd_nxt = QPushButton("Find next")
        self.fnd_nxt.clicked.connect(self.find_next_search_click)
        h_box_search.addWidget(self.fnd_nxt)

        self.lst_par_line = lst_phil_obj
        logging.info("Hi from build_pars")
        self.norm_labl_font = QFont(
            "Courier", self.font_point_size, QFont.Bold
        )
        for data_info in self.lst_par_line:
            label_str = "    " * data_info["indent"]
            label_str += data_info["name"]
            new_label = QLabel(label_str)
            new_label.setAutoFillBackground(True)
            new_label.setFont(self.norm_labl_font)
            data_info["Label"] = new_label
            new_hbox = QHBoxLayout()
            try:
                default = data_info["default"]

            except KeyError:
                default = None

            data_info["widget"] = None
            if data_info["type"] == "scope":
                new_label.my_style = "color: rgba(105, 105, 105, 255)"
                new_label.setStyleSheet(new_label.my_style)
                new_hbox.addWidget(new_label)

            elif(
                (data_info["type"] == "bool"
                 or
                 data_info["type"] == "choice")
            ):
                new_label.my_style = "color: rgba(0, 0, 0, 255)"
                new_label.setStyleSheet(new_label.my_style)
                new_hbox.addWidget(new_label)

                new_combo = MyQComboBox()
                found_none = False
                for opt_itm in data_info["opt_lst"]:
                    new_combo.addItem(opt_itm)
                    if opt_itm == "None" or opt_itm == "none":
                        found_none = True

                if found_none is False:
                    new_combo.addItem("None")

                try:
                    new_combo.setCurrentIndex(default)

                except TypeError:
                    new_combo.setCurrentIndex(0)

                new_combo.local_path = data_info["full_path"]
                new_combo.currentIndexChanged.connect(self.spnbox_changed)
                new_hbox.addWidget(new_combo)
                data_info["widget"] = new_combo

            elif data_info["type"] == "other(s)":
                new_label.my_style = "color: rgba(0, 0, 0, 255)"
                new_label.setStyleSheet(new_label.my_style)
                new_hbox.addWidget(new_label)
                par_str = str(data_info["default"])
                new_txt_in = QLineEdit()
                new_txt_in.setText(par_str)
                new_txt_in.local_path = data_info["full_path"]
                new_txt_in.textChanged.connect(self.text_changed)
                new_hbox.addWidget(new_txt_in)
                data_info["widget"] = new_txt_in

            else:
                logging.info("else: " + str(data_info))

            self.main_vbox.addLayout(new_hbox)

        self.main_vbox.addStretch()

    def do_emit_signal(self, str_path, str_value):
        if self.do_emit:
            str_value = str_value.replace(", ", ",")
            self.item_changed.emit(str_path, str_value)

        self.do_emit = True

    def update_param(self, param_in, value_in):
        logging.info("\n update_param (Advanced)" + str(param_in) + str(value_in))
        for widget in self.children():
            widget_path = None
            if isinstance(widget, QLineEdit):
                widget_path = widget.local_path
                widget_value = str(widget.text())

            if isinstance(widget, MyQComboBox):
                widget_path = widget.local_path
                widget_value = str(widget.currentText())

            if widget_path == param_in:
                if widget_value == value_in:
                    logging.info("No need to change parameter (same value)")

                else:
                    self.do_emit = False
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value_in))

                    if isinstance(widget, MyQComboBox):
                        widget.setCurrentText(str(value_in))

                    self.do_emit = True

    def update_all_pars(self, tup_lst_pars):
        logging.info("(Advanced Widget) updating par to:" + str(tup_lst_pars))
        for par_dic in tup_lst_pars[0]:
            if par_dic["name"] != "":
                self.update_param(par_dic["name"], par_dic["value"])

    def text_changed(self):
        sender = self.sender()
        str_path = str(sender.local_path)
        str_value = str(sender.text())
        self.do_emit_signal(str_path, str_value)

    def spnbox_changed(self):
        sender = self.sender()
        str_path = str(sender.local_path)
        str_value = str(sender.currentText())
        self.do_emit_signal(str_path, str_value)

    def reset_pars(self):
        logging.info("Hi from reset_pars")
        for data_info in self.lst_par_line:
            try:
                default = data_info["default"]

            except KeyError:
                default = None

            if(
                (data_info["type"] == "bool"
                 or
                 data_info["type"] == "choice")
            ):
                try:
                    data_info["widget"].setCurrentIndex(default)

                except TypeError:
                    data_info["widget"].setCurrentIndex(0)

            elif data_info["type"] == "other(s)":
                par_str = str(data_info["default"])
                data_info["widget"].setText(par_str)

    def find_next_search_click(self):
        logging.info("find_next_search_click(AdvancedParameters)")
        try:
            self.num_fnd_widg += 1
            if self.num_fnd_widg >= len(self.lst_found_widg):
                self.num_fnd_widg = 0

            try:
                self.my_scroll_area.ensureWidgetVisible(
                    self.lst_found_widg[self.num_fnd_widg]
                )

            except IndexError:
                logging.info("No match found")

        except AttributeError:
            logging.info("failed to search ... (AdvancedParameters)")

    def search_changed(self):
        sender = self.sender()
        str_value = str(sender.text())
        logging.info("searching for:" + str_value)
        self.lst_found_widg = []
        self.num_fnd_widg = 0
        if len(str_value) > 1:
            for widget in self.children():
                if isinstance(widget, QLabel):
                    labl_text = str(widget.text())
                    if str_value in labl_text:
                        self.lst_found_widg.append(widget)
                        widget.setFont(
                            QFont(
                                "Arial",
                                self.font_point_size + 10, QFont.Bold
                            )
                        )
                        widget.setStyleSheet("color: rgba(65, 175, 175, 255)")

                    else:
                        widget.setFont(self.norm_labl_font)
                        widget.setStyleSheet(widget.my_style)

        else:
            for widget in self.children():
                if isinstance(widget, QLabel):
                    widget.setFont(self.norm_labl_font)
                    widget.setStyleSheet(widget.my_style)


def make_square_srting(long_string_in = None, extra_space = 0):
    lst_str = long_string_in.split("_")
    sqr_str = (3 - len(lst_str)) * " \n"
    row_len = 11 + extra_space
    for row_ini in lst_str:
        row_end = row_ini + (row_len - len(row_ini)) * " " + "\u00A0\n"
        sqr_str += row_end

    sqr_str = sqr_str[0:-1]
    return sqr_str


def draw_quadratic_bezier_3_points(
        scene_obj, p1x, p1y, p2x, p2y, p3x, p3y,
        lin_pen, row_size, col_size
):
    arrowhead = scene_obj.arrowhead
    sharp_turns = scene_obj.sharp_turns
    arrow_head_W = 1.0 / 4.0
    arrow_head_H = 1.0 / 8.0
    if arrowhead:
        if p1x == p2x:
            scene_obj.addLine(
                p3x, p3y,
                p3x - col_size * arrow_head_W, p3y - row_size * arrow_head_H,
                lin_pen
            )
            scene_obj.addLine(
                p3x, p3y,
                p3x - col_size * arrow_head_W, p3y + row_size * arrow_head_H,
                lin_pen
            )

        else:
            scene_obj.addLine(
                p3x, p3y,
                p3x - col_size * arrow_head_H, p3y - row_size * arrow_head_W,
                lin_pen
            )
            scene_obj.addLine(
                p3x, p3y,
                p3x + col_size * arrow_head_H, p3y - row_size * arrow_head_W,
                lin_pen
            )

    if sharp_turns:
        if p1x == p2x:
            vert_lin_y = p3y - row_size
            vert_lin_x = p1x
            scene_obj.addLine(vert_lin_x, p1y, vert_lin_x, vert_lin_y, lin_pen)
            horz_lin_x = p1x + col_size
            scene_obj.addLine(p3x, p3y, horz_lin_x, p3y, lin_pen)

            curv_p1x = vert_lin_x
            curv_p1y = vert_lin_y
            curv_p2x = p2x
            curv_p2y = p2y
            curv_p3x = horz_lin_x
            curv_p3y = p3y

        else:
            vert_lin_x = p3x
            vert_lin_y = p1y + row_size
            scene_obj.addLine(p2x, vert_lin_y, vert_lin_x, p3y, lin_pen)
            horz_lin_x = p3x - col_size
            scene_obj.addLine(p1x, p1y, horz_lin_x, p1y, lin_pen)

            curv_p1x = vert_lin_x
            curv_p1y = vert_lin_y
            curv_p2x = p2x
            curv_p2y = p2y
            curv_p3x = horz_lin_x
            curv_p3y = p1y

        n_points = 15

        dx12 = (curv_p2x - curv_p1x) / n_points
        dx23 = (curv_p3x - curv_p2x) / n_points

        dy12 = (curv_p2y - curv_p1y) / n_points
        dy23 = (curv_p3y - curv_p2y) / n_points

        for pos in range(n_points + 1):
            x1 = curv_p1x + dx12 * float(pos)
            y1 = curv_p1y + dy12 * float(pos)
            x2 = curv_p2x + dx23 * float(pos)
            y2 = curv_p2y + dy23 * float(pos)

            dx1 = (x2 - x1) / n_points
            dy1 = (y2 - y1) / n_points

            gx1 = x1 + dx1 * float(pos)
            gy1 = y1 + dy1 * float(pos)

            if pos > 0:
                scene_obj.addLine(x, y, gx1, gy1, lin_pen)

            x = gx1
            y = gy1

    else:
        scene_obj.addLine(p1x, p1y, p2x, p2y, lin_pen)
        scene_obj.addLine(p2x, p2y, p3x, p3y, lin_pen)


def copy_lst_nodes(old_lst_nodes):
    new_lst = []
    try:
        for old_node in old_lst_nodes:
            cp_new_node = {
                "number": int(old_node["number"]),
                "status": str(old_node["status"]),
            }
            new_child_node_lst = []
            for child_node in old_node["child_node_lst"]:
                new_child_node_lst.append(int(child_node))

            cp_new_node["child_node_lst"] = new_child_node_lst

            new_parent_node_lst = []
            for parent_node in old_node["parent_node_lst"]:
                new_parent_node_lst.append(int(parent_node))

            cp_new_node["parent_node_lst"] = new_parent_node_lst

            new_cmd2show = []
            for cmd in old_node["cmd2show"]:
                new_cmd2show.append(str(cmd))

            cp_new_node["cmd2show"] = new_cmd2show

            new_lst2run = []
            for cmd_lst in old_node["lst2run"]:
                inner_lst = []
                for inner_cmd in cmd_lst:
                    inner_lst.append(str(inner_cmd))

                new_lst2run.append(inner_lst)

            cp_new_node["lst2run"] = new_lst2run

            new_lst.append(cp_new_node)

    except TypeError:
        logging.info("ERR catch on copy_lst_nodes")

    return new_lst


def add_ready_node(old_lst_nodes, com_par):
    try:
        cp_new_node = {
            "number": int(com_par.number),
            "status": str(com_par.status),
            "cmd2show": [str(com_par.m_cmd_lst[-1])],
        }
        new_parent_node_lst = []
        for parent_node in com_par.parent_node_lst:
            new_parent_node_lst.append(int(parent_node))

        cp_new_node["parent_node_lst"] = new_parent_node_lst
        cp_new_node["child_node_lst"] = []

        new_lst = []
        for singl_node in old_lst_nodes:
            if singl_node["number"] in cp_new_node["parent_node_lst"]:
                singl_node["child_node_lst"].append(int(com_par.number))

            new_lst.append(singl_node)

        new_lst.append(cp_new_node)

        return new_lst

    except AttributeError:
        logging.info(" Attribute Err catch (add_ready_node) ")
        return old_lst_nodes

    except IndexError:
        logging.info(" Index Err catch (add_ready_node) ")
        return old_lst_nodes


class TreeDirScene(QGraphicsScene):
    node_clicked_w_left = Signal(int)
    node_clicked_w_right = Signal(int)
    hide_clicked = Signal(int)
    def __init__(self, parent = None):
        super(TreeDirScene, self).__init__(parent)
        self.setFont(QFont("Courier"))
        fm_rect = QFontMetrics(self.font()).boundingRect("W")
        self.f_width = fm_rect.width()
        self.f_height = fm_rect.height()

        ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.px_map = {}
        stp_siz = QSize(self.f_width * 4.1, self.f_height * 1.6)
        for key_str, def_item in widgets_defs.items():
            icon_path = ui_dir_path + os.sep + def_item["icon"]
            tmp_px_map = QPixmap(icon_path)
            self.px_map[key_str] = tmp_px_map.scaled(
                stp_siz, mode = Qt.SmoothTransformation
            )

        hide_show_siz = QSize(self.f_width * 3.5, self.f_height * 1.2)
        hide_icon_path = ui_dir_path + os.sep + "resources" \
                         + os.sep + "hide_branch.png"
        hid_px_map = QPixmap(hide_icon_path)
        self.hide_icon = hid_px_map.scaled(
            hide_show_siz, mode = Qt.SmoothTransformation
        )
        show_icon_path = ui_dir_path + os.sep + "resources" \
                         + os.sep + "show_branch.png"
        show_px_map = QPixmap(show_icon_path)
        self.show_icon = show_px_map.scaled(
            hide_show_siz, mode = Qt.SmoothTransformation
        )
        self.set_colours(True)
        self.set_sharp_turns(True)
        self.set_arrowhead(True)

        self.lst_nod_pos = []
        self.nod_lst = None

        self.tree_obj = format_utils.TreeShow()

        self.bar_pos = 1
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_bars)
        timer.start(500)

    def try_draw_all(self):
        try:
            self.draw_all()
            logging.info(" new sharp_turns =" + str(self.sharp_turns))
            logging.info("self.arrowhead =" + str(self.arrowhead))

        except AttributeError:
            logging.info("not drawing tree/graph")

    def set_sharp_turns(self, sharp_turns_on):
        self.sharp_turns = sharp_turns_on
        self.try_draw_all()

    def set_arrowhead(self, arrowhead_on):
        self.arrowhead = arrowhead_on
        self.try_draw_all()

    def set_colours(self, regular_colours):
        if regular_colours:
            self.font_blue_brush = QBrush(Qt.blue, Qt.SolidPattern)
            self.font_red_brush = QBrush(Qt.darkRed, Qt.SolidPattern)
            self.font_green_brush = QBrush(Qt.darkGreen, Qt.SolidPattern)
            self.font_gray_brush = QBrush(Qt.gray, Qt.SolidPattern)
            self.cursor_brush = QBrush(Qt.cyan, Qt.SolidPattern)
            self.first_gray_brush = QBrush(Qt.lightGray, Qt.SolidPattern)
            self.another_gray_brush = QBrush(Qt.white, Qt.SolidPattern)
            self.invisible_brush = QBrush(Qt.white, Qt.NoBrush)
            self.arrow_green_pen = QPen(
                Qt.darkGreen, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.arrow_red_pen = QPen(
                Qt.darkRed, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.arrow_blue_pen = QPen(
                Qt.blue, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.arrow_gray_pen = QPen(
                Qt.gray, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.gray_pen = QPen(
                Qt.gray, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.rectang_pen = QPen(
                Qt.white, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )

        else:
            self.font_blue_brush = QBrush(Qt.cyan, Qt.SolidPattern)
            self.font_red_brush = QBrush(Qt.red, Qt.SolidPattern)
            self.font_green_brush = QBrush(Qt.green, Qt.SolidPattern)
            self.font_gray_brush = QBrush(Qt.darkCyan, Qt.SolidPattern)
            self.cursor_brush = QBrush(Qt.blue, Qt.SolidPattern)
            self.first_gray_brush = QBrush(Qt.gray, Qt.SolidPattern)
            self.another_gray_brush = QBrush(Qt.darkGray, Qt.SolidPattern)
            self.invisible_brush = QBrush(Qt.white, Qt.NoBrush)
            self.arrow_green_pen = QPen(
                Qt.green, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.arrow_red_pen = QPen(
                Qt.red, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.arrow_blue_pen = QPen(
                Qt.cyan, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.arrow_gray_pen = QPen(
                Qt.darkCyan, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.gray_pen = QPen(
                Qt.gray, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            self.rectang_pen = QPen(
                Qt.darkGray, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )

    def refresh_bars(self):
        do_refresh = False
        if self.nod_lst is not None:
            for node in self.nod_lst:
                if node["stp_stat"] == "B":
                    self.bar_pos += 0.15
                    if self.bar_pos > 3:
                        self.bar_pos = 1

                    self.draw_all()

    def get_coords(self, row, col):
        return col * self.f_width * 4, row  * self.f_height * 2

    def get_pen_colour(self, stat):
        if stat == "S":
            pen_col = self.arrow_blue_pen

        elif stat == "F":
            pen_col = self.arrow_red_pen

        elif stat == "H":
            pen_col = self.arrow_gray_pen

        else:
            pen_col = self.arrow_green_pen

        return pen_col

    def get_brush_colour(self, stat):
        if stat == "S":
            brush_col = self.font_blue_brush

        elif stat == "F":
            brush_col = self.font_red_brush

        elif stat == "H":
            brush_col = self.font_gray_brush

        else:
            brush_col = self.font_green_brush

        return brush_col

    def mouseReleaseEvent(self, event):
        x_ms = event.scenePos().x()
        y_ms = event.scenePos().y()
        ms_b = event.button()
        node_numb = None
        min_d = None
        for num, nod in enumerate(self.lst_nod_pos):
            dy = abs(nod["y_pos"] - y_ms)
            if num == 0:
                min_d = dy
                node_numb = nod["number"]

            elif dy < min_d:
                min_d = dy
                node_numb = nod["number"]

        if node_numb is not None:
            xright = self.x_left + self.x_width
            if(
                x_ms > self.x_left and x_ms < xright
                and ms_b == Qt.MouseButton.LeftButton
            ):
                self.node_clicked_w_left.emit(node_numb)

            elif(
                x_ms < self.x_width + self.f_width
                and x_ms > xright
                and ms_b == Qt.MouseButton.LeftButton
            ):
                self.node_clicked_w_left.emit(node_numb)
                self.hide_clicked.emit(node_numb)
            elif(
                x_ms > self.x_left and
                x_ms < self.x_width + self.f_width
                and ms_b == Qt.MouseButton.RightButton
            ):
                self.node_clicked_w_right.emit(node_numb)

    def draw_all(self):
        if self.nod_lst is not None:
            self.clear()
            max_indent = 0
            max_cmd_len = 0
            for node in self.nod_lst:
                if node["indent"] > max_indent:
                    max_indent = node["indent"]

                node_len = len(node["str_cmd"])
                if node_len > max_cmd_len:
                    max_cmd_len = node_len

            right_x, down_y = self.get_coords(
                len(self.nod_lst),
                max_indent * 1.2 + max_cmd_len * 0.3 + 7
            )
            right_x += self.f_width * 3.8
            left_x, up_y = self.get_coords(-1, -1)
            dx = right_x - left_x
            dy = down_y - up_y
            self.addRect(
                left_x - self.f_width, up_y,
                dx + self.f_width, dy,
                self.gray_pen, self.first_gray_brush
            )
            self.setSceneRect(
                left_x - self.f_width, up_y,
                dx + self.f_width, dy,
            )
            for i in range(int((len(self.nod_lst) - 1) / 2 + 1)):
                pos = i * 2
                my_x, my_y = self.get_coords(pos, -1)
                self.addRect(
                    left_x, my_y - self.f_height,
                    dx - self.f_width, self.f_height * 2,
                    self.rectang_pen, self.another_gray_brush
                )

            for pos, node in enumerate(self.nod_lst):
                my_x, my_y = self.get_coords(pos, -1)
                if node["stp_stat"] == "H":
                    new_ico = self.addPixmap(self.hide_icon)

                else:
                    new_ico = self.addPixmap(self.show_icon)

                new_ico.setPos(
                    right_x - self.f_width * 4.6,
                    my_y - self.f_height * 0.7 + self.f_height * 0.1
                )

            for pos, node in enumerate(self.nod_lst):
                if node["number"] == self.curr_nod_num:
                    current_nod_pos = pos
                    right_x1, down_y1 = self.get_coords(
                        current_nod_pos + 0.43,
                        max_indent * 1.2 + max_cmd_len * 0.3 + 6.7
                    )
                    left_x1, up_y1 = self.get_coords(
                        current_nod_pos - 0.43, -0.7
                    )
                    dx1 = right_x1 - left_x1
                    dy1 = down_y1 - up_y1
                    rect_border_colour = self.get_pen_colour(node["stp_stat"])

                    self.x_left = left_x1 - self.f_width
                    self.x_width = dx1 + self.f_width
                    self.addRect(
                        self.x_left, up_y1, self.x_width, dy1,
                        rect_border_colour, self.cursor_brush
                    )

            row_size, col_size = self.get_coords(0.5, 0.5)
            for pos, node in enumerate(self.nod_lst):
                if len(node["par_lst"]) > 1:
                    my_coord_x ,my_coord_y = self.get_coords(
                        pos, node["indent"]
                    )
                    lst2connect = []
                    for par_pos, prev in enumerate(self.nod_lst[0:pos]):
                        if prev["number"] in node["par_lst"]:
                            lst2connect.append((par_pos, prev["indent"]))

                    max_pos = 0
                    for lst_item in lst2connect:
                        if lst_item[0] > max_pos:
                            max_pos = lst_item[0]

                    for lst_item in lst2connect:
                        if lst_item[0] != max_pos:
                            parent_x, parent_y = self.get_coords(
                                lst_item[0], lst_item[1]
                            )
                            arr_col = self.get_pen_colour(node["stp_stat"])
                            draw_quadratic_bezier_3_points(
                                self,
                                parent_x + self.f_width * 2.4,
                                parent_y,
                                my_coord_x + self.f_width * 0.5,
                                parent_y,
                                my_coord_x + self.f_width * 0.5,
                                my_coord_y - self.f_height * 0.95,
                                arr_col, row_size, col_size
                            )

            for pos, node in enumerate(self.nod_lst):
                my_coord_x ,my_coord_y = self.get_coords(pos, node["indent"])
                if pos > 0:
                    for inner_row, inner_node in enumerate(self.nod_lst):
                        if inner_node["number"] == node["low_par_nod_num"]:
                            parent_x, parent_y = self.get_coords(
                                inner_row, node["parent_indent"]
                            )
                            arr_col = self.get_pen_colour(node["stp_stat"])
                            draw_quadratic_bezier_3_points(
                                self,
                                parent_x,
                                parent_y + self.f_height * 0.9,
                                parent_x, my_coord_y,
                                my_coord_x - self.f_width * 1.6,
                                my_coord_y,
                                arr_col, row_size, col_size
                            )

            self.lst_nod_pos = []
            nod_bar_pos = self.bar_pos
            for pos, node in enumerate(self.nod_lst):
                my_coord_x ,my_coord_y = self.get_coords(pos, node["indent"])
                nod_pos = {
                    "number": node["number"],
                    "x_pos": my_coord_x,
                    "y_pos": my_coord_y
                }
                self.lst_nod_pos.append(nod_pos)
                border_colour = self.get_pen_colour(node["stp_stat"])
                brush_col = self.get_brush_colour(node["stp_stat"])
                elip = self.addRect(
                    my_coord_x - self.f_width * 1.4,
                    my_coord_y - self.f_height * 0.9,
                    self.f_width * 3.6,
                    self.f_height * 1.7,
                    border_colour, self.invisible_brush
                )
                try:
                    tmp_pxm = self.addPixmap(self.px_map[node["str_cmd"]])

                except KeyError:
                    tmp_pxm = self.addPixmap(self.px_map["optional"])

                tmp_pxm.setPos(
                    my_coord_x - self.f_width * 2.6 + self.f_width * 0.9,
                    my_coord_y - self.f_height * 0.9 + self.f_height * 0.1
                )

                my_coord_x ,my_coord_y = self.get_coords(pos, -0.6)
                n_text = self.addSimpleText(str(node["number"]))
                n_text.setPos(
                    my_coord_x - self.f_width * 0.7,
                    my_coord_y - self.f_height * 0.67
                )
                n_text.setBrush(brush_col)

                my_coord_x ,my_coord_y = self.get_coords(
                    pos, max_indent * 1.2 + max_cmd_len * 0.3 + 6.1
                )
                n_text = self.addSimpleText(str(node["number"]))
                n_text.setPos(
                    my_coord_x - self.f_width * 0.7,
                    my_coord_y - self.f_height * 0.67
                )
                n_text.setBrush(brush_col)
                stat_text = self.addSimpleText(str(node["stp_stat"]))
                stat_text.setPos(
                    self.f_width * 0.5,
                    my_coord_y - self.f_height * 0.67
                )
                stat_text.setBrush(brush_col)
                if str(node["stp_stat"]) == "B":
                    right_x1, down_y1 = self.get_coords(
                        pos + 0.3, max_indent + 1
                    )
                    left_x1, up_y1 = self.get_coords(pos - 0.3, max_indent + 4)
                    dx1 = right_x1 - left_x1
                    dy1 = down_y1 - up_y1
                    self.addRect(
                        left_x1 - self.f_width, up_y1,
                        dx1 + self.f_width, dy1,
                        self.arrow_green_pen, self.another_gray_brush
                    )
                    right_x1, down_y1 = self.get_coords(
                        pos + 0.3, max_indent + nod_bar_pos
                    )
                    left_x1, up_y1 = self.get_coords(
                        pos - 0.3, max_indent + nod_bar_pos + 1
                    )
                    dx1 = right_x1 - left_x1
                    dy1 = down_y1 - up_y1
                    self.addRect(
                        left_x1 - self.f_width, up_y1,
                        dx1 + self.f_width, dy1,
                        self.arrow_green_pen, self.font_green_brush
                    )

                cmd_text = self.addSimpleText(str(node["str_cmd"]))
                x1, y1 = self.get_coords(pos - 0.28, max_indent + 5)
                cmd_text.setPos(x1, y1)
                cmd_text.setBrush(brush_col)
                cmd_text.setFont(QFont("Courier"))

            self.update()

    def draw_tree_graph(
        self, nod_lst_in = [], curr_nod_num = 0,
        new_node = None, lst2exl_in = []
    ):
        tmp_local_lst = copy_lst_nodes(nod_lst_in)
        self.nod_lst_2_paint = add_ready_node(tmp_local_lst, new_node)
        lst_str = self.tree_obj(
            lst_nod = self.nod_lst_2_paint, lst2exl = lst2exl_in
        )
        lst_2d_dat = self.tree_obj.get_tree_data()
        self.nod_lst = lst_2d_dat
        self.curr_nod_num = curr_nod_num
        self.draw_all()

    def new_nod_num(self, nod_num_in):
        self.curr_nod_num = nod_num_in
        self.draw_all()

