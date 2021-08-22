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

import sys, os, requests
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *
import numpy as np


try:
    from shared_modules import format_utils

except ModuleNotFoundError:
    '''
    This trick to import the format_utils module can be
    removed once the project gets properly packaged
    '''
    comm_path = os.path.abspath(__file__)[0:-19] + "shared_modules"
    print("comm_path: ", comm_path)
    sys.path.insert(1, comm_path)
    import format_utils


widgets_defs = {
    "Root" : {
        "tooltip": "Root node ... Not supposed to run any code",
        "icon": "resources/root.png",
        "main_cmd"  :"# root node",
        "nxt_widg_lst"  :["import"]
    },
    "import" : {
        "tooltip": "dials.import ...",
        "icon": "resources/import.png",
        "main_cmd"  :"dials.import",
        "nxt_widg_lst"  :["find_spots", "apply_mask"]
    },
    "apply_mask" : {
        "tooltip": "dials.apply_mask ...",
        "icon": "resources/mask.png",
        "main_cmd"  :"dials.apply_mask",
        "nxt_widg_lst"  :["find_spots"]
    },
    "find_spots" : {
        "tooltip": "dials.find_spots ...",
        "icon": "resources/find_spots.png",
        "main_cmd"  :"dials.find_spots",
        "nxt_widg_lst"  :["index", "combine_experiments"]
    },
    "index" : {
        "tooltip": "dials.index ...",
        "icon": "resources/index.png",
        "main_cmd"  :"dials.index",
        "nxt_widg_lst"  :[
            "refine_bravais_settings",
            "refine",
            "combine_experiments"
        ]
    },
    "refine_bravais_settings" : {
        "tooltip": "dials.refine_bravais_settings ...",
        "icon": "resources/refine_bv_set.png",
        "main_cmd"  :"dials.refine_bravais_settings",
        "nxt_widg_lst"  :["reindex"]
    },
    "reindex" : {
        "tooltip": "dials.reindex ...",
        "icon": "resources/reindex.png",
        "main_cmd"  :"dials.reindex",
        "nxt_widg_lst"  :["refine", "integrate"]
    },
    "refine" : {
        "tooltip": "dials.refine ...",
        "icon": "resources/refine.png",
        "main_cmd"  :"dials.refine",
        "nxt_widg_lst"  :["integrate", "refine_bravais_settings"]
    },
    "integrate" : {
        "tooltip": "dials.integrate ...",
        "icon": "resources/integrate.png",
        "main_cmd"  :"dials.integrate",
        "nxt_widg_lst"  :["scale", "symmetry"]
    },
    "symmetry" : {
        "tooltip": "dials.symmetry ...",
        "icon": "resources/symmetry.png",
        "main_cmd"  :"dials.symmetry",
        "nxt_widg_lst"  :["scale", "combine_experiments"]
    },
    "scale" : {
        "tooltip": "dials.scale ...",
        "icon": "resources/scale.png",
        "main_cmd"  :"dials.scale",
        "nxt_widg_lst"  :["symmetry", "combine_experiments"]
    },
    "combine_experiments" : {
        "tooltip": "dials.combine_experiments ...",
        "icon": "resources/combine.png",
        "main_cmd"  :"dials.combine_experiments",
        "nxt_widg_lst"  :["index", "refine", "integrate"]
    }
}


class MyQComboBox(QComboBox):
    def __init__(self, parent=None):
        super(MyQComboBox, self).__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)

    def wheelEvent(self, event):
        print(
            "event: \n", event,
            "\n not suposed to change with wheel event"
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

    def build_pars(self, lst_phil_obj):
        self.lst_par_line = lst_phil_obj
        print("Hi from build_pars")
        for data_info in self.lst_par_line:
            label_str = "    " * data_info["indent"]
            label_str += data_info["name"]
            new_label = QLabel(label_str)
            new_label.setAutoFillBackground(True)
            new_label.setFont(QFont("Monospace", self.font_point_size, QFont.Bold))
            data_info["Label"] = new_label
            new_hbox = QHBoxLayout()

            try:
                default = data_info["default"]

            except KeyError:
                default = None

            data_info["widget"] = None
            if data_info["type"] == "scope":
                new_label.setStyleSheet("color: rgba(105, 105, 105, 255)")
                new_hbox.addWidget(new_label)

            elif(
                (data_info["type"] == "bool"
                 or
                 data_info["type"] == "choice")
            ):
                new_label.setStyleSheet("color: rgba(0, 0, 0, 255)")
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
                new_label.setStyleSheet("color: rgba(0, 0, 0, 255)")
                new_hbox.addWidget(new_label)
                par_str = str(data_info["default"])
                new_txt_in = QLineEdit()
                new_txt_in.setText(par_str)
                new_txt_in.local_path = data_info["full_path"]
                new_txt_in.textChanged.connect(self.text_changed)
                new_hbox.addWidget(new_txt_in)
                data_info["widget"] = new_txt_in

            else:
                print("else: ", data_info)

            self.main_vbox.addLayout(new_hbox)

        self.main_vbox.addStretch()

    def do_emit_signal(self, str_path, str_value):
        if self.do_emit:
            self.item_changed.emit(str_path, str_value)

        self.do_emit = True

    def update_param(self, param_in, value_in):
        print("\n update_param (Advanced)", param_in, value_in)

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
                    print("No need to change parameter (same value)")

                else:
                    self.do_emit = False
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value_in))

                    if isinstance(widget, MyQComboBox):
                        widget.setCurrentText(str(value_in))

                    self.do_emit = True

    def update_all_pars(self, tup_lst_pars):
        print("\n (Advanced Widget) \n time to update par to:", tup_lst_pars, "\n")
        for par_dic in tup_lst_pars[0]:
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
        print("Hi from reset_pars")
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


def draw_quadratic_bezier_3_points(
        scene_obj, p1x, p1y, p2x, p2y, p3x, p3y,
        lin_pen, row_size, col_size
):
    arrow_head = True
    curved_corners = True

    if arrow_head:
        if p1x == p2x:
            scene_obj.addLine(
                p3x, p3y, p3x - col_size / 3, p3y - row_size / 3, lin_pen
            )
            scene_obj.addLine(
                p3x, p3y, p3x - col_size / 3, p3y + row_size / 3, lin_pen
            )
        else:
            scene_obj.addLine(
                p3x, p3y, p3x - col_size / 3, p3y - row_size / 3, lin_pen
            )
            scene_obj.addLine(
                p3x, p3y, p3x + col_size / 3, p3y - row_size / 3, lin_pen
            )

    if curved_corners:
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
    for old_node in old_lst_nodes:
        cp_new_node = {
            "number": int(old_node["number"]),
            "status": str(old_node["status"]),
            "cmd2show": list(old_node["cmd2show"]),
        }
        new_child_node_lst = []
        for child_node in old_node["child_node_lst"]:
            new_child_node_lst.append(int(child_node))

        cp_new_node["child_node_lst"] = new_child_node_lst

        new_parent_node_lst = []
        for parent_node in old_node["parent_node_lst"]:
            new_parent_node_lst.append(int(parent_node))

        cp_new_node["parent_node_lst"] = new_parent_node_lst

        new_cmd_lst = []
        for cmd in old_node["cmd2show"]:
            new_cmd_lst.append(str(cmd))

        cp_new_node["cmd2show"] = new_cmd_lst

        new_lst.append(cp_new_node)

    return new_lst


def add_ready_node(old_lst_nodes, com_par):
    try:
        cp_new_node = {
            "number": int(com_par.number),
            "status": str(com_par.status),
            "cmd2show": [str(com_par.cmd)],
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
        return old_lst_nodes


class TreeDirScene(QGraphicsScene):
    node_clicked = Signal(int)
    def __init__(self, parent = None):
        super(TreeDirScene, self).__init__(parent)
        self.setFont(QFont("Monospace"))
        fm = QFontMetrics(self.font())
        self.f_width = fm.width("0")
        self.f_height = fm.height()

        ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.px_map = {}
        for key_str, def_item in widgets_defs.items():
            icon_path = ui_dir_path + os.sep + def_item["icon"]
            tmp_px_map = QPixmap(icon_path)
            siz = QSize(self.f_width * 4.1, self.f_height * 1.6)
            self.px_map[key_str] = tmp_px_map.scaled(siz)

        self.blue_brush = QBrush(Qt.blue, Qt.SolidPattern)
        self.red_brush = QBrush(Qt.red, Qt.SolidPattern)
        self.green_brush = QBrush(Qt.darkGreen, Qt.SolidPattern)
        self.dark_blue_brush = QBrush(Qt.darkBlue, Qt.SolidPattern)
        self.cyan_brush = QBrush(Qt.cyan, Qt.SolidPattern)
        self.gray_brush = QBrush(Qt.gray, Qt.SolidPattern)
        self.light_gray_brush = QBrush(Qt.lightGray, Qt.SolidPattern)
        self.white_brush = QBrush(Qt.white, Qt.SolidPattern)
        self.invisible_brush = QBrush(Qt.white, Qt.NoBrush)
        self.blue_gradient_brush = QBrush(Qt.blue, Qt.SolidPattern)

        self.black_pen = QPen(
            Qt.black, 1.6, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )

        self.green_pen = QPen(
            Qt.green, 1.6, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.dark_green_pen = QPen(
            Qt.darkGreen, 1.6, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )

        self.red_pen = QPen(
            Qt.red, 1.6, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )

        self.blue_pen = QPen(
            Qt.blue, 1.6, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.dark_blue_pen = QPen(
            Qt.darkBlue, 1.9, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.cyan_pen = QPen(
            Qt.cyan, 2, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.gray_pen = QPen(
            Qt.gray, 2, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.white_pen = QPen(
            Qt.white, 2, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.lst_nod_pos = []
        self.nod_lst = None

        self.tree_obj = format_utils.TreeShow()

        self.bar_pos = 1
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_bars)
        timer.start(500)

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
            pen_col = self.blue_pen

        elif stat == "F":
            pen_col = self.red_pen

        else:
            pen_col = self.dark_green_pen

        return pen_col

    def get_brush_colour(self, stat):
        if stat == "S":
            brush_col = self.blue_brush

        elif stat == "F":
            brush_col = self.red_brush

        else:
            brush_col = self.green_brush

        return brush_col

    def mouseReleaseEvent(self, event):
        y_ms = event.scenePos().y()
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
            self.node_clicked.emit(node_numb)

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
            left_x, up_y = self.get_coords(-1, -1)
            dx = right_x - left_x
            dy = down_y - up_y
            self.addRect(
                left_x - self.f_width, up_y,
                dx + self.f_width, dy,
                self.gray_pen, self.light_gray_brush
            )
            for i in range(int((len(self.nod_lst) - 1) / 2 + 1)):
                pos = i * 2
                my_x, my_y = self.get_coords(pos, -1)
                self.addRect(
                    left_x, my_y - self.f_height,
                    dx - self.f_width, self.f_height * 2,
                    self.white_pen, self.white_brush
                )

            for pos, node in enumerate(self.nod_lst):
                if node["number"] == self.current_nod_num:
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
                    self.addRect(
                        left_x1 - self.f_width, up_y1,
                        dx1 + self.f_width, dy1,
                        rect_border_colour, self.cyan_brush
                    )

            row_size, col_size = self.get_coords(0.5, 0.5)
            for pos, node in enumerate(self.nod_lst):
                if len(node["par_lst"]) > 1:
                    my_coord_x ,my_coord_y = self.get_coords(pos, node["indent"])
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
                            my_parent_coord_x, my_parent_coord_y = self.get_coords(
                                lst_item[0], lst_item[1]
                            )
                            arr_col = self.get_pen_colour(node["stp_stat"])
                            draw_quadratic_bezier_3_points(
                                self,
                                my_parent_coord_x + self.f_width * 2.7, my_parent_coord_y,
                                my_coord_x + self.f_width * 0.5,
                                my_parent_coord_y,
                                my_coord_x + self.f_width * 0.5,
                                my_coord_y - self.f_height * 0.95,
                                arr_col, row_size, col_size
                            )

            for pos, node in enumerate(self.nod_lst):
                my_coord_x ,my_coord_y = self.get_coords(pos, node["indent"])
                if pos > 0:
                    for inner_row, inner_node in enumerate(self.nod_lst):
                        if inner_node["number"] == node["low_par_nod_num"]:
                            my_parent_coord_x, my_parent_coord_y = self.get_coords(
                                inner_row, node["parent_indent"]
                            )
                            arr_col = self.get_pen_colour(node["stp_stat"])
                            draw_quadratic_bezier_3_points(
                                self,
                                my_parent_coord_x,
                                my_parent_coord_y + self.f_height * 0.9,
                                my_parent_coord_x, my_coord_y,
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
                    self.f_height * 1.8,
                    border_colour, self.invisible_brush
                )
                try:
                    tmp_pxm = self.addPixmap(self.px_map[node["str_cmd"]])
                    tmp_pxm.setPos(
                        my_coord_x - self.f_width * 2.6 + self.f_width * 0.9,
                        my_coord_y - self.f_height * 0.9 + self.f_height * 0.1
                    )

                except KeyError:
                    #print("One node without 'str_cmd' ")
                    pass

                my_coord_x ,my_coord_y = self.get_coords(pos, -0.6)
                n_text = self.addSimpleText(str(node["number"]))
                n_text.setPos(my_coord_x - self.f_width * 0.7,
                            my_coord_y - self.f_height * 0.5)
                n_text.setBrush(self.dark_blue_brush)

                my_coord_x ,my_coord_y = self.get_coords(
                    pos, max_indent * 1.2 + max_cmd_len * 0.3 + 6.1
                )
                n_text = self.addSimpleText(str(node["number"]))
                n_text.setPos(my_coord_x - self.f_width * 0.7,
                            my_coord_y - self.f_height * 0.5)
                n_text.setBrush(self.dark_blue_brush)

                stat_text = self.addSimpleText(str(node["stp_stat"]))
                stat_text.setPos(
                    self.f_width * 0.5,
                    my_coord_y - self.f_height * 0.5
                )
                stat_text.setBrush(self.dark_blue_brush)
                if str(node["stp_stat"]) == "B":
                    right_x1, down_y1 = self.get_coords(pos + 0.3, max_indent + 1)
                    left_x1, up_y1 = self.get_coords(pos - 0.3, max_indent + 4)
                    dx1 = right_x1 - left_x1
                    dy1 = down_y1 - up_y1
                    self.addRect(
                        left_x1 - self.f_width, up_y1,
                        dx1 + self.f_width, dy1,
                        self.dark_blue_pen, self.white_brush
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
                        self.dark_blue_pen, self.dark_blue_brush
                    )
                    to_desynchronize_bars = '''
                    nod_bar_pos += 0.1
                    if nod_bar_pos > 3:
                        nod_bar_pos = 1
                    #'''

                cmd_text = self.addSimpleText(str(node["str_cmd"]))
                x1, y1 = self.get_coords(pos - 0.3, max_indent + 5)
                cmd_text.setPos(x1, y1)
                cmd_text.setBrush(brush_col)
                cmd_text.setFont(QFont("Monospace"))

            self.update()

    def draw_tree_graph(
            self, nod_lst_in = [], current_nod_num = 0, new_node = None
    ):
        tmp_local_lst = copy_lst_nodes(nod_lst_in)
        self.paint_nod_lst = add_ready_node(tmp_local_lst, new_node)
        lst_str = self.tree_obj(lst_nod = self.paint_nod_lst)
        lst_2d_dat = self.tree_obj.get_tree_data()

        self.nod_lst = lst_2d_dat
        self.current_nod_num = current_nod_num
        self.draw_all()

    def new_nod_num(self, nod_num_in):
        self.current_nod_num = nod_num_in
        self.draw_all()

