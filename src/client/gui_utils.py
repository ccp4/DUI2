
import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *


nod_lst = [
{"lin_num": 0, "status": "Succeeded", "cmd2show": ["Root"], "child_node_lst": [1, 2, 3, 19, 20], "parent_node_lst": []},
{"lin_num": 1, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [4], "parent_node_lst": [0]},
{"lin_num": 2, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [5], "parent_node_lst": [0]},
{"lin_num": 3, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [6], "parent_node_lst": [0]},
{"lin_num": 4, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [7, 10, 11, 12], "parent_node_lst": [1]},
{"lin_num": 5, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [8, 13, 14], "parent_node_lst": [2]},
{"lin_num": 6, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [9, 15], "parent_node_lst": [3]},
{"lin_num": 7, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [4]},
{"lin_num": 8, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [5]},
{"lin_num": 9, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [6]},
{"lin_num": 10, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [4]},
{"lin_num": 11, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [4]},
{"lin_num": 12, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [4]},
{"lin_num": 13, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [5]},
{"lin_num": 14, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [5]},
{"lin_num": 15, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [16, 17, 18], "parent_node_lst": [6]},
{"lin_num": 16, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [7, 10, 8, 13, 15]},
{"lin_num": 17, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [7, 10, 8, 13, 15]},
{"lin_num": 18, "status": "Succeeded", "cmd2show": ["ls"], "child_node_lst": [], "parent_node_lst": [15, 13, 8, 10, 7]},
{"lin_num": 19, "status": "Failed", "cmd2show": ["0", "ls"], "child_node_lst": [], "parent_node_lst": [0]},
{"lin_num": 20, "status": "Ready", "cmd2show": ["None"], "child_node_lst": [], "parent_node_lst": [0]}
]

def add_indent(nod_lst):
    for node in nod_lst:
        node["indent"] = 0

    for pos, node in enumerate(nod_lst):
        child_indent = node["indent"]
        for inner_node in nod_lst:
            if inner_node["lin_num"] in node["child_node_lst"]:
                inner_node["indent"] = child_indent
                child_indent +=1

        if len(node["parent_node_lst"]) > 1:
            indent_lst = []
            for inner_node in nod_lst:
                if inner_node["lin_num"] in node["parent_node_lst"]:
                    indent_lst.append(inner_node["indent"])

            indent_lst.sort()
            node["indent"] = indent_lst[0]

    #for node in nod_lst:
    #    print(node)

    return nod_lst

def draw_bezier(scene_in, p1x, p1y, p4x, p4y):

    p2x = p1x
    p2y = (p1y + p4y) / 2.0

    p3x = p4x
    p3y = (p1y + p4y) / 2.0

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

def get_coords(row, col):
    return col * 24 + 20 + row * 5, row  * 25 + 10

class MainObject(QObject):
    def __init__(self, parent = None):
        super(MainObject, self).__init__(parent)

        self.window = QtUiTools.QUiLoader().load("tree_test.ui")

        self.window.ButtonSelect.clicked.connect(self.on_select)
        self.window.ButtonClear.clicked.connect(self.on_clear)
        self.window.ButtonMkChild.clicked.connect(self.on_make)

        self.window.show()

    def draw_graph(self, nod_lst):
        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, 350, 600)

        for node in nod_lst:
            str2prn = "     " * node["indent"] + "(" + str(node["lin_num"]) + ")"
            print(str2prn)

        row_size = 24
        for row, node in enumerate(nod_lst):
            my_coord_x ,my_coord_y = get_coords(row, node["indent"])
            for inner_row, inner_node in enumerate(nod_lst):
                if inner_node["lin_num"] in node["parent_node_lst"]:
                    my_parent_coord_x, my_parent_coord_y = get_coords(inner_row, inner_node["indent"])
                    draw_bezier(scene, my_parent_coord_x, my_parent_coord_y, my_coord_x, my_coord_y)

            text = scene.addText(str(node["lin_num"]))
            text.setPos(my_coord_x, my_coord_y)

        self.window.graphicsView.setScene(scene)

    def on_select(self):
        print("on_select")

    def on_clear(self):
        print("on_clear")

    def on_make(self):
        print("on_make")


if __name__ == "__main__":

    nod_lst = add_indent(nod_lst)


    app = QApplication(sys.argv)
    m_obj = MainObject()
    m_obj.draw_graph(nod_lst)
    sys.exit(app.exec_())


old_graph = '''
status: (R)eady  (B)usy  (F)ailed  (S)ucceeded
 |
 |  line number
 |   |
 |   |    command --->
--------------------------
 S   \_(0)                                   | Root
 S       \_(1)                               | ls
 S       |   \_(4)                           | ls
 S       |       \_(7) ``\```\```\           | ls
 S       |       \_(10)``\```\```\           | ls
 S       |       \_(11)  :   :   :           | ls
 S       |       \_(12)  :   :   :           | ls
 S       \_(2)           :   :   :           | ls
 S       |   \_(5)       :   :   :           | ls
 S       |       \_(8) ``\```\```\           | ls
 S       |       \_(13)``\```\```\           | ls
 S       |       \_(14)  :   :   :           | ls
 S       \_(3)           :   :   :           | ls
 S       |   \_(6)       :   :   :           | ls
 S       |       \_(9)   :   :   :           | ls
 S       |       \_(15)  :   :   :           | ls
 S       |           \_(16)  :   :           | ls,  parents:[7, 10, 8, 13, 15]
 S       |           \_____(17)  :           | ls,  parents:[7, 10, 8, 13, 15]
 S       |           \_________(18)          | ls,  parents:[15, 13, 8, 10, 7]
 F       \_(19)                              | 0
 R       \_(20)                              | None
----------------------------------------------------
'''
