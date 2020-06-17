import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

def add_indent(nod_lst):
    for node in nod_lst:
        node["indent"] = 0

    for node in nod_lst:
        if len(node["parent_node_lst"]) > 1:
            indent_lst = []
            for inner_node in nod_lst:
                if inner_node["lin_num"] in node["parent_node_lst"]:
                    indent_lst.append(inner_node["indent"])

            indent_lst.sort()
            node["indent"] = indent_lst[0]

        child_indent = node["indent"]
        for inner_node in nod_lst:
            if inner_node["lin_num"] in node["child_node_lst"]:
                inner_node["indent"] = child_indent
                child_indent +=1

    return nod_lst


def draw_cubic_bezier(scene_obj, p1x, p1y, p4x, p4y,
                      lin_pen = Qt.blue):

    p2x = p1x
    p2y = (p1y + p4y) / 2.0
    p3x = p4x
    p3y = p2y

    n_points = 25

    dx12 = (p2x - p1x) / n_points
    dx23 = (p3x - p2x) / n_points
    dx34 = (p4x - p3x) / n_points

    dy12 = (p2y - p1y) / n_points
    dy23 = (p3y - p2y) / n_points
    dy34 = (p4y - p3y) / n_points

    for pos in range(n_points + 1):
        x1 = p1x + dx12 * float(pos)
        y1 = p1y + dy12 * float(pos)
        x2 = p2x + dx23 * float(pos)
        y2 = p2y + dy23 * float(pos)
        x3 = p3x + dx34 * float(pos)
        y3 = p3y + dy34 * float(pos)
        dx1 = (x2 - x1) / n_points
        dy1 = (y2 - y1) / n_points
        dx2 = (x3 - x2) / n_points
        dy2 = (y3 - y2) / n_points
        gx1 = x1 + dx1 * float(pos)
        gy1 = y1 + dy1 * float(pos)
        gx2 = x2 + dx2 * float(pos)
        gy2 = y2 + dy2 * float(pos)
        dx = (gx2 - gx1) / n_points
        dy = (gy2 - gy1) / n_points
        nx = gx1 + dx * float(pos)
        ny = gy1 + dy * float(pos)

        if pos > 0:
            scene_obj.addLine(x, y, nx, ny, lin_pen)

        x = nx
        y = ny

def draw_quadratic_bezier(scene_obj,
                          p1x, p1y, p3x, p3y,
                          lin_pen = Qt.blue):
    if p3x > p1x:
        p2x = p3x
        p2y = p1y

    else:
        p2x = p1x
        p2y = p3y

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


class TreeGitScene(QGraphicsScene):
    def __init__(self, parent = None):
        super(TreeGitScene, self).__init__(parent)
        fm = QFontMetrics(self.font())
        self.f_width = fm.width("0")
        self.f_height = fm.height()

        self.blue_brush = QBrush(Qt.blue, bs=Qt.SolidPattern)
        self.dark_blue_brush = QBrush(Qt.darkBlue, bs=Qt.SolidPattern)
        self.cyan_brush = QBrush(Qt.cyan, bs=Qt.SolidPattern)
        self.blue_pen = QPen(Qt.blue, 2, Qt.SolidLine)
        self.dark_blue_pen = QPen(Qt.darkBlue, 2, Qt.SolidLine)
        self.cyan_pen = QPen(Qt.cyan, 2, Qt.SolidLine)

    def get_coords(self, row, col):
        return col * self.f_width * 3, row  * self.f_height * 2

    def mouseMoveEvent(self, event):
        print("mouseMoveEvent event.scenePos",
              event.scenePos().x(),
              event.scenePos().y())

    def focusInEvent(self, event):
        print("focusInEvent", event)

    def draw_inner_graph(self, nod_lst):

        lst_w_indent = add_indent(nod_lst)
        for node in lst_w_indent:
            str2prn = "     " * node["indent"] + "(" + str(node["lin_num"]) + ")"
            print(str2prn)

        for row, node in enumerate(lst_w_indent):
            my_coord_x ,my_coord_y = self.get_coords(row, node["indent"])
            for inner_row, inner_node in enumerate(lst_w_indent):
                if inner_node["lin_num"] in node["parent_node_lst"]:
                    my_parent_coord_x, my_parent_coord_y = self.get_coords(
                        inner_row, inner_node["indent"]
                    )

                    draw_quadratic_bezier(
                        self,
                        my_parent_coord_x, my_parent_coord_y + self.f_height / 4,
                        my_coord_x, my_coord_y - self.f_height,
                        self.blue_pen
                    )
                    '''
                    draw_cubic_bezier(
                        self,
                        my_parent_coord_x, my_parent_coord_y + self.f_height / 4,
                        my_coord_x, my_coord_y - self.f_height,
                        self.blue_pen
                    )
                    '''

        for row, node in enumerate(lst_w_indent):
            my_coord_x ,my_coord_y = self.get_coords(row, node["indent"])
            text = self.addEllipse(
                my_coord_x - self.f_width * 1.3, my_coord_y - self.f_height * 0.85,
                self.f_width * 3.2, self.f_height * 1.2,
                self.blue_pen, self.blue_brush
            )

            text = self.addSimpleText(str(node["lin_num"]))
            text.setPos(my_coord_x - self.f_width * 0.5,
                        my_coord_y - self.f_height * 0.8)
            text.setBrush(self.cyan_brush)


##################################################################################################

##################################################################################################

##################################################################################################


class TreeDirScene(QGraphicsScene):
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

    def get_coords(self, row, col):
        return col * self.f_width * 3, row  * self.f_height * 2

    def mouseMoveEvent(self, event):
        print("mouseMoveEvent event.scenePos",
              event.scenePos().x(),
              event.scenePos().y())

    def focusInEvent(self, event):
        print("focusInEvent", event)

    def draw_inner_graph(self, nod_lst):

        lst_w_indent = add_indent(nod_lst)
        for node in lst_w_indent:
            str2prn = "     " * node["indent"] + "(" + str(node["lin_num"]) + ")"
            print(str2prn)

        for row, node in enumerate(lst_w_indent):
            my_coord_x ,my_coord_y = self.get_coords(row, node["indent"])
            for inner_row, inner_node in enumerate(lst_w_indent):
                if inner_node["lin_num"] in node["parent_node_lst"]:
                    my_parent_coord_x, my_parent_coord_y = self.get_coords(
                        inner_row, inner_node["indent"]
                    )

                    draw_quadratic_bezier(
                        self,
                        my_parent_coord_x, my_parent_coord_y + self.f_height / 4,
                        my_coord_x, my_coord_y - self.f_height,
                        self.blue_pen
                    )
                    '''
                    draw_cubic_bezier(
                        self,
                        my_parent_coord_x, my_parent_coord_y + self.f_height / 4,
                        my_coord_x, my_coord_y - self.f_height,
                        self.blue_pen
                    )
                    '''

        for row, node in enumerate(lst_w_indent):
            my_coord_x ,my_coord_y = self.get_coords(row, node["indent"])
            text = self.addEllipse(
                my_coord_x - self.f_width * 1.3, my_coord_y - self.f_height * 0.85,
                self.f_width * 3.2, self.f_height * 1.2,
                self.blue_pen, self.blue_brush
            )

            text = self.addSimpleText(str(node["lin_num"]))
            text.setPos(my_coord_x - self.f_width * 0.5,
                        my_coord_y - self.f_height * 0.8)
            text.setBrush(self.cyan_brush)
