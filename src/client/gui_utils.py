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


def draw_quadratic_bezier_3_points(scene_obj,
                          p1x, p1y, p2x, p2y, p3x, p3y,
                          lin_pen = QPen(Qt.blue, 2, Qt.SolidLine)):
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


def draw_quadratic_bezier_auto(scene_obj,
                          p1x, p1y, p3x, p3y):
    if p3x > p1x:
        p2x = p3x
        p2y = p1y

    else:
        p2x = p1x
        p2y = p3y

    draw_quadratic_bezier_3_points(scene_obj,
                          p1x, p1y, p2x, p2y, p3x, p3y)


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
                    draw_quadratic_bezier_auto(
                        self,
                        my_parent_coord_x, my_parent_coord_y + self.f_height / 4,
                        my_coord_x, my_coord_y - self.f_height
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
            elip = self.addEllipse(
                my_coord_x - self.f_width * 1.3, my_coord_y - self.f_height * 0.85,
                self.f_width * 3.2, self.f_height * 1.2,
                self.blue_pen, self.blue_brush
            )

            text = self.addSimpleText(str(node["lin_num"]))
            text.setPos(my_coord_x - self.f_width * 0.5,
                        my_coord_y - self.f_height * 0.8)
            text.setBrush(self.cyan_brush)



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

    def draw_tree_graph(self, nod_lst):
        for pos, node in enumerate(nod_lst):
            my_coord_x ,my_coord_y = self.get_coords(pos, node.indent)
            elip = self.addEllipse(
                my_coord_x - self.f_width * 1.3, my_coord_y - self.f_height * 0.85,
                self.f_width * 3.2, self.f_height * 1.2,
                self.blue_pen, self.blue_brush
            )

            text = self.addSimpleText(str(node.lin_num))
            text.setPos(my_coord_x - self.f_width * 0.5,
                        my_coord_y - self.f_height * 0.8)
            text.setBrush(self.cyan_brush)

            if pos > 0:
                my_parent_coord_x, my_parent_coord_y = self.get_coords(pos, node.parent_indent)

                self.addLine(
                    my_parent_coord_x, my_parent_coord_y,
                    my_coord_x, my_coord_y, self.blue_pen
                )

        copied = '''

        for pos, obj2prn in enumerate(self.dat_lst):
            if pos > 0:
                if obj2prn.parent_indent < self.dat_lst[pos - 1].parent_indent:
                    for up_pos in range(pos - 1, 0, -1):
                        pos_in_str = obj2prn.parent_indent * len(self.ind_spc) + 5
                        left_side = self.dat_lst[up_pos].stp_prn[0:pos_in_str]
                        right_side = self.dat_lst[up_pos].stp_prn[pos_in_str + 1 :]
                        if self.dat_lst[up_pos].parent_indent > obj2prn.parent_indent:
                            self.dat_lst[up_pos].stp_prn = left_side + "|" + right_side

                        else:
                            break

            lng = len(self.ind_spc) * self.max_indent + 12
            lng_lft = lng - len(obj2prn.stp_prn)
            str_here = lng_lft * " "
            obj2prn.stp_prn += str_here + " | " + obj2prn.str_cmd

        for pos, obj2prn in enumerate(self.dat_lst):
            if len(obj2prn.par_lst) > 1:
                lst2connect = []
                for par_pos, prev in enumerate(self.dat_lst[0:pos]):
                    if prev.lin_num in obj2prn.par_lst:
                        lst2connect.append(par_pos)

                lst2connect.remove(max(lst2connect))
                inde4times = obj2prn.indent * 4

                for raw_pos in range(min(lst2connect) + 1, pos, 1):
                    loc_lin_str = self.dat_lst[raw_pos].stp_prn
                    left_side = loc_lin_str[0:inde4times + 5]
                    right_side = loc_lin_str[inde4times + 6:]
                    self.dat_lst[raw_pos].stp_prn = left_side + ":" + right_side

                for up_lin in lst2connect:
                    loc_lin_str = self.dat_lst[up_lin].stp_prn
                    pos_left = self.dat_lst[up_lin].indent * 4 + 7
                    pos_right = inde4times + 6
                    mid_lin = ""
                    for loc_char in loc_lin_str[pos_left:pos_right - 1]:
                        if loc_char == "\\":
                            mid_lin += "\\"

                        else:
                            mid_lin += "`"

                    mid_lin += "\\"

                    left_side = loc_lin_str[0:pos_left]
                    right_side = loc_lin_str[pos_right:]
                    self.dat_lst[up_lin].stp_prn = left_side + mid_lin + right_side

                obj2prn.stp_prn += ",  parents:" + str(obj2prn.par_lst)

        for prn_str in self.dat_lst:
            self.lst_out.append(prn_str.stp_prn)

        self.lst_out.append("---------------------" + self.max_indent * "-" * len(self.ind_spc))


        '''

