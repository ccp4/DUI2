import numpy as np
import time, logging

def get_np_full_img(raw_dat):
    if len(raw_dat) == 24:
        logging.info("24 panels, assuming i23 data")
        pan_tup = tuple(range(24))
        top_pan = raw_dat[pan_tup[0]].as_numpy_array()

        p_siz0 = np.size(top_pan[:, 0:1])
        p_siz1 = np.size(top_pan[0:1, :])

        p_siz_bg = p_siz0 + 18
        im_siz0 = p_siz_bg * len(pan_tup)
        im_siz1 = p_siz1

        np_arr = np.zeros((im_siz0, im_siz1), dtype=np.double)
        np_arr[:, :] = -1
        np_arr[0:p_siz0, 0:p_siz1] = top_pan[:, :]

        for s_num in pan_tup[1:]:
            pan_dat = raw_dat[pan_tup[s_num]].as_numpy_array()
            np_arr[
                s_num * p_siz_bg : s_num * p_siz_bg + p_siz0, 0:p_siz1
            ] = pan_dat[:, :]

    else:
        logging.info("Using the first panel only")
        data_xy_flex = raw_dat[0].as_double()
        np_arr = data_xy_flex.as_numpy_array()

    return np_arr



def slice_arr_2_str( data2d, inv_scale, x1, y1, x2, y2):
    big_np_arr = get_np_full_img(data2d)

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

    d1 = np_arr.shape[0]
    d2 = np_arr.shape[1]

    rvl_arr = np_arr.ravel()
    str_tup = str(tuple(rvl_arr))

    clean_str = str_tup.replace(" ", "")
    str_data = "{\"str_data\":\"" + clean_str[1:-1]+ \
                "\",\"d1\":" + str(d1) + ",\"d2\":" + str(d2) + "}"

    return str_data


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
    small_arr = np.zeros((small_d0, small_d1))
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


def mask_arr_2_str(data2d_flex):
    return mask_np_2_str(data2d_flex.as_numpy_array())


def mask_np_2_str(bool_np_arr):
    d1 = bool_np_arr.shape[0]
    d2 = bool_np_arr.shape[1]

    str_tup = str(bool_np_arr.ravel().tobytes())
    replace_x = str_tup.replace("\\x0", "")
    str_stream = replace_x[2:-1]

    str_data = "{\"str_data\":\"" + str_stream + \
                "\",\"d1\":" + str(d1) + ",\"d2\":" + str(d2) + "}"

    return str_data


def slice_mask_2_str(data2d, inv_scale, x1, y1, x2, y2):

    bool_np_arr = data2d.as_numpy_array()
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

        str_buff = mask_np_2_str(small_arr)

        return str_buff

