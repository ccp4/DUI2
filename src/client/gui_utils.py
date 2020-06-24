import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

def draw_quadratic_bezier_3_points(scene_obj,
                          p1x, p1y, p2x, p2y, p3x, p3y,
                          lin_pen):
    n_points = 25

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

        x = gx1
        y = gy1


class TreeDirScene(QGraphicsScene):

    node_clicked = Signal(int)

    def __init__(self, parent = None):
        super(TreeDirScene, self).__init__(parent)
        fm = QFontMetrics(self.font())
        self.f_width = fm.width("0")
        self.f_height = fm.height()

        self.blue_brush = QBrush(Qt.blue, bs=Qt.SolidPattern)
        self.dark_blue_brush = QBrush(Qt.darkBlue, bs=Qt.SolidPattern)
        self.cyan_brush = QBrush(Qt.cyan, bs=Qt.SolidPattern)
        self.blue_pen = QPen(Qt.blue, 2, Qt.SolidLine)
        self.dark_blue_pen = QPen(Qt.darkBlue, 2, Qt.SolidLine)
        self.cyan_pen = QPen(Qt.cyan, 2, Qt.SolidLine)

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
        for pos, obj2prn in enumerate(nod_lst):
            if len(obj2prn.par_lst) > 1:
                my_coord_x ,my_coord_y = self.get_coords(pos, obj2prn.indent)
                lst2connect = []
                for par_pos, prev in enumerate(nod_lst[0:pos]):
                    if prev.lin_num in obj2prn.par_lst:
                        lst2connect.append((par_pos, prev.indent))

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
                            self.blue_pen
                        )

        for pos, node in enumerate(nod_lst):
            my_coord_x ,my_coord_y = self.get_coords(pos, node.indent)
            if pos > 0:
                for inner_row, inner_node in enumerate(nod_lst):
                    if inner_node.lin_num == node.low_par_lin_num:
                        my_parent_coord_x, my_parent_coord_y = self.get_coords(
                            inner_row, node.parent_indent
                        )
                        draw_quadratic_bezier_3_points(
                            self,
                            my_parent_coord_x, my_parent_coord_y + self.f_height * 0.6,
                            my_parent_coord_x, my_coord_y,
                            my_coord_x - self.f_width * 1.6, my_coord_y,
                            self.blue_pen
                        )

        self.lst_nod_pos = []
        for pos, node in enumerate(nod_lst):
            my_coord_x ,my_coord_y = self.get_coords(pos, node.indent)
            nod_pos = {"lin_num": node.lin_num, "x_pos": my_coord_x, "y_pos": my_coord_y}
            self.lst_nod_pos.append(nod_pos)
            elip = self.addEllipse(
                my_coord_x - self.f_width * 1.6, my_coord_y - self.f_height * 0.6,
                self.f_width * 3.2, self.f_height * 1.2,
                self.blue_pen, self.cyan_brush
            )
            text = self.addSimpleText(str(node.lin_num))
            text.setPos(my_coord_x - self.f_width * 0.7,
                        my_coord_y - self.f_height * 0.5)
            text.setBrush(self.dark_blue_brush)


