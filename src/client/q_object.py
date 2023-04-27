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

import os, sys, requests, logging

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from PySide2.QtWebEngineWidgets import QWebEngineView

from client.gui_utils import (
    TreeDirScene, widgets_defs, get_widget_def_dict,
    find_scale_cmd, find_next_cmd, check_if_predict_n_report
)
from client.outputs import DoLoadHTML, ShowLog, HandleReciprocalLatticeView
from client.img_view import DoImageView
from client.reindex_table import ReindexTable, get_label_from_str_list
from client.exec_utils import (
    get_optional_list, build_advanced_params_widget, get_req_json_dat,
    get_help_messages, post_req_w_output, CommandParamControl
)

from client.init_firts import ini_data

from client.simpler_param_widgets import RootWidg
from client.simpler_param_widgets import ImportWidget
from client.simpler_param_widgets import MaskWidget
from client.simpler_param_widgets import ExportWidget
from client.simpler_param_widgets import MergeWidget
from client.simpler_param_widgets import OptionalWidget
from client.simpler_param_widgets import (
    FindspotsSimplerParameterTab, IndexSimplerParamTab,
    SsxIndexSimplerParamTab, SsxIntegrateSimplerParamTab,
    RefineBravaiSimplerParamTab, RefineSimplerParamTab,
    IntegrateSimplerParamTab, SymmetrySimplerParamTab,
    ScaleSimplerParamTab, CombineExperimentSimplerParamTab
)

class MainObject(QObject):
    def __init__(self, parent = None, multi_runner = None):
        super(MainObject, self).__init__(parent)
        self.parent_app = parent
        self.runner_handler = multi_runner
        self.ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = self.ui_dir_path + os.sep + "dui_client.ui"
        logging.info("ui_path =" + ui_path)

        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.setWindowTitle("CCP4 DUI2")

        dui2_icon = QIcon()
        st_icon_path = self.ui_dir_path + os.sep + "resources" \
            + os.sep + "DIALS_Logo_smaller_centred.png"
        dui2_icon.addFile(st_icon_path, mode = QIcon.Normal)
        self.window.setWindowIcon(dui2_icon)

        self.reseting = False

        self.help_msg_dict = get_help_messages(self.runner_handler)

        root_widg = RootWidg()
        self.window.RootScrollArea.setWidget(root_widg)

        imp_widg = ImportWidget()
        imp_widg.all_items_changed.connect(self.all_items_param_changed)
        self.window.ImportScrollArea.setWidget(imp_widg)

        self.expr_widg = ExportWidget()
        self.expr_widg.set_parent(self)
        self.expr_widg.all_items_changed.connect(
            self.all_items_param_changed
        )
        self.expr_widg.find_scaled_before.connect(
            self.search_in_parent_nodes_exp
        )
        self.window.ExportScrollArea.setWidget(self.expr_widg)

        self.merg_widg = MergeWidget()
        self.merg_widg.set_parent(self)
        self.merg_widg.all_items_changed.connect(
            self.all_items_param_changed
        )
        self.merg_widg.find_scaled_before.connect(
            self.search_in_parent_nodes_mer
        )
        self.window.MergeScrollArea.setWidget(self.merg_widg)

        self.opt_cmd_lst = get_optional_list(
            "get_optional_command_list", self.runner_handler
        )
        self.optional_widg = OptionalWidget(cmd_lst = self.opt_cmd_lst)
        self.window.OptionalScrollArea.setWidget(self.optional_widg)
        self.optional_widg.all_items_changed.connect(
            self.all_items_param_changed
        )
        self.optional_widg.main_command_changed.connect(
            self.new_main_command_changed
        )

        self.mask_widg = MaskWidget()
        self.mask_widg.all_items_changed.connect(
            self.all_items_param_changed
        )
        self.mask_widg.all_items_changed.connect(self.tmp_mask_changed)
        self.mask_widg.component_changed.connect(self.mask_comp_changed)
        self.window.MaskScrollArea.setWidget(self.mask_widg)

        fd_advanced_parameters = build_advanced_params_widget(
            "find_spots_params", self.window.FindspotsSearchLayout,
            self.runner_handler
        )
        rad_pr_add = False
        for par_line in fd_advanced_parameters.lst_par_line:
            if par_line["full_path"] == "spotfinder.threshold.algorithm":
                lst_opt = par_line["opt_lst"]
                if("radial_profile" in lst_opt):
                    logging.info(
                        "Time to ADD << spotfinder.threshold.algorithm >>" +
                        "to simple Params as a tick box"
                    )
                    rad_pr_add = True

                else:
                    logging.info(
                        "NO Need to add" +
                        "<< spotfinder.threshold.algorithm >>" +
                        "to simple Params as a tick box"
                    )
                    rad_pr_add = False

        fd_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.FindspotsAdvancedScrollArea.setWidget(
            fd_advanced_parameters
        )
        fd_advanced_parameters.set_scroll_parent(
            self.window.FindspotsAdvancedScrollArea
        )

        find_simpl_widg = FindspotsSimplerParameterTab(
            add_rad_prof = rad_pr_add
        )
        find_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.FindspotsSimplerScrollArea.setWidget(find_simpl_widg)

        index_simpl_widg = IndexSimplerParamTab()
        index_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.IndexSimplerScrollArea.setWidget(index_simpl_widg)
        id_advanced_parameters = build_advanced_params_widget(
            "index_params", self.window.IndexSearchLayout,
            self.runner_handler
        )
        id_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.IndexAdvancedScrollArea.setWidget(
            id_advanced_parameters
        )
        id_advanced_parameters.set_scroll_parent(
            self.window.IndexAdvancedScrollArea
        )

        ssx_index_simpl_widg = SsxIndexSimplerParamTab()
        ssx_index_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.SsxIndexSimplerScrollArea.setWidget(ssx_index_simpl_widg)
        ssx_id_advanced_parameters = build_advanced_params_widget(
            "ssx_index_params", self.window.SsxIndexSearchLayout,
            self.runner_handler
        )
        ssx_id_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.SsxIndexAdvancedScrollArea.setWidget(
            ssx_id_advanced_parameters
        )
        ssx_id_advanced_parameters.set_scroll_parent(
            self.window.SsxIndexAdvancedScrollArea
        )

        refi_brv_simpl_widg = RefineBravaiSimplerParamTab()
        refi_brv_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.RefineBravaiSimplerScrollArea.setWidget(
            refi_brv_simpl_widg
        )
        rb_advanced_parameters = build_advanced_params_widget(
            "refine_bravais_settings_params",
            self.window.RefineBravaisSearchLayout,
            self.runner_handler
        )
        rb_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.RefineBravaiAdvancedScrollArea.setWidget(
            rb_advanced_parameters
        )
        rb_advanced_parameters.set_scroll_parent(
            self.window.RefineBravaiAdvancedScrollArea
        )
        self.r_index_widg = ReindexTable()
        self.window.ReindexHeaderLabel.setText("...")
        self.window.ReindexTableScrollArea.setWidget(self.r_index_widg)
        self.best_rd_idx_opt = 0

        ref_simpl_widg = RefineSimplerParamTab()
        ref_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.RefineSimplerScrollArea.setWidget(ref_simpl_widg)
        rf_advanced_parameters = build_advanced_params_widget(
            "refine_params", self.window.RefineSearchLayout,
            self.runner_handler
        )
        rf_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.RefineAdvancedScrollArea.setWidget(
            rf_advanced_parameters
        )
        rf_advanced_parameters.set_scroll_parent(
            self.window.RefineAdvancedScrollArea
        )
        integr_simpl_widg = IntegrateSimplerParamTab()
        integr_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.IntegrateSimplerScrollArea.setWidget(integr_simpl_widg)
        it_advanced_parameters = build_advanced_params_widget(
            "integrate_params", self.window.IntegrateSearchLayout,
            self.runner_handler
        )
        it_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.IntegrateAdvancedScrollArea.setWidget(
            it_advanced_parameters
        )
        it_advanced_parameters.set_scroll_parent(
            self.window.IntegrateAdvancedScrollArea
        )

        ssx_integr_simpl_widg = SsxIntegrateSimplerParamTab()
        ssx_integr_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.SsxIntegrateSimplerScrollArea.setWidget(ssx_integr_simpl_widg)
        ssx_it_advanced_parameters = build_advanced_params_widget(
            "ssx_integrate_params", self.window.SsxIntegrateSearchLayout,
            self.runner_handler
        )
        ssx_it_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.SsxIntegrateAdvancedScrollArea.setWidget(
            ssx_it_advanced_parameters
        )
        ssx_it_advanced_parameters.set_scroll_parent(
            self.window.SsxIntegrateAdvancedScrollArea
        )

        sym_simpl_widg = SymmetrySimplerParamTab()
        sym_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.SymmetrySimplerScrollArea.setWidget(sym_simpl_widg)
        sm_advanced_parameters = build_advanced_params_widget(
            "symmetry_params", self.window.SymetrySearchLayout,
            self.runner_handler
        )
        sm_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.SymmetryAdvancedScrollArea.setWidget(
            sm_advanced_parameters
        )
        sm_advanced_parameters.set_scroll_parent(
            self.window.SymmetryAdvancedScrollArea
        )
        scale_simpl_widg = ScaleSimplerParamTab()
        scale_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.ScaleSimplerScrollArea.setWidget(scale_simpl_widg)
        sc_advanced_parameters = build_advanced_params_widget(
            "scale_params", self.window.ScaleSearchLayout,
            self.runner_handler
        )
        sc_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.ScaleAdvancedScrollArea.setWidget(
            sc_advanced_parameters
        )
        sc_advanced_parameters.set_scroll_parent(
            self.window.ScaleAdvancedScrollArea
        )
        comb_simpl_widg = CombineExperimentSimplerParamTab()
        comb_simpl_widg.item_changed.connect(self.item_param_changed)
        self.window.CombineSimplerScrollArea.setWidget(comb_simpl_widg)
        ce_advanced_parameters = build_advanced_params_widget(
            "combine_experiments_params", self.window.CombineSearchLayout,
            self.runner_handler
        )
        ce_advanced_parameters.item_changed.connect(
            self.item_param_changed
        )
        self.window.CombineAdvancedScrollArea.setWidget(
            ce_advanced_parameters
        )
        ce_advanced_parameters.set_scroll_parent(
            self.window.CombineAdvancedScrollArea
        )
        fd_advanced_parameters.twin_widg = find_simpl_widg
        find_simpl_widg.twin_widg = fd_advanced_parameters
        id_advanced_parameters.twin_widg = index_simpl_widg
        index_simpl_widg.twin_widg = id_advanced_parameters

        ssx_id_advanced_parameters.twin_widg = ssx_index_simpl_widg
        ssx_index_simpl_widg.twin_widg = ssx_id_advanced_parameters

        rb_advanced_parameters.twin_widg = refi_brv_simpl_widg
        refi_brv_simpl_widg.twin_widg = rb_advanced_parameters
        rf_advanced_parameters.twin_widg = ref_simpl_widg
        ref_simpl_widg.twin_widg = rf_advanced_parameters
        it_advanced_parameters.twin_widg = integr_simpl_widg
        integr_simpl_widg.twin_widg = it_advanced_parameters

        ssx_it_advanced_parameters.twin_widg = ssx_integr_simpl_widg
        ssx_integr_simpl_widg.twin_widg = ssx_it_advanced_parameters

        sm_advanced_parameters.twin_widg = sym_simpl_widg
        sym_simpl_widg.twin_widg = sm_advanced_parameters
        sc_advanced_parameters.twin_widg = scale_simpl_widg
        scale_simpl_widg.twin_widg = sc_advanced_parameters
        ce_advanced_parameters.twin_widg = comb_simpl_widg
        comb_simpl_widg.twin_widg = ce_advanced_parameters

        tmp_widget_defs = widgets_defs
        self.param_widgets = get_widget_def_dict(
            widgets_defs, self.ui_dir_path
        )

        self.param_widgets["root"]["simple"] = imp_widg
        self.param_widgets["root"]["advanced"] = None
        self.param_widgets["root"]["main_page"] = self.window.RootPage

        self.param_widgets["import"]["simple"] = imp_widg
        self.param_widgets["import"]["advanced"] = None
        self.param_widgets["import"]["main_page"] = self.window.ImportPage

        self.param_widgets["find_spots"]["simple"] = find_simpl_widg
        self.param_widgets["find_spots"]["advanced"] = fd_advanced_parameters
        self.param_widgets[
            "find_spots"
        ]["main_page"] = self.window.FindspotsPage

        self.param_widgets["apply_mask"]["simple"] = self.mask_widg
        self.param_widgets["apply_mask"]["advanced"] = None
        self.param_widgets["apply_mask"]["main_page"] = self.window.MaskPage

        self.param_widgets["index"]["simple"] = index_simpl_widg
        self.param_widgets["index"]["advanced"] = id_advanced_parameters
        self.param_widgets["index"]["main_page"] = self.window.IndexPage

        self.param_widgets["ssx_index"]["simple"] = ssx_index_simpl_widg
        self.param_widgets["ssx_index"]["advanced"] = id_advanced_parameters
        self.param_widgets["ssx_index"]["main_page"] = self.window.SsxIndexPage

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
        self.param_widgets[
            "integrate"
        ]["main_page"] = self.window.IntegratePage

        self.param_widgets["ssx_integrate"]["simple"] = ssx_integr_simpl_widg
        self.param_widgets["ssx_integrate"]["advanced"] = ssx_it_advanced_parameters
        self.param_widgets[
            "ssx_integrate"
        ]["main_page"] = self.window.SsxIntegratePage

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

        self.param_widgets["merge"]["simple"] = self.merg_widg
        self.param_widgets["merge"]["advanced"] = None
        self.param_widgets["merge"]["main_page"] = self.window.MergePage

        self.param_widgets["optional"]["simple"] = self.optional_widg
        self.param_widgets["optional"]["advanced"] = None
        self.param_widgets["optional"]["main_page"] = self.window.OptionalPage

        self.regular_colours = True
        self.arrowhead_on = True
        self.sharp_turns_on = True

        self.tree_scene = TreeDirScene(self)
        self.lst2exl = []
        self.window.treeView.setScene(self.tree_scene)

        self.current_next_buttons = 0
        self.parent_nums_lst = []

        self.font_point_size = QFont().pointSize()

        self.tree_scene.node_clicked.connect(self.on_node_click)
        self.tree_scene.hide_clicked.connect(self.on_hide_click)
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

        self.recip_latt = HandleReciprocalLatticeView(self)
        self.recip_latt.get_nod_num.connect(self.verify_nod_num)
        self.window.RecipLattOpenButton.clicked.connect(
            self.RecipLattOpenClicked
        )

        self.do_load_html = DoLoadHTML(self)
        try:
            self.window.HtmlReport.setHtml(self.do_load_html.not_avail_html)

        except AttributeError:
            logging.info("tmp HtmlReport not used QObject ")

        self.log_show = ShowLog(self)

        self.do_image_view = DoImageView(self)
        self.do_image_view.new_mask_comp.connect(self.get_new_mask_comp)

        self.curr_outp_tab = self.window.OutputTabWidget.currentIndex()
        self.window.OutputTabWidget.currentChanged.connect(self.refresh_output)
        self.window.ImgNumEdit.editingFinished.connect(self.img_num_changed)
        self.window.PrevImgButton.clicked.connect(self.prev_img)
        self.window.NextImgButton.clicked.connect(self.next_img)

        self.curr_widg_key = "root"
        self.new_node = None
        self.curr_nod_num = 0

        self.server_nod_lst = []
        self.request_display()

        opt4lay = 3

        if opt4lay == 1:
            # semi Imosflm: vertical at the mid left
            self.nxt_2do_layout = self.window.SmallVertiNext2RunLayout
            self.do_next_one = self.do_another_thing
            self.do_next_two = self.do_one_thing
            self.width4labl = 35
            self.nxt_but_stl = Qt.ToolButtonTextBesideIcon

        elif opt4lay == 2:
            # Next steps are placed horizontal at the bottom
            self.nxt_2do_layout = self.window.HorizNext2RunLayout
            self.do_next_one = self.do_another_thing
            self.do_next_two = self.do_one_thing
            self.width4labl = 5
            self.nxt_but_stl = Qt.ToolButtonTextBesideIcon

        else:
            # Imosflm style: vertical at the left
            self.nxt_2do_layout = self.window.VertNext2RunLayout
            self.do_next_one = self.do_one_thing
            self.do_next_two = self.do_another_thing
            self.width4labl = 20
            self.nxt_but_stl = Qt.ToolButtonTextUnderIcon

        self.change_widget(self.curr_widg_key)
        self.thrd_lst = []

        #self.window.MainHSplitter.setStretchFactor(2, 3)
        #self.window.LeftVSplitter.setStretchFactor(1, 2)

        self.parent_app.aboutToQuit.connect(self.close_event)

        self.window.actionExit.triggered.connect(self.exit_triggered)
        self.window.actionReset_Control_Graph.triggered.connect(
            self.reset_graph_triggered
        )
        self.window.actionBright_on_off.triggered.connect(
            self.bright_fonts_triggered
        )

        self.window.actionArrowhead.triggered.connect(
            self.arrowhead_triggered
        )
        self.window.actionSharpTurns.triggered.connect(
            self.sharp_turns_triggered
        )
        self.window.show()
        self.import_init()

    def sharp_turns_triggered(self):
        self.sharp_turns_on = not self.sharp_turns_on
        self.tree_scene.set_sharp_turns(self.sharp_turns_on)

    def arrowhead_triggered(self):
        self.arrowhead_on = not self.arrowhead_on
        self.tree_scene.set_arrowhead(self.arrowhead_on)

    def bright_fonts_triggered(self):
        self.regular_colours = not self.regular_colours
        self.log_show.set_colours(self.regular_colours)
        self.tree_scene.set_colours(self.regular_colours)
        self.r_index_widg.set_colours(self.regular_colours)

        self.refresh_output()
        self.tree_scene.try_draw_all()

    def exit_triggered(self):
        logging.info("exit_triggered(QObject)")
        msgBox  = QMessageBox()
        txt_exit =  "If you are closing by accident,"
        txt_exit += " you don\'t need to worry.    \n"
        txt_exit += "Just launch Dui2 again and "
        txt_exit += "it will pickup just where it left off.  "
        msgBox.setText(txt_exit)
        msgBox.exec()
        self.parent_app.exit()

    def close_event(self):
        logging.info("aboutToQuit ... 1")
        self.recip_latt.quit_kill_all()
        cmd = {"nod_lst":"", "cmd_lst":["closed"]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = self.runner_handler
        )
        resp = lst_req.result_out()
        logging.info("aboutToQuit ... 2")

    def import_init(self):
        loop = QEventLoop()
        QTimer.singleShot(200, loop.quit)
        loop.exec_()
        if len(self.server_nod_lst) == 1:
            self.nxt_key_clicked("import")

        else:
            big_nod_num = 0
            for node in self.server_nod_lst:
                if node["number"] > big_nod_num:
                    big_nod_num = node["number"]

            self.on_node_click(big_nod_num)

    def launch_reindex(self, sol_rei):
        try:
            is_same = self.new_node.set_custom_parameter(str(sol_rei))

        except AttributeError:
            is_same = False

        if is_same:
            logging.info("clicked twice same row, launching reindex")
            self.request_launch()

    def img_num_changed(self):
        new_img_num = self.window.ImgNumEdit.text()
        self.refresh_output()

    def shift_img_num(self, sh_num):
        img_num = int(self.window.ImgNumEdit.text())
        img_num += sh_num
        self.window.ImgNumEdit.setText(str(img_num))
        self.img_num_changed()

    def prev_img(self):
        logging.info("prev_img")
        self.shift_img_num(-1)

    def next_img(self):
        logging.info("next_img")
        self.shift_img_num(1)

    def refresh_output(self, tab_index = None):
        if tab_index == None:
            tab_index = self.window.OutputTabWidget.currentIndex()

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
                logging.info("(empty) update_tmp_mask()")

            self.do_image_view.update_tmp_mask(lst_tmp_par)

            try:
                if(
                    self.new_node is not None and
                    self.new_node.m_cmd_lst[0] == "dials.generate_mask" and
                    self.new_node.number == self.curr_nod_num
                ):
                    self.do_image_view.set_drag_mode(mask_mode = True)

                else:
                    self.do_image_view.set_drag_mode(mask_mode = False)

            except IndexError:
                    self.do_image_view.set_drag_mode(mask_mode = False)

            try:
                img_num = int(self.window.ImgNumEdit.text())

            except ValueError:
                img_num = 0

            self.do_image_view(in_img_num = img_num, nod_or_path = fnd_cur_nod)

        elif tab_index == 1:
            try:
                nod_stat = self.server_nod_lst[self.curr_nod_num]["status"]

            except IndexError:
                nod_stat = "Busy"

            self.log_show(
                self.curr_nod_num, do_request = fnd_cur_nod, stat = nod_stat
            )

        elif tab_index == 2:
            self.do_load_html(do_request = fnd_cur_nod)

        elif tab_index == 3 and self.window.ReLauncCheckBox.isChecked():
            self.recip_latt.quit_kill_all()
            self.recip_latt.change_node(self.curr_nod_num)

        if(
            self.curr_outp_tab == 3 and
            tab_index != 3 and
            self.window.ReLauncCheckBox.isChecked()
        ):
            self.recip_latt.quit_kill_all()

        self.curr_outp_tab = tab_index

    def RecipLattOpenClicked(self):
        logging.info("RecipLattOpenClicked")
        self.recip_latt.launch_RL_view(self.curr_nod_num)

    def verify_nod_num(self, loaded_nod_num):
        if self.curr_nod_num == loaded_nod_num:
            self.recip_latt.do_launch_RL()

        else:
            self.recip_latt.quit_kill_all()
            self.recip_latt.launch_RL_view(self.curr_nod_num)

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
        self.curr_nod_num = node_numb
        try:
            cur_nod = self.server_nod_lst[node_numb]

        except IndexError:
            cur_nod = self.tree_scene.nod_lst_2_paint[node_numb]

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
                lst_req = get_req_json_dat(
                    params_in = cmd, main_handler = self.runner_handler
                )

                try:
                    self.best_rd_idx_opt = int(cur_nod["cmd2show"][1]) - 1

                except IndexError:
                    row_str = self.new_node.get_full_command_list()[0][14:]
                    new_node_row = int(row_str)
                    self.best_rd_idx_opt = new_node_row - 1

                json_data_lst = lst_req.result_out()
                self.r_index_widg.add_opts_lst(
                    json_data = json_data_lst[0],
                    selected_pos = self.best_rd_idx_opt
                )
                self.update_reindex_table_header(cur_nod["parent_node_lst"])

        except KeyError:
            try:
                if key2find in self.opt_cmd_lst:
                    self.change_widget("optional")
                    self.update_all_param()

                else:
                    logging.info("command widget not there yet")
                    return

            except KeyError:
                logging.info("Key Err Catch (clicked_4_navigation) ")
                return

        self.refresh_output()
        self.display()

    def on_node_click(self, node_numb):
        if (
            self.new_node is not None and

            node_numb != self.curr_nod_num and
            node_numb != self.new_node.number and
            self.window.NodeSelecCheck.checkState() and
            self.server_nod_lst[node_numb]["status"] == "Succeeded" and
            self.new_node.m_cmd_lst == ["dials.combine_experiments"]
        ):
            self.new_node.add_or_remove_parent(node_numb)
            self.display()

        else:
            self.clicked_4_navigation(node_numb)

    def on_hide_click(self, node_numb):
        if node_numb in self.lst2exl:
            self.lst2exl.remove(int(node_numb))

        else:
            self.lst2exl.append(int(node_numb))

        self.display()

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
        self.clearLayout(self.nxt_2do_layout)

        self.do_next_one()
        self.do_next_two()


    def do_one_thing(self):
        try:
            str_key = self.server_nod_lst[self.curr_nod_num]["cmd2show"][0][6:]
            self.update_nxt_butt(str_key)

        except (IndexError, AttributeError):
            logging.info("NO need to run << update_nxt_butt >>")

    def do_another_thing(self):
        self.nxt_2do_layout.addWidget(
            QLabel(" " * self.width4labl + "\n" + " " * self.width4labl)
        )
        self.nxt_2do_layout.addStretch()

    def update_nxt_butt(self, str_key):
        small_f_size = int(self.font_point_size * 0.75)
        small_font = QFont("OldEnglish", pointSize = small_f_size, italic=True)
        try:
            if(
                self.server_nod_lst[self.curr_nod_num]["status"] == "Succeeded"
            ):
                fnd_nxt_cmd = find_next_cmd(
                    self.server_nod_lst,
                    self.server_nod_lst[self.curr_nod_num]["parent_node_lst"],
                    str_key, self.param_widgets, self.opt_cmd_lst
                )
                nxt_cmd_lst = fnd_nxt_cmd.get_nxt_cmd()
                for bt_str in nxt_cmd_lst:
                    emt_lin = " " * 22 + "\u00A0"
                    split_label = (2 - bt_str.count("_")) * (emt_lin + "\n")
                    split_label += bt_str.replace("_", "\n")
                    split_label += "\n" + emt_lin
                    nxt_butt = QToolButton()
                    nxt_butt.setToolButtonStyle(self.nxt_but_stl)
                    nxt_butt.setText(split_label)
                    nxt_butt.cmd_str = bt_str
                    nxt_butt.setFont(small_font)
                    nxt_butt.clicked.connect(self.nxt_clicked)
                    nxt_butt.setIcon(self.param_widgets[bt_str]["icon"])
                    nxt_butt.setIconSize(QSize(38, 42))

                    self.nxt_2do_layout.addWidget(nxt_butt, stretch = 8)

        except IndexError:
            logging.info("no need to add next button Index Err Catch")
            print(" >>> here IndexError <<<")
        tmp_off = '''
        except KeyError:
            logging.info("no need to add next button Key Err Catch")
        '''

    def nxt_clicked(self):
        self.nxt_key_clicked(self.sender().cmd_str)

    def update_reindex_table_header(self, nod_lst):
        cmd = {"nod_lst":nod_lst, "cmd_lst":["display_log"]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = self.runner_handler
        )
        json_log = lst_req.result_out()
        try:
            lst_log_lines = json_log[0]
            label2update = get_label_from_str_list(lst_log_lines)

        except TypeError:
            label2update = " Error Loading Log"

        self.window.ReindexHeaderLabel.setText(label2update)

    def nxt_key_clicked(self, str_key):
        logging.info("nxt_clicked ... str_key: " + str_key)

        if str_key == "reindex":
            cmd = {
                "nod_lst":[self.curr_nod_num],
                "cmd_lst":["get_bravais_sum"]
            }
            lst_req = get_req_json_dat(
                params_in = cmd, main_handler = self.runner_handler
            )
            json_data_lst = lst_req.result_out()
            self.r_index_widg.add_opts_lst(
                json_data = json_data_lst[0]
            )
            self.best_rd_idx_opt = self.r_index_widg.get_best_opt()
            self.update_reindex_table_header([self.curr_nod_num])

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
        self.window.RunPedictAndReportCheckBox.setChecked(
            check_if_predict_n_report(str_key)
        )

    def reset_param(self):
        self.reseting = True
        self.param_widgets[self.curr_widg_key]["simple"].reset_pars()
        try:
            self.param_widgets[self.curr_widg_key]["advanced"].reset_pars()

        except AttributeError:
            logging.info("No advanced pars")

        self.reseting = False

    def reset_new_node(self):
        self.new_node.reset_all_params()
        self.reset_param()
        try:
            simpl_widg = self.param_widgets[self.curr_widg_key]["simple"]
            new_full_list = simpl_widg.build_full_list()
            self.tmp_mask_changed(new_full_list)

        except AttributeError:
            logging.info("this node does not need build_full_list")

    def all_items_param_changed(self, lst_of_lst):
        try:
            if self.new_node.number == self.curr_nod_num:
                self.new_node.reset_all_params()
                self.new_node.set_all_parameters(lst_of_lst)

        except AttributeError:
            logging.info(
                "Not updating parameters, no (green node or twin widget)\n"
            )

    def new_main_command_changed(self, new_cmd_str):
        try:
            if self.new_node.number == self.curr_nod_num:
                self.new_node.reset_all_params()
                self.new_node.set_new_main_command(new_cmd_str)

        except AttributeError:
            logging.info(
                "Not updating parameters, no (green node or twin widget)"
            )

    def item_param_changed(
        self, str_path = None, str_value = None, lst_num = 0
    ):
        self.sender().twin_widg.update_param(str_path, str_value)
        try:
            if(
                self.curr_nod_num == self.new_node.number
                and not self.reseting
            ):
                self.new_node.set_parameter(str_path, str_value, lst_num)

        except AttributeError:
            logging.info(
                "Not updating parameters, no (green node or twin widget)"
            )

    def add_new_node(self):
        logging.info("add_new_node")
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

        if local_main_cmd == ['dials.merge']:
            self.param_widgets[self.curr_widg_key]["simple"].reset_pars()

        cmd = {
            "nod_lst":self.new_node.parent_node_lst, "cmd_lst":["get_lambda"]
        }
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = self.runner_handler
        )
        json_lamb = lst_req.result_out()
        try:
            lamb = json_lamb[0]
            if lamb < 0.05:
                self.param_widgets[self.curr_widg_key]["simple"].set_ed_pars()

        except (TypeError, IndexError, AttributeError):
            logging.info(" Err Catch Loading Lamda")

        if local_main_cmd == ['dials.reindex']:
            self.r_index_widg.opt_clicked(self.best_rd_idx_opt, 1)

    def search_in_parent_nodes_exp(self):
        try:
            fnd_scl_cmd = find_scale_cmd(
                self.server_nod_lst, self.new_node.parent_node_lst
            )
            fnd_scl = fnd_scl_cmd.founded_scale()

        except AttributeError:
            logging.info("Attribute Err Catch (search_in_parent_nodes_exp)")
            fnd_scl = False

        self.expr_widg.is_scale_parent1(fnd_scl)

    def search_in_parent_nodes_mer(self):
        try:
            fnd_scl_cmd = find_scale_cmd(
                self.server_nod_lst, self.new_node.parent_node_lst
            )
            fnd_scl = fnd_scl_cmd.founded_scale()

        except AttributeError:
            logging.info("Attribute Err Catch (search_in_parent_nodes_mer)")
            fnd_scl = False

        self.merg_widg.is_scale_parent2(fnd_scl)

    def update_all_param(self):
        tmp_cmd_par = CommandParamControl()
        self.reset_param()
        try:
            tmp_cmd_par.clone_from_list(
                self.server_nod_lst[self.curr_nod_num]["lst2run"]
            )
            logging.info("\n Updating parameters from server_nod_lst")

        except IndexError:
            tmp_cmd_par = self.new_node
            logging.info("\n Updating parameters from ...new_node")

        self.param_widgets[self.curr_widg_key]["simple"].update_all_pars(
            tmp_cmd_par.get_all_params()
        )
        try:
            self.param_widgets[self.curr_widg_key]["advanced"].update_all_pars(
                tmp_cmd_par.get_all_params()
            )
        except AttributeError:
            logging.info("No advanced pars")

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
            logging.info("no need to gray 'None' widget")

        self.window.ClearParentButton.setEnabled(False)
        self.window.RetryButton.setEnabled(False)
        self.window.CmdSend2server.setEnabled(False)
        self.window.ReqStopButton.setEnabled(False)
        self.window.Reset2DefaultPushButton.setEnabled(False)

        if tmp_state == "Ready":
            logging.info("only run (R)")
            self.window.CmdSend2server.setEnabled(True)
            self.param_widgets[str_key]["simple"].setEnabled(True)
            self.window.ClearParentButton.setEnabled(True)
            try:
                self.param_widgets[str_key]["advanced"].setEnabled(True)

            except AttributeError:
                logging.info("no need to un-gray 'None' widget")

            self.window.Reset2DefaultPushButton.setEnabled(True)

        elif tmp_state == "Busy":
            logging.info("only clone or stop (B)")
            self.window.RetryButton.setEnabled(True)
            self.window.ReqStopButton.setEnabled(True)

        else:
            logging.info("only clone (F or S)")
            self.window.RetryButton.setEnabled(True)

        self.check_if_exported_or_merged()

    def check_if_exported_or_merged(self):
        try:
            if self.curr_widg_key == "export":
                my_widg = self.expr_widg

            elif self.curr_widg_key == "merge":
                my_widg = self.merg_widg

            else:
                my_widg = None

            if(
                self.server_nod_lst[self.curr_nod_num][
                    "status"
                ]  == "Succeeded"
            ):
                enabl = True

            else:
                enabl = False

        except IndexError:
            enabl = False

        try:
            my_widg.set_download_stat(
                do_enable = enabl, nod_num = self.curr_nod_num
            )

        except (AttributeError, UnboundLocalError):
            logging.info("it seems neither export or merge node")

    def display(self):
        self.tree_scene.draw_tree_graph(
            nod_lst_in = self.server_nod_lst,
            curr_nod_num = self.curr_nod_num,
            new_node = self.new_node,
            lst2exl_in = self.lst2exl
        )
        self.gray_n_ungray()

    def request_display(self):
        cmd = {"nod_lst":"", "cmd_lst":["display"]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = self.runner_handler
        )
        self.server_nod_lst = lst_req.result_out()
        self.display()

    def on_clone(self):
        logging.info("on_clone")
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

        if(
            self.param_widgets[self.curr_widg_key]["main_cmd"]
            == ['dials.reindex']
        ):
            self.r_index_widg.opt_clicked(self.best_rd_idx_opt, 1)

    def request_launch(self):
        cmd_lst = self.new_node.get_full_command_list()
        lst_of_node_str = self.new_node.parent_node_lst
        cmd = {'nod_lst': lst_of_node_str, 'cmd_lst': cmd_lst}
        self.log_show.clear_4_run()
        do_predictions_n_report = bool(
            self.window.RunPedictAndReportCheckBox.checkState()
        )
        post_thread = post_req_w_output(
            cmd_in = cmd, do_pred_n_rept = do_predictions_n_report,
            main_handler = self.runner_handler
        )
        post_thread.new_line_out.connect(self.log_show.add_line)
        post_thread.first_line.connect(self.line_n1_in)
        post_thread.about_to_end.connect(self.after_thread_end)
        post_thread.finished.connect(self.post_ended)
        post_thread.start()
        self.thrd_lst.append(post_thread)

    def line_n1_in(self, nod_num_in):
        self.request_display()
        self.new_node = None

    def req_stop(self):
        logging.info("req_stop")
        nod_lst = [str(self.curr_nod_num)]
        #cmd = {"nod_lst":nod_lst, "cmd_lst":[["stop"]]}
        cmd = {"nod_lst":nod_lst, "cmd_lst":["stop"]}

        post_thread = post_req_w_output(
            cmd_in = cmd, main_handler = self.runner_handler
        )
        post_thread.finished.connect(self.post_ended)
        post_thread.start()
        self.thrd_lst.append(post_thread)

    def reset_graph_triggered(self):
        logging.info("reset_graph_triggered(QObject)")
        cmd = {"nod_lst":"", "cmd_lst":["reset_graph"]}
        logging.info("cmd =" + str(cmd))
        try:
            self.do_load_html.reset_lst_html()
            post_thread = post_req_w_output(
                cmd_in = cmd, main_handler = self.runner_handler
            )
            post_thread.first_line.connect(self.respose_n1_from_reset)
            post_thread.finished.connect(self.post_ended)
            post_thread.start()
            self.thrd_lst.append(post_thread)

        except requests.exceptions.RequestException:
            logging.info(
                "something went wrong with the << reset_graph >> request"
            )
            #TODO: put inside this [except] some way to kill [post_thread]

    def respose_n1_from_reset(self, line):
        logging.info("respose_from_reset(err code):" + str(line))

    def after_thread_end(self, nod_num_out, do_pred_n_rept):
        if do_pred_n_rept:
            cmd = {"nod_lst":[nod_num_out], "cmd_lst":["run_predict_n_report"]}
            self.do_load_html.reset_lst_html()
            new_thrd = post_req_w_output(
                cmd_in = cmd, main_handler = self.runner_handler
            )
            new_thrd.finished.connect(self.refresh_output)
            new_thrd.start()
            self.thrd_lst.append(new_thrd)

        else:
            self.refresh_output()

    def post_ended(self):
        self.request_display()
        self.check_nxt_btn()

