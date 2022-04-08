try:
    from img_uploader import img_stream_ext

except ImportError:
    import img_stream_ext

from dials.array_family import flex
import json
import time
import pickle

from dxtbx.datablock import DataBlockFactory
from dxtbx.model import Experiment, ExperimentList
from dxtbx.model.experiment_list import (
    ExperimentListFactory,
    InvalidExperimentListError,
)

def get_template_info(exp_path, img_num):
    experiments = ExperimentListFactory.from_json_file(
        exp_path
    )

    on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
        experiments, img_num
    )
    my_sweep = experiments.imagesets()[n_sweep]

    str_json = my_sweep.get_template()
    print("getting template for image num:", img_num)
    img_path = my_sweep.get_path(on_sweep_img_num)
    print("\n get_path =", img_path, "\n")

    data_xy_flex = my_sweep.get_raw_data(0)[0].as_double()
    img_with, img_height = data_xy_flex.all()[0:2]
    return [str_json, img_with, img_height, img_path]

def list_p_arrange_exp(
    bbox_col = None, pan_col = None, hkl_col = None, n_imgs = None,
    num_of_imgs_n_shift_lst = None, id_col = None, num_of_imagesets = 1
):
    print("n_imgs(list_p_arrange_exp) =", n_imgs)
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

        id_num = 0
        if num_of_imagesets > 1:
            for ind_z in range(ref_box[4], ref_box[5]):
                img_id_ind_z = 0
                for id_num in range(id_col[i]):
                    img_id_ind_z += num_of_imgs_n_shift_lst[id_num][0]

                ind_z_shift = ind_z - num_of_imgs_n_shift_lst[id_num][1]
                img_id_ind_z += ind_z_shift

                if img_id_ind_z >= 0 and img_id_ind_z < n_imgs:
                    img_lst[img_id_ind_z].append(box_dat)

        else:
            for ind_z in range(ref_box[4], ref_box[5]):
                ind_z_shift = ind_z - num_of_imgs_n_shift_lst[id_num][1]
                if ind_z_shift >= 0 and ind_z_shift < n_imgs:
                    img_lst[ind_z_shift].append(box_dat)

    return img_lst


def get_refl_lst(expt_path, refl_path, img_num):
    try:
        experiments = ExperimentListFactory.from_json_file(expt_path[0])
        all_sweeps = experiments.imagesets()
        num_of_imagesets = len(all_sweeps)
        print("len(experiments.imagesets()) =", num_of_imagesets)
        print("refl_path =", refl_path)
        table = flex.reflection_table.from_file(refl_path[0])

    except IndexError:
        print("\n sending empty reflection (IndexError) \n")
        return [ [] ]

    except OSError:
        print("\n sending empty reflection (OSError) \n")
        return [ [] ]

    try:
        pan_col = list(map(int, table["panel"]))
        bbox_col = list(map(list, table["bbox"]))
        id_col = list(map(int, table["id"]))

        num_of_imgs_n_shift_lst = []
        n_imgs = 0
        for single_sweep in all_sweeps:
            num_of_imgs = len(single_sweep.indices())
            n_imgs += num_of_imgs
            shift = single_sweep.get_scan().get_image_range()[0] - 1
            num_of_imgs_n_shift_lst.append((num_of_imgs, shift))

        print("n_imgs =", n_imgs)
        print("num_of_imgs_n_shift_lst =", num_of_imgs_n_shift_lst)

        box_flat_data_lst = []
        if n_imgs > 0:
            try:
                hkl_col = list(map(str, table["miller_index"]))

            except KeyError:
                print("NOT found << miller_index >> col")
                hkl_col = None

            box_flat_data_lst = list_p_arrange_exp(
                bbox_col, pan_col, hkl_col, n_imgs,
                num_of_imgs_n_shift_lst, id_col, num_of_imagesets
            )

        try:
            refl_lst = [box_flat_data_lst[img_num]]
            print("len(refl_lst) =", len(refl_lst))

        except IndexError:
            refl_lst = []
            print("refl_lst = []")

        return refl_lst

    except KeyError:
        print("NOT found << bbox_col >> col")
        return [ [] ]


def get_correct_img_num_n_sweep_num(experiments, img_num):
    lst_num_of_imgs = []
    for single_sweep in experiments.imagesets():
        lst_num_of_imgs.append(len(single_sweep.indices()))

    print("lst_num_of_imgs =", lst_num_of_imgs)
    on_sweep_img_num = img_num
    n_sweep = 0
    for num_of_imgs in lst_num_of_imgs:
        if on_sweep_img_num >= num_of_imgs:
            on_sweep_img_num -= num_of_imgs
            n_sweep += 1

        else:
            break

    print("geting image #", on_sweep_img_num, "from sweep #", n_sweep)
    return on_sweep_img_num, n_sweep

def get_json_w_img_2d(experiments_list_path, img_num):
    pan_num = 0
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)

    on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
        experiments, img_num
    )

    my_sweep = experiments.imagesets()[n_sweep]
    data_xy_flex = my_sweep.get_raw_data(on_sweep_img_num)[pan_num].as_double()

    start_tm = time.time()
    np_arr = data_xy_flex.as_numpy_array()
    d1 = np_arr.shape[0]
    d2 = np_arr.shape[1]
    str_tup = str(tuple(np_arr.ravel()))
    str_data = "{\"d1\":" + str(d1) + ",\"d2\":" + str(d2) \
             + ",\"str_data\":\"" + str_tup[1:-1] + "\"}"

    end_tm = time.time()
    print("str/tuple use and compressing took ", end_tm - start_tm)

    return str_data

def get_json_w_mask_img_2d(experiments_list_path, img_num):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)

    on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
        experiments, img_num
    )

    try:
        imageset_tmp = experiments.imagesets()[n_sweep]
        mask_file = imageset_tmp.external_lookup.mask.filename
        pick_file = open(mask_file, "rb")
        mask_tup_obj = pickle.load(pick_file)
        pick_file.close()
        mask_flex = mask_tup_obj[0]
        str_data = img_stream_ext.mask_arr_2_str(mask_flex)

    except FileNotFoundError:
        str_data = None

    return str_data

def get_json_w_2d_slise(experiments_list_path, img_num, inv_scale, x1, y1, x2, y2):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)

    on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
        experiments, img_num
    )

    my_sweep = experiments.imagesets()[n_sweep]
    data_xy_flex = my_sweep.get_raw_data(on_sweep_img_num)[pan_num].as_double()

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

####################################################################################

def get_json_w_2d_mask_slise(experiments_list_path, img_num, inv_scale, x1, y1, x2, y2):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)

    on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
        experiments, img_num
    )

    imageset_tmp = experiments.imagesets()[n_sweep]
    mask_file = imageset_tmp.external_lookup.mask.filename
    try:
        pick_file = open(mask_file, "rb")
        mask_tup_obj = pickle.load(pick_file)
        pick_file.close()

        mask_flex = mask_tup_obj[0]

        start_tm = time.time()
        str_data = img_stream_ext.slice_mask_2_str(
            mask_flex, inv_scale,
            int(float(x1)), int(float(y1)),
            int(float(x2)), int(float(y2))
        )
        end_tm = time.time()
        print("C++ bit took ", end_tm - start_tm)

        if str_data == "Error":
            print('str_data == "Error"')
            str_data = None

    except FileNotFoundError:
        str_data = None

    return str_data




