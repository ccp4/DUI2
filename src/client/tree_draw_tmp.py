
class node_print_data(object):
    def __init__(self, stp_prn, indent, parent_indent, lin_num, str_cmd, par_lst):
        self.stp_prn = stp_prn
        self.indent = indent
        self.parent_indent = parent_indent
        self.lin_num = lin_num
        self.str_cmd = str_cmd
        self.par_lst = par_lst



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
        self.str_lst = []
        self._add_tree(step = self.lst_nod[0], parent_indent = 0, indent=1)
        self._output_connect()
        return self.lst_out

    def _add_tree(self, step=None, parent_indent = 0, indent = 0):
        if step["status"] == "Succeeded":
            stp_prn = " S   "

        elif step["status"] == "Failed":
            stp_prn = " F   "

        elif step["status"] == "Busy":
            stp_prn = " B   "

        else:
            stp_prn = " R   "

        str_lin_num = "(" + str(step["lin_num"]) + ")"
        diff_inde = (indent - parent_indent) * 4 - 3
        stp_prn += self.ind_spc * (parent_indent) + "\\" + r"_" * diff_inde

        stp_prn += str_lin_num
        str_cmd = str(step["cmd2show"][0])

        if str_cmd[:6] == "dials.":
            str_cmd = str_cmd[6:]


        nod_dat = node_print_data(
            stp_prn, indent, parent_indent,
            int(step["lin_num"]),
            str_cmd, step["parent_node_lst"]
            )
        self.str_lst.append(nod_dat)

        new_indent = indent + 1
        if len(step["next_step_list"]) > 0:
            for nxt_stp_lin_num in step["next_step_list"]:
                for node in self.lst_nod:
                    if nxt_stp_lin_num == node["lin_num"]:
                        tmp_lst_num = []
                        for elem in self.str_lst:
                            tmp_lst_num.append(elem.lin_num)

                        found_parents = True
                        for node_pos in node["parent_node_lst"]:
                            if node_pos not in tmp_lst_num:
                                found_parents = False

                        if(
                            found_parents == True and
                            node["lin_num"] not in tmp_lst_num
                        ):
                            if len(node["parent_node_lst"]) > 1:
                                for elem in self.str_lst:
                                    if new_indent < elem.indent + 1:
                                        new_indent = elem.indent + 1

                            self._add_tree(
                                step=node,
                                parent_indent = indent,
                                indent=new_indent)

        else:
            if new_indent > self.max_indent:
                self.max_indent = new_indent

    def _output_connect(self):
        for pos, obj2prn in enumerate(self.str_lst):
            if pos > 0:
                if obj2prn.parent_indent < self.str_lst[pos - 1].parent_indent:
                    for up_pos in range(pos - 1, 0, -1):
                        pos_in_str = obj2prn.parent_indent * len(self.ind_spc) + 5
                        left_side = self.str_lst[up_pos].stp_prn[0:pos_in_str]
                        right_side = self.str_lst[up_pos].stp_prn[pos_in_str + 1 :]
                        if self.str_lst[up_pos].parent_indent > obj2prn.parent_indent:
                            self.str_lst[up_pos].stp_prn = left_side + "|" + right_side

                        else:
                            break

            lng = len(self.ind_spc) * self.max_indent + 12
            lng_lft = lng - len(obj2prn.stp_prn)
            str_here = lng_lft * " "
            obj2prn.stp_prn += str_here + " | " + obj2prn.str_cmd

        for pos, obj2prn in enumerate(self.str_lst):
            if len(obj2prn.par_lst) > 1:
                lst2connect = []
                for par_pos, prev in enumerate(self.str_lst[0:pos]):
                    if prev.lin_num in obj2prn.par_lst:
                        lst2connect.append(par_pos)

                lst2connect.remove(max(lst2connect))
                inde4times = obj2prn.indent * 4

                for raw_pos in range(min(lst2connect) + 1, pos, 1):
                    loc_lin_str = self.str_lst[raw_pos].stp_prn
                    left_side = loc_lin_str[0:inde4times + 5]
                    right_side = loc_lin_str[inde4times + 6:]
                    self.str_lst[raw_pos].stp_prn = left_side + ":" + right_side

                for up_lin in lst2connect:
                    loc_lin_str = self.str_lst[up_lin].stp_prn
                    pos_left = self.str_lst[up_lin].indent * 4 + 7
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
                    self.str_lst[up_lin].stp_prn = left_side + mid_lin + right_side

                obj2prn.stp_prn += ",  parents:" + str(obj2prn.par_lst)

        for prn_str in self.str_lst:
            self.lst_out.append(prn_str.stp_prn)

        self.lst_out.append("---------------------" + self.max_indent * "-" * len(self.ind_spc))

    def print_output(self):
        for prn_str in self.lst_out:
            print(prn_str)



