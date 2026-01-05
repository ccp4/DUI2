try:
    from dui2.server.img_uploader import img_stream_py

except ImportError:
    import img_stream_py

from dials.array_family import flex
#from dxtbx.model.experiment_list import ExperimentList
from dxtbx.model import ExperimentList

import json, logging
import time
import pickle
import numpy as np

from dxtbx.flumpy import to_numpy, from_numpy
from dials.command_line.find_spots import phil_scope as find_spots_phil_scope
from dials.extensions import SpotFinderThreshold
from dials.algorithms.image.threshold import (
    DispersionThresholdDebug, DispersionExtendedThresholdDebug
)
import types

def get_experiments(experiment_path):
    logging.info("importing from:" + experiment_path)
    for repeat in range(10):
        try:
            new_experiments = ExperimentList.from_file(
                experiment_path
            )
            break

        except OSError:
            new_experiments = None
            logging.info("OS Err catch in ExperimentListFactory, trying again")
            time.sleep(0.333)

    return new_experiments


def get_height_with_n_i23_multip(ExpLst):
    img_with, img_height = ExpLst[0].detector[0].get_image_size()
    if len(ExpLst[0].detector) == 24:
        i23_multipanel = True
        img_height = (img_height + 18) * 24

    else:
        i23_multipanel = False

    return img_with, img_height, i23_multipanel


def get_template_info(exp_path, img_num):
    try:
        experiments = get_experiments(exp_path)

        max_img_num = 0
        for single_sweep in experiments.imagesets():
            max_img_num += len(single_sweep.indices())

        max_img_num -= 1
        if img_num < 0:
            new_img_num = 0

        elif img_num > max_img_num:
            new_img_num = max_img_num

        else:
            new_img_num = img_num

        on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
            experiments, new_img_num
        )
        my_sweep = experiments.imagesets()[n_sweep]
        str_json = my_sweep.get_template()
        img_path = my_sweep.get_path(on_sweep_img_num)
        img_height, img_with, i23_multipanel = get_height_with_n_i23_multip(
            experiments
        )
        exp = experiments[0]

        # Get direct beam from detector data
        pnl_beam_intersects, (beam_x_mm, beam_y_mm) = \
            exp.detector.get_ray_intersection(exp.beam.get_s0())
        pnl = exp.detector[pnl_beam_intersects]
        x_px_size, y_px_size = pnl.get_pixel_size()
        x_beam_pix = beam_x_mm / x_px_size
        y_beam_pix = beam_y_mm / y_px_size
        det_mov =  float(pnl_beam_intersects) * 213.0
        y_beam_pix += det_mov

        dict_data = {
            "str_json"       :str_json       ,
            "img_with"       :img_with       ,
            "img_height"     :img_height     ,
            "img_path"       :img_path       ,
            "new_img_num"    :new_img_num    ,
            "i23_multipanel" :i23_multipanel ,
            "x_beam_pix"     :x_beam_pix     ,
            "y_beam_pix"     :y_beam_pix
        }

        return [dict_data]

    except IndexError:
        logging.info(" *** Index err catch  in template ***")
        return

    except OverflowError:
        logging.info(" *** Overflow err catch  in template ***")
        return

    except OSError:
        logging.info(" *** OS Err catch  in template ***")
        return

    except AttributeError:
        logging.info(" *** Attribute Err catch  in template ***")
        return



def get_resolution( experiments, x, y, panel_num=None):
    """
    Determine the resolution of a pixel.
    Arguments are in image pixel coordinates (starting from 1,1).

    as a starting point this was copy/pasted from Dials Image Viewer
    """
    beam = experiments.beams()[0]

    my_imageset = experiments.imagesets()[0]
    detector = my_imageset.get_detector()

    if detector is None or beam is None:
        return None

    if panel_num is None:
        return None

    panel = detector[panel_num]

    if abs(panel.get_distance()) > 0:
        return panel.get_resolution_at_pixel(beam, (x, y))
        #return panel.get_resolution_at_pixel(beam, flex.double(x), flex.double(y))

        #example copy/pasted from C++ header in dials algorithm
        #double d = panel.get_resolution_at_pixel(s0, vec2<double>(i, j));

    else:
        return None


def list_p_arrange_exp(
    bbox_col = None, pan_col = None, hkl_col = None, n_imgs = None,
    num_of_imgs_lst = None, imgs_shift_lst = None, id_col = None,
    num_of_imagesets = 1
):
    logging.info("n_imgs(list_p_arrange_exp) =" + str(n_imgs))
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

        box_dat = {
            "x"           :x_ini,
            "y"           :y_ini,
            "width"       :width,
            "height"      :height,
            "local_hkl"   :local_hkl,
            "big_lst_num" :int(i)
        }
        if num_of_imagesets > 1:
            add_shift = 0
            for id_num in range(id_col[i]):
                add_shift += num_of_imgs_lst[id_num]

            for ind_z in range(ref_box[4], ref_box[5]):
                ind_z_shift = ind_z - imgs_shift_lst[id_col[i]]
                ind_z_shift += add_shift
                if ind_z_shift >= 0 and ind_z_shift < n_imgs:
                    img_lst[ind_z_shift].append(box_dat)

        else:
            for ind_z in range(ref_box[4], ref_box[5]):
                ind_z_shift = ind_z - imgs_shift_lst[0]
                if ind_z_shift >= 0 and ind_z_shift < n_imgs:
                    img_lst[ind_z_shift].append(box_dat)

    return img_lst


def get_refl_lst(expt_path, refl_path, img_num):
    try:
        experiments = get_experiments(expt_path[0])
        all_sweeps = experiments.imagesets()
        num_of_imagesets = len(all_sweeps)
        logging.info("refl_path =" + str(refl_path))
        table = flex.reflection_table.from_file(refl_path[0])

    except IndexError:
        logging.info("sending empty reflection Lst (Index err catch )")
        return []

    except TypeError:
        logging.info("sending empty reflection Lst (Type err catch )")
        return []

    except FileNotFoundError:
        logging.info(
            "sending empty reflection Lst (File Not Found err catch)"
        )
        return []

    except OSError:
        logging.info("sending empty reflection Lst (OS err catch)")
        return []

    try:
        pan_col = list(map(int, table["panel"]))
        bbox_col = list(map(list, table["bbox"]))
        id_col = list(map(int, table["id"]))
        num_of_imgs_lst = []
        imgs_shift_lst = []

        n_imgs = 0
        for single_sweep in all_sweeps:
            num_of_imgs = len(single_sweep.indices())
            n_imgs += num_of_imgs
            shift = single_sweep.get_scan().get_image_range()[0] - 1
            num_of_imgs_lst.append(num_of_imgs)
            imgs_shift_lst.append(shift)

        box_flat_data_lst = []
        if n_imgs > 0:
            try:
                hkl_col = list(map(str, table["miller_index"]))

            except KeyError:
                logging.info("NOT found << miller_index >> col")
                hkl_col = None

            box_flat_data_lst = list_p_arrange_exp(
                bbox_col, pan_col, hkl_col, n_imgs, num_of_imgs_lst,
                imgs_shift_lst, id_col, num_of_imagesets
            )

        try:
            refl_lst = box_flat_data_lst[img_num]
            logging.info("len(refl_lst) =" + str(len(refl_lst)))

        except IndexError:
            refl_lst = []
            logging.info("refl_lst = []")

        return refl_lst

    except KeyError:
        logging.info("NOT found << bbox_col >> col")
        return []


def single_image_arrange_predic(
    xyzcal_col = None, pan_col = None, hkl_col = None, n_imgs = None,
    num_of_imgs_lst = None, imgs_shift_lst = None, id_col = None,
    num_of_imagesets = 1, z_dept = 1, img_num = None
):
    img_lst = []
    for i, ref_xyx in enumerate(xyzcal_col):
        x_cord = ref_xyx[0]
        y_cord = ref_xyx[1] + pan_col[i] * 213
        z_cord = ref_xyx[2]

        if num_of_imagesets > 1:
            add_shift = 0
            for id_num in range(id_col[i]):
                add_shift += num_of_imgs_lst[id_num]

            ind_z_shift = round(z_cord) - imgs_shift_lst[id_col[i]] + add_shift
            z_dist = abs(ind_z_shift - img_num)

            if z_dist < z_dept:
                local_hkl = hkl_col[i]
                if hkl_col[i] == "(0, 0, 0)":
                    hkl_col[i] = "NOT indexed"

                img_lst.append(
                    {
                        "x":x_cord, "y":y_cord,
                        "local_hkl":local_hkl, "z_dist": z_dist
                    }
                )

        else:
            ind_z_shift = round(z_cord) - imgs_shift_lst[0]
            z_dist = abs(ind_z_shift - img_num)
            if z_dist < z_dept:
                local_hkl = hkl_col[i]
                if hkl_col[i] == "(0, 0, 0)":
                    hkl_col[i] = "NOT indexed"

                img_lst.append(
                    {
                        "x":x_cord, "y":y_cord,
                        "local_hkl":local_hkl, "z_dist": z_dist
                    }
                )

    refl_lst = img_lst
    return refl_lst


def get_refl_pred_lst(expt_path, refl_path, img_num, z_dept):
    try:
        experiments = get_experiments(expt_path[0])
        all_sweeps = experiments.imagesets()
        num_of_imagesets = len(all_sweeps)
        logging.info("refl_path =" + str(refl_path))
        table = flex.reflection_table.from_file(refl_path)

    except IndexError:
        logging.info("sending empty predict reflection (Index err catch )")
        return []

    except TypeError:
        logging.info("sending empty predict reflection (Type err catch )")
        return []

    try:
        pan_col = list(map(int, table["panel"]))
        xyzcal_col = list(map(list, table["xyzcal.px"]))
        id_col = list(map(int, table["id"]))

        num_of_imgs_lst = []
        imgs_shift_lst = []
        n_imgs = 0
        for single_sweep in all_sweeps:
            num_of_imgs = len(single_sweep.indices())
            n_imgs += num_of_imgs
            shift = single_sweep.get_scan().get_image_range()[0] - 1
            num_of_imgs_lst.append(num_of_imgs)
            imgs_shift_lst.append(shift)

        box_flat_data_lst = []
        if n_imgs > 0:
            try:
                hkl_col = list(map(str, table["miller_index"]))

            except KeyError:
                logging.info("NOT found << miller_index >> col")
                hkl_col = None

            box_flat_data_lst = single_image_arrange_predic(
                xyzcal_col = xyzcal_col, pan_col = pan_col, hkl_col = hkl_col,
                n_imgs = n_imgs, num_of_imgs_lst = num_of_imgs_lst,
                imgs_shift_lst = imgs_shift_lst, id_col = id_col,
                num_of_imagesets = num_of_imagesets, z_dept = z_dept,
                img_num = img_num
            )

        return box_flat_data_lst

    except KeyError:
        logging.info("NOT found << xyzcal_col >> col")
        return [ [] ]


def get_correct_img_num_n_sweep_num(experiments, img_num):
    lst_num_of_imgs = []
    for single_sweep in experiments.imagesets():
        lst_num_of_imgs.append(len(single_sweep.indices()))

    on_sweep_img_num = img_num
    n_sweep = 0
    for num_of_imgs in lst_num_of_imgs:
        if on_sweep_img_num >= num_of_imgs:
            on_sweep_img_num -= num_of_imgs
            n_sweep += 1

        else:
            break

    return on_sweep_img_num, n_sweep


def get_bytes_w_img_2d(experiments_list_path, img_num):
    experiments = get_experiments(experiments_list_path[0])
    if experiments is not None:
        on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
            experiments, img_num
        )
        my_sweep = experiments.imagesets()[n_sweep]
        raw_dat = my_sweep.get_raw_data(on_sweep_img_num)
        np_arr, i23_multipanel = img_stream_py.get_np_full_img(raw_dat)
        byte_info = img_stream_py.np_arr_2_byte_stream(np_arr)
        return byte_info

    else:
        return None


def get_bytes_w_2d_slise(experiments_list_path, img_num, inv_scale, x1, y1, x2, y2):
    experiments = get_experiments(experiments_list_path[0])
    if experiments is not None:
        pan_num = 0
        on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
            experiments, img_num
        )
        my_sweep = experiments.imagesets()[n_sweep]
        data_xy_flex = my_sweep.get_raw_data(on_sweep_img_num)

        byte_data = img_stream_py.slice_arr_2_byte(
            data_xy_flex, inv_scale,
            int(float(x1)), int(float(y1)),
            int(float(x2)), int(float(y2))
        )

        if byte_data == "Error":
            logging.info('byte_data == "Error"')
            byte_data = None

        return byte_data

    else:
        return None


def get_bytes_w_mask_img_2d(experiments_list_path, img_num):
    experiments = get_experiments(experiments_list_path[0])
    if experiments is not None:
        pan_num = 0
        on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
            experiments, img_num
        )
        try:
            imageset_tmp = experiments.imagesets()[n_sweep]
            mask_file = imageset_tmp.external_lookup.mask.filename
            pick_file = open(mask_file, "rb")
            mask_tup_obj = pickle.load(pick_file)
            pick_file.close()
            str_data, i23_multipanel = img_stream_py.get_str_full_mask(mask_tup_obj)

        except FileNotFoundError:
            str_data = None

        return str_data

    else:
        return None


def get_bytes_w_2d_mask_slise(
    experiments_list_path, img_num, inv_scale, x1, y1, x2, y2
):
    experiments = get_experiments(experiments_list_path[0])
    if experiments is not None:
        on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
            experiments, img_num
        )

        imageset_tmp = experiments.imagesets()[n_sweep]
        mask_file = imageset_tmp.external_lookup.mask.filename
        try:
            pick_file = open(mask_file, "rb")
            mask_tup_obj = pickle.load(pick_file)
            pick_file.close()

            byte_data, i23_multipanel = img_stream_py.slice_mask_2_byte(
                mask_tup_obj, inv_scale,
                int(float(x1)), int(float(y1)),
                int(float(x2)), int(float(y2))
            )

            if byte_data == "Error":
                logging.info('byte_data == "Error"')
                byte_data = None

        except FileNotFoundError:
            byte_data = None

        return byte_data

    else:
        return None


def get_2d_threshold_mask_tupl(
    experiments_list_path, img_num, params
):
    experiments = get_experiments(experiments_list_path[0])

    if experiments is not None:
        on_sweep_img_num, n_sweep = get_correct_img_num_n_sweep_num(
            experiments, img_num
        )

        tup_lst = img_stream_py.get_dispersion_debug_obj_tup(
            expt_path = experiments_list_path[n_sweep],
            on_sweep_img_num = img_num,
            params_in = params
        )
        return tup_lst

    else:
        return None


def get_bytes_w_2d_threshold_mask(
    experiments_list_path, img_num, params
):
    if len(experiments_list_path) > 0:
        tuple_of_flex_mask = get_2d_threshold_mask_tupl(
            experiments_list_path, img_num, params
        )
        if len(tuple_of_flex_mask) == 24:
            i23_multipanel = True
            np_arr = img_stream_py.get_np_full_mask_from_i23_raw(
                raw_mask_data_in = tuple_of_flex_mask, border_to_one = False
            )

        else:
            data_xy_flex = tuple_of_flex_mask[0]
            np_arr = to_numpy(data_xy_flex)

        byte_data = img_stream_py.np_arr_2_byte_stream(np_arr)
        return byte_data

    else:
        return None


def get_bytes_w_2d_threshold_mask_slise(
    experiments_list_path, img_num, inv_scale, x1, y1, x2, y2, params
):
    if len(experiments_list_path) > 0:
        tuple_of_flex_mask = get_2d_threshold_mask_tupl(
            experiments_list_path, img_num, params
        )
        if len(tuple_of_flex_mask) == 24:
            i23_multipanel = True
            np_arr = img_stream_py.get_np_full_mask_from_i23_raw(
                raw_mask_data_in = tuple_of_flex_mask, border_to_one = False
            )

        else:
            data_xy_flex = tuple_of_flex_mask[0]
            np_arr = to_numpy(data_xy_flex)
        #TODO: find why I this: << float inside int >>
        np_arr = img_stream_py.mask_threshold_2_slise(
            np_arr, inv_scale,
            int(float(x1)), int(float(y1)),
            int(float(x2)), int(float(y2))
        )
        byte_data = img_stream_py.np_arr_2_byte_stream(np_arr)
        return byte_data

    else:
        return None


