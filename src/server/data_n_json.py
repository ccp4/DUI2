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

import json
import os, sys
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

from dxtbx.model.experiment_list import ExperimentListFactory
from img_uploader import flex_arr_2_json


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
                    "\n *** ERROR *** \n", my_er, "\n *** \n" +
                    "wrong line \n not logging"
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

            except (IndexError, FileNotFoundError):
                print(
                    "\n *** ERROR *** \n wrong line" +
                    " \n sending empty html"
                )
                return_list = []

    elif uni_cmd == ["get_template"]:
        for lin2go in cmd_dict["nod_lst"]:
            try:
                #TODO check if the first element is enough
                exp_path = step_list[lin2go]._lst_expt_out[0]
                experiments = ExperimentListFactory.from_json_file(
                    exp_path
                )
                my_sweep = experiments.imagesets()[0]
                str_json = my_sweep.get_template()

                data_xy_flex = my_sweep.get_raw_data(0)[0].as_double()
                img_with, img_height = data_xy_flex.all()[0:2]
                return_list = [str_json, img_with, img_height]
            except IndexError:
                print(
                    "\n *** ERROR *** \n wrong line" +
                    " \n not sending template string"
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

            except (IndexError, AttributeError):
                print("\n *** ERROR *** \n wrong line \n not sending IMG")

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
                print("\n *** ERROR *** \n wrong line \n not sending IMG")

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

            except (IndexError, AttributeError):
                print("\n *** ERROR *** \n wrong line \n not sending IMG")

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
                print("\n *** ERROR *** \n wrong line \n not sending IMG")

    elif uni_cmd[0] == "get_reflection_list":
        for lin2go in cmd_dict["nod_lst"]:
            #try:
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

            '''except (IndexError, AttributeError):
                print(
                    "\n *** ERROR *** \n not sending reflection list \n"
                )
                return_list = []'''

    elif uni_cmd == ["get_bravais_sum"]:
        for lin2go in cmd_dict["nod_lst"]:
            try:
                lst2add = step_list[lin2go].get_bravais_summ()
                return_list.append(lst2add)

            except IndexError:
                print("\n *** ERROR *** \n wrong line \n not logging")


    elif uni_cmd[0][-7:] == "_params":
        return_list = get_param_list(uni_cmd[0])

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


def iter_dict(file_path):
    file_name = file_path.split("/")[-1]
    local_dict = {
        "file_name": file_name, "file_path": file_path, "list_child": []
    }
    if os.path.isdir(file_path):
        local_dict["isdir"] = True
        for new_file_name in sorted(os.listdir(file_path)):
            new_file_path = os.path.join(file_path, new_file_name)
            local_dict["list_child"].append(iter_dict(new_file_path))

    else:
        local_dict["isdir"] = False

    return local_dict

