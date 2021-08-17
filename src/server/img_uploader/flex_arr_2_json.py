try:
    from img_uploader import img_stream_ext

except ImportError:
    import img_stream_ext

from dials.array_family import flex
import json
import time

from dxtbx.model.experiment_list import ExperimentListFactory

def list_p_arrange_exp(
    bbox_col = None, pan_col = None, hkl_col = None, n_imgs = None
):

    img_lst = []
    for time in range(n_imgs):
        img_lst.append([])

    for i, ref_box in enumerate(bbox_col):
        x_ini = ref_box[0]
        y_ini = ref_box[2] + pan_col[i] * 213
        width = ref_box[1] - ref_box[0]
        height = ref_box[3] - ref_box[2]

        if hkl_col is None or len(hkl_col) <= 1:
            local_hkl = ""

        else:
            local_hkl = hkl_col[i]
            if local_hkl == "(0, 0, 0)":
                local_hkl = "NOT indexed"

        box_dat = []
        box_dat.append(x_ini)
        box_dat.append(y_ini)
        box_dat.append(width)
        box_dat.append(height)
        box_dat.append(local_hkl)

        for idx in range(ref_box[4], ref_box[5]):
            if idx >= 0 and idx < n_imgs:
                img_lst[idx].append(box_dat)

    return img_lst




def get_refl_lst(expt_path, refl_path, img_num):
    try:
        experiments = ExperimentListFactory.from_json_file(expt_path[0])
        my_sweep = experiments.imagesets()[0]
        #data_xy_flex = my_sweep.get_raw_data(0)[0].as_double()
        print("refl_path =", refl_path)
        table = flex.reflection_table.from_file(refl_path[0])

    except IndexError:
        print(
            "\n sending empty reflection list as no reflection list there \n"
        )
        return [ [] ]

    try:
        pan_col = list(map(int, table["panel"]))
        bbox_col = list(map(list, table["bbox"]))

        n_imgs = len(my_sweep.indices())
        print("n_imgs =", n_imgs)
        box_flat_data_lst = []
        if n_imgs > 0:

            ############################################ xyzcal
            try:
                hkl_col = list(map(str, table["miller_index"]))

            except KeyError:
                print("NOT found << miller_index >> col")
                hkl_col = None

            box_flat_data_lst = list_p_arrange_exp(
                bbox_col, pan_col, hkl_col, n_imgs
            )

        return [box_flat_data_lst[img_num]]

    except KeyError:
        print("NOT found << bbox_col >> col")
        return [ [] ]

old_incomplete = '''
    try:
        pan_col = list(map(int, table["panel"]))
        bbox_col = list(map(list, table["bbox"]))

        n_imgs = len(my_sweep.indices())
        print("n_imgs =", n_imgs)
        box_flat_data_lst = []
        plus_flat_data_lst = []
        if n_imgs > 0:
            box_flat_data_lst = list_p_arrange_exp(
                bbox_col, pan_col, n_imgs
            )

            ############################################ xyzcal
            try:
                pos_col = list(map(list, table["xyzcal.px"]))
                hkl_col = list(map(str, table["miller_index"]))
                plus_flat_data_lst = list_p_arrange_pre(
                    pos_col, hkl_col, pan_col, n_imgs
                )

            except KeyError:
                print("NOT found << xyzcal >> col")
                return [box_flat_data_lst[img_num], []]


        return [box_flat_data_lst[img_num], plus_flat_data_lst[img_num]]

    except KeyError:
        print("NOT found << bbox_col >> col")
        return [ [], [] ]

def list_p_arrange_pre(pos_col, hkl_col, pan_col, n_imgs):
    img_lst = []
    for times in range(n_imgs):
        img_lst.append([])

    print(" len(pos_col) = ", len(pos_col))

    for i, pos_tri in enumerate(pos_col):

        x_ini = '{:.2f}'.format(pos_tri[0] - 1)
        y_ini = '{:.2f}'.format((pos_tri[1] - 1) + pan_col[i] * 213)

        if len(hkl_col) <= 1:
            local_hkl = ""

        else:
            local_hkl = hkl_col[i]
            if local_hkl == "(0, 0, 0)":
                local_hkl = "NOT indexed"

        xrs_size = 1
        int_z_centr = int(pos_tri[2])
        max_xrs_siz = 3
        for idx in range(int_z_centr - max_xrs_siz, int_z_centr + max_xrs_siz):
            xrs_size = max_xrs_siz - abs(int_z_centr - idx)
            if idx == int_z_centr:
                size2 = 2

            else:
                size2 = 0

            dat_to_append = [
                x_ini + "," + y_ini + "," +
                str(xrs_size) + "," + str(size2),
                local_hkl
             ]

            if idx >= 0 and idx < n_imgs:
                img_lst[idx].append(dat_to_append)

    return img_lst
    '''


def get_json_w_img_2d(experiments_list_path, img_num):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)
    my_sweep = experiments.imagesets()[0]
    print("geting image #", img_num)
    data_xy_flex = my_sweep.get_raw_data(img_num)[pan_num].as_double()
    start_tm = time.time()
    str_data = img_stream_ext.img_arr_2_str(data_xy_flex)
    end_tm = time.time()
    print("C++ bit took ", end_tm - start_tm)

    return str_data

def get_json_w_2d_slise(experiments_list_path, img_num, inv_scale, x1, y1, x2, y2):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)
    my_sweep = experiments.imagesets()[0]
    print("geting image #", img_num)
    data_xy_flex = my_sweep.get_raw_data(img_num)[pan_num].as_double()
    start_tm = time.time()
    str_data = img_stream_ext.slice_arr_2_str(
        data_xy_flex, inv_scale,
        int(float(x1)), int(float(y1)),
        int(float(x2)), int(float(y2))
    )
    end_tm = time.time()
    print("C++ bit took ", end_tm - start_tm)

    if str_data == "Error":
        print('str_data == "Error"')
        str_data = None

    return str_data



