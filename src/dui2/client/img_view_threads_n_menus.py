"""
DUI2's image visualization menus and loading threads

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

import sys, os, logging

from dui2.shared_modules.qt_libs import *

import numpy as np
import json, time

from dui2.client.init_firts import ini_data
from dui2.client.exec_utils import (
    get_req_json_dat, get_request_real_time
)

from dui2.client.img_view_utils import (
    load_img_json_w_str, load_mask_img_json_w_str
)

class LoadFullMaskImage(QThread):
    image_loaded = Signal(tuple)
    def __init__(
        self, unit_URL = None, cur_nod_num = None, cur_img_num = None,
        path_in = None, thrs_pars_in = None, main_handler = None
    ):
        super(LoadFullMaskImage, self).__init__()
        self.uni_url = unit_URL   #TODO: check if this variable is needed here
        self.cur_nod_num = cur_nod_num
        self.cur_img_num = cur_img_num
        self.exp_path = path_in
        self.thrs_hld_pars = thrs_pars_in
        self.my_handler = main_handler

    def run(self):
        np_full_img = load_mask_img_json_w_str(
            self.uni_url,
            nod_num_lst = [self.cur_nod_num],
            img_num = self.cur_img_num,
            exp_path = self.exp_path,
            threshold_params = self.thrs_hld_pars,
            main_handler = self.my_handler,
        )
        self.image_loaded.emit(
            (self.cur_nod_num, self.cur_img_num, np_full_img)
        )


class LoadSliceMaskImage(QThread):
    progressing = Signal(int)
    slice_loaded = Signal(dict)
    def __init__(
        self, unit_URL = None, nod_num_lst = None,
        img_num = None, inv_scale = None,
        x1 = None, y1 = None, x2 = None, y2 = None,
        path_in = None, thrs_pars_in = None, main_handler = None
    ):
        super(LoadSliceMaskImage, self).__init__()
        self.uni_url =       unit_URL     #TODO: check if this variable is needed here
        self.nod_num_lst =   nod_num_lst
        self.img_num =       img_num
        self.inv_scale =     inv_scale
        self.x1 =            x1
        self.y1 =            y1
        self.x2 =            x2
        self.y2 =            y2
        self.exp_path =      path_in
        self.thrs_hld_pars = thrs_pars_in
        self.my_handler =    main_handler

    def run(self):
        logging.info("LoadSliceMaskImage.thrs_hld_pars =" + str(self.thrs_hld_pars))
        if self.thrs_hld_pars is None:
            my_cmd_lst = [
                "gmis", str(self.img_num),
                "inv_scale=" + str(self.inv_scale),
                "view_rect=" + str(self.x1) + "," + str(self.y1) +
                         "," + str(self.x2) + "," + str(self.y2)
            ]
            my_cmd = {"nod_lst" : self.nod_num_lst,
                      "path"    : self.exp_path,
                      "cmd_str" : my_cmd_lst}

        else:
            params_str = str(self.thrs_hld_pars)
            my_cmd = {
                'nod_lst': self.nod_num_lst,
                'path': self.exp_path,
                'cmd_str': [
                    'gtmis', str(self.img_num),
                    'inv_scale=' + str(self.inv_scale),
                    'view_rect=' + str(self.x1) + "," + str(self.y1) +
                             "," + str(self.x2) + "," + str(self.y2),
                    'params=' + params_str
                ]
            }

        self.r_time_req = get_request_real_time(
            params_in = my_cmd, main_handler = self.my_handler
        )
        self.r_time_req.prog_new_stat.connect(self.emit_progr)
        self.r_time_req.load_ended.connect(self.emit_n_end)
        self.r_time_req.start()

    def emit_progr(self, percent_progr):
        self.progressing.emit(percent_progr)

    def emit_n_end(self, byte_json):
        try:
            d1d2_n_arr1d = np.frombuffer(byte_json, dtype = float)
            d1 = int(d1d2_n_arr1d[0])
            d2 = int(d1d2_n_arr1d[1])
            np_array_out = d1d2_n_arr1d[2:].reshape(d1, d2)
        except TypeError:
            np_array_out = None

        self.slice_loaded.emit(
            {
                "slice_image" :  np_array_out,
                "inv_scale"   :  self.inv_scale,
                "x1"          :  self.x1,
                "y1"          :  self.y1,
                "x2"          :  self.x2,
                "y2"          :  self.y2
            }
        )


class LoadFullImage(QThread):
    image_loaded = Signal(tuple)
    def __init__(
        self, unit_URL = None, cur_nod_num = None,
        cur_img_num = None, path_in = None, main_handler = None
    ):
        super(LoadFullImage, self).__init__()
        self.uni_url = unit_URL
        self.cur_nod_num = cur_nod_num
        self.cur_img_num = cur_img_num
        self.exp_path = path_in
        self.my_handler = main_handler

    def run(self):
        np_full_img = load_img_json_w_str(
            self.uni_url,
            nod_num_lst = [self.cur_nod_num],
            img_num = self.cur_img_num,
            exp_path = self.exp_path,
            main_handler = self.my_handler
        )
        self.image_loaded.emit(
            (self.cur_nod_num, self.cur_img_num, np_full_img)
        )


class LoadSliceImage(QThread):
    progressing = Signal(int)
    slice_loaded = Signal(dict)
    def __init__(
        self, nod_num_lst = None, img_num = None, inv_scale = None,
        x1 = None, y1 = None, x2 = None, y2 = None,
        path_in = None, main_handler = None
    ):
        super(LoadSliceImage, self).__init__()
        self.nod_num_lst =   nod_num_lst
        self.img_num =       img_num
        self.inv_scale =     inv_scale
        self.x1 =            x1
        self.y1 =            y1
        self.x2 =            x2
        self.y2 =            y2
        self.exp_path =      path_in
        self.my_handler =    main_handler

    def run(self):
        logging.info("loading slice of image")
        my_cmd_lst = [
            "gis", str(self.img_num),
            "inv_scale=" + str(self.inv_scale),
            "view_rect=" + str(self.x1) + "," + str(self.y1) +
                      "," + str(self.x2) + "," + str(self.y2)
        ]
        my_cmd = {"nod_lst" : self.nod_num_lst,
                  "path"    : self.exp_path,
                  "cmd_str" : my_cmd_lst}

        self.r_time_req = get_request_real_time(
            params_in = my_cmd, main_handler = self.my_handler
        )
        self.r_time_req.prog_new_stat.connect(self.emit_progr)
        self.r_time_req.load_ended.connect(self.emit_n_end)
        self.r_time_req.start()

    def emit_progr(self, percent_progr):
        self.progressing.emit(percent_progr)

    def emit_n_end(self, byte_json):
        try:
            d1d2_n_arr1d = np.frombuffer(byte_json, dtype = float)
            d1 = int(d1d2_n_arr1d[0])
            d2 = int(d1d2_n_arr1d[1])
            np_array_out = d1d2_n_arr1d[2:].reshape(d1, d2)

        except TypeError:
            np_array_out = None

        except ValueError:
            np_array_out = None

        self.slice_loaded.emit(
            {
                "slice_image" :  np_array_out,
                "inv_scale"   :  self.inv_scale,
                "x1"          :  self.x1,
                "y1"          :  self.y1,
                "x2"          :  self.x2,
                "y2"          :  self.y2
            }
        )


class LoadInThread(QThread):
    request_loaded = Signal(tuple)
    def __init__(
        self, unit_URL = None, cmd_in = None, main_handler = None
    ):
        super(LoadInThread, self).__init__()
        self.uni_url = unit_URL
        self.cmd = cmd_in
        self.my_handler = main_handler

    def run(self):
        lst_req = get_req_json_dat(
            params_in = self.cmd, main_handler = self.my_handler
        )
        response = lst_req.result_out()
        self.request_loaded.emit((response))


class DispersionParamWidget(QWidget):
    def __init__(self, default_params_in):
        super(DispersionParamWidget, self).__init__()
        default_threshold_params = default_params_in
        self.param_nsig_b = QLineEdit(
            str(default_threshold_params["nsig_b"])
        )
        self.param_nsig_s = QLineEdit(
            str(default_threshold_params["nsig_s"])
        )
        self.param_global_threshold = QLineEdit(
            str(default_threshold_params["global_threshold"])
        )
        self.param_min_count = QLineEdit(
            str(default_threshold_params["min_count"])
        )
        self.param_gain = QLineEdit(str(default_threshold_params["gain"]))
        self.param_size = QLineEdit(
            str(default_threshold_params["size"][0]) + "," +
            str(default_threshold_params["size"][1])
        )

        hbox_nsig_b = QHBoxLayout()
        hbox_nsig_s = QHBoxLayout()
        hbox_global_threshold = QHBoxLayout()
        hbox_min_count = QHBoxLayout()
        hbox_gain = QHBoxLayout()
        hbox_size = QHBoxLayout()
        hbox_nsig_b.addWidget(QLabel("Sigma background"))
        hbox_nsig_s.addWidget(QLabel("Sigma strong"))
        hbox_global_threshold.addWidget(QLabel("Global threshold"))
        hbox_min_count.addWidget(QLabel("Min local"))
        hbox_gain.addWidget(QLabel("Gain"))
        hbox_size.addWidget(QLabel("Kernel size"))
        hbox_nsig_b.addWidget(self.param_nsig_b)
        hbox_nsig_s.addWidget(self.param_nsig_s)
        hbox_global_threshold.addWidget(self.param_global_threshold)
        hbox_min_count.addWidget(self.param_min_count)
        hbox_gain.addWidget(self.param_gain)
        hbox_size.addWidget(self.param_size)

        v_left_box = QVBoxLayout()
        v_left_box.addLayout(hbox_nsig_b)
        v_left_box.addLayout(hbox_nsig_s)
        v_left_box.addLayout(hbox_global_threshold)

        v_centr_box = QVBoxLayout()
        v_centr_box.addLayout(hbox_min_count)
        v_centr_box.addLayout(hbox_gain)
        v_centr_box.addLayout(hbox_size)

        center_h_box = QHBoxLayout()
        center_h_box.addLayout(v_left_box)
        center_h_box.addLayout(v_centr_box)
        self.setLayout(center_h_box)


class RadialParamWidget(QWidget):
    def __init__(self):
        super(RadialParamWidget, self).__init__()
        #FIXME it should use << default_threshold_params >> here
        self.param_n_iqr = QLineEdit("6")

        self.param_blur_select = QComboBox()
        self.blur_lst = [None, "narrow", "wide"]
        for n, blr in enumerate(self.blur_lst):
            self.param_blur_select.addItem(str(blr))

        self.param_n_bins = QLineEdit("100")

        hbox_rad_niqr = QHBoxLayout()
        hbox_rad_niqr.addWidget(QLabel("IQR multiplier"))
        hbox_rad_niqr.addWidget(self.param_n_iqr)
        hbox_rad_blur = QHBoxLayout()
        hbox_rad_blur.addWidget(QLabel("blur"))
        hbox_rad_blur.addWidget(self.param_blur_select)
        hbox_rad_nbin = QHBoxLayout()
        hbox_rad_nbin.addWidget(QLabel("N bins"))
        hbox_rad_nbin.addWidget(self.param_n_bins)

        v_right_box = QVBoxLayout()
        v_right_box.addLayout(hbox_rad_niqr)
        v_right_box.addLayout(hbox_rad_blur)
        v_right_box.addLayout(hbox_rad_nbin)

        self.setLayout(v_right_box)


class ThresholdDisplayMenu(QMenu):
    user_param_pass = Signal()
    new_threshold_param = Signal(dict)
    def __init__(self, parent = None):
        super().__init__()
        my_main_box = QVBoxLayout()
        self.default_threshold_params = {
            "algorithm":"dispersion_extended", "nsig_b":6.0, "nsig_s":3.0,
            "global_threshold":0.0, "min_count":2, "gain":1.0, "size":(3, 3),
            "n_iqr":6, "blur":None,"n_bins":100
        }

        hbox_algorithm = QHBoxLayout()
        hbox_algorithm.addWidget(QLabel("Threshold algorithm"))
        self.algorithm_select = QComboBox()
        self.algorithm_lst = ["dispersion_extended", "dispersion", "radial_profile"]
        for n, algo in enumerate(self.algorithm_lst):
            self.algorithm_select.addItem(algo)

        hbox_algorithm.addWidget(self.algorithm_select)
        self.step_param_widg =  QStackedWidget()
        self.rad_par_wig = RadialParamWidget()
        self.step_param_widg.addWidget(self.rad_par_wig)
        self.dispr_par_widg = DispersionParamWidget(
            self.default_threshold_params
        )
        self.step_param_widg.addWidget(self.dispr_par_widg)
        self.user_pass_btn = QPushButton("Apply to spot find")
        my_main_box.addLayout(hbox_algorithm)
        my_main_box.addWidget(self.step_param_widg)
        my_main_box.addWidget(self.user_pass_btn)

        self.rad_par_wig.param_n_iqr.textChanged.connect(
            self.threshold_param_changed
        )
        self.rad_par_wig.param_blur_select.currentIndexChanged.connect(
            self.threshold_param_changed
        )
        self.rad_par_wig.param_n_bins.textChanged.connect(
            self.threshold_param_changed
        )
        self.dispr_par_widg.param_nsig_b.textChanged.connect(
            self.threshold_param_changed
        )
        self.dispr_par_widg.param_nsig_s.textChanged.connect(
            self.threshold_param_changed
        )
        self.dispr_par_widg.param_global_threshold.textChanged.connect(
            self.threshold_param_changed
        )
        self.dispr_par_widg.param_min_count.textChanged.connect(
            self.threshold_param_changed
        )
        self.dispr_par_widg.param_gain.textChanged.connect(
            self.threshold_param_changed
        )
        self.dispr_par_widg.param_size.textChanged.connect(
            self.threshold_param_changed
        )

        self.algorithm_select.currentIndexChanged.connect(
            self.algorithm_changed
        )
        self.user_pass_btn.clicked.connect(self.user_applied)

        self.setLayout(my_main_box)
        self.algorithm_changed()

    def algorithm_changed(self):
        tmp_algo = self.algorithm_lst[int(
            self.algorithm_select.currentIndex()
        )]
        if tmp_algo == "radial_profile":
            self.step_param_widg.setCurrentWidget(self.rad_par_wig)

        else:
            self.step_param_widg.setCurrentWidget(self.dispr_par_widg)

        self.threshold_param_changed(None)

    def threshold_param_changed(self, value):
        #if self.threshold_box_show.isChecked():

        tmp_algo = self.algorithm_lst[int(
            self.algorithm_select.currentIndex()
        )]

        try:
            tmp_nsig_b = float(self.dispr_par_widg.param_nsig_b.text())

        except ValueError:
            tmp_nsig_b = self.default_threshold_params["nsig_b"]

        try:
            tmp_nsig_s = float(self.dispr_par_widg.param_nsig_s.text())

        except ValueError:
            tmp_nsig_s = self.default_threshold_params["nsig_s"]

        #TODO try to restrict to { global_threshold > 0 }
        try:
            tmp_global_threshold = float(self.dispr_par_widg.param_global_threshold.text())

        except ValueError:
            tmp_global_threshold = self.default_threshold_params["global_threshold"]

        try:
            tmp_min_count = int(self.dispr_par_widg.param_min_count.text())

        except ValueError:
            tmp_min_count = self.default_threshold_params["min_count"]

        try:
            tmp_gain = float(self.dispr_par_widg.param_gain.text())

        except ValueError:
            tmp_gain = self.default_threshold_params["gain"]

        lst_size = str(self.dispr_par_widg.param_size.text()).split(",")
        try:
            tmp_size = [int(lst_size[0]), int(lst_size[1])]

        except (ValueError, IndexError):
            tmp_size = self.default_threshold_params["size"]

        self.threshold_params_dict = {
            "algorithm":            tmp_algo,
            "nsig_b":               tmp_nsig_b,
            "nsig_s":               tmp_nsig_s,
            "global_threshold":     tmp_global_threshold,
            "min_count":            tmp_min_count,
            "gain":                 tmp_gain,
            "size":                 tmp_size
        }

        if tmp_algo == "radial_profile":
            try:
                tmp_n_iqr = int(self.rad_par_wig.param_n_iqr.text())

            except ValueError:
                #print("assigning default value to n_iqr ...(ValueError) ")
                tmp_n_iqr = self.default_threshold_params["n_iqr"]

            tmp_blur = self.rad_par_wig.blur_lst[int(
                self.rad_par_wig.param_blur_select.currentIndex()
            )]

            try:
                tmp_n_bins = int(self.rad_par_wig.param_n_bins.text())

            except ValueError:
                tmp_n_bins = self.default_threshold_params["n_bins"]

            self.threshold_params_dict["n_iqr"] = tmp_n_iqr
            self.threshold_params_dict["blur"] = tmp_blur
            self.threshold_params_dict["n_bins"] = tmp_n_bins

        self.new_threshold_param.emit(self.threshold_params_dict)

        old_connected_2_commented_IF = '''
        else:
            self.new_threshold_param.emit(None)
        '''

    def user_applied(self):
        logging.info("user_pass_btn")
        self.user_param_pass.emit()
        self.hide()


class InfoDisplayMenu(QMenu):
    new_i_min_max = Signal(int, int)
    new_palette = Signal(str)
    new_overlay = Signal(str)
    new_mask_colour = Signal(str)
    new_mask_transp = Signal(float)
    new_redraw = Signal()
    new_ref_list = Signal()
    new_mask_y_n = Signal()
    def __init__(self, parent = None):
        super().__init__()
        self.my_parent = parent

        # Palette tuning
        self.i_min = int(self.my_parent.i_min_max[0])
        self.i_max = int(self.my_parent.i_min_max[1])
        self.palette = self.my_parent.palette
        palette_group = QGroupBox("Palette tuning")
        palette_box_layout = QVBoxLayout()
        self.i_min_line = QLineEdit(str(self.i_min))
        self.i_min_line.textChanged.connect(self.i_min_changed)
        self.i_max_line = QLineEdit(str(self.i_max))
        self.i_max_line.textChanged.connect(self.i_max_changed)
        i_min_max_layout = QHBoxLayout()
        i_min_max_layout.addWidget(QLabel("Min(i)"))
        i_min_max_layout.addWidget(self.i_min_line)
        i_min_max_layout.addWidget(QLabel("Max(i)"))
        i_min_max_layout.addWidget(self.i_max_line)
        palette_box_layout.addLayout(i_min_max_layout)

        self.palette_select = QComboBox()
        self.palette_lst = ["grayscale", "invert", "heat", "heat invert"]
        for n, plt in enumerate(self.palette_lst):
            self.palette_select.addItem(plt)
            if plt == self.palette:
                self.palette_select.setCurrentIndex(n)

        self.palette_select.currentIndexChanged.connect(
            self.palette_changed_by_user
        )

        self.overlay_select = QComboBox()
        self.overlay_lst = ["blue", "cyan", "red", "green"]
        for n, plt in enumerate(self.overlay_lst):
            self.overlay_select.addItem(plt)

        self.overlay_select.currentIndexChanged.connect(
            self.overlay_changed_by_user
        )
        palette_h_layout = QHBoxLayout()
        palette_h_layout.addWidget(QLabel(" Image palette "))
        palette_h_layout.addWidget(self.palette_select)
        palette_box_layout.addLayout(palette_h_layout)

        colour_h_layout = QHBoxLayout()
        colour_h_layout.addWidget(QLabel(" Overlayed reflections  "))
        colour_h_layout.addWidget(self.overlay_select)
        palette_box_layout.addLayout(colour_h_layout)

        palette_box_layout.addStretch() #Maybe we will remove this stretch soon

        palette_group.setLayout(palette_box_layout)

        #Mask overlay
        mask_colour_group = QGroupBox("Overlay viewing")
        mask_col_n_tra_v_layout = QVBoxLayout()

        # mask showing
        self.chk_box_mask_show = QCheckBox("Excluding mask")
        self.chk_box_mask_show.setChecked(True)
        self.chk_box_mask_show.stateChanged.connect(self.sig_mask_yes_or_not)
        mask_col_n_tra_v_layout.addWidget(self.chk_box_mask_show)


        # threshold showing
        self.threshold_box_show = QCheckBox("Spot finding threshold")
        self.threshold_box_show.setChecked(False)
        mask_col_n_tra_v_layout.addWidget(self.threshold_box_show)
        self.threshold_box_show.stateChanged.connect(
            self.sig_mask_yes_or_not
        )
        #  ... if self.threshold_box_show.isChecked():



        # mask colouring
        mask_col_h_layout = QHBoxLayout()
        mask_col_h_layout.addWidget(QLabel("colour"))
        self.mask_colour_select = QComboBox()
        self.mask_col_lst = ["red", "green", "blue"]
        for n, plt in enumerate(self.mask_col_lst):
            self.mask_colour_select.addItem(plt)
            if plt == self.palette:
                self.mask_colour_select.setCurrentIndex(n)

        self.mask_colour_select.currentIndexChanged.connect(
            self.mask_colour_changed_by_user
        )
        mask_col_h_layout.addWidget(self.mask_colour_select)

        mask_col_n_tra_v_layout.addLayout(mask_col_h_layout)

        # mask transparency
        mask_tra_h_layout = QHBoxLayout()
        mask_tra_h_layout.addWidget(QLabel("transparency"))
        self.transp_slider = QSlider(Qt.Horizontal)
        self.transp_slider.setMinimum(10)
        self.transp_slider.setMaximum(90)
        self.transp_slider.valueChanged.connect(self.transp_changed)
        mask_tra_h_layout.addWidget(self.transp_slider)
        mask_col_n_tra_v_layout.addLayout(mask_tra_h_layout)
        mask_colour_group.setLayout(mask_col_n_tra_v_layout)

        # hkl Viewing Tool
        info_group = QGroupBox("Reflection info")
        ref_box_layout = QVBoxLayout()
        self.chk_box_show = QCheckBox("Show reflection info")
        self.chk_box_show.setChecked(True)
        self.chk_box_show.stateChanged.connect(self.sig_new_redraw)
        ref_box_layout.addWidget(self.chk_box_show)
        self.rad_but_near_hkl = QRadioButton("Nearest HKL")
        self.rad_but_near_hkl.clicked.connect(self.sig_new_redraw)
        self.rad_but_near_hkl.setChecked(True)
        ref_box_layout.addWidget(self.rad_but_near_hkl)
        self.rad_but_all_hkl = QRadioButton("All HKLs")
        self.rad_but_all_hkl.clicked.connect(self.sig_new_redraw)
        ref_box_layout.addWidget(self.rad_but_all_hkl)
        self.rad_but_none_hkl = QRadioButton("No HKL")
        self.rad_but_none_hkl.clicked.connect(self.sig_new_redraw)
        ref_box_layout.addWidget(self.rad_but_none_hkl)
        info_group.setLayout(ref_box_layout)

        # Find vs Predictions
        find_vs_predict_group = QGroupBox("Reflection Type")
        fnd_vs_prd_layout = QVBoxLayout()
        self.rad_but_obs = QRadioButton("Observation")
        self.rad_but_obs.clicked.connect(self.sig_new_refl)
        self.rad_but_obs.setChecked(True)
        fnd_vs_prd_layout.addWidget(self.rad_but_obs)
        self.rad_but_pred = QRadioButton("Prediction      View Depth")
        self.rad_but_pred.clicked.connect(self.sig_new_refl)
        self.z_dept_combo = QSpinBox(self)
        self.z_dept_combo.setMinimum(1)
        self.z_dept_combo.setMaximum(7)
        self.z_dept_combo.setValue(1)
        self.z_dept_combo.valueChanged.connect(self.sig_new_refl)
        predict_h_layout = QHBoxLayout()
        predict_h_layout.addWidget(self.rad_but_pred)
        predict_h_layout.addWidget(self.z_dept_combo)
        fnd_vs_prd_layout.addLayout(predict_h_layout)
        find_vs_predict_group.setLayout(fnd_vs_prd_layout)

        left_side_box = QVBoxLayout()
        left_side_box.addWidget(palette_group)
        left_side_box.addWidget(mask_colour_group)

        right_side_box = QVBoxLayout()
        right_side_box.addWidget(info_group)
        right_side_box.addWidget(find_vs_predict_group)

        my_main_box = QHBoxLayout()
        my_main_box.addLayout(left_side_box)
        my_main_box.addLayout(right_side_box)

        self.setLayout(my_main_box)

    def sig_new_redraw(self):
        logging.info("new_redraw")
        self.new_redraw.emit()

    def sig_mask_yes_or_not(self):
        self.new_mask_y_n.emit()

    def sig_new_refl(self):
        logging.info("new_ref_list")
        self.new_ref_list.emit()

    def palette_changed_by_user(self, new_palette_num):
        self.palette = self.palette_lst[new_palette_num]
        logging.info("self.palette =" + str(self.palette))
        self.new_palette.emit(str(self.palette))

    def overlay_changed_by_user(self, new_overlay_num):
        self.overlay = self.overlay_lst[new_overlay_num]
        logging.info("self.overlay =" + str(self.overlay))
        self.new_overlay.emit(str(self.overlay))

    def mask_colour_changed_by_user(self, new_colour_number):
        new_colour = self.mask_col_lst[new_colour_number]
        self.new_mask_colour.emit(str(new_colour))

    def transp_changed(self, new_transp_entered):
        new_transp = new_transp_entered / 100.0
        #print("new_transp =", new_transp)
        self.new_mask_transp.emit(float(new_transp))

    def i_min_max_changed(self):
        self.new_i_min_max.emit(self.i_min, self.i_max)

    def i_min_changed(self, value):
        logging.info("i_min_changed; value=" + str(value))
        try:
            self.i_min = int(value)

        except ValueError:
            self.i_min = 0

        self.i_min_max_changed()

    def i_max_changed(self, value):
        logging.info("i_max_changed; value=" + str(value))
        self.i_max = int(value)
        self.i_min_max_changed()

