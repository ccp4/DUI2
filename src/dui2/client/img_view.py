"""
DUI2's image visualization main classes

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


import sys, os, logging, platform

from dui2.shared_modules.qt_libs import *
from dui2.shared_modules.img_view_utils import (
    crunch_min_max, np2bmp_monocrome, np2bmp_heat, np2bmp_mask
)

import numpy as np
import json

from dui2.client.init_firts import ini_data
from dui2.client.exec_utils import get_req_json_dat
from dui2.client.outputs import HandleLoadStatusLabel


from dui2.client.img_view_threads_n_menus import (
    LoadInThread, InfoDisplayMenu, ThresholdDisplayMenu, LoadFullImage,
    LoadSliceImage, LoadSliceMaskImage, LoadFullMaskImage
)
from dui2.client.file_nav_utils import FileBrowser


class CrosshairItem(QGraphicsItem):
    def __init__(self, positions, z_depths, z_depth_ref, pen, max_size=6, parent=None):
        super().__init__(parent)
        self.positions = positions  # List of (x,y) tuples
        self.z_depths = z_depths    # List of z_dist values
        self.z_depth_ref = z_depth_ref
        self.pen = pen
        self.max_size = max_size
        self._bounding_rect = QRectF()

        if not self.positions:
            self._bounding_rect = QRectF()
            return

        # Calculate the largest possible crosshair size
        max_paint_size = self.max_size
        min_x = min(pos[0] for pos in self.positions) - max_paint_size
        max_x = max(pos[0] for pos in self.positions) + max_paint_size
        min_y = min(pos[1] for pos in self.positions) - max_paint_size
        max_y = max(pos[1] for pos in self.positions) + max_paint_size

        self._bounding_rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        for (x, y), z_dist in zip(self.positions, self.z_depths):
            paint_size = self.max_size - 4.0 * z_dist / self.z_depth_ref
            # Vertical line
            painter.drawLine(x, y - paint_size, x, y + paint_size)
            # Horizontal line
            painter.drawLine(x - paint_size, y, x + paint_size, y)

    def boundingRect(self):
        return self._bounding_rect


class MultiRectItem(QGraphicsItem):
    def __init__(self, rects, pen, parent=None):
        super().__init__(parent)
        self.rects = rects  # List of QRectF
        self.pen = pen
        self._bounding_rect = QRectF()

        if not self.rects:
            self._bounding_rect = QRectF()
            return

        self._bounding_rect = self.rects[0]
        for rect in self.rects[1:]:
            self._bounding_rect = self._bounding_rect.united(rect)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        for rect in self.rects:
            painter.drawRect(rect)

    def boundingRect(self):
        return self._bounding_rect


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

        self._multi_rect_item = None  # Will hold our optimized item
        self._crosshair_item = None  # Will hold our optimized item

        self.draw_all_hkl = False
        self.draw_near_hkl = True
        self.beam_xy_pair = (-1, -1)

        timer_4_b_centr = QTimer(self)
        timer_4_b_centr.timeout.connect(self.check_if_draw_b_centr)
        self.draw_b_center = False
        timer_4_b_centr.start(500)

    def draw_ref_rect(self):

        self.clear()
        if self.my_pix_map is not None:
            self.curr_pixmap = self.my_pix_map

        self.addPixmap(self.curr_pixmap)
        if self.parent_obj.pop_display_menu.rad_but_obs.isChecked():
            tick_size = 10.0
            # Create list of QRectF objects first
            rects = [QRectF(refl["x"], refl["y"], refl["width"], refl["height"])
                    for refl in self.refl_list]

            self._multi_rect_item = MultiRectItem(rects, self.overlay_pen1)
            self.addItem(self._multi_rect_item)

            for refl in self.refl_list:
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

            # Prepare data for the crosshair item
            positions = [(refl["x"], refl["y"]) for refl in self.refl_list]
            z_depths = [refl["z_dist"] for refl in self.refl_list]

            self._crosshair_item = CrosshairItem(
                positions, z_depths, z_dept_fl,
                self.overlay_pen1, max_size=6
            )
            self.addItem(self._crosshair_item)


        if self.my_mask_pix_map is not None:
            self.addPixmap(self.my_mask_pix_map)

    def check_if_draw_b_centr(self):
        if self.draw_b_center:
            self.draw_beam_center()

        self.draw_b_center = False

    def draw_beam_center(self):
        x_bc = self.beam_xy_pair[0]
        y_bc = self.beam_xy_pair[1]
        l_size = 20.0
        self.addLine(
            x_bc, y_bc - l_size, x_bc, y_bc + l_size, self.overlay_pen1
        )

        self.addLine(
            x_bc - l_size, y_bc, x_bc + l_size, y_bc, self.overlay_pen1
        )

    def update_tmp_mask(self, new_temp_mask):
        self.temp_mask = new_temp_mask
        self.draw_b_center = True

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
            logging.info("Type Err Catch(draw_temp_mask)")

    def __call__(
        self, new_pixmap, refl_list1, new_temp_mask, new_beam_xy_pair
    ):
        self.my_pix_map = new_pixmap
        self.refl_list = refl_list1
        self.temp_mask = new_temp_mask
        self.beam_xy_pair = new_beam_xy_pair
        self.refresh_imgs()
        self.draw_b_center = True

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

        zoom_full_out_icon = QIcon()
        zoom_full_out_icon_path = res_ico_path + os.sep + "zoom_border.png"
        zoom_full_out_icon.addFile(zoom_full_out_icon_path, mode = QIcon.Normal)
        self.main_obj.window.UnZoomFullButton.setIcon(zoom_full_out_icon)
        self.main_obj.window.UnZoomFullButton.clicked.connect(self.UnZoomFullImg)

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
        self.overlay = "cyan"

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
        self.pop_display_menu.new_mask_y_n.connect(self.update_masking)

        self.pop_display_menu.save_img_2_disc.connect(self.save_img_file)

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
        self.beam_xy_pair = None

        self.load_thread_list = []

        (self.old_x1, self.old_y1, self.old_x2, self.old_y2) = (-1, -1, -1, -1)
        self.old_inv_scl = self.inv_scale
        self.old_nod_num = self.cur_nod_num
        self.old_img_num = self.cur_img_num

        self.list_temp_mask = None

        self.threshold_params = None
        self.old_threshold_params = None

        timer_4_move = QTimer(self)
        timer_4_move.timeout.connect(self.check_move)
        timer_4_move.start(1600)

        timer_4_resolution = QTimer(self)
        timer_4_resolution.timeout.connect(self.check_if_new_mouse_xy)
        self.mouse_xy = (-1, -1)
        self.old_mouse_xy = self.mouse_xy
        self.mouse_moving = False
        timer_4_resolution.start(350)

        QTimer.singleShot(4000, self.try_2_un_zoom)

    def __call__(
        self, in_img_num, nod_or_path = True,
        on_filter_reflections = False
    ):
        self.cur_img_num = in_img_num
        self.nod_or_path = nod_or_path
        self.exp_path = None
        self.on_filter_reflections = on_filter_reflections
        self.build_background_n_get_nod_num(self.cur_img_num)
        logging.info("self.threshold_params =" + str(self.threshold_params))

    def add_2_thread_list_n_review(self, new_thread):
        if len(self.load_thread_list) > 20:
            for num, single_thread in enumerate(self.load_thread_list[0:-10]):
                if single_thread.isRunning():
                    try:
                        single_thread.quit()
                        #single_thread.wait()

                    except AttributeError:
                        logging.info("no need to quit n" + str(num) + " thread")

        if len(self.load_thread_list) > 60:
            logging.info("erased bunch of threads")
            del self.load_thread_list[0:-45]

        self.load_thread_list.append(new_thread)

    def save_img_file(self):
        print("save_img_file")

    def quit_kill_all(self):
        for thread in self.load_thread_list:
            if thread.isRunning():
                thread.quit()
                if not thread.wait(1200):  # Wait up to 1.2 seconds per thread
                    print(f"Thread {thread} did not exit gracefully")
                    logging.info("Thread: " + str(thread) + " did not exit gracefully")
                    thread.terminate()  # Force termination if necessary

                thread.wait()

    def set_just_imported(self):
        self.just_imported = True

    def try_2_un_zoom(self):
        self.UnZoomFullImg(None)

    def tune_palette_ini(
        self,x_ini = None, x_end = None, y_ini = None, y_end = None
    ):
        if self.just_imported == True:
            try:
                medi_i = np.median(self.np_full_img[x_ini: x_end, y_ini: y_end])
                i_max_to_edit = str(int((medi_i + 1) * 10))
                logging.info("moving max palette to: " + i_max_to_edit)
                self.pop_display_menu.i_max_line.setText(i_max_to_edit)

                #TODO is it here where we want to call the UnZoomFullImg?
                self.UnZoomFullImg(None)

            except TypeError:
                logging.info("Type Err catch(tune_palette_ini)")

        self.just_imported = False

    def update_threshold_params(self, new_params):
        self.pop_display_menu.set_thresh_mask()
        self.threshold_params = new_params
        self.emit_reload()

    def update_masking(self):
        if self.pop_display_menu.exl_mask_rad.isChecked():
            self.threshold_params = None
            logging.info("exl_mask_rad.isChecked")

        elif self.pop_display_menu.threshol_mask_rad.isChecked():
            self.threshold_params = self.pop_threshold_menu.threshold_params_dict
            logging.info("threshol_mask_rad.isChecked")

        logging.info("update_masking")
        self.emit_reload()

    def emit_reload(self):
        self.need_2_reload.emit()

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

        load_template_thread = LoadInThread(
            self.uni_url, my_cmd, self.my_handler
        )
        load_template_thread.request_loaded.connect(
            self.after_requesting_template
        )

        load_template_thread.start()
        self.add_2_thread_list_n_review(load_template_thread)

    def after_requesting_template(self, tup_data):
        try:
            json_data_dict = tup_data[0]
            new_templ = str(json_data_dict["str_json"])
            logging.info("new_templ = " + new_templ)
            self.img_d1_d2 = (
                json_data_dict["img_with"], json_data_dict["img_height"]
            )
            new_img_path = str(json_data_dict["img_path"])
            self.cur_img_num = int(json_data_dict["new_img_num"])
            self.main_obj.window.ImgNumEdit.setText(str(self.cur_img_num))
            self.i23_multipanel = bool(json_data_dict["i23_multipanel"])
            self.beam_xy_pair = (
                float(json_data_dict["x_beam_pix"]),
                float(json_data_dict["y_beam_pix"])
            )

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
            self.np_full_img = None

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
            load_reflx_thread = LoadInThread(
                self.uni_url, my_cmd, self.my_handler
            )
            if self.pop_display_menu.rad_but_obs.isChecked():
                load_reflx_thread.request_loaded.connect(
                    self.after_requesting_ref_lst
                )

            else:
                load_reflx_thread.request_loaded.connect(
                    self.after_requesting_predict_lst
                )

            load_reflx_thread.start()
            self.add_2_thread_list_n_review(load_reflx_thread)

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
        try:
            if len(self.r_list0) > 0 or len(self.r_list1) > 0:
                logging.info("un-ticking << show threshold >> option")
                self.pop_threshold_menu.threshold_box_show.setChecked(False)

        except AttributeError:
            logging.info(
                "leaving << show threshold >> untouched, no reflection list"
            )

        except RuntimeError:
            logging.info(
                "Runtime Err Catch, seems to be running without this menu 1"
            )

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
                        new_pixmap, self.r_list0, self.list_temp_mask,
                        self.beam_xy_pair
                    )

                else:
                    self.my_scene(
                        new_pixmap, self.r_list1, self.list_temp_mask,
                        self.beam_xy_pair
                    )

            else:
                self.my_scene(
                    new_pixmap, [], self.list_temp_mask, self.beam_xy_pair
                )

        except (TypeError, AttributeError):
            logging.info("None self.np_full_img")

        try:
            if(
                self.pop_display_menu.exl_mask_rad.isChecked() or
                self.pop_display_menu.threshol_mask_rad.isChecked()
            ):
                data_mask = self.np_full_mask_img
            else:
                data_mask= np.zeros((
                    self.img_d1_d2[0], self.img_d1_d2[1]
                ), dtype = 'float')


            m_rgb_np = self.bmp_mask.img_2d_rgb(
                data2d = data_mask,
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
            self.my_scene.self.draw_b_center = True

        except AttributeError:
            logging.info("no mask to draw here")

        except RuntimeError:
            logging.info(
                "Runtime Err Catch, seems to be running without this menu 2"
            )

        except TypeError:
            logging.info(
                "Type Err Catch, attempting to show a mask without xy(max)"
            )

    def change_i_min_max(self, new_i_min, new_i_max):
        self.i_min_max = [new_i_min, new_i_max]
        self.refresh_pixel_map()

    def change_palette(self, new_palette):
        self.palette = new_palette
        self.refresh_pixel_map()

    def change_mask_colour(self, new_colour):
        self.mask_colour = new_colour
        self.refresh_pixel_map()

    def change_mask_transp(self, new_transp):
        self.mask_transp = new_transp
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
        self.full_mask_show()

    def new_full_mask_img(self, tup_data):
        self.np_full_mask_img = tup_data[2]
        self.refresh_pixel_map()

    def full_img_show(self):
        self.full_image_loaded = False
        load_full_image_thread = LoadFullImage(
            unit_URL = self.uni_url,
            cur_nod_num = self.cur_nod_num,
            cur_img_num = self.cur_img_num,
            path_in = self.exp_path,
            main_handler = self.my_handler
        )

        load_full_image_thread.image_loaded.connect(self.new_full_img)
        load_full_image_thread.start()
        self.add_2_thread_list_n_review(load_full_image_thread)

    def full_mask_show(self):
        load_full_mask_image_thread = LoadFullMaskImage(
            unit_URL = self.uni_url,
            cur_nod_num = self.cur_nod_num,
            cur_img_num = self.cur_img_num,
            path_in = self.exp_path,
            thrs_pars_in = self.threshold_params,
            main_handler = self.my_handler
        )
        load_full_mask_image_thread.image_loaded.connect(self.new_full_mask_img)
        load_full_mask_image_thread.start()
        self.add_2_thread_list_n_review(load_full_mask_image_thread)

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

    def check_if_new_mouse_xy(self):
        if self.mouse_xy != self.old_mouse_xy:
            self.old_mouse_xy = self.mouse_xy
            self.mouse_moving = True

        elif self.mouse_moving:
            self.get_resolution_if_stopped_moving()
            self.mouse_moving = False

    def get_resolution_if_stopped_moving(self):
        x_pnt = self.mouse_xy[0]
        y_pnt = self.mouse_xy[1]
        panel_num = 0
        try:
            if self.i23_multipanel:
                panel_height = 213
                panel_num = int(y_pnt / panel_height)
                y_pnt = y_pnt - float(panel_num * panel_height)

            full_cmd = {
                'nod_lst': [self.cur_nod_num],
                'cmd_str': [
                    'get_resolution', 'panel=' + str(panel_num),
                    'xy_coordinates=' + str(x_pnt) + ',' + str(y_pnt)
                ]
            }
            lst_req = get_req_json_dat(
                params_in = full_cmd, main_handler = self.my_handler
            )
            self.resolution = lst_req.result_out()[0]

            logging.info("resolution 2 update = " + str(self.resolution))
            self.update_real_time_label(x_pnt, y_pnt)

        except TypeError:
            logging.info("Type Err catch  while getting resolution")

        except IndexError:
            logging.info("Index Err catch  while getting resolution")

        except AttributeError:
            logging.info("Attribute Err catch  while getting resolution")

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

    def get_scale_n_set_label(self):
        avg_scale = float(
            self.main_obj.window.imageView.transform().m11() +
            self.main_obj.window.imageView.transform().m22()
        ) / 2.0
        avg_scale = abs(avg_scale)
        str_label = "scale = {:3.3}".format(avg_scale)
        self.main_obj.window.InvScaleLabel.setText(str_label)
        return avg_scale

    def set_inv_scale(self):
        avg_scale = self.get_scale_n_set_label()
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
            self.get_x1_y1_x2_y2()
            self.set_inv_scale()
            load_slice_image_thread = LoadSliceImage(
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
            load_slice_image_thread.slice_loaded.connect(
                self.new_slice_img
            )
            load_slice_image_thread.progressing.connect(
                self.update_progress
            )
            load_slice_image_thread.start()
            self.add_2_thread_list_n_review(load_slice_image_thread)

            # Now Same for mask
            load_slice_mask_thread = LoadSliceMaskImage(
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
            load_slice_mask_thread.slice_loaded.connect(
                self.new_slice_mask_img
            )
            load_slice_mask_thread.progressing.connect(
                self.update_progress
            )
            load_slice_mask_thread.start()
            self.add_2_thread_list_n_review(load_slice_mask_thread)

    def OneOneScale(self, event):
        logging.info("OneOneScale")
        self.main_obj.window.imageView.resetTransform()
        avg_scale = self.get_scale_n_set_label()

    def ZoomInScale(self, event):
        logging.info("ZoomInScale")
        self.scale_img(1.05)
        avg_scale = self.get_scale_n_set_label()

    def ZoomOutScale(self, event):
        logging.info("ZoomOutScale")
        self.scale_img(0.95)
        avg_scale = self.get_scale_n_set_label()

    def UnZoomFullImg(self, event):
        try:
            img_d1, img_d2 = self.img_d1_d2[0], self.img_d1_d2[1]
            self.main_obj.window.imageView.fitInView(
                QRect(0,0, img_d2, img_d1), aspectRadioMode=Qt.KeepAspectRatio
            )
            avg_scale = self.get_scale_n_set_label()

        except TypeError:
            print("not need to zoom-out")

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
            #self.main_obj.window.imageView.setMatrix(
            self.main_obj.window.imageView.setTransform(
                #QMatrix(
                QTransform(
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
            self.pop_display_menu.set_exl_mask()

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

    def update_real_time_label(self, x_pos, y_pos):
        try:
            str_out = "  I(" + str(x_pos) + ", " + str(y_pos) + ")  =  " +\
                  "{:8.1f}".format(self.np_full_img[y_pos, x_pos])

        except (AttributeError, IndexError, TypeError):
            str_out = " I  =  ?"

        try:
            str_out += "  mask=" + str(self.np_full_mask_img[y_pos, x_pos])

        except (AttributeError, IndexError, TypeError):
            str_out += "  mask = ?"

        try:
            str_out += "  Resolution=" + "{:8.2f}".format(self.resolution)

        except (AttributeError, TypeError):
            str_out += "  Resolution= ? "

        self.main_obj.window.EasterEggButton.setText(str_out)

    def on_mouse_move(self, x_pos, y_pos):
        #TODO: maybe self.update_real_time_label... can be done only when stop
        #TODO: moving the mouse consider if the next line should run ALWAYS
        self.update_real_time_label(x_pos, y_pos)

        self.mouse_xy = (x_pos, y_pos)
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
                    r = float(np.sqrt(dx * dx + dy * dy) / 2.0)
                    xc = self.mask_x_ini + dx / 2.0
                    yc = self.mask_y_ini + dy / 2.0
                    x1 = xc - r
                    y1 = yc - r
                    rectangle1 = QRectF(
                        x1, y1, 2 * r, 2 * r
                    )
                    self.my_scene.addEllipse(
                        rectangle1, self.my_scene.overlay_pen1
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
                    dx = float(x_pos - self.mask_x_ini)
                    dy = float(y_pos - self.mask_y_ini)
                    r = int(np.sqrt(dx * dx + dy * dy) / 2)
                    xc = int(self.mask_x_ini + dx / 2.0)
                    yc = int(self.mask_y_ini + dy / 2.0)

                    self.new_mask_comp.emit(
                        {
                            "type"              : "circ" ,
                            "x_c"               :  xc ,
                            "y_c"               :  yc ,
                            "r"                 :  r  ,
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
        try:
            json_data_dict = lst_req.result_out()[0]
            new_templ = str(json_data_dict["str_json"])
            logging.info("new_templ = " + new_templ)
            self.img_d1_d2 = (
                json_data_dict["img_with"], json_data_dict["img_height"]
            )
            self.refresh_output(nod_or_path = self.nod_or_path)

        except(TypeError, IndexError):
            logging.info("Type Err catch while opening imgs")

    def open_dir_widget(self):
        cmd = {"nod_lst":"", "cmd_str":["dir_path"]}
        lst_req = get_req_json_dat(
            params_in = cmd, main_handler = self.my_handler
        )
        dic_str = lst_req.result_out()
        init_path = dic_str[0]

        self.open_widget = FileBrowser(
            self.window, path_ini = init_path, limit_path = init_path,
            only_dir = False
        )
        self.open_widget.resize(self.open_widget.size() * 2)
        self.open_widget.select_done.connect(self.set_selection)


def main(par_def = None):

    if platform.system() == "Windows":
        win_str = "true"

    else:
        #TODO: test this variables on m1 mac
        win_str = "false"
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        os.environ["WAYLAND_DISPLAY"] = ""

    data_init = ini_data()
    data_init.set_data(par_def)
    uni_url = data_init.get_url()
    app = QApplication(sys.argv)
    m_obj = MainImgViewObject(parent = app)
    sys.exit(app.exec_())

