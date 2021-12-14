"""
DUI2's image visualization utilities

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


import sys, os
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtUiTools

import numpy as np
import json, zlib, time, requests

from init_firts import ini_data

from exec_utils import json_data_request
from outputs import HandleLoadStatusLabel

from img_view_utils import (
    crunch_min_max, np2bmp_monocrome, np2bmp_heat, load_json_w_str
)

#FIXME change the name of FileBrowser to camel_case
from simpler_param_widgets import FileBrowser, build_template


class LoadFullImage(QThread):
    image_loaded = Signal(tuple)
    def __init__(
        self, unit_URL = None, cur_nod_num = None,
        cur_img_num = None, path_in = None
    ):
        super(LoadFullImage, self).__init__()
        self.uni_url = unit_URL
        self.cur_nod_num = cur_nod_num
        self.cur_img_num = cur_img_num
        self.exp_path = path_in

    def run(self):
        print("loading image ", self.cur_img_num, " in full resolution")
        np_full_img = load_json_w_str(
            self.uni_url,
            nod_num_lst = [self.cur_nod_num],
            img_num = self.cur_img_num,
            exp_path = self.exp_path
        )
        self.image_loaded.emit(
            (self.cur_nod_num, self.cur_img_num, np_full_img)
        )


class LoadSliceImage(QThread):
    progressing = Signal(int)
    slice_loaded = Signal(dict)
    def __init__(
        self, unit_URL = None, nod_num_lst = None,
        img_num = None, inv_scale = None,
        x1 = None, y1 = None, x2 = None, y2 = None,
        path_in = None
    ):
        super(LoadSliceImage, self).__init__()
        self.uni_url =      unit_URL
        self.nod_num_lst =  nod_num_lst
        self.img_num =      img_num
        self.inv_scale =    inv_scale
        self.x1 =           x1
        self.y1 =           y1
        self.x2 =           x2
        self.y2 =           y2
        self.exp_path =     path_in

    def run(self):
        print("loading slice of image ")

        my_cmd_lst = [
            "gis " + str(self.img_num) +
            " inv_scale=" + str(self.inv_scale) +
            " view_rect=" + str(self.x1) + "," + str(self.y1) +
                      "," + str(self.x2) + "," + str(self.y2)
        ]

        my_cmd = {"nod_lst" : self.nod_num_lst,
                  "path"    : self.exp_path,
                  "cmd_lst" : my_cmd_lst}
        start_tm = time.time()

        try:
            req_get = requests.get(self.uni_url, stream=True, params = my_cmd)
            total_size = int(req_get.headers.get('content-length', 0)) + 1
            print("total_size =", total_size)
            block_size = 65536
            downloaded_size = 0
            compresed = bytes()
            for data in req_get.iter_content(block_size):
                compresed += data
                downloaded_size += block_size
                progress = int(100.0 * (downloaded_size / total_size))
                self.progressing.emit(progress)

            dic_str = zlib.decompress(compresed)
            arr_dic = json.loads(dic_str)
            end_tm = time.time()
            print("slice IMG request took ", end_tm - start_tm, "sec")

            str_data = arr_dic["str_data"]
            d1 = arr_dic["d1"]
            d2 = arr_dic["d2"]
            print("d1, d2 =", d1, d2)
            arr_1d = np.fromstring(str_data, dtype = float, sep = ',')
            np_array_out = arr_1d.reshape(d1, d2)

        except zlib.error:
            print("zlib.error(load_slice_img_json)")
            np_array_out = None

        except ConnectionError:
            print("\n ConnectionError (load_slice_img_json) \n")
            np_array_out = None

        except requests.exceptions.RequestException:
            print(
                "\n requests.exceptions.RequestException (load_slice_img_json) \n"
            )
            np_array_out = None

        except json.decoder.JSONDecodeError:
            print(
                "\n json.decoder.JSONDecodeError (load_slice_img_json) \n"
            )
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


class ImgGraphicsScene(QGraphicsScene):
    img_scale = Signal(float)
    new_mouse_pos = Signal(int, int)
    mouse_pressed = Signal(int, int)
    mouse_released = Signal(int, int)

    def __init__(self, parent = None):
        super(ImgGraphicsScene, self).__init__(parent)
        self.parent_obj = parent
        self.curr_pixmap = None

        self.green_pen = QPen(
            Qt.green, 0.8, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        self.draw_all_hkl = False
        self.draw_near_hkl = True

    def draw_ref_rect(self):
        self.clear()
        if self.my_pix_map is not None:
            self.curr_pixmap = self.my_pix_map

        self.addPixmap(self.curr_pixmap)
        for refl in self.refl_list:
            rectangle = QRectF(
                refl["x"], refl["y"], refl["width"], refl["height"]
            )
            self.addRect(rectangle, self.green_pen)

        to_use_later = '''
        for refl in refl_list1:
            self.addLine(
                refl["x_ini"] + 1 + refl["xrs_size"], refl["y_ini"] + 1,
                refl["x_ini"] + 1 - refl["xrs_size"], refl["y_ini"] + 1,
                self.green_pen
            )
            self.addLine(
                refl["x_ini"] + 1, refl["y_ini"] + 1 + refl["xrs_size"],
                refl["x_ini"] + 1, refl["y_ini"] + 1 - refl["xrs_size"],
                self.green_pen
            )
        '''

    def __call__(self, new_pixmap, refl_list0):
        self.refl_list = refl_list0
        self.my_pix_map = new_pixmap
        self.draw_ref_rect()
        if self.draw_all_hkl:
            for refl in self.refl_list:
                n_text = self.addSimpleText(str(refl["local_hkl"]))
                n_text.setPos(refl["x"], refl["y"])
                n_text.setPen(self.green_pen)

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
                    x_ref = refl["x"] + refl["width"] / 2
                    y_ref = refl["y"] + refl["height"] / 2

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
                n_text.setPen(self.green_pen)

            except (UnboundLocalError, TypeError, AttributeError):
                prints_to_console_for_debugging = '''
                print(
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

class PopActionsMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__()
        self.my_parent = parent

        mask_group = QGroupBox("Mask tool")
        mask_box_layout = QVBoxLayout()
        mask_box_layout.addWidget(QLabel("Dummy_01"))
        mask_box_layout.addWidget(QLabel("Dummy_02"))
        mask_group.setLayout(mask_box_layout)

        sp_find_group = QGroupBox("Spot finding steps")
        sp_find_box_layout = QVBoxLayout()
        sp_find_box_layout.addWidget(QLabel("Dummy ... one"))
        sp_find_box_layout.addWidget(QLabel("Dummy ... two"))
        sp_find_box_layout.addWidget(QLabel("Dummy ... three"))
        sp_find_group.setLayout(sp_find_box_layout)

        my_main_box = QHBoxLayout()
        my_main_box.addWidget(mask_group)
        my_main_box.addWidget(sp_find_group)
        self.setLayout(my_main_box)


class PopDisplayMenu(QMenu):
    new_i_min_max = Signal(int, int)
    new_palette = Signal(str)
    new_redraw = Signal()
    def __init__(self, parent=None):
        super().__init__()
        self.my_parent = parent

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
        i_min_max_layout.addWidget(self.i_min_line)
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

        palette_box_layout.addWidget(QLabel("  ... "))
        palette_box_layout.addWidget(self.palette_select)

        palette_group.setLayout(palette_box_layout)

        info_group = QGroupBox("Reflection info")
        ref_box_layout = QVBoxLayout()


        # Viewing Tool
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

        my_main_box = QVBoxLayout()
        my_main_box.addWidget(palette_group)
        my_main_box.addWidget(info_group)
        self.setLayout(my_main_box)
    def sig_new_redraw(self):
        print("new_redraw")
        self.new_redraw.emit()

    def palette_changed_by_user(self, new_palette_num):
        self.palette = self.palette_lst[new_palette_num]
        print("self.palette =", self.palette)
        self.new_palette.emit(str(self.palette))

    def i_min_max_changed(self):
        self.new_i_min_max.emit(self.i_min, self.i_max)

    def i_min_changed(self, value):
        print("i_min_changed; value=", value)
        self.i_min = int(value)
        self.i_min_max_changed()

    def i_max_changed(self, value):
        print("i_max_changed; value=", value)
        self.i_max = int(value)
        self.i_min_max_changed()


class DoImageView(QObject):
    new_mask_comp = Signal(dict)
    def __init__(self, parent = None):
        super(DoImageView, self).__init__(parent)
        self.main_obj = parent

        data_init = ini_data()
        self.uni_url = data_init.get_url()

        self.l_stat = HandleLoadStatusLabel(self.main_obj)

        self.my_scene = ImgGraphicsScene(self)
        self.main_obj.window.imageView.setScene(self.my_scene)
        self.main_obj.window.imageView.setMouseTracking(True)
        self.set_drag_mode()
        self.set_mask_comp()

        self.main_obj.window.ScaleOneOneButton.clicked.connect(
            self.OneOneScale
        )
        self.main_obj.window.ZoomInButton.clicked.connect(
            self.ZoomInScale
        )
        self.main_obj.window.ZoomOutButton.clicked.connect(
            self.ZoomOutScale
        )

        self.main_obj.window.EasterEggButton.clicked.connect(self.easter_egg)
        self.easter_egg_active = False

        self.i_min_max = [-2, 50]
        self.palette = "grayscale"

        self.pop_display_menu = PopDisplayMenu(self)
        self.main_obj.window.DisplayButton.setMenu(self.pop_display_menu)
        self.pop_display_menu.new_i_min_max.connect(self.change_i_min_max)
        self.pop_display_menu.new_palette.connect(self.change_palette)
        self.pop_display_menu.new_redraw.connect(self.refresh_pixel_map)

        self.pop_act_menu = PopActionsMenu(self)
        self.main_obj.window.ActionsButton.setMenu(self.pop_act_menu)

        self.my_scene.img_scale.connect(self.scale_img)
        self.my_scene.new_mouse_pos.connect(self.on_mouse_move)
        self.my_scene.mouse_pressed.connect(self.on_mouse_press)
        self.my_scene.mouse_released.connect(self.on_mouse_release)

        self.bmp_heat = np2bmp_heat()
        self.bmp_m_cro = np2bmp_monocrome()
        self.cur_img_num = None
        self.cur_nod_num = None
        self.cur_templ = None
        self.img_d1_d2 = (None, None)
        self.inv_scale = 1
        self.full_image_loaded = False

        (self.old_x1, self.old_y1, self.old_x2, self.old_y2) = (-1, -1, -1, -1)
        self.old_inv_scl = self.inv_scale
        self.old_cur_nod_num = self.cur_nod_num
        self.old_cur_img_num = self.cur_img_num



        timer = QTimer(self)
        timer.timeout.connect(self.check_move)
        timer.start(1600)

    def __call__(self, in_img_num, nod_or_path):
        print(
            "refreshing Image Viewer\n img:", in_img_num,
            "\n node in List:", nod_or_path
        )
        self.r_list0 = []
        self.exp_path = None
        #self.r_list1 = []

        nod_num = self.build_background_n_get_nod_num(nod_or_path, in_img_num)

        if nod_or_path is True:
            my_cmd = {
                'nod_lst': [nod_num], 'cmd_lst': ["grl " + str(in_img_num)]
            }

        elif type(nod_or_path) is str:
            my_cmd = {
                'path': nod_or_path,
                'cmd_lst': "get_reflection_list " + str(in_img_num)
            }

        elif nod_or_path is False:
            print("No reflection list to show (known not to be)")

        if nod_or_path is not False:
            json_lst = json_data_request(self.uni_url, my_cmd)
            try:
                for inner_list in json_lst[0]:
                    self.r_list0.append(
                        {
                            "x"         : float(inner_list[0]),
                            "y"         : float(inner_list[1]),
                            "width"     : float(inner_list[2]),
                            "height"    : float(inner_list[3]),
                            "local_hkl" :   str(inner_list[4]),
                        }
                    )

            except TypeError:
                print("No reflection list to show (TypeError except)")

            except IndexError:
                print("No reflection list to show (IndexError except)")

        self.cur_nod_num = nod_num
        self.cur_img_num = in_img_num

        self.refresh_pixel_map()

        if not self.easter_egg_active:
            self.full_img_show()

    def build_background_n_get_nod_num(self, nod_or_path, in_img_num):
        if nod_or_path is True:
            nod_num = self.main_obj.current_nod_num
            cmd = {'nod_lst': [nod_num], 'cmd_lst': ["gt"]}

        elif nod_or_path is False:
            nod_num = self.main_obj.new_node.parent_node_lst[0]
            cmd = {'nod_lst': [nod_num], 'cmd_lst': ["gt"]}

        elif type(nod_or_path) is str:
            nod_num = nod_or_path
            cmd = {"path": nod_or_path, 'cmd_lst': "get_template"}
            self.exp_path = nod_or_path

        json_data_lst = json_data_request(self.uni_url, cmd)

        try:
            new_templ = json_data_lst[0]
            self.img_d1_d2 = (
                json_data_lst[1], json_data_lst[2]
            )
            if(
                self.cur_img_num != in_img_num or
                self.cur_templ != new_templ
            ):
                x_ax = np.arange(self.img_d1_d2[1])
                y_ax = np.arange(self.img_d1_d2[0])
                pi_2 = 3.14159235358 * 2.0
                sx = 1.0-(np.cos(x_ax * pi_2 / self.img_d1_d2[1]))
                sy = 1.0-(np.cos(y_ax * pi_2 / self.img_d1_d2[0]))
                xx, yy = np.meshgrid(sx, sy, sparse = True)
                self.np_full_img = xx + yy
                self.np_full_img = self.i_min_max[1] * (
                    self.np_full_img / self.np_full_img.max()
                )
            self.cur_templ = new_templ

        except (IndexError, TypeError):
            print("Not loaded new template in full")
            #TODO check what happens here if the user navigates
            #     to a different dataset

        return nod_num

    def refresh_pixel_map(self):
        show_refl = self.pop_display_menu.chk_box_show.isChecked()
        print("show_refl =", show_refl)
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
                self.my_scene(new_pixmap, self.r_list0)

            else:
                self.my_scene(new_pixmap, [])

        except (TypeError, AttributeError):
            print("None self.np_full_img")

    def change_i_min_max(self, new_i_min, new_i_max):
        self.i_min_max = [new_i_min, new_i_max]
        self.refresh_pixel_map()

    def change_palette(self, new_palette):
        self.palette = new_palette
        self.refresh_pixel_map()

    def menu_display(self, event):
        print("menu_display")

    def menu_actions(self, event):
        print("menu_actions")

    def new_full_img(self, tup_data):
        self.full_image_loaded = True
        print(
            "new_full_img from: node ", tup_data[0], ", image ", tup_data[1]
        )
        self.np_full_img = tup_data[2]
        self.refresh_pixel_map()

    def full_img_show(self):
        self.full_image_loaded = False
        try:
            #print(dir(self.load_full_image))
            self.load_full_image.quit()
            self.load_full_image.wait()

        except AttributeError:
            print("first full image loading")

        self.load_full_image = LoadFullImage(
            unit_URL = self.uni_url,
            cur_nod_num = self.cur_nod_num,
            cur_img_num = self.cur_img_num,
            path_in = self.exp_path
        )
        self.load_full_image.image_loaded.connect(self.new_full_img)
        self.load_full_image.start()

    def check_move(self):
        self.get_x1_y1_x2_y2()
        if(
            self.old_x1 != self.x1 or self.old_y1 != self.y1 or
            self.old_x2 != self.x2 or self.old_y2 != self.y2 or
            self.old_inv_scl != self.inv_scale or
            self.old_cur_nod_num != self.cur_nod_num or
            self.old_cur_img_num != self.cur_img_num
        ):
            print("scaled or dragged image")
            self.slice_show_img()

        self.old_x1 = self.x1
        self.old_y1 = self.y1
        self.old_x2 = self.x2
        self.old_y2 = self.y2
        self.old_inv_scl = self.inv_scale
        self.old_cur_nod_num = self.cur_nod_num
        self.old_cur_img_num = self.cur_img_num

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

            if dict_slice["x1"] + rep_len_x > np.size(self.np_full_img[:,0:1]):
                rep_len_x = np.size(self.np_full_img[:,0:1]) - dict_slice["x1"]
                print("limiting dx")

            if dict_slice["y1"] + rep_len_y > np.size(self.np_full_img[0:1,:]):
                rep_len_y = np.size(self.np_full_img[0:1,:]) - dict_slice["y1"]
                print("limiting dy")

            if self.full_image_loaded == False:
                self.np_full_img[
                    dict_slice["x1"]:dict_slice["x1"] + rep_len_x,
                    dict_slice["y1"]:dict_slice["y1"] + rep_len_y
                ] = rep_slice_img[0:rep_len_x, 0:rep_len_y]
                self.refresh_pixel_map()

        except TypeError:
            print("loading image slice in next loop")

        self.l_stat.load_finished()

    def update_progress(self, progress):
        #print("time to show ", progress, " in progress bar")
        self.l_stat.load_progress(progress)

    def slice_show_img(self):
        if self.full_image_loaded == False:
            self.l_stat.load_started()

            try:
                self.load_slice_image.quit()
                self.load_slice_image.wait()

            except AttributeError:
                print("first slice of image loading")

            self.get_x1_y1_x2_y2()
            self.set_inv_scale()

            self.load_slice_image = LoadSliceImage(
                unit_URL = self.uni_url,
                nod_num_lst = [self.cur_nod_num],
                img_num = self.cur_img_num,
                inv_scale = self.inv_scale,
                x1 = self.x1,
                y1 = self.y1,
                x2 = self.x2,
                y2 = self.y2,
                path_in = self.exp_path
            )
            self.load_slice_image.slice_loaded.connect(
                self.new_slice_img
            )
            self.load_slice_image.progressing.connect(
                self.update_progress
            )
            self.load_slice_image.start()

    def OneOneScale(self, event):
        print("OneOneScale")
        self.main_obj.window.imageView.resetTransform()
        avg_scale = self.get_scale_label()

    def ZoomInScale(self, event):
        print("ZoomInScale")
        self.scale_img(1.05)
        avg_scale = self.get_scale_label()

    def ZoomOutScale(self, event):
        print("ZoomOutScale")
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
                        dx <= self.img_d1_d2[0] or dy <= self.img_d1_d2[1]
                    )
                )
            ):
                self.main_obj.window.imageView.scale(
                    relative_new_scale, relative_new_scale
                )
                self.set_inv_scale()

        except TypeError:
            print("not zooming/unzooming before loading image")

    def easter_egg(self, event):
        self.easter_egg_active = not self.easter_egg_active
        print("self.easter_egg_active =", self.easter_egg_active)
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

        print("\n set_drag_mode \n mask_mode =", self.mask_mode)

    def set_mask_comp(self, mask_comp = None):
        self.mask_comp = mask_comp
        print("mask_comp =", self.mask_comp)
        if self.mask_comp is None:
            self.mask_x_ini = None
            self.mask_y_ini = None

    def on_mouse_move(self, x_pos, y_pos):
        try:
            str_out = "  I(" + str(x_pos) + ", " + str(y_pos) + ") = " +\
                      str(self.np_full_img[y_pos, x_pos]) + "  "

        except (AttributeError, IndexError, TypeError):
            str_out = " I = ?"

        self.main_obj.window.EasterEggButton.setText(str_out)
        if self.mask_mode:
            if(
                self.mask_comp is not None and
                self.mask_x_ini is not None and
                self.mask_y_ini is not None
            ):
                tmp_width = x_pos - self.mask_x_ini
                tmp_height = y_pos - self.mask_y_ini
                rectangle = QRectF(
                    self.mask_x_ini, self.mask_y_ini, tmp_width, tmp_height
                )
                self.my_scene.addRect(rectangle, self.my_scene.green_pen)


    def on_mouse_press(self, x_pos, y_pos):
        print("on_mouse_press \n x_pos, y_pos =", x_pos, y_pos)
        if self.mask_mode:
            print("mask_comp =", self.mask_comp)
            if self.mask_comp is not None:
                self.mask_x_ini = x_pos
                self.mask_y_ini = y_pos

    def on_mouse_release(self, x_pos, y_pos):
        print("on_mouse_release \n x_pos, y_pos =", x_pos, y_pos)
        if self.mask_mode:
            if(
                self.mask_comp is not None and
                self.mask_x_ini is not None and
                self.mask_y_ini is not None
            ):
                x_ini = int(self.mask_x_ini)
                x_end = int(x_pos)
                y_ini = int(self.mask_y_ini)
                y_end = int(y_pos)
                if x_ini > x_end:
                    x_ini, x_end = x_end, x_ini

                if y_ini > y_end:
                    y_ini, y_end = y_end, y_ini

                self.new_mask_comp.emit(
                    {
                        "type"  : str(self.mask_comp) ,
                        "x_ini" : x_ini ,
                        "x_end" : x_end ,
                        "y_ini" : y_ini ,
                        "y_end" : y_end ,
                    }
                )
                self.mask_x_ini = None
                self.mask_y_ini = None


class MainImgViewObject(QObject):
    def __init__(self, parent = None):
        super(MainImgViewObject, self).__init__(parent)
        self.parent_app = parent
        self.ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = self.ui_dir_path + os.sep + "view_client.ui"
        print("ui_path =", ui_path)

        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.setWindowTitle("CCP4 DUI Cloud")

        data_init = ini_data()
        data_init.set_data()
        self.uni_url = data_init.get_url()

        self.current_nod_num = 1
        self.nod_or_path = True
        self.do_image_view = DoImageView(self)

        self.window.show()

        self.window.ImgNumEdit.textChanged.connect(self.img_num_changed)
        self.window.PrevImgButton.clicked.connect(self.prev_img)
        self.window.NextImgButton.clicked.connect(self.next_img)
        self.window.OpenFileButton.clicked.connect(self.open_dir_widget)

    def refresh_output(self, nod_or_path = True):
        img_num = int(self.window.ImgNumEdit.text())
        self.do_image_view(in_img_num = img_num, nod_or_path = nod_or_path)

    def img_num_changed(self, new_img_num):
        print("should load IMG num:", new_img_num)
        self.refresh_output(nod_or_path = self.nod_or_path)

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

    def set_selection(self, str_select, isdir):
        print("str_select =", str_select, "isdir =", isdir)
        self.nod_or_path = str_select
        self.dir_selected = isdir
        self.window.IntroPathEdit.setText(self.nod_or_path)

        cmd = {"path": self.nod_or_path, 'cmd_lst': "get_template"}
        json_data_lst = json_data_request(self.uni_url, cmd)
        new_templ = json_data_lst[0]
        self.img_d1_d2 = (json_data_lst[1], json_data_lst[2])
        print("self.img_d1_d2 =", self.img_d1_d2)
        self.refresh_output(nod_or_path = self.nod_or_path)

    def open_dir_widget(self):
        #TODO make sure self.window is that goes as argument
        self.open_widget = FileBrowser(self.window)
        self.open_widget.file_or_dur_selected.connect(self.set_selection)


def main():
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    m_obj = MainImgViewObject(parent = app)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()




