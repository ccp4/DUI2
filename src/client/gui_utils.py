"""
DUI's command simple stacked widgets

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

import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *
import numpy as np

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
        print("Hi from AdvancedParameters")
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

    def text_changed(self):
        sender = self.sender()

        str_path = str(sender.local_path)
        str_value = str(sender.text())
        self.item_changed.emit(str_path, str_value)

    def spnbox_changed(self):
        sender = self.sender()

        str_path = str(sender.local_path)
        str_value = str(sender.currentText())
        self.item_changed.emit(str_path, str_value)


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

def draw_quadratic_bezier_3_points(scene_obj,
                          p1x, p1y, p2x, p2y, p3x, p3y,
                          lin_pen):
    n_points = 45

    dx12 = (p2x - p1x) / n_points
    dx23 = (p3x - p2x) / n_points

    dy12 = (p2y - p1y) / n_points
    dy23 = (p3y - p2y) / n_points

    for pos in range(n_points + 1):
        x1 = p1x + dx12 * float(pos)
        y1 = p1y + dy12 * float(pos)
        x2 = p2x + dx23 * float(pos)
        y2 = p2y + dy23 * float(pos)

        dx1 = (x2 - x1) / n_points
        dy1 = (y2 - y1) / n_points

        gx1 = x1 + dx1 * float(pos)
        gy1 = y1 + dy1 * float(pos)

        if pos > 0:
            scene_obj.addLine(x, y, gx1, gy1, lin_pen)

        if pos == n_points - 5:
            arrow_base_x = x
            arrow_base_y = y

        elif pos == n_points:
            arrow_tip_x = gx1
            arrow_tip_y = gy1

        x = gx1
        y = gy1

    dx = arrow_tip_x - arrow_base_x
    dy = arrow_tip_y - arrow_base_y

    # temporal non scaled arrowhead positions
    x_base_1 = arrow_base_x + dy / 2.0
    y_base_1 = arrow_base_y - dx / 2.0
    x_base_2 = arrow_base_x - dy / 2.0
    y_base_2 = arrow_base_y + dx / 2.0

    #scaling arrowheads
    dx1 = arrow_tip_x - x_base_1
    dy1 = arrow_tip_y - y_base_1
    dx2 = arrow_tip_x - x_base_2
    dy2 = arrow_tip_y - y_base_2

    size = np.sqrt((dx1 + dx2) ** 2.0 + (dy1 + dy2) ** 2.0) / 2.0

    scale = 7.0 / size

    x_base_1 = arrow_tip_x - dx1 * scale
    y_base_1 = arrow_tip_y - dy1 * scale

    x_base_2 = arrow_tip_x - dx2 * scale
    y_base_2 = arrow_tip_y - dy2 * scale

    #drawing arrowheads
    scene_obj.addLine(
        arrow_tip_x, arrow_tip_y,
        x_base_2, y_base_2,
        lin_pen
    )

    scene_obj.addLine(
        x_base_1, y_base_1,
        arrow_tip_x, arrow_tip_y,
        lin_pen
    )


class TreeDirScene(QGraphicsScene):
    node_clicked = Signal(int)
    def __init__(self, parent = None):
        super(TreeDirScene, self).__init__(parent)
        fm = QFontMetrics(self.font())
        self.f_width = fm.width("0")
        self.f_height = fm.height()

        self.blue_brush = QBrush(
            Qt.blue, Qt.SolidPattern,
        )
        self.dark_blue_brush = QBrush(
            Qt.darkBlue, Qt.SolidPattern,
        )
        self.cyan_brush = QBrush(
            Qt.cyan, Qt.SolidPattern,
        )

        self.gray_brush = QBrush(
            Qt.gray, Qt.SolidPattern,
        )

        self.light_gray_brush = QBrush(
            Qt.lightGray, Qt.SolidPattern,
        )
        self.white_brush = QBrush(
            Qt.white, Qt.SolidPattern,
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

    def get_coords(self, row, col):
        return col * self.f_width * 4, row  * self.f_height * 2

    def mouseReleaseEvent(self, event):
        x_ms = event.scenePos().x()
        y_ms = event.scenePos().y()
        nod_num = None
        min_d = None
        for num, nod in enumerate(self.lst_nod_pos):
            dx_sq = (nod["x_pos"] - x_ms) ** 2
            dy_sq = (nod["y_pos"] - y_ms) ** 2
            d_sq = dx_sq + dy_sq
            if num == 0:
                min_d = d_sq
                nod_num = nod["lin_num"]

            elif d_sq < min_d:
                min_d = d_sq
                nod_num = nod["lin_num"]

        if nod_num is not None:
            self.node_clicked.emit(nod_num)

    def draw_tree_graph(self, nod_lst):
        max_indent = 0
        for node in nod_lst:
            if node["indent"] > max_indent:
                max_indent = node["indent"]

        right_x, down_y = self.get_coords(len(nod_lst), max_indent + 5)
        left_x, up_y = self.get_coords(-1, 0)
        dx = right_x - left_x
        dy = down_y - up_y
        self.addRect(
            left_x - self.f_width, up_y,
            dx + self.f_width, dy,
            self.gray_pen, self.light_gray_brush
        )
        for i in range(int((len(nod_lst) - 1) / 2 + 1)):
            pos = i * 2
            my_x, my_y = self.get_coords(pos, 0)
            self.addRect(
                left_x, my_y - self.f_height,
                dx - self.f_width, self.f_height * 2,
                self.white_pen, self.white_brush
            )
        for pos, obj2prn in enumerate(nod_lst):
            if len(obj2prn["par_lst"]) > 1:
                my_coord_x ,my_coord_y = self.get_coords(pos, obj2prn["indent"])
                lst2connect = []
                for par_pos, prev in enumerate(nod_lst[0:pos]):
                    if prev["lin_num"] in obj2prn["par_lst"]:
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
                        draw_quadratic_bezier_3_points(
                            self,
                            my_parent_coord_x + self.f_width * 1.6, my_parent_coord_y,
                            my_coord_x, my_parent_coord_y,
                            my_coord_x, my_coord_y - self.f_height * 0.6,
                            self.dark_blue_pen
                        )

        for pos, node in enumerate(nod_lst):
            my_coord_x ,my_coord_y = self.get_coords(pos, node["indent"])
            if pos > 0:
                for inner_row, inner_node in enumerate(nod_lst):
                    if inner_node["lin_num"] == node["low_par_lin_num"]:
                        my_parent_coord_x, my_parent_coord_y = self.get_coords(
                            inner_row, node["parent_indent"]
                        )
                        draw_quadratic_bezier_3_points(
                            self,
                            my_parent_coord_x, my_parent_coord_y + self.f_height * 0.6,
                            my_parent_coord_x, my_coord_y,
                            my_coord_x - self.f_width * 1.6, my_coord_y,
                            self.dark_blue_pen
                        )

        self.lst_nod_pos = []
        for pos, node in enumerate(nod_lst):
            my_coord_x ,my_coord_y = self.get_coords(pos, node["indent"])
            nod_pos = {"lin_num": node["lin_num"], "x_pos": my_coord_x, "y_pos": my_coord_y}
            self.lst_nod_pos.append(nod_pos)
            elip = self.addEllipse(
                my_coord_x - self.f_width * 1.6, my_coord_y - self.f_height * 0.6,
                self.f_width * 3.2, self.f_height * 1.2,
                self.blue_pen, self.cyan_brush
            )
            text = self.addSimpleText(str(node["lin_num"]))
            text.setPos(my_coord_x - self.f_width * 0.7,
                        my_coord_y - self.f_height * 0.5)
            text.setBrush(self.dark_blue_brush)


