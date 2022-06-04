import numpy as np
import time
def slice_arr_2_str( data2d, inv_scale, x1, y1, x2, y2):
    data_xy_flex = data2d.as_double()
    big_np_arr = data_xy_flex.as_numpy_array()

    big_d1 = big_np_arr.shape[0]
    big_d2 = big_np_arr.shape[1]

    if(
        x1 >= big_d1 or x2 > big_d1 or x1 < 0 or x2 <= 0 or
        y1 >= big_d2 or y2 > big_d2 or y1 < 0 or y2 <= 0 or
        x1 > x2 or y1 > y2
    ):
        print("\n ***  array bounding error  *** \n")
        return "Error"

    else:
        print("\n ***  array bounding OK  *** \n")


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

if __name__ == "__main__":
    d0, d1 = 5000, 4000
    big_arr = np.arange(d0 * d1, dtype=float).reshape(d0, d1)
    print("big_arr =\n", big_arr)
    start_tm = time.time()
    scaled_arr = scale_np_arr(big_arr, 5)
    end_tm = time.time()
    print("scaling took ", end_tm - start_tm)
    #print("scaled_arr =\n", scaled_arr)

