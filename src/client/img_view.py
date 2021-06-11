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

from dials_viewer_ext import rgb_img
from dials.array_family import flex


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
        data2d_ini = np.copy(data2d)
        if(i_min_max == [None, None]):
            i_min_max = [data2d_ini.min(), data2d_ini.max()]
            print("no max and min provided, assuming:", i_min_max)

        elif(i_min_max[0] > data2d_ini.min() or i_min_max[1] < data2d_ini.max()):
            print("clipping to [max, min]:", i_min_max, "  ...")
            np.clip(data2d_ini, i_min_max[0], i_min_max[1], out = data2d_ini)
            print("... done clipping")

        self.width = np.size( data2d_ini[0:1, :] )
        self.height = np.size( data2d_ini[:, 0:1] )

        data2d_pos = data2d_ini[:,:] - i_min_max[0] + 1.0
        data2d_pos_max = data2d_pos.max()

        calc_pos_max = i_min_max[1] - i_min_max[0] + 1.0
        if(calc_pos_max > data2d_pos_max):
            data2d_pos_max = calc_pos_max

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
        data2d_ini = np.copy(data2d)
        if(i_min_max == [None, None]):
            i_min_max = [data2d_ini.min(), data2d_ini.max()]
            print("no max and min provided, assuming:", i_min_max)

        elif(i_min_max[0] > data2d_ini.min() or i_min_max[1] < data2d_ini.max()):
            print("clipping to [max, min]:", i_min_max, "  ...")
            np.clip(data2d_ini, i_min_max[0], i_min_max[1], out = data2d_ini)
            print("... done clipping")

        self.width = np.size( data2d_ini[0:1, :] )
        self.height = np.size( data2d_ini[:, 0:1] )

        data2d_pos = data2d_ini[:,:] - i_min_max[0] + 1.0
        data2d_pos_max = data2d_pos.max()

        calc_pos_max = i_min_max[1] - i_min_max[0] + 1.0
        if(calc_pos_max > data2d_pos_max):
            data2d_pos_max = calc_pos_max

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
    start_tm = time.time()
    try:
        req_get = requests.get(
            'http://localhost:8080/', stream = True, params = my_cmd
        )

        compresed = req_get.content

        dic_str = zlib.decompress(compresed)
        arr_dic = json.loads(dic_str)
        end_tm = time.time()
        print("request took ", end_tm - start_tm, "\n converting to dict ...")

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



    return np_array_out


class DoImageView(QObject):
    def __init__(self, parent = None):
        super(DoImageView, self).__init__(parent)
        self.main_obj = parent
        self.my_scene = QGraphicsScene()
        self.main_obj.window.imageView.setScene(self.my_scene)
        self.main_obj.window.imageView.setDragMode(QGraphicsView.ScrollHandDrag)

        self.bmp_heat = np2bmp_heat()
        self.bmp_m_cro = np2bmp_monocrome()

    def __call__(self, nod_num, in_img_num):
        np_array_img = load_json_w_str(
            nod_num_lst = [nod_num], img_num = in_img_num
        )
        try:
            rgb_np = self.bmp_m_cro.img_2d_rgb(
                data2d = np_array_img, invert = False, i_min_max = [-2, 50]
            )
            q_img = QImage(
                rgb_np.data,
                np.size(rgb_np[0:1, :, 0:1]),
                np.size(rgb_np[:, 0:1, 0:1]),
                QImage.Format_ARGB32
            )
            tmp_pixmap = QPixmap.fromImage(q_img)
            self.my_scene.addPixmap(tmp_pixmap)

        except TypeError:
            print("None np_array_img")



class Form(QObject):
    '''
    This class should only be use when testing,
    is just a quick way to show/load images
    '''
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.window = QtUiTools.QUiLoader().load("client.ui")
        self.my_scene_1 = QGraphicsScene()
        self.bmp_heat = np2bmp_heat()
        self.bmp_m_cro = np2bmp_monocrome()
        self.window.imageView.setScene(self.my_scene_1)
        self.window.imageView.setDragMode(QGraphicsView.ScrollHandDrag)
        self.window.CmdSend2server.clicked.connect(self.btn_clk)
        self.window.show()

    def btn_clk(self):
        np_array_img = load_json_w_str()
        try:
            #'''
            rgb_np = self.bmp_heat.img_2d_rgb(
                data2d = np_array_img, invert = False, i_min_max = [-2, 25]
            )

            '''
            rgb_np = self.bmp_m_cro.img_2d_rgb(
                data2d = np_array_img, invert = False, i_min_max = [-2, 50]
            )
            '''
            q_img = QImage(
                rgb_np.data,
                np.size(rgb_np[0:1, :, 0:1]),
                np.size(rgb_np[:, 0:1, 0:1]),
                QImage.Format_ARGB32
            )
            tmp_pixmap = QPixmap.fromImage(q_img)
            self.my_scene_1.addPixmap(tmp_pixmap)

        except TypeError:
            print("Must have a server running with iport done already")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())

