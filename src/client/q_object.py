"""
DUI2's Main window << Object >> on client side

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


from gui_utils import TreeDirScene, widgets_defs, get_icons
from outputs import DoLoadHTML, ShowLog
from img_view import DoImageView
from reindex_table import ReindexTable
from exec_utils import (
    build_advanced_params_widget, json_data_request, Run_n_Output,
    CommandParamControl
)

from init_firts import ini_data

from simpler_param_widgets import RootWidg
from simpler_param_widgets import ImportWidget
from simpler_param_widgets import MaskWidget
from simpler_param_widgets import ExportWidget
from simpler_param_widgets import (
    FindspotsSimplerParameterTab, IndexSimplerParamTab,
    RefineBravaiSimplerParamTab, RefineSimplerParamTab,
    IntegrateSimplerParamTab, SymmetrySimplerParamTab,
    ScaleSimplerParamTab, CombineExperimentSimplerParamTab
)


class find_scale_cmd(object):
    '''
    This class works as a function that internally navigates with
    recursive calls to find out if there is a << dials.scale >> command
    '''
    def __init__(self, nod_lst, nod_num):
        print(
            "searching for Scale Command in history \n single node =",
             nod_lst[nod_num]
        )
        self.nod_lst = nod_lst
        self.found_scale = False
        self.get_parent_num(nod_num)

    def get_parent_num(self, nod_num):
        print(
            "(number, cmd2show[0]) =", nod_num, ":",
            self.nod_lst[nod_num]["cmd2show"][0]
        )
        if self.nod_lst[nod_num]["cmd2show"][0] == "dials.scale":
            self.found_scale = True

        for new_nod_num in self.nod_lst[nod_num]["parent_node_lst"]:
            self.get_parent_num(new_nod_num)

    def foung_scale(self):
        return self.found_scale


class MainObject(QObject):
    def __init__(self, parent = None):
        super(MainObject, self).__init__(parent)
        self.parent_app = parent
        self.ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = self.ui_dir_path + os.sep + "dui_client.ui"
        print("ui_path =", ui_path)

        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.setWindowTitle("CCP4 DUI Cloud")

        data_init = ini_data()
        self.uni_url = data_init.get_url()

        self.reseting = False
        try:
            root_widg = RootWidg()
            self.window.RootScrollArea.setWidget(root_widg)

            imp_widg = ImportWidget()
            imp_widg.all_items_changed.connect(self.all_items_param_changed)
            self.window.ImportScrollArea.setWidget(imp_widg)

            self.expr_widg = ExportWidget()
            self.expr_widg.all_items_changed.connect(self.all_items_param_changed)
            self.expr_widg.find_scaled_before.connect(self.search_in_parent_nodes)
            self.window.ExportScrollArea.setWidget(self.expr_widg)

            self.mask_widg = MaskWidget()
            self.mask_widg.all_items_changed.connect(self.all_items_param_changed)
            self.mask_widg.all_items_changed.connect(self.tmp_mask_changed)
            self.mask_widg.component_changed.connect(self.mask_comp_changed)
            self.window.MaskScrollArea.setWidget(self.mask_widg)

            find_simpl_widg = FindspotsSimplerParameterTab()
            find_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.FindspotsSimplerScrollArea.setWidget(find_simpl_widg)
            fd_advanced_parameters = build_advanced_params_widget(
                "find_spots_params"
            )
            fd_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.FindspotsAdvancedScrollArea.setWidget(
                fd_advanced_parameters
            )

            index_simpl_widg = IndexSimplerParamTab()
            index_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.IndexSimplerScrollArea.setWidget(index_simpl_widg)
            id_advanced_parameters = build_advanced_params_widget("index_params")
            id_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.IndexAdvancedScrollArea.setWidget(id_advanced_parameters)

            refi_brv_simpl_widg = RefineBravaiSimplerParamTab()
            refi_brv_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.RefineBravaiSimplerScrollArea.setWidget(
                refi_brv_simpl_widg
            )
            rb_advanced_parameters = build_advanced_params_widget(
                "refine_bravais_settings_params"
            )
            rb_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.RefineBravaiAdvancedScrollArea.setWidget(
                rb_advanced_parameters
            )

            self.r_index_widg = ReindexTable()
            self.window.ReindexTableScrollArea.setWidget(self.r_index_widg)

            ref_simpl_widg = RefineSimplerParamTab()
            ref_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.RefineSimplerScrollArea.setWidget(ref_simpl_widg)
            rf_advanced_parameters = build_advanced_params_widget("refine_params")
            rf_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.RefineAdvancedScrollArea.setWidget(rf_advanced_parameters)

            integr_simpl_widg = IntegrateSimplerParamTab()
            integr_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.IntegrateSimplerScrollArea.setWidget(integr_simpl_widg)
            it_advanced_parameters = build_advanced_params_widget(
                "integrate_params"
            )
            it_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.IntegrateAdvancedScrollArea.setWidget(
                it_advanced_parameters
            )

            sym_simpl_widg = SymmetrySimplerParamTab()
            sym_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.SymmetrySimplerScrollArea.setWidget(sym_simpl_widg)
            sm_advanced_parameters = build_advanced_params_widget(
                "symmetry_params"
            )
            sm_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.SymmetryAdvancedScrollArea.setWidget(
                sm_advanced_parameters
            )

            scale_simpl_widg = ScaleSimplerParamTab()
            scale_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.ScaleSimplerScrollArea.setWidget(scale_simpl_widg)
            sc_advanced_parameters = build_advanced_params_widget("scale_params")
            sc_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.ScaleAdvancedScrollArea.setWidget(sc_advanced_parameters)

            comb_simpl_widg = CombineExperimentSimplerParamTab()
            comb_simpl_widg.item_changed.connect(self.item_param_changed)
            self.window.CombineSimplerScrollArea.setWidget(comb_simpl_widg)
            ce_advanced_parameters = build_advanced_params_widget(
                "combine_experiments_params"
            )
            ce_advanced_parameters.item_changed.connect(self.item_param_changed)
            self.window.CombineAdvancedScrollArea.setWidget(
                ce_advanced_parameters
            )

            fd_advanced_parameters.twin_widg = find_simpl_widg
            find_simpl_widg.twin_widg = fd_advanced_parameters
            id_advanced_parameters.twin_widg = index_simpl_widg
            index_simpl_widg.twin_widg = id_advanced_parameters
            rb_advanced_parameters.twin_widg = refi_brv_simpl_widg
            refi_brv_simpl_widg.twin_widg = rb_advanced_parameters
            rf_advanced_parameters.twin_widg = ref_simpl_widg
            ref_simpl_widg.twin_widg = rf_advanced_parameters
            it_advanced_parameters.twin_widg = integr_simpl_widg
            integr_simpl_widg.twin_widg = it_advanced_parameters
            sm_advanced_parameters.twin_widg = sym_simpl_widg
            sym_simpl_widg.twin_widg = sm_advanced_parameters
            sc_advanced_parameters.twin_widg = scale_simpl_widg
            scale_simpl_widg.twin_widg = sc_advanced_parameters
            ce_advanced_parameters.twin_widg = comb_simpl_widg
            comb_simpl_widg.twin_widg = ce_advanced_parameters

        except TypeError:
            print("failed to connect to server on:", self.uni_url)
            sys.exit()

        tmp_widget_defs = widgets_defs
        self.param_widgets = get_icons(widgets_defs, self.ui_dir_path)

        self.param_widgets["Root"]["simple"] = imp_widg
        self.param_widgets["Root"]["advanced"] = None
        self.param_widgets["Root"]["main_page"] = self.window.RootPage

        self.param_widgets["import"]["simple"] = imp_widg
        self.param_widgets["import"]["advanced"] = None
        self.param_widgets["import"]["main_page"] = self.window.ImportPage

        self.param_widgets["find_spots"]["simple"] = find_simpl_widg
        self.param_widgets["find_spots"]["advanced"] = fd_advanced_parameters
        self.param_widgets["find_spots"]["main_page"] = self.window.FindspotsPage

        self.param_widgets["apply_mask"]["simple"] = self.mask_widg
        self.param_widgets["apply_mask"]["advanced"] = None
        self.param_widgets["apply_mask"]["main_page"] = self.window.MaskPage

        self.param_widgets["index"]["simple"] = index_simpl_widg
        self.param_widgets["index"]["advanced"] = id_advanced_parameters
        self.param_widgets["index"]["main_page"] = self.window.IndexPage

        self.param_widgets[
            "refine_bravais_settings"
        ]["simple"] = refi_brv_simpl_widg

        self.param_widgets[
            "refine_bravais_settings"
        ]["advanced"] = rb_advanced_parameters

        self.param_widgets[
            "refine_bravais_settings"
        ]["main_page"] = self.window.RefinBrabPage

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
        self.param_widgets[
            "combine_experiments"
        ]["advanced"] = ce_advanced_parameters

        self.param_widgets[
            "combine_experiments"
        ]["main_page"] = self.window.CombinePage

        self.param_widgets["export"]["simple"] = self.expr_widg
        self.param_widgets["export"]["advanced"] = None
        self.param_widgets["export"]["main_page"] = self.window.ExportPage

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
            self.reset_new_node
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

        try:
            self.do_load_html = DoLoadHTML(self)
            self.window.HtmlReport.setHtml(self.do_load_html.not_avail_html)

        except AttributeError:
            print("removing HtmlReport for old vesion of PySide2 ")

        self.log_show = ShowLog(self)

        self.do_image_view = DoImageView(self)
        self.do_image_view.new_mask_comp.connect(self.get_new_mask_comp)

        self.window.OutputTabWidget.currentChanged.connect(self.refresh_output)
        self.window.ImgNumEdit.textChanged.connect(self.img_num_changed)
        self.window.PrevImgButton.clicked.connect(self.prev_img)
        self.window.NextImgButton.clicked.connect(self.next_img)

        self.curr_widg_key = "Root"
        self.new_node = None
        self.curr_nod_num = 0

        self.server_nod_lst = []
        self.request_display()

        self.change_widget(self.curr_widg_key)
        self.thrd_lst = []

        self.window.MainHSplitter.setStretchFactor(0, 1)
        self.window.MainHSplitter.setStretchFactor(1, 2)
        self.window.LeftVSplitter.setStretchFactor(0, 3)
        self.window.LeftVSplitter.setStretchFactor(1, 1)

        self.window.show()
        self.import_init()

    def import_init(self):
        loop = QEventLoop()
        QTimer.singleShot(200, loop.quit)
        loop.exec_()
        print("self.server_nod_lst =", self.server_nod_lst)
        if len(self.server_nod_lst) == 1:
            self.nxt_key_clicked("import")

        else:
            big_nod_num = 0
            for node in self.server_nod_lst:
                if node["number"] > big_nod_num:
                    big_nod_num = node["number"]

            self.on_node_click(big_nod_num)

    def launch_reindex(self, sol_rei):
        print("reindex solution", sol_rei)
        is_same = self.new_node.set_custom_parameter(str(sol_rei))
        if is_same:
            print("clicked twice same row, launching reindex")
            self.request_launch()

    def img_num_changed(self, new_img_num):
        print("should load IMG num:", new_img_num)
        self.refresh_output()

    def shift_img_num(self, sh_num):
        img_num = int(self.window.ImgNumEdit.text())
        img_num += sh_num
        self.window.ImgNumEdit.setText(str(img_num))

    def prev_img(self):
        print("prev_img")
        self.shift_img_num(-1)

    def next_img(self):
        print("next_img")
        self.shift_img_num(1)

    def refresh_output(self, tab_index = None):
        if tab_index == None:
            tab_index = self.window.OutputTabWidget.currentIndex()

        print("tab_index =", tab_index)
        fnd_cur_nod = False
        for node in self.server_nod_lst:
            if node["number"] == self.curr_nod_num:
                fnd_cur_nod = True

        if tab_index == 0:
            lst_tmp_par = []
            try:
                simpl_widg = self.param_widgets[self.curr_widg_key]["simple"]
                new_lst = simpl_widg.comp_list_update()
                if(
                    self.new_node is not None and
                    self.new_node.m_cmd_lst[0] == "dials.generate_mask" and
                    self.new_node.number == self.curr_nod_num
                ):
                    lst_tmp_par = new_lst[0][0:-1]

            except AttributeError:
                print("(empty) update_tmp_mask()")

            self.do_image_view.update_tmp_mask(lst_tmp_par)

            if(
                self.new_node is not None and
                self.new_node.m_cmd_lst[0] == "dials.generate_mask" and
                self.new_node.number == self.curr_nod_num
            ):
                self.do_image_view.set_drag_mode(mask_mode = True)

            else:
                self.do_image_view.set_drag_mode(mask_mode = False)

            img_num = int(self.window.ImgNumEdit.text())
            self.do_image_view(in_img_num = img_num, nod_or_path = fnd_cur_nod)

        elif tab_index == 1:
            self.log_show(self.curr_nod_num, do_request = fnd_cur_nod)

        elif tab_index == 2:
            try:
                self.do_load_html(do_request = fnd_cur_nod)

            except AttributeError:
                print("removing HtmlReport for old vesion of PySide2 ")


    def mask_comp_changed(self, mask_comp):
        self.do_image_view.set_mask_comp(mask_comp)

    def get_new_mask_comp(self, comp_dict):
        self.mask_widg.get_new_comp(comp_dict)

    def tmp_mask_changed(self, lst_of_lst):
        self.do_image_view.update_tmp_mask(lst_of_lst[0][0:-1])

    def clear_parent_list(self):
        self.new_node.clear_parents()
        self.display()

    def clicked_4_navigation(self, node_numb):
        print("\n clicked_4_navigation\n  node_numb =", node_numb)
        self.curr_nod_num = node_numb
        try:
            cur_nod = self.server_nod_lst[node_numb]

        except IndexError:
            cur_nod = self.tree_scene.paint_nod_lst[node_numb]

        cmd_ini = cur_nod["cmd2show"][0]
        key2find = cmd_ini[6:]
        try:
            self.change_widget(key2find)
            self.update_all_param()
            if key2find == "reindex":
                cmd = {
                    "nod_lst":cur_nod["parent_node_lst"],
                    "cmd_lst":["get_bravais_sum"]
                }
                json_data_lst = json_data_request(self.uni_url, cmd)
                self.r_index_widg.add_opts_lst(
                    json_data = json_data_lst[0]
                )

        except KeyError:
            print("command widget not there yet")
            return

        self.refresh_output()
        self.display()

    def on_node_click(self, node_numb):
        if (
            self.new_node is not None and
            node_numb != self.curr_nod_num and
            self.window.NodeSelecCheck.checkState() and
            self.curr_widg_key == "combine_experiments"
        ):
            self.new_node.add_or_remove_parent(node_numb)
            self.display()

        else:
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
        self.clearLayout(self.window.Next2RunLayout)
        self.window.Next2RunLayout.addStretch()
        try:
            str_key = self.server_nod_lst[self.curr_nod_num]["cmd2show"][0][6:]
            print("update_nxt_butt(", str_key, ")")
            self.update_nxt_butt(str_key)

        except (IndexError, AttributeError):
            print("NO need to run << update_nxt_butt >>")

    def update_nxt_butt(self, str_key):
        small_f_size = int(self.font_point_size * 0.85)
        small_font = QFont("OldEnglish", pointSize = small_f_size, italic=True)
        try:
            if(
                self.server_nod_lst[self.curr_nod_num]["status"] == "Succeeded"
            ):
                print("\nupdate_nxt_butt: key =", str_key, "\n")
                for bt_labl in self.param_widgets[str_key]["nxt_widg_lst"]:
                    nxt_butt = QPushButton(bt_labl)
                    nxt_butt.cmd_str = bt_labl
                    nxt_butt.setFont(small_font)
                    nxt_butt.clicked.connect(self.nxt_clicked)
                    nxt_butt.setIcon(self.param_widgets[bt_labl]["icon"])
                    nxt_butt.setIconSize(QSize(38, 42))
                    self.window.Next2RunLayout.addWidget(nxt_butt)

        except (IndexError, KeyError):
            print("no need to add next button")

    def nxt_clicked(self):
        self.nxt_key_clicked(self.sender().cmd_str)

    def nxt_key_clicked(self, str_key):
        print("nxt_clicked ... str_key: ", str_key)

        if str_key == "reindex":
            cmd = {
                "nod_lst":[self.curr_nod_num],
                "cmd_lst":["get_bravais_sum"]
            }
            json_data_lst = json_data_request(self.uni_url, cmd)
            self.r_index_widg.add_opts_lst(
                json_data = json_data_lst[0]
            )

        self.change_widget(str_key)
        self.reset_param()
        self.add_new_node()
        self.check_nxt_btn()

    def change_widget(self, str_key):
        self.window.BoxControlWidget.setTitle(str_key)
        self.window.StackedParamsWidget.setCurrentWidget(
            self.param_widgets[str_key]["main_page"]
        )
        self.check_nxt_btn()
        self.curr_widg_key = str_key

    def reset_param(self):
        self.reseting = True
        self.param_widgets[self.curr_widg_key]["simple"].reset_pars()
        try:
            self.param_widgets[self.curr_widg_key]["advanced"].reset_pars()

        except AttributeError:
            print("No advanced pars")

        self.reseting = False

    def reset_new_node(self):
        self.new_node.reset_all_params()
        self.reset_param()
        try:
            simpl_widg = self.param_widgets[self.curr_widg_key]["simple"]
            new_full_list = simpl_widg.build_full_list()
            self.tmp_mask_changed(new_full_list)

        except AttributeError:
            print("this node does not need build_full_list")

    def all_items_param_changed(self, lst_of_lst):
        try:
            if self.new_node.number == self.curr_nod_num:
                print("\n Updating Params with", lst_of_lst, "\n")
                self.new_node.reset_all_params()
                self.new_node.set_all_parameters(lst_of_lst)

        except AttributeError:
            print("Not updating parameters, no (green node or twin widget)\n")
            print("self.new_node.number =", self.new_node.number)
            print("self.curr_nod_num =", self.curr_nod_num)

    def item_param_changed(self, str_path = None, str_value = None, lst_num = 0):
        try:
            self.sender().twin_widg.update_param(str_path, str_value)

        except AttributeError:
            print("no twin widget to update")

        try:
            if(
                self.curr_nod_num == self.new_node.number
                and not self.reseting
            ):
                self.new_node.set_parameter(str_path, str_value, lst_num)

        except AttributeError:
            print("Not updating parameters, no (green node or twin widget)\n")

    def add_new_node(self):
        print("add_new_node")
        local_main_cmd = self.param_widgets[self.curr_widg_key]["main_cmd"]
        self.new_node = CommandParamControl(
            main_list = local_main_cmd
        )
        self.new_node.set_connections(
            self.server_nod_lst, [self.curr_nod_num]
        )
        self.curr_nod_num = self.new_node.number
        self.display()
        self.refresh_output()
        if local_main_cmd == ['dials.export']:
            self.param_widgets[self.curr_widg_key]["simple"].reset_pars()

    def search_in_parent_nodes(self):
        try:
            fnd_scl_cmd = find_scale_cmd(
                self.server_nod_lst, self.new_node.parent_node_lst[0]
            )
            fnd_scl = fnd_scl_cmd.foung_scale()
            print("found_scale =", fnd_scl)
            self.expr_widg.is_scale_parent(fnd_scl)

        except AttributeError:
            print("no need to find scale step as parent")

    def update_all_param(self):
        tmp_cmd_par = CommandParamControl()
        self.reset_param()
        try:
            tmp_cmd_par.clone_from_list(
                self.server_nod_lst[self.curr_nod_num]["lst2run"]
            )
            print("\n Updating parameters from server_nod_lst")

        except IndexError:
            tmp_cmd_par = self.new_node
            print("\n Updating parameters from ...new_node")

        print(
            "update_all_param(MainObject)...tmp_cmd_par.get_all_params() = ",
            tmp_cmd_par.get_all_params()
        )
        self.param_widgets[self.curr_widg_key]["simple"].update_all_pars(
            tmp_cmd_par.get_all_params()
        )
        try:
            self.param_widgets[self.curr_widg_key]["advanced"].update_all_pars(
                tmp_cmd_par.get_all_params()
            )
        except AttributeError:
            print("No advanced pars")

    def gray_n_ungray(self):
        try:
            tmp_state = self.server_nod_lst[self.curr_nod_num]["status"]

        except IndexError:
            tmp_state = "Ready"

        str_key = self.curr_widg_key
        self.param_widgets[str_key]["simple"].setEnabled(False)
        try:
            self.param_widgets[str_key]["advanced"].setEnabled(False)

        except AttributeError:
            print("no need to gray 'None' widget")

        self.window.ClearParentButton.setEnabled(False)
        self.window.RetryButton.setEnabled(False)
        self.window.CmdSend2server.setEnabled(False)
        self.window.ReqStopButton.setEnabled(False)
        self.window.Reset2DefaultPushButton.setEnabled(False)

        if tmp_state == "Ready":
            print("only run (R)")
            self.window.CmdSend2server.setEnabled(True)
            self.param_widgets[str_key]["simple"].setEnabled(True)
            self.window.ClearParentButton.setEnabled(True)
            try:
                self.param_widgets[str_key]["advanced"].setEnabled(True)

            except AttributeError:
                print("no need to un-gray 'None' widget")

            self.window.Reset2DefaultPushButton.setEnabled(True)

        elif tmp_state == "Busy":
            print("only clone or stop (B)")
            self.window.RetryButton.setEnabled(True)
            self.window.ReqStopButton.setEnabled(True)

        else:
            print("only clone (F or S)")
            self.window.RetryButton.setEnabled(True)

        self.check_if_exported()

    def check_if_exported(self):
        try:
            if(
                self.server_nod_lst[self.curr_nod_num]["status"]  == "Succeeded"
                and
                self.server_nod_lst[self.curr_nod_num]["cmd2show"][0] == "dials.export"
            ):
                enabl = True

            else:
                enabl = False

        except IndexError:
            enabl = False

        self.expr_widg.set_download_stat(do_enable = enabl)


    def display(self):
        self.tree_scene.draw_tree_graph(
            nod_lst_in = self.server_nod_lst,
            curr_nod_num = self.curr_nod_num,
            new_node = self.new_node
        )
        self.gray_n_ungray()

    def request_display(self):
        cmd = {"nod_lst":"", "cmd_lst":["display"]}
        self.server_nod_lst = json_data_request(self.uni_url, cmd)
        self.display()

    def on_clone(self):
        print("on_clone")
        self.new_node = CommandParamControl(
            main_list = self.param_widgets[self.curr_widg_key]["main_cmd"]
        )
        self.new_node.set_connections(
            self.server_nod_lst,
            self.server_nod_lst[self.curr_nod_num]["parent_node_lst"]
        )
        self.new_node.clone_from_list(
            self.server_nod_lst[self.curr_nod_num]["lst2run"]
        )
        self.curr_nod_num = self.new_node.number
        self.display()
        self.check_nxt_btn()
        self.refresh_output()

    def request_launch(self):
        cmd_lst = self.new_node.get_full_command_list()
        lst_of_node_str = self.new_node.parent_node_lst
        cmd = {'nod_lst': lst_of_node_str, 'cmd_lst': cmd_lst}
        print("cmd =", cmd)
        self.window.incoming_text.clear()
        try:
            new_req_post = requests.post(
                self.uni_url, stream = True, data = cmd
            )
            new_thrd = Run_n_Output(new_req_post)
            new_thrd.new_line_out.connect(self.log_show.add_line)
            new_thrd.first_line.connect(self.line_n1_in)
            new_thrd.finished.connect(self.request_display)
            new_thrd.finished.connect(self.check_nxt_btn)
            new_thrd.finished.connect(self.refresh_output)
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
        nod_lst = [str(self.curr_nod_num)]
        print("\n nod_lst", nod_lst)
        cmd = {"nod_lst":nod_lst, "cmd_lst":["stop"]}
        print("cmd =", cmd)
        try:
            lst_params = json_data_request(self.uni_url, cmd)

        except requests.exceptions.RequestException:
            print(
                "something went wrong with the request launch"
            )
