import numpy as np
import time, logging
import types, pickle
from dials.array_family import flex
from dials.command_line.find_spots import phil_scope as find_spots_phil_scope
from dials.extensions import SpotFinderThreshold
from dxtbx.flumpy import to_numpy, from_numpy
from dials.algorithms.image.threshold import (
    DispersionThresholdDebug, DispersionExtendedThresholdDebug
)

from dxtbx.model import ExperimentList

def get_np_full_img(raw_dat):
    i23_multipanel = False
    if len(raw_dat) == 24:
        i23_multipanel = True
        logging.info("24 panels, assuming i23 data(main image)")
        pan_tup = tuple(range(24))
        np_top_pan = to_numpy(raw_dat[pan_tup[0]])

        p_siz0 = np.size(np_top_pan[:, 0:1])
        p_siz1 = np.size(np_top_pan[0:1, :])

        p_siz_bg = p_siz0 + 18

        im_siz0 = p_siz_bg * len(pan_tup)
        im_siz1 = p_siz1

        np_arr = np.zeros((im_siz0, im_siz1), dtype=np.double)
        np_arr[:, :] = -1
        np_arr[0:p_siz0, 0:p_siz1] = np_top_pan[:, :]

        for s_num in pan_tup[1:]:
            pan_dat = to_numpy(raw_dat[pan_tup[s_num]])
            np_arr[
                s_num * p_siz_bg : s_num * p_siz_bg + p_siz0, 0:p_siz1
            ] = pan_dat[:, :]

    else:
        logging.info("Using the first panel only")
        data_xy_flex = raw_dat[0].as_double()
        np_arr = to_numpy(data_xy_flex)

    logging.info("type(np_arr[0,0]) = " + str(type(np_arr[0,0])))

    return np_arr, i23_multipanel


def np_arr_2_byte_stream(np_arr_in):
    d1 = np_arr_in.shape[0]
    d2 = np_arr_in.shape[1]

    logging.info("type(np_arr_in[0,0]) = " + str(type(np_arr_in[0,0])))

    img_arr = np.zeros(d1 * d2 + 2, dtype = float)
    img_arr[0] = float(d1)
    img_arr[1] = float(d2)
    img_arr[2:] = np_arr_in.ravel()
    byte_info = img_arr.tobytes(order='C')
    return byte_info


def slice_arr_2_byte(data2d, inv_scale, x1, y1, x2, y2):
    big_np_arr, i23_multipanel = get_np_full_img(data2d)

    big_d1 = big_np_arr.shape[0]
    big_d2 = big_np_arr.shape[1]

    if(
        x1 >= big_d1 or x2 > big_d1 or x1 < 0 or x2 <= 0 or
        y1 >= big_d2 or y2 > big_d2 or y1 < 0 or y2 <= 0 or
        x1 > x2 or y1 > y2
    ):
        logging.info("***  array bounding error  ***")
        return "Error"

    else:
        logging.info(" array bounding OK ")

    np_arr = scale_np_arr(big_np_arr[x1:x2,y1:y2], inv_scale)
    byte_info = np_arr_2_byte_stream(np_arr)
    return byte_info


def scale_np_arr(big_np_arr, inv_scale):
    a_d0 = big_np_arr.shape[0]
    a_d1 = big_np_arr.shape[1]
    small_d0 = int(0.995 + a_d0 / inv_scale)
    short_arr = np.zeros((small_d0, a_d1))
    for row_num in range(small_d0):
        row_cou = 0
        for sub_row_num in range(inv_scale):
            big_row = row_num * inv_scale + sub_row_num
            if big_row < a_d0:
                short_arr[row_num,:] += big_np_arr[big_row, :]
                row_cou += 1

        short_arr[row_num,:] /= float(row_cou)

    small_d1 = int(0.995 + a_d1 / inv_scale)
    small_arr = np.zeros((small_d0, small_d1), dtype = float)
    for col_num in range(small_d1):
        col_cou = 0
        for sub_col_num in range(inv_scale):
            big_col = col_num * inv_scale + sub_col_num
            if big_col < a_d1:
                small_arr[:,col_num] += short_arr[:,big_col]
                col_cou += 1

        small_arr[:,col_num] /= float(col_cou)

    rd_arr = np.round(small_arr, 1)
    return rd_arr


def get_np_full_mask_from_i23_raw(
    raw_mask_data_in = None, border_to_one = False
):
    pan_tup = tuple(range(24))
    np_top_pan = to_numpy(raw_mask_data_in[pan_tup[0]])
    p_siz0 = np.size(np_top_pan[:, 0:1])
    p_siz1 = np.size(np_top_pan[0:1, :])
    p_siz_bg = p_siz0 + 18

    im_siz0 = p_siz_bg * len(pan_tup)
    im_siz1 = p_siz1

    np_arr = np.zeros((im_siz0, im_siz1), dtype=bool)
    if border_to_one:
        np_arr[:, :] = 1

    np_arr[0:p_siz0, 0:p_siz1] = np_top_pan[:, :]

    for s_num in pan_tup[1:]:
        pan_dat = to_numpy(raw_mask_data_in[pan_tup[s_num]])
        np_arr[
            s_num * p_siz_bg : s_num * p_siz_bg + p_siz0, 0:p_siz1
        ] = pan_dat[:, :]

    return np_arr


def get_np_full_mask_from_image(raw_image_data):
    i23_multipanel = False
    first_flex_panel = raw_image_data[0]
    top_data_xy_flex = flex.bool(flex.grid(first_flex_panel.all()),True)
    if len(raw_image_data) == 24:
        logging.info("24 panels, assuming i23 data(masking 2)")
        i23_multipanel = True
        pan_tup_size = 24
        np_top_pan = to_numpy(top_data_xy_flex)

        p_siz0 = np.size(np_top_pan[:, 0:1])
        p_siz1 = np.size(np_top_pan[0:1, :])
        p_siz_bg = p_siz0 + 18
        im_siz0 = p_siz_bg * pan_tup_size
        im_siz1 = p_siz1

        np_arr = np.zeros((im_siz0, im_siz1), dtype=np.double)
        np_arr[:, :] = -1
        np_arr[0:p_siz0, 0:p_siz1] = np_top_pan[:, :]
        for s_num in range(1,pan_tup_size):
            pan_dat = np.copy(np_top_pan)
            np_arr[
                s_num * p_siz_bg : s_num * p_siz_bg + p_siz0, 0:p_siz1
            ] = pan_dat[:, :]

    else:
        logging.info("Using the first panel only (masking 2)")
        np_arr = to_numpy(top_data_xy_flex)

    return np_arr, i23_multipanel


def get_np_full_mask(raw_mask_data, raw_image_data):
    i23_multipanel = False
    try:
        if len(raw_mask_data) == 24:
            logging.info("24 panels, assuming i23 data(masking 1)")
            i23_multipanel = True
            np_arr = get_np_full_mask_from_i23_raw(
                raw_mask_data_in = raw_mask_data, border_to_one = True
            )

        else:
            logging.info("Using the first panel only (masking 1)")
            data_xy_flex = raw_mask_data[0]
            np_arr = to_numpy(data_xy_flex)

    except TypeError:
        logging.info("Type Err catch (get_np_full_mask)")
        np_arr, i23_multipanel = get_np_full_mask_from_image(raw_image_data)

    return np_arr, i23_multipanel


def get_str_full_mask(raw_dat):
    np_arr_mask, i23_multipanel = get_np_full_mask(raw_dat, None)
    logging.info(
        "type(np_arr_mask) =" + str(type(np_arr_mask))
        + str("... get_str_full_mask")
    )
    np_arr_mask = 1 - np_arr_mask
    str_arr_mask = np_arr_2_byte_stream(np_arr_mask)
    return str_arr_mask, i23_multipanel


def slice_mask_2_byte(raw_dat, inv_scale, x1, y1, x2, y2):
    bool_np_arr, i23_multipanel = get_np_full_mask(raw_dat, None)
    bool_np_arr = 1 - bool_np_arr
    logging.info(
        "type(bool_np_arr) =" + str(type(bool_np_arr))
        + "... slice_mask_2_byte"
    )
    big_d0 = bool_np_arr.shape[0]
    big_d1 = bool_np_arr.shape[1]

    if(
        x1 >= big_d0 or x2 > big_d0 or x1 < 0 or x2 <= 0 or
        y1 >= big_d1 or y2 > big_d1 or y1 < 0 or y2 <= 0 or
        x1 > x2 or y1 > y2
    ):
        logging.info("***  array bounding error  ***")
        return "Error"

    else:
        logging.info(" array bounding OK ")
        slice_np_arr = bool_np_arr[x1:x2,y1:y2]
        a_d0 = slice_np_arr.shape[0]
        a_d1 = slice_np_arr.shape[1]

        small_d0 = int(0.995 + a_d0 / inv_scale)
        short_arr = np.zeros((small_d0, a_d1), dtype = bool)
        for row_num in range(small_d0):
            for sub_row_num in range(inv_scale):
                big_row = row_num * inv_scale + sub_row_num
                if big_row < a_d0:
                    short_arr[row_num,:] = np.bitwise_or(
                        short_arr[row_num,:], slice_np_arr[big_row, :]
                    )

        small_d1 = int(0.995 + a_d1 / inv_scale)
        small_arr = np.zeros((small_d0, small_d1), dtype = bool)

        for col_num in range(small_d1):
            for sub_col_num in range(inv_scale):
                big_col = col_num * inv_scale + sub_col_num
                if big_col < a_d1:
                    small_arr[:,col_num] = np.bitwise_or(
                        small_arr[:,col_num], short_arr[:,big_col]
                    )

        byte_buff = np_arr_2_byte_stream(small_arr)

        return byte_buff, i23_multipanel


def convert_2_black_n_white(np_img):
    sig_img = (np_img + 0.00000001) / np.abs(np_img + 0.00000001)
    abs_img = (sig_img + 1) / 2
    return abs_img


def mask_threshold_2_slise(
    flex_debug_mask, inv_scale, x1, y1, x2, y2
):
    np_debug_mask = to_numpy(flex_debug_mask)
    big_d0 = np_debug_mask.shape[0]
    big_d1 = np_debug_mask.shape[1]
    if(
        x1 >= big_d0 or x2 > big_d0 or x1 < 0 or x2 <= 0 or
        y1 >= big_d1 or y2 > big_d1 or y1 < 0 or y2 <= 0 or
        x1 > x2 or y1 > y2
    ):
        logging.info("***  array bounding error  ***")
        return "Error"

    else:
        logging.info(" array bounding OK ")
        slice_np_arr = np_debug_mask[x1:x2,y1:y2]
        a_d0 = slice_np_arr.shape[0]
        a_d1 = slice_np_arr.shape[1]

        small_d0 = int(0.995 + a_d0 / inv_scale)
        short_arr = np.zeros((small_d0, a_d1), dtype = bool)
        for row_num in range(small_d0):
            for sub_row_num in range(inv_scale):
                big_row = row_num * inv_scale + sub_row_num
                if big_row < a_d0:
                    short_arr[row_num,:] = np.bitwise_or(
                        short_arr[row_num,:], slice_np_arr[big_row, :]
                    )

        small_d1 = int(0.995 + a_d1 / inv_scale)
        small_arr = np.zeros((small_d0, small_d1), dtype = bool)

        for col_num in range(small_d1):
            for sub_col_num in range(inv_scale):
                big_col = col_num * inv_scale + sub_col_num
                if big_col < a_d1:
                    small_arr[:,col_num] = np.bitwise_or(
                        small_arr[:,col_num], short_arr[:,big_col]
                    )

        return small_arr


class RadialProfileThresholdDebug:
    # The radial_profile threshold algorithm does not have an associated
    # 'Debug' class. It does not create the same set of intermediate images
    # as the dispersion algorithms, so we can delegate to a
    # DispersionThresholdDebug object for those, while overriding the final_mask
    # method. This wrapper class handles that.

    # This class was Copy/Pasted and edited from the module spotfinder_frame.py
    # that is part of the Dials image viewer

    def __init__(self, imageset, n_iqr, blur, n_bins):
        self.imageset = imageset
        params = find_spots_phil_scope.extract()
        params.spotfinder.threshold.radial_profile.blur = blur
        params.spotfinder.threshold.radial_profile.n_bins = n_bins
        params.spotfinder.threshold.radial_profile.n_iqr = n_iqr
        self.radial_profile = SpotFinderThreshold.load("radial_profile")(params)
        self.i_panel = 0

    def __call__(self, *args):
        dispersion = DispersionThresholdDebug(*args)
        image = args[0]
        mask = args[1]
        dispersion._final_mask = self.radial_profile.compute_threshold(
            image, mask, imageset=self.imageset, i_panel=self.i_panel
        )
        dispersion.final_mask = types.MethodType(lambda x: x._final_mask, dispersion)
        return dispersion


def from_image_n_mask_2_threshold(
    my_algorithm, flex_image, mask, imageset_tmp, pars, panel_number
):
    np_mask = to_numpy(mask)
    np_img = to_numpy(flex_image)
    abs_img = convert_2_black_n_white(np_img)

    (
        nsig_b, nsig_s, global_threshold, min_count, gain, size,
        n_iqr, blur, n_bins
    ) = pars

    sum_np_mask = np_mask + abs_img - 1.5
    added_np_mask = convert_2_black_n_white(sum_np_mask)

    bool_np_mask = added_np_mask.astype(bool)
    mask_w_panels = from_numpy(bool_np_mask)
    gain_map = flex.double(flex.grid(flex_image.all()), gain)
    if my_algorithm == "dispersion_extended":
        algorithm = DispersionExtendedThresholdDebug

    elif my_algorithm == "dispersion":
        algorithm = DispersionThresholdDebug

    else:
        algorithm = RadialProfileThresholdDebug(
            imageset_tmp, n_iqr, blur, n_bins
        )
    algorithm.i_panel = panel_number
    debug = algorithm(
        flex_image.as_double(),
        mask_w_panels,
        gain_map, size, nsig_b, nsig_s, global_threshold, min_count,
    )
    return debug


def get_dispersion_debug_obj_tup(
    expt_path = "/tmp/...", on_sweep_img_num = 0, params_in = {None}
):
    try:
        nsig_b =            params_in["nsig_b"]
        nsig_s =            params_in["nsig_s"]
        global_threshold =  params_in["global_threshold"]
        min_count =         params_in["min_count"]
        gain =              params_in["gain"]
        size =              params_in["size"]

    except KeyError:
        nsig_b =            6.0
        nsig_s =            3.0
        global_threshold =  0.0
        min_count =         2
        gain =              1.0
        size =              (3,3)

    try:
        n_iqr =     params_in["n_iqr"]
        blur =      params_in["blur"]
        n_bins =    params_in["n_bins"]

    except KeyError:
        n_iqr =     6
        blur =      None
        n_bins =    100

    experiments = ExperimentList.from_file(expt_path)
    my_imageset = experiments.imagesets()[0]

    detector = my_imageset.get_detector()

    obj_w_alg_lst = []
    for panel_number in range(len(detector)):
        flex_image = my_imageset.get_raw_data(on_sweep_img_num)[panel_number]
        try:
            mask_file = my_imageset.external_lookup.mask.filename
            pick_file = open(mask_file, "rb")
            mask_tup_obj = pickle.load(pick_file)
            pick_file.close()
            mask = mask_tup_obj[panel_number]

        except FileNotFoundError:
            mask = flex.bool(flex.grid(flex_image.all()),True)

        pars = (
            nsig_b, nsig_s, global_threshold, min_count, gain, size,
            n_iqr, blur, n_bins
        )

        obj_w_alg = from_image_n_mask_2_threshold(
            params_in["algorithm"],
            flex_image, mask, my_imageset, pars, panel_number
        )
        fin_mask = obj_w_alg.final_mask()
        obj_w_alg_lst.append(fin_mask)

    obj_w_alg_tup = tuple(obj_w_alg_lst)
    return obj_w_alg_tup



