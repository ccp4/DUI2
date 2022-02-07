try:
    from img_uploader import img_stream_ext

except ImportError:
    import img_stream_ext

from dials.array_family import flex
import json
import time
import pickle

#from dxtbx.model.experiment_list import ExperimentListFactory

from dxtbx.datablock import DataBlockFactory
from dxtbx.model import Experiment, ExperimentList
from dxtbx.model.experiment_list import (
    ExperimentListFactory,
    InvalidExperimentListError,
)


def list_p_arrange_exp(
    bbox_col = None, pan_col = None, hkl_col = None, n_imgs = None,
    n_imgs_lst = None, id_col = None, num_of_imagesets = 1
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

        if num_of_imagesets > 1:
            for ind_z in range(ref_box[4], ref_box[5]):
                img_id_ind_z = 0
                for id_num in range(id_col[i]):
                    img_id_ind_z += n_imgs_lst[id_num]

                img_id_ind_z += ind_z

                if img_id_ind_z >= 0 and img_id_ind_z < n_imgs:
                    img_lst[img_id_ind_z].append(box_dat)

        else:
            for ind_z in range(ref_box[4], ref_box[5]):
                if ind_z >= 0 and ind_z < n_imgs:
                    img_lst[ind_z].append(box_dat)

    return img_lst


def get_refl_lst(expt_path, refl_path, img_num):
    try:
        experiments = ExperimentListFactory.from_json_file(expt_path[0])
        #my_sweep = experiments.imagesets()[0]
        all_sweeps = experiments.imagesets()
        num_of_imagesets = len(experiments.imagesets())
        print("len(experiments.imagesets()) =", num_of_imagesets)
        print("refl_path =", refl_path)
        table = flex.reflection_table.from_file(refl_path[0])

    except (IndexError, OSError):
        print(
            "\n sending empty reflection list as no reflection list there \n"
        )
        return [ [] ]

    try:
        pan_col = list(map(int, table["panel"]))
        bbox_col = list(map(list, table["bbox"]))
        id_col = list(map(int, table["id"]))

        #n_imgs = len(my_sweep.indices())
        n_imgs_lst = []
        n_imgs = 0
        for single_sweep in all_sweeps:
            len_sweep = len(single_sweep.indices())
            n_imgs += len_sweep
            n_imgs_lst.append(len_sweep)

        print("n_imgs =", n_imgs)
        print("n_imgs_lst =", n_imgs_lst)

        box_flat_data_lst = []
        if n_imgs > 0:
            try:
                hkl_col = list(map(str, table["miller_index"]))

            except KeyError:
                print("NOT found << miller_index >> col")
                hkl_col = None

            box_flat_data_lst = list_p_arrange_exp(
                bbox_col, pan_col, hkl_col, n_imgs, n_imgs_lst, id_col, num_of_imagesets
            )

        try:
            refl_lst = [box_flat_data_lst[img_num]]

        except IndexError:
            refl_lst = []

        return refl_lst

    except KeyError:
        print("NOT found << bbox_col >> col")
        return [ [] ]


def get_json_w_img_2d(experiments_list_path, img_num):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)
    '''
    my_sweep = experiments.imagesets()[0]
    print("geting image #", img_num)
    data_xy_flex = my_sweep.get_raw_data(img_num)[pan_num].as_double()
    '''
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


    ######################################################### START copy

def get_json_w_mask_img_2d(experiments_list_path, img_num):
    print("experiments_list_path, img_num:", experiments_list_path, img_num)
    pan_num = 0
    experiments_path = experiments_list_path[0]
    print("importing from:", experiments_path)
    experiments = ExperimentListFactory.from_json_file(experiments_path)

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
    '''
    my_sweep = experiments.imagesets()[0]
    print("geting image #", img_num)
    data_xy_flex = my_sweep.get_raw_data(img_num)[pan_num].as_double()
    '''

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




