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

        json_out = json.loads(str_lst[1])

    except requests.exceptions.RequestException:
        print("\n requests.exceptions.RequestException \n")
        json_out = None

    return json_out


class Run_n_Output(QThread):
    line_out = Signal(str)
    def __init__(self, request):
        super(Run_n_Output, self).__init__()
        self.request = request

    def run(self):
        line_str = ''
        while True:
            tmp_dat = self.request.raw.read(1)
            single_char = str(tmp_dat.decode('utf-8'))
            line_str += single_char
            if single_char == '\n':
                print(line_str[:-1])
                self.line_out.emit(line_str)
                line_str = ''

            elif line_str[-7:] == '/*EOF*/':
                print('>>  /*EOF*/  <<')
                self.line_out.emit(' \n /*EOF*/ \n')
                break

            time.sleep(0.00001)

def build_advanced_params_widget(cmd_str):
    cmd = {"nod_lst":"", "cmd_lst":[cmd_str]}
    lst_params = json_data_request(uni_url, cmd)
    lin_lst = format_utils.param_tree_2_lineal(lst_params)
    par_def = lin_lst()
    advanced_parameters = AdvancedParameters()
    advanced_parameters.build_pars(par_def)
    return advanced_parameters


class MainObject(QObject):
    def __init__(self, parent = None):
        super(MainObject, self).__init__(parent)
        ui_path = os.path.dirname(os.path.abspath(__file__))
        ui_path += os.sep + "client.ui"
        self.window = QtUiTools.QUiLoader().load(ui_path)

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

        self.thrd_lst = []
        self.req_get_lst = []
        self.window.show()

    def on_retry(self):
        print("on_retry")

    def req_stop(self):
        print("req_stop")

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
        print("clicked node number ", nod_num)
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

        for pos, node in enumerate(self.lst_nodes):
            if node["lin_num"] == nod_num:
                cmd_ini = node["cmd2show"][0]
                if cmd_ini.startswith("dials."):
                    key2find = cmd_ini[6:]
                    print("key2find =", key2find)

                else:
                    #TODO: remove this "else" then "ls" command
                    #TODO: is no longer needed
                    key2find = cmd_ini

                try:
                    self.change_widget(key2find)

                except KeyError:
                    print("command widget for", key2find, "not there yet")

    def add_line(self, new_line):
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

    def request_launch(self):
        cmd_str = str(self.window.CmdEdit.text())
        self.params2run = []
        self.window.CmdEdit.clear()
        print("\n cmd_str", cmd_str)
        nod_str = str(self.window.NumLinLst.text())
        nod_lst = nod_str.split(" ")
        self.window.NumLinLst.clear()
        print("\n nod_lst", nod_lst)
        cmd = {"nod_lst":nod_lst, "cmd_lst":[cmd_str]}
        print("cmd =", cmd)

        try:
            new_req_get = requests.get(uni_url, stream = True, params = cmd)
            new_thrd = Run_n_Output(new_req_get)
            self.req_get_lst.append(new_req_get)
            new_thrd.line_out.connect(self.add_line)
            new_thrd.finished.connect(self.request_display)
            new_thrd.start()
            self.thrd_lst.append(new_thrd)

        except requests.exceptions.RequestException:
            print("something went wrong with the request launch")

    def request_display(self):
        cmd = {"nod_lst":"", "cmd_lst":["display"]}
        self.lst_nodes = json_data_request(uni_url, cmd)
        if self.lst_nodes is not None:
            lst_str = self.tree_obj(lst_nod = self.lst_nodes)
            lst_2d_dat = self.tree_obj.get_tree_data()
            for tree_line in lst_str:
                self.add_line(tree_line + "\n")

            self.tree_scene.clear()
            self.tree_scene.draw_tree_graph(lst_2d_dat)
            self.tree_scene.update()

        else:
            print("something went wrong with the list of nodes")

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

    def nxt_clicked(self):
        print("nxt_clicked")
        str_key = self.sender().cmd_str
        print("str_key: ", str_key)
        self.change_widget(str_key)
        self.current_params_widget = str_key


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    m_obj = MainObject()
    sys.exit(app.exec_())

