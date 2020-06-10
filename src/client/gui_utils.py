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

def draw_bezier(scene_in, p1x, p1y, p4x, p4y):
    p2x = p1x
    p2y = (p1y + p4y) / 2.0
    p3x = p4x
    p3y = (p1y + p4y) / 2.0
    #p3y = p1y - (p4y - p1y) / 4.0

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
            scene_in.addLine(x, y, nx, ny)

        x = nx
        y = ny

    x_arr_siz = (p4x - p1x) / 30.0
    y_arr_siz = (p4y - p1y) / 20.0
    scene_in.addLine(
        p4x, p4y,
        p4x + x_arr_siz, p4y - y_arr_siz
    )
    scene_in.addLine(
        p4x, p4y,
        p4x - x_arr_siz, p4y - y_arr_siz
    )


def get_coords(row, col, ft_ht, ft_wd):
    return col * ft_wd * 2 + row * ft_wd / 4, row  * ft_ht * 2


def draw_inner_graph(scene_in, nod_lst):
    fm = QFontMetrics(scene_in.font())
    ft_wd = fm.width("0")
    ft_ht = fm.height()
    red_pen = QPen(Qt.red)
    grayBrush = QBrush(Qt.gray, bs=Qt.SolidPattern)

    lst_w_indent = add_indent(nod_lst)
    for node in lst_w_indent:
        str2prn = "     " * node["indent"] + "(" + str(node["lin_num"]) + ")"
        print(str2prn)

    for row, node in enumerate(lst_w_indent):
        my_coord_x ,my_coord_y = get_coords(row, node["indent"], ft_ht, ft_wd)
        for inner_row, inner_node in enumerate(lst_w_indent):
            if inner_node["lin_num"] in node["parent_node_lst"]:
                my_parent_coord_x, my_parent_coord_y = get_coords(
                    inner_row, inner_node["indent"],
                    ft_ht, ft_wd
                )
                draw_bezier(
                    scene_in,
                    my_parent_coord_x, my_parent_coord_y + ft_ht / 4,
                    my_coord_x, my_coord_y - ft_ht
                )

    for row, node in enumerate(lst_w_indent):
        my_coord_x ,my_coord_y = get_coords(row, node["indent"], ft_ht, ft_wd)
        text = scene_in.addEllipse(
            my_coord_x - ft_wd * 1.3, my_coord_y - ft_ht * 0.85,
            ft_wd * 3.2, ft_ht * 1.2,
            red_pen, grayBrush
        )

        text = scene_in.addText(str(node["lin_num"]))
        text.setPos(my_coord_x - ft_wd, my_coord_y - ft_ht)

