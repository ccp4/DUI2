"""
DUI2's re-index table widget

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

import json
import logging
import sys
import os

from PySide2.QtCore import *
from PySide2.QtWidgets import *
#from PySide2 import QtUiTools
from PySide2.QtGui import *

def choice_if_decimal(num_in):

    str_f = "{:6.2f}".format(num_in)
    if str_f[-3:] == ".00":
        str_out = str_f[0:-3]

    else:
        str_out = str_f

    return str_out

def ops_list_from_json(json_data = None):
    if json_data is None:
        return None

    lst_ops = []
    for key, value in json_data.items():
        recommended_str = "  "
        #print("outer key:", key)
        #print("outer dict:", value)
        for inner_key in value:
            if inner_key == "rmsd":
                rmsd_val = value["rmsd"]
                rmsd_str = " {:7.2}".format(rmsd_val)

            elif inner_key == "min_cc":
                try:
                    min_cc_val = value["min_cc"]
                    min_cc_str = " {:7.2}".format(min_cc_val)

                except TypeError:
                    min_cc_str = "    - "

                # TODO the format here is not always giving the same with

                # TODO think about someting like:
                #   "aa = list(round(i, ndigits=6) for i in aa)"

            elif inner_key == "max_cc":
                max_cc_val = value["max_cc"]
                try:
                    max_cc_str = " {:7.2}".format(max_cc_val)

                except TypeError:
                    max_cc_str = "    - "

                # print "__________________________________________
                # type(max_cc_val) =", type(max_cc_val)
                # TODO the format here is not always giving the same with

                # TODO think about someting like:
                #   "aa = list(round(i, ndigits=6) for i in aa)"

            elif inner_key == "bravais":
                bravais_val = value["bravais"]
                bravais_str = " " + str(bravais_val).ljust(3)

            elif inner_key == "max_angular_difference":
                angular_diff_val = value["max_angular_difference"]
                angular_diff_str = " {:7.2} ".format(angular_diff_val)

            elif inner_key == "correlation_coefficients":
                # corr_coeff_val = value["correlation_coefficients"]
                # corr_coeff_str = str(corr_coeff_val)
                pass

            elif inner_key == "unit_cell":
                unit_cell_val = value["unit_cell"]
                uc_d = unit_cell_val[0:3]
                uc_a = unit_cell_val[3:6]
                unit_cell_str_a = "{:6.1f}".format(uc_d[0])
                unit_cell_str_b = "{:6.1f}".format(uc_d[1])
                unit_cell_str_c = "{:6.1f}".format(uc_d[2])

                unit_cell_str_apl = choice_if_decimal(uc_a[0])
                unit_cell_str_bet = choice_if_decimal(uc_a[1])
                unit_cell_str_gam = choice_if_decimal(uc_a[2])

            elif inner_key == "recommended":
                recommended_val = value["recommended"]
                if recommended_val:
                    recommended_str = " Y"
                else:
                    recommended_str = " N"

            else:
                #print("Fell off end of key list with inner_key=", inner_key)
                pass

        single_lin_lst = [
            int(key),
            angular_diff_str,
            rmsd_str,
            min_cc_str,
            max_cc_str,
            bravais_str,
            unit_cell_str_a,
            unit_cell_str_b,
            unit_cell_str_c,
            unit_cell_str_apl,
            unit_cell_str_bet,
            unit_cell_str_gam,
            recommended_str,
        ]

        lst_ops.append(single_lin_lst)

    sorted_lst_ops = sorted(lst_ops)
    return sorted_lst_ops


class ReindexTable(QTableWidget):
    opt_signal = Signal(int)

    def __init__(self, parent = None):
        super(ReindexTable, self).__init__(parent)

        self.cellClicked.connect(self.opt_clicked)

        self.v_sliderBar = self.verticalScrollBar()
        self.h_sliderBar = self.horizontalScrollBar()

        #self.tmp_sel = None

        sys_font = QFont()
        self.sys_font_point_size = sys_font.pointSize()
        # self.show()

    def opt_clicked(self, row, col):
        print("Solution clicked = ", row + 1)
        v_sliderValue = self.v_sliderBar.value()
        h_sliderValue = self.h_sliderBar.value()

        self.del_opts_lst()
        self.add_opts_lst(lst_labels=self.list_labl, selected_pos=row)

        self.v_sliderBar.setValue(v_sliderValue)
        self.h_sliderBar.setValue(h_sliderValue)

        self.opt_pick(row)

    def ok_clicked(self):
        self.opt_pick(self.tmp_sel)

    def opt_pick(self, row):
        '''
        if self.tmp_sel == row:
            print("\n selecting opt: ", row + 1, "\n")
        '''
        self.opt_signal.emit(row + 1)

        self.tmp_sel = row

    def find_best_solu(self):
        bst_sol = -1
        for row, row_cont in enumerate(self.list_labl):
            if row_cont[self.rec_col] == " Y":
                if row > bst_sol:
                    bst_sol = row

        print("bst_sol = ", bst_sol)

        return bst_sol

    def add_opts_lst(
        self, lst_labels = None, json_data = None, selected_pos = None
    ):

        if lst_labels is None:
            self.list_labl = ops_list_from_json(json_data)

        n_row = len(self.list_labl)
        print("n_row =", n_row)
        n_col = len(self.list_labl[0])
        print("n_col =", n_col)

        self.setRowCount(n_row)
        self.setColumnCount(n_col - 1)

        alpha_str = " " + u"\u03B1" + " "
        beta_str = " " + u"\u03B2" + " "
        gamma_str = " " + u"\u03B3" + " "

        low_delta_str = u"\u03B4"
        delta_max_str = "max " + low_delta_str

        header_label_lst = [
            delta_max_str,
            "rmsd",
            " min cc",
            "max cc",
            "latt",
            "  a ",
            "  b ",
            "  c ",
            alpha_str,
            beta_str,
            gamma_str,
            "Ok",
        ]

        self.setHorizontalHeaderLabels(header_label_lst)

        self.rec_col = None

        for row, row_cont in enumerate(self.list_labl):
            for col, col_cont in enumerate(row_cont[1:]):
                item = QTableWidgetItem(col_cont)
                item.setFlags(Qt.ItemIsEnabled)
                if col_cont == " Y":
                    item.setBackground(QColor(Qt.green).lighter())
                    item.setForeground(Qt.black)

                    self.rec_col = col + 1

                elif col_cont == " N":
                    item.setBackground(QColor(Qt.red).lighter())
                    item.setForeground(Qt.black)

                else:
                    if row == selected_pos:
                        item.setBackground(Qt.blue)
                        item.setForeground(Qt.yellow)

                    else:
                        if float(row) / 2.0 == int(float(row) / 2.0):
                            item.setBackground(QColor(50, 50, 50, 50))

                        else:
                            item.setBackground(Qt.white)

                        item.setForeground(Qt.black)

                item.setFont(
                    QFont("Monospace", self.sys_font_point_size)
                )  # , QFont.Bold))
                self.setItem(row, col, item)

        self.resizeColumnsToContents()

    def update_all_pars(self, tup_lst_pars):
        print("\n (ReindexTable) \n time to update par to:", tup_lst_pars, "\n")

    def reset_pars(self):
        print("\n reset_pars(ReindexTable) \n")

    def del_opts_lst(self):

        print("del_opts_lst")
        self.clear()
        self.setRowCount(1)
        self.setColumnCount(1)

def get_label_from_str_list(log_data):

        for num, single_line in enumerate(log_data):
            if single_line[:6] == "Chiral":
                ini_num = num - 1

            if single_line[:6] == "+-----":
                end_num = num - 1
                break

        print("ini_num =", ini_num)
        print("end_num =", end_num)

        lst_str = log_data[ini_num:end_num]
        full_label_str = ""
        for label_line in lst_str:
            full_label_str += label_line

        return full_label_str


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #full_json_path = "/scratch/dui_tst/X4_wide/dui_files/bravais_summary.json"
        full_json_path = "/home/lui-temp/xrd_data/tst_area/run4/bravais_summary.json"
        full_log_path = "/home/lui-temp/xrd_data/tst_area/run4/out.log"

        with open(full_json_path) as json_file:
            json_data = json.load(json_file)

        lof_file = open(full_log_path, "r")
        log_data = lof_file.readlines()
        lof_file.close()

        full_label_str = get_label_from_str_list(log_data)

        my_inner_table = ReindexTable()
        my_inner_table.add_opts_lst(json_data = json_data)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(full_label_str))
        vbox.addWidget(my_inner_table)
        vbox.addWidget(QLabel("\n some clicking suggestion here \n"))

        self.main_widget = QWidget(self)
        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWidget = MainWindow()
    myWidget.show()
    app.exec_()




