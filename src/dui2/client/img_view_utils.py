"""
DUI2's array to image conversion tools on client's side

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


import numpy as np
import time, logging

from dui2.client.init_firts import ini_data
from dui2.client.exec_utils import get_request_shot

def load_img_json_w_str(
    uni_url = None, nod_num_lst = [1], img_num = 0,
    exp_path = None, main_handler = None
):
    my_cmd_lst = ["gi", str(img_num)]
    my_cmd = {"nod_lst" : nod_num_lst,
              "path"    : exp_path,
              "cmd_str" : my_cmd_lst}

    print("\n\n load_img_json_w_str   ... Ini")
    try:
        start_tm = time.time()
        req_shot = get_request_shot(
            params_in = my_cmd, main_handler = main_handler
        )
        byte_json =  req_shot.result_out()
        d1d2_n_arr1d = np.frombuffer(byte_json, dtype = float)
        d1 = int(d1d2_n_arr1d[0])
        d2 = int(d1d2_n_arr1d[1])
        np_array_out = d1d2_n_arr1d[2:].reshape(d1, d2)
        end_tm = time.time()
        '''print(
            "full IMG request BIN time=" + str(end_tm - start_tm) + "sec"
        )'''


    except TypeError:
        print("Type err catch  (load_img_json_w_str)")
        return None

    except ZeroDivisionError:
        print("ZeroDivision err catch (load_img_json_w_str)")
        return None

    print("\n\n load_img_json_w_str   ... End")
    return np_array_out


def load_mask_img_json_w_str(
    uni_url = None, nod_num_lst = None, img_num = 0,
    exp_path = None, threshold_params = None, main_handler = None
):

    if threshold_params is None:
        my_cmd_lst = ["gmi", str(img_num)]
        my_cmd = {"nod_lst" : nod_num_lst,
                  "path"    : exp_path,
                  "cmd_str" : my_cmd_lst}

    else:
        params_str = str(threshold_params)
        my_cmd = {
            'nod_lst': nod_num_lst,
            'path': exp_path,
            'cmd_str': [
                'gtmi', str(img_num),
                'params=' + params_str
            ]
        }

    try:
        start_tm = time.time()

        req_shot = get_request_shot(
            params_in = my_cmd, main_handler = main_handler
        )

        byte_json =  req_shot.result_out()
        d1d2_n_arr1d = np.frombuffer(byte_json, dtype = float)
        d1 = int(d1d2_n_arr1d[0])
        d2 = int(d1d2_n_arr1d[1])
        np_array_out = d1d2_n_arr1d[2:].reshape(d1, d2)
        end_tm = time.time()
        logging.info(
            "full Mask IMG request BIN time " +
            str(end_tm - start_tm) + "sec"
        )

    except TypeError:
        #print("Type err catch  (load_mask_img_json_w_str)")
        return None

    except ZeroDivisionError:
        #print("ZeroDivision err catch (load_mask_img_json_w_str)")
        return None

    return np_array_out


def crunch_min_max(data2d, i_min_max):
    data2d_ini = np.copy(data2d)
    if(i_min_max == [None, None]):
        i_min_max = [data2d_ini.min(), data2d_ini.max()]
        logging.info("no max and min provided, assuming:" + str(i_min_max))

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


class np2bmp_mask(object):
    def __init__(self):
        logging.info("Dummy __init__ (np2bmp_mask)")

    def img_2d_rgb(self, data2d = None, colour_in = None, transp = None):
        try:
            self.width = np.size( data2d[0:1, :] )
            self.height = np.size( data2d[:, 0:1] )

        except TypeError:
            return None

        img_all_chanl = np.empty( (self.height, self.width), 'int')

        #img_all_chanl[:,:] = 254.0 - data2d[:,:] * 254.0
        img_all_chanl[:,:] = data2d[:,:] * 254.0

        img_array = np.zeros( (self.height, self.width, 4) , dtype=np.uint8)
        img_array[:, :, 3] = img_all_chanl[:,:] * transp   #Transp

        if colour_in == "blue":
            img_array[:, :, 0] = img_all_chanl[:,:]          #Blue

        elif colour_in == "green":
            img_array[:, :, 1] = img_all_chanl[:,:]         #Green

        else:
            img_array[:, :, 2] = img_all_chanl[:,:]         #Red

        #TODO: find why the last chanel(Blue) is used for a Red colour
        return img_array

