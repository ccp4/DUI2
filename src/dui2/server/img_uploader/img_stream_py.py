import numpy as np
import time, logging
from dials.array_family import flex
from dxtbx.flumpy import to_numpy, from_numpy
from dials.algorithms.image.threshold import (
    DispersionThresholdDebug, DispersionExtendedThresholdDebug
)

def get_np_full_img(raw_dat):
    i23_multipanel = False
    if len(raw_dat) == 24:
        i23_multipanel = True
        logging.info("24 panels, assuming i23 data(main image)")
        pan_tup = tuple(range(24))
        top_pan = to_numpy(raw_dat[pan_tup[0]])

        p_siz0 = np.size(top_pan[:, 0:1])
        p_siz1 = np.size(top_pan[0:1, :])

        p_siz_bg = p_siz0 + 18

        im_siz0 = p_siz_bg * len(pan_tup)
        im_siz1 = p_siz1

        np_arr = np.zeros((im_siz0, im_siz1), dtype=np.double)
        np_arr[:, :] = -1
        np_arr[0:p_siz0, 0:p_siz1] = top_pan[:, :]

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
        logging.info("\n ***  array bounding error  *** \n")
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


def get_np_full_mask(raw_dat):
    i23_multipanel = False
    if len(raw_dat) == 24:
        i23_multipanel = True
        logging.info("24 panels, assuming i23 data(masking)")

        pan_tup = tuple(range(24))
        top_pan = to_numpy(raw_dat[pan_tup[0]])
        p_siz0 = np.size(top_pan[:, 0:1])
        p_siz1 = np.size(top_pan[0:1, :])
        p_siz_bg = p_siz0 + 18

        im_siz0 = p_siz_bg * len(pan_tup)
        im_siz1 = p_siz1

        np_arr = np.zeros((im_siz0, im_siz1), dtype=bool)
        np_arr[:, :] = 1
        np_arr[0:p_siz0, 0:p_siz1] = top_pan[:, :]

        for s_num in pan_tup[1:]:
            pan_dat = to_numpy(raw_dat[pan_tup[s_num]])
            np_arr[
                s_num * p_siz_bg : s_num * p_siz_bg + p_siz0, 0:p_siz1
            ] = pan_dat[:, :]

    else:
        logging.info("Using the first panel only")
        data_xy_flex = raw_dat[0]
        np_arr = to_numpy(data_xy_flex)

    return np_arr, i23_multipanel



def get_str_full_mask(raw_dat):
    np_arr_mask, i23_multipanel = get_np_full_mask(raw_dat)
    str_arr_mask = np_arr_2_byte_stream(np_arr_mask)
    return str_arr_mask, i23_multipanel


def slice_mask_2_byte(raw_dat, inv_scale, x1, y1, x2, y2):

    bool_np_arr, i23_multipanel = get_np_full_mask(raw_dat)
    big_d0 = bool_np_arr.shape[0]
    big_d1 = bool_np_arr.shape[1]

    if(
        x1 >= big_d0 or x2 > big_d0 or x1 < 0 or x2 <= 0 or
        y1 >= big_d1 or y2 > big_d1 or y1 < 0 or y2 <= 0 or
        x1 > x2 or y1 > y2
    ):
        logging.info("\n ***  array bounding error  *** \n")
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


def from_image_n_mask_2_threshold(np_img, np_mask, params):
    nsig_b           = params["nsig_b"]
    nsig_s           = params["nsig_s"]
    global_threshold = params["global_threshold"]
    min_count        = params["min_count"]
    gain             = params["gain"]
    size             = params["size"]

    #np_mask = to_numpy(mask)
    #np_img = to_numpy(image)
    abs_img = convert_2_black_n_white(np_img)

    sum_np_mask = np_mask + abs_img - 1.5
    added_np_mask = convert_2_black_n_white(sum_np_mask)
    bool_np_mask = added_np_mask.astype(bool)
    mask_w_panels = from_numpy(bool_np_mask)
    gain_map = flex.double(flex.grid(np_img.shape), gain)
    my_algorithm = "dispersion_extended"

    if my_algorithm == "dispersion_extended":
        algorithm = DispersionExtendedThresholdDebug
    elif my_algorithm == "dispersion":
        algorithm = DispersionThresholdDebug

    image = from_numpy(np_img)
    to_view_later = '''
    else:
        algorithm = RadialProfileThresholdDebug(
            image, self.settings.n_iqr, self.settings.blur, self.settings.n_bins
        )

    radial_profile {
      n_iqr = 6
      blur = narrow wide
      n_bins = 100
    '''
    flex_debug_img = algorithm(
        image.as_double(),
        mask_w_panels,
        gain_map, size, nsig_b, nsig_s, global_threshold, min_count,
    )

    return flex_debug_img

def slice_mask_threshold_2_byte(
    image_raw_dat, mask_raw_dat, inv_scale, x1, y1, x2, y2, params
):
    print("<< HERE >>   #2 \n")
    bool_np_arr, i23_multipanel = get_np_full_mask(mask_raw_dat)
    np_full_img, i23_multipanel = get_np_full_img(image_raw_dat)
    debug_mask_obj = from_image_n_mask_2_threshold(np_full_img, bool_np_arr, params)
    flex_debug_mask = debug_mask_obj.final_mask()
    np_debug_mask = to_numpy(flex_debug_mask)
    print("type(np_debug_mask) =", type(np_debug_mask))
    print("<<< HERE #3 >>>\n")

    big_d0 = np_debug_mask.shape[0]
    big_d1 = np_debug_mask.shape[1]

    if(
        x1 >= big_d0 or x2 > big_d0 or x1 < 0 or x2 <= 0 or
        y1 >= big_d1 or y2 > big_d1 or y1 < 0 or y2 <= 0 or
        x1 > x2 or y1 > y2
    ):
        logging.info("\n ***  array bounding error  *** \n")
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

        byte_buff = np_arr_2_byte_stream(small_arr)

        return byte_buff, i23_multipanel
