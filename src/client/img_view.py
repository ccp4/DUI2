import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtUiTools

import numpy as np
import json
import zlib
import time
import requests

from exec_utils import json_data_request, uni_url
from outputs import HandleLoadStatusLabel

def crunch_min_max(data2d, i_min_max):
    data2d_ini = np.copy(data2d)
    if(i_min_max == [None, None]):
        i_min_max = [data2d_ini.min(), data2d_ini.max()]
        print("no max and min provided, assuming:", i_min_max)

    elif(i_min_max[0] > data2d_ini.min() or i_min_max[1] < data2d_ini.max()):
        np.clip(data2d_ini, i_min_max[0], i_min_max[1], out = data2d_ini)

    width = np.size( data2d_ini[0:1, :] )
    height = np.size( data2d_ini[:, 0:1] )

    data2d_pos = data2d_ini[:,:] - i_min_max[0] + 1.0
    data2d_pos_max = data2d_pos.max()

    calc_pos_max = i_min_max[1] - i_min_max[0] + 1.0
    if(calc_pos_max > data2d_pos_max):
        data2d_pos_max = calc_pos_max

    return data2d_pos, data2d_pos_max, width, height


class np2bmp_heat(object):
    def __init__(self):
        self.red_byte = np.empty( (255 * 3), 'int')
        self.green_byte = np.empty( (255 * 3), 'int')
        self.blue_byte = np.empty( (255 * 3), 'int')

        for i in range(255):
            self.red_byte[i] = i
            self.green_byte[i + 255] = i
            self.blue_byte[i + 255 * 2 ] = i

        self.red_byte[255:255 * 3] = 255
        self.green_byte[0:255] = 0
        self.green_byte[255 * 2 : 255 * 3] = 255
        self.blue_byte[0:255 * 2] = 0

        self.blue_byte[764] = 255
        self.red_byte[764] = 255
        self.green_byte[764] = 255

    def img_2d_rgb(
        self, data2d = None, invert = False, i_min_max = [None, None]
    ):
        data2d_pos, data2d_pos_max, self.width, self.height = crunch_min_max(
            data2d, i_min_max
        )
        div_scale = 764.0 / data2d_pos_max
        data2d_scale = np.multiply(data2d_pos, div_scale)
        if(invert == True):
            for x in np.nditer(
                data2d_scale[:,:], op_flags=['readwrite'],
                flags=['external_loop']
            ):
                x[...] = 764.0 - x[...]

        img_array = np.zeros([self.height, self.width, 4], dtype=np.uint8)
        img_array_r = np.empty( (self.height, self.width), 'int')
        img_array_g = np.empty( (self.height, self.width), 'int')
        img_array_b = np.empty( (self.height, self.width), 'int')
        scaled_i = np.empty( (self.height, self.width), 'int')
        scaled_i[:,:] = data2d_scale[:,:]

        img_array_r[:,:] = scaled_i[:,:]
        for x in np.nditer(
            img_array_r[:,:], op_flags=['readwrite'],
            flags=['external_loop']
        ):
            x[...] = self.red_byte[x]

        img_array_g[:,:] = scaled_i[:,:]
        for x in np.nditer(
            img_array_g[:,:], op_flags=['readwrite'],
            flags=['external_loop']
        ):
            x[...] = self.green_byte[x]

        img_array_b[:,:] = scaled_i[:,:]
        for x in np.nditer(
            img_array_b[:,:], op_flags=['readwrite'],
            flags=['external_loop']
        ):
            x[...] = self.blue_byte[x]

        img_array[:, :, 3] = 255
        img_array[:, :, 2] = img_array_r[:,:] #Blue
        img_array[:, :, 1] = img_array_g[:,:] #Green
        img_array[:, :, 0] = img_array_b[:,:] #Red
        return img_array


class np2bmp_monocrome(object):
    def __init__(self):
        self.all_chan_byte = np.empty( (255), 'int')
        for i in range(255):
            self.all_chan_byte[i] = i

    def img_2d_rgb(
        self, data2d = None, invert = False, i_min_max = [None, None]
    ):
        data2d_pos, data2d_pos_max, self.width, self.height = crunch_min_max(
            data2d, i_min_max
        )

        div_scale = 254.0 / data2d_pos_max
        data2d_scale = np.multiply(data2d_pos, div_scale)
        if(invert == True):
            for x in np.nditer(
                data2d_scale[:,:], op_flags=['readwrite'],
                flags=['external_loop']
            ):
                x[...] = 254.0 - x[...]

        img_array = np.zeros([self.height, self.width, 4], dtype=np.uint8)
        img_all_chanl = np.empty( (self.height, self.width), 'int')
        scaled_i = np.empty( (self.height, self.width), 'int')
        scaled_i[:,:] = data2d_scale[:,:]

        img_all_chanl[:,:] = scaled_i[:,:]
        for x in np.nditer(
            img_all_chanl[:,:], op_flags=['readwrite'],
            flags=['external_loop']
        ):
            x[...] = self.all_chan_byte[x]

        img_array[:, :, 3] = 255
        img_array[:, :, 2] = img_all_chanl[:,:] #Blue
        img_array[:, :, 1] = img_all_chanl[:,:] #Green
        img_array[:, :, 0] = img_all_chanl[:,:] #Red
        return img_array


def load_json_w_str(nod_num_lst = [1], img_num = 0):
    my_cmd_lst = ["gi " + str(img_num)]
    my_cmd = {"nod_lst":nod_num_lst, "cmd_lst":my_cmd_lst}

    print("\n full img here \n")
    try:
        start_tm = time.time()
        req_get = requests.get(uni_url, stream=True, params = my_cmd)
        total_size = int(req_get.headers.get('content-length', 0)) + 1
        print("total_size =", total_size)
        #block_size = 1024 #1 Kibibyte
        block_size = 65536
        downloaded_size = 0
        compresed = bytes()
        print("starting to load full image ...")
        for data in req_get.iter_content(block_size):
            compresed += data
            downloaded_size += block_size
            progress = int(100.0 * (downloaded_size / total_size))
            #print("progress(full image) =", progress )

        print("... finished loading full image")

        dic_str = zlib.decompress(compresed)
        arr_dic = json.loads(dic_str)
        end_tm = time.time()
        print("request took ", end_tm - start_tm)
        d1 = arr_dic["d1"]
        d2 = arr_dic["d2"]
        str_data = arr_dic["str_data"]
        print("d1, d2 =", d1, d2)
        arr_1d = np.fromstring(str_data, dtype = float, sep = ',')
        np_array_out = arr_1d.reshape(d1, d2)

    except zlib.error:
        print("zlib.error(load_json_w_str)")
        return None

    except ConnectionError:
        print("\n ConnectionError (load_json_w_str) \n")
        return None

    except requests.exceptions.RequestException:
        print("\n requests.exceptions.RequestException (load_json_w_str) \n")
        return None

    except ZeroDivisionError:
        print("\n ZeroDivisionError (load_json_w_str) \n")
        return None

    return np_array_out


class LoadFullImage(QThread):
    image_loaded = Signal(tuple)
    def __init__(self, cur_nod_num, cur_img_num):
        super(LoadFullImage, self).__init__()
        self.cur_nod_num = cur_nod_num
        self.cur_img_num = cur_img_num

    def run(self):
        print("loading image ", self.cur_img_num, " in full resolution")
        np_full_img = load_json_w_str(
            nod_num_lst = [self.cur_nod_num],
            img_num = self.cur_img_num
        )
        self.image_loaded.emit(
            (self.cur_nod_num, self.cur_img_num, np_full_img)
        )


class LoadSliceImage(QThread):
    progressing = Signal(int)
    slice_loaded = Signal(dict)
    def __init__(
        self, parent_obj, nod_num_lst, img_num, inv_scale,x1 ,y1 ,x2 ,y2
    ):
        super(LoadSliceImage, self).__init__()
        self.parent_obj =   parent_obj
        self.nod_num_lst =  nod_num_lst
        self.img_num =      img_num
        self.inv_scale =    inv_scale
        self.x1 =           x1
        self.y1 =           y1
        self.x2 =           x2
        self.y2 =           y2

    def run(self):
        print("loading slice of image ")

        my_cmd_lst = [
            "gis " + str(self.img_num) +
            " inv_scale=" + str(self.inv_scale) +
            " view_rect=" + str(self.x1) + "," + str(self.y1) +
                      "," + str(self.x2) + "," + str(self.y2)
        ]

        my_cmd = {"nod_lst":self.nod_num_lst, "cmd_lst":my_cmd_lst}
        start_tm = time.time()
        try:
            req_get = requests.get(uni_url, stream=True, params = my_cmd)
            total_size = int(req_get.headers.get('content-length', 0)) + 1
            print("total_size =", total_size)
            block_size = 65536
            downloaded_size = 0
            compresed = bytes()
            for data in req_get.iter_content(block_size):
                compresed += data
                downloaded_size += block_size
                progress = int(100.0 * (downloaded_size / total_size))

                #next commented line seems to be the culprit of a segmentation fault
                self.progressing.emit(progress)

            dic_str = zlib.decompress(compresed)
            arr_dic = json.loads(dic_str)
            end_tm = time.time()
            print("request took ", end_tm - start_tm)

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

    def __init__(self, parent = None):
        super(ImgGraphicsScene, self).__init__(parent)
        self.parent_obj = parent
        self.curr_pixmap = None

    def __call__(self, new_pixmap, refl_list0):
        to_use_later = '''
    def __call__(self, new_pixmap, refl_list0, refl_list1):
        '''
        self.clear()
        if new_pixmap is not None:
            self.curr_pixmap = new_pixmap

        self.addPixmap(self.curr_pixmap)

        green_pen = QPen(
            Qt.green, 0.8, Qt.SolidLine,
            Qt.RoundCap, Qt.RoundJoin
        )
        for refl in refl_list0:
            rectangle = QRectF(
                refl["x"], refl["y"], refl["width"], refl["height"]
            )
            self.addRect(rectangle, green_pen)


            n_text = self.addSimpleText(str(refl["local_hkl"]))
            n_text.setPos(refl["x"], refl["y"])
            n_text.setPen(green_pen)

        to_use_later = '''
        for refl in refl_list1:
            self.addLine(
                refl["x_ini"] + 1 + refl["xrs_size"], refl["y_ini"] + 1,
                refl["x_ini"] + 1 - refl["xrs_size"], refl["y_ini"] + 1,
                green_pen
            )
            self.addLine(
                refl["x_ini"] + 1, refl["y_ini"] + 1 + refl["xrs_size"],
                refl["x_ini"] + 1, refl["y_ini"] + 1 - refl["xrs_size"],
                green_pen
            )
        '''

    def wheelEvent(self, event):
        float_delta = float(event.delta())
        new_scale = 1.0 + float_delta / 1500.0
        self.img_scale.emit(new_scale)
        event.accept()


class DoImageView(QObject):
    def __init__(self, parent = None):
        super(DoImageView, self).__init__(parent)
        self.main_obj = parent

        self.l_stat = HandleLoadStatusLabel(self.main_obj)

        self.my_scene = ImgGraphicsScene(self)
        self.main_obj.window.imageView.setScene(self.my_scene)
        self.main_obj.window.imageView.setDragMode(
            QGraphicsView.ScrollHandDrag
        )
        self.main_obj.window.ScaleOneOneButton.clicked.connect(
            self.OneOneScale
        )

        self.my_scene.img_scale.connect(self.scale_img)

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

    def __call__(self, in_img_num, nod_in_lst):
        print(
            "refreshing Image Viewer\n img:", in_img_num,
            "\n node in List:", nod_in_lst
        )
        self.r_list0 = []
        #self.r_list1 = []

        if nod_in_lst:
            nod_num = self.main_obj.current_nod_num

        else:
            nod_num = self.main_obj.new_node.parent_node_lst[0]

        cmd = {'nod_lst': [nod_num], 'cmd_lst': ["gt"]}
        json_data_lst = json_data_request(uni_url, cmd)

        try:
            new_templ = json_data_lst[0]
            self.img_d1_d2 = (
                json_data_lst[1], json_data_lst[2]
            )
            if(
                self.cur_img_num != in_img_num or
                self.cur_templ != new_templ
            ):
                ##############################################
                x_ax = np.arange(self.img_d1_d2[1])
                y_ax = np.arange(self.img_d1_d2[0])
                pi_2 = 3.14159235358 * 2.0
                sx = 1.0-(np.cos(x_ax * pi_2 / self.img_d1_d2[1]))
                sy = 1.0-(np.cos(y_ax * pi_2 / self.img_d1_d2[0]))
                xx, yy = np.meshgrid(sx, sy, sparse = True)
                self.np_full_img = xx + yy
                ##############################################
                '''
                self.np_full_img = np.arange(
                    self.img_d1_d2[0] * self.img_d1_d2[1]
                ).reshape(
                    self.img_d1_d2[0], self.img_d1_d2[1]
                )
                '''
                self.np_full_img = 50 * (
                    self.np_full_img / self.np_full_img.max()
                )
            self.cur_templ = new_templ

        except (IndexError, TypeError):
            print("Not loaded new template in full")
            #TODO check what happens here if the user navigates
            #     to a different dataset

        if nod_in_lst:
            my_cmd = {
                'nod_lst': [nod_num], 'cmd_lst': ["grl " + str(in_img_num)]
            }
            json_lst = json_data_request(uni_url, my_cmd)
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
                to_remove = '''
                for inner_list in json_lst[1]:
                    lst_str1 = inner_list[0].split(',')
                    x_ini = float(lst_str1[0])
                    y_ini = float(lst_str1[1])
                    xrs_size = int(lst_str1[2])
                    size2 = int(lst_str1[3])
                    local_hkl = str(inner_list[1])
                    self.r_list1.append(
                       {
                         "x_ini"       : x_ini     ,
                         "y_ini"       : y_ini     ,
                         "xrs_size"    : xrs_size  ,
                         "size2"       : size2     ,
                         "local_hkl"   : local_hkl ,
                       }
                    )
                '''
            except TypeError:
                print("No reflection list to show (TypeError except)")

        else:
            print("No reflection list to show (known not to be)")

        self.cur_nod_num = nod_num
        self.cur_img_num = in_img_num

        self.refresh_pixel_map()
        #self.full_img_show()

    def refresh_pixel_map(self):
        try:
            rgb_np = self.bmp_m_cro.img_2d_rgb(
                data2d = self.np_full_img, invert = False,
                i_min_max = [-2, 50]
            )
            q_img = QImage(
                rgb_np.data,
                np.size(rgb_np[0:1, :, 0:1]),
                np.size(rgb_np[:, 0:1, 0:1]),
                QImage.Format_ARGB32
            )
            new_pixmap = QPixmap.fromImage(q_img)
            self.my_scene(new_pixmap, self.r_list0)
            #self.my_scene(new_pixmap, self.r_list0, self.r_list1)

        except (TypeError, AttributeError):
            print("None self.np_full_img")

    def new_full_img(self, tup_data):
        print(
            "new_full_img from: node ", tup_data[0], ", image ", tup_data[1]
        )
        self.full_image_loaded = True
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
            cur_nod_num = self.cur_nod_num, cur_img_num = self.cur_img_num
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

    def get_x1_y1_x2_y2(self):
        viewport_rect = QRect(
            0, 0, self.main_obj.window.imageView.viewport().width(),
            self.main_obj.window.imageView.viewport().height()
        )
        visibleSceneRect = self.main_obj.window.imageView.mapToScene(
            viewport_rect
        ).boundingRect()
        visibleSceneCoords = visibleSceneRect.getCoords()
        self.x1 = int(visibleSceneCoords[1])
        self.y1 = int(visibleSceneCoords[0])
        self.x2 = int(visibleSceneCoords[3])
        self.y2 = int(visibleSceneCoords[2])
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

    def get_inv_scale(self):
        avg_scale = float(
            self.main_obj.window.imageView.transform().m11() +
            self.main_obj.window.imageView.transform().m22()
        ) / 2.0
        avg_scale = abs(avg_scale)
        self.inv_scale = int(1.0 / avg_scale)
        if self.inv_scale < 1:
            self.inv_scale = 1

        if self.inv_scale > 36:
            self.inv_scale = 36

        str_label = "scale = 1 / " + str(self.inv_scale)
        self.main_obj.window.InvScaleLabel.setText(str_label)

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
        #if self.full_image_loaded == False:
        self.l_stat.load_started()

        try:
            self.load_slice_image.quit()
            self.load_slice_image.wait()

        except AttributeError:
            print("first slice of image loading")

        self.get_x1_y1_x2_y2()
        self.get_inv_scale()

        self.load_slice_image = LoadSliceImage(
            parent_obj = self,
            nod_num_lst = [self.cur_nod_num],
            img_num = self.cur_img_num,
            inv_scale = self.inv_scale,
            x1 = self.x1,
            y1 = self.y1,
            x2 = self.x2,
            y2 = self.y2
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

    def scale_img(self, relative_new_scale):
        self.main_obj.window.imageView.scale(
            relative_new_scale, relative_new_scale
        )
        self.get_inv_scale()

