"""
DUI2's Main window on client side

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

import os, sys, requests

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from PySide2.QtWebEngineWidgets import QWebEngineView

from gui_utils import TreeDirScene, widgets_defs
from outputs import DoLoadHTML, ShowLog
from reindex_table import ReindexTable
from exec_utils import (
    build_advanced_params_widget,
    json_data_request,
    Run_n_Output,
    CommandParamControl,
    uni_url
)
from simpler_param_widgets import ImportTmpWidg as ImportWidget
from simpler_param_widgets import MaskTmpWidg as MaskWidget
from simpler_param_widgets import (
    FindspotsSimplerParameterTab, IndexSimplerParamTab,
    RefineBravaiSimplerParamTab, RefineSimplerParamTab,
    IntegrateSimplerParamTab, SymmetrySimplerParamTab,
    ScaleSimplerParamTab, CombineExperimentSimplerParamTab
)



class MainObject(QObject):
    def __init__(self, parent = None):
        super(MainObject, self).__init__(parent)
        self.parent_app = parent
        self.ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = self.ui_dir_path + os.sep + "client.ui"
        print("ui_path =", ui_path)

        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.setWindowTitle("CCP4 DUI Cloud")

        try:
            imp_widg = ImportWidget()
            imp_widg.item_changed.connect(self.item_param_changed)
            self.window.ImportScrollArea.setWidget(imp_widg)

            mask_widg = MaskWidget()
            #mask_widg.item_changed.connect(self.item_param_changed)
            self.window.MaskScrollArea.setWidget(mask_widg)


            find_simpl_widg = FindspotsSimplerParameterTab()
            find_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.FindspotsSimplerScrollArea.setWidget(find_simpl_widg)
            fd_advanced_parameters = build_advanced_params_widget("find_spots_params")
            fd_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.FindspotsAdvancedScrollArea.setWidget(fd_advanced_parameters)

            fd_advanced_parameters.twin_widg = find_simpl_widg
            find_simpl_widg.twin_widg = fd_advanced_parameters

            index_simpl_widg = IndexSimplerParamTab()
            index_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.IndexSimplerScrollArea.setWidget(index_simpl_widg)
            id_advanced_parameters = build_advanced_params_widget("index_params")
            id_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.IndexAdvancedScrollArea.setWidget(id_advanced_parameters)

            id_advanced_parameters.twin_widg = index_simpl_widg
            index_simpl_widg.twin_widg = id_advanced_parameters

            refi_brv_simpl_widg = RefineBravaiSimplerParamTab()
            refi_brv_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.RefineBravaiSimplerScrollArea.setWidget(refi_brv_simpl_widg)
            rb_advanced_parameters = build_advanced_params_widget("refine_bravais_settings_params")
            rb_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.RefineBravaiAdvancedScrollArea.setWidget(rb_advanced_parameters)

            rb_advanced_parameters.twin_widg = refi_brv_simpl_widg
            refi_brv_simpl_widg.twin_widg = rb_advanced_parameters

            self.r_index_widg = ReindexTable()
            self.window.ReindexTableScrollArea.setWidget(self.r_index_widg)

            ref_simpl_widg = RefineSimplerParamTab()
            ref_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.RefineSimplerScrollArea.setWidget(ref_simpl_widg)
            rf_advanced_parameters = build_advanced_params_widget("refine_params")
            rf_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.RefineAdvancedScrollArea.setWidget(rf_advanced_parameters)

            rf_advanced_parameters.twin_widg = ref_simpl_widg
            ref_simpl_widg.twin_widg = rf_advanced_parameters

            integr_simpl_widg = IntegrateSimplerParamTab()
            integr_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.IntegrateSimplerScrollArea.setWidget(integr_simpl_widg)
            it_advanced_parameters = build_advanced_params_widget("integrate_params")
            it_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.IntegrateAdvancedScrollArea.setWidget(it_advanced_parameters)

            it_advanced_parameters.twin_widg = integr_simpl_widg
            integr_simpl_widg.twin_widg = it_advanced_parameters

            sym_simpl_widg = SymmetrySimplerParamTab()
            sym_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.SymmetrySimplerScrollArea.setWidget(sym_simpl_widg)
            sm_advanced_parameters = build_advanced_params_widget("symmetry_params")
            sm_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.SymmetryAdvancedScrollArea.setWidget(sm_advanced_parameters)

            sm_advanced_parameters.twin_widg = sym_simpl_widg
            sym_simpl_widg.twin_widg = sm_advanced_parameters

            scale_simpl_widg = ScaleSimplerParamTab()
            scale_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.ScaleSimplerScrollArea.setWidget(scale_simpl_widg)
            sc_advanced_parameters = build_advanced_params_widget("scale_params")
            sc_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.ScaleAdvancedScrollArea.setWidget(sc_advanced_parameters)

            sc_advanced_parameters.twin_widg = scale_simpl_widg
            scale_simpl_widg.twin_widg = sc_advanced_parameters

            comb_simpl_widg = CombineExperimentSimplerParamTab()
            comb_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.CombineSimplerScrollArea.setWidget(comb_simpl_widg)
            ce_advanced_parameters = build_advanced_params_widget(
                "combine_experiments_params"
            )
            ce_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.CombineAdvancedScrollArea.setWidget(ce_advanced_parameters)

            ce_advanced_parameters.twin_widg = comb_simpl_widg
            comb_simpl_widg.twin_widg = ce_advanced_parameters

        except TypeError:
            print("failed to connect to server")
            sys.exit()

        self.param_widgets = widgets_defs

        self.param_widgets["import"]["simple"] = imp_widg
        self.param_widgets["import"]["advanced"] = None
        self.param_widgets["import"]["main_page"] = self.window.ImportPage

        self.param_widgets["find_spots"]["simple"] = find_simpl_widg
        self.param_widgets["find_spots"]["advanced"] = fd_advanced_parameters
        self.param_widgets["find_spots"]["main_page"] = self.window.FindspotsPage

        self.param_widgets["apply_mask"]["simple"] = mask_widg
        self.param_widgets["apply_mask"]["advanced"] = None
        self.param_widgets["apply_mask"]["main_page"] = self.window.MaskPage

        self.param_widgets["index"]["simple"] = index_simpl_widg
        self.param_widgets["index"]["advanced"] = id_advanced_parameters
        self.param_widgets["index"]["main_page"] = self.window.IndexPage

        self.param_widgets["refine_bravais_settings"]["simple"] = refi_brv_simpl_widg
        self.param_widgets["refine_bravais_settings"]["advanced"] = rb_advanced_parameters
        self.param_widgets["refine_bravais_settings"]["main_page"] = self.window.RefinBrabPage

        self.param_widgets["reindex"]["simple"] = self.r_index_widg
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

        self.window.incoming_text.setFont(QFont("Monospace"))
        self.tree_scene = TreeDirScene(self)
        self.window.treeView.setScene(self.tree_scene)

        self.window.Next2RunLayout.addWidget(
            QLabel("                  . . .       ")
        )
        self.current_next_buttons = 0
        self.parent_nums_lst = []

        self.font_point_size = QFont().pointSize()

        self.tree_scene.node_clicked.connect(self.on_node_click)
        self.window.Reset2DefaultPushButton.clicked.connect(
            self.reset_param
        )
        self.window.ClearParentButton.clicked.connect(
            self.clear_parent_list
        )
        self.r_index_widg.opt_signal.connect(self.launch_reindex)

        re_try_icon = QIcon()
        rt_icon_path = self.ui_dir_path + os.sep + "resources" \
            + os.sep + "re_try.png"
        re_try_icon.addFile(rt_icon_path, mode = QIcon.Normal)
        self.window.RetryButton.setIcon(re_try_icon)
        run_icon = QIcon()
        rn_icon_path = self.ui_dir_path + os.sep + "resources" \
            + os.sep + "DIALS_Logo_smaller_centred.png"
        run_icon.addFile(rn_icon_path, mode = QIcon.Normal)
        self.window.CmdSend2server.setIcon(run_icon)
        stop_icon = QIcon()
        st_icon_path = self.ui_dir_path + os.sep + "resources" \
            + os.sep + "stop.png"
        stop_icon.addFile(st_icon_path, mode = QIcon.Normal)
        self.window.ReqStopButton.setIcon(stop_icon)

        self.window.RetryButton.clicked.connect(self.on_clone)
        self.window.CmdSend2server.clicked.connect(self.request_launch)
        self.window.ReqStopButton.clicked.connect(self.req_stop)
        self.window.RetryButton.setEnabled(True)
        self.window.CmdSend2server.setEnabled(True)
        self.window.ReqStopButton.setEnabled(True)


        self.do_load_html = DoLoadHTML(self)
        self.window.HtmlReport.setHtml(self.do_load_html.not_avail_html)

        self.log_show = ShowLog(self)

        self.window.OutputTabWidget.currentChanged.connect(self.tab_changed)

        self.current_widget_key = "import"
        self.new_node = None
        self.current_nod_num = 0

        self.server_nod_lst = []
        self.request_display()

        self.change_widget(self.current_widget_key)
        self.thrd_lst = []

        self.window.MainHSplitter.setStretchFactor(0, 1)
        self.window.MainHSplitter.setStretchFactor(1, 2)

        self.window.LeftVSplitter.setStretchFactor(0, 3)
        self.window.LeftVSplitter.setStretchFactor(1, 1)

        self.window.show()

    def launch_reindex(self, sol_rei):
        print("reindex solution", sol_rei)
        is_same = self.cmd_par.set_custom_parameter(str(sol_rei))
        if is_same:
            print("clicked twice same row, launching reindex")
            self.request_launch()

    def clicked_4_combine(self, node_numb):
        print("\n clicked_4_combine\n  node_numb =", node_numb)
        self.display()

    def if_needed_html(self):
        tab_index = self.window.OutputTabWidget.currentIndex()
        if tab_index == 1:
            print("updating html report ")
            self.do_load_html()

    def tab_changed(self, tab_index):
        print("tab_index =", tab_index)
        if tab_index == 0:
            self.display_log(self.current_nod_num)

        elif tab_index == 1:
            self.do_load_html()

    def clear_parent_list(self):
        print("clear_parent_list")

    def clicked_4_navigation(self, node_numb):
        print("\n clicked_4_navigation\n  node_numb =", node_numb)
        self.current_nod_num = node_numb
        ##############################################################
        try:
            cur_nod = self.server_nod_lst[node_numb]

        except IndexError:
            cur_nod = self.tree_scene.paint_nod_lst[node_numb]

        if self.window.OutputTabWidget.currentIndex() == 0:
            self.display_log(node_numb)

        else:
            self.do_load_html()

        #self.parent_nums_lst"] = [node_numb]

        print("\n cur_nod = ", cur_nod, "\n")

        cmd_ini = cur_nod["cmd2show"][0]
        key2find = cmd_ini[6:]
        try:
            self.change_widget(key2find)
            #self.update_all_param(cur_nod)
            if key2find == "reindex":
                cmd = {
                    "nod_lst":cur_nod["parent_node_lst"],
                    "cmd_lst":["get_bravais_sum"]
                }
                json_data_lst = json_data_request(uni_url, cmd)
                self.r_index_widg.add_opts_lst(
                    json_data=json_data_lst[0]
                )

        except KeyError:
            print("command widget not there yet")
            return

        ##############################################################
        self.display()

    def on_node_click(self, node_numb):
        #if node_numb != self.current_nod_num:
        #    if(
        #        self.window.NodeSelecCheck.checkState()
        #    ):
        #        self.clicked_4_combine(node_numb)
        #
        #    else:
        #        self.clicked_4_navigation(node_numb)
        #
        #else:
        #    print("clicked current node, no need to do anything")
        self.clicked_4_navigation(node_numb)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                else:
                    self.clearLayout(item.layout())

    def check_nxt_btn(self):
        try:
            print(
                "trying to << check_nxt_btn >> on node",
                self.current_nod_num
            )
            str_key = self.server_nod_lst[self.current_nod_num]["cmd2show"][0][6:]
            print("str_key =", str_key)
            self.update_nxt_butt(str_key)

        except AttributeError:
            print("NO current_nod_num (AttributeError)")

        except IndexError:
            print("NO current_nod_num (IndexError)")

    def update_nxt_butt(self, str_key):
        small_f_size = int(self.font_point_size * 0.85)
        small_font = QFont("OldEnglish", pointSize = small_f_size, italic=True)
        try:
            if(
                self.server_nod_lst[self.current_nod_num]["status"]
                == "Succeeded"
            ):
                self.clearLayout(self.window.Next2RunLayout)
                self.window.Next2RunLayout.addStretch()
                for bt_labl in self.param_widgets[str_key]["nxt_widg_lst"]:
                    nxt_butt = QPushButton(bt_labl)
                    nxt_butt.cmd_str = bt_labl
                    nxt_butt.setFont(small_font)
                    nxt_butt.clicked.connect(self.nxt_clicked)
                    nxt_ico = QIcon()
                    icon_path = self.ui_dir_path + os.sep + \
                        self.param_widgets[bt_labl]["icon"]

                    nxt_ico.addFile(
                        icon_path,
                        mode=QIcon.Normal
                    )
                    nxt_butt.setIcon(nxt_ico)
                    nxt_butt.setIconSize(QSize(38, 42))

                    self.window.Next2RunLayout.addWidget(nxt_butt)

        except IndexError:
            print("no need to add next button")

    def nxt_clicked(self):
        str_key = self.sender().cmd_str
        print("nxt_clicked ... str_key: ", str_key)
        if str_key == "reindex":
            cmd = {
                "nod_lst":[self.current_nod_num],
                "cmd_lst":["get_bravais_sum"]
            }
            json_data_lst = json_data_request(uni_url, cmd)
            self.r_index_widg.add_opts_lst(
                json_data = json_data_lst[0]
            )
        self.change_widget(str_key)
        self.reset_param()
        self.add_new_node()
        self.do_load_html.set_output_as_ready()

    def change_widget(self, str_key):
        self.window.BoxControlWidget.setTitle(str_key)
        self.window.StackedParamsWidget.setCurrentWidget(
            self.param_widgets[str_key]["main_page"]
        )
        self.clearLayout(self.window.Next2RunLayout)
        self.update_nxt_butt(str_key)
        self.current_widget_key = str_key
        self.update_all_param()

    def reset_param(self):
        self.param_widgets[self.current_widget_key]["simple"].reset_pars()
        try:
            self.param_widgets[self.current_widget_key]["advanced"].reset_pars()

        except AttributeError:
            print("No advanced pars")

    def item_param_changed(self, str_path, str_value):
        self.sender().twin_widg.update_param(str_path, str_value)
        if self.current_nod_num == self.new_node.number:
            self.new_node.set_parameter(str_path, str_value)

    def add_new_node(self):
        print("add_new_node")
        self.new_node = CommandParamControl(
            self.param_widgets[self.current_widget_key]["main_cmd"]
        )
        self.new_node.set_connections(
            self.server_nod_lst, [self.current_nod_num]
        )
        self.current_nod_num = self.new_node.number
        self.display()

    def update_all_param(self):
        tmp_cmd_par = CommandParamControl()
        try:
            tmp_cmd_par.clone_from_list(
                self.server_nod_lst[self.current_nod_num]["cmd2show"]
            )

        except IndexError:
            tmp_cmd_par = self.new_node

        self.reset_param()
        self.param_widgets[self.current_widget_key]["simple"].update_all_pars(
            tmp_cmd_par.get_all_params()
        )
        try:
            self.param_widgets[self.current_widget_key]["advanced"].update_all_pars(
                tmp_cmd_par.get_all_params()
            )
        except AttributeError:
            print("No advanced pars")

    def display_log(self, nod_p_num = 0):
        self.log_show(nod_p_num)

    def display(self):
        self.tree_scene.draw_tree_graph(
            nod_lst_in = self.server_nod_lst,
            current_nod_num = self.current_nod_num,
            new_node = self.new_node
        )

    def request_display(self):
        cmd = {"nod_lst":"", "cmd_lst":["display"]}
        self.server_nod_lst = json_data_request(uni_url, cmd)
        self.display()

    def on_clone(self):
        print("on_clone", "*" * 50)

    def request_launch(self):
        cmd_str = self.new_node.get_full_command_string()
        lst_of_node_str = self.new_node.parent_node_lst

        cmd = {'nod_lst': lst_of_node_str, 'cmd_lst': [cmd_str]}
        print("cmd =", cmd)
        self.window.incoming_text.clear()

        try:
            new_req_get = requests.get(uni_url, stream = True, params = cmd)
            #TODO make sure when client is relaunched,
            #TODO somehow it should know about busy nodes
            new_thrd = Run_n_Output(new_req_get)
            new_thrd.new_line_out.connect(self.log_show.add_line)
            new_thrd.first_line.connect(self.line_n1_in)
            new_thrd.finished.connect(self.request_display)
            new_thrd.finished.connect(self.check_nxt_btn)
            new_thrd.finished.connect(self.if_needed_html)
            new_thrd.start()
            self.thrd_lst.append(new_thrd)

        except requests.exceptions.RequestException:
            print("something went wrong with the request launch")
            #TODO: put inside this << except >> some way to kill << new_thrd >>

    def line_n1_in(self, nod_num_in):
        self.request_display()
        print("line_n1_in(nod_num_in) = ", nod_num_in)
        #TODO: consider if this line goes in << request_launch >>
        self.new_node = None

    def req_stop(self):
        print("req_stop")
        #self.window.incoming_text.clear()
        nod_lst = [str(self.current_nod_num)]
        print("\n nod_lst", nod_lst)
        cmd = {"nod_lst":nod_lst, "cmd_lst":["stop"]}
        print("cmd =", cmd)
        try:
            lst_params = json_data_request(uni_url, cmd)

        except requests.exceptions.RequestException:
            print(
                "something went wrong with the request launch"
            )


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    m_obj = MainObject(parent = app)
    sys.exit(app.exec_())

