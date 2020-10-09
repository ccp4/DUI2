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

def get_lst2show(main_obj):
    lst_nod = []
    for uni in main_obj.step_list:
        print("\n\n uni.lst2run =", uni.lst2run, "\n\n")

        if uni.lst2run == []:
            cmd2show = ["None"]

        else:
            cmd2show = uni.lst2run[-1]


        node = {"lin_num"           :uni.lin_num,
                "status"            :uni.status,
                "cmd2show"          :cmd2show,
                "child_node_lst"    :uni.child_node_lst,
                "parent_node_lst"   :uni.parent_node_lst}
        lst_nod.append(node)

    return lst_nod

class TreeShow(object):
    def __init__(self):
        self.ind_spc = "    "

    def __call__(self, lst_nod = None):
        self.lst_nod = lst_nod

        self.lst_out = []
        self.lst_out.append("")
        self.lst_out.append("status: (R)eady  (B)usy  (F)ailed  (S)ucceeded")
        self.lst_out.append(" | ")
        self.lst_out.append(" |  line number ")
        self.lst_out.append(" |   | ")
        self.lst_out.append(" |   |    command --->  ")
        self.lst_out.append("--------------------------")

        self.max_indent = 0
        self.dat_lst = []
        self._add_tree(step = self.lst_nod[0], parent_indent = 0, indent=1)
        self._output_connect()
        return self.lst_out

    def _add_tree(self, step=None, parent_indent = 0, indent = 0, low_par_lin_num = 0):
        '''
        building recursively the a list of objects dictionaries
        which contains info about how to draw the tree
        '''
        if step["status"] == "Succeeded":
            stp_prn = " S   "
            stp_stat = "S"

        elif step["status"] == "Failed":
            stp_prn = " F   "
            stp_stat = "F"

        elif step["status"] == "Busy":
            stp_prn = " B   "
            stp_stat = "B"

        else:
            stp_prn = " R   "
            stp_stat = "R"

        str_lin_num = "(" + str(step["lin_num"]) + ")"
        diff_inde = (indent - parent_indent) * 4 - 3
        stp_prn += self.ind_spc * (parent_indent) + "\\" + r"_" * diff_inde

        stp_prn += str_lin_num
        str_cmd = str(step["cmd2show"][0])

        if str_cmd[:6] == "dials.":
            str_cmd = str_cmd[6:]

        nod_dat = {
            "stp_prn"         : stp_prn ,
            "indent"          : indent ,
            "parent_indent"   : parent_indent ,
            "lin_num"         : int(step["lin_num"]) ,
            "str_cmd"         : str_cmd ,
            "par_lst"         : step["parent_node_lst"] ,
            "low_par_lin_num" : low_par_lin_num ,
            "stp_stat"        : stp_stat
        }
        self.dat_lst.append(nod_dat)

        new_indent = indent + 1
        if len(step["child_node_lst"]) > 0:
            '''
                making sure all parent nodes of <step>
                are already in <self.lst_nod>
            '''
            for node in self.lst_nod:
                if node["lin_num"] in step["child_node_lst"]:
                    lst_num = [emt["lin_num"] for emt in self.dat_lst]
                    found_parents = True
                    for node_pos in node["parent_node_lst"]:
                        if node_pos not in lst_num:
                            found_parents = False

                    if(
                        found_parents == True and
                        node["lin_num"] not in lst_num
                    ):
                        if len(node["parent_node_lst"]) > 1:
                            #finding top parent and bottom parent
                            lst_par_pos = []
                            for tmp_pos, tmp_elem in enumerate(self.dat_lst):
                                if tmp_elem["lin_num"] in node["parent_node_lst"]:
                                    lst_par_pos.append(tmp_pos)

                            for elem in self.dat_lst[min(lst_par_pos):]:
                                if new_indent < elem["indent"] + 1:
                                    new_indent = elem["indent"] + 1

                        elif len(node["parent_node_lst"]) == 1:
                            for tmp_elem in self.dat_lst:
                                if tmp_elem["lin_num"] == node["parent_node_lst"][0]:
                                    new_indent = tmp_elem["indent"] + 1

                        self._add_tree(
                            step=node,
                            parent_indent = indent,
                            indent = new_indent,
                            low_par_lin_num = step["lin_num"]
                            )

        else:
            if new_indent > self.max_indent:
                self.max_indent = new_indent

    def _output_connect(self):
        '''
        inserting/editing what to print in in <stp_prn>
        which is part of each element of <self.dat_lst>
        '''
        for pos, obj2prn in enumerate(self.dat_lst):
            if pos > 0:
                if obj2prn["parent_indent"] < self.dat_lst[pos - 1]["parent_indent"]:
                    for up_pos in range(pos - 1, 0, -1):
                        pos_in_str = obj2prn["parent_indent"] * len(self.ind_spc) + 5
                        left_side = self.dat_lst[up_pos]["stp_prn"][0:pos_in_str]
                        right_side = self.dat_lst[up_pos]["stp_prn"][pos_in_str + 1 :]
                        if self.dat_lst[up_pos]["parent_indent"] > obj2prn["parent_indent"]:
                            self.dat_lst[up_pos]["stp_prn"] = left_side + "|" + right_side

                        else:
                            break

            lng = len(self.ind_spc) * self.max_indent + 12
            lng_lft = lng - len(obj2prn["stp_prn"])
            str_here = lng_lft * " "
            obj2prn["stp_prn"] += str_here + " | " + obj2prn["str_cmd"]

        for pos, obj2prn in enumerate(self.dat_lst):
            if len(obj2prn["par_lst"]) > 1:
                lst2connect = []
                for par_pos, prev in enumerate(self.dat_lst[0:pos]):
                    if prev["lin_num"] in obj2prn["par_lst"]:
                        lst2connect.append(par_pos)

                lst2connect.remove(max(lst2connect))
                inde4times = obj2prn["indent"] * 4

                try:
                    for raw_pos in range(min(lst2connect) + 1, pos, 1):
                        loc_lin_str = self.dat_lst[raw_pos]["stp_prn"]
                        left_side = loc_lin_str[0:inde4times + 5]
                        right_side = loc_lin_str[inde4times + 6:]
                        self.dat_lst[raw_pos]["stp_prn"] = left_side + ":" + right_side

                except ValueError:
                    print("repeated parent")

                for up_lin in lst2connect:
                    loc_lin_str = self.dat_lst[up_lin]["stp_prn"]
                    pos_left = self.dat_lst[up_lin]["indent"] * 4 + 7
                    pos_right = inde4times + 6
                    mid_lin = ""
                    for loc_char in loc_lin_str[pos_left:pos_right - 1]:
                        if loc_char == "\\":
                            mid_lin += "\\"

                        else:
                            mid_lin += "`"

                    mid_lin += "\\"

                    left_side = loc_lin_str[0:pos_left]
                    right_side = loc_lin_str[pos_right:]
                    self.dat_lst[up_lin]["stp_prn"] = left_side + mid_lin + right_side

                obj2prn["stp_prn"] += ",  parents:" + str(obj2prn["par_lst"])

        for prn_str in self.dat_lst:
            self.lst_out.append(prn_str["stp_prn"])

        self.lst_out.append("---------------------" + self.max_indent * "-" * len(self.ind_spc))

    def print_output(self):
        for prn_str in self.lst_out:
            print(prn_str)

    def get_tree_data(self):
        return self.dat_lst


class param_tree_2_lineal(object):
    """
    Recursively navigates the Phil objects in a way that the final
    self.lst_obj is a lineal list without ramifications
    """
    def __init__(self, phl_obj_lst):
        self.lst_obj = []
        self.deep_in_recurs(phl_obj_lst)

    def __call__(self):
        return self.lst_obj

    def deep_in_recurs(self, phl_obj_lst):
        for single_obj in phl_obj_lst:
            single_obj["indent"] = int(str(single_obj["full_path"]).count("."))
            if single_obj["name"] == "output":
                print(" << output >> should be handled by DUI")

            elif single_obj["type"] == "scope":
                self.lst_obj.append(single_obj)
                self.deep_in_recurs(single_obj["child_objects"])

            else:
                self.lst_obj.append(single_obj)



