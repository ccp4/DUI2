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

import os, sys
import time, json
import requests

try:
    from shared_modules import format_utils

except ModuleNotFoundError:
    '''
    This trick to import the format_utils module can be
    removed once the project gets properly packaged
    '''
    comm_path = os.path.abspath(__file__)[0:-21] + "shared_modules"
    print("comm_path: ", comm_path)
    sys.path.insert(1, comm_path)
    import format_utils

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from gui_utils import TreeDirScene, AdvancedParameters, widgets_defs

from reindex_table import ReindexTable

from simpler_param_widgets import ImportTmpWidg as ImportWidget
from simpler_param_widgets import (
    FindspotsSimplerParameterTab, IndexSimplerParamTab,
    RefineBravaiSimplerParamTab, RefineSimplerParamTab,
    IntegrateSimplerParamTab, SymmetrySimplerParamTab,
    ScaleSimplerParamTab, CombineExperimentSimplerParamTab
)

uni_url = 'http://localhost:8080/'


def build_advanced_params_widget(cmd_str):
    cmd = {"nod_lst":"", "cmd_lst":[cmd_str]}
    lst_params = json_data_request(uni_url, cmd)
    lin_lst = format_utils.param_tree_2_lineal(lst_params)
    par_def = lin_lst()
    advanced_parameters = AdvancedParameters()
    advanced_parameters.build_pars(par_def)
    return advanced_parameters

def copy_lst_nodes(old_lst_nodes):
    new_lst = []
    for old_node in old_lst_nodes:
        cp_new_node = {
            'lin_num': int(old_node["lin_num"]),
            'status': str(old_node["status"]),
            'cmd2show': list(old_node["cmd2show"]),
            'child_node_lst': list(old_node["child_node_lst"]),
            'parent_node_lst': list(old_node["parent_node_lst"])
        }
        new_lst.append(cp_new_node)

    return new_lst

def json_data_request(url, cmd):
    try:
        req_get = requests.get(url, stream = True, params = cmd)
        str_lst = []
        line_str = ''
        while True:
            tmp_dat = req_get.raw.read(1)
            single_char = str(tmp_dat.decode('utf-8'))
            line_str += single_char
            if single_char == '\n':
                str_lst.append(line_str[:-1])
                line_str = ''

            elif line_str[-7:] == '/*EOF*/':
                print('>>  /*EOF*/  <<')
                break

        json_out = json.loads(str_lst[0])

    except requests.exceptions.RequestException:
        print("\n requests.exceptions.RequestException \n")
        json_out = None

    return json_out


class Run_n_Output(QThread):
    new_line_out = Signal(str, int)
    first_line = Signal(int)
    def __init__(self, request):
        super(Run_n_Output, self).__init__()
        self.request = request
        self.lin_num = None

    def run(self):
        line_str = ''
        not_yet_read = True
        while True:
            tmp_dat = self.request.raw.read(1)
            single_char = str(tmp_dat.decode('utf-8'))
            line_str += single_char
            if single_char == '\n':
                if not_yet_read:
                    not_yet_read = False
                    nod_lin_num = int(line_str.split("=")[1])
                    self.lin_num = nod_lin_num
                    print("\n QThread.lin_num =", self.lin_num)
                    self.first_line.emit(self.lin_num)

                else:
                    self.new_line_out.emit(line_str, self.lin_num)

                line_str = ''

            elif line_str[-7:] == '/*EOF*/':
                #TODO: consider a different Signal to say finished
                print('>>  /*EOF*/  <<')
                self.new_line_out.emit(' \n /*EOF*/ \n', self.lin_num)
                break

            self.usleep(1)

class MainObject(QObject):
    def __init__(self, parent = None):
        super(MainObject, self).__init__(parent)
        ui_path = os.path.dirname(os.path.abspath(__file__))
        ui_path += os.sep + "client.ui"
        self.window = QtUiTools.QUiLoader().load(ui_path)

        try:
            imp_widg = ImportWidget()
            imp_widg.item_changed.connect(self.item_param_changed)
            self.window.ImportScrollArea.setWidget(imp_widg)

            find_simpl_widg = FindspotsSimplerParameterTab()
            find_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.FindspotsSimplerScrollArea.setWidget(find_simpl_widg)
            fd_advanced_parameters = build_advanced_params_widget("find_spots_params")
            fd_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.FindspotsAdvancedScrollArea.setWidget(fd_advanced_parameters)

            index_simpl_widg = IndexSimplerParamTab()
            index_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.IndexSimplerScrollArea.setWidget(index_simpl_widg)
            id_advanced_parameters = build_advanced_params_widget("index_params")
            id_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.IndexAdvancedScrollArea.setWidget(id_advanced_parameters)

            refi_brv_simpl_widg = RefineBravaiSimplerParamTab()
            refi_brv_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.RefineBravaiSimplerScrollArea.setWidget(refi_brv_simpl_widg)
            rb_advanced_parameters = build_advanced_params_widget("refine_bravais_settings_params")
            rb_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.RefineBravaiAdvancedScrollArea.setWidget(rb_advanced_parameters)

            full_json_path = "/scratch/dui_tst/X4_wide/dui_files/bravais_summary.json"
            r_index_widg = ReindexTable()
            r_index_widg.add_opts_lst(json_path=full_json_path)
            self.window.ReindexTableScrollArea.setWidget(r_index_widg)

            ref_simpl_widg = RefineSimplerParamTab()
            ref_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.RefineSimplerScrollArea.setWidget(ref_simpl_widg)
            rf_advanced_parameters = build_advanced_params_widget("refine_params")
            rf_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.RefineAdvancedScrollArea.setWidget(rf_advanced_parameters)

            integr_simpl_widg = IntegrateSimplerParamTab()
            integr_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.IntegrateSimplerScrollArea.setWidget(integr_simpl_widg)
            it_advanced_parameters = build_advanced_params_widget("integrate_params")
            it_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.IntegrateAdvancedScrollArea.setWidget(it_advanced_parameters)

            sym_simpl_widg = SymmetrySimplerParamTab()
            sym_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.SymmetrySimplerScrollArea.setWidget(sym_simpl_widg)
            sm_advanced_parameters = build_advanced_params_widget("symmetry_params")
            sm_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.SymmetryAdvancedScrollArea.setWidget(sm_advanced_parameters)

            scale_simpl_widg = ScaleSimplerParamTab()
            scale_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.ScaleSimplerScrollArea.setWidget(scale_simpl_widg)
            sc_advanced_parameters = build_advanced_params_widget("scale_params")
            sc_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.ScaleAdvancedScrollArea.setWidget(sc_advanced_parameters)

            comb_simpl_widg = CombineExperimentSimplerParamTab()
            comb_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.CombineSimplerScrollArea.setWidget(comb_simpl_widg)
            ce_advanced_parameters = build_advanced_params_widget("combine_experiments_params")
            ce_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.CombineAdvancedScrollArea.setWidget(ce_advanced_parameters)

        except TypeError:
            print("failed to connect to server")
            sys.exit()

        dummy_ls_widg = self.window.TmpLsPage

        self.param_widgets = widgets_defs

        self.param_widgets["import"]["simple"] = imp_widg
        self.param_widgets["import"]["advanced"] = None
        self.param_widgets["import"]["main_page"] = self.window.ImportPage

        self.param_widgets["find_spots"]["simple"] = find_simpl_widg
        self.param_widgets["find_spots"]["advanced"] = fd_advanced_parameters
        self.param_widgets["find_spots"]["main_page"] = self.window.FindspotsPage

        self.param_widgets["index"]["simple"] = index_simpl_widg
        self.param_widgets["index"]["advanced"] = id_advanced_parameters
        self.param_widgets["index"]["main_page"] = self.window.IndexPage

        self.param_widgets["refine_bravais_settings"]["simple"] = refi_brv_simpl_widg
        self.param_widgets["refine_bravais_settings"]["advanced"] = rb_advanced_parameters
        self.param_widgets["refine_bravais_settings"]["main_page"] = self.window.RefinBrabPage

        self.param_widgets["reindex"]["simple"] = r_index_widg
        self.param_widgets["reindex"]["advanced"] = None
        self.param_widgets["reindex"]["main_page"] = self.window.ReindexPage

        self.param_widgets["refine"]["simple"] = ref_simpl_widg
        self.param_widgets["refine"]["advanced"] = rf_advanced_parameters
        self.param_widgets["refine"]["main_page"] = self.window.RefinePage

        self.param_widgets["integrate"]["simple"] = integr_simpl_widg
        self.param_widgets["integrate"]["advanced"] = it_advanced_parameters
        self.param_widgets["integrate"]["main_page"] = self.window.IntegratePage

        self.param_widgets["symmetry"]["simple"] = sym_simpl_widg
        self.param_widgets["symmetry"]["advanced"] = sm_advanced_parameters
        self.param_widgets["symmetry"]["main_page"] = self.window.SimmetryPage

        self.param_widgets["scale"]["simple"] = scale_simpl_widg
        self.param_widgets["scale"]["advanced"] = sc_advanced_parameters
        self.param_widgets["scale"]["main_page"] = self.window.ScalePage

        self.param_widgets["combine_experiments"]["simple"] = comb_simpl_widg
        self.param_widgets["combine_experiments"]["advanced"] = ce_advanced_parameters
        self.param_widgets["combine_experiments"]["main_page"] = self.window.CombinePage


        self.param_widgets["ls"]["simple"] = comb_simpl_widg
        self.param_widgets["ls"]["advanced"] = None
        self.param_widgets["ls"]["main_page"] = self.window.TmpLsPage


        self.window.incoming_text.setFont(QFont("Monospace"))
        self.tree_obj = format_utils.TreeShow()
        self.tree_scene = TreeDirScene(self)
        self.window.treeView.setScene(self.tree_scene)

        self.window.Next2RunLayout.addWidget(QLabel("                  . . .       "))

        self.current_next_buttons = 0
        self.params2run = []

        self.font_point_size = QFont().pointSize()
        big_f_size = int(self.font_point_size * 1.6)
        big_font = QFont("OldEnglish", pointSize = big_f_size, italic=True)
        self.window.CurrentControlWidgetLabel.setFont(big_font)

        self.tree_scene.node_clicked.connect(self.on_node_click)
        self.window.RetryButton.clicked.connect(self.on_retry)
        self.window.CmdSend2server.clicked.connect(self.request_launch)
        self.window.ReqStopButton.clicked.connect(self.req_stop)
        self.window.Reset2DefaultPushButton.clicked.connect(self.reset_param)
        self.tree_scene.draw_tree_graph([])

        self.current_params_widget = "import"
        self.change_widget(self.current_params_widget)

        self.new_node = None
        self.lst_node_info_out = [] #{"lin_num": int, "log_line_lst": [str]}

        self.current_lin_num = 0
        self.request_display()
        self.local_nod_lst = copy_lst_nodes(self.server_nod_lst)

        self.thrd_lst = []
        self.window.show()

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                else:
                    self.clearLayout(item.layout())

    def on_node_click(self, nod_num):
        self.current_lin_num = nod_num
        try:
            cur_nod = self.server_nod_lst[nod_num]
            self.display_log(nod_num)
            self.window.NumLinLst.setText(str(nod_num))

        except IndexError:
            print("nod_num ", nod_num, "not ran yet")
            cur_nod = self.local_nod_lst[nod_num]
            self.window.incoming_text.clear()
            self.window.incoming_text.insertPlainText("Ready to run ...")
            n_lst_str = ""
            for par_nod_num in cur_nod["parent_node_lst"]:
                n_lst_str += str(par_nod_num) + " "

            n_lst_str = n_lst_str[:-1]
            self.window.NumLinLst.setText(n_lst_str)

        cmd_ini = cur_nod["cmd2show"][0]
        key2find = cmd_ini[6:]

        try:
            self.change_widget(key2find)

        except KeyError:
            print("command widget not there yet")
            return


        self.display()

        to_review_later = '''
        if(
            self.window.CurrentControlWidgetLabel.text() == "combine_experiments"
            or
            self.window.CurrentControlWidgetLabel.text() == "ls"
        ):
            prev_text = str(self.window.NumLinLst.text())
            self.window.NumLinLst.setText(
                str(prev_text + " " + str(nod_num))
            )

        else:
            self.window.NumLinLst.setText(str(nod_num))
        '''
    def add_line(self, new_line, nod_lin_num):
        found_lin_num = False
        for log_node in self.lst_node_info_out:
            if log_node["lin_num"] == nod_lin_num:
                log_node["log_line_lst"].append(new_line[0:-1])
                found_lin_num = True

        if not found_lin_num:
            self.lst_node_info_out.append(
                {
                    "lin_num"       : nod_lin_num,
                    "log_line_lst"  : [new_line]
                }
            )

        if self.current_lin_num == nod_lin_num:
            self.window.incoming_text.moveCursor(QTextCursor.End)
            self.window.incoming_text.insertPlainText(new_line)
            self.window.incoming_text.moveCursor(QTextCursor.End)

    def item_param_changed(self, str_path, str_value):
        print("item paran changed")
        print("str_path, str_value: ", str_path, str_value)
        self.params2run.append(str_path + "=" + str_value)
        str_key = self.current_params_widget
        cmd2run = self.param_widgets[str_key]["main_cmd"]
        for sinlge_param in self.params2run:
            cmd2run = cmd2run + " " + sinlge_param

        print("\n main_cmd = ", cmd2run, "\n")
        self.window.CmdEdit.setText(str(cmd2run))

    def display(self, in_lst_nodes = None):
        old_way = '''
        if in_lst_nodes is None:
            lst_2_draw = self.last_lst_nodes

        else:
            lst_2_draw = in_lst_nodes

        lst_str = self.tree_obj(lst_nod = lst_2_draw)
        lst_2d_dat = self.tree_obj.get_tree_data()
        self.tree_scene.draw_tree_graph(lst_2d_dat, self.current_lin_num)

        if in_lst_nodes is not None:
            self.last_lst_nodes = in_lst_nodes
        '''
        if in_lst_nodes is None:
            self.tree_scene.new_lin_num(self.current_lin_num)

        else:
            lst_str = self.tree_obj(lst_nod = in_lst_nodes)
            lst_2d_dat = self.tree_obj.get_tree_data()
            self.tree_scene.draw_tree_graph(lst_2d_dat, self.current_lin_num)

    def line_n1_in(self, lin_num_in):
        print("new busy node = ", lin_num_in)
        self.request_display()
        self.window.NumLinLst.clear()
        self.window.NumLinLst.setText(str(lin_num_in))

    def display_log(self, nod_lin_num = 0):
        found_lin_num = False
        for log_node in self.lst_node_info_out:
            if log_node["lin_num"] == nod_lin_num:
                found_lin_num = True
                lst_log_lines = log_node["log_line_lst"]

        if not found_lin_num:
            cmd = {"nod_lst":[nod_lin_num], "cmd_lst":["display_log"]}
            json_log = json_data_request(uni_url, cmd)
            lst_log_lines = json_log[0]
            self.lst_node_info_out.append(
                {
                    "lin_num"       : nod_lin_num,
                    "log_line_lst"  : lst_log_lines
                }
            )
        self.window.incoming_text.clear()
        for single_log_line in lst_log_lines:
            self.window.incoming_text.insertPlainText(single_log_line + "\n")
            self.window.incoming_text.moveCursor(QTextCursor.End)

    def reset_param(self):
        print("reset_param")
        str_key = self.current_params_widget
        self.param_widgets[str_key]["simple"].reset_pars()
        try:
            self.param_widgets[str_key]["advanced"].reset_pars()

        except AttributeError:
            print("No advanced pars")

        self.params2run = []

    def change_widget(self, str_key):
        self.window.CurrentControlWidgetLabel.setText(str_key)
        self.window.StackedParamsWidget.setCurrentWidget(
            self.param_widgets[str_key]["main_page"]
        )
        self.clearLayout(self.window.Next2RunLayout)
        self.window.Next2RunLayout.addStretch()
        for bt_labl in self.param_widgets[str_key]["nxt_widg_lst"]:
            nxt_butt = QPushButton(bt_labl)
            nxt_butt.cmd_str = bt_labl
            nxt_butt.clicked.connect(self.nxt_clicked)
            self.window.Next2RunLayout.addWidget(nxt_butt)

        self.params2run = []

    def add_new_node(self):
        self.local_nod_lst.append(self.new_node)
        for node in self.local_nod_lst:
            if node["lin_num"] in self.new_node["parent_node_lst"]:
                node["child_node_lst"].append(int(self.new_node["lin_num"]))

        self.display(self.local_nod_lst)
        self.window.CmdEdit.setText(self.new_node["cmd2show"][0])
        #TODO add parameters in self.window.CmdEdit

    def request_display(self):
        print("\n request_display \n")
        cmd = {"nod_lst":"", "cmd_lst":["display"]}
        self.server_nod_lst = json_data_request(uni_url, cmd)
        if self.new_node is None:
            self.display(self.server_nod_lst)
            print("self.new_node is None")

        else:
            self.local_nod_lst = copy_lst_nodes(self.server_nod_lst)
            self.add_new_node()
            print("self.new_node =", self.new_node)

    def request_launch(self):
        cmd_str = str(self.window.CmdEdit.text())
        self.params2run = []
        self.window.CmdEdit.clear()
        print("\n cmd_str", cmd_str)
        nod_str = str(self.window.NumLinLst.text())
        nod_lst = nod_str.split(" ")
        #self.window.NumLinLst.clear()
        self.window.incoming_text.clear()
        print("\n nod_lst", nod_lst)
        cmd = {"nod_lst":nod_lst, "cmd_lst":[cmd_str]}
        print("cmd =", cmd)

        try:
            new_req_get = requests.get(uni_url, stream = True, params = cmd)
            #TODO make sure when client is relaunched,
            #TODO somehow it know about busy nodes
            new_thrd = Run_n_Output(new_req_get)
            new_thrd.new_line_out.connect(self.add_line)
            new_thrd.first_line.connect(self.line_n1_in)
            new_thrd.finished.connect(self.request_display)
            new_thrd.start()
            self.thrd_lst.append(new_thrd)
            self.new_node = None

        except requests.exceptions.RequestException:
            print("something went wrong with the request launch")

    def nxt_clicked(self):
        print("nxt_clicked")
        str_key = self.sender().cmd_str
        print("str_key: ", str_key)
        self.change_widget(str_key)
        self.current_params_widget = str_key

        self.local_nod_lst = copy_lst_nodes(self.server_nod_lst)
        par_lin_num = int(self.current_lin_num)
        max_lin_num = 0
        for node in self.local_nod_lst:
            if node["lin_num"] > max_lin_num:
                max_lin_num = node["lin_num"]

        self.current_lin_num = max_lin_num + 1

        self.new_node = {
            'lin_num': int(self.current_lin_num),
            'status': 'Ready',
            'cmd2show': ["dials." + str(str_key)],
            'child_node_lst': [],
            'parent_node_lst': [par_lin_num]
        }
        self.add_new_node()
        self.window.incoming_text.clear()
        self.window.incoming_text.insertPlainText("Ready to run: ")

    def on_retry(self):
        print("on_retry")
        nod2clone = dict(self.server_nod_lst[int(self.current_lin_num)])
        str_key = str(nod2clone["cmd2show"][0][6:])
        print("str_key: ", str_key)
        self.change_widget(str_key)
        self.current_params_widget = str_key
        #TODO put here the cloned parameters
        self.local_nod_lst = copy_lst_nodes(self.server_nod_lst)
        max_lin_num = 0
        for node in self.local_nod_lst:
            if node["lin_num"] > max_lin_num:
                max_lin_num = node["lin_num"]

        self.current_lin_num = max_lin_num + 1
        self.new_node = {
            'lin_num': int(self.current_lin_num),
            'status': 'Ready',
            'cmd2show': list(nod2clone["cmd2show"]),
            'child_node_lst': [],
            'parent_node_lst': list(nod2clone["parent_node_lst"])
        }
        self.add_new_node()
        self.window.incoming_text.clear()
        self.window.incoming_text.insertPlainText("Ready to run: ")

        n_lst_str = ""
        for par_nod_num in self.new_node["parent_node_lst"]:
            n_lst_str += str(par_nod_num) + " "

        n_lst_str = n_lst_str[:-1]
        self.window.NumLinLst.setText(n_lst_str)

    def req_stop(self):
        print("req_stop")
        self.window.CmdEdit.clear()
        #self.window.NumLinLst.clear()
        self.window.incoming_text.clear()
        nod_lst = [str(self.current_lin_num)]
        print("\n nod_lst", nod_lst)
        cmd = {"nod_lst":nod_lst, "cmd_lst":["stop"]}
        print("cmd =", cmd)

        try:
            lst_params = json_data_request(uni_url, cmd)

        except requests.exceptions.RequestException:
            print("something went wrong with the request launch")


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    m_obj = MainObject()
    sys.exit(app.exec_())

