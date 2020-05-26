import json

def get_lst2show(main_obj):
    lst_nod = []
    for uni in main_obj.step_list:
        if uni.lst2run == []:
            cmd2show = ["None"]

        else:
            cmd2show = uni.lst2run[0]

        node = {"lin_num"           :uni.lin_num,
                "status"            :uni.status,
                "cmd2show"          :cmd2show,
                "next_step_list"    :uni.next_step_list,
                "parent_node_lst"   :uni.parent_node_lst}

        print("\n")
        #print("_base_dir =         ", uni._base_dir         )
        #print("_lst_expt =         ", uni._lst_expt         )
        #print("_lst_refl =         ", uni._lst_refl         )
        #print("_run_dir =          ", uni._run_dir          )
        print("lin_num =           ", uni.lin_num           )
        #print("lst2run =           ", uni.lst2run           )
        print("next_step_list =    ", uni.next_step_list    )
        print("parent_node_lst =   ", uni.parent_node_lst   )
        #print("status =            ", uni.status            )

        lst_nod.append(node)

    return lst_nod

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
        diff_inde = (indent - parent_indent) * 2 - 1
        stp_prn += self.ind_spc * (parent_indent) + "\\" + r"__" * diff_inde

        stp_prn += str_lin_num
        str_cmd = str(step["cmd2show"][0])

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
                                    if elem.indent > new_indent:
                                        new_indent = elem.indent

                                new_indent += 1

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
            str_here = lng_lft * "."
            obj2prn.stp_prn += str_here + " | " + str(pos) + " " + obj2prn.str_cmd

        ##############################################################################
        for pos, obj2prn in enumerate(self.str_lst):
            if len(obj2prn.par_lst) > 1:
                lst2connect = []
                for par_pos, prev in enumerate(self.str_lst[0:pos]):
                    if prev.lin_num in obj2prn.par_lst:
                        lst2connect.append(par_pos)

                lst2connect.remove(max(lst2connect))

                for raw_pos in range(min(lst2connect) + 1, pos, 1):
                    left_side = self.str_lst[raw_pos].stp_prn[0:obj2prn.indent * 4 + 5]
                    right_side = self.str_lst[raw_pos].stp_prn[obj2prn.indent * 4 + 6:]
                    self.str_lst[raw_pos].stp_prn = left_side + "|" + right_side

                obj2prn.stp_prn += " arr pos:" + str(lst2connect) + ",  lst pos:" + str(obj2prn.par_lst)

                for up_lin in lst2connect:
                        self.str_lst[up_lin].stp_prn += "XX"




        for prn_str in self.str_lst:
            self.lst_out.append(prn_str.stp_prn)

        self.lst_out.append("---------------------" + self.max_indent * "-" * len(self.ind_spc))

    def print_output(self):
        for prn_str in self.lst_out:
            print(prn_str)

