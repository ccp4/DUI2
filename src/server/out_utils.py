
def print_list(lst, curr):
    print("__________________________listing:")
    for uni in lst:
        # TODO loopthru all commands, in "both" lists
        stp_str = (
            str(uni.lin_num)
            + " "
            + str(uni.success)
            + " comm: "
            + str(uni._lst2run[0])
        )

        to_go = '''
        try:
            stp_str += " prev: " + str(uni.prev_step.lin_num)

        except BaseException as e:
            print("Caught unknown exception type %s: %s", type(e).__name__, e)
            stp_str += " prev: None"
        '''

        stp_str += " nxt: "
        if len(uni.next_step_list) > 0:
            for nxt_uni in uni.next_step_list:
                stp_str += "  " + str(nxt_uni.lin_num)
        else:
            stp_str += "empty"

        if curr == uni.lin_num:
            stp_str += "                           <<< here I am <<<"

        print(stp_str)


class TreeShow(object):
    def __init__(self):
        self.ind_spc = "      "
        self.ind_lin = "------"

    def __call__(self, my_runner):

        print("\n")
        print("")
        print("status ")
        print(" |  lin num ")
        print(" |   |  command ")
        print(" |   |   | ")
        print("------------------")
        self.max_indent = 0
        self.str_lst = []
        self.add_tree(step=my_runner.step_list[0], indent=0)
        self.tree_print(my_runner.current_line)
        # TODO maybe here goes a print print function instead of logger ...
        print("---------------------" + self.max_indent * self.ind_lin)

    def add_tree(self, step=None, indent=None):
        if step.success is True:
            stp_prn = " S "
        elif step.success is False:
            stp_prn = " F "
        else:
            stp_prn = " N "

        str_lin_num = "{0:3}".format(int(step.lin_num))

        stp_prn += str_lin_num + self.ind_spc * indent + r"   \___"
        for new_stp in step._lst2run:
            stp_prn += str(step._lst2run[0][0]) + "     "

        self.str_lst.append([stp_prn, indent, int(step.lin_num)])
        new_indent = indent
        if len(step.next_step_list) > 0:
            for line in step.next_step_list:
                new_indent = indent + 1
                self.add_tree(step=line, indent=new_indent)

        else:
            new_indent = int(new_indent)
            if new_indent > self.max_indent:
                self.max_indent = new_indent

    def tree_print(self, curr):
        self.tree_dat = []
        for tmp_lst in self.str_lst:
            self.tree_dat.append(tmp_lst)

        for pos, loc_lst in enumerate(self.tree_dat):
            if pos > 0:
                if loc_lst[1] < self.tree_dat[pos - 1][1]:
                    for up_pos in range(pos - 1, 0, -1):
                        pos_in_str = loc_lst[1] * len(self.ind_spc) + 9
                        left_side = self.tree_dat[up_pos][0][0:pos_in_str]
                        right_side = self.tree_dat[up_pos][0][pos_in_str + 1 :]
                        if self.tree_dat[up_pos][1] > loc_lst[1]:
                            self.tree_dat[up_pos][0] = left_side + "|" + right_side

                        elif self.tree_dat[up_pos][1] == loc_lst[1]:
                            break

            if loc_lst[2] == curr:
                lng = len(self.ind_spc) * self.max_indent + 22
                lng_lft = lng - len(self.tree_dat[pos][0])
                str_here = lng_lft * " "
                self.tree_dat[pos][0] += str_here + "  <<< here "

        for prn_str in self.tree_dat:
            print(prn_str[0])
