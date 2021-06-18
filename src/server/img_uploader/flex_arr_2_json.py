try:
    from img_uploader import img_stream_ext

except ImportError:
    import img_stream_ext

from dials.array_family import flex
import json
import time

from dxtbx.model.experiment_list import ExperimentListFactory

def list_p_arrange(pos_col, hkl_col, pan_col, n_imgs):
    img_lst = []
    for times in range(n_imgs):
        img_lst.append([])

    txt_lab = "updating Predicted Reflections Data:"
    #my_bar = ProgBarBox(min_val=0, max_val=len(pos_col), text=txt_lab)
    print(" len(pos_col) = ", len(pos_col))

    for i, pos_tri in enumerate(pos_col):
        #my_bar(i)

        x_ini = '{:.2f}'.format(pos_tri[0] - 1)
        y_ini = '{:.2f}'.format((pos_tri[1] - 1) + pan_col[i] * 213)

        #x_ini = pos_tri[0] - 1
        #y_ini = (pos_tri[1] - 1) + pan_col[i] * 213

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

    #my_bar.ended()

    return img_lst


def get_refl_lst(expt_path, refl_path, img_num):
    experiments = ExperimentListFactory.from_json_file(expt_path[0])
    my_sweep = experiments.imagesets()[0]
    data_xy_flex = my_sweep.get_raw_data(0)[0].as_double()
    print("\n refl_path =", refl_path)
    table = flex.reflection_table.from_file(refl_path[0])
    try:
        pos_col = list(map(list, table["xyzcal.px"]))
        hkl_col = list(map(str, table["miller_index"]))
        pan_col = list(map(int, table["panel"]))

        n_imgs = len(my_sweep.indices())
        pred_spt_flat_data_lst = []
        if n_imgs > 0:
            pred_spt_flat_data_lst = list_p_arrange(
                pos_col, hkl_col, pan_col, n_imgs
            )
        return pred_spt_flat_data_lst[img_num]

    except KeyError:
        print("NOT found << xyzcal >> col")
        return []


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

