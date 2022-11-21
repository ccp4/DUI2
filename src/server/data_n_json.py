"""
DUI's command simple stacked widgets

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

import json, os, glob
import libtbx.phil
from dials.command_line.find_spots import phil_scope as phil_scope_find_spots
from dials.command_line.index import working_phil as phil_scope_index
from dials.command_line.refine_bravais_settings import (
    phil_scope as phil_scope_r_b_settings,
)
from dials.command_line.refine import working_phil as phil_scope_refine
from dials.command_line.integrate import phil_scope as phil_scope_integrate

from dials.command_line.scale import phil_scope as phil_scope_scale
from dials.command_line.symmetry import phil_scope as phil_scope_symmetry
from dials.command_line.combine_experiments import (
    phil_scope as phil_scope_combine_params
)
from server.img_uploader import flex_arr_2_json


def spit_out(str_out = None, req_obj = None, out_type = None):
    #print("req_obj(spit_out) =", req_obj)
    if req_obj is None:
        if out_type == 'utf-8':
            print(" ... ", str(str_out[:-1]), " ... ")

        else:
            print(" ... ", str_out , " ... ")

    elif 'ReqHandler' in str(type(req_obj)):
        if out_type == 'utf-8':
            req_obj.wfile.write(bytes(str_out, 'utf-8'))

        else:
            req_obj.wfile.write(bytes(str_out))

    else:
        if out_type == 'utf-8':
            req_obj.call_back_str(str_out)
            #print("<< YES utf-8, len=", len(str_out) , ">>")

        else:
            req_obj.call_back_bin(str_out)
            print(">> NOT utf-8,  len=", len(str_out) , "<<")


def get_data_from_steps(uni_cmd, cmd_dict, step_list):
    return_list = []
    if uni_cmd == ["display_log"]:
        for lin2go in cmd_dict["nod_lst"]:
            try:
                lof_file = open(
                    step_list[lin2go].log_file_path, "r"
                )
                lst2add = lof_file.readlines()
                lof_file.close()
                return_list.append(lst2add)

            except (IndexError, TypeError, FileNotFoundError) as my_er:
                print(
                    "\n  err catch ", my_er, " wrong line not logging \n"
                )

    elif uni_cmd == ["get_mtz"]:
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print("compresing mtz generated from node #:", lin2go)

                mtz_dir_path = step_list[lin2go]._run_dir
                print("mtz_dir_path =", mtz_dir_path)
                mtz_path = glob.glob(mtz_dir_path + os.sep + "*.mtz")[0]
                print("mtz_path =", mtz_path)

                with open(mtz_path, 'rb') as fil_h:
                    byt_data = fil_h.read()

                return_list = byt_data

            except IndexError:
                print(
                    "\n Index Err catch , sending empty mtz \n"
                )

            except FileNotFoundError:
                print(
                    "\n FileNotFound Err catch , sending empty mtz \n"
                )

    elif uni_cmd[0] == "get_experiments_file":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print("compresing experiments file from node #:", lin2go)
                exp_path = str(step_list[lin2go]._lst_expt_out[0])
                with open(exp_path, 'rb') as fil_h1:
                    exp_byt_data = fil_h1.read()

                return_list = exp_byt_data

            except (IndexError, FileNotFoundError):
                print(
                    "\n  err catch , wrong line," +
                    " NOT sending experiments file \n"
                )

    elif uni_cmd[0] == "get_reflections_file":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print("compresing reflection file from node #:", lin2go)
                ref_path = str(step_list[lin2go]._lst_refl_out[0])
                with open(ref_path, 'rb') as fil_h2:
                    ref_byt_data = fil_h2.read()

                return_list = ref_byt_data

            except (IndexError, FileNotFoundError):
                print(
                    "\n  err catch , wrong line," +
                    " NOT sending experiments or reflections \n"
                )

    elif uni_cmd == ["get_report"]:
        for lin2go in cmd_dict["nod_lst"]:
            try:
                rep_path = str(step_list[lin2go]._html_rep)
                print(
                    "#" * 70 + "\n HTML report in: " +
                    rep_path + "\n" + "#" * 70
                )
                fil = open(rep_path, "r")
                str_file = fil.read()
                fil.close()

                byt_data = bytes(str_file.encode('utf-8'))
                return_list = byt_data

            except IndexError:
                print(
                    "\n  Index Err catch, sending empty html list\n"
                )
                return_list = []

            except FileNotFoundError:
                print(
                    "\n  FileNotFound Err catch, sending empty html list \n"
                )
                return_list = []


    elif uni_cmd[0] == "get_template":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                #TODO check if the first element is enough
                exp_path = str(step_list[lin2go]._lst_expt_out[0])
                img_num = int(uni_cmd[1])
                return_list = flex_arr_2_json.get_template_info(
                    exp_path, img_num
                )

            except IndexError:
                print(
                    "\n  err catch , wrong line, not sending template string \n"
                )
    elif uni_cmd[0] == "get_image":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print(
                    "generating image JSON data for line:", lin2go,
                    " image:", int(uni_cmd[1])
                )
                #TODO remember to check if the list is empty
                str_json = flex_arr_2_json.get_json_w_img_2d(
                    step_list[lin2go]._lst_expt_out,
                    int(uni_cmd[1])
                )

                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

            except (IndexError, AttributeError, ValueError):
                print("\n  err catch , wrong line, not sending IMG \n")

    elif uni_cmd[0] == "get_image_slice":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print(
                    "generating slice of image for line:", lin2go,
                    " image:", int(uni_cmd[1]), "\n uni_cmd =", uni_cmd,
                    "\n"
                )
                inv_scale = 1
                for sub_par in uni_cmd[2:]:
                    eq_pos = sub_par.find("=")
                    left_side = sub_par[0:eq_pos]
                    right_side = sub_par[eq_pos + 1:]
                    if left_side == "inv_scale":
                        inv_scale = int(right_side)
                        print("inv_scale =", inv_scale)

                    elif left_side == "view_rect":
                        print("view_rect =", right_side)
                        [x1, y1, x2, y2] = right_side.split(",")
                        print("x1, y1, x2, y2 =", x1, y1, x2, y2)

                #TODO remember to check if the list is empty
                str_json = flex_arr_2_json.get_json_w_2d_slise(
                    step_list[lin2go]._lst_expt_out,
                    int(uni_cmd[1]), inv_scale, x1, y1, x2, y2
                )
                if str_json is not None:
                    byt_data = bytes(str_json.encode('utf-8'))
                    return_list = byt_data

            except (IndexError, AttributeError):
                print("\n  err catch , wrong line, not sending IMG \n")

            except ValueError:
                print("\n  err catch , wrong command, not sending IMG \n")


    elif uni_cmd[0] == "get_mask_image":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print(
                    "generating mask image JSON data for line:", lin2go,
                    " image:", int(uni_cmd[1])
                )
                #TODO remember to check if the list is empty
                str_json = flex_arr_2_json.get_json_w_mask_img_2d(
                    step_list[lin2go]._lst_expt_out,
                    int(uni_cmd[1])
                )

                byt_data = bytes(str_json.encode('utf-8'))
                return_list = byt_data

            except (IndexError, AttributeError, ValueError):
                print("\n  err catch , wrong line, not sending IMG \n")

    elif uni_cmd[0] == "get_mask_image_slice":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print(
                    "generating slice of mask image for line:", lin2go,
                    " image:", int(uni_cmd[1]), "\n uni_cmd =", uni_cmd,
                    "\n"
                )
                inv_scale = 1
                for sub_par in uni_cmd[2:]:
                    eq_pos = sub_par.find("=")
                    left_side = sub_par[0:eq_pos]
                    right_side = sub_par[eq_pos + 1:]
                    if left_side == "inv_scale":
                        inv_scale = int(right_side)
                        print("inv_scale =", inv_scale)

                    elif left_side == "view_rect":
                        print("view_rect =", right_side)
                        [x1, y1, x2, y2] = right_side.split(",")
                        print("x1, y1, x2, y2 =", x1, y1, x2, y2)

                #TODO remember to check if the list is empty
                str_json = flex_arr_2_json.get_json_w_2d_mask_slise(
                    step_list[lin2go]._lst_expt_out,
                    int(uni_cmd[1]), inv_scale, x1, y1, x2, y2
                )
                if str_json is not None:
                    byt_data = bytes(str_json.encode('utf-8'))
                    return_list = byt_data

            except (IndexError, AttributeError):
                print("\n  err catch , wrong line, not sending mask IMG \n")

            except ValueError:
                print("\n  err catch , wrong command, not sending mask IMG \n")

    elif uni_cmd[0] == "get_reflection_list":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print(
                    "generating reflection list for line:", lin2go,
                    " image:", int(uni_cmd[1])
                )
                refl_lst = flex_arr_2_json.get_refl_lst(
                    step_list[lin2go]._lst_expt_out,
                    step_list[lin2go]._lst_refl_out,
                    int(uni_cmd[1])
                )
                return_list = refl_lst

            except (IndexError, AttributeError, ValueError):
                print("\n  Err Catch , not sending reflection list \n")
                return_list = []

    elif uni_cmd[0] == "get_lambda":
        for lin2go in cmd_dict["nod_lst"]:
            try:
                print("generating lambda for line:", lin2go)
                experiments = flex_arr_2_json.get_experiments(
                    step_list[lin2go]._lst_expt_out[0]
                )
                return_list = [experiments.beams()[0].get_wavelength()]

            except (IndexError, AttributeError, ValueError, TypeError):
                print("\n  Err Catch , not sending lambda \n")
                return_list = []

    elif uni_cmd[0] == "get_predictions":
        print("running << get_predictions >> ")
        for lin2go in cmd_dict["nod_lst"]:
            try:
                img_num = int(uni_cmd[1])
                print(
                    "generating predictions for line:", lin2go,
                    " image:", img_num
                )
                sub_par = uni_cmd[2]
                if sub_par[0:7] == "z_dept=":
                    z_dept = int(sub_par[7:])

                else:
                    z_dept = 1

                refl_pre_lst = flex_arr_2_json.get_refl_pred_lst(
                    step_list[lin2go]._lst_expt_out,
                    step_list[lin2go]._predic_refl,
                    img_num, z_dept
                )
                return_list = refl_pre_lst

            except (IndexError, AttributeError, ValueError):
                print(
                    "\n  err catch , not sending predictions \n"
                )
                return_list = []

    elif uni_cmd == ["get_bravais_sum"]:
        for lin2go in cmd_dict["nod_lst"]:
            try:
                lst2add = step_list[lin2go].get_bravais_summ()
                return_list.append(lst2add)

            except IndexError:
                print("\n  err catch , wrong line, not sending bravais_sum \n")

    elif uni_cmd[0][-7:] == "_params":
        return_list = get_param_list(uni_cmd[0])

    elif uni_cmd[0] == "get_optional_command_list":
        return_list = get_cmd_opt_list()

    return return_list


class build_json_data(object):
    """
    Recursively navigates the Phil objects and creates another list
    of dictionaries with info about parameters, this new list is still
    ramified with objects hierarchy
    """
    def __init__(self, phl_obj_lst):
        self.lst_obj = []
        for single_obj in phl_obj_lst:
            nxt = self.deep_in_recurs(single_obj)
            if nxt is not None:
                self.lst_obj.append(nxt)

    def __call__(self):
        return self.lst_obj

    def deep_in_recurs(self, single_obj):
        if single_obj.name == "output":
            print(" << output >> should be handled by DUI")

        elif single_obj.is_definition:
            param_info = {
                "name"          :str(single_obj.name),
                "full_path"     :str(single_obj.full_path()),
                "short_caption" :str(single_obj.short_caption),
                "help"          :str(single_obj.help),
                "type"          :None,
                "opt_lst"       :None,
                "default"       :None
            }

            if single_obj.type.phil_type == "bool":
                param_info["type"] = "bool"
                param_info["opt_lst"] = ["True", "False", "Auto"]
                if str(single_obj.extract()) == "True":
                    param_info["default"] = 0

                elif str(single_obj.extract()) == "False":
                    param_info["default"] = 1

                else:
                    param_info["default"] = 2

            elif single_obj.type.phil_type == "choice":
                param_info["type"] = "choice"
                param_info["opt_lst"] = []
                param_info["default"] = len(single_obj.words)
                for num, opt in enumerate(single_obj.words):
                    opt = str(opt)
                    if opt[0] == "*":
                        opt = opt[1:]
                        param_info["default"] = num

                    param_info["opt_lst"].append(opt)

            else:
                param_info["type"] = "other(s)"
                param_info["default"] = str(single_obj.extract())

            return param_info

        elif single_obj.is_scope:
            param_info = {
                "name"          :str(single_obj.name),
                "full_path"     :str(single_obj.full_path()),
                "short_caption" :str(single_obj.short_caption),
                "help"          :str(single_obj.help),
                "type"          :"scope",
                "child_objects" :[]
            }
            for child in single_obj.objects:
                nxt = self.deep_in_recurs(child)
                if nxt is not None:
                    param_info["child_objects"].append(nxt)

            return param_info

        else:
            print("\n", single_obj.name,
                "\n WARNING neither definition or scope\n")

        return None

def get_cmd_opt_list():
    command_list = [
        "find_spots"                        ,
        "find_rotation_axis"                ,
        "index"                             ,
        "refine"                            ,
        "integrate"                         ,
        "symmetry"                          ,
        "scale"                             ,
        "merge"                             ,
        "cosym"                             ,
        "slice_sequence"                    ,
      "align_crystal"                          ,
      "anvil_correction"                       ,
      "assign_experiment_identifiers"          ,
      "augment_spots"                          ,
      "background"                             ,
      "check_indexing_symmetry"                ,
      "cluster_unit_cell"                      ,
      "compare_orientation_matrices"           ,
      "complete_full_sphere"                   ,
      "compute_delta_cchalf"                   ,
      "convert_to_cbf"                         ,
      "create_profile_model"                   ,
      "damage_analysis"                        ,
      "data"                                   ,
      "detect_blanks"                          ,
      "estimate_gain"                          ,
      "estimate_resolution"                    ,
      "export_best"                            ,
      "export_bitmaps"                         ,
      "filter_reflections"                     ,
      "find_bad_pixels"                        ,
      "find_hot_pixels"                        ,
      "find_shared_models"                     ,
      "find_spots_client"                      ,
      "find_spots_server"                      ,
      "frame_orientations"                     ,
      "generate_distortion_maps"               ,
      "geometry_viewer"                        ,
      "goniometer_calibration"                 ,
      "image_viewer"                           ,
      "import_xds"                             ,
      "indexed_as_integrated"                  ,
      "merge_cbf"                              ,
      "merge_reflection_lists"                 ,
      "missing_reflections"                    ,
      "model_background"                       ,
      "modify_geometry"                        ,
      "plot_Fo_vs_Fc"                          ,
      "plot_reflections"                       ,
      "plot_scan_varying_model"                ,
      "plugins"                                ,
      "powder_calibrate"                       ,
      "predict"                                ,
      "rbs"                                    ,
      "reference_profile_viewer"               ,
      "refine_error_model"                     ,
      "reflection_viewer"                      ,
      "rl_png"                                 ,
      "rlv"                                    ,
      "rs_mapper"                              ,
      "search_beam_position"                   ,
      "sequence_to_stills"                     ,
      "shadow_plot"                            ,
      "show"                                   ,
      "show_build_path"                        ,
      "show_dist_paths"                        ,
      "sort_reflections"                       ,
      "split_experiments"                      ,
      "spot_counts_per_image"                  ,
      "spot_resolution_shells"                 ,
      "stereographic_projection"               ,
      "stills_process"                         ,
      "two_theta_offset"                       ,
      "two_theta_refine"                       ,
      "unit_cell_histogram"                    ,
      "version"                                ,
    ]
    return command_list


def get_param_list(cmd_str):
    connect_dict = {
            "find_spots_params"              :phil_scope_find_spots.objects    ,
            "index_params"                   :phil_scope_index.objects         ,
            "refine_bravais_settings_params" :phil_scope_r_b_settings.objects  ,
            "refine_params"                  :phil_scope_refine.objects        ,
            "integrate_params"               :phil_scope_integrate.objects     ,
            "symmetry_params"                :phil_scope_symmetry.objects      ,
            "scale_params"                   :phil_scope_scale.objects         ,
            "combine_experiments_params"     :phil_scope_combine_params.objects,
        }

    lst_dict = build_json_data(connect_dict[cmd_str])
    lst_phil_obj = lst_dict()
    return lst_phil_obj


def iter_dict(file_path, depth_ini):
    file_name = file_path.split("/")[-1]
    local_dict = {
        "file_name": file_name, "file_path": file_path, "list_child": []
    }
    if depth_ini >= 30:
        #print("reached to deep with: ", file_path)
        local_dict["isdir"] = False

    elif os.path.isdir(file_path):
        local_dict["isdir"] = True
        depth_next = depth_ini + 1
        #print("depth_next =", depth_next)
        for new_file_name in sorted(os.listdir(file_path)):
            try:
                new_file_path = os.path.join(os.sep, file_path, new_file_name)
                local_dict["list_child"].append(iter_dict(new_file_path, depth_next))

            except PermissionError:
                local_dict["list_child"] = []
                local_dict["isdir"] = False
                break
                return local_dict

    else:
        local_dict["isdir"] = False

    return local_dict

