"""
DUI2's image visualization main programs

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
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtUiTools

import numpy as np
import json, time, requests

from dui2.client.init_firts import ini_data
from dui2.client.exec_utils import (
    get_req_json_dat, get_request_real_time
)
from dui2.client.outputs import HandleLoadStatusLabel

from dui2.client.img_view_utils import (
    crunch_min_max, np2bmp_monocrome, np2bmp_heat, np2bmp_mask,
    load_img_json_w_str, load_mask_img_json_w_str
)

from dui2.client.file_nav_utils import FileBrowser

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

    def say_good_bye(self):
        self.r_time_req.quit()
        self.r_time_req.wait()


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

    def say_good_bye(self):
        self.r_time_req.quit()
        self.r_time_req.wait()


class ImgGraphicsScene(QGraphicsScene):
    img_scale = Signal(float)
    new_mouse_pos = Signal(int, int)
    mouse_pressed = Signal(int, int)
    mouse_released = Signal(int, int)

    def __init__(self, parent = None):
        super(ImgGraphicsScene, self).__init__(parent)
        self.parent_obj = parent
        self.curr_pixmap = None
        self.my_mask_pix_map = None

        self.overlay_pen1 = QPen(
            Qt.white, 0.5, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )

        self.overlay_pen1.setCosmetic(True)

        self.draw_all_hkl = False
        self.draw_near_hkl = True

    def draw_ref_rect(self):
        self.clear()
        if self.my_pix_map is not None:
            self.curr_pixmap = self.my_pix_map

        self.addPixmap(self.curr_pixmap)
        if self.parent_obj.pop_display_menu.rad_but_obs.isChecked():
            tick_size = 10.0
            for refl in self.refl_list:
                rectangle1 = QRectF(
                    refl["x"], refl["y"], refl["width"], refl["height"]
                )
                self.addRect(rectangle1, self.overlay_pen1)

                if refl["x_me_out"]:
                    xp = refl["x"] + refl["width"] / 2.0
                    yp = refl["y"] + refl["height"] / 2.0
                    self.addLine(
                        xp - tick_size, yp - tick_size,
                        xp + tick_size, yp + tick_size,
                        self.overlay_pen1
                    )
                    self.addLine(
                        xp - tick_size, yp + tick_size,
                        xp + tick_size, yp - tick_size,
                        self.overlay_pen1
                    )

        else:
            z_dept_fl = float(self.parent_obj.pop_display_menu.z_dept_combo.value())
            max_size = 6
            for refl in self.refl_list:
                paint_size = max_size - 4.0 * refl["z_dist"] / z_dept_fl
                self.addLine(
                    refl["x"], refl["y"] - paint_size,
                    refl["x"], refl["y"] + paint_size,
                    self.overlay_pen1
                )
                self.addLine(
                    refl["x"] + paint_size, refl["y"],
                    refl["x"] - paint_size, refl["y"],
                    self.overlay_pen1
                )

        if self.my_mask_pix_map is not None:
            self.addPixmap(self.my_mask_pix_map)

    def update_tmp_mask(self, new_temp_mask):
        self.temp_mask = new_temp_mask

    def draw_temp_mask(self):
        try:
            for pict in self.temp_mask:
                lst_str = pict[1].split(",")
                lst_num = []
                for in_str in lst_str:
                    try:
                        lst_num.append(int(in_str))

                    except ValueError:
                        pass

                if pict[0] == 'untrusted.rectangle':
                    tmp_width = lst_num[1] - lst_num[0]
                    tmp_height = lst_num[3] - lst_num[2]
                    x_rect_1 = lst_num[0]
                    y_rect_1 = lst_num[2]
                    rectangle = QRectF(
                        x_rect_1, y_rect_1, tmp_width, tmp_height
                    )
                    self.addRect(rectangle, self.overlay_pen1)

                elif pict[0] == 'untrusted.circle':
                    x_rect_1 = lst_num[0] - lst_num[2]
                    y_rect_1 = lst_num[1] - lst_num[2]
                    side = 2 * lst_num[2]
                    rectangle = QRectF(
                        x_rect_1, y_rect_1, side, side
                    )
                    self.addEllipse(rectangle, self.overlay_pen1)

                elif pict[0] == 'untrusted.polygon':
                    siz_n_blk = (len(lst_num) - 2) / 2
                    if siz_n_blk >= 1:
                        for i in range(int(siz_n_blk)):
                            self.addLine(
                                lst_num[i * 2], lst_num[i * 2 + 1],
                                lst_num[i * 2 + 2], lst_num[i * 2 + 3],
                                self.overlay_pen1
                            )

                elif pict[0] == 'multipanel.rectangle':
                    tmp_width = lst_num[1] - lst_num[0]
                    tmp_height = lst_num[3] - lst_num[2]
                    x_rect_1 = lst_num[0]
                    y_rect_1 = lst_num[2]
                    y_rect_1 += 213 * lst_num[4]
                    rectangle = QRectF(
                        x_rect_1, y_rect_1, tmp_width, tmp_height
                    )
                    self.addRect(rectangle, self.overlay_pen1)

                elif pict[0] == 'multipanel.circle':
                    x_rect_1 = lst_num[0] - lst_num[2]
                    y_rect_1 = lst_num[1] - lst_num[2]
                    side = 2 * lst_num[2]
                    y_rect_1 += 213 * lst_num[3]
                    rectangle = QRectF(
                        x_rect_1, y_rect_1, side, side
                    )
                    self.addEllipse(rectangle, self.overlay_pen1)

        except TypeError:
            pass

    def __call__(self, new_pixmap, refl_list1, new_temp_mask):
        self.my_pix_map = new_pixmap
        self.refl_list = refl_list1
        self.temp_mask = new_temp_mask
        self.refresh_imgs()

    def refresh_imgs(self):
        if self.parent_obj.overlay == "blue":
            overlay_colour1 = Qt.blue

        elif self.parent_obj.overlay == "cyan":
            overlay_colour1 = Qt.cyan

        elif self.parent_obj.overlay == "green":
            overlay_colour1 = Qt.green

        else:
            overlay_colour1 = Qt.red

        self.overlay_pen1 = QPen(
            overlay_colour1, 2.5, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.overlay_pen1.setCosmetic(True)
        self.draw_ref_rect()
        if self.draw_all_hkl:
            for refl in self.refl_list:
                n_text = self.addSimpleText(str(refl["local_hkl"]))
                n_text.setPos(refl["x"], refl["y"])
                n_text.setPen(self.overlay_pen1)

        self.draw_temp_mask()

    def add_mask_pixmap(self, mask_pixmap):
        self.my_mask_pix_map = mask_pixmap

    def wheelEvent(self, event):
        float_delta = float(event.delta())
        new_scale = 1.0 + float_delta / 1500.0
        self.img_scale.emit(new_scale)
        event.accept()

    def mouseMoveEvent(self, event):
        ev_pos = event.scenePos()
        x_pos, y_pos = int(ev_pos.x()), int(ev_pos.y())
        if self.draw_near_hkl == True:
            try:
                pos_min = None
                d_cuad_min = 10000000
                for num, refl in enumerate(self.refl_list):

                    x_ref = refl["x"]
                    y_ref = refl["y"]

                    dx = x_ref - x_pos
                    dy = y_ref - y_pos
                    d_cuad = dx * dx + dy * dy
                    if d_cuad < d_cuad_min:
                        d_cuad_min = d_cuad
                        pos_min = num

                self.draw_ref_rect()
                refl = self.refl_list[pos_min]
                n_text = self.addSimpleText(str(refl["local_hkl"]))
                n_text.setPos(refl["x"], refl["y"])
                n_text.setPen(self.overlay_pen1)

            except (UnboundLocalError, TypeError, AttributeError):
                not_neded_to_log = ''' logging.info(
                    "not found the nearer reflection " +
                    "or not existent reflection list yet"
                )'''
                pass

        self.new_mouse_pos.emit(x_pos, y_pos)

    def mousePressEvent(self, event):
        ev_pos = event.scenePos()
        x_pos, y_pos = int(ev_pos.x()), int(ev_pos.y())
        self.mouse_pressed.emit(x_pos, y_pos)

    def mouseReleaseEvent(self, event):
        ev_pos = event.scenePos()
        x_pos, y_pos = int(ev_pos.x()), int(ev_pos.y())
        self.mouse_released.emit(x_pos, y_pos)


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
        hbox_nsig_b.addWidget(QLabel("nsig_b"))
        hbox_nsig_s.addWidget(QLabel("nsig_s"))
        hbox_global_threshold .addWidget(QLabel("global_threshold"))
        hbox_min_count.addWidget(QLabel("min_count"))
        hbox_gain.addWidget(QLabel("gain"))
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
        self.threshold_box_show = QCheckBox("Show threshold")
        self.threshold_box_show.setChecked(False)
        self.default_threshold_params = {
            "algorithm":"dispersion_extended", "nsig_b":6.0, "nsig_s":3.0,
            "global_threshold":0, "min_count":2, "gain":1.0, "size":(3, 3),
            "n_iqr":6.0, "blur":None,"n_bins":100
        }

        hbox_algorithm = QHBoxLayout()
        hbox_algorithm.addWidget(QLabel("Threshold algorithm"))
        self.algorithm_select = QComboBox()
        self.algorithm_lst = ["dispersion_extended", "dispersion", "radial_profile"]
        for n, algo in enumerate(self.algorithm_lst):
            self.algorithm_select.addItem(algo)

        hbox_algorithm.addWidget(self.algorithm_select)

        #stacked_box = QHBoxLayout()
        self.step_param_widg =  QStackedWidget()


        self.rad_par_wig = RadialParamWidget()
        #stacked_box.addWidget(self.rad_par_wig)
        self.step_param_widg.addWidget(self.rad_par_wig)

        self.dispr_par_widg = DispersionParamWidget(
            self.default_threshold_params
        )
        #stacked_box.addWidget(self.dispr_par_widg)
        self.step_param_widg.addWidget(self.dispr_par_widg)

        self.user_pass_btn = QPushButton("Apply to spot find")

        my_main_box.addWidget(self.threshold_box_show)
        my_main_box.addLayout(hbox_algorithm)
        #my_main_box.addLayout(stacked_box)
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

        self.threshold_box_show.stateChanged.connect(
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
        if self.threshold_box_show.isChecked():

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

            local_threshold_params = {
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
                    tmp_n_iqr = self.default_threshold_params["n_iqr"]

                tmp_blur = self.rad_par_wig.blur_lst[int(
                    self.rad_par_wig.param_blur_select.currentIndex()
                )]

                try:
                    tmp_n_bins = int(self.rad_par_wig.param_n_bins.text())

                except ValueError:
                    tmp_n_bins = self.default_threshold_params["n_bins"]

                local_threshold_params["n_iqr"] = tmp_n_iqr
                local_threshold_params["blur"] = tmp_blur
                local_threshold_params["n_bins"] = tmp_n_bins

            self.new_threshold_param.emit(local_threshold_params)

        else:
            self.new_threshold_param.emit(None)

    def user_applied(self):
        logging.info("user_pass_btn")
        self.user_param_pass.emit()


class InfoDisplayMenu(QMenu):
    new_i_min_max = Signal(int, int)
    new_palette = Signal(str)
    new_overlay = Signal(str)
    new_mask_colour = Signal(str)
    new_mask_transp = Signal(float)
    new_redraw = Signal()
    new_ref_list = Signal()
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


        # mask colouring
        mask_colour_group = QGroupBox("Mask overlay")
        mask_col_n_tra_v_layout = QVBoxLayout()

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


class DoImageView(QObject):
    new_mask_comp = Signal(dict)
    user_pass_threshold_param = Signal(dict)
    new_refl = Signal(int)
    need_2_reload = Signal()

    def __init__(self, parent = None):
        super(DoImageView, self).__init__(parent)
        self.main_obj = parent
        self.my_handler = parent.runner_handler

        data_init = ini_data()
        self.uni_url = data_init.get_url()
        self.l_stat = HandleLoadStatusLabel(self.main_obj)
        self.my_scene = ImgGraphicsScene(self)
        self.main_obj.window.imageView.setScene(self.my_scene)
        self.main_obj.window.imageView.setMouseTracking(True)
        self.set_drag_mode()
        self.set_mask_comp()
        res_ico_path = self.main_obj.ui_dir_path + os.sep + "resources"
        one_one_icon = QIcon()
        one_one_icon_path = res_ico_path + os.sep + "zoom_ono_one_ico.png"
        one_one_icon.addFile(one_one_icon_path, mode = QIcon.Normal)
        self.main_obj.window.ScaleOneOneButton.setIcon(one_one_icon)
        self.main_obj.window.ScaleOneOneButton.clicked.connect(self.OneOneScale)
        zoom_in_icon = QIcon()
        zoom_in_icon_path = res_ico_path + os.sep + "zoom_plus_ico.png"
        zoom_in_icon.addFile(zoom_in_icon_path, mode = QIcon.Normal)
        self.main_obj.window.ZoomInButton.setIcon(zoom_in_icon)
        self.main_obj.window.ZoomInButton.clicked.connect(self.ZoomInScale)
        zoom_out_icon = QIcon()
        zoom_out_icon_path = res_ico_path + os.sep + "zoom_minus_ico.png"
        zoom_out_icon.addFile(zoom_out_icon_path, mode = QIcon.Normal)
        self.main_obj.window.ZoomOutButton.setIcon(zoom_out_icon)
        self.main_obj.window.ZoomOutButton.clicked.connect(self.ZoomOutScale)
        self.main_obj.window.EasterEggButton.clicked.connect(self.easter_egg)

        data_init = ini_data()
        self.run_local = data_init.get_if_local()
        if self.run_local:
            self.easter_egg_active = False

        else:
            self.easter_egg_active = True

        self.i_min_max = [-2, 50]
        self.palette = "grayscale"
        self.just_imported = False
        self.overlay = "blue"

        self.pop_threshold_menu = ThresholdDisplayMenu(self)
        try:
            self.main_obj.window.ThresholdButton.setMenu(self.pop_threshold_menu)
            self.pop_threshold_menu.new_threshold_param.connect(
                self.update_threshold_params
            )
            self.pop_threshold_menu.user_param_pass.connect(self.user_applied)

        except AttributeError:
            self.pop_threshold_menu.deleteLater()

        self.pop_display_menu = InfoDisplayMenu(self)
        self.main_obj.window.DisplayButton.setMenu(self.pop_display_menu)
        self.pop_display_menu.new_i_min_max.connect(self.change_i_min_max)
        self.pop_display_menu.new_palette.connect(self.change_palette)
        self.pop_display_menu.new_overlay.connect(self.change_overlay)

        self.pop_display_menu.new_mask_colour.connect(self.change_mask_colour)
        self.mask_colour = "red"

        self.pop_display_menu.new_mask_transp.connect(self.change_mask_transp)
        self.mask_transp = 0.5

        self.pop_display_menu.new_redraw.connect(self.refresh_pixel_map)

        self.pop_display_menu.new_ref_list.connect(
            self.request_reflection_list
        )
        self.my_scene.img_scale.connect(self.scale_img)
        self.my_scene.new_mouse_pos.connect(self.on_mouse_move)
        self.my_scene.mouse_pressed.connect(self.on_mouse_press)
        self.my_scene.mouse_released.connect(self.on_mouse_release)

        self.bmp_heat = np2bmp_heat()
        self.bmp_m_cro = np2bmp_monocrome()
        self.bmp_mask = np2bmp_mask()

        self.cur_img_num = None
        self.cur_nod_num = None
        self.img_d1_d2 = (None, None)
        self.inv_scale = 1
        self.full_image_loaded = False
        self.img_path = "?"

        (self.old_x1, self.old_y1, self.old_x2, self.old_y2) = (-1, -1, -1, -1)
        self.old_inv_scl = self.inv_scale
        self.old_nod_num = self.cur_nod_num
        self.old_img_num = self.cur_img_num

        self.list_temp_mask = None

        self.threshold_params = None
        self.old_threshold_params = None


        timer = QTimer(self)
        timer.timeout.connect(self.check_move)
        timer.start(1600)

    def __call__(
        self, in_img_num, nod_or_path = True,
        on_filter_reflections = False
    ):
        self.cur_img_num = in_img_num
        self.nod_or_path = nod_or_path
        self.exp_path = None
        self.on_filter_reflections = on_filter_reflections
        self.build_background_n_get_nod_num(self.cur_img_num)

    def set_just_imported(self):
        self.just_imported = True

    def tune_palette_ini(
        self,x_ini = None, x_end = None, y_ini = None, y_end = None
    ):
        if self.just_imported == True:
            try:
                medi_i = np.median(self.np_full_img[x_ini: x_end, y_ini: y_end])
                i_max_to_edit = str(int((medi_i + 1) * 10))
                logging.info("moving max palette to: " + i_max_to_edit)
                self.pop_display_menu.i_max_line.setText(i_max_to_edit)

            except TypeError:
                logging.info("Type Err catch(tune_palette_ini)")

        self.just_imported = False

    def update_threshold_params(self, new_params):
        self.threshold_params = new_params
        self.need_2_reload.emit() #TODO: rethink if this signal is needed here

    def user_applied(self):
        self.user_pass_threshold_param.emit(self.threshold_params)

    def build_background_n_get_nod_num(self, in_img_num):
        if self.nod_or_path is False or self.on_filter_reflections:
            self.cur_nod_num = self.main_obj.new_node.parent_node_lst[0]

        elif self.nod_or_path is True:
            self.cur_nod_num = self.main_obj.curr_nod_num

        elif type(self.nod_or_path) is str:
            self.cur_nod_num = self.nod_or_path
            self.exp_path = str(self.cur_nod_num)

        my_cmd_lst = ["get_template", str(in_img_num)]
        my_cmd = {"nod_lst" : [self.cur_nod_num],
                  "path"    : self.nod_or_path,
                  "cmd_str" : my_cmd_lst}

        try:
            self.ld_tpl_thread.quit()
            self.ld_tpl_thread.wait()

        except AttributeError:
            logging.info("first reflection list loading")

        self.ld_tpl_thread = LoadInThread(
            self.uni_url, my_cmd, self.my_handler
        )
        self.ld_tpl_thread.request_loaded.connect(
            self.after_requesting_template
        )

        self.ld_tpl_thread.start()

    def after_requesting_template(self, tup_data):
        json_data_lst = tup_data
        try:
            new_templ = str(json_data_lst[0])
            self.cur_img_num = int(json_data_lst[4])
            self.main_obj.window.ImgNumEdit.setText(str(self.cur_img_num))
            logging.info("new_templ = " + new_templ)
            self.img_d1_d2 = (
                json_data_lst[1], json_data_lst[2]
            )
            new_img_path = str(json_data_lst[3])
            self.i23_multipanel = bool(json_data_lst[5])
            logging.info("Is I23 multidetector:" + str(self.i23_multipanel))
            if(
                self.img_path != new_img_path or
                self.old_img_num != self.cur_img_num
            ):
                x_ax = np.arange(
                    start = -self.img_d1_d2[1] / 2,
                    stop = self.img_d1_d2[1] / 2 + 1,
                    step = 1
                )
                y_ax = np.arange(
                    start = -self.img_d1_d2[0] / 2,
                    stop = self.img_d1_d2[0] / 2 + 1,
                    step = 1
                )
                sx = x_ax * x_ax
                sy = y_ax * y_ax
                xx, yy = np.meshgrid(sx, sy, sparse = True)
                tmp_2d_arr = xx + yy
                tmp_2d_arr = tmp_2d_arr.max() - tmp_2d_arr
                tmp_2d_arr = tmp_2d_arr ** 6
                self.np_full_img = self.i_min_max[1] * (
                    tmp_2d_arr / tmp_2d_arr.max()
                )

            self.img_path = new_img_path
            self.main_obj.window.ImagePathText.setText(str(self.img_path))

        except (IndexError, TypeError):
            logging.info("Not loaded new template in full")

        try:
            self.np_full_mask_img = np.zeros((
                self.img_d1_d2[0], self.img_d1_d2[1]
                ), dtype = 'float')
            #self.np_full_mask_img[:,:] = 0.0

        except TypeError:
            self.np_full_mask_img = None

        self.request_reflection_list()

    def request_reflection_list(self):
        if self.on_filter_reflections:
            logging.info(
                "loading reflections from parent node ...on_filter_reflections"
            )
            lst_2_load = self.main_obj.new_node.parent_node_lst

        else:
            lst_2_load = [self.cur_nod_num]

        if self.nod_or_path is True:
            if self.pop_display_menu.rad_but_obs.isChecked():
                my_cmd = {
                    'nod_lst': lst_2_load,
                    'cmd_str': ["grl", str(self.cur_img_num)]
                }

            else:
                z_dept_str = str(self.pop_display_menu.z_dept_combo.value())
                my_cmd = {
                    'nod_lst': lst_2_load,
                    'cmd_str': [
                        "grp", str(self.cur_img_num),
                        "z_dept=" + z_dept_str
                    ]
                }

        elif type(self.nod_or_path) is str:
            my_cmd = {
                'path': self.nod_or_path,
                'cmd_str': ["get_reflection_list", str(self.cur_img_num)]
            }

        elif self.nod_or_path is False:
            self.r_list0 = []
            self.r_list1 = []
            self.refresh_img_n_refl()

        if self.nod_or_path is not False:
            try:
                self.ld_ref_thread.quit()
                self.ld_ref_thread.wait()

            except AttributeError:
                logging.info("first reflection list loading")

            self.ld_ref_thread = LoadInThread(
                self.uni_url, my_cmd, self.my_handler
            )
            if self.pop_display_menu.rad_but_obs.isChecked():
                self.ld_ref_thread.request_loaded.connect(
                    self.after_requesting_ref_lst
                )

            else:
                self.ld_ref_thread.request_loaded.connect(
                    self.after_requesting_predict_lst
                )

            self.ld_ref_thread.start()

    def after_requesting_ref_lst(self, req_tup):
        json_lst = req_tup
        self.r_list0 = []
        try:
            for inner_dict in json_lst:
                self.r_list0.append(
                    {
                        "x"           : float(inner_dict["x"]),
                        "y"           : float(inner_dict["y"]),
                        "width"       : float(inner_dict["width"]),
                        "height"      : float(inner_dict["height"]),
                        "local_hkl"   :   str(inner_dict["local_hkl"]),
                        "big_lst_num" :   int(inner_dict["big_lst_num"]),
                        "x_me_out"    : False,
                    }
                )

            logging.info("Reflection list loaded")

        except TypeError:
            logging.info("No reflection list to show (Type err catch except)")

        except IndexError:
            logging.info("No reflection list to show (Index err catch except)")

        self.x_out_selected()
        self.refresh_img_n_refl()

    def x_out_selected(self):
        lst_2_x_out = []
        try:
            if self.on_filter_reflections:
                lst_of_str = self.main_obj.new_node.par_lst[0][0]['value'].split(",")
                for single_str in lst_of_str:
                    lst_2_x_out.append(int(single_str))

            for n, small_lst_refl in enumerate(self.r_list0):
                self.r_list0[n]["x_me_out"] = False
                if small_lst_refl["big_lst_num"] in lst_2_x_out:
                    self.r_list0[n]["x_me_out"] = True

        except IndexError:
            logging.info("empty list(x_out_selected)")

    def after_requesting_predict_lst(self, req_tup):
        json_lst = req_tup
        self.r_list1 = []
        try:
            for inner_dict in json_lst:
                self.r_list1.append(
                    {
                        "x"         : float(inner_dict["x"]),
                        "y"         : float(inner_dict["y"]),
                        "local_hkl" :   str(inner_dict["local_hkl"]),
                        "z_dist"    : float(inner_dict["z_dist"]),
                        "x_me_out"  : False,
                    }
                )

        except TypeError:
            logging.info(
                "No reflection << predict >> to show (Type err catch except)"
            )

        except IndexError:
            logging.info(
                "No reflection << predict >> to show (Index err catch except)"
            )

        except KeyError:
            logging.info(
                "No reflection << predict >> to show (Key err catch except)"
            )

        self.refresh_img_n_refl()

    def refresh_img_n_refl(self):
        self.refresh_pixel_map()
        if not self.easter_egg_active:
            self.full_img_show()

    def refresh_pixel_map(self):
        show_refl = self.pop_display_menu.chk_box_show.isChecked()
        self.my_scene.draw_all_hkl = \
            self.pop_display_menu.rad_but_all_hkl.isChecked()
        self.my_scene.draw_near_hkl = \
            self.pop_display_menu.rad_but_near_hkl.isChecked()

        try:
            if self.palette == "heat":
                rgb_np = self.bmp_heat.img_2d_rgb(
                    data2d = self.np_full_img, invert = False,
                    i_min_max = self.i_min_max
                )

            elif self.palette == "grayscale":
                rgb_np = self.bmp_m_cro.img_2d_rgb(
                    data2d = self.np_full_img, invert = False,
                    i_min_max = self.i_min_max
                )

            elif self.palette == "heat invert":
                rgb_np = self.bmp_heat.img_2d_rgb(
                    data2d = self.np_full_img, invert = True,
                    i_min_max = self.i_min_max
                )

            elif self.palette == "invert":
                rgb_np = self.bmp_m_cro.img_2d_rgb(
                    data2d = self.np_full_img, invert = True,
                    i_min_max = self.i_min_max
                )

            q_img = QImage(
                rgb_np.data,
                np.size(rgb_np[0:1, :, 0:1]),
                np.size(rgb_np[:, 0:1, 0:1]),
                QImage.Format_ARGB32
            )
            new_pixmap = QPixmap.fromImage(q_img)
            if show_refl:
                if self.pop_display_menu.rad_but_obs.isChecked():
                    self.my_scene(
                        new_pixmap, self.r_list0, self.list_temp_mask
                    )

                else:
                    self.my_scene(
                        new_pixmap, self.r_list1, self.list_temp_mask
                    )

            else:
                self.my_scene(
                    new_pixmap, [], self.list_temp_mask
                )

        except (TypeError, AttributeError):
            logging.info("None self.np_full_img")

        try:
            m_rgb_np = self.bmp_mask.img_2d_rgb(
                data2d = self.np_full_mask_img,
                colour_in = self.mask_colour, transp = self.mask_transp
            )

            q_img = QImage(
                m_rgb_np.data,
                np.size(m_rgb_np[0:1, :, 0:1]),
                np.size(m_rgb_np[:, 0:1, 0:1]),
                QImage.Format_ARGB32
            )
            new_m_pixmap = QPixmap.fromImage(q_img)
            self.my_scene.add_mask_pixmap(new_m_pixmap)
            self.my_scene.refresh_imgs()

        except AttributeError:
            logging.info("no mask to draw here")

    def change_i_min_max(self, new_i_min, new_i_max):
        self.i_min_max = [new_i_min, new_i_max]
        self.refresh_pixel_map()

    def change_palette(self, new_palette):
        self.palette = new_palette
        self.refresh_pixel_map()

    def change_mask_colour(self, new_colour):
        self.mask_colour = new_colour
        #print("self.mask_colour =", self.mask_colour)
        self.refresh_pixel_map()

    def change_mask_transp(self, new_transp):
        self.mask_transp = new_transp
        #print("self.mask_transp =", self.mask_transp)
        self.refresh_pixel_map()

    def change_overlay(self, new_overlay):
        self.overlay = new_overlay
        self.refresh_img_n_refl()

    def menu_display(self, event):
        logging.info("menu_display")

    def menu_actions(self, event):
        logging.info("menu_actions")

    def new_full_img(self, tup_data):
        self.full_image_loaded = True
        self.np_full_img = tup_data[2]
        self.tune_palette_ini()
        self.refresh_pixel_map()

    def new_full_mask_img(self, tup_data):
        self.np_full_mask_img = tup_data[2]
        self.refresh_pixel_map()

    def full_img_show(self):
        self.full_image_loaded = False
        try:
            self.load_full_image.quit()
            self.load_full_image.wait()

        except AttributeError:
            logging.info("first full image loading")

        try:
            self.load_full_mask_image.quit()
            self.load_full_mask_image.wait()

        except AttributeError:
            logging.info("first full image loading")

        self.load_full_image = LoadFullImage(
            unit_URL = self.uni_url,
            cur_nod_num = self.cur_nod_num,
            cur_img_num = self.cur_img_num,
            path_in = self.exp_path,
            main_handler = self.my_handler
        )
        self.load_full_mask_image = LoadFullMaskImage(
            unit_URL = self.uni_url,
            cur_nod_num = self.cur_nod_num,
            cur_img_num = self.cur_img_num,
            path_in = self.exp_path,
            thrs_pars_in = self.threshold_params,
            main_handler = self.my_handler
        )
        self.load_full_image.image_loaded.connect(self.new_full_img)
        self.load_full_image.start()
        self.load_full_mask_image.image_loaded.connect(self.new_full_mask_img)
        self.load_full_mask_image.start()

    def check_move(self):
        self.get_x1_y1_x2_y2()
        if(
            self.old_x1 != self.x1 or self.old_y1 != self.y1 or
            self.old_x2 != self.x2 or self.old_y2 != self.y2 or
            self.old_inv_scl != self.inv_scale or
            self.old_nod_num != self.cur_nod_num or
            self.old_img_num != self.cur_img_num or
            self.old_threshold_params != self.threshold_params
        ):
            logging.info(
                "scaled, dragged, changed image or threshold_params changed"
            )
            self.slice_show_img()

        self.old_x1 = self.x1
        self.old_y1 = self.y1
        self.old_x2 = self.x2
        self.old_y2 = self.y2
        self.old_inv_scl = self.inv_scale
        self.old_nod_num = self.cur_nod_num
        self.old_img_num = self.cur_img_num
        self.old_threshold_params = self.threshold_params

    def det_tmp_x1_y1_x2_y2(self):
        viewport_rect = QRect(
            0, 0, self.main_obj.window.imageView.viewport().width(),
            self.main_obj.window.imageView.viewport().height()
        )
        visibleSceneRect = self.main_obj.window.imageView.mapToScene(
            viewport_rect
        ).boundingRect()
        visibleSceneCoords = visibleSceneRect.getCoords()
        tmp_x1 = int(visibleSceneCoords[1])
        tmp_y1 = int(visibleSceneCoords[0])
        tmp_x2 = int(visibleSceneCoords[3])
        tmp_y2 = int(visibleSceneCoords[2])
        return tmp_x1, tmp_y1, tmp_x2, tmp_y2

    def get_x1_y1_x2_y2(self):
        self.x1, self.y1, self.x2, self.y2 = self.det_tmp_x1_y1_x2_y2()
        try:
            if self.x2 > self.img_d1_d2[0] - 1:
                self.x2 = self.img_d1_d2[0] - 1

            if self.y2 > self.img_d1_d2[1] - 1:
                self.y2 = self.img_d1_d2[1] - 1

            if self.x1 < 0:
                self.x1 = 0

            if self.y1 < 0:
                self.y1 = 0

        except TypeError:
            (self.x1, self.y1, self.x2, self.y2) = (-1, -1, -1, -1)

    def get_scale_label(self):
        avg_scale = float(
            self.main_obj.window.imageView.transform().m11() +
            self.main_obj.window.imageView.transform().m22()
        ) / 2.0
        avg_scale = abs(avg_scale)
        str_label = "scale = {:3.3}".format(avg_scale)
        self.main_obj.window.InvScaleLabel.setText(str_label)
        return avg_scale

    def set_inv_scale(self):
        avg_scale = self.get_scale_label()
        self.inv_scale = int(1.0 / avg_scale)

        if self.inv_scale < 1:
            self.inv_scale = 1

        if self.inv_scale > 36:
            self.inv_scale = 36

    def new_slice_img(self, dict_slice):
        try:
            slice_image = dict_slice["slice_image"]
            rep_slice_img = np.repeat(np.repeat(
                    slice_image[:,:],
                    dict_slice["inv_scale"], axis=0
                ),
                dict_slice["inv_scale"], axis=1
            )

            rep_len_x = np.size(rep_slice_img[:,0:1])
            rep_len_y = np.size(rep_slice_img[0:1,:])

            x_ini = dict_slice["x1"]
            y_ini = dict_slice["y1"]
            x_end = x_ini + rep_len_x
            y_end = y_ini + rep_len_y

            if x_end > np.size(self.np_full_img[:,0:1]):
                rep_len_x = np.size(self.np_full_img[:,0:1]) - x_ini
                logging.info("limiting dx")

            if y_end > np.size(self.np_full_img[0:1,:]):
                rep_len_y = np.size(self.np_full_img[0:1,:]) - y_ini
                logging.info("limiting dy")

            if self.full_image_loaded == False:
                self.np_full_img[
                    x_ini:x_end,
                    y_ini:y_end
                ] = rep_slice_img[0:rep_len_x, 0:rep_len_y]
                self.refresh_pixel_map()

            self.tune_palette_ini(x_ini, x_end, y_ini, y_end)

        except TypeError:
            logging.info("loading image slice in next loop")

        self.l_stat.load_finished()

    def new_slice_mask_img(self, dict_slice):
        if self.easter_egg_active:
            try:
                slice_image = dict_slice["slice_image"]
                rep_slice_img = np.repeat(np.repeat(
                        slice_image[:,:],
                        dict_slice["inv_scale"], axis=0
                    ),
                    dict_slice["inv_scale"], axis=1
                )
                rep_len_x = np.size(rep_slice_img[:,0:1])
                rep_len_y = np.size(rep_slice_img[0:1,:])

                if dict_slice["x1"] + rep_len_x > np.size(self.np_full_mask_img[:,0:1]):
                    rep_len_x = np.size(self.np_full_mask_img[:,0:1]) - dict_slice["x1"]
                    logging.info("limiting dx")

                if dict_slice["y1"] + rep_len_y > np.size(self.np_full_mask_img[0:1,:]):
                    rep_len_y = np.size(self.np_full_mask_img[0:1,:]) - dict_slice["y1"]
                    logging.info("limiting dy")

                if self.full_image_loaded == False:
                    self.np_full_mask_img[
                        dict_slice["x1"]:dict_slice["x1"] + rep_len_x,
                        dict_slice["y1"]:dict_slice["y1"] + rep_len_y
                    ] = rep_slice_img[0:rep_len_x, 0:rep_len_y]
                    self.refresh_pixel_map()

            except TypeError:
                logging.info("loading image slice in next loop")

            self.l_stat.load_finished()

        self.refresh_pixel_map()

    def update_progress(self, progress):
        self.l_stat.load_progress(progress)

    def slice_show_img(self):
        if self.full_image_loaded == False and self.easter_egg_active:
            self.l_stat.load_started()

            try:
                self.load_slice_image.say_good_bye()
                self.load_slice_image.quit()
                self.load_slice_image.wait()

            except AttributeError:
                logging.info("first slice of image loading")

            try:
                self.load_slice_mask_image.say_good_bye()
                self.load_slice_mask_image.quit()
                self.load_slice_mask_image.wait()

            except AttributeError:
                logging.info("first slice of mask image loading")

            self.get_x1_y1_x2_y2()
            self.set_inv_scale()
            self.load_slice_image = LoadSliceImage(
                nod_num_lst = [self.cur_nod_num],
                img_num = self.cur_img_num,
                inv_scale = self.inv_scale,
                x1 = self.x1,
                y1 = self.y1,
                x2 = self.x2,
                y2 = self.y2,
                path_in = self.exp_path,
                main_handler = self.my_handler
            )
            self.load_slice_image.slice_loaded.connect(
                self.new_slice_img
            )
            self.load_slice_image.progressing.connect(
                self.update_progress
            )
            self.load_slice_image.start()

            # Now Same for mask

            self.load_slice_mask_image = LoadSliceMaskImage(
                unit_URL = self.uni_url,
                nod_num_lst = [self.cur_nod_num],
                img_num = self.cur_img_num,
                inv_scale = self.inv_scale,
                x1 = self.x1,
                y1 = self.y1,
                x2 = self.x2,
                y2 = self.y2,
                path_in = self.exp_path,
                thrs_pars_in = self.threshold_params,
                main_handler = self.my_handler
            )
            self.load_slice_mask_image.slice_loaded.connect(
                self.new_slice_mask_img
            )
            self.load_slice_mask_image.progressing.connect(
                self.update_progress
            )
            self.load_slice_mask_image.start()

    def OneOneScale(self, event):
        logging.info("OneOneScale")
        self.main_obj.window.imageView.resetTransform()
        avg_scale = self.get_scale_label()

    def ZoomInScale(self, event):
        logging.info("ZoomInScale")
        self.scale_img(1.05)
        avg_scale = self.get_scale_label()

    def ZoomOutScale(self, event):
        logging.info("ZoomOutScale")
        self.scale_img(0.95)
        avg_scale = self.get_scale_label()

    def scale_img(self, relative_new_scale):
        tmp_x1, tmp_y1, tmp_x2, tmp_y2 = self.det_tmp_x1_y1_x2_y2()
        dx = tmp_x2 - tmp_x1
        dy = tmp_y2 - tmp_y1

        try:
            if(
                (
                    relative_new_scale > 1.0 and  dx > 10 and dy > 10
                ) or (
                    relative_new_scale < 1.0 and (
                        dx <= self.img_d1_d2[0]
                        or dy <= self.img_d1_d2[1]
                    )
                )
            ):

                self.main_obj.window.imageView.scale(
                    relative_new_scale, relative_new_scale
                )
                self.set_inv_scale()
                self.sheck_inversion()

        except TypeError:
            logging.info("not zooming/unzooming before loading image")

    def sheck_inversion(self):
        m11 = self.main_obj.window.imageView.transform().m11()
        m22 = self.main_obj.window.imageView.transform().m22()
        if m11 < 0 or m22 < 0:
            self.main_obj.window.imageView.setMatrix(
                QMatrix(
                    float(abs(m11)), float(0.0), float(0.0),
                    float(abs(m22)), float(0.0), float(0.0)
                )
            )
            m11 = self.main_obj.window.imageView.transform().m11()
            m22 = self.main_obj.window.imageView.transform().m22()

    def easter_egg(self, event):
        self.easter_egg_active = not self.easter_egg_active
        print("Easter egg activated/deactivated")
        print("scaling and cropping behaviour:" + str(self.easter_egg_active))
        print("remember to change the image (next/previous)")
        logging.info("self.easter_egg_active =" + str(self.easter_egg_active))
        self.full_image_loaded = False

    def set_drag_mode(self, mask_mode = False):
        self.mask_mode = mask_mode
        if self.mask_mode:
            self.main_obj.window.imageView.setDragMode(
                QGraphicsView.NoDrag
            )

        else:
            self.main_obj.window.imageView.setDragMode(
                QGraphicsView.ScrollHandDrag
            )

        logging.info("\n set_drag_mode \n mask_mode =" + str(self.mask_mode))

    def set_mask_comp(self, mask_comp = None):
        self.mask_comp = mask_comp
        if self.mask_comp is None:
            self.mask_x_ini = None
            self.mask_y_ini = None

    def update_tmp_mask(self, lst_of_lst_0):
        self.list_temp_mask = lst_of_lst_0
        self.refresh_pixel_map()

    def on_mouse_move(self, x_pos, y_pos):
        try:
            str_out = "  I(" + str(x_pos) + ", " + str(y_pos) + ")  =  " +\
                  "{:8.1f}".format(self.np_full_img[y_pos, x_pos])

        except (AttributeError, IndexError, TypeError):
            str_out = " I  =  ?"

        try:
            str_out += "  mask=" + str(self.np_full_mask_img[y_pos, x_pos])

        except (AttributeError, IndexError, TypeError):
            str_out += "  mask = ?"

        self.main_obj.window.EasterEggButton.setText(str_out)

        self.my_scene.update_tmp_mask(self.list_temp_mask)
        if self.mask_mode:
            self.my_scene.draw_temp_mask()
            if(
                self.mask_comp is not None and
                self.mask_x_ini is not None and
                self.mask_y_ini is not None
            ):
                if self.mask_comp == "rect":
                    x1 = int(x_pos)
                    y1 = int(y_pos)
                    x2 = int(self.mask_x_ini)
                    y2 = int(self.mask_y_ini)

                    if x1 < x2:
                        x1, x2 = x2, x1

                    if y1 < y2:
                        y1, y2 = y2, y1

                    tmp_width = x1 - x2
                    tmp_height = y1 - y2

                    rectangle1 = QRectF(x2, y2, tmp_width, tmp_height)
                    self.my_scene.addRect(rectangle1, self.my_scene.overlay_pen1)

                elif self.mask_comp == "circ":

                    dx = float(x_pos - self.mask_x_ini)
                    dy = float(y_pos - self.mask_y_ini)
                    r = int(np.sqrt(dx * dx + dy * dy))
                    rectangle1 = QRectF(
                        x_pos - r, y_pos - r, 2 * r, 2 * r
                    )

                    self.my_scene.addEllipse(
                        rectangle1, self.my_scene.overlay_pen1
                    )

                    self.my_scene.addLine(
                        self.mask_x_ini, self.mask_y_ini, x_pos,
                        y_pos, self.my_scene.overlay_pen1
                    )

                elif self.mask_comp == "poly":
                    dx = float(x_pos - self.mask_x_ini)
                    dy = float(y_pos - self.mask_y_ini)
                    r = int(np.sqrt(dx * dx + dy * dy))

                    self.my_scene.addLine(
                        self.mask_x_ini, self.mask_y_ini, x_pos,
                        y_pos, self.my_scene.overlay_pen1
                    )

    def on_mouse_press(self, x_pos, y_pos):
        if self.mask_mode:
            if self.mask_comp is not None:
                self.mask_x_ini = x_pos
                self.mask_y_ini = y_pos

    def on_mouse_release(self, x_pos, y_pos):
        if self.mask_mode:
            if(
                self.mask_comp is not None and
                self.mask_x_ini is not None and
                self.mask_y_ini is not None
            ):
                if self.mask_comp == "rect":
                    x_ini = int(self.mask_x_ini)
                    y_ini = int(self.mask_y_ini)
                    x_end = int(x_pos)
                    y_end = int(y_pos)
                    if x_ini > x_end:
                        x_ini, x_end = x_end, x_ini

                    if y_ini > y_end:
                        y_ini, y_end = y_end, y_ini

                    if x_ini < 0:
                        x_ini = 0

                    if y_ini < 0:
                        y_ini = 0

                    if x_end > self.img_d1_d2[1]:
                        x_end = self.img_d1_d2[1]

                    if y_end > self.img_d1_d2[0]:
                        y_end = self.img_d1_d2[0]

                    self.new_mask_comp.emit(
                        {
                            "type"              : "rect" ,
                            "x_ini"             : x_ini ,
                            "x_end"             : x_end ,
                            "y_ini"             : y_ini ,
                            "y_end"             : y_end ,
                            "i23_multipanel"    : self.i23_multipanel,
                        }
                    )

                elif self.mask_comp == "circ":
                    dx = float(self.mask_x_ini - x_pos)
                    dy = float(self.mask_y_ini - y_pos)
                    r = int(np.sqrt(dx * dx + dy * dy))

                    self.new_mask_comp.emit(
                        {
                            "type"              : "circ" ,
                            "x_c"               : int(x_pos) ,
                            "y_c"               : int(y_pos) ,
                            "r"                 : r ,
                            "i23_multipanel"    : self.i23_multipanel,
                        }
                    )

                elif self.mask_comp == "poly":
                    x_ini = int(self.mask_x_ini)
                    x_end = int(x_pos)
                    y_ini = int(self.mask_y_ini)
                    y_end = int(y_pos)

                    if x_ini < 0:
                        x_ini = 0

                    if y_ini < 0:
                        y_ini = 0

                    if x_end < 0:
                        x_end = 0

                    if y_end < 0:
                        y_end = 0

                    if x_ini > self.img_d1_d2[0] - 2:
                        x_ini = self.img_d1_d2[0] - 2

                    if y_ini > self.img_d1_d2[1] - 2:
                        y_ini = self.img_d1_d2[1] - 2

                    if x_end > self.img_d1_d2[0] - 2:
                        x_end = self.img_d1_d2[0] - 2

                    if y_end > self.img_d1_d2[1] - 2:
                        y_end = self.img_d1_d2[1] - 2

                    self.new_mask_comp.emit(
                        {
                            "type"              : "poly" ,
                            "x_ini"             : x_ini ,
                            "x_end"             : x_end ,
                            "y_ini"             : y_ini ,
                            "y_end"             : y_end ,
                            "i23_multipanel"    : self.i23_multipanel,
                        }
                    )

                self.mask_x_ini = None
                self.mask_y_ini = None

        elif self.on_filter_reflections:
            pos_min = None
            d_cuad_min = 10000000
            for num, refl in enumerate(self.r_list0):

                x_ref = refl["x"]
                y_ref = refl["y"]

                dx = x_ref - x_pos
                dy = y_ref - y_pos
                d_cuad = dx * dx + dy * dy
                if d_cuad < d_cuad_min:
                    d_cuad_min = d_cuad
                    pos_min = num

            pos_2_emit = self.r_list0[pos_min]["big_lst_num"]
            self.new_refl.emit(pos_2_emit)

            self.x_out_selected()
            self.my_scene.draw_ref_rect()


class MainImgViewObject(QObject):
    def __init__(self, parent = None):
        super(MainImgViewObject, self).__init__(parent)
        self.parent_app = parent
        #self.my_handler = parent.runner_handler

        # temp hack, will obviously break if running in all ram mode ...star
        self.my_handler = None
        self.runner_handler = None
        # temp hack, will obviously break if running in all ram mode ...end

        self.ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = self.ui_dir_path + os.sep + "view_client.ui"
        logging.info("ui_path =", ui_path)

        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.setWindowTitle("CCP4 DUIs embedded image viewer")

        data_init = ini_data()
        data_init.set_data()
        self.uni_url = data_init.get_url()

        self.curr_nod_num = 1
        self.nod_or_path = True
        self.do_image_view = DoImageView(self)

        self.window.show()

        self.window.ImgNumEdit.editingFinished.connect(self.img_num_changed)
        self.window.PrevImgButton.clicked.connect(self.prev_img)
        self.window.NextImgButton.clicked.connect(self.next_img)
        self.window.OpenFileButton.clicked.connect(self.open_dir_widget)

    def img_num_changed(self):
        self.refresh_output(nod_or_path = self.nod_or_path)

    def refresh_output(self, nod_or_path = True):
        img_num = int(self.window.ImgNumEdit.text())
        self.do_image_view(in_img_num = img_num, nod_or_path = nod_or_path)

    def shift_img_num(self, sh_num):
        img_num = int(self.window.ImgNumEdit.text())
        img_num += sh_num
        self.window.ImgNumEdit.setText(str(img_num))

    def prev_img(self):
        logging.info("prev_img")
        self.shift_img_num(-1)
        self.img_num_changed()

    def next_img(self):
        logging.info("next_img")
        self.shift_img_num(1)
        self.img_num_changed()

    def set_selection(self, str_select, isdir):
        self.nod_or_path = str_select
        self.dir_selected = isdir
        self.window.IntroPathEdit.setText(self.nod_or_path)
        my_cmd_lst = ["get_template", "0"]
        my_cmd = {
            "path"    : self.nod_or_path,
            "cmd_str" : my_cmd_lst
        }
        lst_req = get_req_json_dat(
            params_in = my_cmd, main_handler = self.my_handler
        )
        json_data_lst = lst_req.result_out()
        try:
            new_templ = json_data_lst[0]
            self.img_d1_d2 = (json_data_lst[1], json_data_lst[2])
            self.refresh_output(nod_or_path = self.nod_or_path)

        except TypeError:
            logging.info("Type Err catch while opening imgs")

    def open_dir_widget(self):
        cmd = {"nod_lst":"", "cmd_str":["dir_path"]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = self.my_handler
        )
        dic_str = lst_req.result_out()
        init_path = dic_str[0]

        self.open_widget = FileBrowser(
            self.window, path_in = init_path, only_dir = False
        )
        self.open_widget.resize(self.open_widget.size() * 2)
        self.open_widget.select_done.connect(self.set_selection)


def main(par_def = None):
    data_init = ini_data()
    data_init.set_data(par_def)
    uni_url = data_init.get_url()
    app = QApplication(sys.argv)
    m_obj = MainImgViewObject(parent = app)
    sys.exit(app.exec_())

