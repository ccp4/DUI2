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
    def __init__(self, stp_prn, indent, lin_num, str_cmd):
        self.stp_prn = stp_prn
        self.indent = indent
        self.lin_num = lin_num
        self.str_cmd = str_cmd


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
        self._add_tree(step = self.lst_nod[0], indent=0)
        self._output_connect()

    def _add_tree(self, step=None, indent=None):
        if step["status"] == "Succeeded":
            stp_prn = " S "

        elif step["status"] == "Failed":
            stp_prn = " F "

        elif step["status"] == "Busy":
            stp_prn = " B "

        else:
            stp_prn = " R "

        str_lin_num = "(" + str(step["lin_num"]) + ")"
        stp_prn += self.ind_spc * indent + r"  \__"

        stp_prn += str_lin_num + "     "
        str_cmd = str(step["cmd2show"][0])

        nod_dat = node_print_data(stp_prn, indent, int(step["lin_num"]), str_cmd)
        self.str_lst.append(nod_dat)

        new_indent = indent

        if len(step["next_step_list"]) > 0:
            for nxt_stp_lin_num in step["next_step_list"]:
                for node in self.lst_nod:
                    if nxt_stp_lin_num == node["lin_num"]:
                        #if all(item in List1 for item in List2):
                        #if all(item in node[parent_node_lst] for item in self.str_lst[:][2]):
                        found = False
                        for node_pos in self.str_lst:
                            if node_pos.lin_num == node["lin_num"]:
                                found = True
                        if found == False:
                            new_indent = indent + 1
                            self._add_tree(step=node, indent=new_indent)
        else:
            new_indent = int(new_indent)
            if new_indent > self.max_indent:
                self.max_indent = new_indent

    def _output_connect(self):
        for pos, loc_lst in enumerate(self.str_lst):
            if pos > 0:
                if loc_lst.indent < self.str_lst[pos - 1].indent:
                    for up_pos in range(pos - 1, 0, -1):
                        pos_in_str = loc_lst.indent * len(self.ind_spc) + 5
                        left_side = self.str_lst[up_pos].stp_prn[0:pos_in_str]
                        right_side = self.str_lst[up_pos].stp_prn[pos_in_str + 1 :]
                        if self.str_lst[up_pos].indent > loc_lst.indent:
                            self.str_lst[up_pos].stp_prn = left_side + "|" + right_side

                        elif self.str_lst[up_pos].indent == loc_lst.indent:
                            break

            lng = len(self.ind_spc) * self.max_indent + 22
            lng_lft = lng - len(self.str_lst[pos].stp_prn)
            str_here = lng_lft * " "
            self.str_lst[pos].stp_prn += str_here + " | " + self.str_lst[pos].str_cmd

        for prn_str in self.str_lst:
            self.lst_out.append(prn_str.stp_prn)

        self.lst_out.append("---------------------" + self.max_indent * "-" * len(self.ind_spc))

    def print_output(self):
        for prn_str in self.lst_out:
            print(prn_str)

